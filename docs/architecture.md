# Architecture Overview

## System Design

The RNA State Intelligence Platform is built as a modular, layered system with clear separation of concerns.

## Layer Architecture

```
┌─────────────────────────────────────┐
│   Visualization & API Layer        │
│   (frontend/, backend/api/)        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   State Transition Modeling          │
│   (ml/transitions/) - Phase 3        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Cell State Abstraction             │
│   (ml/states/) - Phase 2             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Foundation Models                  │
│   (ml/foundation/)                   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Preprocessing & Normalization      │
│   (ml/preprocessing/)                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Data Ingestion                    │
│   (backend/pipelines/)               │
└─────────────────────────────────────┘
```

## Phase 1 Components

### 1. Data Ingestion (`backend/pipelines/`)

**Purpose**: Accept and validate RNA expression data

**Inputs**:
- Bulk RNA-seq (CSV/TSV)
- Single-cell RNA-seq (.h5ad/AnnData)

**Outputs**:
- Validated expression matrices
- Preserved metadata
- Sample provenance tracking

**Key Files**:
- `backend/pipelines/ingestion.py` - IngestionService
- `backend/schemas/data_schemas.py` - Data structures

### 2. Normalization (`ml/preprocessing/`)

**Purpose**: Deterministic normalization of expression data

**Process**:
- Log normalization (log1p)
- Optional batch correction (placeholder)
- Parameter logging for reproducibility

**Key Files**:
- `ml/preprocessing/normalization.py` - NormalizationPipeline
- `ml/preprocessing/config.py` - Parameters

### 3. Foundation Model (`ml/foundation/`)

**Purpose**: Generate latent embeddings from normalized expression

**Architecture**:
- Simple autoencoder
- Unsupervised training
- Reconstruction loss

**Key Files**:
- `ml/foundation/autoencoder.py` - Model architecture
- `ml/foundation/trainer.py` - Training loop
- `ml/foundation/inference.py` - Embedding generation

### 4. Visualization (`frontend/visualizations/`)

**Purpose**: Display embeddings in 2D/3D space

**Methods**:
- UMAP projection
- PCA projection
- Interactive scatter plots

**Key Files**:
- `frontend/visualizations/embedding_viz.py` or `.tsx`
- `frontend/components/VisualizationContainer.tsx`

### 5. API (`backend/api/`)

**Purpose**: Expose functionality via REST endpoints

**Endpoints**:
- `POST /ingest` - Ingest expression data
- `GET /embeddings` - Retrieve embeddings
- `POST /embeddings/generate` - Generate embeddings

**Key Files**:
- `backend/api/ingest.py`
- `backend/api/embeddings.py`
- `backend/main.py` - FastAPI app

## Data Flow (Phase 1)

```
Public RNA Data
    ↓
[Ingestion Service]
    ↓
Expression Matrix + Metadata
    ↓
[Normalization Pipeline]
    ↓
Normalized Expression Matrix
    ↓
[Foundation Model]
    ↓
Latent Embeddings
    ↓
[Visualization] or [API Response]
```

## Design Principles

### 1. Modularity

Each layer is independently testable and replaceable. ML logic never lives in API handlers.

### 2. Determinism

All processing steps are reproducible:
- Fixed random seeds
- Logged parameters
- Versioned models

### 3. Neutral Language

All components use neutral terminology:
- No medical claims
- No diagnostic language
- Descriptive, not prescriptive

### 4. Abstraction

Biology is treated as a complex system:
- Expression = runtime signal
- States = inferred configurations
- Transitions = probabilistic evolution

## Technology Stack

- **Backend**: Python 3.10+, FastAPI
- **ML**: PyTorch, scikit-learn
- **Data**: pandas, numpy, scanpy, anndata
- **Visualization**: UMAP, PCA, Plotly/D3.js
- **API**: FastAPI, Pydantic

## Future Phases

### Phase 2: Cell State Abstraction
- Clustering embeddings into states
- State signature identification
- State comparison tools

### Phase 3: State Transitions
- Probabilistic transition modeling
- Trajectory visualization
- Confidence decay over time

## Constraints

See `docs/ethics.md` and `docs/non-medical-scope.md` for enforced constraints on:
- Language and terminology
- Medical claims
- Patient identification
- Scope boundaries
