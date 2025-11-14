"""
Smart Chat Interface for Expression Atlas using Claude API

This module provides an AI-powered conversational interface that:
1. Understands natural language queries about gene expression data
2. Queries Expression Atlas website for available experiments
3. Dynamically asks follow-up questions based on results
4. Helps users find and download the right data
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import anthropic
import requests
from bs4 import BeautifulSoup
from expression_atlas import ExpressionAtlasAPI

# Load environment variables
load_dotenv()


class SmartExpressionAtlasChat:
    """
    AI-powered chat interface for Expression Atlas data retrieval.

    Uses Claude API to understand user intent and guide them through
    finding the right experiments.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the smart chat interface.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY in .env)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. Please set ANTHROPIC_API_KEY "
                "environment variable or pass it as a parameter."
            )

        self.claude = anthropic.Anthropic(api_key=self.api_key)
        self.atlas_api = ExpressionAtlasAPI()
        self.conversation_history = []
        self.extracted_info = {
            'species': None,
            'experiment_type': None,
            'keywords': [],
            'experiment_id': None
        }

    def start(self):
        """Start the intelligent conversation."""
        print("=" * 70)
        print("AI-Powered Expression Atlas Assistant")
        print("=" * 70)
        print("\nHello! I'm your AI assistant for finding gene expression data.")
        print("Just tell me what you're looking for in natural language.")
        print("\nExamples:")
        print("  - 'I need Arabidopsis expression data'")
        print("  - '我需要拟南芥在不同发育阶段的表达数据'")
        print("  - 'Show me human brain vs liver differential expression'")
        print("\nType 'quit' or 'exit' to stop.\n")

        while True:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nGoodbye! Visit https://www.ebi.ac.uk/gxa/home for more info.")
                break

            # Process user input with Claude
            response = self._process_with_claude(user_input)
            print(f"\nAssistant: {response}\n")

            # Check if we have enough information to search
            if self._has_enough_info():
                if self._confirm_search():
                    self._search_and_present_results()

    def _process_with_claude(self, user_input: str) -> str:
        """
        Process user input with Claude to extract information and generate response.

        Args:
            user_input: User's message

        Returns:
            Assistant's response
        """
        # Build system prompt
        system_prompt = """You are an expert assistant helping researchers find gene expression data from Expression Atlas (https://www.ebi.ac.uk/gxa/home).

Your tasks:
1. Extract information from user's request:
   - Species/organism (e.g., Arabidopsis thaliana, Homo sapiens, Mus musculus)
   - Experiment type (baseline or differential)
   - Keywords (genes, tissues, conditions, developmental stages, diseases, treatments)
   - Specific experiment ID if mentioned (format: E-MTAB-####, E-GEOD-####)

2. Ask clarifying questions when information is missing or ambiguous:
   - If only species is mentioned, ask about experiment type and what they want to study
   - If experiment type is unclear, explain the difference between baseline and differential
   - Suggest common options based on the species

3. Be conversational and helpful. Support both English and Chinese.

Expression Atlas data types:
- **Baseline**: Gene expression in normal conditions across tissues, cell types, developmental stages
- **Differential**: Comparison between conditions (treatment vs control, disease vs healthy, time points, etc.)

Common species: Human, Mouse, Rat, Arabidopsis, Zebrafish, Drosophila, C. elegans, Yeast

Format your response as JSON with two fields:
{
    "extracted_info": {
        "species": "scientific name or null",
        "experiment_type": "baseline|differential|null",
        "keywords": ["keyword1", "keyword2"],
        "experiment_id": "E-XXXX-#### or null"
    },
    "response": "Your natural language response to the user"
}"""

        # Add conversation history
        messages = self.conversation_history.copy()
        messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            # Call Claude API
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )

            # Parse response
            response_text = response.content[0].text

            # Try to parse JSON from response
            try:
                # Find JSON in response (might be wrapped in markdown code blocks)
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    parsed = json.loads(json_match.group())

                    # Update extracted info
                    if 'extracted_info' in parsed:
                        for key, value in parsed['extracted_info'].items():
                            if value:
                                if key == 'keywords' and isinstance(value, list):
                                    self.extracted_info[key].extend(value)
                                    self.extracted_info[key] = list(set(self.extracted_info[key]))  # Remove duplicates
                                else:
                                    self.extracted_info[key] = value

                    # Get natural language response
                    if 'response' in parsed:
                        natural_response = parsed['response']
                    else:
                        natural_response = response_text
                else:
                    # If no JSON found, use the whole response
                    natural_response = response_text
            except json.JSONDecodeError:
                # If JSON parsing fails, use the whole response
                natural_response = response_text

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })

            return natural_response

        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}\nPlease try again."

    def _has_enough_info(self) -> bool:
        """Check if we have enough information to search for experiments."""
        # We need at least a species or experiment ID
        return (
            self.extracted_info['species'] is not None or
            self.extracted_info['experiment_id'] is not None
        )

    def _confirm_search(self) -> bool:
        """Ask user to confirm before searching."""
        print("\n" + "=" * 70)
        print("Current Information")
        print("=" * 70)
        print(f"Species: {self.extracted_info['species'] or 'Not specified'}")
        print(f"Type: {self.extracted_info['experiment_type'] or 'Not specified'}")
        print(f"Keywords: {', '.join(self.extracted_info['keywords']) if self.extracted_info['keywords'] else 'None'}")
        if self.extracted_info['experiment_id']:
            print(f"Experiment ID: {self.extracted_info['experiment_id']}")
        print()

        response = input("Would you like me to search Expression Atlas now? (yes/no): ").strip().lower()
        return response in ['yes', 'y', '1', 'true', '是', '好']

    def _search_and_present_results(self):
        """Search Expression Atlas and present results to user."""
        print("\n" + "=" * 70)
        print("Searching Expression Atlas...")
        print("=" * 70)

        if self.extracted_info['experiment_id']:
            # Direct lookup by experiment ID
            self._lookup_experiment(self.extracted_info['experiment_id'])
        else:
            # Search by species and keywords
            self._search_experiments()

    def _lookup_experiment(self, experiment_id: str):
        """Look up a specific experiment by ID."""
        print(f"\nLooking up experiment: {experiment_id}")

        # Get experiment page URL
        exp_url = f"https://www.ebi.ac.uk/gxa/experiments/{experiment_id}"
        print(f"Experiment page: {exp_url}")

        try:
            # Fetch experiment page
            response = requests.get(exp_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract basic info (this is simplified - actual parsing would be more complex)
                title = soup.find('h2')
                if title:
                    print(f"\nExperiment: {title.text.strip()}")

                print(f"\n✓ This experiment exists!")
                print(f"\nTo download data:")
                print(f"1. Visit: {exp_url}")
                print(f"2. Click on the 'Downloads' tab")
                print(f"3. Download the files you need")

                # Ask if user wants to see the page
                response = input("\nWould you like me to provide the download links? (yes/no): ").strip().lower()
                if response in ['yes', 'y', '是']:
                    self._show_download_info(experiment_id)
            else:
                print(f"\n⚠ Could not access experiment page (HTTP {response.status_code})")
                print(f"Please check: {exp_url}")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            print(f"Please visit: {exp_url}")

    def _search_experiments(self):
        """Search for experiments based on extracted information."""
        species = self.extracted_info['species']
        exp_type = self.extracted_info['experiment_type']
        keywords = ' '.join(self.extracted_info['keywords']) if self.extracted_info['keywords'] else None

        print(f"\nSearching for:")
        print(f"  Species: {species}")
        print(f"  Type: {exp_type or 'Any'}")
        print(f"  Keywords: {keywords or 'None'}")

        # Construct search URL
        base_url = "https://www.ebi.ac.uk/gxa/experiments"
        if exp_type:
            base_url = f"https://www.ebi.ac.uk/gxa/{exp_type}/experiments"

        print(f"\n🌐 Browse experiments at: {base_url}")

        # Try to fetch and parse experiments list
        try:
            params = {}
            if species:
                params['species'] = species
            if keywords:
                params['keyword'] = keywords

            response = requests.get(base_url, params=params, timeout=10)
            if response.status_code == 200:
                # For now, just provide the URL
                # Actual parsing would require more detailed HTML analysis
                full_url = response.url
                print(f"\nSearch URL: {full_url}")
                print(f"\nPlease visit this URL to browse available experiments.")
                print(f"Look for experiments matching your criteria.")

                # Suggest popular experiments for the species
                self._suggest_popular_experiments()

        except Exception as e:
            print(f"\n⚠ Could not perform automatic search: {e}")
            self._suggest_popular_experiments()

    def _suggest_popular_experiments(self):
        """Suggest popular experiments based on species."""
        print(f"\n" + "=" * 70)
        print("Popular Experiments")
        print("=" * 70)

        species = self.extracted_info['species']
        exp_type = self.extracted_info['experiment_type'] or 'baseline'

        # Map species to popular experiments
        popular_by_species = {
            'arabidopsis thaliana': {
                'baseline': ['E-MTAB-3358'],
                'differential': []
            },
            'homo sapiens': {
                'baseline': ['E-MTAB-513'],
                'differential': ['E-GEOD-21860']
            },
            'mus musculus': {
                'baseline': ['E-MTAB-5214'],
                'differential': ['E-MTAB-1733']
            }
        }

        if species and species.lower() in popular_by_species:
            exps = popular_by_species[species.lower()].get(exp_type, [])
            if exps:
                print(f"\nFor {species} ({exp_type}):")
                for exp_id in exps:
                    print(f"  • {exp_id}")
                    print(f"    {self.atlas_api.BASE_URL}experiments/{exp_id}")
            else:
                print(f"\nNo pre-configured experiments for {species} ({exp_type})")

        # Always show general popular experiments
        print(f"\nGeneral popular experiments:")
        all_popular = self.atlas_api.get_popular_experiments(exp_type)
        for exp_id in all_popular:
            print(f"  • {exp_id}")
            print(f"    {self.atlas_api.BASE_URL}experiments/{exp_id}")

    def _show_download_info(self, experiment_id: str):
        """Show download information for an experiment."""
        print(f"\n" + "=" * 70)
        print("Download Instructions")
        print("=" * 70)

        print(f"\n1. Visit the experiment page:")
        print(f"   https://www.ebi.ac.uk/gxa/experiments/{experiment_id}")

        print(f"\n2. Available download files typically include:")
        print(f"   - Expression data (TPM/FPKM values)")
        print(f"   - Raw counts (for RNA-seq)")
        print(f"   - Experiment design (sample information)")
        print(f"   - R data objects")

        print(f"\n3. After downloading, load data with:")
        print(f"   ```python")
        print(f"   from expression_atlas import ExpressionAtlasAPI")
        print(f"   api = ExpressionAtlasAPI()")
        print(f"   df = api.load_expression_data('path/to/file.tsv')")
        print(f"   ```")


def main():
    """Main entry point for the smart chat interface."""
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("=" * 70)
        print("⚠ API Key Required")
        print("=" * 70)
        print("\nThis tool requires an Anthropic API key to function.")
        print("\nPlease:")
        print("1. Get an API key from: https://console.anthropic.com/")
        print("2. Create a .env file in this directory with:")
        print("   ANTHROPIC_API_KEY=your_key_here")
        print("\nOr set the environment variable:")
        print("   export ANTHROPIC_API_KEY=your_key_here")
        print("\n" + "=" * 70)
        return

    try:
        chat = SmartExpressionAtlasChat()
        chat.start()
    except Exception as e:
        print(f"\n✗ Error initializing chat: {e}")
        print("\nPlease check your API key and try again.")


if __name__ == "__main__":
    main()
