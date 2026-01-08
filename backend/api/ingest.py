"""Ingestion API endpoints."""

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config import settings
from backend.pipelines.ingestion import IngestionService
from backend.schemas.api_schemas import IngestionResponse

logger = logging.getLogger(__name__)

router = APIRouter()
ingestion_service = IngestionService()


@router.post("", response_model=IngestionResponse)
async def ingest_data(file: UploadFile = File(...)):
    """
    Ingest RNA expression data.

    Supports:
    - Bulk RNA-seq: CSV/TSV files (genes × samples)
    - Single-cell RNA-seq: .h5ad files (AnnData format)

    Args:
        file: Uploaded file

    Returns:
        IngestionResponse with sample IDs and metadata
    """
    try:
        # Determine file format
        file_extension = Path(file.filename).suffix.lower()
        logger.info(f"Ingesting file: {file.filename} (format: {file_extension})")

        # Save uploaded file temporarily
        with NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)

        try:
            # Ingest based on format
            if file_extension == ".h5ad":
                ingested_data = ingestion_service.ingest_h5ad(tmp_path)
            elif file_extension in [".csv", ".tsv"]:
                delimiter = "," if file_extension == ".csv" else "\t"
                ingested_data = ingestion_service.ingest_bulk_rnaseq(
                    tmp_path, delimiter=delimiter
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format: {file_extension}. "
                    "Supported: .csv, .tsv, .h5ad",
                )

            # Build response
            response = IngestionResponse(
                ingestion_id=ingested_data.ingestion_id,
                sample_ids=ingested_data.expression_matrix.sample_ids,
                num_genes=len(ingested_data.expression_matrix.gene_ids),
                num_samples=len(ingested_data.expression_matrix.sample_ids),
                format=ingested_data.format,
                status="success",
                message=f"Successfully ingested {len(ingested_data.expression_matrix.sample_ids)} samples",
            )

            logger.info(
                f"Ingestion successful: {response.ingestion_id}, "
                f"{response.num_samples} samples, {response.num_genes} genes"
            )

            return response

        finally:
            # Clean up temporary file
            tmp_path.unlink(missing_ok=True)

    except ValueError as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{ingestion_id}")
async def get_ingestion_info(ingestion_id: str):
    """
    Get information about a previous ingestion.

    Args:
        ingestion_id: Ingestion identifier

    Returns:
        Ingestion information
    """
    ingested_data = ingestion_service.load_ingested_data(ingestion_id)

    if ingested_data is None:
        raise HTTPException(status_code=404, detail=f"Ingestion {ingestion_id} not found")

    return IngestionResponse(
        ingestion_id=ingested_data.ingestion_id,
        sample_ids=ingested_data.expression_matrix.sample_ids,
        num_genes=len(ingested_data.expression_matrix.gene_ids),
        num_samples=len(ingested_data.expression_matrix.sample_ids),
        format=ingested_data.format,
        status="success",
        message="Ingestion found",
    )
