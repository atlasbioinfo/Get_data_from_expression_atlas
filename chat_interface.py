"""
Interactive Chat Interface for Expression Atlas

This module provides a conversational interface to help users
retrieve data from Expression Atlas by asking them questions
about their requirements.
"""

import re
from typing import Dict, Optional, List
from expression_atlas import ExpressionAtlasAPI, ExpressionAtlasQuery


class ExpressionAtlasChat:
    """
    Conversational interface for Expression Atlas data retrieval.

    This class guides users through specifying their data requirements
    via an interactive question-and-answer session.
    """

    # Common species names and their variations
    SPECIES_MAP = {
        'human': 'homo sapiens',
        'humans': 'homo sapiens',
        'homo sapiens': 'homo sapiens',
        'h. sapiens': 'homo sapiens',
        'mouse': 'mus musculus',
        'mice': 'mus musculus',
        'mus musculus': 'mus musculus',
        'm. musculus': 'mus musculus',
        'rat': 'rattus norvegicus',
        'arabidopsis': 'arabidopsis thaliana',
        'thale cress': 'arabidopsis thaliana',
        'a. thaliana': 'arabidopsis thaliana',
        'zebrafish': 'danio rerio',
        'd. rerio': 'danio rerio',
        'fruit fly': 'drosophila melanogaster',
        'drosophila': 'drosophila melanogaster',
        'd. melanogaster': 'drosophila melanogaster',
        'yeast': 'saccharomyces cerevisiae',
        'c. elegans': 'caenorhabditis elegans',
        'worm': 'caenorhabditis elegans',
        'chicken': 'gallus gallus',
        'pig': 'sus scrofa',
        'cow': 'bos taurus',
        'cattle': 'bos taurus',
    }

    def __init__(self):
        """Initialize the chat interface."""
        self.api = ExpressionAtlasAPI()
        self.query = ExpressionAtlasQuery()
        self.user_requirements = {
            'species': None,
            'experiment_type': None,
            'keyword': None,
            'experiment_id': None,
            'output_dir': './expression_atlas_data'
        }

    def start(self):
        """Start the interactive conversation."""
        print("=" * 70)
        print("Expression Atlas Data Retrieval Tool")
        print("=" * 70)
        print("\nWelcome! I'll help you retrieve gene expression data from")
        print("EMBL-EBI Expression Atlas (https://www.ebi.ac.uk/gxa/home)\n")
        print("Let me ask you a few questions about your data requirements.\n")

        # Ask questions to gather requirements
        self._ask_experiment_id()

        if not self.user_requirements['experiment_id']:
            self._ask_species()
            self._ask_experiment_type()
            self._ask_keyword()

        self._ask_output_directory()

        # Summarize requirements
        self._summarize_requirements()

        # Confirm and proceed
        if self._confirm_download():
            self._execute_download()
        else:
            print("\nDownload cancelled. Run the tool again to start over.")

    def _ask_experiment_id(self):
        """Ask if user has a specific experiment ID."""
        print("=" * 70)
        print("Question 1: Experiment ID")
        print("=" * 70)
        print("\nDo you have a specific experiment ID?")
        print("(e.g., E-MTAB-513, E-GEOD-21860)")
        print("\nIf you don't have one, just press Enter to search for experiments.\n")

        response = input("Experiment ID (or press Enter to skip): ").strip()

        if response:
            # Validate format (E-MTAB-xxxxx or E-GEOD-xxxxx)
            if re.match(r'^E-(MTAB|GEOD|MEXP|TABM|ATMX|AFMX|MAGE)-\d+$', response, re.IGNORECASE):
                self.user_requirements['experiment_id'] = response.upper()
                print(f"\n✓ Using experiment ID: {response.upper()}")
            else:
                print("\n⚠ Invalid format. Expected format: E-MTAB-#### or E-GEOD-####")
                print("Continuing with search-based approach...\n")

    def _ask_species(self):
        """Ask about target species."""
        print("\n" + "=" * 70)
        print("Question 2: Species/Organism")
        print("=" * 70)
        print("\nWhich species/organism are you interested in?")
        print("\nCommon options:")
        print("  - Human (Homo sapiens)")
        print("  - Mouse (Mus musculus)")
        print("  - Rat (Rattus norvegicus)")
        print("  - Arabidopsis (Arabidopsis thaliana)")
        print("  - Zebrafish (Danio rerio)")
        print("  - Fruit fly (Drosophila melanogaster)")
        print("  - Or any other species name\n")

        response = input("Species: ").strip().lower()

        if response:
            # Try to map to standard name
            species = self.SPECIES_MAP.get(response, response)
            self.user_requirements['species'] = species
            print(f"✓ Species set to: {species}")
        else:
            print("⚠ No species specified. Search will include all species.")

    def _ask_experiment_type(self):
        """Ask about experiment type."""
        print("\n" + "=" * 70)
        print("Question 3: Experiment Type")
        print("=" * 70)
        print("\nWhat type of expression data do you need?")
        print("\n1. Baseline experiments")
        print("   - Gene expression in normal, untreated conditions")
        print("   - Shows expression across tissues, cell types, developmental stages")
        print("   - Example: 'Where is gene X expressed in human tissues?'")
        print("\n2. Differential experiments")
        print("   - Compares expression between conditions")
        print("   - Treatment vs control, disease vs healthy, time points, etc.")
        print("   - Example: 'Which genes are upregulated in cancer vs normal?'")
        print("\n3. Both/Don't know\n")

        response = input("Enter 1, 2, or 3: ").strip()

        if response == '1':
            self.user_requirements['experiment_type'] = 'baseline'
            print("✓ Looking for baseline experiments")
        elif response == '2':
            self.user_requirements['experiment_type'] = 'differential'
            print("✓ Looking for differential experiments")
        else:
            print("✓ Will search both types of experiments")

    def _ask_keyword(self):
        """Ask about search keywords."""
        print("\n" + "=" * 70)
        print("Question 4: Search Keywords")
        print("=" * 70)
        print("\nWhat are you interested in? You can specify:")
        print("  - Gene names (e.g., BRCA1, TP53, APOE)")
        print("  - Tissues (e.g., brain, liver, heart)")
        print("  - Diseases (e.g., cancer, diabetes, Alzheimer)")
        print("  - Conditions (e.g., drug treatment, stress response)")
        print("  - Or any other relevant keywords\n")

        response = input("Keywords (or press Enter to skip): ").strip()

        if response:
            self.user_requirements['keyword'] = response
            print(f"✓ Will search for: {response}")
        else:
            print("⚠ No keywords specified")

    def _ask_output_directory(self):
        """Ask where to save downloaded files."""
        print("\n" + "=" * 70)
        print("Question 5: Output Directory")
        print("=" * 70)
        print(f"\nWhere would you like to save the downloaded files?")
        print(f"Default: {self.user_requirements['output_dir']}\n")

        response = input(f"Output directory (or press Enter for default): ").strip()

        if response:
            self.user_requirements['output_dir'] = response
            print(f"✓ Files will be saved to: {response}")
        else:
            print(f"✓ Using default directory: {self.user_requirements['output_dir']}")

    def _summarize_requirements(self):
        """Display a summary of user requirements."""
        print("\n" + "=" * 70)
        print("Summary of Your Requirements")
        print("=" * 70)

        if self.user_requirements['experiment_id']:
            print(f"\n📋 Experiment ID: {self.user_requirements['experiment_id']}")
        else:
            print(f"\n🧬 Species: {self.user_requirements['species'] or 'Any'}")
            print(f"🔬 Experiment Type: {self.user_requirements['experiment_type'] or 'Any'}")
            print(f"🔍 Keywords: {self.user_requirements['keyword'] or 'None'}")

        print(f"📁 Output Directory: {self.user_requirements['output_dir']}")
        print()

    def _confirm_download(self) -> bool:
        """Ask user to confirm before downloading."""
        response = input("Proceed with download? (yes/no): ").strip().lower()
        return response in ['yes', 'y', '1', 'true']

    def _execute_download(self):
        """Execute the data download based on user requirements."""
        print("\n" + "=" * 70)
        print("Retrieving Data from Expression Atlas")
        print("=" * 70 + "\n")

        if self.user_requirements['experiment_id']:
            # Direct download with experiment ID
            self._download_by_id(self.user_requirements['experiment_id'])
        else:
            # Search and suggest experiments
            self._search_and_suggest()

    def _download_by_id(self, experiment_id: str):
        """Download data for a specific experiment ID."""
        print(f"Fetching information for experiment {experiment_id}...\n")

        # Get experiment info
        info = self.api.get_experiment_info(experiment_id)
        if 'error' not in info:
            print(f"Experiment: {info.get('description', experiment_id)}")
            print(f"Type: {info.get('type', 'Unknown')}")
            print(f"Species: {info.get('species', 'Unknown')}\n")

        # Download files
        print("Downloading data files...\n")
        files = self.api.download_experiment_data(
            experiment_id,
            self.user_requirements['output_dir']
        )

        if files:
            print(f"\n{'=' * 70}")
            print("Download Complete!")
            print("=" * 70)
            print(f"\nDownloaded {len(files)} file(s):")
            for file_type, path in files.items():
                print(f"  • {file_type}: {path}")

            # Suggest next steps
            print(f"\n📊 Next steps:")
            print(f"  1. Load data in Python:")
            print(f"     from expression_atlas import ExpressionAtlasAPI")
            print(f"     api = ExpressionAtlasAPI()")
            if 'analytics' in files:
                print(f"     df = api.load_expression_data('{files['analytics']}')")
            print(f"\n  2. View in R:")
            if 'r-object' in files:
                print(f"     load('{files['r-object']}')")
        else:
            print("\n⚠ No files were downloaded.")
            print(f"\nPlease check the experiment page directly:")
            print(f"https://www.ebi.ac.uk/gxa/experiments/{experiment_id}")

    def _search_and_suggest(self):
        """Search for experiments and suggest some to the user."""
        print("Searching Expression Atlas for matching experiments...\n")

        # Try to search
        results = self.api.search_experiments(
            species=self.user_requirements['species'],
            experiment_type=self.user_requirements['experiment_type'],
            keyword=self.user_requirements['keyword']
        )

        if results and isinstance(results, list) and len(results) > 0:
            print(f"Found {len(results)} matching experiments.\n")
            # Display first few results
            for i, exp in enumerate(results[:5], 1):
                print(f"{i}. {exp.get('accession', 'N/A')}: {exp.get('description', 'N/A')}")

            print("\nPlease visit the Expression Atlas website to browse experiments:")
        else:
            print("Could not retrieve search results via API.\n")

            # Suggest popular experiments based on their requirements
            print("Here are some popular experiments you might be interested in:\n")

            exp_type = self.user_requirements['experiment_type'] or 'baseline'
            popular = self.api.get_popular_experiments(exp_type)

            for exp_id in popular:
                print(f"  • {exp_id}")

            print(f"\nYou can download any of these by running:")
            print(f"  from expression_atlas import get_expression_data")
            print(f"  files = get_expression_data('{popular[0]}', output_dir='{self.user_requirements['output_dir']}')")

        print(f"\n🌐 Browse all experiments at:")
        url = f"https://www.ebi.ac.uk/gxa/experiments"
        if self.user_requirements['experiment_type']:
            url = f"https://www.ebi.ac.uk/gxa/{self.user_requirements['experiment_type']}/experiments"
        print(f"   {url}")


def main():
    """Main entry point for the chat interface."""
    chat = ExpressionAtlasChat()
    chat.start()


if __name__ == "__main__":
    main()
