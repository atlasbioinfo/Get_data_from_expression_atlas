# MCP Server Setup Guide

## 🎯 What is MCP?

**Model Context Protocol (MCP)** is a standard protocol that allows AI assistants like Claude to interact with external tools and data sources. This Expression Atlas MCP server provides Claude with tools to search, browse, and download gene expression data.

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `mcp` - Model Context Protocol SDK
- `requests` - For HTTP requests
- `pandas` - For data handling
- `python-dotenv` - For environment configuration

### 2. Test the MCP Server

Run the server directly to verify it works:

```bash
python mcp_server.py
```

The server communicates via stdio (standard input/output), so you won't see output unless connected to an MCP client.

## 🔧 Configuration

### For Claude Desktop

1. **Locate your Claude Desktop config file:**

   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add the Expression Atlas server:**

   ```json
   {
     "mcpServers": {
       "expression-atlas": {
         "command": "python",
         "args": [
           "/absolute/path/to/Get_data_from_expression_atlas/mcp_server.py"
         ],
         "env": {}
       }
     }
   }
   ```

   **Important**: Replace `/absolute/path/to/` with the actual full path to your installation!

3. **Restart Claude Desktop**

4. **Verify the connection:**
   - Look for a 🔌 icon in Claude Desktop
   - Ask Claude: "What MCP tools do you have access to?"
   - You should see the Expression Atlas tools listed

### For Other MCP Clients

If you're using another MCP client (e.g., custom application), configure it to run:

```bash
python /path/to/mcp_server.py
```

The server uses stdio for communication, following the standard MCP protocol.

## 🛠️ Available Tools

Once configured, Claude can use these tools:

### 1. `search_experiments`
Search for experiments by species, type, and keywords.

**Example prompts:**
- "Search for human brain expression experiments"
- "Find differential expression experiments in mice"

### 2. `get_experiment_info`
Get detailed information about a specific experiment.

**Example prompts:**
- "Get info for experiment E-MTAB-513"
- "What is experiment E-GEOD-21860 about?"

### 3. `browse_experiment_ftp`
List all files available in an experiment's FTP directory.

**Example prompts:**
- "Browse the FTP for experiment E-MTAB-513"
- "What files are available for E-GEOD-21860?"

### 4. `identify_expression_files`
Intelligently identify gene expression data files from a list.

**Example prompts:**
- "Which files contain gene expression data?"
- "What's the recommended file to download?"

### 5. `download_expression_data`
Download gene expression data files.

**Example prompts:**
- "Download expression data for E-MTAB-513"
- "Get the TPM data for this experiment"

### 6. `get_popular_experiments`
Get a list of popular example experiments.

**Example prompts:**
- "Show me popular baseline experiments"
- "What are some example differential expression studies?"

## 💡 Usage Examples

### Example 1: Complete Workflow

**User:** "I need human tissue expression data"

**Claude will:**
1. Use `search_experiments` with species="human", type="baseline"
2. Suggest experiment E-MTAB-513 (Human Body Map)
3. Use `browse_experiment_ftp` to see available files
4. Use `identify_expression_files` to recommend the TPM file
5. Use `download_expression_data` to download the data

### Example 2: Specific Experiment

**User:** "Download data for experiment E-MTAB-513"

**Claude will:**
1. Use `get_experiment_info` to verify the experiment
2. Use `browse_experiment_ftp` to see what's available
3. Use `download_expression_data` to get the files
4. Confirm the download location

### Example 3: Exploratory Search

**User:** "I'm interested in cancer gene expression studies"

**Claude will:**
1. Use `search_experiments` with keyword="cancer", type="differential"
2. Present matching experiments
3. Help you browse and download relevant data

## 🐛 Troubleshooting

### Server doesn't appear in Claude Desktop

1. **Check the config path is correct:**
   ```bash
   # macOS/Linux
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Or check your specific OS location
   ```

2. **Verify Python path:**
   ```bash
   which python  # or which python3
   ```
   Use the full path in your config if needed

3. **Check file permissions:**
   ```bash
   chmod +x mcp_server.py
   ```

4. **Test the server manually:**
   ```bash
   python mcp_server.py
   ```

### Tools not working

1. **Check dependencies are installed:**
   ```bash
   pip list | grep -E "(mcp|requests|pandas)"
   ```

2. **Check for error messages in Claude Desktop logs**

3. **Verify internet connectivity** (needed to access Expression Atlas)

### Downloads failing

- Expression Atlas has rate limits and access restrictions
- Some downloads may require manual intervention
- The server provides direct FTP URLs as fallback

## 🔐 Security Notes

- The server runs locally on your machine
- No API keys or authentication required
- Downloads go to the directory you specify
- All data comes from public Expression Atlas resources

## 📚 Additional Resources

- **Expression Atlas**: https://www.ebi.ac.uk/gxa/home
- **MCP Documentation**: https://modelcontextprotocol.io
- **Claude Desktop**: https://claude.ai/download

## 🆘 Getting Help

If you encounter issues:
1. Check this setup guide
2. Review the main README.md
3. Check Expression Atlas documentation
4. Open an issue on GitHub
