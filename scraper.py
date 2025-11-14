"""
Expression Atlas Experiments Scraper

This module downloads and caches experiment metadata from Expression Atlas
to enable faster and more accurate local searches.
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import re


class ExpressionAtlasExperimentsScraper:
    """
    Scraper to download and cache Expression Atlas experiment metadata.
    """

    def __init__(self, cache_dir: str = "./atlas_cache"):
        """
        Initialize the scraper.

        Args:
            cache_dir: Directory to store cached experiment data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ExpressionAtlasBot/1.0)'
        })

    def scrape_experiments_list(
        self,
        experiment_type: str = "baseline",
        max_pages: int = 10
    ) -> pd.DataFrame:
        """
        Scrape experiments list from Expression Atlas.

        Args:
            experiment_type: 'baseline' or 'differential'
            max_pages: Maximum number of pages to scrape

        Returns:
            DataFrame with experiment metadata
        """
        base_url = f"https://www.ebi.ac.uk/gxa/{experiment_type}/experiments"

        experiments = []

        print(f"Scraping {experiment_type} experiments from Expression Atlas...")

        # Try to get JSON data if available
        json_url = f"https://www.ebi.ac.uk/gxa/json/{experiment_type}/experiments"

        try:
            response = self.session.get(json_url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if 'experiments' in data:
                    for exp in data['experiments']:
                        experiments.append({
                            'accession': exp.get('experimentAccession'),
                            'type': experiment_type,
                            'species': exp.get('species'),
                            'description': exp.get('experimentDescription'),
                            'last_update': exp.get('lastUpdate'),
                            'factors': ', '.join(exp.get('experimentalFactors', [])),
                        })
                    print(f"✓ Found {len(experiments)} experiments via JSON API")
                    return pd.DataFrame(experiments)
        except Exception as e:
            print(f"JSON API not available, trying HTML scraping... ({e})")

        # Fallback: Scrape HTML pages
        for page in range(max_pages):
            page_url = f"{base_url}?page={page + 1}"

            try:
                print(f"Scraping page {page + 1}...", end=" ")
                response = self.session.get(page_url, timeout=30)

                if response.status_code != 200:
                    print(f"✗ Failed (HTTP {response.status_code})")
                    break

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find experiment entries
                # The exact selector may need adjustment based on actual HTML structure
                exp_rows = soup.find_all('div', class_='experiment-list-item')

                if not exp_rows:
                    # Try alternative selectors
                    exp_rows = soup.find_all('tr', class_='experiment')

                if not exp_rows:
                    print("✗ No experiments found on this page")
                    break

                page_experiments = 0
                for row in exp_rows:
                    # Extract experiment data
                    exp_data = self._parse_experiment_row(row, experiment_type)
                    if exp_data:
                        experiments.append(exp_data)
                        page_experiments += 1

                print(f"✓ Found {page_experiments} experiments")

                # Small delay to be polite
                time.sleep(1)

            except Exception as e:
                print(f"✗ Error: {e}")
                break

        if not experiments:
            print("\n⚠ Could not scrape experiments. Using manual list...")
            return self._get_manual_experiment_list(experiment_type)

        df = pd.DataFrame(experiments)
        print(f"\n✓ Total: {len(df)} experiments scraped")
        return df

    def _parse_experiment_row(self, row, experiment_type: str) -> Optional[Dict]:
        """Parse a single experiment row from HTML."""
        try:
            # Try to find accession
            accession_elem = row.find('a', href=re.compile(r'/experiments/E-'))
            if accession_elem:
                accession = accession_elem.get('href', '').split('/')[-1]
            else:
                return None

            # Extract other fields
            description_elem = row.find('div', class_='experiment-description')
            description = description_elem.text.strip() if description_elem else ''

            species_elem = row.find('span', class_='species')
            species = species_elem.text.strip() if species_elem else ''

            return {
                'accession': accession,
                'type': experiment_type,
                'species': species,
                'description': description,
                'last_update': '',
                'factors': '',
            }
        except Exception:
            return None

    def _get_manual_experiment_list(self, experiment_type: str) -> pd.DataFrame:
        """Return a manually curated list of popular experiments."""
        manual_data = {
            'baseline': [
                {
                    'accession': 'E-MTAB-513',
                    'type': 'baseline',
                    'species': 'Homo sapiens',
                    'description': 'RNA-seq of human tissues from Illumina Body Map',
                    'last_update': '2024',
                    'factors': 'organism part',
                },
                {
                    'accession': 'E-MTAB-5214',
                    'type': 'baseline',
                    'species': 'Mus musculus',
                    'description': 'RNA-seq of mouse tissues',
                    'last_update': '2024',
                    'factors': 'organism part',
                },
                {
                    'accession': 'E-MTAB-3358',
                    'type': 'baseline',
                    'species': 'Arabidopsis thaliana',
                    'description': 'RNA-seq of Arabidopsis thaliana tissues and developmental stages',
                    'last_update': '2024',
                    'factors': 'developmental stage, organism part',
                },
            ],
            'differential': [
                {
                    'accession': 'E-GEOD-21860',
                    'type': 'differential',
                    'species': 'Homo sapiens',
                    'description': 'Transcription profiling of human colorectal cancer',
                    'last_update': '2024',
                    'factors': 'disease',
                },
                {
                    'accession': 'E-MTAB-1733',
                    'type': 'differential',
                    'species': 'Mus musculus',
                    'description': 'RNA-seq of mouse liver after drug treatment',
                    'last_update': '2024',
                    'factors': 'compound',
                },
            ]
        }

        return pd.DataFrame(manual_data.get(experiment_type, []))

    def download_all_experiments(self) -> Dict[str, pd.DataFrame]:
        """
        Download experiments lists for both baseline and differential.

        Returns:
            Dictionary with 'baseline' and 'differential' DataFrames
        """
        results = {}

        for exp_type in ['baseline', 'differential']:
            print(f"\n{'='*70}")
            print(f"Downloading {exp_type.upper()} experiments")
            print('='*70)

            df = self.scrape_experiments_list(exp_type)
            results[exp_type] = df

            # Save to cache
            cache_file = self.cache_dir / f"{exp_type}_experiments.csv"
            df.to_csv(cache_file, index=False)
            print(f"✓ Saved to {cache_file}")

            # Also save as JSON for easier loading
            json_file = self.cache_dir / f"{exp_type}_experiments.json"
            df.to_json(json_file, orient='records', indent=2)
            print(f"✓ Saved to {json_file}")

        return results

    def load_cached_experiments(
        self,
        experiment_type: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load cached experiments from disk.

        Args:
            experiment_type: 'baseline', 'differential', or None for both

        Returns:
            DataFrame with cached experiments
        """
        if experiment_type:
            cache_file = self.cache_dir / f"{experiment_type}_experiments.csv"
            if cache_file.exists():
                return pd.read_csv(cache_file)
            else:
                print(f"⚠ No cache found for {experiment_type}")
                return pd.DataFrame()
        else:
            # Load both
            dfs = []
            for exp_type in ['baseline', 'differential']:
                df = self.load_cached_experiments(exp_type)
                if not df.empty:
                    dfs.append(df)

            if dfs:
                return pd.concat(dfs, ignore_index=True)
            return pd.DataFrame()

    def search_experiments(
        self,
        species: Optional[str] = None,
        experiment_type: Optional[str] = None,
        keywords: Optional[str] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Search experiments with filters.

        Args:
            species: Species name (e.g., 'Arabidopsis thaliana')
            experiment_type: 'baseline' or 'differential'
            keywords: Search keywords
            use_cache: Use cached data if available

        Returns:
            Filtered DataFrame
        """
        # Load data
        if use_cache:
            df = self.load_cached_experiments(experiment_type)
            if df.empty:
                print("No cached data, downloading...")
                df = self.scrape_experiments_list(
                    experiment_type or 'baseline'
                )
        else:
            df = self.scrape_experiments_list(experiment_type or 'baseline')

        # Apply filters
        if species:
            df = df[df['species'].str.contains(species, case=False, na=False)]

        if keywords:
            # Search in description and factors
            mask = (
                df['description'].str.contains(keywords, case=False, na=False) |
                df['factors'].str.contains(keywords, case=False, na=False)
            )
            df = df[mask]

        return df


def main():
    """Demo usage of the scraper."""
    scraper = ExpressionAtlasExperimentsScraper()

    # Download all experiments
    print("Downloading Expression Atlas experiments metadata...")
    results = scraper.download_all_experiments()

    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    for exp_type, df in results.items():
        print(f"{exp_type.capitalize()}: {len(df)} experiments")

    # Test search
    print("\n" + "="*70)
    print("Testing search: Arabidopsis + seedling")
    print("="*70)

    results = scraper.search_experiments(
        species="Arabidopsis",
        experiment_type="baseline",
        keywords="seedling",
        use_cache=True
    )

    print(f"\nFound {len(results)} experiments:")
    if not results.empty:
        print(results[['accession', 'species', 'description']].to_string())


if __name__ == "__main__":
    main()
