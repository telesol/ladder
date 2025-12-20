# Plan: Compute First, Then Reason

**Date:** 2025-12-19
**Status:** Ready for collaboration

---

## The Problem

We've been asking LLMs to factor large numbers. That's backwards.
- LLMs are pattern recognizers, not calculators
- Factoring 60-bit numbers requires computation, not reasoning
- Current approach: LLM tries to factor → timeout/gibberish

## The Solution

**Phase 1: COMPUTE (Python)**
- Use sympy/gmpy2 to factor m[36]-m[70]
- Store results in structured JSON
- This is deterministic - no AI needed

**Phase 2: REASON (LLMs)**
- Feed factorizations to models
- Ask: "What's the pattern in these prime indices?"
- This is what LLMs are good at

---

## Phase 1: Computation Pipeline

### Step 1.1: Factor all m-values
```python
# Use sympy.factorint with timeout
# For very large numbers, use ECM (Elliptic Curve Method)
# Output: {n: {m: value, factors: {p1: e1, p2: e2}, prime_indices: [i1, i2]}}
```

### Step 1.2: Compute prime indices
```python
# For each prime factor p, find i where prime(i) = p
# Store as: prime_indices: [7, 30] means p[7] × p[30]
```

### Step 1.3: Store in JSON
```json
{
  "36": {
    "m": 22185816780,
    "factors": {"2": 2, "3": 1, "5": 1, ...},
    "prime_indices": [1, 2, 3, ...]
  }
}
```

---

## Phase 2: Pattern Recognition

### Step 2.1: Local models (parallel)
- Spark1 (qwq:32b): Look for n-relationships in indices
- Spark2 (phi4:14b): Look for self-references to m[2]-m[35]
- Box211 (deepseek:70b): Deep mathematical analysis
- Box212 (mixtral): Broad hypothesis generation

### Step 2.2: Cloud models (if needed)
- qwen3-coder:480b-cloud on Spark2
- Send condensed factorization data
- Ask specific pattern questions

### Step 2.3: Synthesis
- Maestro (Claude) collects all hypotheses
- Verify each against actual data
- Build unified formula

---

## Resources Available

| Resource | Capability | Best For |
|----------|------------|----------|
| Spark1 | 128GB RAM, GPU | Heavy computation, qwq:32b |
| Spark2 | 128GB RAM, GPU | phi4:14b, cloud models |
| Box211 | GPU | deepseek-r1:70b |
| Box212 | GPU | mixtral:8x22b |
| Python/sympy | Exact math | Factorization |
| User laptop | Experiment data | New approaches |

---

## Experiment Integration Point

**USER:** Upload your experiment here:
- Path: `/home/solo/LA/experiments/`
- Or describe it and I'll integrate

**CLAUDE:** Will read and merge with this plan.

---

## Current State

- [x] m[2]-m[35] formulas verified (in FORMULA_SUMMARY.md)
- [ ] m[36]-m[70] factorizations (NEED TO COMPUTE)
- [ ] Pattern recognition on factorizations
- [ ] Unified formula derivation

---

## Quick Start

```bash
# Kill current LLM tasks (they're doing the wrong thing)
pkill -f "ollama run"

# Run computation script (to be created)
python compute_factorizations.py

# Then dispatch to models with factorization data
./dispatch_pattern_recognition.sh
```

---

## Waiting For

1. User experiment upload
2. Confirmation to proceed with computation-first approach
