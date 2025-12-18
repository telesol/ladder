# Session Findings: Construction Approaches
Date: 2025-12-18

## Solver Deep Reasoning Results

### B-Solver (phi4) - EC Scalar Construction
**STATUS**: COMPLETED

Key proposals:
1. Ladder generator: `kₙ = 2·kₙ₋₁ + adjₙ`
2. adj derived from EC: `adjₙ = f(x(n·G)) mod 2ⁿ`
3. Verification pseudocode provided
4. Parameter search strategies outlined

**Testing Results**: Simple EC approaches (n*G coordinates) do NOT match adj_n
- Only 2/19 matches (n=2,3 where adj=1 coincidentally)

### C-Solver (QWQ) - PRNG Reconstruction
**STATUS**: PARTIAL (reasoning cut off)

Key insights before cutoff:
1. m_n / 2^(n-d_n) must be in [0.72, 2.75]
2. m_n MUST be integer
3. d_n chosen from {1..8} to minimize |m_n|
4. PRNG candidates: LCG, XORshift, Mersenne Twister

## Prototype Testing Results

### EC Hypothesis Tests
| Test | Result |
|------|--------|
| adj_n = x(n*G) mod 2^n | NO MATCH |
| adj_n = x(k_{n-1}*G) mod 2^n | NO MATCH |
| adj_n = x_diff(k_n*G - k_{n-1}*G) | 1 match only |
| adj_n = y(n*G) mod 2^n | NO MATCH |
| adj_n = SHA256(n) mod 2^n | NO MATCH |

### PRNG (LCG) Seed Search
- Best result: 3/20 matches (essentially random)
- LCG does NOT explain the sequence

### adj_n Sequence Analysis

**Sign Pattern**:
- 43.5% negative (not random)
- Negative at n = [4, 7, 10, 13, 16, 17, 19, 22, ...]

**Key Property**:
- |adj_n| < 2^n ALWAYS (bounded as expected)

**Divisibility**:
- adj_n often divisible by k_d values (from formula definition)

### Normalized m Analysis

**Critical Finding**:
```
n=2: norm_m = 1.5000 = 3/2    (EXACT match to 2-1/n = 1.5)
n=3: norm_m = 1.7500 = 7/4
n=4: norm_m = 2.7500 = 11/4
n=5: norm_m = 1.1250 = 9/8
n=6: norm_m = 1.1875 = 19/16
n=7: norm_m = 1.5625 = 25/16
n=8: norm_m = 1.4375 = 23/16
```

**Pattern**: First few norm_m values are CLEAN FRACTIONS with power-of-2 denominators!

**d_n Distribution**:
- d=1: 46.4% (most common)
- d=2: 27.5%
- d=4: 7.2%
- Others: <5%

**d_n Sequence**: `11122241712141411112214112114181352126222512311113`

## Key Barrier Analysis

The barrier remains: **How is m_n generated?**

Tested and FAILED:
1. m_n = f(EC point coordinates) - NO
2. m_n = LCG PRNG output - NO
3. m_n = simple function of n - NO

The clean fractions at low n suggest a SIMPLE generating rule,
but it becomes more complex at higher n.

## Hypothesis for Next Session

The puzzle creator may have:
1. Started with simple fractions (3/2, 7/4, 11/4...)
2. Applied a transformation that obscures the pattern at higher n
3. Used some external data source (dates, transaction IDs, etc.)

## Files Created This Session
- `SOLVER_SYNTHESIS.md` - Combined solver findings
- `ladder_generator.py` - Main prototype
- `ec_deep_test.py` - EC hypothesis tests
- `adj_sequence_analysis.py` - adj pattern analysis
- `norm_m_analysis.py` - Normalized m analysis
- `bsolver_ec_clean.txt` - Cleaned B-Solver output
- `CONSTRUCTION_TASK_BSOLVER.txt` - B-Solver task
- `CONSTRUCTION_TASK_CSOLVER.txt` - C-Solver task

## Verified Facts
1. k_n = 2*k_{n-1} + adj_n (100% for all 70 keys)
2. adj_n = 2^n - m_n * k_{d_n}
3. norm_m bounded [0.72, 2.75], mean ~1.68
4. d_n predominantly 1 or 2

## Next Steps
1. Test if early m values (3, 7, 22, 9, 19, 50, 23, 493...) follow a recurrence
2. Check if m_n relates to k values: m_n = a*k_x + b*k_y
3. Analyze m_n prime factorizations for hidden structure
4. Try non-LCG PRNGs (XORshift, MT) with various seeds
5. Check blockchain metadata from puzzle creation time
