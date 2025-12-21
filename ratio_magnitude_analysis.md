# Combined Ratio and Magnitude Growth Analysis

**Analysis Date:** 2025-12-21

**Project:** Bitcoin Puzzle Analysis - k-value sequence analysis

---

## Task 10: Ratio Analysis (k[n]/k[n-1])

### 10.1 Ratio Values (n=2 to n=70)

Computed r[n] = k[n]/k[n-1] for all consecutive pairs.

**Total ratios computed:** 69

#### Sample Ratios (n=2 to n=21)

| n | k[n] | k[n-1] | r[n] = k[n]/k[n-1] |
|---|------|--------|--------------------|
| 2 | 3 | 1 | 3.000000 |
| 3 | 7 | 3 | 2.333333 |
| 4 | 8 | 7 | 1.142857 |
| 5 | 21 | 8 | 2.625000 |
| 6 | 49 | 21 | 2.333333 |
| 7 | 76 | 49 | 1.551020 |
| 8 | 224 | 76 | 2.947368 |
| 9 | 467 | 224 | 2.084821 |
| 10 | 514 | 467 | 1.100642 |
| 11 | 1155 | 514 | 2.247082 |
| 12 | 2683 | 1155 | 2.322944 |
| 13 | 5216 | 2683 | 1.944092 |
| 14 | 10544 | 5216 | 2.021472 |
| 15 | 26867 | 10544 | 2.548084 |
| 16 | 51510 | 26867 | 1.917222 |
| 17 | 95823 | 51510 | 1.860280 |
| 18 | 198669 | 95823 | 2.073291 |
| 19 | 357535 | 198669 | 1.799652 |
| 20 | 863317 | 357535 | 2.414636 |
| 21 | 1811764 | 863317 | 2.098608 |

### 10.2 Continued Fraction Representations

Continued fraction expansion of k[n]/k[n-1] for n=2 to n=21:

**n=2:** [3]
  - Convergents: 3/1

**n=3:** [2, 3]
  - Convergents: 2/1, 7/3

**n=4:** [1, 7]
  - Convergents: 1/1, 8/7

**n=5:** [2, 1, 1, 1, 2]
  - Convergents: 2/1, 3/1, 5/2, 8/3, 21/8

**n=6:** [2, 3]
  - Convergents: 2/1, 7/3

**n=7:** [1, 1, 1, 4, 2, 2]
  - Convergents: 1/1, 2/1, 3/2, 14/9, 31/20

**n=8:** [2, 1, 18]
  - Convergents: 2/1, 3/1, 56/19

**n=9:** [2, 11, 1, 3, 1, 3]
  - Convergents: 2/1, 23/11, 25/12, 98/47, 123/59

**n=10:** [1, 9, 1, 14, 1, 2]
  - Convergents: 1/1, 10/9, 11/10, 164/149, 175/159

**n=11:** [2, 4, 21, 6]
  - Convergents: 2/1, 9/4, 191/85, 1155/514

**n=12:** [2, 3, 10, 2, 1, 3, 3]
  - Convergents: 2/1, 7/3, 72/31, 151/65, 223/96

**n=13:** [1, 1, 16, 1, 7, 1, 4, 1, 2]
  - Convergents: 1/1, 2/1, 33/17, 35/18, 278/143

**n=14:** [2, 46, 1, 1, 3]
  - Convergents: 2/1, 93/46, 95/47, 188/93, 659/326

**n=15:** [2, 1, 1, 4, 1, 2, 3, 12, 2, 1, 2]
  - Convergents: 2/1, 3/1, 5/2, 23/9, 28/11

**n=16:** [1, 1, 11, 12, 2, 2, 1, 4, 2, 2]
  - Convergents: 1/1, 2/1, 23/12, 278/145, 579/302

**n=17:** [1, 1, 6, 6, 2, 1, 3, 34]
  - Convergents: 1/1, 2/1, 13/7, 80/43, 173/93

**n=18:** [2, 13, 1, 1, 1, 4, 3, 1, 2, 14]
  - Convergents: 2/1, 27/13, 29/14, 56/27, 85/41

