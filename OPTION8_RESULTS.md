# Option 8: Alternative Decomposition Results

**Date**: 2025-12-18
**Status**: TESTED - No pattern found

## Summary
Tested multiple alternative decomposition forms for adj_n. None revealed a predictable pattern for m_n.

## Forms Tested

### 1. Multiplicative Form
**Formula**: `adj_n = (a*n + b)*k_{d_n} + c*2^n`

**Result**: Non-integer coefficients (c ≈ -0.396)
- System of equations doesn't have integer solution
- Indicates this form doesn't fit the data exactly

### 2. Ratio Form  
**Formula**: `adj_n / 2^n = f(n)`

**Result**: No clear function f(n)
- Values range from -0.375 to 1.72
- No periodicity or polynomial pattern detected

### 3. d-Sequence Pattern
**Question**: Can we predict d_n from n alone?

**Result**: NO
- d=1 is most common (43.5% of cases)
- "Lowest set bit" heuristic only 40.6% accurate
- d depends on key values, not just n

### 4. Normalized m Analysis
**Formula**: `norm_m = m_n / 2^(n - d_n)`

**Result**: Bounded but not deterministic
- Range: [0.72, 2.75], mean ≈ 1.66
- Clusters around simple fractions: 1.0, 1.25, 1.5, 1.75, 2.0, 2.25
- No formula to predict exact value

### 5. Key Relationship Tests
**Tests**:
- m_n mod k_{n-1}: No pattern
- m_n XOR n: No pattern  
- GCD(m_n, earlier keys): Occasional non-trivial GCDs, no pattern

### 6. Prime Factorization
**Observation**: m_n values have diverse prime factors
- m_9 = 17 × 29
- m_11 = 17 × 113
- m_12 = 17 × 73
- Three consecutive with factor 17, likely coincidental
- No common prime structure across sequence

## Key Insights

1. **The d-sequence is optimization-based**: d_n is chosen to minimize |m_n|, so it depends on actual key values, not just n.

2. **m_n appears "random" within bounds**: While bounded in [1, 2.75] × 2^(n-d), the exact value shows no deterministic pattern.

3. **No simple recurrence**: m_n doesn't follow a linear recurrence in terms of m_{n-1}, m_{n-2}, etc.

## Conclusion

Option 8 does not reveal the m_n generation rule. The values appear to be:
- Either deterministic with a complex, unknown formula
- Or derived from a PRNG/hash function
- Or stored in a lookup table by the creator

## Next Steps

1. **Option 9**: Try elliptic curve relationship analysis
2. **Option 10**: Test if m_n relates to EC scalar operations on k values
3. **Option 11**: Analyze if the puzzle creator's public keys reveal patterns
