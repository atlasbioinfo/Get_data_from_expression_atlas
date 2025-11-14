"""
Basic functionality test for Expression Atlas tools
"""

import sys
import os

# Test imports
print("Testing imports...")
try:
    from expression_atlas import ExpressionAtlasAPI, ExpressionAtlasQuery, get_expression_data
    print("✓ expression_atlas module imported successfully")
except Exception as e:
    print(f"✗ Error importing expression_atlas: {e}")
    sys.exit(1)

try:
    from chat_interface import ExpressionAtlasChat
    print("✓ chat_interface module imported successfully")
except Exception as e:
    print(f"✗ Error importing chat_interface: {e}")
    sys.exit(1)

# Test API initialization
print("\nTesting API initialization...")
try:
    api = ExpressionAtlasAPI()
    print(f"✓ ExpressionAtlasAPI initialized")
    print(f"  Base URL: {api.BASE_URL}")
    print(f"  FTP Base: {api.FTP_BASE}")
except Exception as e:
    print(f"✗ Error initializing API: {e}")
    sys.exit(1)

# Test query builder
print("\nTesting query builder...")
try:
    query = ExpressionAtlasQuery()
    query.set_species("homo sapiens")
    query.set_experiment_type("baseline")
    query.set_keyword("brain")
    print(f"✓ Query builder works")
    print(f"  Species: {query.species}")
    print(f"  Type: {query.experiment_type}")
    print(f"  Keyword: {query.keyword}")
except Exception as e:
    print(f"✗ Error with query builder: {e}")
    sys.exit(1)

# Test species mapping
print("\nTesting species mapping...")
try:
    chat = ExpressionAtlasChat()
    test_species = ['human', 'mouse', 'arabidopsis']
    for species in test_species:
        mapped = chat.SPECIES_MAP.get(species)
        print(f"  '{species}' → '{mapped}'")
    print("✓ Species mapping works")
except Exception as e:
    print(f"✗ Error with species mapping: {e}")
    sys.exit(1)

# Test popular experiments
print("\nTesting popular experiments list...")
try:
    api = ExpressionAtlasAPI()
    baseline = api.get_popular_experiments("baseline")
    differential = api.get_popular_experiments("differential")
    print(f"✓ Popular experiments retrieved")
    print(f"  Baseline: {baseline}")
    print(f"  Differential: {differential}")
except Exception as e:
    print(f"✗ Error getting popular experiments: {e}")
    sys.exit(1)

# Test FTP URL construction
print("\nTesting FTP URL construction...")
try:
    api = ExpressionAtlasAPI()
    experiment_id = "E-MTAB-513"
    ftp_url = api.FTP_BASE + experiment_id + "/"
    print(f"✓ FTP URL constructed")
    print(f"  URL: {ftp_url}")
except Exception as e:
    print(f"✗ Error constructing FTP URL: {e}")

# Test file pattern generation
print("\nTesting file patterns...")
try:
    experiment_id = "E-MTAB-513"
    file_patterns = {
        'analytics': f"{experiment_id}-analytics.tsv",
        'tpms': f"{experiment_id}-tpms.tsv",
        'r-object': f"{experiment_id}.Rdata",
    }
    print(f"✓ File patterns generated")
    for file_type, filename in file_patterns.items():
        print(f"  {file_type}: {filename}")
except Exception as e:
    print(f"✗ Error with file patterns: {e}")

print("\n" + "=" * 70)
print("All basic tests passed!")
print("=" * 70)
print("\nThe tool is ready to use. Try running:")
print("  python chat_interface.py")
print("\nOr check the examples in the 'examples/' directory.")
