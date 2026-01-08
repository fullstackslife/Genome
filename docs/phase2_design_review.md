# Hostile Peer Review: Phase 2 Design Specification

**Review Date**: Design review before implementation
**Reviewer**: Critical analysis for safety and clarity
**Target**: `docs/phase2_design.md`

---

## Executive Summary

This review identifies **critical ambiguities**, **potential misuse scenarios**, and **gaps** that could lead to:
- Medical terminology violations
- Scope creep into Phase 3
- Ambiguous state definitions
- Versioning conflicts
- Output interpretation risks

**Severity Levels**:
- 🔴 **CRITICAL**: Must fix before implementation
- 🟡 **HIGH**: Should fix to prevent issues
- 🟢 **MEDIUM**: Clarification recommended

---

## 🔴 CRITICAL ISSUES

### 1. Ambiguous "Defining Features" Specification

**Location**: Section 3, "Defining Features"

**Problem**: 
- States "Vector or set of embedding dimension indices"
- Example: "State 3 is defined by high values in embedding dimensions [5, 12, 45, 78]"
- **Ambiguity**: What does "high values" mean? Relative to what? What threshold?

**Risk**:
- Implementers might use gene expression thresholds (medical interpretation)
- Could lead to "this state has high expression of disease genes" claims
- No clear definition of "characteristic"

**Fix Required**:
- Specify: "Defining features are embedding dimension indices where samples in this state have statistically different distributions compared to all samples"
- Add: "No gene-level interpretation. Features are purely embedding-space properties."
- Clarify: "High" means relative to embedding space distribution, not expression levels

---

### 2. Missing Input Validation Specification

**Location**: Section 2, "Allowed Inputs"

**Problem**:
- Lists allowed inputs but doesn't specify validation rules
- No checks for:
  - Embedding dimension consistency
  - Missing metadata
  - Corrupted embeddings
  - Version mismatches

**Risk**:
- Phase 2 could accept embeddings from wrong model version
- Could process corrupted data silently
- No guardrails against misuse

**Fix Required**:
- Add explicit validation requirements:
  - Embedding dimension must match model version metadata
  - All required metadata fields must be present
  - Embeddings must be numeric and finite
  - Sample count must match metadata
- Specify error handling: fail fast, clear error messages

---

### 3. "Stability Score" Interpretation Risk

**Location**: Section 3, "Stability Score"

**Problem**:
- Says "Not: A measure of health, normality, or desirability"
- But doesn't prevent users from interpreting it that way
- No explicit guardrails in output format

**Risk**:
- Users might interpret low stability = "unhealthy" or "abnormal"
- High stability might be interpreted as "normal" or "baseline"
- Medical interpretation could slip in through user inference

**Fix Required**:
- Add to output specification: "Stability scores must be accompanied by explicit disclaimer in all outputs"
- Specify: "API responses must include metadata explaining that stability is a clustering metric, not a biological or medical measure"
- Add validation: Any output that could be interpreted medically must include neutral language disclaimer

---

### 4. Soft Assignment Threshold Ambiguity

**Location**: Section 4, "Soft Assignment"

**Problem**:
- Says "threshold (e.g., 0.1)" but doesn't specify:
  - Is this configurable?
  - Is this fixed?
  - Who decides?
  - What happens at boundaries?

**Risk**:
- Different implementations might use different thresholds
  - Breaks reproducibility
  - Makes state assignments incomparable
- Boundary cases undefined (probability exactly 0.1)

**Fix Required**:
- Specify: "Threshold is a fixed constant: 0.1 (10%)"
- Or: "Threshold is configurable but must be logged and versioned with state model"
- Define boundary behavior: "Probability >= threshold is considered active"
- Add to versioning: Threshold value must be in state model metadata

---

### 5. State Drift Handling Ambiguity

**Location**: Section 4, "State Drift"

**Problem**:
- Says "Changes in state definitions over time (when new data is added)"
- But doesn't specify:
  - When does state drift occur? (Every new sample? Batch updates?)
  - How is drift detected?
  - When should state model be re-versioned?
  - What triggers a new state model version?

**Risk**:
- Implementers might auto-update states on every new sample (bad)
- Or never update states (also bad)
- No clear policy for when to create new state model version

**Fix Required**:
- Specify: "State models are immutable. New data requires new state model version."
- Or: "State models can be updated, but changes must trigger version increment and change log"
- Define: "State drift detection criteria" (e.g., >X% of samples change primary state)
- Clarify: This is Phase 2 scope (state definition changes), not Phase 3 (temporal transitions)

---

