# Phase 1 Acceptance Checklist

This document defines concrete criteria for Phase 1 completion. Each item must be verifiable through commands or API calls.

## Prerequisites

Before validation, ensure:
- Dependencies installed: `pip install -r requirements.txt`
- Example data generated: `python3 data/examples/generate_examples.py`
- Model trained: `python3 scripts/train_model.py`

## Acceptance Criteria

### 1. Repository Structure

**Criterion**: All required directories and files exist as specified in `context.md`

**Validation**:
```bash
# Check directory structure
ls -R backend/ ml/ frontend/ data/ docs/

# Verify key files exist
test -f backend/main.py && echo "✓ backend/main.py exists"
test -f ml/foundation/autoencoder.py && echo "✓ autoencoder exists"
test -f docs/ethics.md && echo "✓ ethics.md exists"
test -f docs/non-medical-scope.md && echo "✓ non-medical-scope.md exists"
```

**Expected**: All directories and files from `context.md` structure exist

---

### 2. Data Ingestion

**Criterion**: System can ingest both bulk RNA-seq (CSV) and single-cell (.h5ad) formats

**Validation**:
```bash
# Start API server
uvicorn backend.main:app --reload &

# Ingest bulk RNA-seq
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@data/examples/example_bulk.csv" \
  | jq '.status, .num_samples, .num_genes'

# Ingest single-cell
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@data/examples/example_single_cell.h5ad" \
  | jq '.status, .num_samples, .num_genes'
```

**Expected**: Both requests return `"status": "success"` with correct sample/gene counts

**Alternative (without server)**:
```bash
python3 scripts/demo_phase1.py
# Should show ingestion success for both formats
```

---

### 3. Deterministic Normalization

**Criterion**: Normalization produces identical results for identical inputs

**Validation**:
```python
# Run normalization twice on same data
python3 -c "
from backend.pipelines.ingestion import IngestionService
from ml.preprocessing.normalization import NormalizationPipeline
import pandas as pd

ingestion = IngestionService()
data = ingestion.load_ingested_data('<ingestion_id>')
df = pd.DataFrame(data.expression_matrix.expression_values, 
                  index=data.expression_matrix.gene_ids,
                  columns=data.expression_matrix.sample_ids)

norm = NormalizationPipeline()
result1, _ = norm.normalize(df)
result2, _ = norm.normalize(df)

assert result1.equals(result2), 'Normalization not deterministic'
print('✓ Normalization is deterministic')
"
```

**Expected**: No assertion error, identical outputs

---

### 4. Embedding Generation

**Criterion**: Canonical pipeline generates embeddings deterministically

**Validation**:
```bash
# Run pipeline via API
INGESTION_ID=$(curl -s -X POST "http://localhost:8000/ingest" \
  -F "file=@data/examples/example_bulk.csv" | jq -r '.ingestion_id')

curl -X POST "http://localhost:8000/embeddings/generate?ingestion_id=$INGESTION_ID" \
  | jq '.status, .num_samples, .num_genes, .embedding_dim, .model_version'
```

**Expected**: Returns metadata with `"status": "success"`, correct dimensions

**Alternative**:
```bash
python3 scripts/demo_phase1.py
# Should complete pipeline and show embedding dimensions
```

---

### 5. Dimensionality Validation

**Criterion**: System fails clearly when gene count doesn't match model

**Validation**:
```bash
# Create test data with wrong gene count
python3 -c "
import pandas as pd
import numpy as np
df = pd.DataFrame(np.random.rand(50, 10),  # 50 genes, 10 samples (wrong!)
                  index=[f'GENE_{i}' for i in range(50)],
                  columns=[f'SAMPLE_{i}' for i in range(10)])
df.to_csv('test_wrong_dim.csv', index=True)
"

# Attempt ingestion and embedding generation
INGESTION_ID=$(curl -s -X POST "http://localhost:8000/ingest" \
  -F "file=@test_wrong_dim.csv" | jq -r '.ingestion_id')

curl -X POST "http://localhost:8000/embeddings/generate?ingestion_id=$INGESTION_ID"
```

**Expected**: HTTP 400 error with clear message about dimension mismatch

---

### 6. Embedding Retrieval

**Criterion**: Generated embeddings can be retrieved via API

**Validation**:
```bash
# After generating embeddings
curl "http://localhost:8000/embeddings?ingestion_id=$INGESTION_ID" \
  | jq '.total_count, .embeddings[0].embedding_dim, .embeddings[0].model_version'
```

