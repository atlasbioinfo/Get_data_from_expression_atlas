"""
Smart Chat Demo - AI-Powered Expression Atlas Assistant

This example shows how to use the AI-powered chat interface.

Requirements:
- Anthropic API key in .env file
- Run: pip install -r requirements.txt
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from smart_chat import SmartExpressionAtlasChat

def demo_basic_usage():
    """
    Basic usage example
    """
    print("=" * 70)
    print("Smart Chat Demo")
    print("=" * 70)
    print("\nThis demo shows the AI-powered chat interface.")
    print("Make sure you have set ANTHROPIC_API_KEY in your .env file.\n")

    try:
        # Initialize the smart chat
        chat = SmartExpressionAtlasChat()

        print("✓ Smart chat initialized successfully!")
        print("\nStarting interactive chat...")
        print("(Type 'exit' to quit)\n")

        # Start the conversation
        chat.start()

    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease set up your API key:")
        print("1. Copy .env.example to .env")
        print("2. Add your Anthropic API key")
        print("3. Run this demo again")


def demo_example_queries():
    """
    Show example queries that work well
    """
    print("\n" + "=" * 70)
    print("Example Queries")
    print("=" * 70)

    examples = [
        "I need Arabidopsis expression data",
        "Show me human brain expression in different conditions",
        "我需要拟南芥在不同发育阶段的表达数据",
        "Find mouse liver vs kidney differential expression",
        "What experiments are available for zebrafish development?",
        "I want to study gene expression in cancer vs normal tissue"
    ]

    print("\nHere are some example queries you can try:\n")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")

    print("\nThe AI will:")
    print("  • Understand your intent")
    print("  • Extract species, experiment type, and keywords")
    print("  • Ask clarifying questions if needed")
    print("  • Search Expression Atlas")
    print("  • Provide specific experiment recommendations")


if __name__ == "__main__":
    # Show examples first
    demo_example_queries()

    # Ask if user wants to try
    print("\n" + "=" * 70)
    response = input("\nWould you like to start the smart chat now? (yes/no): ").strip().lower()

    if response in ['yes', 'y', '1', 'true']:
        demo_basic_usage()
    else:
        print("\nTo use smart chat later, run: python smart_chat.py")
