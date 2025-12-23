# TASK 4: Drift Formula Discovery Results

**Date**: 2025-12-23
**Status**: NO 100% SOLUTION FOUND
**Next Action**: Per-lane PySR models

---

## Summary

Tested 5 approaches for discovering drift evolution formula:
1. Unified PySR model (TASK 4)
2. H1: Index-based patterns
3. H2: Cryptographic hash functions
4. H3: PRNG models
5. H4: Recursive patterns

**Best overall**: H4 Affine Recurrence (70.5%)

---

## Results

### TASK 4: Unified PySR Model

**Accuracy**: 1.7% (2/116 validation samples)
**R²**: 0.1355
**MAE**: 64.01

**Best equation** (complexity 17):
```
drift = -2*lane - Mod(exponent, Mod(steps - 120.6, -lane/steps - 114.9)) + 33.9
```

**Conclusion**: Unified model FAILED. Drift pattern too complex for single formula.

---

### H1: Index-Based Patterns

**Approaches tested**:
- Polynomial fits (degree 0-4)
- Modular arithmetic: `drift = (a*k + b) mod 256`
- PySR symbolic regression

**Best**: Modular arithmetic (69.57%)
- Lanes 9-15: 100% (constant 0)
- Lanes 0-8: 0-91% (varies by lane)

**Conclusion**: FAILED (< 90%)

---

### H2: Cryptographic Hash Functions

**Hashes tested**:
- SHA256, SHA512, SHA1, MD5, RIPEMD160
- HASH256, HASH160 (Bitcoin-specific)
- Various encodings: bytes, packed, string
- Salted/seeded variants
- XOR combinations

**Best**: SHA512 string concatenation (0.82%)

**Conclusion**: FAILED. Drift is NOT hash-based.

---

### H3: PRNG (Pseudo-Random Generators)

**Models tested**:
- Python `random.Random()`
- NumPy random
- LCG variants (MINSTD, GLIBC, BORLAND, etc.)
- Brute force seed search (0-100,000)

**Best**: MINSTD LCG seed=0 (69.2%)

**Conclusion**: FAILED. Drift is NOT standard PRNG.

---

### H4: Recursive Patterns (Drift Ladder)

**Approaches tested**:
1. Affine recurrence: `drift_next = (A*drift + C) mod 256`
2. Polynomial recurrence: `drift_next = drift^n mod 256`
3. Bridge spacing: `drift[k] = drift[k-spacing]`
4. Multi-step (linear/fibonacci)

**Best**: Affine recurrence (70.5% overall)

**Per-lane results (affine)**:
```
Lane  0:  5.9% | A=10,  C=163
Lane  1: 11.8% | A=120, C=0
Lane  2: 23.5% | A=2,   C=0
Lane  3: 35.3% | A=7,   C=0
Lane  4: 47.1% | A=31,  C=0
Lane  5: 58.8% | A=178, C=0
Lane  6: 70.6% | A=5,   C=0
Lane  7: 82.4% | A=23,  C=0
Lane  8: 92.6% | A=1,   C=0
Lane  9: 100%  | constant 0
Lane 10: 100%  | constant 0
Lane 11: 100%  | constant 0
Lane 12: 100%  | constant 0
Lane 13: 100%  | constant 0
Lane 14: 100%  | constant 0
Lane 15: 100%  | constant 0
```

**Observation**: Accuracy increases with lane number!
Lanes with less data (activated later) have simpler/more predictable patterns.

**Conclusion**: PARTIAL SUCCESS. Lanes 7-8 show promise (>80%).

---

## Key Insights

1. **No unified formula exists** - each lane has independent drift generator
2. **Complexity decreases with lane number** - Lane 8 (92.6%) >> Lane 0 (5.9%)
3. **Lanes 9-15 solved** - always 0 (never activated in puzzles 1-70)
4. **H4 affine recurrence closest** to solution for high lanes

---

## Next Steps: Per-Lane PySR Models

**Strategy**: Train 16 independent PySR models (one per lane)

**Priority order** (based on H4 results):
1. **Lane 8**: 92.6% baseline → high chance of 100%
2. **Lane 7**: 82.4% baseline → good chance
3. **Lane 6**: 70.6% baseline → medium chance
4. **Lane 5**: 58.8% baseline
5. **Lane 4**: 47.1% baseline
6. **Lanes 0-3**: <36% baseline → low chance

**Features per lane**:
- `k` (puzzle number)
- `steps_since_activation` (k - lane×8)
- Previous drift values (if recursive)

**Goal**: Find 100% accurate formula for at least Lane 8, then work down.

**Estimated runtime**:
- 2 hours per lane (high priority)
- 16-20 hours total for all lanes

**Acceptance criteria**: 100% exact match on validation set (puzzles 56-69)

---

## Files

**Results**:
- `results/H1_research_output.txt` - Index-based results
- `results/H2_research_output.txt` - Hash function results
- `results/H3_research_output.txt` - PRNG results
- `results/H4_results.json` - Recursive pattern results (detailed)
- `experiments/01-pysr-symbolic-regression/drift_formula/results/drift_equations_unified.csv` - TASK 4 equations

**Next**: Per-lane training scripts in `experiments/01-pysr-symbolic-regression/drift_formula/`
