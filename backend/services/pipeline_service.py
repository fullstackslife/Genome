"""Canonical Phase 1 pipeline: ingestion_id → load → normalize → embed → persist."""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from backend.config import settings
from backend.pipelines.ingestion import IngestionService
from ml.foundation.config import ModelConfig
from ml.foundation.inference import EmbeddingGenerator
from ml.preprocessing.config import NormalizationConfig
from ml.preprocessing.normalization import NormalizationPipeline

logger = logging.getLogger(__name__)


class PipelineService:
    """Canonical Phase 1 pipeline service."""

    def __init__(self):
        """Initialize pipeline service."""
        self.ingestion_service = IngestionService()
        self.normalization_pipeline = NormalizationPipeline()

    def run_pipeline(
        self,
        ingestion_id: str,
        model_path: Optional[Path] = None,
        normalization_config: Optional[NormalizationConfig] = None,
    ) -> dict:
        """
        Run the canonical Phase 1 pipeline.

        Pipeline steps:
        1. Load ingested data
        2. Validate dimensionality
        3. Normalize expression
        4. Generate embeddings
        5. Persist embeddings

        Args:
            ingestion_id: Ingestion identifier
            model_path: Path to trained model, or None to use default
            normalization_config: Normalization config, or None for defaults

        Returns:
            Dictionary with pipeline metadata (counts, dimensions, model version)

        Raises:
            ValueError: If ingestion not found, model not found, or dimensionality mismatch
        """
        logger.info(f"Starting pipeline for ingestion: {ingestion_id}")

        # Step 1: Load ingested data
        logger.info("Step 1: Loading ingested data")
        ingested_data = self.ingestion_service.load_ingested_data(ingestion_id)
        if ingested_data is None:
            raise ValueError(f"Ingestion {ingestion_id} not found")

        # Convert to DataFrame
        expression_df = pd.DataFrame(
            ingested_data.expression_matrix.expression_values,
            index=ingested_data.expression_matrix.gene_ids,
            columns=ingested_data.expression_matrix.sample_ids,
        )

        num_genes = len(expression_df.index)
        num_samples = len(expression_df.columns)
        logger.info(f"Loaded expression matrix: {num_genes} genes × {num_samples} samples")
        logger.info(f"Gene IDs (first 5): {list(expression_df.index[:5])}")

        # Step 2: Validate model exists and check dimensionality
        logger.info("Step 2: Validating model and dimensionality")
        if model_path is None:
            model_path = settings.models_dir / "best_model.pth"

        if not model_path.exists():
            raise ValueError(f"Model not found: {model_path}")

        # Load model config to validate dimensionality
        import torch

        checkpoint = torch.load(model_path, map_location="cpu")
        model_config_dict = checkpoint.get("config", {})
        model_input_dim = model_config_dict.get("input_dim")

        if model_input_dim is None:
            raise ValueError(f"Model config missing input_dim: {model_path}")

        # Validate gene count matches model input dimension
        if num_genes != model_input_dim:
            raise ValueError(
                f"Gene dimension mismatch: "
                f"expression data has {num_genes} genes, "
                f"model expects {model_input_dim} genes. "
                f"Gene ordering must match model training data."
            )

        logger.info(f"✓ Dimensionality validated: {num_genes} genes match model input_dim")

        # Step 3: Normalize expression
        logger.info("Step 3: Normalizing expression data")
        if normalization_config is None:
            normalization_config = NormalizationConfig()

        normalized_df, norm_config_dict = self.normalization_pipeline.normalize(
            expression_df
        )

        logger.info(f"Normalized expression matrix: {normalized_df.shape}")

        # Step 4: Generate embeddings
        logger.info("Step 4: Generating embeddings")
        embedding_generator = EmbeddingGenerator(model_path)
        embeddings_df = embedding_generator.generate_embeddings(normalized_df)

        embedding_dim = len(embeddings_df.columns)
        logger.info(f"Generated embeddings: {embeddings_df.shape} (samples × {embedding_dim})")

        # Step 5: Persist embeddings
        logger.info("Step 5: Persisting embeddings")
        embeddings_dir = settings.embeddings_dir / ingestion_id
        embeddings_dir.mkdir(parents=True, exist_ok=True)
        embeddings_path = embeddings_dir / "embeddings.parquet"
        embeddings_df.to_parquet(embeddings_path)

        # Also save metadata
        import json

        metadata = {
            "ingestion_id": ingestion_id,
            "num_samples": num_samples,
            "num_genes": num_genes,
            "embedding_dim": embedding_dim,
            "model_version": model_config_dict.get("model_version", "unknown"),
            "model_path": str(model_path),
            "normalization_config": norm_config_dict,
        }

        metadata_path = embeddings_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"✓ Embeddings persisted: {embeddings_path}")
        logger.info(f"✓ Metadata saved: {metadata_path}")

        logger.info("Pipeline complete")

        # Return metadata only (counts, dimensions, model version)
        return {
            "ingestion_id": ingestion_id,
            "num_samples": num_samples,
            "num_genes": num_genes,
            "embedding_dim": embedding_dim,
            "model_version": model_config_dict.get("model_version", "unknown"),
            "status": "success",
        }