**Expected**: Returns list of embeddings with correct dimensions and model version

---

### 7. Visualization Data Generation

**Criterion**: System can generate UMAP and PCA projections

**Validation**:
```bash
# UMAP projection
curl "http://localhost:8000/embeddings/visualize?ingestion_id=$INGESTION_ID&method=umap&n_components=2" \
  | jq '.projection_method, .n_components, (.coordinates | length)'

# PCA projection
curl "http://localhost:8000/embeddings/visualize?ingestion_id=$INGESTION_ID&method=pca&n_components=2" \
  | jq '.projection_method, .n_components, (.coordinates | length)'
```

**Expected**: Both return projection coordinates matching sample count

---

### 8. Medical Terminology Enforcement

**Criterion**: No forbidden medical terms exist in codebase

**Validation**:
```bash
python3 scripts/check_medical_terms.py
```

**Expected**: Output shows "✅ No forbidden medical terminology found!"

---

### 9. Configuration Standardization

**Criterion**: Backend uses BaseSettings, ML uses dataclasses

**Validation**:
```bash
# Check backend config
python3 -c "
from backend.config import settings
assert hasattr(settings, 'api_version')
assert hasattr(settings, 'random_seed')
print('✓ Backend config uses BaseSettings')
"

# Check ML configs are dataclasses
python3 -c "
from dataclasses import is_dataclass
from ml.preprocessing.config import NormalizationConfig
from ml.foundation.config import ModelConfig
assert is_dataclass(NormalizationConfig)
assert is_dataclass(ModelConfig)
print('✓ ML configs use dataclasses')
"
```

**Expected**: Both assertions pass

---

### 10. Canonical Pipeline

**Criterion**: Single clear execution path: ingestion_id → load → normalize → embed → persist

**Validation**:
```bash
# Check pipeline service exists and has run_pipeline method
python3 -c "
from backend.services.pipeline_service import PipelineService
import inspect
methods = [m for m in dir(PipelineService) if not m.startswith('_')]
assert 'run_pipeline' in methods
print('✓ PipelineService.run_pipeline exists')
"
```

**Expected**: Pipeline service method exists

**Functional validation**:
```bash
python3 scripts/demo_phase1.py
# Should show all pipeline steps executing in order
```

---

### 11. Metadata Persistence

**Criterion**: Embeddings and metadata are persisted correctly

**Validation**:
```bash
# After running pipeline
INGESTION_ID="<from_previous_step>"
test -f "embeddings/$INGESTION_ID/embeddings.parquet" && echo "✓ Embeddings saved"
test -f "embeddings/$INGESTION_ID/metadata.json" && echo "✓ Metadata saved"

# Check metadata contents
cat "embeddings/$INGESTION_ID/metadata.json" | jq '.num_samples, .num_genes, .embedding_dim, .model_version'
```

**Expected**: Both files exist with correct metadata

---

### 12. Example Data

**Criterion**: Example datasets are available and valid

**Validation**:
```bash
test -f "data/examples/example_bulk.csv" && echo "✓ Bulk example exists"
test -f "data/examples/example_single_cell.h5ad" && echo "✓ Single-cell example exists"

# Verify data can be read
python3 -c "
import pandas as pd
df = pd.read_csv('data/examples/example_bulk.csv', index_col=0)
print(f'✓ Bulk data: {df.shape[0]} genes × {df.shape[1]} samples')
"
```

**Expected**: Both example files exist and are readable

---

## Phase 1 Complete When

All 12 criteria above pass validation. The system should:

1. ✅ Ingest public RNA datasets (bulk and single-cell)
2. ✅ Normalize deterministically
3. ✅ Generate embeddings via canonical pipeline
4. ✅ Validate dimensionality correctly
5. ✅ Persist embeddings and metadata
6. ✅ Generate visualization projections
7. ✅ Enforce non-medical constraints
8. ✅ Use standardized configuration patterns

## What is NOT Phase 1

The following are explicitly out of scope and belong to future phases:

- ❌ Cell state clustering (Phase 2)
- ❌ State transition modeling (Phase 3)
- ❌ Authentication/authorization
- ❌ Web dashboard UI
- ❌ Batch correction implementation
- ❌ Model optimization/tuning
- ❌ Additional API endpoints beyond Phase 1 scope

See `docs/architecture.md` for phase roadmap.
