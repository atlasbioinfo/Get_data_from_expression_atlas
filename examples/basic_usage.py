"""
Basic Usage Examples for Expression Atlas Data Retrieval

This script demonstrates basic usage of the Expression Atlas API.
"""

from expression_atlas import ExpressionAtlasAPI, get_expression_data

# Example 1: Download data using a known experiment ID
print("=" * 70)
print("Example 1: Download data with experiment ID")
print("=" * 70)

# Human tissues baseline experiment
experiment_id = "E-MTAB-513"
output_dir = "./data/human_tissues"

print(f"\nDownloading experiment: {experiment_id}")
print(f"Output directory: {output_dir}\n")

files = get_expression_data(
    experiment_id=experiment_id,
    output_dir=output_dir
)

print(f"\nDownloaded files:")
for file_type, path in files.items():
    print(f"  {file_type}: {path}")


# Example 2: Using the API class directly
print("\n" + "=" * 70)
print("Example 2: Using ExpressionAtlasAPI class")
print("=" * 70)

api = ExpressionAtlasAPI()

# Get experiment information
experiment_id = "E-MTAB-5214"  # Mouse tissues
print(f"\nGetting info for {experiment_id}...")

info = api.get_experiment_info(experiment_id)
print(f"\nExperiment info:")
for key, value in info.items():
    print(f"  {key}: {value}")

# Download specific file types only
print(f"\nDownloading specific file types...")
files = api.download_experiment_data(
    experiment_id=experiment_id,
    output_dir="./data/mouse_tissues",
    file_types=['analytics', 'tpms']  # Only download these files
)


# Example 3: Load and analyze the data
print("\n" + "=" * 70)
print("Example 3: Load and analyze expression data")
print("=" * 70)

if files and 'analytics' in files:
    df = api.load_expression_data(files['analytics'])

    print(f"\nData shape: {df.shape}")
    print(f"\nFirst few rows:")
    print(df.head())

    print(f"\nColumn names:")
    print(df.columns.tolist())


# Example 4: Get list of popular experiments
print("\n" + "=" * 70)
print("Example 4: Browse popular experiments")
print("=" * 70)

print("\nPopular baseline experiments:")
baseline_exps = api.get_popular_experiments("baseline")
for exp_id in baseline_exps:
    print(f"  • {exp_id}")

print("\nPopular differential experiments:")
diff_exps = api.get_popular_experiments("differential")
for exp_id in diff_exps:
    print(f"  • {exp_id}")

print("\n" + "=" * 70)
print("Done!")
print("=" * 70)