## 🟡 HIGH PRIORITY ISSUES

### 6. "State Comparison" Scope Ambiguity

**Location**: Section 6, "State Comparison"

**Problem**:
- Says "Comparing states to each other" and "Measuring distances between states"
- But doesn't specify:
  - Can states from different state model versions be compared?
  - What does "similar/dissimilar" mean?
  - Is this just distance in embedding space?

**Risk**:
- Users might compare states across incompatible versions
- "Similar states" could be interpreted as "similar biological conditions"
- Medical interpretation risk

**Fix Required**:
- Specify: "States can only be compared within the same state model version"
- Add: "Cross-version comparison requires explicit version mapping (future feature)"
- Clarify: "Similar" means "close in embedding space", not "biologically similar"
- Add disclaimer to comparison outputs

---

### 7. Missing Output Format Specification

**Location**: Throughout document

**Problem**:
- Defines state object conceptually but doesn't specify:
  - API response format
  - File storage format
  - JSON schema (even conceptual)
  - Required vs optional fields

**Risk**:
- Implementers might add fields that enable medical interpretation
- No standard format for interoperability
- Could include forbidden metadata

**Fix Required**:
- Add section: "Output Format Specification (Conceptual)"
- Specify required fields (state_id, stability_score, etc.)
- List forbidden fields (any medical terminology, labels, annotations)
- Define optional fields and their constraints

---

### 8. "Confidence" vs "Confidence Interval" Ambiguity

**Location**: Section 3, multiple places

**Problem**:
- Uses "Confidence Interval" for state assignment uncertainty
- Also uses "Confidence" for sample assignment (Section 3, "Sample-State Assignment")
- These are different concepts but not clearly distinguished

**Risk**:
- Confusion between:
  - Statistical confidence intervals (uncertainty bounds)
  - Assignment confidence (certainty of state membership)
- Could lead to misinterpretation

**Fix Required**:
- Rename one to avoid confusion:
  - "Confidence Interval" → "Uncertainty Bounds" or "Assignment Uncertainty"
  - "Confidence" → "Assignment Certainty" or "State Membership Confidence"
- Clearly distinguish in definitions

---

### 9. Versioning Format Ambiguity

**Location**: Section 3, "Versioning Rules"

**Problem**:
- Shows examples: "v1.0", "v2.1", "v1_state_3", "state_3_v1"
- Multiple formats shown but no standard specified
- state_id format also ambiguous

**Risk**:
- Inconsistent versioning across implementations
- Parsing/validation becomes impossible
- State IDs might collide

**Fix Required**:
- Specify standard format:
  - State model version: "v{Major}.{Minor}" (semantic versioning)
  - State ID: "state_{number}_v{model_version}" or "{model_version}_state_{number}"
- Define uniqueness rules
- Specify validation requirements

---

### 10. Missing Edge Case Handling

**Location**: Throughout

**Problem**:
- No specification for:
  - What if all samples have uniform probability distribution? (no clear primary state)
  - What if clustering finds only 1 state? (is this valid?)
  - What if clustering finds 100+ states? (is this valid?)
  - What if no samples can be confidently assigned? (all probabilities < threshold)

**Risk**:
- Implementers might handle edge cases inconsistently
- Could lead to errors or unexpected behavior
- Medical interpretation of edge cases

**Fix Required**:
- Add section: "Edge Cases and Validation Rules"
- Specify:
  - Minimum/maximum number of states (e.g., 2-50)
  - Handling of uniform probability distributions
  - Handling of low-confidence assignments
  - Validation that at least some samples have clear primary state

---

## 🟢 MEDIUM PRIORITY ISSUES

### 11. "Biological Systems" Language Risk

**Location**: Section 4, "Soft Assignment"

**Problem**:
- Rationale says: "Biological systems are continuous, not discrete"
- This is a biological claim, even if true

**Risk**:
- Could be interpreted as making biological statements
- Violates "no biological interpretation" principle in Section 5

**Fix Required**:
- Change to: "Expression patterns in embedding space are continuous, not discrete"
- Remove biological framing
- Focus on mathematical/statistical rationale

---

### 12. Missing Reproducibility Specification

**Location**: Section 4, "State Inference Rules"

**Problem**:
- Says clustering is unsupervised but doesn't specify:
  - Must clustering be deterministic?
  - What random seeds are used?
  - How is reproducibility ensured?

**Risk**:
- Non-deterministic clustering breaks reproducibility
- State assignments might vary between runs
- Violates Phase 1 determinism principle

