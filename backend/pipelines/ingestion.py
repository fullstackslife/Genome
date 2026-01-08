"""Data ingestion pipeline for RNA expression data."""

import csv
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import anndata as ad
import numpy as np
import pandas as pd

from backend.config import settings
from backend.schemas.data_schemas import ExpressionMatrix, IngestedData, Metadata


class IngestionService:
    """Service for ingesting RNA expression data."""

    def __init__(self):
        """Initialize ingestion service."""
        self.processed_dir = settings.processed_dir
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def ingest_bulk_rnaseq(
        self, file_path: Path, delimiter: str = ","
    ) -> IngestedData:
        """
        Ingest bulk RNA-seq data from CSV/TSV file.

        Expected format: genes as rows, samples as columns
        First column should be gene IDs/names

        Args:
            file_path: Path to CSV/TSV file
            delimiter: Delimiter character (default: comma)

        Returns:
            IngestedData object with expression matrix and metadata
        """
        try:
            # Read CSV/TSV
            df = pd.read_csv(file_path, delimiter=delimiter, index_col=0)

            # Extract gene and sample IDs
            gene_ids = df.index.tolist()
            sample_ids = df.columns.tolist()

            # Convert to numpy array
            expression_values = df.values.tolist()

            # Create expression matrix
            expression_matrix = ExpressionMatrix(
                gene_ids=gene_ids,
                sample_ids=sample_ids,
                expression_values=expression_values,
            )

            # Create metadata (minimal - no identifying information)
            metadata_list = [
                Metadata(
                    sample_id=sample_id,
                    metadata={"source": "bulk_rnaseq", "format": "csv"},
                    provenance=str(file_path),
                    timestamp=datetime.now(),
                )
                for sample_id in sample_ids
            ]

            # Generate ingestion ID
            ingestion_id = str(uuid.uuid4())

            ingested_data = IngestedData(
                expression_matrix=expression_matrix,
                metadata=metadata_list,
                ingestion_id=ingestion_id,
                ingested_at=datetime.now(),
                format="bulk_csv",
            )

            # Save ingested data
            self._save_ingested_data(ingested_data)

            return ingested_data

        except Exception as e:
            raise ValueError(f"Failed to ingest bulk RNA-seq data: {str(e)}") from e

    def ingest_h5ad(self, file_path: Path) -> IngestedData:
        """
        Ingest single-cell RNA-seq data from .h5ad (AnnData) file.

        Args:
            file_path: Path to .h5ad file

        Returns:
            IngestedData object with expression matrix and metadata
        """
        try:
            # Read AnnData object
            adata = ad.read_h5ad(file_path)

            # Extract expression matrix (genes × cells)
            # AnnData stores as cells × genes, so transpose
            expression_df = pd.DataFrame(
                adata.X.toarray() if hasattr(adata.X, "toarray") else adata.X,
                index=adata.obs.index,
                columns=adata.var.index,
            ).T

            gene_ids = expression_df.index.tolist()
            sample_ids = expression_df.columns.tolist()
            expression_values = expression_df.values.tolist()

            # Create expression matrix
            expression_matrix = ExpressionMatrix(
                gene_ids=gene_ids,
                sample_ids=sample_ids,
                expression_values=expression_values,
            )

            # Extract metadata from AnnData obs (cell metadata)
            # Only include non-identifying metadata
            metadata_list = []
            for sample_id in sample_ids:
                sample_obs = adata.obs.loc[sample_id]
                # Convert to dict, excluding potential identifiers
                sample_metadata = {
                    k: str(v) for k, v in sample_obs.items() if not self._is_identifier(k)
                }
                sample_metadata["source"] = "single_cell"
                sample_metadata["format"] = "h5ad"

                metadata_list.append(
                    Metadata(
                        sample_id=sample_id,
                        metadata=sample_metadata,
                        provenance=str(file_path),
                        timestamp=datetime.now(),
                    )
                )

            # Generate ingestion ID
            ingestion_id = str(uuid.uuid4())

            ingested_data = IngestedData(
                expression_matrix=expression_matrix,
                metadata=metadata_list,
                ingestion_id=ingestion_id,
                ingested_at=datetime.now(),
                format="h5ad",
            )

            # Save ingested data
            self._save_ingested_data(ingested_data)

            return ingested_data

        except Exception as e:
            raise ValueError(f"Failed to ingest .h5ad data: {str(e)}") from e

    def _is_identifier(self, key: str) -> bool:
        """
        Check if a metadata key might be an identifier.

        Args:
            key: Metadata key name

        Returns:
            True if key looks like an identifier
        """
        identifier_keywords = [
            "id",
            "subject",
            "donor",
            "name",
            "identifier",
        ]
        key_lower = key.lower()
        return any(keyword in key_lower for keyword in identifier_keywords)

    def _save_ingested_data(self, ingested_data: IngestedData) -> None:
        """
        Save ingested data to disk.

        Args:
            ingested_data: IngestedData object to save
        """
        ingestion_dir = self.processed_dir / ingested_data.ingestion_id
        ingestion_dir.mkdir(parents=True, exist_ok=True)

        # Save expression matrix as parquet for efficient storage
        df = pd.DataFrame(
            ingested_data.expression_matrix.expression_values,
            index=ingested_data.expression_matrix.gene_ids,
            columns=ingested_data.expression_matrix.sample_ids,
        )
        df.to_parquet(ingestion_dir / "expression_matrix.parquet")

        # Save metadata as JSON
        import json

        metadata_dict = {
            "ingestion_id": ingested_data.ingestion_id,
            "ingested_at": ingested_data.ingested_at.isoformat(),
            "format": ingested_data.format,
            "num_genes": len(ingested_data.expression_matrix.gene_ids),
            "num_samples": len(ingested_data.expression_matrix.sample_ids),
            "metadata": [m.model_dump() for m in ingested_data.metadata],
        }

        with open(ingestion_dir / "metadata.json", "w") as f:
            json.dump(metadata_dict, f, indent=2)

    def load_ingested_data(self, ingestion_id: str) -> Optional[IngestedData]:
        """
        Load previously ingested data.

        Args:
            ingestion_id: Ingestion identifier

        Returns:
            IngestedData object or None if not found
        """
        ingestion_dir = self.processed_dir / ingestion_id
        if not ingestion_dir.exists():
            return None

        try:
            # Load expression matrix
            df = pd.read_parquet(ingestion_dir / "expression_matrix.parquet")
            expression_matrix = ExpressionMatrix(
                gene_ids=df.index.tolist(),
                sample_ids=df.columns.tolist(),
                expression_values=df.values.tolist(),
            )

            # Load metadata
            import json

            with open(ingestion_dir / "metadata.json", "r") as f:
                metadata_dict = json.load(f)

            metadata_list = [
                Metadata(**m) for m in metadata_dict["metadata"]
            ]

            ingested_data = IngestedData(
                expression_matrix=expression_matrix,
                metadata=metadata_list,
                ingestion_id=metadata_dict["ingestion_id"],
                ingested_at=datetime.fromisoformat(metadata_dict["ingested_at"]),
                format=metadata_dict["format"],
            )

            return ingested_data

        except Exception as e:
            raise ValueError(f"Failed to load ingested data: {str(e)}") from e
