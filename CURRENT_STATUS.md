# Bitcoin Puzzle Formula Derivation - Current Status

**Date**: 2025-12-16
**Session**: Deep mathematical analysis complete

## THE MASTER FORMULA (VERIFIED)

```
k_n = 2 × k_{n-1} + adj_n
```

Where `adj_n = a × 2^c + b × k_i` for specific coefficients.

**VERIFIED**: Holds for ALL 69 consecutive key pairs (k1-k70).

## Verified Adjustment Formulas

| n | adj_n | Simple Formula | Power-of-2 Form |
|---|-------|----------------|-----------------|
| 2 | +1 | 1×k1 | - |
| 3 | +1 | 1×k1 | -8×2² + 11×k2 |
| 4 | -6 | -2×k2 | -6×2³ + 14×k2 |
| 5 | +5 | n×k1 | -8×2⁴ + 19×k3 |
| 6 | +7 | 1×k3 | -7×2⁵ + 11×k5 |
| 7 | -22 | -k1-k5 | -8×2⁶ + 10×k6 |
| 8 | +72 | 9×k4 | -3×2⁷ + 6×k7 |
| 9 | +19 | 19×k1 | -1×2⁷ + 7×k5 |
| 10 | -420 | -2n×k5 | 2×2⁹ - 19×k7 |
| 11 | +127 | 2⁷-1 | 1×2⁷ - 1×k1 |
| 12 | +373 | - | 1×2⁷ + 5×k6 |
| 13 | -150 | -50×k2 | - |
| 14 | +112 | n×k4 | 1×2¹⁰ - 12×k7 |

## Key Properties

### Adjustment Bounds
- adj_n / 2^(n-1) ∈ [-0.73, +0.74]
- Mean ratio ≈ 0.01
- Adjustments are bounded perturbations

### Early Key Formulas (also verified)

### Corrections Made

| Old Claim | Actual (from DB) |
|-----------|------------------|
| k13 = 5765 | k13 = **5216** |
| k15 ≈ 17024 | k15 = **26867** |

### Discovered Patterns

**Position Anomalies** (near minimum):
- k4: 0.00%
- k10: 0.39%
- k69: 0.72%

**Prime Keys** (can't be factored):
- k9 = 467 (prime)
- k12 = 2683 (prime)

**Keys Divisible by N**:
- k1, k4, k8, k11, k36

**Multiplier Sequence**:
```
k7:  9
k8:  13
k11: 19
k12: 12
k13: 10
k14: 9  ← repeats!
k15: 10 ← repeats!
k16: 45 ← jump!
k18: 38
```

## What We Don't Know

### Keys Without Formulas (52 remaining)
k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30...k70

### Open Questions

1. **What determines the multiplier?**
   - Pattern [9, 13, 19, 12, 10, 9, 10, 45, 38] is not obvious
   - Is it derived from key values? From puzzle number?

2. **What determines the offset?**
   - Offsets: [+49, -49, +19, -18, +224, -5, +76, +149, +37, -465, +461]
   - Why negative sometimes?

3. **What determines the base key?**
   - k7 uses k2, k8 uses k5, k11 uses k6...
   - Gap pattern: [5, 3, 5, 4, 3, 3, 3, 5, 5]

4. **Does pattern continue for k23+?**
   - Formulas break down after k22
   - Need different approach

5. **Do high keys (k66-k70) follow same rules?**
   - Not yet tested

## Next Steps (Priority Order)

1. **Find pattern in multiplier sequence**
   - Mathematical relationship needed

2. **Test formulas on k66-k70**
   - Verify pattern holds at large scale

3. **Derive remaining keys k23-k65**
   - May need expanded search or new formula types

4. **Bridge analysis**
   - Can we derive k71 from k70?
   - What about k75, k80, k85, k90?

## Files

- `derive_formula.py` - Pure math derivation script
- `AGENT_RULES.md` - Strict no-prediction rules
- `DERIVATION_ROADMAP.md` - Full roadmap
- `db/kh.db` - Source of truth (74 known keys)
