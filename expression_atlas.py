"""
Expression Atlas Data Retrieval Module

This module provides classes and functions to access gene expression data
from EMBL-EBI Expression Atlas (https://www.ebi.ac.uk/gxa/home).
"""

import requests
import json
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin
import pandas as pd
from pathlib import Path


class ExpressionAtlasAPI:
    """
    Class to interact with Expression Atlas API and FTP resources.

    Provides methods to search for experiments, retrieve metadata,
    and download expression data.
    """

    BASE_URL = "https://www.ebi.ac.uk/gxa/"
    FTP_BASE = "ftp://ftp.ebi.ac.uk/pub/databases/microarray/data/atlas/experiments/"
    WEB_DOWNLOAD_BASE = "https://www.ebi.ac.uk/gxa/experiments-content/"

    def __init__(self):
        """Initialize the Expression Atlas API client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ExpressionAtlasClient/1.0'
        })

    def search_experiments(
        self,
        species: Optional[str] = None,
        experiment_type: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for experiments in Expression Atlas.

        Args:
            species: Species name (e.g., 'homo sapiens', 'mus musculus')
            experiment_type: 'baseline' or 'differential'
            keyword: Search keyword (gene name, disease, tissue, etc.)

        Returns:
            List of experiment dictionaries with metadata
        """
        # Try to search via the web interface endpoints
        # Note: This may need to be adjusted based on actual API endpoints
        search_url = urljoin(self.BASE_URL, "json/experiments")

        params = {}
        if species:
            params['species'] = species
        if experiment_type:
            params['experimentType'] = experiment_type
        if keyword:
            params['geneQuery'] = keyword

        try:
            response = self.session.get(search_url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API returned status {response.status_code}, trying alternative method...")
                return self._search_via_web_scraping(species, experiment_type, keyword)
        except Exception as e:
            print(f"Error searching experiments: {e}")
            return []

    def _search_via_web_scraping(
        self,
        species: Optional[str] = None,
        experiment_type: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> List[Dict]:
        """
        Alternative search method using web interface.

        This is a fallback when API endpoints are not available.
        """
        # This would need to be implemented based on the actual web interface
        # For now, return a helpful message
        print("Direct API access not available. Please use the web interface at:")
        print(f"{self.BASE_URL}home")
        return []

    def get_experiment_info(self, experiment_id: str) -> Dict:
        """
        Get detailed information about a specific experiment.

        Args:
            experiment_id: Experiment accession (e.g., 'E-MTAB-513', 'E-GEOD-12345')

        Returns:
            Dictionary with experiment metadata
        """
        info_url = urljoin(self.BASE_URL, f"json/experiments/{experiment_id}")

        try:
            response = self.session.get(info_url, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Could not retrieve info for {experiment_id}")
                return {"experiment_id": experiment_id, "error": response.status_code}
        except Exception as e:
            print(f"Error getting experiment info: {e}")
            return {"experiment_id": experiment_id, "error": str(e)}

    def download_experiment_data(
        self,
        experiment_id: str,
        output_dir: str = ".",
        file_types: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Download expression data files for an experiment.

        Args:
            experiment_id: Experiment accession (e.g., 'E-MTAB-513')
            output_dir: Directory to save downloaded files
            file_types: List of file types to download
                       (e.g., ['tsv', 'analytics', 'r-object'])
                       If None, downloads all available files

        Returns:
            Dictionary mapping file type to local file path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        downloaded_files = {}

        # Common file patterns for Expression Atlas experiments
        # Note: Different experiments may have different file naming conventions
        file_patterns = {
            'tpms': f"{experiment_id}-tpms.tsv",
            'fpkms': f"{experiment_id}-fpkms.tsv",
            'counts': f"{experiment_id}-raw-counts.tsv",
            'condensed-sdrf': f"{experiment_id}.condensed-sdrf.tsv",
            'design': f"{experiment_id}.sdrf.txt",
            'coexpressions': f"{experiment_id}-tpms-coexpressions.tsv.gz",
        }

        # Filter file types if specified
        if file_types:
            file_patterns = {k: v for k, v in file_patterns.items() if k in file_types}

        base_ftp = self.FTP_BASE + f"{experiment_id}/"

        for file_type, filename in file_patterns.items():
            local_path = output_path / filename

            # Try web API first (more reliable with requests library)
            print(f"Downloading {file_type}...")
            web_success = self._try_web_download(
                experiment_id, file_type, local_path
            )

            if web_success:
                downloaded_files[file_type] = str(local_path)
                continue

            # If web API fails, try direct HTTPS to FTP mirror
            # Some EBI FTP servers are also accessible via HTTPS
            http_ftp_url = base_ftp.replace('ftp://', 'https://')
            file_url = http_ftp_url + filename

            try:
                response = self.session.get(file_url, timeout=60)

                if response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    downloaded_files[file_type] = str(local_path)
                    print(f"  ✓ Downloaded via FTP mirror: {local_path}")
                else:
                    print(f"  ✗ File not available from either source")

            except Exception as e:
                print(f"  ✗ Could not download {file_type}")

        if not downloaded_files:
            print(f"\nNo files were downloaded. You can browse available files at:")
            print(f"{base_ftp}")
            print(f"\nOr visit the experiment page at:")
            print(f"{self.BASE_URL}experiments/{experiment_id}")

        return downloaded_files

    def _try_web_download(
        self,
        experiment_id: str,
        file_type: str,
        local_path: Path
    ) -> bool:
        """
        Try downloading via the web API endpoint as a fallback.

        Args:
            experiment_id: Experiment accession
            file_type: Type of file to download
            local_path: Local path to save the file

        Returns:
            True if download successful, False otherwise
        """
        # Map file types to web API resource names
        resource_map = {
            'tpms': 'tpms.tsv',
            'fpkms': 'fpkms.tsv',
            'counts': 'raw-counts.tsv',
        }

        if file_type not in resource_map:
            return False

        # Determine experiment type (baseline or differential)
        # Try baseline first, then differential
        for exp_type in ['RnaSeqBaseline', 'RnaSeqDifferential', 'ProteomicsBaseline']:
            web_url = (
                f"{self.WEB_DOWNLOAD_BASE}{experiment_id}/"
                f"resources/ExperimentDownloadSupplier.{exp_type}/"
                f"{resource_map[file_type]}"
            )

            try:
                response = self.session.get(web_url, timeout=60)
                if response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    print(f"  ✓ Downloaded via web API: {local_path}")
                    return True
            except Exception:
                continue

        return False

    def load_expression_data(self, tsv_file: str) -> pd.DataFrame:
        """
        Load expression data from a TSV file into a pandas DataFrame.

        Args:
            tsv_file: Path to TSV file

        Returns:
            DataFrame with expression data
        """
        try:
            df = pd.read_csv(tsv_file, sep='\t')
            print(f"Loaded expression data: {df.shape[0]} rows × {df.shape[1]} columns")
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()

    def get_popular_experiments(self, experiment_type: str = "baseline") -> List[str]:
        """
        Get a list of popular/example experiment IDs.

        Args:
            experiment_type: 'baseline' or 'differential'

        Returns:
            List of experiment accession IDs
        """
        # These are example experiments from Expression Atlas
        popular_experiments = {
            "baseline": [
                "E-MTAB-513",   # Human tissues
                "E-MTAB-5214",  # Mouse tissues
                "E-MTAB-3358",  # Arabidopsis tissues
            ],
            "differential": [
                "E-GEOD-21860",  # Cancer vs normal
                "E-MTAB-1733",   # Drug treatment
            ]
        }

        return popular_experiments.get(experiment_type, [])


class ExpressionAtlasQuery:
    """
    Helper class to build and execute Expression Atlas queries.
    """

    def __init__(self):
        self.api = ExpressionAtlasAPI()
        self.species = None
        self.experiment_type = None
        self.keyword = None
        self.experiment_id = None

    def set_species(self, species: str):
        """Set the species filter."""
        self.species = species.lower()
        return self

    def set_experiment_type(self, exp_type: str):
        """Set experiment type (baseline or differential)."""
        if exp_type.lower() in ['baseline', 'differential']:
            self.experiment_type = exp_type.lower()
        else:
            raise ValueError("experiment_type must be 'baseline' or 'differential'")
        return self

    def set_keyword(self, keyword: str):
        """Set search keyword (gene, tissue, disease, etc.)."""
        self.keyword = keyword
        return self

    def set_experiment_id(self, exp_id: str):
        """Set specific experiment ID."""
        self.experiment_id = exp_id
        return self

    def execute(self):
        """Execute the query and return results."""
        if self.experiment_id:
            return self.api.get_experiment_info(self.experiment_id)
        else:
            return self.api.search_experiments(
                species=self.species,
                experiment_type=self.experiment_type,
                keyword=self.keyword
            )

    def download(self, output_dir: str = "."):
        """Download data for the specified experiment."""
        if not self.experiment_id:
            raise ValueError("Must set experiment_id before downloading")
        return self.api.download_experiment_data(self.experiment_id, output_dir)


# Convenience function
def get_expression_data(
    experiment_id: str,
    output_dir: str = ".",
    file_types: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Convenience function to download Expression Atlas data.

    Args:
        experiment_id: Experiment accession (e.g., 'E-MTAB-513')
        output_dir: Directory to save files
        file_types: Specific file types to download

    Returns:
        Dictionary of downloaded files

    Example:
        >>> files = get_expression_data('E-MTAB-513', output_dir='./data')
        >>> print(files)
    """
    api = ExpressionAtlasAPI()
    return api.download_experiment_data(experiment_id, output_dir, file_types)
