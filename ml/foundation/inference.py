"""Inference utilities for generating embeddings."""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import torch

from ml.foundation.autoencoder import RNAAutoencoder
from ml.foundation.config import ModelConfig

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings from expression data using trained model."""

    def __init__(self, model_path: Path, device: Optional[str] = None):
        """
        Initialize embedding generator.

        Args:
            model_path: Path to trained model checkpoint
            device: Device to use ('cuda' or 'cpu'), or None for auto
        """
        self.model_path = Path(model_path)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Load model
        self.model, self.config = self._load_model()
        logger.info(f"Loaded model from {model_path}")

    def _load_model(self) -> tuple[RNAAutoencoder, ModelConfig]:
        """Load model from checkpoint."""
        checkpoint = torch.load(self.model_path, map_location=self.device)

        # Reconstruct config
        config_dict = checkpoint.get("config", {})
        config = ModelConfig(
            input_dim=config_dict["input_dim"],
            latent_dim=config_dict["latent_dim"],
            hidden_dims=config_dict["hidden_dims"],
            model_version=config_dict.get("model_version", "0.1.0"),
        )

        # Initialize model
        model = RNAAutoencoder(
            input_dim=config.input_dim,
            latent_dim=config.latent_dim,
            hidden_dims=config.hidden_dims,
        ).to(self.device)

        # Load weights
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()

        return model, config

    def generate_embeddings(
        self,
        expression_matrix: pd.DataFrame,
        batch_size: int = 32,
    ) -> pd.DataFrame:
        """
        Generate embeddings for expression matrix.

        Args:
            expression_matrix: Normalized expression matrix [genes × samples]
            batch_size: Batch size for inference

        Returns:
            DataFrame with embeddings [samples × latent_dim]
        """
        logger.info(f"Generating embeddings for {len(expression_matrix.columns)} samples")

        # Transpose to [samples × genes]
        expression_array = expression_matrix.T.values

        # Convert to tensor
        expression_tensor = torch.FloatTensor(expression_array).to(self.device)

        # Generate embeddings in batches
        embeddings_list = []
        with torch.no_grad():
            for i in range(0, len(expression_tensor), batch_size):
                batch = expression_tensor[i : i + batch_size]
                embeddings_batch = self.model.encode(batch)
                embeddings_list.append(embeddings_batch.cpu().numpy())

        # Concatenate all embeddings
        embeddings_array = np.concatenate(embeddings_list, axis=0)

        # Create DataFrame
        embedding_columns = [f"dim_{i}" for i in range(self.config.latent_dim)]
        embeddings_df = pd.DataFrame(
            embeddings_array,
            index=expression_matrix.columns,
            columns=embedding_columns,
        )

        logger.info(f"Generated embeddings: {embeddings_df.shape}")
        return embeddings_df

    def get_embedding_for_sample(
        self, expression_vector: np.ndarray
    ) -> np.ndarray:
        """
        Generate embedding for a single sample.

        Args:
            expression_vector: Expression vector [genes]

        Returns:
            Embedding vector [latent_dim]
        """
        # Ensure correct shape
        if expression_vector.ndim == 1:
            expression_vector = expression_vector.reshape(1, -1)

        # Convert to tensor
        expression_tensor = torch.FloatTensor(expression_vector).to(self.device)

        # Generate embedding
        with torch.no_grad():
            embedding = self.model.encode(expression_tensor)

        return embedding.cpu().numpy().flatten()
