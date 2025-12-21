# Offset Formula Verification Report

**Date**: 2025-12-21
**Task**: TASK 2 - Verify and extend Mistral's offset formula
**Data Source**: `/home/rkh/ladder/db/kh.db` (74 known k values)

---

## Executive Summary

Mistral's proposed offset formula has been **REJECTED** based on empirical verification:

```
PROPOSED: offset[n] = (-1)^(n+1) × 2^f(n) × 5^g(n) × h(n)
where f(n) = floor(n/3) - 2, h(n) ∈ {17, 19} based on n mod 6
```

**Verification Results**:
- **f(n) = floor(n/3) - 2**: 1/61 matches (1.6%) - **FAILED**
- **Sign pattern (-1)^(n+1)**: 32/61 matches (52.5%) - **FAILED**
- **Prime 17 hypothesis**: 3 appearances, all match hypothesis (but only 4.9% coverage)
- **Prime 19 hypothesis**: 5 appearances, 0/5 match hypothesis (0% accuracy) - **FAILED**

**Conclusion**: The offset structure is far more complex than Mistral's simple formula suggests. NO consistent power-of-2 pattern exists, and the prime selection hypothesis is incorrect.

---

## Methodology

### Data Extraction
- Queried SQLite database `/home/rkh/ladder/db/kh.db`
- Extracted 74 known k values (puzzles 1-70, 75, 80, 85, 90)
- Computed offsets for n=10 to n=70 (61 total offsets)

### Offset Computation
```
offset[n] = k[n] - 9 × k[n-3]
```

All 61 offsets were computed and completely factorized using prime factorization.

---

## Complete Offset Data (n=10 to n=70)

