"""Test for Phase 1 pipeline determinism."""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.config import settings
from backend.pipelines.ingestion import IngestionService
from backend.services.pipeline_service import PipelineService


def hash_dataframe(df: pd.DataFrame) -> str:
    """Compute hash of DataFrame for comparison."""
    # Convert to string representation and hash
    return hashlib.sha256(df.to_csv().encode()).hexdigest()


def hash_metadata(metadata_path: Path) -> str:
    """Compute hash of metadata JSON."""
    with open(metadata_path, "r") as f:
        content = json.dumps(json.load(f), sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()


@pytest.fixture
def example_data():
    """Provide example data for testing."""
    bulk_example = Path("data/examples/example_bulk.csv")
    if not bulk_example.exists():
        pytest.skip("Example data not found. Run: python3 data/examples/generate_examples.py")
    return bulk_example


@pytest.fixture
def trained_model():
    """Check that model exists."""
    model_path = settings.models_dir / "best_model.pth"
    if not model_path.exists():
        pytest.skip("Model not found. Run: python3 scripts/train_model.py")
    return model_path


def test_pipeline_determinism(example_data, trained_model):
    """Test that pipeline produces identical outputs when run twice."""
    ingestion_service = IngestionService()
    pipeline_service = PipelineService()
    
    # First run
    ingested_data_1 = ingestion_service.ingest_bulk_rnaseq(example_data)
    ingestion_id_1 = ingested_data_1.ingestion_id
    
    result_1 = pipeline_service.run_pipeline(ingestion_id_1)
    
    embeddings_path_1 = settings.embeddings_dir / ingestion_id_1 / "embeddings.parquet"
    metadata_path_1 = settings.embeddings_dir / ingestion_id_1 / "metadata.json"
    
    embeddings_1 = pd.read_parquet(embeddings_path_1)
    hash_1_embeddings = hash_dataframe(embeddings_1)
    hash_1_metadata = hash_metadata(metadata_path_1)
    
    # Second run (new ingestion to avoid caching)
    ingested_data_2 = ingestion_service.ingest_bulk_rnaseq(example_data)
    ingestion_id_2 = ingested_data_2.ingestion_id
    
    result_2 = pipeline_service.run_pipeline(ingestion_id_2)
    
    embeddings_path_2 = settings.embeddings_dir / ingestion_id_2 / "embeddings.parquet"
    metadata_path_2 = settings.embeddings_dir / ingestion_id_2 / "metadata.json"
    
    embeddings_2 = pd.read_parquet(embeddings_path_2)
    hash_2_embeddings = hash_dataframe(embeddings_2)
    hash_2_metadata = hash_metadata(metadata_path_2)
    
    # Assert identical embeddings (within float tolerance)
    pd.testing.assert_frame_equal(
        embeddings_1,
        embeddings_2,
        check_exact=False,
        rtol=1e-9,
        atol=1e-9,
    )
    
    # Assert identical metadata hashes
    assert hash_1_metadata == hash_2_metadata, "Metadata should be identical"
    
    # Assert identical result metadata
    assert result_1["num_samples"] == result_2["num_samples"]
    assert result_1["num_genes"] == result_2["num_genes"]
    assert result_1["embedding_dim"] == result_2["embedding_dim"]
    
    print("✓ Pipeline determinism test passed")


def test_normalization_determinism(example_data):
    """Test that normalization is deterministic."""
    from ml.preprocessing.normalization import NormalizationPipeline
    
    ingestion_service = IngestionService()
    ingested_data = ingestion_service.ingest_bulk_rnaseq(example_data)
    
    expression_df = pd.DataFrame(
        ingested_data.expression_matrix.expression_values,
        index=ingested_data.expression_matrix.gene_ids,
        columns=ingested_data.expression_matrix.sample_ids,
    )
    
    norm_pipeline = NormalizationPipeline()
    
    # Run normalization twice
    normalized_1, _ = norm_pipeline.normalize(expression_df)
    normalized_2, _ = norm_pipeline.normalize(expression_df)
    
    # Assert identical results
    pd.testing.assert_frame_equal(
        normalized_1,
        normalized_2,
        check_exact=False,
        rtol=1e-9,
        atol=1e-9,
    )
    
    print("✓ Normalization determinism test passed")
