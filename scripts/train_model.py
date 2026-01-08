"""Script to train the foundation embedding model."""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.config import settings
from backend.pipelines.ingestion import IngestionService
from ml.foundation.config import ModelConfig
from ml.foundation.trainer import AutoencoderTrainer
from ml.preprocessing.normalization import NormalizationPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Train the foundation model."""
    logger.info("Starting model training")

    # For Phase 1, we'll use example data or the first ingested dataset
    # Check for ingested data
    ingestion_service = IngestionService()
    ingestion_dirs = sorted(
        settings.processed_dir.glob("*"),
        key=lambda p: p.stat().st_mtime if p.is_dir() else 0,
        reverse=True,
    )

    if not ingestion_dirs or not any(d.is_dir() for d in ingestion_dirs):
        logger.warning("No ingested data found. Using synthetic data for training.")
        # Generate synthetic training data
        num_genes = 1000
        num_samples = 100
        np.random.seed(settings.random_seed)
        expression_data = np.random.lognormal(mean=5, sigma=2, size=(num_samples, num_genes))
        expression_df = pd.DataFrame(
            expression_data,
            index=[f"SAMPLE_{i:03d}" for i in range(num_samples)],
            columns=[f"GENE_{i:05d}" for i in range(num_genes)],
        )
    else:
        # Use most recent ingestion
        ingestion_id = ingestion_dirs[0].name
        logger.info(f"Using ingested data: {ingestion_id}")
        ingested_data = ingestion_service.load_ingested_data(ingestion_id)

        if ingested_data is None:
            raise ValueError(f"Failed to load ingestion {ingestion_id}")

        # Convert to DataFrame
        expression_df = pd.DataFrame(
            ingested_data.expression_matrix.expression_values,
            index=ingested_data.expression_matrix.gene_ids,
            columns=ingested_data.expression_matrix.sample_ids,
        )

    # Normalize
    logger.info("Normalizing expression data")
    normalization_pipeline = NormalizationPipeline()
    normalized_df, _ = normalization_pipeline.normalize(expression_df)

    # Prepare training data (transpose to samples × genes)
    training_data = normalized_df.T.values
    logger.info(f"Training data shape: {training_data.shape}")

    # Create model config (using defaults from ModelConfig dataclass)
    model_config = ModelConfig(
        input_dim=training_data.shape[1],  # Number of genes
        random_seed=settings.random_seed,  # Use global random seed
    )

    # Create trainer
    trainer = AutoencoderTrainer(model_config)

    # Train model
    output_dir = settings.models_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Starting training...")
    history = trainer.train(training_data, output_dir)

    logger.info("Training complete!")
    logger.info(f"Model saved to: {output_dir}")
    logger.info(f"Final training loss: {history['train_loss'][-1]:.6f}")
    logger.info(f"Final validation loss: {history['val_loss'][-1]:.6f}")


if __name__ == "__main__":
    main()
