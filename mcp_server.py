#!/usr/bin/env python3
"""
Expression Atlas MCP Server

A Model Context Protocol server that provides tools for retrieving
gene expression data from EMBL-EBI Expression Atlas.
"""

import asyncio
import json
import re
from typing import Any, Optional
from urllib.parse import urljoin
import requests
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from expression_atlas import ExpressionAtlasAPI


# Initialize the MCP server
app = Server("expression-atlas-server")

# Initialize Expression Atlas API
api = ExpressionAtlasAPI()

# Species mapping for common names
SPECIES_MAP = {
    'human': 'homo sapiens',
    'humans': 'homo sapiens',
    'homo sapiens': 'homo sapiens',
    'mouse': 'mus musculus',
    'mice': 'mus musculus',
    'mus musculus': 'mus musculus',
    'rat': 'rattus norvegicus',
    'arabidopsis': 'arabidopsis thaliana',
    'zebrafish': 'danio rerio',
    'fruit fly': 'drosophila melanogaster',
    'drosophila': 'drosophila melanogaster',
    'yeast': 'saccharomyces cerevisiae',
    'c. elegans': 'caenorhabditis elegans',
    'worm': 'caenorhabditis elegans',
}


def browse_ftp_directory(experiment_id: str) -> dict:
    """
    Browse the FTP directory for a given experiment to list all available files.

    Args:
        experiment_id: Experiment accession (e.g., 'E-MTAB-513')

    Returns:
        Dictionary with file listing and metadata
    """
    # Try multiple approaches to list files

    # Approach 1: Try HTTPS access to FTP mirror
    https_ftp_base = f"https://ftp.ebi.ac.uk/pub/databases/microarray/data/atlas/experiments/{experiment_id}/"

    try:
        response = requests.get(https_ftp_base, timeout=30)
        if response.status_code == 200:
            # Parse HTML directory listing
            files = []
            # Look for links in the HTML
            links = re.findall(r'<a href="([^"]+)">', response.text)
            for link in links:
                if not link.startswith('?') and link != '../':
                    files.append(link)

            if files:
                return {
                    'success': True,
                    'experiment_id': experiment_id,
                    'ftp_url': https_ftp_base,
                    'files': files,
                    'method': 'https_ftp_browse'
                }
    except Exception as e:
        pass

    # Approach 2: Try common file patterns
    common_patterns = [
        f"{experiment_id}-tpms.tsv",
        f"{experiment_id}-fpkms.tsv",
        f"{experiment_id}-raw-counts.tsv",
        f"{experiment_id}.condensed-sdrf.tsv",
        f"{experiment_id}.sdrf.txt",
        f"{experiment_id}-configuration.xml",
        f"{experiment_id}-analytics.tsv",
        f"{experiment_id}.Rdata",
    ]

    available_files = []
    for filename in common_patterns:
        file_url = https_ftp_base + filename
        try:
            head_response = requests.head(file_url, timeout=10)
            if head_response.status_code == 200:
                available_files.append({
                    'name': filename,
                    'url': file_url,
                    'size': head_response.headers.get('Content-Length', 'unknown')
                })
        except:
            continue

    if available_files:
        return {
            'success': True,
            'experiment_id': experiment_id,
            'ftp_url': https_ftp_base,
            'files': available_files,
            'method': 'pattern_matching'
        }

    # If nothing worked, return guidance
    return {
        'success': False,
        'experiment_id': experiment_id,
        'ftp_url': https_ftp_base,
        'message': 'Could not automatically list files. Please visit the FTP URL or experiment page.',
        'experiment_page': f"https://www.ebi.ac.uk/gxa/experiments/{experiment_id}"
    }


