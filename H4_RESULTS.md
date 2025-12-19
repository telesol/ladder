# H4 Results: Recursive/Drift Ladder Patterns
**Completed**: 2025-12-19
**Runtime**: ~8 minutes
**Hypothesis**: drift[k+1] = f(drift[k], drift[k-1], ...)

---

## Summary

**Overall Accuracy**: 70.50% (BEST of H1-H4!)

### Best Results by Lane:

| Lane | Best Pattern | Accuracy | Formula |
|------|--------------|----------|---------|
| 0-6 | Complex | <70% | No simple recursion found |
| **7** | **Affine** | **82.4%** | `23 × drift[k-1] mod 256` |
| **8** | **Affine** | **92.6%** | `1 × drift[k-1] mod 256` |
| 9-15 | Bridge spacing | **100%** | `drift[k] = drift[k-5]` (always 0) |

**Overall average**: 70.50%

---

## Tests Performed

1. ✅ Affine recurrence: `drift[k] = A × drift[k-1] + C mod 256`
2. ✅ Polynomial recurrence: `drift[k] = drift[k-1]^n mod 256`
3. ✅ Bridge spacing: `drift[k] = drift[k-spacing]`
4. ✅ Multi-step: `drift[k] = f(drift[k-1], drift[k-2])`

---

## Key Discoveries

### 1. Lane 8 is Nearly Perfect! ⭐
```
drift[k][8] = drift[k-1][8] mod 256
```
**92.6% accuracy** - highest of any single-lane formula!

Lane 8 follows a simple identity recurrence with occasional deviations.

### 2. Lane 7 Uses Affine Pattern
```
drift[k][7] = 23 × drift[k-1][7] mod 256
```
**82.4% accuracy** - multiplier is 23 (a prime!)

### 3. Upper Lanes Have 5-Spacing
```
drift[k][9..15] = drift[k-5][9..15]
```
**100% accuracy** because drift is always 0 (confirmed in H1).

This suggests the drift might be calculated every 5 puzzles and cached.

### 4. Lower Lanes are Complex
Lanes 0-6 don't follow simple recursive patterns (<70% accuracy).

---

## Analysis

### Lane Complexity Hierarchy

**Simple → Complex:**
- Lanes 9-15: Constant (always 0) - TRIVIAL
- Lane 8: Identity recurrence (92.6%) - VERY SIMPLE
- Lane 7: Affine with prime multiplier (82.4%) - SIMPLE
- Lanes 0-6: No simple pattern (<70%) - COMPLEX

**Hypothesis**: The drift generator was designed with decreasing complexity:
- Upper lanes don't matter (always 0)
- Middle lanes use simple recurrence
- Lower lanes require complex logic

### Why 23 for Lane 7?

23 is prime and appears in m-sequence (m[8] = 23)!

**Connection**:
- m[8] = 23
- Lane 7 drift uses multiplier 23
- Is there a formula linking m[n] → drift multipliers?

---

## Comparison to H1-H3

| Hypothesis | Overall | Lane 8 | Lane 7 | Lanes 9-15 |
|------------|---------|--------|--------|------------|
| H1 (Modular) | 69.57% | 91.3% | ? | 100% |
| H2 (Hash) | 0.82% | <1% | <1% | <1% |
| H3 (PRNG) | 69.20% | ? | ? | ? |
| **H4 (Recursive)** | **70.50%** | **92.6%** | **82.4%** | **100%** |

**H4 is the best overall** and shows the clearest lane-specific patterns.

---

## Verdict

✅ **Recursive patterns WORK** (70.50% accuracy)

✅ **Lane 8 nearly solved** (92.6% with identity recurrence)

❌ **Lanes 0-6 still need work** (<70%)

**Recommendation**:
1. Use H4 for lanes 7-8
2. Use H1 (modular) for lanes 0-6
3. Combine into hybrid approach
4. OR: Focus on m-sequence approach (might bypass drift entirely)

---

## Next Actions

### If Continuing Drift Approach:
1. Train ML model on residuals for lanes 0-6
2. Build hybrid: H4 (lanes 7-8) + H1 (lanes 0-6) + corrections
3. Test on validation set

### If Pivoting to M-Sequence:
1. Use RKH's convergent patterns
2. Generate m[71-160] candidates
3. Validate on Bitcoin bridges
4. Derive drift from m-sequence if needed

---

## Files Generated

- `H4_output.log` - Full test output
- `H4_results.json` - Detailed results by lane
- `H4_RESULTS.md` - This summary

---

**Conclusion**: H4 achieved the best overall accuracy (70.50%) and discovered lane-specific recursive patterns. Lane 8 is nearly solved at 92.6%!
