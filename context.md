Below is a **clean, Cursor-optimized `context.md`** you can drop directly into the repo root.
This is written for **maximum signal, minimum ambiguity**, and structured exactly how Cursor reasons about scope, constraints, and sequencing.

No fluff. No marketing. No science-fair nonsense.

---

# context.md

**Project:** RNA State Intelligence Platform
**Status:** Greenfield build
**Audience:** Cursor (primary), developers (secondary)

---

## 1. Project Intent (Authoritative)

This project builds an **AI-native observability platform for RNA expression data**.

The system interprets RNA expression into **abstract, explainable cell states** and models **probabilistic transitions between those states over time or perturbation**.

This is **not**:

* a medical device
* a diagnostic system
* a treatment or recommendation engine

The platform is an **interpretation and modeling layer**, not a clinical decision system.

---

## 2. Core Mental Model

Use this framing consistently throughout the codebase:

* DNA = source code (out of scope for v1)
* RNA expression = runtime execution trace
* Cell state = inferred latent system state
* Disease = emergent drift between states (never labeled or predicted)

AI functions as a **debugger and profiler**, not a physician.

Language must remain neutral and descriptive.

---

## 3. Hard Scope Constraints (Non-Negotiable)

The system must **never**:

* diagnose disease
* predict disease outcomes
* recommend treatment
* classify samples as healthy/sick
* reference patient identity or individual medical claims

Instead use:

* baseline
* divergence
* instability
* variance
* transition probability
* confidence decay

Cursor must enforce these constraints in naming, UI, docs, and APIs.

---

## 4. Supported Data (v1)

### Inputs

* Bulk RNA-seq (raw counts + metadata)
* Single-cell RNA-seq (`.h5ad` / AnnData)
* Public datasets (e.g. GEO-style formats)

### Rules

* Preserve provenance and metadata
* Accept flexible schemas
* Never assume a single dataset format
* No private patient datasets in v1

---

## 5. System Architecture (High Level)

### Layers (must remain separated)

1. Data ingestion
2. Normalization & preprocessing
3. Foundation models
4. Cell state abstraction
5. State transition modeling
6. Visualization & API

ML logic **must not** live inside API handlers.
Visualization **must not** encode medical meaning.

---

## 6. Repository Structure (Canonical)

```
/rna-intel
  /backend
    /api            # REST endpoints only
    /services       # business logic
    /pipelines      # ingestion & processing orchestration
    /schemas        # request/response schemas
  /ml
    /preprocessing  # normalization, batch correction
    /foundation     # embedding models
    /states         # clustering & abstraction
    /transitions    # probabilistic modeling
    /evaluation     # stability & drift metrics
  /frontend
    /dashboard
    /visualizations
    /components
  /data
    /schemas
    /examples
  /docs
    architecture.md
    terminology.md
    ethics.md
    non-medical-scope.md
  context.md
  README.md
```

Cursor should scaffold files gradually, not all at once.

---

## 7. Data Processing Requirements

### Normalization

* Log normalization
* Optional batch correction
* Deterministic execution
* Reproducible outputs

All parameters must be configurable and logged.

---

## 8. Foundation Model (RNA Representation)

### Purpose

Learn **expression grammar**, not labels.

### Characteristics

* Unsupervised or self-supervised
* Input: gene expression vectors
* Output: latent embeddings
* Cross-tissue generalization preferred

### Explicit Restrictions

* No disease labels
* No phenotype prediction
* No clinical benchmarks

Evaluation focuses on:

* reconstruction error
* embedding stability
* clustering consistency

---

## 9. Cell State Abstraction (Product Core)

A **cell state** is a latent cluster inferred from embeddings.

Each state must include:

* unique state ID
* defining gene signatures
* stability score
* variance profile
* confidence interval

States are:

* versioned
* descriptive
* probabilistic
* non-diagnostic

Cells may belong to multiple states (soft assignment).

---

## 10. State Transition Modeling

### Goal

Model **how states evolve**, not why they exist.

### Requirements

* probabilistic transitions
* uncertainty propagation
* confidence decay over time
* simulation support (non-biological claims)

This enables trajectory visualization without medical interpretation.

---

## 11. API Design Principles

### Endpoints (v1)

* `/ingest`
* `/embeddings`
* `/states`
* `/transitions`
* `/compare`

### Rules

* JSON only
* developer-first
* no auth complexity in v1
* no patient identifiers

APIs expose **structure**, not conclusions.

---

## 12. Visualization Rules

### Required Views

* embedding projections (UMAP / PCA)
* state clusters
* transition graphs
* sample diffs

### UX Constraints

* no red/green health indicators
* no “normal vs abnormal”
* neutral color scales
* uncertainty must be visible

---

## 13. Evaluation Metrics (Allowed)

We evaluate:

* reproducibility
* stability across datasets
* interpretability of states
* model drift

We explicitly **do not** evaluate:

* disease accuracy
* clinical sensitivity/specificity

---

## 14. Ethics & Compliance

The following documents must exist and be enforced:

* `ethics.md`
* `non-medical-scope.md`

Cursor must treat these as **enforceable constraints**, not documentation afterthoughts.

---

## 15. Development Philosophy

* clarity > cleverness
* explainable > opaque
* modular > monolithic
* abstraction > raw biology

Biology is treated as a **complex system**, not a list of conditions.

---

## 16. Phase Roadmap (Execution Order)

### Phase 1

* ingest public RNA datasets
* normalize & embed
* visualize embeddings

### Phase 2

* define cell states
* enable state comparison

### Phase 3

* model transitions
* expose API
* finalize docs

Cursor should implement sequentially.

---

## 17. Explicit Non-Goals

Do NOT implement:

* CRISPR
* gene editing
* wet-lab workflows
* treatment pipelines
* personalized medicine claims

---

## 18. Cursor Operating Instructions

* Proceed file by file
* Ask questions **only** when blocked by architecture
* Do not add scope without instruction
* Treat constraints as hard limits

---

**End of context.md**
