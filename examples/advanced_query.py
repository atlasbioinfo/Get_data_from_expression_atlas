"""
Advanced Query Building Example

This demonstrates using the ExpressionAtlasQuery builder
for more complex queries.
"""

from expression_atlas import ExpressionAtlasQuery

# Example 1: Build a query step by step
print("=" * 70)
print("Example 1: Query builder pattern")
print("=" * 70)

query = ExpressionAtlasQuery()

# Chain method calls to build the query
query.set_species("homo sapiens") \
     .set_experiment_type("baseline") \
     .set_keyword("brain")

print("\nQuery parameters:")
print(f"  Species: {query.species}")
print(f"  Type: {query.experiment_type}")
print(f"  Keyword: {query.keyword}")

# Execute search
print("\nExecuting search...")
results = query.execute()

if results:
    print(f"Found {len(results)} results")
else:
    print("No results or API not available")


# Example 2: Download with specific experiment ID
print("\n" + "=" * 70)
print("Example 2: Direct download with query builder")
print("=" * 70)

query2 = ExpressionAtlasQuery()
query2.set_experiment_id("E-MTAB-3358")  # Arabidopsis tissues

print(f"\nDownloading experiment: {query2.experiment_id}")

try:
    files = query2.download(output_dir="./data/arabidopsis")
    print(f"\nDownloaded files:")
    for file_type, path in files.items():
        print(f"  {file_type}: {path}")
except Exception as e:
    print(f"Error: {e}")


# Example 3: Multiple species comparison
print("\n" + "=" * 70)
print("Example 3: Download baseline data for multiple species")
print("=" * 70)

species_experiments = {
    "human": "E-MTAB-513",
    "mouse": "E-MTAB-5214",
    "arabidopsis": "E-MTAB-3358"
}

for species, exp_id in species_experiments.items():
    print(f"\nProcessing {species} ({exp_id})...")

    query = ExpressionAtlasQuery()
    query.set_experiment_id(exp_id)

    output_dir = f"./data/comparison/{species}"
    files = query.download(output_dir=output_dir)

    if files:
        print(f"  ✓ Downloaded {len(files)} file(s) to {output_dir}")
    else:
        print(f"  ✗ Download failed")

print("\n" + "=" * 70)
print("Done!")
print("=" * 70)