| n | offset | Complete Factorization |
|---|--------|------------------------|
| 10 | -170 | -2 × 5 × 17 |
| 11 | -861 | -3 × 7 × 41 |
| 12 | -1520 | -2^4 × 5 × 19 |
| 13 | 590 | 2 × 5 × 59 |
| 14 | 149 | 149 |
| 15 | 2720 | 2^5 × 5 × 17 |
| 16 | 4566 | 2 × 3 × 761 |
| 17 | 927 | 3^2 × 103 |
| 18 | -43134 | -2 × 3 × 7 × 13 × 79 |
| 19 | -106055 | -5 × 21211 |
| 20 | 910 | 2 × 5 × 7 × 13 |
| 21 | 23743 | 23743 |
| 22 | -210312 | -2^3 × 3^2 × 23 × 127 |
| 23 | -2171051 | -61 × 35591 |
| 24 | -1877200 | -2^4 × 5^2 × 13 × 19^2 |
| 25 | 6117982 | 2 × 13 × 235307 |
| 26 | 4149644 | 2^2 × 1037411 |
| 27 | -17908143 | -3 × 11 × 127 × 4273 |
| 28 | -71035173 | -3^2 × 11 × 717527 |
| 29 | -90140864 | -2^6 × 11 × 19 × 23 × 293 |
| 30 | 25612615 | 5 × 7 × 467 × 1567 |
| 31 | 53678879 | 4729 × 11351 |
| 32 | -512907232 | -2^5 × 16028351 |
| 33 | -2161020844 | -2^2 × 23 × 2069 × 11353 |
| 34 | -4788424802 | -2 × 7 × 19 × 18001597 |
| 35 | -7728383534 | -2 × 193 × 1429 × 14011 |
| 36 | -21849171228 | -2^2 × 3^3 × 101 × 103 × 19447 |
| 37 | -26946088818 | -2 × 3 × 11 × 12241 × 33353 |
| 38 | -34044309536 | -2^5 × 1979 × 537587 |
| 39 | -57764960883 | -3^2 × 7 × 37 × 239 × 103687 |
| 40 | 101387367595 | 5 × 31 × 654112049 |
| 41 | 135508375819 | 7727 × 17536997 |
| 42 | -18150167970 | -2 × 3^2 × 5 × 11 × 941 × 19483 |
| 43 | -1623051668725 | -5^2 × 64922066749 |
| 44 | 2280491910748 | 2^2 × 47 × 79 × 97 × 1582967 |
| 45 | -6061907885570 | -2 × 5 × 43 × 2861 × 4927459 |
| 46 | -15279629081813 | -15279629081813 |
| 47 | -18976196699469 | -3^2 × 101141 × 20846801 |
| 48 | 11238806921070 | 2 × 3 × 5 × 66533 × 5630693 |
| 49 | -53559128104983 | -3^2 × 22303 × 266825729 |
| 50 | -465859435859766 | -2 × 3^2 × 13 × 409 × 4867609511 |
| 51 | 337906742849889 | 3 × 14657 × 23879 × 321821 |
| 52 | 534425494307975 | 5^2 × 107 × 503 × 397187339 |
| 53 | 1263419505968248 | 2^3 × 157927438246031 |
| 54 | -8554470391888177 | -81559 × 104886896503 |
| 55 | -7903070264536840 | -2^3 × 5 × 197576756613421 |
| 56 | -16654413450626541 | -3^3 × 616830127800983 |
| 57 | 48475661710376129 | 31 × 89 × 41641 × 421940191 |
| 58 | -70431846450483091 | -7 × 10061692350069013 |
| 59 | 127101703624177016 | 2^3 × 7 × 69259 × 32770806379 |
| 60 | -109170479978122046 | -2 × 11 × 19 × 1018679 × 256384393 |
| 61 | -374002469168423459 | -7 × 13 × 29 × 141721284262381 |
| 62 | -817260915816573657 | -3 × 11 × 13 × 1905037099805533 |
| 63 | -1222142202450997670 | -2 × 5 × 67 × 1894229 × 962973769 |
| 64 | 4967579474010341790 | 2 × 3 × 5 × 7 × 504379 × 46899534581 |
| 65 | -4606975570506195703 | -227 × 20295046566106589 |
| 66 | -34592851995373892186 | -2 × 11317 × 1528357868488729 |
| 67 | -27540062615817873350 | -2 × 5^2 × 232782127 × 2366166421 |
| 68 | -55217129595261785870 | -2 × 5 × 683 × 8084499208676689 |
| 69 | -119841466032741115730 | -2 × 5 × 11483 × 27972671 × 37309361 |
| 70 | -223475518416452616237 | -3 × 7 × 11 × 17 × 827 × 4039793 × 17033521 |

---

## Verification Results

### 2.3. Power of 2: f(n) = floor(n/3) - 2

**Hypothesis**: The power of 2 in offset[n] follows f(n) = floor(n/3) - 2

**Result**: **FAILED** (1/61 matches, 1.6%)

#### Sample Exceptions (first 10):

| n | Actual 2^f | Expected 2^f | Difference |
|---|-----------|--------------|------------|
| 11 | 2^0 | 2^1 | -1 |
| 12 | 2^4 | 2^2 | +2 |
| 13 | 2^1 | 2^2 | -1 |
| 14 | 2^0 | 2^2 | -2 |
| 15 | 2^5 | 2^3 | +2 |
| 16 | 2^1 | 2^3 | -2 |
| 17 | 2^0 | 2^3 | -3 |
| 18 | 2^1 | 2^4 | -3 |
| 19 | 2^0 | 2^4 | -4 |
| 20 | 2^1 | 2^4 | -3 |

**Analysis**:
- Only n=10 matches the hypothesis
- Powers of 2 vary wildly (from 2^0 to 2^6)
- No consistent linear relationship with n
- Many offsets have NO factor of 2 (2^0)

---

### 2.4. Prime Selection Hypothesis

**Hypothesis**:
- Prime 17 appears when n ≡ 0, 3, 4 (mod 6)
- Prime 19 appears when n ≡ 2 (mod 6)

**Results**:

#### Prime 17 Appearances (3 total, 4.9% of offsets):

| n | n mod 6 | Expected 17? | Actual | Result |
|---|---------|--------------|--------|--------|
| 10 | 4 | Yes | Yes | ✓ |
| 15 | 3 | Yes | Yes | ✓ |
| 70 | 4 | Yes | Yes | ✓ |

