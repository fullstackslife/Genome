"""Embeddings API endpoints.

PHASE 1 SCOPE:
- POST /embeddings/generate - Run canonical pipeline
- GET /embeddings - Retrieve embeddings
- GET /embeddings/visualize - Generate projection coordinates

FUTURE PHASES (not implemented):
- POST /states - Cell state inference (Phase 2)
- GET /transitions - State transition probabilities (Phase 3)
- POST /compare - State comparison (Phase 2)
"""

import logging
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from backend.config import settings
from backend.pipelines.ingestion import IngestionService
from backend.schemas.api_schemas import (
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingsListResponse,
    VisualizationResponse,
)
from backend.services.embedding_service import EmbeddingService
from backend.services.pipeline_service import PipelineService

logger = logging.getLogger(__name__)

router = APIRouter()
ingestion_service = IngestionService()
embedding_service = EmbeddingService()
pipeline_service = PipelineService()


@router.get("", response_model=EmbeddingsListResponse)
async def get_embeddings(
    ingestion_id: str = Query(..., description="Ingestion identifier"),
    sample_ids: Optional[List[str]] = Query(None, description="Specific sample IDs to retrieve"),
):
    """
    Retrieve embeddings for ingested samples.

    Args:
        ingestion_id: Ingestion identifier
        sample_ids: Optional list of specific sample IDs

    Returns:
        List of embeddings
    """
    try:
        # Load ingested data
        ingested_data = ingestion_service.load_ingested_data(ingestion_id)
        if ingested_data is None:
            raise HTTPException(
                status_code=404, detail=f"Ingestion {ingestion_id} not found"
            )

        # Check if embeddings exist
        embeddings_path = (
            settings.embeddings_dir / ingestion_id / "embeddings.parquet"
        )
        metadata_path = (
            settings.embeddings_dir / ingestion_id / "metadata.json"
        )

        if not embeddings_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Embeddings not found for ingestion {ingestion_id}. "
                "Generate embeddings first using POST /embeddings/generate",
            )

        # Load embeddings
        embeddings_df = pd.read_parquet(embeddings_path)

        # Load metadata for model version
        model_version = settings.api_version  # Default
        if metadata_path.exists():
            import json

            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                model_version = metadata.get("model_version", model_version)

        # Filter by sample IDs if provided
        if sample_ids:
            missing_ids = set(sample_ids) - set(embeddings_df.index)
            if missing_ids:
                raise HTTPException(
                    status_code=404,
                    detail=f"Samples not found: {list(missing_ids)}",
                )
            embeddings_df = embeddings_df.loc[sample_ids]

        # Convert to response format
        embedding_responses = []
        for sample_id, embedding_row in embeddings_df.iterrows():
            embedding_responses.append(
                EmbeddingResponse(
                    sample_id=sample_id,
                    embedding=embedding_row.values.tolist(),
                    embedding_dim=len(embedding_row),
                    model_version=model_version,
                )
            )

        return EmbeddingsListResponse(
            embeddings=embedding_responses,
            total_count=len(embedding_responses),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/generate")
async def generate_embeddings(
    ingestion_id: str = Query(..., description="Ingestion identifier"),
):
    """
    Generate embeddings for ingested data using canonical Phase 1 pipeline.

    Pipeline: ingestion_id → load → normalize → embed → persist

    This endpoint:
    1. Loads ingested expression data
    2. Validates dimensionality (gene count must match model)
    3. Normalizes the data deterministically
    4. Generates embeddings using the foundation model
    5. Persists embeddings and metadata

    Args:
        ingestion_id: Ingestion identifier

    Returns:
        Metadata only: counts, dimensions, model version

    Raises:
        400: If dimensionality mismatch (gene count doesn't match model)
        404: If ingestion or model not found
        500: Internal server error
    """
    try:
        result = pipeline_service.run_pipeline(ingestion_id)
        return result

    except ValueError as e:
        # ValueError indicates user error (not found, dimension mismatch)
        error_msg = str(e)
        if "dimension mismatch" in error_msg.lower() or "mismatch" in error_msg.lower():
            raise HTTPException(status_code=400, detail=error_msg)
        raise HTTPException(status_code=404, detail=error_msg)
    except Exception as e:
        logger.error(f"Error in pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/visualize", response_model=VisualizationResponse)
async def visualize_embeddings(
    ingestion_id: str = Query(..., description="Ingestion identifier"),
    method: str = Query("umap", description="Projection method (umap or pca)"),
    n_components: int = Query(2, description="Number of dimensions (2 or 3)"),
):
    """
    Generate visualization data for embeddings.

    Args:
        ingestion_id: Ingestion identifier
        method: Projection method ('umap' or 'pca')
        n_components: Number of projection dimensions (2 or 3)

    Returns:
        Visualization data with projection coordinates
    """
    try:
        viz_data = embedding_service.get_visualization_data(
            ingestion_id=ingestion_id,
            method=method,
            n_components=n_components,
        )

        return VisualizationResponse(**viz_data)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
