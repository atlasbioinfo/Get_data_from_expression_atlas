#!/usr/bin/env python3
"""
Vector-based search for Expression Atlas experiments

Uses sentence embeddings to find the most relevant experiments
based on natural language queries.
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np


class ExperimentVectorSearch:
    """Vector search for experiments using sentence embeddings."""

    def __init__(self, cache_dir: str = "./atlas_cache"):
        """
        Initialize vector search.

        Args:
            cache_dir: Directory containing experiment CSV files
        """
        self.cache_dir = Path(cache_dir)
        self.experiments = []
        self.embeddings = None
        self.model = None

        # Load experiments
        self._load_experiments()

    def _load_experiments(self):
        """Load experiments from CSV files."""
        import pandas as pd

        baseline_file = self.cache_dir / "baseline_experiments.csv"
        differential_file = self.cache_dir / "differential_experiments.csv"

        experiments = []

        # Load baseline experiments
        if baseline_file.exists():
            df = pd.read_csv(baseline_file)
            for _, row in df.iterrows():
                experiments.append({
                    'accession': row['accession'],
                    'type': 'baseline',
                    'species': row['species'],
                    'description': row['description'] if pd.notna(row['description']) else '',
                    'factors': row['factors'] if pd.notna(row['factors']) else '',
                })

        # Load differential experiments
        if differential_file.exists():
            df = pd.read_csv(differential_file)
            for _, row in df.iterrows():
                experiments.append({
                    'accession': row['accession'],
                    'type': 'differential',
                    'species': row['species'],
                    'description': row['description'] if pd.notna(row['description']) else '',
                    'factors': row['factors'] if pd.notna(row['factors']) else '',
                })

        self.experiments = experiments
        print(f"Loaded {len(self.experiments)} experiments")

    def _init_model(self):
        """Initialize the sentence transformer model (lazy loading)."""
        if self.model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer
            print("Loading sentence transformer model...")
            # Use a lightweight multilingual model
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("Model loaded successfully")
        except ImportError:
            print("⚠ sentence-transformers not installed. Using fallback TF-IDF search.")
            print("Install with: pip install sentence-transformers")
            self.model = None

    def _create_searchable_text(self, experiment: Dict) -> str:
        """Create searchable text from experiment metadata."""
        parts = [
            str(experiment.get('species', '')),
            str(experiment.get('description', '')),
            str(experiment.get('type', '')),
        ]

        # Add factors if available
        if experiment.get('factors'):
            # Clean up factors string
            factors = str(experiment['factors']).replace(',', ' ')
            parts.append(factors)

        # Filter out empty strings and 'nan'
        parts = [p for p in parts if p and p.lower() != 'nan']

        return ' '.join(parts)

    def build_index(self, force_rebuild: bool = False):
        """
        Build vector index for all experiments.

        Args:
            force_rebuild: Rebuild index even if cached version exists
        """
        cache_file = self.cache_dir / "embeddings_cache.pkl"

        # Try to load cached embeddings
        if not force_rebuild and cache_file.exists():
            print("Loading cached embeddings...")
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                self.embeddings = cache_data['embeddings']
                method = cache_data.get('method', 'sentence-transformers')
                print(f"Loaded {len(self.embeddings)} cached embeddings (method: {method})")

                # Initialize the appropriate encoder for queries
                if method == 'tfidf':
                    self._init_tfidf_for_queries()
                else:
                    # Sentence transformers - need to load the model for query encoding
                    self._init_model()
                return

        # Initialize model
        self._init_model()

        if self.model is None:
            # Fallback to TF-IDF
            self._build_tfidf_index()
            return

        # Create searchable texts
        texts = [self._create_searchable_text(exp) for exp in self.experiments]

        print(f"Creating embeddings for {len(texts)} experiments...")
        self.embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

        # Cache the embeddings
        cache_file.parent.mkdir(exist_ok=True, parents=True)
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'embeddings': self.embeddings,
                'num_experiments': len(self.experiments),
                'method': 'sentence-transformers'
            }, f)
        print(f"Cached embeddings to {cache_file}")

    def _init_tfidf_for_queries(self):
        """Initialize TF-IDF for query encoding (when loading from cache)."""
        from sklearn.feature_extraction.text import TfidfVectorizer

        texts = [self._create_searchable_text(exp) for exp in self.experiments]

        self.tfidf = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        self.tfidf.fit(texts)  # Only fit, don't transform (embeddings already loaded)

    def _build_tfidf_index(self):
        """Fallback: Build TF-IDF index if sentence transformers not available."""
        from sklearn.feature_extraction.text import TfidfVectorizer

        texts = [self._create_searchable_text(exp) for exp in self.experiments]

        print("Building TF-IDF index (fallback mode)...")
        self.tfidf = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        self.embeddings = self.tfidf.fit_transform(texts).toarray()
        print("TF-IDF index built")

        # Cache the embeddings for faster loading next time
        cache_file = self.cache_dir / "embeddings_cache.pkl"
        cache_file.parent.mkdir(exist_ok=True, parents=True)
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'embeddings': self.embeddings,
                'num_experiments': len(self.experiments),
                'method': 'tfidf'
            }, f)
        print(f"Cached TF-IDF embeddings to {cache_file}")

    def search(
        self,
        query: str,
        top_k: int = 5,
        species_filter: Optional[str] = None,
        experiment_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for experiments matching the query.

        Args:
            query: Natural language query
            top_k: Number of results to return
            species_filter: Filter by species (e.g., 'arabidopsis thaliana')
            experiment_type: Filter by type ('baseline' or 'differential')

        Returns:
            List of matching experiments with scores
        """
        if self.embeddings is None:
            self.build_index()

        # Filter experiments if needed
        filtered_indices = []
        filtered_experiments = []
        filtered_embeddings = []

        for idx, exp in enumerate(self.experiments):
            # Apply filters
            exp_species = str(exp.get('species', '')).lower()
            if species_filter and species_filter.lower() not in exp_species:
                continue
            if experiment_type and exp.get('type') != experiment_type:
                continue

            filtered_indices.append(idx)
            filtered_experiments.append(exp)
            filtered_embeddings.append(self.embeddings[idx])

        if not filtered_experiments:
            return []

        filtered_embeddings = np.array(filtered_embeddings)

        # Encode query
        if self.model is not None:
            query_embedding = self.model.encode([query], convert_to_numpy=True)[0]
        else:
            # TF-IDF fallback
            query_embedding = self.tfidf.transform([query]).toarray()[0]

        # Calculate cosine similarities
        similarities = np.dot(filtered_embeddings, query_embedding) / (
            np.linalg.norm(filtered_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )

        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            exp = filtered_experiments[idx]
            results.append({
                **exp,
                'similarity_score': float(similarities[idx]),
                'rank': len(results) + 1
            })

        return results

    def search_by_keywords(
        self,
        species: Optional[str] = None,
        keywords: List[str] = None,
        experiment_type: str = 'baseline',
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search experiments by species and keywords.

        Args:
            species: Species name
            keywords: List of keywords (tissues, conditions, etc.)
            experiment_type: 'baseline' or 'differential'
            top_k: Number of results to return

        Returns:
            List of matching experiments
        """
        # Build query from components
        query_parts = []

        if species:
            query_parts.append(species)

        if keywords:
            query_parts.extend(keywords)

        query = ' '.join(query_parts)

        return self.search(
            query=query,
            top_k=top_k,
            species_filter=species,
            experiment_type=experiment_type
        )


def main():
    """Test the vector search."""
    print("=" * 80)
    print("Expression Atlas Vector Search Test")
    print("=" * 80)

    # Initialize search
    search = ExperimentVectorSearch()

    # Build index
    search.build_index()

    # Test queries
    test_queries = [
        ("我需要拟南芥seedling的数据", "arabidopsis thaliana", ["seedling"], "baseline"),
        ("human brain expression", "homo sapiens", ["brain"], "baseline"),
        ("mouse liver baseline", "mus musculus", ["liver"], "baseline"),
    ]

    for query, species, keywords, exp_type in test_queries:
        print(f"\n{'=' * 80}")
        print(f"Query: {query}")
        print(f"Species: {species}")
        print(f"Keywords: {keywords}")
        print(f"Type: {exp_type}")
        print("=" * 80)

        results = search.search_by_keywords(
            species=species,
            keywords=keywords,
            experiment_type=exp_type,
            top_k=3
        )

        print(f"\nTop {len(results)} results:")
        for result in results:
            print(f"\n  {result['rank']}. {result['accession']} (score: {result['similarity_score']:.3f})")
            print(f"     Species: {result['species']}")
            print(f"     Description: {result['description'][:100]}...")


if __name__ == "__main__":
    main()