**Fix Required**:
- Add: "State inference must be deterministic given same inputs and random seed"
- Specify: "Random seed must be logged with state model version"
- Require: "Same embeddings + same seed = same state assignments"

---

### 13. "State Model" vs "State" Confusion

**Location**: Throughout document

**Problem**:
- Uses "state model" (collection of states) and "state" (individual state)
- Sometimes ambiguous which is meant
- Versioning applies to both but not clearly distinguished

**Risk**:
- Confusion about what gets versioned
- State-level vs model-level versioning unclear

**Fix Required**:
- Consistently use:
  - "State Model" = collection of states (versioned as whole)
  - "State" = individual state within a model (not independently versioned)
- Clarify: States are versioned only as part of state model

---

### 14. Missing Performance/Scale Constraints

**Location**: Throughout

**Problem**:
- No specification for:
  - Maximum number of samples
  - Maximum number of states
  - Computational limits
  - Memory constraints

**Risk**:
- Implementers might design for wrong scale
  - Too small: can't handle real datasets
  - Too large: over-engineered
- No guidance for optimization decisions

**Fix Required**:
- Add: "Scale Constraints (Guidance)"
- Specify expected ranges:
  - Samples: 100 - 1,000,000
  - States: 3 - 50 (typical)
  - Embedding dimensions: 64 - 512 (from Phase 1)
- Note: These are guidelines, not hard limits

---

### 15. Visualization Scope Ambiguity

**Location**: Section 6, "State Visualization"

**Problem**:
- Says "Visualizing states in embedding space"
- But doesn't specify:
  - Is this Phase 2 or just conceptual?
  - What visualization methods?
  - Output format?

**Risk**:
- Could be interpreted as requiring interactive UI (out of scope)
- Or could be interpreted as just data preparation (unclear)

**Fix Required**:
- Clarify: "Phase 2 generates visualization data (coordinates, colors, etc.), not interactive UI"
- Specify: "Visualization data format: coordinates + state assignments + metadata"
- Note: "Interactive visualization UI is future phase"

---

## Additional Concerns

### 16. Missing API Endpoint Specification

**Problem**: No specification of Phase 2 API endpoints

**Risk**: Implementers might design incompatible APIs

**Recommendation**: Add conceptual API specification:
- `POST /states/infer` - Infer states from embeddings
- `GET /states/{state_model_id}` - Retrieve state model
- `GET /states/{state_model_id}/assignments` - Get sample assignments
- `GET /states/{state_model_id}/compare` - Compare states

---

### 17. Missing Error Handling Specification

**Problem**: No specification of error conditions and handling

**Risk**: Inconsistent error handling, poor user experience

**Recommendation**: Add error handling section:
- Invalid embeddings (wrong dimension, NaN, Inf)
- Missing metadata
- Version mismatches
- Clustering failures
- All errors must use neutral language

---

### 18. Missing Testing Requirements

**Problem**: No specification of how to validate Phase 2 correctness

**Risk**: Implementers might not test properly

**Recommendation**: Add testing requirements:
- Determinism tests (same inputs = same outputs)
- Terminology enforcement tests
- Edge case tests
- Reproducibility tests

---

## Summary of Required Fixes

### Must Fix Before Implementation (Critical):
1. Clarify "defining features" specification
2. Add input validation requirements
3. Add output disclaimers for stability scores
4. Specify soft assignment threshold policy
5. Define state drift handling policy

### Should Fix (High Priority):
6. Clarify state comparison scope and constraints
7. Add output format specification
8. Distinguish confidence vs confidence interval
9. Standardize versioning format
10. Add edge case handling specification

### Recommended (Medium Priority):
11. Remove biological language from rationale
12. Add reproducibility requirements
13. Clarify state model vs state terminology
14. Add scale constraints guidance
15. Clarify visualization scope

---

## Positive Aspects

The design specification is generally strong:
- ✅ Clear non-claims section
- ✅ Good Phase 2/Phase 3 boundary
- ✅ Strong emphasis on neutral language
- ✅ Clear input constraints
- ✅ Good conceptual foundation

The issues identified are primarily:
- Ambiguities that could lead to inconsistent implementation
- Missing specifications that could enable misuse
- Terminology that could enable medical interpretation

---

## Recommendation

**Before implementation**, update `docs/phase2_design.md` to address:
- All 🔴 CRITICAL issues
- All 🟡 HIGH PRIORITY issues
- Selected 🟢 MEDIUM PRIORITY issues (based on implementation approach)

This will ensure:
- Consistent implementation
- Safety from medical terminology violations
- Clear boundaries and constraints
- Reproducible, deterministic behavior

---

**End of Hostile Peer Review**
