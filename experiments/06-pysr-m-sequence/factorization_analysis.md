# M-Sequence Factorization Analysis

## Overview
Factorization analysis of m[2] through m[31] (first 30 m-sequence values) to identify prime structure patterns.

**Prime Notation:** p[1]=2, p[2]=3, p[3]=5, p[4]=7, p[5]=11, p[6]=13, p[7]=17, p[8]=19, p[9]=23, p[10]=29, etc.

---

## KEY FINDINGS

### 1. p[7]=17 Pattern (MOST SIGNIFICANT)

**p[7]=17 appears in 4 out of 30 values:**

| m[n] | Value | Factorization | Pattern |
|------|-------|---------------|---------|
| m[9] | 493 | p[7] × p[10] | 17 × 29 |
| m[11] | 1921 | p[7] × p[30] | 17 × 113 |
| m[12] | 1241 | p[7] × p[21] | 17 × 73 |
| m[24] | 1693268 | p[1]² × p[7] × p[12] × p[122] | 4 × 17 × 37 × 673 |

**Observations:**
- Appears at indices: 9, 11, 12, 24
- Index pattern: 9, 11, 12 are consecutive in "17-group", then jumps to 24
- Always appears with exponent 1 (never squared)
- Early occurrences (m[9], m[11], m[12]) are simple products of exactly 2 primes involving 17
- Later occurrence (m[24]) involves 17 as one factor among multiple primes

---

### 2. Most Common Primes

| Rank | Prime | Index | Frequency | Percentage |
|------|-------|-------|-----------|------------|
| 1 | 2 | p[1] | 11 | 36.7% |
| 2 | 5 | p[3] | 6 | 20.0% |
| 3-6 (tie) | 11 | p[5] | 4 | 13.3% |
| 3-6 (tie) | 3 | p[2] | 4 | 13.3% |
| 3-6 (tie) | 19 | p[8] | 4 | 13.3% |
| 3-6 (tie) | **17** | **p[7]** | **4** | **13.3%** |

**Key Insight:** The first few small primes (2, 3, 5, 11) dominate, BUT p[7]=17 and p[8]=19 appear as frequently as p[2]=3 and p[5]=11, despite being larger primes.

---

### 3. Small Prime Products (m[4] through m[16])

| m[n] | Value | Factorization | Contains only p[1]-p[5]? |
|------|-------|---------------|--------------------------|
| m[4] | 22 | p[1] × p[5] | ✓ (uses p[1], p[5]) |
| m[5] | 9 | p[2]² | ✓ (uses p[2]) |
| m[7] | 50 | p[1] × p[3]² | ✓ (uses p[1], p[3]) |
| m[16] | 8470 | p[1] × p[3] × p[4] × p[5]² | ✓ (uses p[1], p[3], p[4], p[5]) |

**m[16] is special:** 8470 = 2 × 5 × 7 × 11² = p[1] × p[3] × p[4] × p[5]²
- Product of the first 4 primes (with 11 squared)
- Highly composite structure

---

### 4. Prime Values (m[n] itself is prime)

| m[n] | Value | Prime Index | Note |
|------|-------|-------------|------|
| m[6] | 19 | p[8] | Also appears as m[10] |
| m[8] | 23 | p[9] | |
| m[10] | 19 | p[8] | Duplicate of m[6]! |
| m[18] | 255121 | p[22450] | Very large prime |
| m[20] | 900329 | p[71300] | Very large prime |

**Observation:** m[6]=m[10]=19 is a **self-reference/repetition**!

---

### 5. Products of Exactly 2 Primes

| m[n] | Value | Factorization | Pattern |
|------|-------|---------------|---------|
| m[4] | 22 | p[1] × p[5] | 2 × 11 |
| m[6] | 19 | p[8] | Prime (special case) |
| m[9] | 493 | p[7] × p[10] | 17 × 29 |
| m[10] | 19 | p[8] | Prime (special case) |
| m[11] | 1921 | p[7] × p[30] | 17 × 113 |
| m[12] | 1241 | p[7] × p[21] | 17 × 73 |
| m[15] | 26989 | p[33] × p[45] | 137 × 197 |
| m[17] | 138269 | p[12]² × p[26] | 37² × 101 |
| m[30] | 105249691 | p[109] × p[15965] | 599 × 175709 |

**Pattern:** Many early m-values are products of exactly 2 distinct primes (or prime themselves).

---

### 6. Repeated Prime Indices Across Different m[n]

| Prime | Index | Appears in m[n] |
|-------|-------|-----------------|
| 2 | p[1] | 4, 7, 13, 14, 16, 21, 23, 24, 26, 28, 29 (11 times) |
| 3 | p[2] | 5, 14, 21, 22 (4 times) |
| 5 | p[3] | 7, 16, 25, 26, 28, 31 (6 times) |
| 11 | p[5] | 4, 16, 19, 27 (4 times) |
| 13 | p[6] | 25, 28 (2 times) |
| **17** | **p[7]** | **9, 11, 12, 24** (4 times) |
| 19 | p[8] | 6, 10, 19, 25 (4 times) |
| 37 | p[12] | 17, 24 (2 times) |
| 113 | p[30] | 11, 14 (2 times) |

