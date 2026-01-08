"""Minimal demo script for Phase 1 pipeline.

This script demonstrates the complete Phase 1 workflow:
1. Ingest example data
2. Run canonical pipeline (load → normalize → embed → persist)
3. Generate embeddings
4. Produce visualization projection (UMAP/PCA)

No server required. Outputs to console and saves files.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.config import settings
from backend.pipelines.ingestion import IngestionService
from backend.services.pipeline_service import PipelineService
from frontend.visualizations import EmbeddingVisualizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Run Phase 1 demo pipeline."""
    print("=" * 60)
    print("Phase 1 Demo: RNA State Intelligence Platform")
    print("=" * 60)
    print()

    # Step 1: Ingest example data
    print("Step 1: Ingesting example data")
    print("-" * 60)

    ingestion_service = IngestionService()

    # Check if example data exists
    bulk_example = Path("data/examples/example_bulk.csv")
    sc_example = Path("data/examples/example_single_cell.h5ad")

    if not bulk_example.exists():
        print(f"❌ Example data not found: {bulk_example}")
        print("   Run: python3 data/examples/generate_examples.py")
        return 1

    print(f"✓ Found bulk example: {bulk_example}")

    # Ingest bulk RNA-seq
    try:
        ingested_data = ingestion_service.ingest_bulk_rnaseq(bulk_example)
        ingestion_id = ingested_data.ingestion_id
        print(f"✓ Ingested bulk RNA-seq")
        print(f"  Ingestion ID: {ingestion_id}")
        print(f"  Samples: {len(ingested_data.expression_matrix.sample_ids)}")
        print(f"  Genes: {len(ingested_data.expression_matrix.gene_ids)}")
        print()
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return 1

    # Step 2: Run canonical pipeline
    print("Step 2: Running canonical pipeline")
    print("-" * 60)
    print("Pipeline: ingestion_id → load → normalize → embed → persist")
    print()

    pipeline_service = PipelineService()

    try:
        result = pipeline_service.run_pipeline(ingestion_id)
        print()
        print("✓ Pipeline complete")
        print(f"  Samples processed: {result['num_samples']}")
        print(f"  Genes: {result['num_genes']}")
        print(f"  Embedding dimension: {result['embedding_dim']}")
        print(f"  Model version: {result['model_version']}")
        print()
    except ValueError as e:
        print(f"❌ Pipeline failed: {e}")
        print()
        print("Common issues:")
        print("  - Model not trained: Run python3 scripts/train_model.py")
        print("  - Gene dimension mismatch: Check model input_dim matches data")
        return 1
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        return 1

    # Step 3: Generate visualization projection
    print("Step 3: Generating visualization projection")
    print("-" * 60)

    visualizer = EmbeddingVisualizer()

    # Load embeddings
    embeddings_path = settings.embeddings_dir / ingestion_id / "embeddings.parquet"
    if not embeddings_path.exists():
        print(f"❌ Embeddings not found: {embeddings_path}")
        return 1

    import pandas as pd

    embeddings_df = pd.read_parquet(embeddings_path)
    print(f"✓ Loaded embeddings: {embeddings_df.shape}")

    # Generate UMAP projection
    try:
        print("  Computing UMAP projection...")
        umap_projection = visualizer.project_umap(embeddings_df, n_components=2)
        print(f"✓ UMAP projection: {umap_projection.shape}")

        # Save projection
        projection_path = settings.embeddings_dir / ingestion_id / "umap_projection.csv"
        umap_projection.to_csv(projection_path)
        print(f"✓ Saved: {projection_path}")
        print()
    except Exception as e:
        print(f"❌ UMAP projection failed: {e}")
        return 1

    # Generate PCA projection
    try:
        print("  Computing PCA projection...")
        pca_projection = visualizer.project_pca(embeddings_df, n_components=2)
        print(f"✓ PCA projection: {pca_projection.shape}")

        # Save projection
        projection_path = settings.embeddings_dir / ingestion_id / "pca_projection.csv"
        pca_projection.to_csv(projection_path)
        print(f"✓ Saved: {projection_path}")
        print()
    except Exception as e:
        print(f"❌ PCA projection failed: {e}")
        return 1

    # Summary
    print("=" * 60)
    print("Phase 1 Demo Complete")
    print("=" * 60)
    print()
    print("Generated files:")
    print(f"  - Ingested data: data/processed/{ingestion_id}/")
    print(f"  - Embeddings: embeddings/{ingestion_id}/embeddings.parquet")
    print(f"  - Metadata: embeddings/{ingestion_id}/metadata.json")
    print(f"  - UMAP projection: embeddings/{ingestion_id}/umap_projection.csv")
    print(f"  - PCA projection: embeddings/{ingestion_id}/pca_projection.csv")
    print()
    print("Next steps:")
    print("  - Review embeddings/{ingestion_id}/metadata.json")
    print("  - Visualize projections using external tools")
    print("  - Proceed to Phase 2: Cell state abstraction")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
