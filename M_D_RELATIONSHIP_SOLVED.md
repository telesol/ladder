# M-D Relationship: SOLVED

**Date**: 2025-12-20
**Status**: VERIFIED 67/67

## The Critical Discovery

The `data_for_csolver.json` has an **index shift of +1**:
- `m_seq[n-1]` stores what FORMULA_PATTERNS.md calls `m[n+1]`
- `d_seq[n-1]` stores what FORMULA_PATTERNS.md calls `d[n+1]`

## Correct Formula

For puzzle number n (where n ≥ 4):

```
adj[n] = k[n] - 2*k[n-1]          # Definition (always true)

m_formula = m_seq[n-2]            # CORRECTED indexing!
d_formula = d_seq[n-2]            # CORRECTED indexing!

# Verification formula:
m_formula = (2^n - adj[n]) / k[d_formula]
```

**Verification Result: 67/67 matches** for n=4 to n=70

## Reconstruction Formula

Given the corrected indexing, we can now express k[n] as:

```
k[n] = 2*k[n-1] + adj[n]
     = 2*k[n-1] + 2^n - m_formula * k[d_formula]
     = 2*k[n-1] + 2^n - m_seq[n-2] * k[d_seq[n-2]]
```

## Example Verification

For n=5:
- k[5] = 21, k[4] = 8
- adj[5] = 21 - 2*8 = 5
- m_formula = m_seq[5-2] = m_seq[3] = 9
- d_formula = d_seq[5-2] = d_seq[3] = 2
- k[d] = k[2] = 3
- Check: (2^5 - 5) / 3 = 27 / 3 = 9 = m_formula ✓

For n=10:
- k[10] = 514, k[9] = 467
- adj[10] = 514 - 2*467 = -420
- m_formula = m_seq[8] = 19
- d_formula = d_seq[8] = 7
- k[d] = k[7] = 76
- Check: (2^10 - (-420)) / 76 = 1444 / 76 = 19 = m_formula ✓

## Key Insight: d[n] Minimizes m[n]

For each n, d[n] is chosen to **minimize** m[n] among all valid divisors.

This means:
1. Calculate adj[n] = k[n] - 2*k[n-1]
2. Calculate numerator = 2^n - adj[n]
3. Find all k[j] that divide numerator evenly
4. Choose j that gives the smallest quotient → that's d[n]

## Implications for Prediction

To predict k[n+1] from k[1..n]:
1. We would need to know m[n+1] and d[n+1]
2. d[n+1] minimizes m[n+1], but we don't know m[n+1] in advance
3. m[n+1] is constructed from mathematical constants (π, e, √2, etc.)
4. The construction rules for m[n] are in FORMULA_PATTERNS.md

## Files

- `verify_m_d_corrected.py` - Verification script (67/67 pass)
- `FORMULA_PATTERNS.md` - m-sequence construction rules
- `data_for_csolver.json` - Source data (note: index shifted!)

## Summary

| Item | Status |
|------|--------|
| m[n] = (2^n - adj[n]) / k[d[n]] | ✅ VERIFIED (67/67) |
| Index correction needed | ✅ m_seq[n-2], d_seq[n-2] |
| d[n] minimizes m[n] | ✅ Previously verified |
| k[n] reconstruction | ✅ k[n] = 2*k[n-1] + 2^n - m*k[d] |
