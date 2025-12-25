# Wave 21+ Autonomous Exploration Breakthroughs

## Session 1-5 Summary (Previous Sessions)

### Verified Facts
1. **Recurrence**: k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]] (100% verified n=2-70)
2. **m[n] Formula**: m[n] = (2^n - adj[n]) / k[d[n]] **MUST BE INTEGER**
3. **m[n] Positivity**: m[n] > 0 always (100% verified)
4. **d[n] Selection**: d[n] minimizes |m[n]| among valid divisors (100% verified)
5. **d Distribution**: d ∈ {1,2} for ~74% of cases

### Ruled Out (Previous)
- Smallest k[n] in range (fails n≥5)
- Globally smallest |m| (fails n≥4)
- Predict d[n] from n alone (55% max)

---

## Session 6 (2025-12-24 19:42) - COMPREHENSIVE HYPOTHESIS TESTING

### CRITICAL FINDING: "Minimize |m|" Does NOT Select k[n]

**Test:** For n=4-20, check if actual k[n] has minimum |m| among all valid candidates.

**Result: 0% match (0/17)**

- For EVERY n, a candidate with m=0 exists (k[n] = 2*k[n-1] + 2^n)
- But m=0 candidates are NEVER the actual k[n]
- Actual k[n] always has MUCH larger |m|

| n | Actual k[n] | Actual m | Min |m| candidate | Min |m| |
|---|-------------|----------|---------------------|---------|
| 4 | 8           | 22       | 30                  | 0       |
| 5 | 21          | 27       | 48                  | 0       |
| 6 | 49          | 57       | 106                 | 0       |
| 10| 514         | 1444     | 1958                | 0       |

**CONCLUSION:** The recurrence admits infinitely many valid k[n], and "minimize |m|" is NOT the selection criterion.

---

### Multiplicative Structure Analysis

**Finding:** Multiplicative relationships exist but are EMERGENT, not a selection criterion.

| n | k[n] | Structure |
|---|------|-----------|
| 4 | 8    | 2³ × k[1] |
| 5 | 21   | k[2] × k[3] = 3 × 7 |
| 6 | 49   | k[3]² = 7² |
| 8 | 224  | 2⁵ × k[3] = 32 × 7 |

- Only 4/27 k[n] values have exact multiplicative formulas
- 14/27 are divisible by some previous k[i]
- 9/27 have no clear multiplicative structure
- Key insight: Most k[n] for n≥3 contain k[3]=7 as a factor

---

### Fibonacci Connection Discovered ★★★

Some k[n] values ARE Fibonacci numbers:
- k[1] = 1 = F₁
- k[2] = 3 = F₄
- k[4] = 8 = F₆
- k[5] = 21 = F₈

Combined with Mersenne pattern:
- k[1] = 1 = 2¹ - 1
- k[2] = 3 = 2² - 1
- k[3] = 7 = 2³ - 1

This suggests the puzzle creator intentionally chose early values from known sequences.

---

### Growth Rate Selection Hypothesis - DISPROVEN

**Hypothesis:** k[n] is selected to maintain growth rate λ ≈ 2.0073

**Test:** Check if actual k[n] is closest to λ*k[n-1] among valid candidates

**Result: 0% match (0/7 for n=4-10)**

- Computed λ (geometric mean) = 2.014461
- Growth rate varies wildly: min=1.10, max=3.37
- Actual k[n] is NOT closest to λ*k[n-1]

---

### Binary Pattern Observations

Notable binary structures:
- k[1-3]: All 1s (Mersenne: 0b1, 0b11, 0b111)
- k[4] = 8 = 0b1000 (power of 2)
- k[10] = 514 = 0b1000000010 (only 2 bits set, very sparse)

"Prime-like" k[n] (coprime with all previous):
- k[9] = 467
- k[12] = 2683
- k[15] = 26867

---

### adj[n] Sign Pattern

Pattern for n=2-16: ++- (repeating)
- 5 complete cycles before break
- BREAKS at n=17 (Fermat prime 2⁴ + 1)
- After n=17: irregular pattern

Full pattern (n=2..41): `++-++-++-++-++--+-++--++-++-++-+--++-++-`

---

## THE FUNDAMENTAL MYSTERY (Still Unsolved)

Given k[1..n-1], what mathematical property UNIQUELY determines k[n]?

**Disproven hypotheses:**
1. ✗ Minimize |m| globally
2. ✗ Smallest k in valid range
3. ✗ Closest to λ*k[n-1] (growth rate)
4. ✗ Simple multiplicative formula

**Remaining possibilities:**
1. PRNG/hash with unknown seed
2. Undiscovered mathematical formula
3. Minimize some OTHER function
4. Construction algorithm we haven't identified
5. Semi-random with constraints

**Key observation:** The puzzle creator appears to have used intentional patterns for early values (Mersenne, Fibonacci) but the selection criterion for larger n remains unknown.

---

## Next Steps

1. Test if there's a relationship between consecutive adj[n] values
2. Analyze if k[n] minimizes some OTHER objective function
3. Search for PRNG/seed patterns in the k-sequence
4. Investigate if the puzzle creator documented the generation method anywhere

---

## Files Created This Session

- `test_minimize_m.py` - Proves minimize |m| doesn't select k[n]
- `test_multiplicative_selection.py` - Analyzes multiplicative structure
- `analyze_adj_direct.py` - Direct adj[n] pattern analysis
- `test_adj_formula.py` - Tests formulas for adj[n]
- `test_generation_hypothesis.py` - Tests algorithmic generation
- `test_continued_fractions.py` - Tests CF relationships
- `test_growth_rate_selection.py` - Tests growth rate hypothesis