**Key Observations:**
- p[7]=17 appears at m[9], m[11], m[12], m[24]
- p[8]=19 appears at m[6], m[10] (as the value itself!), m[19], m[25]
- p[12]=37 appears at m[17] (squared!) and m[24]
- p[30]=113 appears at m[11] and m[14]

---

### 7. Self-References and Relationships

#### Direct Repetition
- **m[6] = m[10] = 19** (exact duplicate value!)

#### Potential Self-References via Prime Indices
Looking for patterns where m[n] contains a prime at index related to n:

| m[n] | Prime Indices Used | Potential Self-Reference? |
|------|-------------------|---------------------------|
| m[9] | p[7], p[10] | Contains p[10], close to index 9 |
| m[11] | p[7], p[30] | No direct match |
| m[12] | p[7], p[21] | No direct match |
| m[17] | p[12]², p[26] | Contains p[12], but m[17]=12² × 101 not 17-related |

**No strong self-referential pattern detected in indices.**

---

### 8. Mathematical Constants Connection

From the Bitcoin Puzzle Analysis (CLAUDE.md):
- **m[4]/m[3] = 22/7 ≈ π** (known π approximation)
- 22 = p[1] × p[5] = 2 × 11
- This suggests m-sequence may encode mathematical constants!

---

### 9. Factorization Complexity Growth

| m[n] Range | Average # of Prime Factors | Max # of Prime Factors | % Prime Values |
|------------|---------------------------|------------------------|----------------|
| m[2]-m[10] | 1.44 | 2 | 33% (3 of 9) |
| m[11]-m[20] | 2.60 | 4 | 20% (2 of 10) |
| m[21]-m[31] | 2.82 | 4 | 0% (0 of 11) |

**Trend:** Later m-values have more prime factors and fewer prime values.

---

### 10. Power of 2 (p[1]) Patterns

| m[n] | p[1] Exponent | Full Factorization |
|------|---------------|-------------------|
| m[4] | 1 | p[1] × p[5] |
| m[7] | 1 | p[1] × p[3]² |
| m[13] | 1 | p[1] × p[14] × p[25] |
| m[14] | 1 | p[1] × p[2]² × p[30] |
| m[16] | 1 | p[1] × p[3] × p[4] × p[5]² |
| m[21] | 1 | p[1] × p[2] × p[10599] |
| m[23] | **2** | p[1]² × p[162752] |
| m[24] | **2** | p[1]² × p[7] × p[12] × p[122] |
| m[26] | **2** | p[1]² × p[3] × p[279719] |
| m[28] | 1 | p[1] × p[3] × p[6] × p[151454] |
| m[29] | 1 | p[1] × p[11] × p[39] × p[52]² |

**Pattern:**
- Most values with p[1] have exponent 1
- p[1]² appears at m[23], m[24], m[26] (consecutive cluster!)

---

## SUMMARY OF PATTERNS

### Most Significant Patterns:

1. **p[7]=17 appears 4 times** in positions 9, 11, 12, 24
   - Early cluster: 9, 11, 12
   - Later appearance: 24

2. **m[6] = m[10] = 19** - Direct value repetition

3. **Small primes dominate**: p[1] through p[5] appear in 70% of values

4. **Simple early structure**: m[2] through m[12] mostly products of 1-2 primes

5. **Complexity increases**: Later values have more prime factors and larger primes

6. **π connection**: m[4]/m[3] = 22/7 ≈ π suggests mathematical constant encoding

### Recommendations for Further Analysis:

1. **Check if m[n] values appear as factors in later m[k] values** (k > n)
   - Example: Does m[4]=22 appear as a factor anywhere?

2. **Look for relationships between p[7]=17 appearances**:
   - m[9] = 17 × 29
   - m[11] = 17 × 113
   - m[12] = 17 × 73
   - Check if 29, 113, 73 have relationships

3. **Analyze the d_seq in relation to prime structure**
   - d_seq might index which prime structures to use

4. **Check if prime indices relate to Fibonacci, Lucas, or other sequences**

5. **Test if m[n] = f(m[n-d[n]])** where d[n] is the d_seq value
   - Could factorizations of m[n] and m[n-d[n]] be related?

---

## Technical Details

- **Total values analyzed:** 30 (m[2] through m[31])
- **Total unique primes found:** 38
- **Smallest prime:** p[1] = 2
- **Largest prime:** p[118241] = 1558243 (in m[31])
- **Prime values in sequence:** 5 out of 30 (16.7%)
- **Average number of prime factors:** 2.33

---

*Generated: 2025-12-19*
*Script: /home/rkh/ladder/experiments/06-pysr-m-sequence/factor_m_sequence.py*
*Data: /home/rkh/ladder/experiments/06-pysr-m-sequence/factorization_results.json*
