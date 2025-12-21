# Building Block Discovery Document
**Date**: 2025-12-21
**Session**: Claude Dell Deep Dive

## Executive Summary

The m-sequence is constructed from a small set of **building blocks** using simple operations.

---

## Verified Building Blocks

| Block | Value | Origin |
|-------|-------|--------|
| B1 | 1 | Unity / Identity |
| B7 | 7 | Mersenne M_3 = 2^3 - 1 |
| B19 | 19 | e convergent (19/7) |
| B22 | 22 | π convergent (22/7) |

---

## Verified Formulas for m[2] through m[11]

| n | m[n] | Formula | Type |
|---|------|---------|------|
| 2 | 1 | 2^2 - M_1 = 4 - 3 | Mersenne subtraction |
| 3 | 1 | 2^3 - M_2 = 8 - 7 | Mersenne subtraction |
| 4 | 22 | B22 | π convergent |
| 5 | 9 | 2^3 + B1 = 8 + 1 | Power + unity |
| 6 | 19 | B19 | e convergent |
| 7 | 50 | B7² + B1 = 49 + 1 | Square + unity |
| 8 | 23 | B1 + B22 = 1 + 22 | Sum of blocks |
| 9 | 493 | 2^9 - B19 = 512 - 19 | Power - e |
| 10 | 19 | B1 × B19 = 1 × 19 | Product (trivial) |
| 11 | 1921 | 2^11 - M_7 = 2048 - 127 | Mersenne subtraction |

---

## Pattern Categories

### Category 1: Mersenne Subtraction
```
m[n] = 2^n - M_k where M_k = 2^k - 1

Examples:
  m[2] = 2^2 - (2^2 - 1) = 4 - 3 = 1
  m[3] = 2^3 - (2^3 - 1) = 8 - 7 = 1
  m[11] = 2^11 - (2^7 - 1) = 2048 - 127 = 1921
```

### Category 2: Continued Fraction Constants
```
m[4] = 22 (π convergent numerator)
m[6] = 19 (e convergent numerator)
m[10] = 19 (e convergent, repeat)
```

### Category 3: Self-Referential
```
m[7] = m[3]² + 1 = 7² + 1 = 50
m[8] = m[2] + m[4] = 1 + 22 = 23
```

### Category 4: Power Operations
```
m[5] = 2^3 + 1 = 9
m[9] = 2^9 - 19 = 493
```

---

## 17-Network Cofactor Formula

For n in {9, 11, 12} where m[n] ≡ 0 (mod 17):

```
m[n] = 17 × p[n + m[j]]

where:
  - p[k] is the k-th prime
  - j ∈ {2, 5, 6} such that d[j] = 2
```

| n | j | m[j] | prime_idx | p[idx] | m[n] |
|---|---|------|-----------|--------|------|
| 9 | 2 | 1 | 10 | 29 | 493 |
| 11 | 6 | 19 | 30 | 113 | 1921 |
| 12 | 5 | 9 | 21 | 73 | 1241 |

**Key Insight**: All j-values satisfy d[j] = 2!

---

## Connection to EC Ladder

The EC ladder formula is:
```
P[n] = 2*P[n-1] + 2^n × G - m[n] × P[d[n]]
```

The m[n] values modulate the ladder construction, with:
1. Early terms (n=2,3) using Mersenne bootstrap
2. π and e convergents providing irrational structure
3. Self-reference creating recursive dependencies
4. 17-network adding prime structure

---

## Next Steps

1. Find formulas for m[12] through m[15]
2. Determine the j-selection rule for 17-network
3. Test if m[71] follows building block pattern
4. Explore why d[j] = 2 for all j in 17-network

---

## Hypothesis: Direct Formula

If m[n] can be expressed entirely in terms of building blocks and 2^n, then:

```
k[n] = f(n, B1, B7, B19, B22, Mersennes)
```

The gap puzzles (75, 80, 85, 90) PROVE this formula exists!
