"""Training utilities for autoencoder."""

import json
import logging
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from ml.foundation.autoencoder import RNAAutoencoder
from ml.foundation.config import ModelConfig

logger = logging.getLogger(__name__)


class AutoencoderTrainer:
    """Trainer for RNA autoencoder."""

    def __init__(self, config: ModelConfig):
        """
        Initialize trainer.

        Args:
            config: Model configuration
        """
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

        # Set random seed
        torch.manual_seed(config.random_seed)
        np.random.seed(config.random_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(config.random_seed)

        # Initialize model
        self.model = RNAAutoencoder(
            input_dim=config.input_dim,
            latent_dim=config.latent_dim,
            hidden_dims=config.hidden_dims,
        ).to(self.device)

        # Initialize optimizer
        self.optimizer = optim.Adam(
            self.model.parameters(), lr=config.learning_rate
        )

        # Loss function
        self.criterion = nn.MSELoss()

    def train(
        self,
        expression_data: np.ndarray,
        output_dir: Path,
        validation_split: float = 0.1,
    ) -> dict:
        """
        Train the autoencoder.

        Args:
            expression_data: Normalized expression matrix [samples, genes]
            output_dir: Directory to save model and training logs
            validation_split: Fraction of data for validation

        Returns:
            Dictionary with training history
        """
        logger.info(f"Starting training on {len(expression_data)} samples")

        # Convert to tensor
        data_tensor = torch.FloatTensor(expression_data).to(self.device)

        # Split into train/validation
        n_train = int(len(data_tensor) * (1 - validation_split))
        train_data = data_tensor[:n_train]
        val_data = data_tensor[n_train:]

        # Create data loaders
        train_dataset = TensorDataset(train_data)
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
        )

        val_dataset = TensorDataset(val_data)
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
        )

        # Training history
        history = {
            "train_loss": [],
            "val_loss": [],
        }

        # Training loop
        best_val_loss = float("inf")
        for epoch in range(self.config.num_epochs):
            # Train
            train_loss = self._train_epoch(train_loader)
            history["train_loss"].append(train_loss)

            # Validate
            val_loss = self._validate(val_loader)
            history["val_loss"].append(val_loss)

            logger.info(
                f"Epoch {epoch+1}/{self.config.num_epochs} - "
                f"Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}"
            )

            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self._save_model(output_dir / "best_model.pth")

        # Save final model
        self._save_model(output_dir / "final_model.pth")

        # Save training history
        with open(output_dir / "training_history.json", "w") as f:
            json.dump(history, f, indent=2)

        # Save config
        with open(output_dir / "model_config.json", "w") as f:
            json.dump(self.config.to_dict(), f, indent=2)

        logger.info(f"Training complete. Best validation loss: {best_val_loss:.6f}")
        return history

    def _train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        for batch in train_loader:
            x = batch[0]

            # Forward pass
            self.optimizer.zero_grad()
            reconstructed, _ = self.model(x)

            # Compute loss
            loss = self.criterion(reconstructed, x)

            # Backward pass
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        return total_loss / num_batches

    def _validate(self, val_loader: DataLoader) -> float:
        """Validate on validation set."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        with torch.no_grad():
            for batch in val_loader:
                x = batch[0]

                # Forward pass
                reconstructed, _ = self.model(x)

                # Compute loss
                loss = self.criterion(reconstructed, x)

                total_loss += loss.item()
                num_batches += 1

        return total_loss / num_batches

    def _save_model(self, path: Path) -> None:
        """Save model checkpoint."""
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "config": self.config.to_dict(),
            },
            path,
        )
        logger.info(f"Saved model: {path}")
