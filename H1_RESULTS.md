# H1 Results: Index-Based Patterns
**Completed**: 2025-12-19
**Runtime**: ~10 minutes
**Hypothesis**: drift[k][lane] = f(k, lane) using polynomials/modular arithmetic

---

## Summary

**Overall Accuracy**: 69.57% (modular arithmetic)

### Results by Lane:

| Lane | Pattern | Accuracy | Notes |
|------|---------|----------|-------|
| 0 | Varying (59 values) | Low | corr=0.138 |
| 1 | Varying (57 values) | Low | corr=0.219 |
| 2 | Varying (43 values) | Low | corr=0.640 |
| 3 | Varying (45 values) | Low | corr=0.687 |
| 4 | Varying (37 values) | Low | corr=0.634 |
| 5 | Varying (28 values) | Low | corr=0.632 |
| 6 | Varying (20 values) | Low | corr=0.617 |
| 7 | Varying (14 values) | Low | corr=0.533 |
| 8 | 91.3% modular | **91.3%** | mult=0, offset=0 |
| 9 | **CONSTANT = 0** | **100%** | drift always 0 |
| 10 | **CONSTANT = 0** | **100%** | drift always 0 |
| 11 | **CONSTANT = 0** | **100%** | drift always 0 |
| 12 | **CONSTANT = 0** | **100%** | drift always 0 |
| 13 | **CONSTANT = 0** | **100%** | drift always 0 |
| 14 | **CONSTANT = 0** | **100%** | drift always 0 |
| 15 | **CONSTANT = 0** | **100%** | drift always 0 |

---

## Key Discoveries

### ✅ Upper Lanes are Zero
**Lanes 9-15 are ALWAYS zero** - this matches our neural network findings from experiment 05!

### ✅ Lane 8 is Nearly Constant
91.3% of the time, lane 8 drift = 0

### ❌ Lower Lanes Need Different Approach
Lanes 0-7 have complex patterns that don't fit simple index-based formulas

---

## Polynomial Fits

- Lane 7: 7.2% accuracy (degree 4)
- Lane 8: 26.1% accuracy (degree 3)
- **Overall**: 46.65% accuracy

**Conclusion**: Polynomials don't work

---

## PySR Symbolic Regression

- **Accuracy**: 21.74%
- **Best equation**: `0.0692 / (0.0213 + (lane²/k²))²`

**Conclusion**: PySR couldn't find exact formula

---

## Verdict

❌ **Index-based patterns are INSUFFICIENT**

While we can perfectly predict lanes 9-15 (always 0) and nearly predict lane 8 (91.3%), the critical lanes 0-7 require a different approach.

**Recommendation**: Try H2 (hash functions) or H3 (PRNG)

---

## Connection to Other Discoveries

This confirms findings from **experiments/05-ai-learns-ladder**:
- Neural network learned that lanes 9-15 = 0
- Upper lanes contribute nothing to key generation
- All complexity is in lanes 0-8

**Implication**: We only need to crack 9 lanes, not 16!
