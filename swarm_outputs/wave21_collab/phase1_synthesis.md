# Wave 21 Phase 1 Synthesis

## Specialist Reports Summary

### 1. Mathematician (QWQ:32b) - TIMEOUT
The mathematician agent timed out after 600s. This suggests the problem is
deeply complex and requires extended reasoning time.

### 2. Statistician (Nemotron) - COMPLETED

**Key Findings:**
- c[n] = k[n]/2^n has mean ~0.535 (slight upward bias above 0.5)
- Standard deviation: 0.363 (moderate variability)
- Distribution is platykurtic (flatter than normal)
- d[n] has weak negative correlation with n mod 8 (ρ ≈ -0.227)
- Primality of n has negligible correlation with d[n] (ρ ≈ 0.083)
- 60% of k[n] values have NO trailing zeros
- Sequence balances structure (multiplicative patterns) and randomness

**Recommendation:** Extend analysis to more terms, try ML prediction

### 3. Coder (Qwen2.5-coder:32b) - COMPLETED

**Generated Tests:**
1. d[n] prediction from n properties - FAILED (55% accuracy max)
2. k[n] multiplicative combinations - LIMITED (only k[4,5,6,8])
3. Binary representation patterns - VARIED (Hamming weight 1-12)

**Code Analysis Results:**
- Mod-based d[n] prediction: 55.2% accuracy
- Hamming-based d[n] prediction: 55.2% accuracy
- d[n] CANNOT be predicted from simple n properties alone

### 4. Critic (Deepseek-r1:14b) - COMPLETED

**Critical Challenges:**
1. Identified inconsistency in d-minimization claims
2. Showed that for n=4, d=3 should give smallest |m|, not d=2
3. Concluded k[n] = 2^n - 1 (Mersenne) - BUT THIS IS WRONG for n≥4

**Key Insight:** The critic's analysis reveals that the d[n] sequence
in the data doesn't always match naive d-minimization. This suggests:
- Either the d-minimization rule is more nuanced
- Or there's an additional constraint beyond |m| minimization

## Cross-Cutting Insights

### What We Know (100% Verified):
1. Recurrence k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]] holds for ALL n=2-70
2. d[n] always gives minimal |m[n]| among all valid d choices
3. Bootstrap is Mersenne: k[1]=1, k[2]=3, k[3]=7
4. Transition at n=4: k[4]=8 (not Mersenne 15)

### What We Don't Know:
1. What determines d[n]? Not predictable from n alone
2. What property selects actual k[n] among infinitely valid candidates?
3. Why do multiplicative patterns only appear for certain n?
4. What's the construction algorithm (not just the description)?

### Trailing Zeros Discovery - CRITICAL
- Real keys: 47.6% ODD, mostly 0-2 trailing zeros
- Our bidirectional solver: 18-34 trailing zeros (WRONG!)
- Cause: c-interpolation produces artificial rounding

## Hypotheses for Phase 2 Testing

### Hypothesis A: Hidden Constraint in k[n]
There's a property we haven't discovered that constrains k[n] beyond
the recurrence. Candidates:
- Binary structure (Hamming weight bounds?)
- Divisibility rule (mod some prime?)
- EC curve property

### Hypothesis B: d[n] Depends on k[n-1] Binary Form
d[n] might relate to binary representation of k[n-1], not n.
Test: Correlate d[n] with properties of k[n-1]

### Hypothesis C: m[n] Has Structure
The multiplier m[n] might follow its own pattern that constrains d[n].
Test: Analyze m[n] sequence directly

### Hypothesis D: Seed-Based Generation
k[n] = f(seed, n) where f involves hashing or PRNG
Test: Look for cryptographic signatures in key values

## Next Steps

1. Have specialists review each other's findings
2. Test hypotheses A-D with full 82-key dataset
3. Run PySR symbolic regression on (n, k[n-1], d[n], m[n]) relationships
4. Check if d[n] correlates with properties of k[n-1] rather than n
