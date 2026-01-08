"""API request/response schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IngestionRequest(BaseModel):
    """Request schema for data ingestion."""

    # File will be handled via multipart form data
    pass


class IngestionResponse(BaseModel):
    """Response schema for data ingestion."""

    ingestion_id: str = Field(..., description="Unique ingestion identifier")
    sample_ids: List[str] = Field(..., description="List of ingested sample IDs")
    num_genes: int = Field(..., description="Number of genes")
    num_samples: int = Field(..., description="Number of samples")
    format: str = Field(..., description="Source format")
    status: str = Field(default="success", description="Ingestion status")
    message: Optional[str] = Field(None, description="Additional message")


class EmbeddingRequest(BaseModel):
    """Request schema for embedding generation."""

    sample_ids: Optional[List[str]] = Field(
        None, description="Specific sample IDs, or None for all"
    )
    force_regenerate: bool = Field(
        default=False, description="Force regeneration even if embeddings exist"
    )


class EmbeddingResponse(BaseModel):
    """Response schema for embeddings."""

    sample_id: str = Field(..., description="Sample identifier")
    embedding: List[float] = Field(..., description="Latent embedding vector")
    embedding_dim: int = Field(..., description="Embedding dimensionality")
    model_version: str = Field(..., description="Model version used")


class EmbeddingsListResponse(BaseModel):
    """Response schema for multiple embeddings."""

    embeddings: List[EmbeddingResponse] = Field(..., description="List of embeddings")
    total_count: int = Field(..., description="Total number of embeddings")


class VisualizationResponse(BaseModel):
    """Response schema for visualization data."""

    sample_ids: List[str] = Field(..., description="Sample identifiers")
    coordinates: List[List[float]] = Field(
        ..., description="2D/3D projection coordinates"
    )
    projection_method: str = Field(..., description="Projection method (UMAP, PCA)")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for visualization"
    )
