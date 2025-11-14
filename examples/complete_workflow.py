"""
Complete Workflow Example for Expression Atlas Tool

This example demonstrates the full workflow:
1. Finding experiments using the interactive chat
2. Getting experiment information
3. Manual download guidance
4. Loading and analyzing data
"""

import sys
from pathlib import Path
# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from expression_atlas import ExpressionAtlasAPI
from chat_interface import ExpressionAtlasChat

def demo_chat_interface():
    """
    Demo 1: Using the interactive chat interface
    """
    print("=" * 70)
    print("Demo 1: Interactive Chat Interface")
    print("=" * 70)
    print("\nThis will guide you through finding the right experiment.")
    print("Uncomment the next line to try it:\n")
    print("# chat = ExpressionAtlasChat()")
    print("# chat.start()")
    print("\nFor this demo, we'll skip the interactive part.\n")


def demo_experiment_info():
    """
    Demo 2: Getting experiment information
    """
    print("=" * 70)
    print("Demo 2: Get Experiment Information")
    print("=" * 70)

    api = ExpressionAtlasAPI()

    # Show popular experiments
    print("\nPopular baseline experiments:")
    baseline = api.get_popular_experiments("baseline")
    for exp_id in baseline:
        print(f"  • {exp_id}")
        print(f"    View at: https://www.ebi.ac.uk/gxa/experiments/{exp_id}")

    print("\nPopular differential experiments:")
    differential = api.get_popular_experiments("differential")
    for exp_id in differential:
        print(f"  • {exp_id}")
        print(f"    View at: https://www.ebi.ac.uk/gxa/experiments/{exp_id}")


def demo_manual_download_guide():
    """
    Demo 3: Manual download guidance
    """
    print("\n" + "=" * 70)
    print("Demo 3: Manual Download Guide")
    print("=" * 70)

    experiment_id = "E-MTAB-513"  # Human tissues

    print(f"\nTo download data for experiment {experiment_id}:")
    print(f"\n1. Visit the experiment page:")
    print(f"   https://www.ebi.ac.uk/gxa/experiments/{experiment_id}")

    print(f"\n2. Click on the 'Downloads' tab")

    print(f"\n3. Download the files you need:")
    print(f"   - For gene expression: Download 'Expression Data' (TPMs)")
    print(f"   - For sample info: Download 'Experiment Design'")
    print(f"   - For R analysis: Download 'R Data Object'")

    print(f"\n4. Save files to a local directory, e.g.:")
    print(f"   ./data/{experiment_id}/")

    print(f"\n5. Use this tool to load and analyze the data (see next demo)")


def demo_data_loading():
    """
    Demo 4: Loading downloaded data
    """
    print("\n" + "=" * 70)
    print("Demo 4: Loading Downloaded Data")
    print("=" * 70)

    # This would work if you have actually downloaded a file
    example_file = "./data/E-MTAB-513-tpms.tsv"

    print(f"\nOnce you've downloaded a file, load it like this:\n")
    print("```python")
    print("from expression_atlas import ExpressionAtlasAPI")
    print("import pandas as pd")
    print("")
    print("api = ExpressionAtlasAPI()")
    print(f"df = api.load_expression_data('{example_file}')")
    print("")
    print("# View basic info")
    print("print(f'Shape: {df.shape}')")
    print("print(f'Columns: {df.columns.tolist()}')")
    print("")
    print("# Filter data")
    print("if 'brain' in df.columns:")
    print("    brain_genes = df[df['brain'] > 10]")
    print("    print(f'Genes expressed in brain: {len(brain_genes)}')")
    print("")
    print("# Export results")
    print("df.to_csv('./results/processed.csv', index=False)")
    print("```")


def demo_data_analysis():
    """
    Demo 5: Example data analysis workflow
    """
    print("\n" + "=" * 70)
    print("Demo 5: Data Analysis Example")
    print("=" * 70)

    print("\nExample analysis workflow:\n")
    print("```python")
    print("import pandas as pd")
    print("import matplotlib.pyplot as plt")
    print("from expression_atlas import ExpressionAtlasAPI")
    print("")
    print("# Load data")
    print("api = ExpressionAtlasAPI()")
    print("df = api.load_expression_data('E-MTAB-513-tpms.tsv')")
    print("")
    print("# Identify tissue columns (excluding Gene ID, Name, etc.)")
    print("tissue_cols = [col for col in df.columns ")
    print("               if col not in ['Gene ID', 'Gene Name']]")
    print("")
    print("# Find genes expressed in specific tissues")
    print("brain_genes = df[df['brain'] > 50]  # TPM > 50")
    print("liver_genes = df[df['liver'] > 50]")
    print("")
    print("# Find tissue-specific genes (high in one, low in others)")
    print("brain_specific = brain_genes[")
    print("    (brain_genes[tissue_cols].drop('brain', axis=1) < 10).all(axis=1)")
    print("]")
    print("")
    print("# Visualization")
    print("plt.figure(figsize=(10, 6))")
    print("df[['brain', 'liver', 'heart']].hist(bins=50)")
    print("plt.suptitle('Gene Expression Distribution Across Tissues')")
    print("plt.savefig('expression_distribution.png')")
    print("")
    print("# Export filtered results")
    print("brain_specific.to_csv('brain_specific_genes.csv', index=False)")
    print("```")


def main():
    """
    Run all demos
    """
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Expression Atlas Tool - Complete Workflow" + " " * 12 + "║")
    print("╚" + "=" * 68 + "╝")

    demo_chat_interface()
    demo_experiment_info()
    demo_manual_download_guide()
    demo_data_loading()
    demo_data_analysis()

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print("\n✓ This tool helps you:")
    print("  1. Identify experiments through interactive questions")
    print("  2. Map species names to scientific names")
    print("  3. Classify experiment types (baseline vs differential)")
    print("  4. Get direct links to experiment pages")
    print("  5. Load and analyze downloaded data with pandas")
    print("\n⚠ Note: Due to Expression Atlas access restrictions,")
    print("  automated downloads are not available. Manual download")
    print("  from the web interface is required.")
    print("\n📚 For more information:")
    print("  - See USAGE_GUIDE.md for detailed Chinese documentation")
    print("  - Check examples/ directory for more code samples")
    print("  - Visit https://www.ebi.ac.uk/gxa/home")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
