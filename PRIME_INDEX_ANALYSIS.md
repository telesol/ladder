# Prime Index Analysis of m-sequence

**Generated**: 2025-12-19

## Complete Factorization Summary (n=2 to n=70)

### Primes (m_n is prime itself)
| n | m_n | Prime Index |
|---|-----|-------------|
| 6 | 19 | 8 |
| 8 | 23 | 9 |
| 10 | 19 | 8 |
| 18 | 255121 | 22450 |
| 20 | 900329 | 71300 |

**Note**: m[6] = m[10] = 19 (identical values!)

### Contains p[7] = 17 (frequently appears!)
| n | m_n | Full Factorization | Other Factor |
|---|-----|-------------------|--------------|
| 9 | 493 | 17 × 29 | p[10] |
| 11 | 1921 | 17 × 113 | p[30] |
| 12 | 1241 | 17 × 73 | p[21] |
| 24 | 1693268 | 2² × 17 × 37 × 673 | multiple |
| 48 | 329601320238553 | 11 × 17 × large | p[5] × p[7] × large |
| 67 | 35869814695994276026 | 2 × 17 × 31 × 179 × ... | multiple |

**Pattern**: p[7]=17 appears at n = 9, 11, 12, 24, 48, 67

### Contains p[8] = 19
| n | m_n | Full Factorization |
|---|-----|--------------------|
| 6 | 19 | 19 (prime) |
| 10 | 19 | 19 (prime) |
| 19 | 564091 | 11 × 19 × 2699 |
| 25 | 29226275 | 5² × 13 × 19 × 4733 |
| 57 | 4490805416683930 | 2 × 5 × 19 × 113 × ... |
| 58 | 121581741999020893 | 19 × 191 × ... |
| 69 | 34896088136426753598 | 2 × 3 × 19 × 109 × ... |

**Pattern**: p[8]=19 appears at n = 6, 10, 19, 25, 57, 58, 69

### Two-Prime Products
| n | m_n | Factorization | Indices |
|---|-----|---------------|---------|
| 4 | 22 | 2 × 11 | [1, 5] |
| 9 | 493 | 17 × 29 | [7, 10] |
| 11 | 1921 | 17 × 113 | [7, 30] |
| 12 | 1241 | 17 × 73 | [7, 21] |
| 15 | 26989 | 137 × 197 | [33, 45] |
| 30 | 105249691 | 599 × 175709 | [109, 15965] |
| 37 | 121962932837 | 257 × 474563941 | [55, 25084026] |

### Perfect Squares
| n | m_n | Factorization |
|---|-----|---------------|
| 5 | 9 | 3² |
| 17 | 138269 | 37² × 101 |

### Pattern: Second Index Relation to n
For n=9,11,12 (all have p[7]=17):
- n=9: indices [7, 10] → 10 = n+1
- n=11: indices [7, 30] → 30 = n + 19 = n + m[6]
- n=12: indices [7, 21] → 21 = n + 9 = n + m[5]

**HYPOTHESIS**: When m_n = p[7] × p[k], then k = n + m[j] for some j < n

---

## Key Observations

1. **p[7]=17 is special** - appears in many factorizations
2. **m[6] = m[10] = 19** - identical values at different n
3. **Self-referential structure** - indices reference earlier m values
4. **Primes at n=18,20** - very large prime indices (22450, 71300)

---

## Hypotheses to Test

### H1: Index Formula
For m_n = p[a] × p[b]:
- a = fixed (often 7)
- b = n + m[f(n)] for some function f

### H2: Prime at Large n
When m_n is prime, its index may be computable from earlier values

### H3: d_n Determines Structure
The d_n value might determine whether m_n is prime vs composite

---

## Questions for LLMs

1. What pattern generates the second prime index in products?
2. Why does m[6] = m[10]?
3. How is the prime index 22450 (for m[18]) computed?
4. Is there a formula relating d_n to the factorization structure of m_n?
