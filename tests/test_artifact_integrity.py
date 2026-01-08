"""Test for artifact integrity and consistency."""

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.config import settings
from backend.pipelines.ingestion import IngestionService
from backend.services.pipeline_service import PipelineService


@pytest.fixture
def example_data():
    """Provide example data for testing."""
    bulk_example = Path("data/examples/example_bulk.csv")
    if not bulk_example.exists():
        pytest.skip("Example data not found")
    return bulk_example


@pytest.fixture
def trained_model():
    """Check that model exists."""
    model_path = settings.models_dir / "best_model.pth"
    if not model_path.exists():
        pytest.skip("Model not found")
    return model_path


def test_artifact_integrity(example_data, trained_model):
    """Test that all artifacts are present, versioned, and internally consistent."""
    ingestion_service = IngestionService()
    pipeline_service = PipelineService()
    
    # Run pipeline
    ingested_data = ingestion_service.ingest_bulk_rnaseq(example_data)
    ingestion_id = ingested_data.ingestion_id
    
    result = pipeline_service.run_pipeline(ingestion_id)
    
    # Check artifacts exist
    embeddings_path = settings.embeddings_dir / ingestion_id / "embeddings.parquet"
    metadata_path = settings.embeddings_dir / ingestion_id / "metadata.json"
    
    assert embeddings_path.exists(), "Embeddings file should exist"
    assert metadata_path.exists(), "Metadata file should exist"
    
    # Load artifacts
    embeddings_df = pd.read_parquet(embeddings_path)
    
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    # Validate embeddings structure
    assert embeddings_df.shape[0] > 0, "Embeddings should have samples"
    assert embeddings_df.shape[1] > 0, "Embeddings should have dimensions"
    
    # Validate metadata structure
    assert "ingestion_id" in metadata
    assert "num_samples" in metadata
    assert "num_genes" in metadata
    assert "embedding_dim" in metadata
    assert "model_version" in metadata
    
    # Validate consistency: sample count
    assert embeddings_df.shape[0] == metadata["num_samples"], (
        f"Embedding sample count ({embeddings_df.shape[0]}) "
        f"should match metadata ({metadata['num_samples']})"
    )
    
    # Validate consistency: embedding dimension
    assert embeddings_df.shape[1] == metadata["embedding_dim"], (
        f"Embedding dimension ({embeddings_df.shape[1]}) "
        f"should match metadata ({metadata['embedding_dim']})"
    )
    
    # Validate consistency: result metadata
    assert result["num_samples"] == metadata["num_samples"]
    assert result["num_genes"] == metadata["num_genes"]
    assert result["embedding_dim"] == metadata["embedding_dim"]
    assert result["model_version"] == metadata["model_version"]
    
    # Validate versioning
    assert metadata["model_version"] is not None
    assert metadata["model_version"] != ""
    
    # Validate gene count consistency with ingestion
    assert metadata["num_genes"] == len(ingested_data.expression_matrix.gene_ids), (
        f"Metadata gene count ({metadata['num_genes']}) "
        f"should match ingestion ({len(ingested_data.expression_matrix.gene_ids)})"
    )
    
    print("✓ Artifact integrity test passed")
