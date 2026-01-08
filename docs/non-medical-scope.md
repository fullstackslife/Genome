# Non-Medical Scope Constraints

## Purpose

This document defines **hard constraints** that must be enforced throughout the codebase. These are not suggestions—they are requirements that define the platform's scope.

## Forbidden Terms List

The following terms are **forbidden** in:
- Code (variable names, function names, class names)
- Comments and docstrings
- API endpoint names and responses
- Configuration files
- Documentation
- User interface labels

### Medical/Clinical Terms
- disease, diseases
- diagnosis, diagnose, diagnostic
- treatment, treat, therapy, therapeutic
- cure, healing, recovery
- patient, patients
- clinical, clinic
- medical, medicine
- pathology, pathological
- disorder, condition
- symptom, symptoms
- prognosis, prognosticate
- health, healthy, unhealthy
- sick, sickness
- normal, abnormal (in medical context)
- wellness, unwell

### Alternative Neutral Terms

Use these instead:

| Forbidden | Neutral Alternative |
|-----------|-------------------|
| disease | state divergence, expression instability |
| diagnosis | state inference, pattern recognition |
| treatment | intervention, perturbation |
| patient | sample, dataset, expression profile |
| healthy/normal | baseline, reference state |
| sick/abnormal | divergent, shifted state |
| medical | biological, expression-based |
| clinical | experimental, observational |

## Required Neutral Terminology

### Core Concepts

- **Baseline**: Reference expression pattern
- **Divergence**: Deviation from baseline
- **Variance**: Expression variability
- **Instability**: High variance or rapid changes
- **Transition probability**: Likelihood of state change
- **Confidence decay**: Decreasing certainty over time
- **State shift**: Change in expression pattern
- **Expression profile**: RNA expression vector
- **Cell state**: Inferred latent state (not medical condition)

### Mental Model

- DNA = source code (static)
- RNA expression = runtime execution trace (dynamic)
- Cell state = inferred latent system state
- State transition = probabilistic evolution
- AI = observability and abstraction layer

## Code Review Checklist

Every code review must verify:

- [ ] No forbidden terms in code
- [ ] No forbidden terms in comments
- [ ] Variable/function names use neutral terms
- [ ] API endpoints use neutral naming
- [ ] API responses contain no medical claims
- [ ] Error messages use neutral language
- [ ] Log messages avoid medical framing

## API Response Validation

All API responses must:
1. Use neutral terminology only
2. Avoid any diagnostic language
3. Frame results as "observations" not "conclusions"
4. Include uncertainty/confidence metrics
5. Never classify samples medically

### Example: Good Response
```json
{
  "sample_id": "sample_001",
  "embedding": [0.1, 0.2, ...],
  "baseline_divergence": 0.15,
  "expression_variance": 0.08,
  "confidence": 0.92
}
```

### Example: Bad Response
```json
{
  "sample_id": "sample_001",
  "diagnosis": "healthy",  // ❌ FORBIDDEN
  "disease_risk": 0.1,     // ❌ FORBIDDEN
  "treatment": "none"      // ❌ FORBIDDEN
}
```

## Enforcement Mechanism

1. **Automated scanning**: Use grep/ripgrep to search for forbidden terms
2. **Code review**: Manual verification in PR reviews
3. **CI/CD checks**: Automated validation in pipeline
4. **Documentation review**: Regular audits of docs

## Scope Boundaries

### In Scope (Phase 1)
- RNA expression data ingestion
- Deterministic normalization
- Unsupervised embedding generation
- Embedding visualization
- State pattern observation

### Out of Scope (All Phases)
- Medical diagnosis
- Treatment recommendations
- Patient identification
- Clinical decision support
- Health outcome prediction

## Violation Handling

If forbidden terms are found:
1. Immediate flag in code review
2. Required replacement with neutral terms
3. Documentation of why the term was used
4. Update to this document if new patterns emerge
