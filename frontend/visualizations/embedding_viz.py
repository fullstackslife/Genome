"""Embedding visualization utilities."""

import logging
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from umap import UMAP

logger = logging.getLogger(__name__)


class EmbeddingVisualizer:
    """Generate 2D/3D projections of embeddings for visualization."""

    def __init__(self, random_seed: int = 42):
        """
        Initialize visualizer.

        Args:
            random_seed: Random seed for reproducibility
        """
        self.random_seed = random_seed

    def project_umap(
        self,
        embeddings: pd.DataFrame,
        n_components: int = 2,
        n_neighbors: int = 15,
        min_dist: float = 0.1,
    ) -> pd.DataFrame:
        """
        Project embeddings to 2D/3D using UMAP.

        Args:
            embeddings: Embedding matrix [samples × latent_dim]
            n_components: Number of projection dimensions (2 or 3)
            n_neighbors: UMAP n_neighbors parameter
            min_dist: UMAP min_dist parameter

        Returns:
            DataFrame with projection coordinates [samples × n_components]
        """
        logger.info(f"Computing UMAP projection: {embeddings.shape} -> {n_components}D")

        # Initialize UMAP
        umap_model = UMAP(
            n_components=n_components,
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            random_state=self.random_seed,
        )

        # Fit and transform
        projection = umap_model.fit_transform(embeddings.values)

        # Create DataFrame
        column_names = [f"umap_{i+1}" for i in range(n_components)]
        projection_df = pd.DataFrame(
            projection,
            index=embeddings.index,
            columns=column_names,
        )

        return projection_df

    def project_pca(
        self,
        embeddings: pd.DataFrame,
        n_components: int = 2,
    ) -> pd.DataFrame:
        """
        Project embeddings to 2D/3D using PCA.

        Args:
            embeddings: Embedding matrix [samples × latent_dim]
            n_components: Number of principal components (2 or 3)

        Returns:
            DataFrame with projection coordinates [samples × n_components]
        """
        logger.info(f"Computing PCA projection: {embeddings.shape} -> {n_components}D")

        # Initialize PCA
        pca_model = PCA(
            n_components=n_components,
            random_state=self.random_seed,
        )

        # Fit and transform
        projection = pca_model.fit_transform(embeddings.values)

        # Create DataFrame
        column_names = [f"pc_{i+1}" for i in range(n_components)]
        projection_df = pd.DataFrame(
            projection,
            index=embeddings.index,
            columns=column_names,
        )

        # Store explained variance
        explained_variance = pca_model.explained_variance_ratio_
        logger.info(
            f"PCA explained variance: "
            f"{', '.join([f'PC{i+1}: {v:.2%}' for i, v in enumerate(explained_variance)])}"
        )

        return projection_df

    def create_visualization_data(
        self,
        embeddings: pd.DataFrame,
        method: str = "umap",
        n_components: int = 2,
        metadata: Optional[pd.DataFrame] = None,
    ) -> dict:
        """
        Create visualization data structure.

        Args:
            embeddings: Embedding matrix [samples × latent_dim]
            method: Projection method ('umap' or 'pca')
            n_components: Number of projection dimensions
            metadata: Optional metadata DataFrame [samples × metadata_cols]

        Returns:
            Dictionary with visualization data
        """
        # Project embeddings
        if method.lower() == "umap":
            projection_df = self.project_umap(embeddings, n_components=n_components)
        elif method.lower() == "pca":
            projection_df = self.project_pca(embeddings, n_components=n_components)
        else:
            raise ValueError(f"Unknown projection method: {method}")

        # Build result dictionary
        result = {
            "sample_ids": projection_df.index.tolist(),
            "coordinates": projection_df.values.tolist(),
            "projection_method": method.upper(),
            "n_components": n_components,
        }

        # Add metadata if provided
        if metadata is not None:
            # Ensure metadata aligns with embeddings
            aligned_metadata = metadata.loc[projection_df.index]
            result["metadata"] = aligned_metadata.to_dict(orient="records")

        return result
