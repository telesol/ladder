# Bitcoin Puzzle Key Generation Formula

**Date**: 2025-12-16
**Status**: DERIVED FROM DATABASE (74 known keys)

## The Master Recurrence

```
k_n = 2 × k_{n-1} + adj_n
```

Where `adj_n` (the adjustment term) can be expressed as:

```
adj_n = a × 2^c + b × k_i
```

For specific integer coefficients `a`, `b`, `c`, and key index `i < n`.

## Foundation Keys

```
k1 = 1   (seed)
k2 = 3   (seed)
k3 = 7   (seed)
```

These appear to be Lucas numbers: k1 = L(1), k2 = L(2), k3 = L(4).

## Verified Adjustment Formulas

| n | adj_n | Formula | Alternative |
|---|-------|---------|-------------|
| 2 | +1 | 1×k1 | - |
| 3 | +1 | 1×k1 | -8×2² + 11×k2 |
| 4 | -6 | -2×k2 | -6×2³ + 14×k2 |
| 5 | +5 | 5×k1 = n×k1 | -8×2⁴ + 19×k3 |
| 6 | +7 | 1×k3 | -7×2⁵ + 11×k5 |
| 7 | -22 | -1×k1 - 1×k5 | -8×2⁶ + 10×k6 |
| 8 | +72 | 9×k4 | -3×2⁷ + 6×k7 |
| 9 | +19 | 19×k1 | -1×2⁷ + 7×k5 |
| 10 | -420 | -20×k5 = -2n×k5 | 2×2⁹ - 19×k7 |
| 11 | +127 | 2⁷ - 1 | 1×2⁷ - 1×k1 |
| 12 | +373 | - | 1×2⁷ + 5×k6 |
| 13 | -150 | -50×k2 | - |
| 14 | +112 | 14×k4 = n×k4 | 1×2¹⁰ - 12×k7 |

## Key Observations

### 1. Multiplier = n Pattern
For some n: `adj_n = n × k_i`
- adj_5 = 5×k1 (n=5)
- adj_14 = 14×k4 (n=14)

### 2. Multiplier = -2n Pattern
For some n: `adj_n = -2n × k_i`
- adj_10 = -20×k5 = -2×10×k5

### 3. Powers of 2 + Key Multiples
Every adjustment can be expressed as:
```
adj_n = a × 2^c + b × k_i
```

### 4. Special Numbers
- adj_11 = 127 = 2⁷ - 1 (Mersenne prime)
- adj_12 = 373 (prime)

### 5. Sign Pattern
```
adj sequence: + + - + + - + + - + + - + + - - + -
```
Roughly ++- repeating with deviations at n=15,16,17.

## Lucas Number Connection

Early keys ARE Lucas numbers:
- k1 = 1 = L(1)
- k2 = 3 = L(2)
- k3 = 7 = L(4)
- k7 = 76 = L(9)

## Position Anomalies

Keys near minimum (frac ≈ 0):
- k1, k4: exactly at 2^(n-1) (0%)
- k10: 0.39% into range
- k69: 0.72% into range

## Full Recurrence Verification

```
k2  = 2×1 + 1 = 3
k3  = 2×3 + 1 = 7
k4  = 2×7 - 6 = 8
k5  = 2×8 + 5 = 21
k6  = 2×21 + 7 = 49
k7  = 2×49 - 22 = 76
k8  = 2×76 + 72 = 224
k9  = 2×224 + 19 = 467
k10 = 2×467 - 420 = 514
k11 = 2×514 + 127 = 1155
k12 = 2×1155 + 373 = 2683
k13 = 2×2683 - 150 = 5216
k14 = 2×5216 + 112 = 10544
```

ALL VERIFIED against database.

## Unknown: Coefficient Selection Rule

The remaining mystery is: **How are a, b, c, i determined for each n?**

Possibilities:
1. PRNG with specific seed
2. Deterministic but complex function of n
3. Lookup table created by puzzle designer

## Next Steps

1. Find the coefficient selection rule
2. Apply formula to derive k71-k160
3. Verify against k75, k80, k85, k90 (bridge keys)

## Data Source

All values verified against `db/kh.db`:
```sql
SELECT puzzle_id, priv_hex FROM keys;
```

74 known keys: k1-k70, k75, k80, k85, k90
