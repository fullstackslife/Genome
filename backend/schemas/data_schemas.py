"""Data schemas for RNA expression data."""

from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


class ExpressionMatrix(BaseModel):
    """Expression matrix structure: genes × samples."""

    gene_ids: List[str] = Field(..., description="Gene identifiers")
    sample_ids: List[str] = Field(..., description="Sample identifiers")
    expression_values: List[List[float]] = Field(
        ..., description="Expression matrix [genes × samples]"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "gene_ids": ["GENE1", "GENE2"],
                "sample_ids": ["SAMPLE1", "SAMPLE2"],
                "expression_values": [[1.0, 2.0], [3.0, 4.0]],
            }
        }


class Metadata(BaseModel):
    """Flexible metadata container."""

    sample_id: str = Field(..., description="Sample identifier")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary metadata key-value pairs"
    )
    provenance: Optional[str] = Field(None, description="Data source/provenance")
    timestamp: Optional[datetime] = Field(None, description="Ingestion timestamp")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "sample_id": "SAMPLE1",
                "metadata": {"tissue": "liver", "age": 30},
                "provenance": "public_dataset",
                "timestamp": "2024-01-01T00:00:00",
            }
        }


class IngestedData(BaseModel):
    """Complete ingested dataset."""

    expression_matrix: ExpressionMatrix
    metadata: List[Metadata]
    ingestion_id: str = Field(..., description="Unique ingestion identifier")
    ingested_at: datetime = Field(default_factory=datetime.now)
    format: str = Field(..., description="Source format (bulk_csv, h5ad, etc.)")