def identify_expression_files(files_list: list) -> dict:
    """
    Intelligently identify gene expression data files from a list of files.

    Args:
        files_list: List of filenames or file objects

    Returns:
        Dictionary categorizing files by type
    """
    expression_files = {
        'tpms': [],  # Transcripts Per Million
        'fpkms': [],  # Fragments Per Kilobase Million
        'counts': [],  # Raw counts
        'analytics': [],  # Processed analytics
        'metadata': [],  # Sample metadata
        'other': []
    }

    for file_item in files_list:
        # Handle both string filenames and dict objects
        if isinstance(file_item, dict):
            filename = file_item.get('name', '')
        else:
            filename = str(file_item)

        filename_lower = filename.lower()

        # Categorize based on filename patterns
        if 'tpm' in filename_lower and filename_lower.endswith('.tsv'):
            expression_files['tpms'].append(file_item)
        elif 'fpkm' in filename_lower and filename_lower.endswith('.tsv'):
            expression_files['fpkms'].append(file_item)
        elif 'count' in filename_lower and filename_lower.endswith('.tsv'):
            expression_files['counts'].append(file_item)
        elif 'analytics' in filename_lower:
            expression_files['analytics'].append(file_item)
        elif 'sdrf' in filename_lower or 'metadata' in filename_lower:
            expression_files['metadata'].append(file_item)
        elif filename_lower.endswith(('.tsv', '.txt', '.csv')):
            # Other tabular files might contain expression data
            expression_files['other'].append(file_item)
        else:
            expression_files['other'].append(file_item)

    # Determine recommended file for download
    recommended = None
    if expression_files['tpms']:
        recommended = expression_files['tpms'][0]
        recommended_type = 'tpms'
    elif expression_files['fpkms']:
        recommended = expression_files['fpkms'][0]
        recommended_type = 'fpkms'
    elif expression_files['counts']:
        recommended = expression_files['counts'][0]
        recommended_type = 'counts'
    elif expression_files['analytics']:
        recommended = expression_files['analytics'][0]
        recommended_type = 'analytics'

    return {
        'categorized_files': expression_files,
        'recommended_file': recommended,
        'recommended_type': recommended_type if recommended else None,
        'summary': {
            'total_files': len(files_list),
            'expression_files': len(expression_files['tpms']) + len(expression_files['fpkms']) + len(expression_files['counts']),
            'metadata_files': len(expression_files['metadata'])
        }
    }


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_experiments",
            description="Search Expression Atlas for experiments based on species, experiment type, and keywords. Returns a list of matching experiments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "species": {
                        "type": "string",
                        "description": "Species/organism name (e.g., 'human', 'mouse', 'arabidopsis'). Can use common names or scientific names."
                    },
                    "experiment_type": {
                        "type": "string",
                        "enum": ["baseline", "differential"],
                        "description": "Type of experiment: 'baseline' (normal conditions) or 'differential' (comparative studies)"
                    },
                    "keyword": {
                        "type": "string",
                        "description": "Search keywords: gene names, tissues, diseases, or conditions"
                    }
                }
            }
        ),
        Tool(
            name="get_experiment_info",
            description="Get detailed information about a specific experiment by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "Experiment accession ID (e.g., 'E-MTAB-513', 'E-GEOD-21860')"
                    }
                },
                "required": ["experiment_id"]
            }
        ),
        Tool(
            name="browse_experiment_ftp",
            description="Browse the FTP directory for an experiment to see all available data files. This helps identify what gene expression data is available before downloading.",
            inputSchema={
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "Experiment accession ID (e.g., 'E-MTAB-513')"
                    }
                },
                "required": ["experiment_id"]
            }
        ),
        Tool(
            name="identify_expression_files",
            description="Intelligently identify and categorize gene expression data files from a list of files. Returns recommended files to download for expression analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of filenames to analyze"
                    }
                },
                "required": ["files"]
            }
        ),
        Tool(
            name="download_expression_data",
            description="Download gene expression data files for a specific experiment. Can specify which file types to download (tpms, fpkms, counts, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "Experiment accession ID"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to save downloaded files (default: './expression_atlas_data')"
                    },
                    "file_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific file types to download (e.g., ['tpms', 'counts']). If not specified, downloads all available."
                    }
                },
                "required": ["experiment_id"]
            }
        ),
        Tool(
            name="get_popular_experiments",
            description="Get a list of popular/example experiments for a given type. Useful when users are exploring Expression Atlas.",
            inputSchema={
                "type": "object",
                "properties": {
                    "experiment_type": {
                        "type": "string",
                        "enum": ["baseline", "differential"],
                        "description": "Type of experiments to list"
                    }
                },
                "required": ["experiment_type"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""

    try:
        if name == "search_experiments":
            species = arguments.get("species")
            experiment_type = arguments.get("experiment_type")
            keyword = arguments.get("keyword")

            # Normalize species name
            if species:
                species = SPECIES_MAP.get(species.lower(), species.lower())

            # Try to search
            results = api.search_experiments(
                species=species,
                experiment_type=experiment_type,
                keyword=keyword
            )

            if not results:
                # Return popular experiments as fallback
                popular = api.get_popular_experiments(experiment_type or "baseline")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "message": "Could not search via API. Here are some popular experiments:",
                        "popular_experiments": popular,
                        "browse_url": "https://www.ebi.ac.uk/gxa/experiments"
                    }, indent=2)
                )]

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(results),
                    "experiments": results[:10]  # Return first 10
                }, indent=2)
            )]

        elif name == "get_experiment_info":
            experiment_id = arguments["experiment_id"].upper()
            info = api.get_experiment_info(experiment_id)

            # Add experiment page URL
            info['experiment_page'] = f"https://www.ebi.ac.uk/gxa/experiments/{experiment_id}"

            return [TextContent(
                type="text",
                text=json.dumps(info, indent=2)
            )]

        elif name == "browse_experiment_ftp":
            experiment_id = arguments["experiment_id"].upper()
            result = browse_ftp_directory(experiment_id)

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "identify_expression_files":
            files = arguments["files"]
            result = identify_expression_files(files)

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "download_expression_data":
            experiment_id = arguments["experiment_id"].upper()
            output_dir = arguments.get("output_dir", "./expression_atlas_data")
            file_types = arguments.get("file_types")

            downloaded = api.download_experiment_data(
                experiment_id=experiment_id,
                output_dir=output_dir,
                file_types=file_types
            )

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": len(downloaded) > 0,
                    "experiment_id": experiment_id,
                    "downloaded_files": downloaded,
                    "output_directory": output_dir
                }, indent=2)
            )]

        elif name == "get_popular_experiments":
            experiment_type = arguments["experiment_type"]
            experiments = api.get_popular_experiments(experiment_type)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "experiment_type": experiment_type,
                    "popular_experiments": experiments,
                    "info": "These are well-curated example experiments from Expression Atlas"
                }, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }, indent=2)
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
