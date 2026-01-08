# Approved Terminology Guide

## Core Mental Model

This platform uses a **systems-level, observability-focused** mental model for RNA expression data.

### Fundamental Analogies

- **DNA** = source code (static, out of scope for v1)
- **RNA expression** = runtime execution trace (dynamic, observable)
- **Cell state** = inferred latent system state
- **State transition** = probabilistic evolution between states
- **AI/ML** = observability and abstraction layer (debugger/profiler)

## Approved Vocabulary

### Data & Expression

| Term | Definition | Usage |
|------|------------|-------|
| Expression profile | Vector of RNA expression values | "The expression profile shows high variance" |
| Expression pattern | Observed distribution of expression | "Expression patterns differ between samples" |
| Expression matrix | Gene × sample matrix | "The expression matrix contains 20,000 genes" |
| Expression vector | Single sample's expression values | "Each expression vector is normalized" |
| Expression level | Magnitude of RNA abundance | "Expression levels vary across genes" |

### States & Patterns

| Term | Definition | Usage |
|------|------------|-------|
| Cell state | Inferred latent state from embeddings | "Cells cluster into distinct states" |
| State ID | Unique identifier for a state | "State ID 3 shows high variance" |
| Baseline state | Reference or starting state | "Deviation from baseline state" |
| State divergence | Distance from reference state | "State divergence increases over time" |
| State shift | Change in inferred state | "We observe a state shift in sample X" |
| State transition | Probabilistic movement between states | "Transition probability from state A to B" |

### Variance & Stability

| Term | Definition | Usage |
|------|------------|-------|
| Variance | Expression variability | "High variance in gene X" |
| Instability | High variance or rapid changes | "Expression instability detected" |
| Stability score | Measure of state consistency | "State has stability score of 0.85" |
| Confidence | Certainty in inference | "Confidence decays over time" |
| Confidence interval | Uncertainty bounds | "Confidence interval: [0.7, 0.9]" |
| Confidence decay | Decreasing certainty | "Confidence decay rate: 0.1 per day" |

### Processing & Analysis

| Term | Definition | Usage |
|------|------------|-------|
| Normalization | Expression scaling/transformation | "Log normalization applied" |
| Embedding | Latent representation vector | "128-dimensional embeddings generated" |
| Projection | Dimensionality reduction | "UMAP projection of embeddings" |
| Clustering | Unsupervised grouping | "Cells cluster into 5 states" |
| Reconstruction | Model output matching input | "Reconstruction error: 0.05" |

### Comparisons & Differences

| Term | Definition | Usage |
|------|------------|-------|
| Baseline | Reference point | "Compared to baseline expression" |
| Divergence | Distance from reference | "Divergence from baseline: 0.2" |
| Shift | Change in pattern | "Expression shift detected" |
| Difference | Quantitative change | "Expression difference between samples" |
| Variance profile | Distribution of variability | "Variance profile shows instability" |

## Forbidden Terms & Alternatives

See `non-medical-scope.md` for complete list. Key examples:

- ❌ "disease" → ✅ "state divergence" or "expression instability"
- ❌ "diagnosis" → ✅ "state inference" or "pattern recognition"
- ❌ "healthy/normal" → ✅ "baseline" or "reference state"
- ❌ "sick/abnormal" → ✅ "divergent" or "shifted state"
- ❌ "patient" → ✅ "sample" or "expression profile"
- ❌ "treatment" → ✅ "intervention" or "perturbation"

## Code Naming Conventions

### Variables
- `expression_profile` not `patient_data`
- `baseline_state` not `normal_state`
- `state_divergence` not `disease_score`
- `variance_score` not `health_metric`

### Functions
- `infer_state()` not `diagnose()`
- `compute_divergence()` not `check_health()`
- `normalize_expression()` not `standardize_patient()`
- `generate_embeddings()` not `classify_samples()`

### Classes
- `ExpressionMatrix` not `PatientData`
- `StateInference` not `DiagnosticModel`
- `BaselineComparator` not `HealthChecker`
- `VarianceAnalyzer` not `DiseaseDetector`

## API Endpoint Naming

- `/ingest` - ingest expression data
- `/embeddings` - retrieve embeddings
- `/states` - get inferred states (Phase 2)
- `/transitions` - state transition probabilities (Phase 3)
- `/compare` - compare expression profiles

Avoid: `/diagnose`, `/health`, `/patients`, `/disease`

## Documentation Style

### Good Examples

> "The platform infers cell states from RNA expression patterns. States represent latent system configurations, not medical conditions. High variance indicates expression instability, which may correlate with state transitions."

> "Embeddings capture expression grammar in a low-dimensional space. Clustering embeddings reveals distinct baseline states and divergent patterns."

### Bad Examples

> "The platform diagnoses diseases from patient RNA data. It identifies healthy and sick samples based on expression patterns." ❌

> "The model predicts health outcomes and recommends treatments." ❌

## Consistency Rules

1. **Always** use "sample" not "patient"
2. **Always** use "baseline" not "normal/healthy"
3. **Always** use "divergence" not "disease/abnormality"
4. **Always** use "state" not "condition"
5. **Always** frame as "observation" not "diagnosis"

## Review Process

Before committing code:
1. Search for forbidden terms
2. Verify variable/function names use approved vocabulary
3. Check API responses for neutral language
4. Review comments and docstrings
5. Ensure UI labels (if any) use approved terms
