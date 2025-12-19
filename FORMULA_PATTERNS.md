# M-Sequence Formula Patterns

**Date**: 2025-12-19
**Status**: Active Research

---

## Overview

The m-sequence values are constructed using a combination of:
1. **Mathematical constant convergents** (π, e, √2, √3, φ, ln(2))
2. **Prime numbers** (especially p[7]=17 from √2)
3. **Self-referential recursion** (m[n] builds on earlier m-values)
4. **The d-sequence** (determines which earlier value to reference)

---

## Construction Methods

### Type 1: Direct Convergent Values
m[n] equals a numerator or denominator from a continued fraction.

| n | m[n] | Formula |
|---|------|---------|
| 4 | 22 | π numerator[1] from 22/7 |
| 5 | 9 | ln(2) numerator[4] from 9/13 |
| 6 | 19 | e numerator[4] from 19/7 |
| 10 | 19 | Same as m[6] |

### Type 2: Convergent Products (Same Index)
m[n] = const_A_conv[i] × const_B_conv[i]

| n | m[n] | Formula |
|---|------|---------|
| 7 | 50 | φ_num[3] × ln2_den[3] = 5 × 10 |
| 11 | 1921 | √2_num[3] × π_den[3] = 17 × 113 |

### Type 3: Convergent Sums
m[n] = conv_A + conv_B

| n | m[n] | Formula |
|---|------|---------|
| 8 | 23 | π_den[0] + π_num[1] = 1 + 22 |
| 14 | 2034 | √2_num[7] + e_num[9] = 577 + 1457 |

### Type 4: Convergent Differences
m[n] = conv_A - conv_B

| n | m[n] | Formula |
|---|------|---------|
| 12 | 1241 | ln2_den[9] - √2_den[7] = 1649 - 408 |

### Type 5: Prime-Index Formula (17-Network)
m[n] = 17 × p[n + m[earlier]]

| n | m[n] | Formula | Verification |
|---|------|---------|--------------|
| 9 | 493 | 17 × p[9 + m[2]] = 17 × p[10] | 17 × 29 = 493 ✓ |
| 11 | 1921 | 17 × p[11 + m[6]] = 17 × p[30] | 17 × 113 = 1921 ✓ |
| 12 | 1241 | 17 × p[12 + m[5]] = 17 × p[21] | 17 × 73 = 1241 ✓ |

**Key**: 17 = √2 convergent numerator at index 3

### Type 6: Recursive Convergent Multiplier ★★★★★
m[n] = m[earlier] × (product of convergents)

| n | m[n] | Formula |
|---|------|---------|
| 14 | 2034 | m[5] × e_num[0] × π_den[3] = 9 × 2 × 113 |
| 16 | 8470 | m[4] × √2_den[2] × π_den[1] × e_num[3] = 22 × 5 × 7 × 11 |

### Type 7: Divisibility Chains
m[n] = m[earlier] × k for some integer k

**m[4] = 22 divides**: m[16], m[38], m[50], m[55], m[61]
**m[6] = 19 divides**: m[10], m[19], m[25], m[57], m[58], m[69]

---

## D-Sequence Patterns

### Power-of-2 Correlation
| d value | Positions | Correlation |
|---------|-----------|-------------|
| d=4 | 8, 14, 16, 24, 30 | Near 2³, 2⁴, 2⁵ |
| d=8 | 32, 60, 66 | Near 2⁵, 2⁶ |

### D-Sequence Distribution (Full Range)
| d | Count | % |
|---|-------|---|
| 1 | 30 | 43.5% |
| 2 | 20 | 29.0% |
| 4 | 5 | 7.2% |
| 3 | 4 | 5.8% |
| 5 | 5 | 7.2% |

---

## 17-Network (Complete)

The prime 17 appears in m[n] at: **n = 9, 11, 12, 24, 48, 67**

| n | m[n] | Factorization | Pattern |
|---|------|---------------|---------|
| 9 | 493 | 17 × 29 | 17 × p[10] |
| 11 | 1921 | 17 × 113 | 17 × p[30] |
| 12 | 1241 | 17 × 73 | 17 × p[21] |
| 24 | 1693268 | 4 × 17 × 37 × 673 | Complex |
| 48 | 329601320238553 | 11 × 17 × ... | Complex |
| 67 | 35869814695994276026 | 2 × 17 × ... | Complex |

---

## Key Constants

| Constant | First Few Convergents | Used For |
|----------|----------------------|----------|
| π | 3/1, 22/7, 333/106, 355/113, ... | m[4], m[8], m[11] |
| e | 2/1, 3/1, 8/3, 11/4, 19/7, ... | m[6], m[14], m[16] |
| √2 | 1/1, 3/2, 7/5, 17/12, 41/29, ... | m[9], m[11], m[12] |
| φ | 1/1, 2/1, 3/2, 5/3, 8/5, ... | m[7] |
| ln(2) | 1/1, 1/1, 2/3, 9/13, 11/16, ... | m[5], m[7], m[12] |

---

## Unified Formula Hypothesis

```
m[n] = f(n, d[n], m[1..n-1], CONVERGENTS)

where:
- CONVERGENTS = {π, e, √2, √3, φ, ln(2)} continued fractions
- f selects: DIRECT, PRODUCT, SUM, DIFF, PRIME-IDX, or RECURSIVE
- Selection rule based on: n mod 8, d[n], position relative to 2^k
```

---

## What We Need

1. **Index Selection Rule**: For Type 2/3/4, which convergent index to use?
2. **Constant Selection Rule**: Which constant(s) for each n?
3. **Operation Selection Rule**: Which operation type for each n?
4. **D-Sequence Generation**: How is d[n] computed from n?

---

## Files

- `experiments/06-pysr-m-sequence/` - Analysis scripts
- `FINDINGS_RKH_CLAUDE.md` - Detailed findings
- `data_for_csolver.json` - Source data (m_seq, d_seq)
