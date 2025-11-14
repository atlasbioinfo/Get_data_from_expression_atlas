# Expression Atlas Data Retrieval Tool

A conversational Python tool for retrieving gene expression data from [EMBL-EBI Expression Atlas](https://www.ebi.ac.uk/gxa/home).

## ⚡ NEW: MCP Server Available!

This tool is now available as a **Model Context Protocol (MCP) server**, allowing Claude and other AI assistants to directly search, browse, and download Expression Atlas data.

**Quick Start with MCP:**
```bash
# Install dependencies
pip install -r requirements.txt

# See MCP_SETUP.md for configuration instructions
```

👉 **[Full MCP Setup Guide](MCP_SETUP.md)** - Configure for Claude Desktop or other MCP clients

## Features

- 🤖 **MCP Server** - Direct integration with Claude and other AI assistants
- 🌟 **Smart Chat** - Natural language interface (supports Chinese & English) - NEW!
- 🔍 Interactive conversation-based interface to specify data requirements
- 🧬 Support for both baseline and differential expression experiments
- 🌍 Filter by species/organism
- 📊 Download expression data in various formats (TSV, R objects)
- 🔌 Access via FTP and web API
- 🧠 Smart file identification - automatically detects gene expression data files

## What is Expression Atlas?

Expression Atlas is an open science resource providing information on gene and protein expression across species and biological conditions. It helps answer questions like:
- Where is a certain gene expressed?
- What genes are expressed in a particular tissue?
- How does gene expression differ between conditions?

## Installation

```bash
pip install -r requirements.txt
```

## Usage Methods

### 🤖 Method 1: MCP Server (Recommended for AI Assistants)

Use with Claude Desktop or any MCP-compatible client:

1. **Configure Claude Desktop** (see [MCP_SETUP.md](MCP_SETUP.md) for details)
2. **Ask Claude naturally:**
   - "Find human brain expression experiments"
   - "Download data for experiment E-MTAB-513"
   - "What files are available for this experiment?"

**MCP Tools Available:**
- `search_experiments` - Search by species, type, keywords
- `browse_experiment_ftp` - List all files in an experiment
- `identify_expression_files` - Smart detection of expression data
- `download_expression_data` - Download with automatic retry
- `get_experiment_info` - Get experiment metadata

👉 See [MCP_SETUP.md](MCP_SETUP.md) for complete setup instructions

## Quick Start (CLI/Python)

### 🌟 Method 2: Smart Chat (Recommended for CLI)

**Get data with one sentence!** Just like talking to an AI:

```bash
python smart_chat.py
```

**Then type what you need in natural language (Chinese or English):**
- "我需要拟南芥seedling的数据"
- "I need human brain expression data"
- "小鼠肝脏表达数据"
- "Download experiment E-MTAB-513"

**The tool automatically:**
1. ✅ Understands your request (supports 中文 & English)
2. ✅ Identifies species, keywords, experiment type
3. ✅ Recommends the best experiment
4. ✅ Browses FTP for available files
5. ✅ Helps you download data

### 💻 Method 3: Step-by-step Chat Interface

```bash
python chat_interface.py
```

The tool will guide you through:
1. Specifying your experiment ID (if known)
2. Or searching by species, experiment type, and keywords
3. Getting direct links to download data from Expression Atlas

### 🐍 Method 4: Programmatic Access

```python
from chat_interface import ExpressionAtlasChat

# Start interactive conversation
chat = ExpressionAtlasChat()
chat.start()
```

### 📁 Method 5: Direct Data Loading (if you have downloaded files)

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

1. **Run the chat interface** to identify your experiment:
   ```bash
   python chat_interface.py
   ```

2. **Visit the experiment page** provided by the tool (e.g., `https://www.ebi.ac.uk/gxa/experiments/E-MTAB-513`)

3. **Manually download** the data files you need from the Downloads tab

4. **Load and analyze** using this tool:
   ```python
   from expression_atlas import ExpressionAtlasAPI
   api = ExpressionAtlasAPI()
   df = api.load_expression_data('path/to/downloaded/file.tsv')
   ```

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
├── mcp_server.py             # 🤖 MCP server for AI assistants
├── smart_chat.py             # 🌟 Smart chat - natural language interface (NEW!)
├── expression_atlas.py       # Main module for data retrieval
├── chat_interface.py         # Step-by-step CLI interface
├── requirements.txt          # Dependencies (includes mcp)
├── MCP_SETUP.md             # MCP server setup guide
├── mcp_config_example.json  # Example MCP configuration
├── examples/                # Usage examples
│   ├── basic_usage.py       # Basic API usage
│   ├── interactive_chat.py  # Chat interface demo
│   ├── advanced_query.py    # Query builder examples
│   └── complete_workflow.py # End-to-end workflow
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
- `E-CURD-1` - Arabidopsis tissues (whole organism, floral bud, rosette)

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