"""Simple autoencoder model for RNA expression embeddings."""

import torch
import torch.nn as nn
import torch.nn.functional as F


class RNAAutoencoder(nn.Module):
    """Simple autoencoder for generating latent embeddings from expression data."""

    def __init__(self, input_dim: int, latent_dim: int = 128, hidden_dims: list[int] = None):
        """
        Initialize autoencoder.

        Args:
            input_dim: Input dimension (number of genes)
            latent_dim: Latent embedding dimension
            hidden_dims: List of hidden layer dimensions for encoder/decoder
        """
        super().__init__()

        if hidden_dims is None:
            hidden_dims = [512, 256]

        self.input_dim = input_dim
        self.latent_dim = latent_dim

        # Build encoder
        encoder_layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            encoder_layers.append(nn.Linear(prev_dim, hidden_dim))
            encoder_layers.append(nn.ReLU())
            prev_dim = hidden_dim
        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)

        # Build decoder (symmetric)
        decoder_layers = []
        prev_dim = latent_dim
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.append(nn.Linear(prev_dim, hidden_dim))
            decoder_layers.append(nn.ReLU())
            prev_dim = hidden_dim
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.

        Args:
            x: Input expression vector [batch_size, input_dim]

        Returns:
            Tuple of (reconstructed, embedding)
        """
        # Encode to latent space
        embedding = self.encoder(x)

        # Decode from latent space
        reconstructed = self.decoder(embedding)

        return reconstructed, embedding

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """
        Encode input to latent embedding.

        Args:
            x: Input expression vector [batch_size, input_dim]

        Returns:
            Latent embedding [batch_size, latent_dim]
        """
        return self.encoder(x)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """
        Decode latent embedding to expression space.

        Args:
            z: Latent embedding [batch_size, latent_dim]

        Returns:
            Reconstructed expression [batch_size, input_dim]
        """
        return self.decoder(z)
