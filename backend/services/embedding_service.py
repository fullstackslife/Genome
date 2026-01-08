"""Service for orchestrating embedding generation pipeline."""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from backend.config import settings
from backend.pipelines.ingestion import IngestionService
from frontend.visualizations import EmbeddingVisualizer
from ml.foundation.inference import EmbeddingGenerator
from ml.preprocessing.normalization import NormalizationPipeline

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing embeddings."""

    def __init__(self):
        """Initialize embedding service."""
        self.ingestion_service = IngestionService()
        self.normalization_pipeline = NormalizationPipeline()
        self.visualizer = EmbeddingVisualizer()

    def generate_embeddings_for_ingestion(
        self,
        ingestion_id: str,
        model_path: Optional[Path] = None,
    ) -> pd.DataFrame:
        """
        Generate embeddings for an ingested dataset.

        Full pipeline:
        1. Load ingested data
        2. Normalize expression
        3. Generate embeddings
        4. Save embeddings

        Args:
            ingestion_id: Ingestion identifier
            model_path: Path to trained model, or None to use default

        Returns:
            DataFrame with embeddings [samples × latent_dim]
        """
        logger.info(f"Generating embeddings for ingestion: {ingestion_id}")

        # Load ingested data
        ingested_data = self.ingestion_service.load_ingested_data(ingestion_id)
        if ingested_data is None:
            raise ValueError(f"Ingestion {ingestion_id} not found")

        # Convert to DataFrame
        expression_df = pd.DataFrame(
            ingested_data.expression_matrix.expression_values,
            index=ingested_data.expression_matrix.gene_ids,
            columns=ingested_data.expression_matrix.sample_ids,
        )

        # Normalize
        logger.info("Normalizing expression data")
        normalized_df, _ = self.normalization_pipeline.normalize(expression_df)

        # Load or use default model
        if model_path is None:
            model_path = settings.models_dir / "best_model.pth"

        if not model_path.exists():
            raise ValueError(f"Model not found: {model_path}")

        # Generate embeddings
        logger.info("Generating embeddings")
        embedding_generator = EmbeddingGenerator(model_path)
        embeddings_df = embedding_generator.generate_embeddings(normalized_df)

        # Save embeddings
        embeddings_dir = settings.embeddings_dir / ingestion_id
        embeddings_dir.mkdir(parents=True, exist_ok=True)
        embeddings_path = embeddings_dir / "embeddings.parquet"
        embeddings_df.to_parquet(embeddings_path)

        logger.info(f"Saved embeddings: {embeddings_path}")
        return embeddings_df

    def get_visualization_data(
        self,
        ingestion_id: str,
        method: str = "umap",
        n_components: int = 2,
    ) -> dict:
        """
        Get visualization data for embeddings.

        Args:
            ingestion_id: Ingestion identifier
            method: Projection method ('umap' or 'pca')
            n_components: Number of projection dimensions

        Returns:
            Visualization data dictionary
        """
        # Load embeddings
        embeddings_path = (
            settings.embeddings_dir / ingestion_id / "embeddings.parquet"
        )

        if not embeddings_path.exists():
            raise ValueError(
                f"Embeddings not found for ingestion {ingestion_id}. "
                "Generate embeddings first."
            )

        embeddings_df = pd.read_parquet(embeddings_path)

        # Generate visualization
        viz_data = self.visualizer.create_visualization_data(
            embeddings=embeddings_df,
            method=method,
            n_components=n_components,
        )

        return viz_data
