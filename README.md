# Expression Atlas Data Retrieval Tool

A conversational Python tool for retrieving gene expression data from [EMBL-EBI Expression Atlas](https://www.ebi.ac.uk/gxa/home).

## ✨ New: AI-Powered Smart Chat

Now with **Claude AI integration** for natural language queries!

Simply say: *"I need Arabidopsis expression data"* or *"我需要拟南芥在不同发育阶段的表达数据"*

The AI will:
- Understand your intent
- Query Expression Atlas for available experiments
- Ask clarifying questions based on what it finds
- Guide you to the right data

## Features

- 🤖 **AI-powered natural language interface** (using Claude API)
- 🔍 Traditional interactive Q&A interface
- 🧬 Support for both baseline and differential expression experiments
- 🌍 Filter by species/organism
- 📊 Load and analyze expression data in pandas
- 🌐 Real-time queries to Expression Atlas website

## What is Expression Atlas?

Expression Atlas is an open science resource providing information on gene and protein expression across species and biological conditions. It helps answer questions like:
- Where is a certain gene expressed?
- What genes are expressed in a particular tissue?
- How does gene expression differ between conditions?

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Setup API Key (for AI features)

1. Get an API key from [Anthropic Console](https://console.anthropic.com/)
2. Create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and add your key:
   ANTHROPIC_API_KEY=your_key_here
   ```

### Method 1: AI-Powered Smart Chat (⭐ Recommended)

**Natural language queries with Claude AI:**

```bash
python smart_chat.py
```

Then just talk naturally:
```
You: I need Arabidopsis expression data
Assistant: Great! I can help you find Arabidopsis expression data.
          Could you tell me what type of data you're looking for?
          - Baseline: expression across tissues/developmental stages
          - Differential: comparison between conditions

You: baseline, developmental stages
Assistant: Perfect! Let me search for Arabidopsis baseline experiments
          focusing on developmental stages...
```

The AI understands natural language and asks smart follow-up questions!

### Method 2: Traditional Q&A Interface

**Guided step-by-step questions:**

```bash
python chat_interface.py
```

### Method 3: Programmatic Access

```python
from chat_interface import ExpressionAtlasChat

chat = ExpressionAtlasChat()
chat.start()
```

### Method 4: Direct Data Loading (if you have downloaded files)

```python
from expression_atlas import ExpressionAtlasAPI

api = ExpressionAtlasAPI()

# Load already downloaded TSV file
df = api.load_expression_data('./data/E-MTAB-513-tpms.tsv')
print(df.head())
```

## Important Note About Data Access

**Expression Atlas has access restrictions on automated downloads.** This tool provides:

1. ✅ **Interactive guidance** to help you identify the right experiments
2. ✅ **Direct links** to Expression Atlas pages where you can manually download data
3. ✅ **Data loading utilities** to work with downloaded files
4. ✅ **Species mapping** and experiment type classification
5. ⚠️ **Automated downloads may not work** due to server restrictions

### Recommended Workflow

#### With AI (Smart Chat):

1. **Run smart chat** and describe what you need:
   ```bash
   python smart_chat.py
   ```

2. **Have a natural conversation** - the AI will ask follow-up questions

3. **Get experiment recommendations** based on your requirements

4. **Visit the provided URL** to manually download data

5. **Load and analyze** using the tool

#### Without AI (Traditional):

1. **Run traditional chat** for guided questions:
   ```bash
   python chat_interface.py
   ```

2. **Answer step-by-step questions** about species, type, etc.

3. **Get experiment links** and download manually

4. **Load data** using the API

## Data Types

### Baseline Experiments
Shows gene expression in normal, untreated conditions across different:
- Tissues and cell types
- Developmental stages
- Organisms (human, mouse, Arabidopsis, etc.)

### Differential Experiments
Compares gene expression between different:
- Treatment vs control
- Disease vs healthy
- Time points
- Genotypes

## Project Structure

```
.
├── expression_atlas.py      # Main module for data retrieval
├── chat_interface.py         # Conversational interface
├── requirements.txt          # Dependencies
├── examples/                 # Usage examples
│   ├── basic_usage.py       # Basic API usage
│   ├── interactive_chat.py  # Chat interface demo
│   └── advanced_query.py    # Query builder examples
├── USAGE_GUIDE.md           # Detailed Chinese usage guide
└── test_basic.py            # Basic functionality tests
```

## Example: Complete Workflow

Here's a complete example of using the tool:

```python
from chat_interface import ExpressionAtlasChat
from expression_atlas import ExpressionAtlasAPI
import pandas as pd

# Step 1: Use chat interface to find experiments
print("=== Step 1: Find Experiments ===")
chat = ExpressionAtlasChat()
# This will guide you through questions and provide experiment URLs

# Step 2: Manually download from the provided URL
# Visit: https://www.ebi.ac.uk/gxa/experiments/E-MTAB-513
# Download the TPMs file to ./data/

# Step 3: Load and analyze the data
print("\n=== Step 2: Load and Analyze Data ===")
api = ExpressionAtlasAPI()
df = api.load_expression_data('./data/E-MTAB-513-tpms.tsv')

# Step 4: Basic analysis
print(f"\nDataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()[:5]}...")

# Filter for highly expressed genes in a specific tissue
if 'brain' in df.columns:
    high_expr_genes = df[df['brain'] > 100]
    print(f"\nGenes highly expressed in brain: {len(high_expr_genes)}")

# Export results
df.to_csv('./results/processed_data.csv', index=False)
print("\nAnalysis complete!")
```

## Popular Experiments

The tool includes pre-configured popular experiment IDs:

**Baseline Experiments:**
- `E-MTAB-513` - Human tissues (Illumina Body Map)
- `E-MTAB-5214` - Mouse tissues
- `E-MTAB-3358` - Arabidopsis tissues

**Differential Experiments:**
- `E-GEOD-21860` - Cancer vs normal tissues
- `E-MTAB-1733` - Drug treatment studies

## Contributing

Contributions are welcome! This tool provides a foundation for working with Expression Atlas data. Potential improvements:
- Additional data parsing utilities
- Visualization helpers
- Integration with other bioinformatics tools
- Enhanced search capabilities

## Resources

- **Expression Atlas**: https://www.ebi.ac.uk/gxa/home
- **Help Documentation**: https://www.ebi.ac.uk/gxa/help/index.html
- **Browse Experiments**: https://www.ebi.ac.uk/gxa/experiments
- **中文使用指南**: See `USAGE_GUIDE.md` for detailed Chinese documentation

## License

MIT License - See LICENSE file for details