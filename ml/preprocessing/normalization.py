"""Normalization pipeline for RNA expression data."""

import json
import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd

from backend.config import settings
from ml.preprocessing.config import NormalizationConfig

logger = logging.getLogger(__name__)


class NormalizationPipeline:
    """Deterministic normalization pipeline for expression data."""

    def __init__(self, config: Optional[NormalizationConfig] = None):
        """
        Initialize normalization pipeline.

        Args:
            config: Normalization configuration, or None for defaults
        """
        if config is None:
            config = NormalizationConfig()
            # Use global random seed from settings
            config.random_seed = settings.random_seed
        self.config = config
        self._set_random_seed()

    def _set_random_seed(self) -> None:
        """Set random seed for reproducibility."""
        np.random.seed(self.config.random_seed)

    def normalize(
        self,
        expression_matrix: pd.DataFrame,
        output_path: Optional[Path] = None,
    ) -> Tuple[pd.DataFrame, dict]:
        """
        Normalize expression matrix deterministically.

        Args:
            expression_matrix: Gene × sample expression matrix
            output_path: Optional path to save normalized data and config

        Returns:
            Tuple of (normalized_matrix, config_dict)
        """
        logger.info(f"Normalizing expression matrix: {expression_matrix.shape}")

        # Make a copy to avoid modifying original
        normalized = expression_matrix.copy()

        # Step 1: Log normalization
        if self.config.use_log1p:
            # log1p(x) = log(1 + x) handles zeros gracefully
            normalized = np.log1p(normalized)
            logger.info("Applied log1p normalization")
        else:
            # Standard log with base
            if self.config.log_base == 2.0:
                normalized = np.log2(normalized + 1)
            elif self.config.log_base == 10.0:
                normalized = np.log10(normalized + 1)
            else:
                normalized = np.log(normalized + 1) / np.log(self.config.log_base)
            logger.info(f"Applied log normalization (base={self.config.log_base})")

        # Step 2: Optional batch correction (placeholder)
        if self.config.apply_batch_correction:
            logger.warning("Batch correction requested but not implemented in Phase 1")
            # Placeholder for future implementation

        # Step 3: Optional scaling
        if self.config.scale_to_unit_variance:
            # Scale each gene to unit variance
            gene_stds = normalized.std(axis=1)
            gene_stds[gene_stds == 0] = 1  # Avoid division by zero
            normalized = normalized.div(gene_stds, axis=0)
            logger.info("Applied unit variance scaling")

        if self.config.center_mean:
            # Center each gene to zero mean
            gene_means = normalized.mean(axis=1)
            normalized = normalized.sub(gene_means, axis=0)
            logger.info("Applied mean centering")

        # Convert back to DataFrame
        normalized_df = pd.DataFrame(
            normalized,
            index=expression_matrix.index,
            columns=expression_matrix.columns,
        )

        # Create config dict for logging
        config_dict = self.config.to_dict()
        config_dict["input_shape"] = list(expression_matrix.shape)
        config_dict["output_shape"] = list(normalized_df.shape)

        # Save if output path provided
        if output_path:
            self._save_normalized_data(normalized_df, config_dict, output_path)

        logger.info(f"Normalization complete: {normalized_df.shape}")
        return normalized_df, config_dict

    def _save_normalized_data(
        self, normalized_df: pd.DataFrame, config_dict: dict, output_path: Path
    ) -> None:
        """
        Save normalized data and configuration.

        Args:
            normalized_df: Normalized expression matrix
            config_dict: Configuration dictionary
            output_path: Path to save data
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save normalized matrix as parquet
        parquet_path = output_path.with_suffix(".parquet")
        normalized_df.to_parquet(parquet_path)
        logger.info(f"Saved normalized matrix: {parquet_path}")

        # Save configuration as JSON
        config_path = output_path.with_suffix(".config.json")
        with open(config_path, "w") as f:
            json.dump(config_dict, f, indent=2)
        logger.info(f"Saved normalization config: {config_path}")

    def load_normalized_data(
        self, parquet_path: Path, config_path: Optional[Path] = None
    ) -> Tuple[pd.DataFrame, dict]:
        """
        Load previously normalized data.

        Args:
            parquet_path: Path to normalized data parquet file
            config_path: Optional path to config JSON

        Returns:
            Tuple of (normalized_matrix, config_dict)
        """
        # Load normalized matrix
        normalized_df = pd.read_parquet(parquet_path)

        # Load config if provided
        if config_path and config_path.exists():
            with open(config_path, "r") as f:
                config_dict = json.load(f)
        else:
            # Try to find config file with same name
            config_path = parquet_path.with_suffix(".config.json")
            if config_path.exists():
                with open(config_path, "r") as f:
                    config_dict = json.load(f)
            else:
                config_dict = {"warning": "Config file not found"}

        return normalized_df, config_dict
