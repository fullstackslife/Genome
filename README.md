# RNA State Intelligence Platform - Phase 1

## Overview

This is Phase 1 of the RNA State Intelligence Platform: an AI-native observability system for RNA expression data.

**Phase 1 Scope:**
- Ingest public RNA datasets (bulk RNA-seq and single-cell .h5ad)
- Normalize expression data deterministically
- Generate latent embeddings via unsupervised model
- Visualize embeddings (UMAP/PCA)
- Minimal API for ingestion and embedding retrieval

## Phase 1 Status

**✅ COMPLETE**: Phase 1 implementation is frozen and ready for validation.

See `docs/phase1_acceptance.md` for acceptance criteria and validation commands.

**What is intentionally unfinished (future phases):**
- Cell state clustering → Phase 2
- State transition modeling → Phase 3
- Batch correction → Future phase
- Authentication/authorization → Future phase
- Web dashboard UI → Future phase

See `docs/architecture.md` and `context.md` for phase roadmap.

## Important Constraints

This platform is **not** a medical device, diagnostic system, or treatment engine. It is an interpretation and modeling layer for RNA expression data.

See `docs/ethics.md` and `docs/non-medical-scope.md` for enforced constraints.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Phase 1 Demo (No Server Required)

Run the complete Phase 1 pipeline:

```bash
# Generate example data
python3 data/examples/generate_examples.py

# Train model (required before generating embeddings)
python3 scripts/train_model.py

# Run demo pipeline
python3 scripts/demo_phase1.py
```

This will:
- Ingest example data
- Run canonical pipeline (load → normalize → embed → persist)
- Generate UMAP and PCA projections
- Save all outputs to disk

### API Server (Optional)

```bash
uvicorn backend.main:app --reload
```

### Ingest Data via API

```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@data/examples/example_bulk.csv"
```

### Generate Embeddings via API

```bash
curl -X POST "http://localhost:8000/embeddings/generate?ingestion_id=<ingestion_id>"
```

### Get Embeddings via API

```bash
curl "http://localhost:8000/embeddings?ingestion_id=<ingestion_id>"
```

## Project Structure

```
/backend          - API and business logic
/ml              - Machine learning pipelines
/frontend         - Visualization components
/data             - Data schemas and examples
/docs             - Documentation and constraints
```

## Development Philosophy

- Clarity > cleverness
- Explainable > opaque
- Modular > monolithic
- Abstraction > raw biology
