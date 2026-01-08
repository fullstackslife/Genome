"""Smoke tests for Phase 1 components."""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all Phase 1 modules can be imported."""
    try:
        from backend.config import settings
        from backend.pipelines.ingestion import IngestionService
        from backend.services.pipeline_service import PipelineService
        from ml.preprocessing.normalization import NormalizationPipeline
        from ml.foundation.autoencoder import RNAAutoencoder
        from frontend.visualizations import EmbeddingVisualizer
        
        assert settings is not None
        assert IngestionService is not None
        assert PipelineService is not None
        assert NormalizationPipeline is not None
        assert RNAAutoencoder is not None
        assert EmbeddingVisualizer is not None
        
        print("✓ All Phase 1 modules import successfully")
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_demo_script_exists():
    """Test that demo script exists and is executable."""
    demo_script = Path("scripts/demo_phase1.py")
    assert demo_script.exists(), "Demo script should exist"
    assert demo_script.is_file(), "Demo script should be a file"
    print("✓ Demo script exists")