**Prime 17**: 3/3 matches (100%), but only appears in 4.9% of offsets

#### Prime 19 Appearances (5 total, 8.2% of offsets):

| n | n mod 6 | Expected 19? | Actual | Result |
|---|---------|--------------|--------|--------|
| 12 | 0 | No | Yes | ✗ |
| 24 | 0 | No | Yes | ✗ |
| 29 | 5 | No | Yes | ✗ |
| 34 | 4 | No | Yes | ✗ |
| 60 | 0 | No | Yes | ✗ |

**Prime 19**: 0/5 matches (0%) - **COMPLETELY WRONG**

**Conclusion**:
- Prime 17 hypothesis works when 17 appears, but 17 is extremely rare
- Prime 19 hypothesis is completely incorrect
- Primes 17 and 19 are NOT the dominant primes in offsets
- The n mod 6 selection rule is REJECTED

---

### 2.5. Sign Pattern: (-1)^(n+1)

**Hypothesis**: Offset sign follows (-1)^(n+1) pattern

**Result**: **FAILED** (32/61 matches, 52.5%)

This is essentially a coin flip - no pattern detected.

#### Sign Breakdown by Range:

| Range | Matches | Total | Percentage |
|-------|---------|-------|------------|
| n=10-20 | 6/11 | 11 | 54.5% |
| n=21-30 | 5/10 | 10 | 50.0% |
| n=31-40 | 6/10 | 10 | 60.0% |
| n=41-50 | 5/10 | 10 | 50.0% |
| n=51-60 | 6/10 | 10 | 60.0% |
| n=61-70 | 4/10 | 10 | 40.0% |

**Conclusion**: No systematic sign pattern exists. Sign appears random or follows a different rule.

---

## Prime Distribution Analysis

### Overall Prime Frequency (n=10-70, all 61 offsets):

| Prime | Appearances | Percentage |
|-------|-------------|------------|
| 2 | 34/61 | 55.7% |
| 5 | 20/61 | 32.8% |
| 3 | 20/61 | 32.8% |
| 7 | 11/61 | 18.0% |
| 11 | 8/61 | 13.1% |
| 13 | 7/61 | 11.5% |
| 19 | 5/61 | 8.2% |
| 17 | 3/61 | 4.9% |
| 23 | 3/61 | 4.9% |

**Key Finding**: The most common primes are 2, 5, and 3 - NOT 17 and 19 as Mistral hypothesized.

### Prime Distribution for n ≥ 40 (31 offsets):

| Prime | Appearances | Percentage |
|-------|-------------|------------|
| 2 | 15/31 | 48.4% |
| 5 | 12/31 | 38.7% |
| 3 | 10/31 | 32.3% |
| 7 | 5/31 | 16.1% |
| 11 | 4/31 | 12.9% |
| 13 | 3/31 | 9.7% |
| 17 | 1/31 | 3.2% |
| 19 | 1/31 | 3.2% |

**Observation**: For large n (≥40), primes 17 and 19 become even rarer (only 3.2% each).

---

## Power of 5 Analysis

### Distribution of 5^g(n):

| Power | Count | Percentage |
|-------|-------|------------|
| 5^0 | 41/61 | 67.2% |
| 5^1 | 16/61 | 26.2% |
| 5^2 | 4/61 | 6.6% |

**Cases with 5^2** (n where g(n) = 2):
- n=24: -2^4 × 5^2 × 13 × 19^2
- n=43: -5^2 × 64922066749
- n=52: 5^2 × 107 × 503 × 397187339
- n=67: -2 × 5^2 × 232782127 × 2366166421

**Observation**:
- Most offsets (67.2%) have NO factor of 5
- When 5 appears, it's usually 5^1 (26.2%)
- 5^2 is rare (6.6%, only 4 cases)
- Mistral's assumption that g(n) is "usually 1" is WRONG - it's usually 0!

---

## Patterns NOT Detected