**n=19:** [1, 1, 3, 1, 114, 26, 1, 1, 1, 1, 2]
  - Convergents: 1/1, 2/1, 7/4, 9/5, 1033/574

**n=20:** [2, 2, 2, 2, 3, 272, 4, 1, 1, 3]
  - Convergents: 2/1, 5/2, 12/5, 29/12, 99/41

**n=21:** [2, 10, 7, 11, 1, 7, 1, 3, 1, 3, 1, 4]
  - Convergents: 2/1, 21/10, 149/71, 1660/791, 1809/862

### 10.3 Convergence Analysis: Do Ratios Approach 2?

#### Overall Statistics

- **Mean ratio:** 2.083809
- **Standard deviation:** 0.541590
- **Median ratio:** 2.052664
- **Min ratio:** 1.100642
- **Max ratio:** 3.368734
- **Deviation from 2.0:** 0.083809

#### Windowed Analysis (10-value windows)

| Window | Mean Ratio | Deviation from 2.0 | StDev |
|--------|------------|-------------------|-------|
| n_12_to_21 | 2.100028 | 0.100028 | 0.249834 |
| n_22_to_31 | 2.050170 | 0.050170 | 0.342664 |
| n_2_to_11 | 2.136546 | 0.136546 | 0.678009 |
| n_32_to_41 | 1.987644 | 0.012356 | 0.546352 |
| n_42_to_51 | 2.142040 | 0.142040 | 0.610496 |
| n_52_to_61 | 2.022728 | 0.022728 | 0.689566 |

**Interpretation:** Ratios are very close to 2.0 on average, suggesting near-exponential doubling.

### 10.4 Correlation with 2^n Growth

#### Linear Regression: log2(k[n]) vs n

**Formula:** log2(k[n]) ≈ 1.0025*n + -0.5212

- **Slope:** 1.002479
- **Intercept:** -0.521234
- **Theoretical slope (if k[n] = 2^n):** 1.000000
- **Deviation from theoretical:** 0.002479

**Interpretation:** Slope is very close to 1.0, confirming k[n] grows approximately as 2^n.

#### Sample log2(k[n]) Deviations from n (n=1 to n=20)

| n | log2(k[n]) | Theoretical (n) | Deviation |
|---|------------|-----------------|----------|
| 1 | 0.0000 | 1 | -1.0000 |
| 2 | 1.5850 | 2 | -0.4150 |
| 3 | 2.8074 | 3 | -0.1926 |
| 4 | 3.0000 | 4 | -1.0000 |
| 5 | 4.3923 | 5 | -0.6077 |
| 6 | 5.6147 | 6 | -0.3853 |
| 7 | 6.2479 | 7 | -0.7521 |
| 8 | 7.8074 | 8 | -0.1926 |
| 9 | 8.8673 | 9 | -0.1327 |
| 10 | 9.0056 | 10 | -0.9944 |
| 11 | 10.1737 | 11 | -0.8263 |
| 12 | 11.3896 | 12 | -0.6104 |
| 13 | 12.3487 | 13 | -0.6513 |
| 14 | 13.3641 | 14 | -0.6359 |
| 15 | 14.7135 | 15 | -0.2865 |
| 16 | 15.6526 | 16 | -0.3474 |
| 17 | 16.5481 | 17 | -0.4519 |
| 18 | 17.6000 | 18 | -0.4000 |
| 19 | 18.4477 | 19 | -0.5523 |
| 20 | 19.7195 | 20 | -0.2805 |

---

## Task 12: Magnitude Growth Analysis (adj[n])

### 12.1 Magnitude Data: log2(|adj[n]|) for n=4 to n=70

**Total data points:** 28

#### Sample Data (n=4 to n=23)

