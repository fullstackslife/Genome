# Ethics Guidelines

## Core Principles

This platform is designed as an **observability and modeling layer** for RNA expression data. It is not a medical device, diagnostic system, or treatment recommendation engine.

## Hard Constraints

### 1. No Medical Diagnosis Claims

The system must **never**:
- Diagnose any condition or state
- Classify samples as "healthy" or "sick"
- Predict disease outcomes
- Recommend treatments or interventions

### 2. No Patient Identification

The system must **never**:
- Store or process patient identifiers
- Link expression data to individual identities
- Make claims about specific individuals
- Expose personally identifiable information

### 3. Neutral Language Requirements

All code, documentation, API responses, and user interfaces must use neutral, descriptive language:

**Forbidden terms:**
- disease, diagnosis, treatment, cure
- healthy, sick, normal, abnormal
- patient, clinical, medical
- pathology, disorder, condition

**Required neutral terms:**
- baseline, divergence, variance, instability
- transition probability, confidence decay
- expression pattern, state shift
- sample, dataset, expression profile

### 4. Data Privacy Considerations

- All data processing must preserve anonymity
- No storage of identifying metadata
- Clear data retention policies
- Transparent data usage documentation

## Enforcement

These constraints are **enforceable requirements**, not suggestions. Code reviews must verify:
1. No medical terminology in code, comments, or variable names
2. No diagnostic claims in API responses
3. No patient identifiers in data schemas
4. Neutral language in all user-facing text

## Scope Boundaries

This platform:
- ✅ Models RNA expression patterns
- ✅ Infers abstract cell states
- ✅ Tracks state transitions probabilistically
- ✅ Provides observability into expression dynamics

This platform does NOT:
- ❌ Diagnose conditions
- ❌ Predict health outcomes
- ❌ Recommend treatments
- ❌ Classify samples medically

## Review Checklist

Before any code merge:
- [ ] No medical terminology found in codebase
- [ ] API responses use neutral language
- [ ] No patient identifiers in data structures
- [ ] Documentation uses approved vocabulary
- [ ] Error messages avoid medical framing