1. **NO consistent power-of-2 formula** - f(n) varies from 0 to 6 with no pattern
2. **NO n mod 6 prime selection rule** - Prime 19 hypothesis completely fails
3. **NO simple sign pattern** - 52.5% match is random noise
4. **NO dominance of primes 17/19** - They appear in only 4.9% and 8.2% of offsets

---

## Patterns DETECTED

### 1. Small Prime Dominance
- Primes 2, 3, 5, 7, 11, 13 are the most common
- These account for the majority of offset factorizations

### 2. Large Prime Factors
Many offsets have large prime factors (>10^6), indicating offset values are NOT constructed from small building blocks.

Examples:
- offset[46] = -15279629081813 (prime itself!)
- offset[54] = -81559 × 104886896503 (large primes)
- offset[58] = -7 × 10061692350069013 (huge prime)

### 3. Highly Composite Offsets
Some offsets are products of many small primes:

- offset[18] = -2 × 3 × 7 × 13 × 79 (5 primes)
- offset[36] = -2^2 × 3^3 × 101 × 103 × 19447 (5 distinct primes)
- offset[64] = 2 × 3 × 5 × 7 × 504379 × 46899534581 (6 distinct primes)

### 4. Prime Offsets
Some offsets are prime themselves:
- offset[14] = 149 (prime)
- offset[21] = 23743 (prime)
- offset[46] = -15279629081813 (prime)

This indicates the offset formula is NOT a simple product of small prime powers.

---

## Corrected Understanding

The offset relationship `k[n] = 9 × k[n-3] + offset[n]` is **verified** for n=10 to n=70.

However, the offset values themselves do NOT follow Mistral's simple formula:

```
❌ WRONG: offset[n] = (-1)^(n+1) × 2^f(n) × 5^g(n) × h(n)
```

### What We Know About Offsets:

1. **They vary wildly in magnitude** (from hundreds to 10^20)
2. **They have diverse prime factorizations** (no pattern detected)
3. **They include prime offsets** (cannot be decomposed)
4. **They do NOT follow n mod 6 rules** for prime selection
5. **Powers of 2 and 5 do NOT follow simple formulas**

### Implications:

The offset sequence is likely:
- Derived from a more complex formula involving k[n-1], k[n-2], adj[n], etc.
- NOT independently generated from n alone
- Possibly emergent from the main recurrence relation k[n] = 2k[n-1] + adj[n]

---

## Recommended Next Steps

1. **Abandon Mistral's formula** - It does not match empirical data

2. **Investigate offset relationships**:
   - Can offset[n] be expressed in terms of adj[n], m[n], d[n]?
   - Are there secondary recurrences for offsets?

3. **Look for offset patterns by n mod 3**:
   - Since the base recurrence is mod-3, check if offsets split by n mod 3

4. **Analyze offset ratios**:
   - offset[n]/offset[n-3]
   - offset[n]/k[n-3]

5. **Cross-reference with adj[n] sequence**:
   - Offsets may be related to the adjustment sequence

---

## Data Artifacts

### Files Generated:
- `/home/rkh/ladder/verify_offset_formula.py` - Verification script
- `/home/rkh/ladder/offset_verification_results.json` - JSON results
- `/home/rkh/ladder/offset_formula_verified.md` - This report

### Database Queries:
All data extracted from `/home/rkh/ladder/db/kh.db` table `keys`.

---

## Conclusion

**Mistral's offset formula is REJECTED based on empirical evidence.**

- f(n) hypothesis: 1.6% match
- Sign pattern hypothesis: 52.5% match (random)
- Prime 17 hypothesis: 100% when it appears, but only 4.9% coverage
- Prime 19 hypothesis: 0% accuracy

The offset sequence is far more complex than a simple product of prime powers. Further investigation is needed to understand the true structure of offset[n].

**NO ASSUMPTIONS MADE. ALL CONCLUSIONS DERIVED FROM DATABASE.**

---

*Report Generated: 2025-12-21*
*Script: verify_offset_formula.py*
*Database: /home/rkh/ladder/db/kh.db (74 known keys)*