| n | adj[n] | |adj[n]| | log2(|adj[n]|) | Sign |
|---|--------|----------|----------------|------|
| 4 | -6 | 6 | 2.5850 | - |
| 5 | 5 | 5 | 2.3219 | + |
| 6 | 7 | 7 | 2.8074 | + |
| 7 | -22 | 22 | 4.4594 | - |
| 8 | 72 | 72 | 6.1699 | + |
| 9 | 19 | 19 | 4.2479 | + |
| 10 | -420 | 420 | 8.7142 | - |
| 11 | 127 | 127 | 6.9887 | + |
| 12 | 373 | 373 | 8.5430 | + |
| 13 | -150 | 150 | 7.2288 | - |
| 14 | 112 | 112 | 6.8074 | + |
| 15 | 5779 | 5779 | 12.4966 | + |
| 16 | -2224 | 2224 | 11.1189 | - |
| 17 | -7197 | 7197 | 12.8132 | - |
| 18 | 7023 | 7023 | 12.7779 | + |
| 19 | -39803 | 39803 | 15.2806 | - |
| 20 | 148247 | 148247 | 17.1776 | + |
| 21 | 85130 | 85130 | 16.3774 | + |
| 22 | -616025 | 616025 | 19.2326 | - |
| 23 | -416204 | 416204 | 18.6669 | - |

### 12.2 Linear Regression: log2(|adj[n]|) vs n

**Formula:** log2(|adj[n]|) ≈ 0.9486*n + -2.8196

- **Slope:** 0.948587
- **Intercept:** -2.819557
- **R² (goodness of fit):** 0.965462
- **Theoretical slope (if adj grows as O(2^n)):** 1.000000
- **Deviation from theoretical:** 0.051413

### 12.3 Comparison with Theoretical O(2^n) Growth

**Result:** Slope of 0.9486 is very close to 1.0, confirming |adj[n]| grows approximately as O(2^n).

**Fit Quality:** R² = 0.965462 indicates excellent exponential fit.

### 12.4 Deviation Patterns from Exponential Growth

- **Mean absolute deviation:** 1.2222
- **Max absolute deviation:** 3.6533

#### Significant Deviations (|deviation| > 0.5)

- **Values above expected:** 12
  - Puzzle IDs: [4, 7, 8, 10, 15, 20, 22, 24, 25, 26, 29, 30]

- **Values below expected:** 10
  - Puzzle IDs: [9, 11, 13, 14, 16, 18, 21, 27, 28, 31]

**Note:** Values with |deviation| > 0.5 indicate significant departure from exponential growth

#### Top 10 Largest Deviations

| Rank | n | Deviation | Direction |
|------|---|-----------|----------|
| 1 | 14 | -3.6533 | Below |
| 2 | 13 | -2.2833 | Below |
| 3 | 30 | +2.1499 | Above |
| 4 | 10 | +2.0479 | Above |
| 5 | 28 | -1.9084 | Below |
| 6 | 24 | +1.6770 | Above |
| 7 | 26 | +1.6525 | Above |
| 8 | 4 | +1.6102 | Above |
| 9 | 31 | -1.4826 | Below |
| 10 | 18 | -1.4771 | Below |

---

## Combined Insights

### Key Findings

1. **k-value growth rate:**
   - Average ratio k[n]/k[n-1] = 2.0838
   - Linear regression slope (log2 scale) = 1.0025
   - Interpretation: k-values grow at approximately 2^1.0025 per step

2. **adj-value magnitude growth:**
   - Linear regression slope (log2 scale) = 0.9486
   - Interpretation: |adj[n]| grows at approximately 2^0.9486 per step

3. **Relationship between k and adj growth:**
   - Growth rate ratio: k-slope / adj-slope = 1.0568
   - **Both grow at similar exponential rates**, suggesting adj is a significant component of k-value jumps.

### Formula Context

Recall the fundamental formula:

```
k[n] = 2*k[n-1] + adj[n]
adj[n] = 2^n - m[n] * k[d[n]]
```

This analysis shows:
- The 2*k[n-1] term dominates (exponential with base ~2^1.002)
- The adj[n] term provides adjustments (exponential with base ~2^0.949)
- Deviations in adj growth reveal where m[n] selection creates unusual corrections

---

**Analysis complete.** All numerical results have been computed from database values.
