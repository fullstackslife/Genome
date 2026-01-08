# Integration Testing Guide

## Phase 1 Integration Test Flow

This document describes how to test the complete Phase 1 pipeline end-to-end.

## Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Generate example data (if not already present):
```bash
python3 data/examples/generate_examples.py
```

3. Train the foundation model:
```bash
python3 scripts/train_model.py
```

## Test Flow

### Step 1: Start API Server

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

### Step 2: Ingest Data

**Bulk RNA-seq:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@data/examples/example_bulk.csv"
```

**Single-cell RNA-seq:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@data/examples/example_single_cell.h5ad"
```

Expected response:
```json
{
  "ingestion_id": "...",
  "sample_ids": ["SAMPLE_000", ...],
  "num_genes": 100,
  "num_samples": 20,
  "format": "bulk_csv",
  "status": "success"
}
```

Save the `ingestion_id` for next steps.

### Step 3: Generate Embeddings

```bash
curl -X POST "http://localhost:8000/embeddings/generate?ingestion_id=<INGESTION_ID>"
```

Expected response:
```json
{
  "status": "success",
  "message": "Generated embeddings for 20 samples",
  "ingestion_id": "..."
}
```

### Step 4: Retrieve Embeddings

```bash
curl "http://localhost:8000/embeddings?ingestion_id=<INGESTION_ID>"
```

Expected response:
```json
{
  "embeddings": [
    {
      "sample_id": "SAMPLE_000",
      "embedding": [0.1, 0.2, ...],
      "embedding_dim": 128,
      "model_version": "0.1.0"
    },
    ...
  ],
  "total_count": 20
}
```

### Step 5: Generate Visualization

**UMAP projection:**
```bash
curl "http://localhost:8000/embeddings/visualize?ingestion_id=<INGESTION_ID>&method=umap&n_components=2"
```

**PCA projection:**
```bash
curl "http://localhost:8000/embeddings/visualize?ingestion_id=<INGESTION_ID>&method=pca&n_components=2"
```

Expected response:
```json
{
  "sample_ids": ["SAMPLE_000", ...],
  "coordinates": [[x1, y1], [x2, y2], ...],
  "projection_method": "UMAP",
  "n_components": 2
}
```

## Validation Checklist

- [ ] Data ingestion succeeds for both bulk and single-cell formats
- [ ] Embeddings are generated deterministically (same input = same output)
- [ ] Visualization coordinates are returned correctly
- [ ] API responses use neutral terminology only
- [ ] No medical terminology in any API responses
- [ ] All endpoints return structured JSON

## Medical Terminology Check

Run the automated check:
```bash
python3 scripts/check_medical_terms.py
```

Expected: ✅ No forbidden medical terminology found!

## Success Criteria

Phase 1 is complete when:
1. ✅ Public RNA dataset can be ingested via API
2. ✅ Embeddings are generated deterministically
3. ✅ Embeddings can be visualized (UMAP/PCA)
4. ✅ APIs return structured, interpretable JSON
5. ✅ No medical or diagnostic claims exist anywhere
6. ✅ All constraint documents are in place
