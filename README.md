# RNA State Intelligence Platform - Phase 1

## Overview

This is Phase 1 of the RNA State Intelligence Platform: an AI-native observability system for RNA expression data.

**Phase 1 Scope:**
- Ingest public RNA datasets (bulk RNA-seq and single-cell .h5ad)
- Normalize expression data deterministically
- Generate latent embeddings via unsupervised model
- Visualize embeddings (UMAP/PCA)
- Minimal API for ingestion and embedding retrieval

## Important Constraints

This platform is **not** a medical device, diagnostic system, or treatment engine. It is an interpretation and modeling layer for RNA expression data.

See `docs/ethics.md` and `docs/non-medical-scope.md` for enforced constraints.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run API Server

```bash
uvicorn backend.main:app --reload
```

### Ingest Data

```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@data/examples/example_bulk.csv"
```

### Get Embeddings

```bash
curl "http://localhost:8000/embeddings?sample_id=<sample_id>"
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
