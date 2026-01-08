"""Configuration for foundation embedding model."""

from dataclasses import dataclass
from typing import List


@dataclass
class ModelConfig:
    """Configuration for autoencoder model."""

    # Architecture
    input_dim: int  # Number of genes/features
    latent_dim: int = 128
    hidden_dims: List[int] = None  # Encoder/decoder hidden dimensions

    # Training
    learning_rate: float = 0.001
    batch_size: int = 32
    num_epochs: int = 100
    random_seed: int = 42

    # Model versioning
    model_version: str = "0.1.0"

    def __post_init__(self):
        """Set default hidden dims if not provided."""
        if self.hidden_dims is None:
            # Default: symmetric encoder/decoder
            self.hidden_dims = [512, 256]

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "input_dim": self.input_dim,
            "latent_dim": self.latent_dim,
            "hidden_dims": self.hidden_dims,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "num_epochs": self.num_epochs,
            "random_seed": self.random_seed,
            "model_version": self.model_version,
        }
