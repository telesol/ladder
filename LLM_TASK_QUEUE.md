# LLM Task Queue - 12 Hours of Research

**Created**: 2025-12-20
**Orchestrator**: Dell (Claude Opus)
**Target**: Local LLM on Dell

---

## Overview

These tasks are designed for systematic mathematical derivation. Each task should:
- Read relevant files before starting
- Show all mathematical work
- Verify against known data
- Document findings in markdown

**RULES**: DERIVE, don't predict. VERIFY against database. NO guessing.

---

## TASK 1: adj[n] Formula Derivation (2 hours)

**Priority**: CRITICAL
**Files to read**: `COMPLETE_FORMULA_SYSTEM.md`, `data_for_csolver.json`

### Objective
Derive a closed-form formula for adj[n] = k[n] - 2*k[n-1]

### Known Facts
```
adj[2] = 1, adj[3] = 1 (Mersenne bootstrap)
adj[4] = -6, adj[5] = 5, adj[6] = 7, adj[7] = -22
Sign pattern ++- holds for n=2-16 (76.7% match)
```

### Sub-tasks
1.1. Extract adj[n] for n=2 to n=70 from k-sequence
1.2. Analyze adj[n] mod p for primes p = 2,3,5,7,11,13,17,19
1.3. Check if adj[n] relates to continued fractions of π, e, √2
1.4. Find recurrence relation if exists: adj[n] = f(adj[n-1], adj[n-2], ...)
1.5. Test hypothesis: adj[n] = ±2^a × 3^b × p where p ∈ {17, 19, ...}

### Output
`adj_formula_analysis.md` with verified formula or detailed negative result

---

## TASK 2: Offset Formula Verification (1.5 hours)

**Priority**: HIGH
**Files to read**: `K_FORMULAS_COMPLETE.md`, `MISTRAL_SYNTHESIS.md`

### Objective
Verify and extend Mistral's offset formula:
```
offset[n] = (-1)^(n+1) × 2^f(n) × 5^g(n) × h(n)
```

### Sub-tasks
2.1. Compute offset[n] = k[n] - 9*k[n-3] for n=10 to n=70
2.2. Factorize each offset completely
2.3. Verify Mistral's f(n) = floor(n/3) - 2 hypothesis
2.4. Verify prime selection: 17 for n ≡ 0,3,4 (mod 6), 19 for n ≡ 2 (mod 6)
2.5. Find exceptions and patterns for n ≥ 40

### Output
`offset_formula_verified.md` with complete verification table

---

## TASK 3: d[n] Closed-Form Derivation (1.5 hours)

**Priority**: HIGH
**Files to read**: `FORMULA_PATTERNS.md`, `data_for_csolver.json`

### Objective
Find closed-form for d[n] beyond "minimizes m[n]"

### Known Facts
```
d[n] = max{i : k[i] | (2^n - adj[n])}
Distribution: d=1 (43.5%), d=2 (29%), d=4 (7.2%)
```

### Sub-tasks
3.1. For each n, compute all divisors of (2^n - adj[n]) that are k[i] values
3.2. Find pattern: when is d[n]=1 vs d[n]=2 vs d[n]=4?
3.3. Check correlation: d[n] vs n mod 3, n mod 6, n mod 12
3.4. Check correlation: d[n] vs floor(log2(n))
3.5. Derive explicit formula if possible

### Output
`d_sequence_formula.md` with derivation

---

## TASK 4: Phase Transition Analysis at n=17 (1 hour)

**Priority**: MEDIUM
**Files to read**: `MISTRAL_SYNTHESIS.md`, `FORMULA_PATTERNS.md`

### Objective
Understand why patterns break at n=17

### Known Facts
```
k[17] = 3^4 × 7 × 13^2 = 95823 (highly structured)
17 = 2^(2^2) + 1 is Fermat prime F_2
Sign pattern ++- breaks at n=17
```

### Sub-tasks
4.1. Compare k[n] factorization for n=14,15,16 vs n=17,18,19
4.2. Compare adj[n] properties before/after n=17
4.3. Check if 2^16 = 65536 is a threshold
4.4. Analyze m[n] formula changes at n=17
4.5. Propose: is there a different algorithm for n≥17?

### Output
`phase_transition_n17.md` with analysis

---

## TASK 5: Jump Puzzle Constraint Analysis (1.5 hours)

**Priority**: HIGH
**Files to read**: `db/kh.db` (query k[75], k[80], k[85], k[90])

### Objective
Use known jump puzzles to constrain formulas

### Known Values
```sql
SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IN (75, 80, 85, 90);
```

### Sub-tasks
5.1. Verify 3-step recursion k[n] = 9*k[n-3] + offset for n=75,80,85,90
5.2. Back-calculate what k[72,73,74] would need to be for k[75] formula
5.3. Check if offset growth rate is consistent
5.4. Find constraints on k[71] from k[75]
5.5. Test if adj formula extends to n=75,80,85,90

### Output
`jump_puzzle_constraints.md` with derived bounds

---

## TASK 6: k[n] Prime Factorization Patterns (1 hour)

**Priority**: MEDIUM
**Files to read**: `db/kh.db`

### Objective
Find patterns in prime factorizations of k[n]

### Sub-tasks
6.1. Factorize k[n] for n=1 to n=70
6.2. Count occurrence of each prime p < 100 in factorizations
6.3. Find: which k[n] are prime? (k[9]=467, k[12]=2683, ...)
6.4. Find: which k[n] are highly composite?
6.5. Check: does k[n] share factors with k[n mod 3 siblings]?

### Output
`k_factorization_patterns.md` with statistics

---

## TASK 7: EC Point Arithmetic Investigation (1 hour)

**Priority**: MEDIUM
**Files to read**: `analyze_ec_compression.py`

### Objective
Analyze relationships between P[n] = k[n]*G points

### Sub-tasks
7.1. Compute x-coordinates of k[n]*G for n=1 to n=20
7.2. Check if x[n+1] - x[n] has pattern
7.3. Check if point addition: P[n] = P[a] + P[b] for any a,b < n
7.4. Analyze y-parity sequence beyond what's known
7.5. Check if scalar relationships exist: k[n] = 2*k[a] + k[b]

### Output
`ec_point_analysis.md` with findings

---

## TASK 8: Binary Pattern Analysis (1 hour)

**Priority**: MEDIUM
**Files to read**: `db/kh.db`

### Objective
Find patterns in binary representations of k[n]

### Sub-tasks
8.1. Convert k[n] to binary for n=1 to n=70
8.2. Count bit patterns: number of 1s, longest run of 1s, etc.
8.3. Check: is there a pattern in bit_count(k[n]) - n?
8.4. Check: Hamming distance between k[n] and k[n-1]
8.5. Check: XOR patterns k[n] ^ k[n-1]

### Output
`binary_patterns.md` with analysis

---

## TASK 9: Modular Arithmetic Properties (1 hour)

**Priority**: MEDIUM
**Files to read**: `data_for_csolver.json`

### Objective
Find modular relationships in sequences

### Sub-tasks
9.1. Compute k[n] mod p for p = 7, 17, 19, 37, 41
9.2. Find periodicity in k[n] mod p sequences
9.3. Check: k[n] ≡ 0 (mod p) patterns
9.4. Check: m[n] mod 17, m[n] mod 19 patterns
9.5. Relate to Fermat's Little Theorem if applicable

### Output
`modular_analysis.md` with period tables

---

## TASK 10: Ratio Analysis k[n]/k[n-1] (0.5 hours)

**Priority**: LOW
**Files to read**: `db/kh.db`

### Objective
Analyze the ratio sequence

### Sub-tasks
10.1. Compute r[n] = k[n]/k[n-1] for n=2 to n=70
10.2. Find continued fraction of each ratio
10.3. Check if ratios approach a limit
10.4. Check correlation with 2^n growth

### Output
`ratio_analysis.md` with continued fractions

---

## TASK 11: Sign Pattern Mathematical Derivation (0.5 hours)

**Priority**: MEDIUM
**Files to read**: `FORMULA_PATTERNS.md`

### Objective
Derive the ++- sign pattern mathematically

### Known Facts
```
adj[n] sign: + + - + + - + + - ... for n=2-16 (76.7% match overall)
```

### Sub-tasks
11.1. Verify sign(adj[n]) for n=2 to n=70
11.2. Model as: sign(adj[n]) = (-1)^f(n) for some f
11.3. Test f(n) = floor((n+1)/3) mod 2
11.4. Find exact formula for sign pattern

### Output
`sign_pattern_formula.md` with derivation

---

## TASK 12: Magnitude Growth Rate (0.5 hours)

**Priority**: MEDIUM
**Files to read**: `analyze_compression.py`

### Objective
Derive growth rate of |adj[n]| and |offset[n]|

### Sub-tasks
12.1. Compute log2(|adj[n]|) for n=4 to n=70
12.2. Fit linear regression: log2(|adj[n]|) ≈ a*n + b
12.3. Compare with theoretical: adj grows as O(2^n)
12.4. Find deviation patterns from exponential growth

### Output
`magnitude_growth.md` with regression results

---

## Summary Table

| Task | Hours | Priority | Key Question |
|------|-------|----------|--------------|
| 1 | 2.0 | CRITICAL | What is adj[n] formula? |
| 2 | 1.5 | HIGH | Is offset formula correct? |
| 3 | 1.5 | HIGH | Closed-form for d[n]? |
| 4 | 1.0 | MEDIUM | Why n=17 transition? |
| 5 | 1.5 | HIGH | What do jump puzzles tell us? |
| 6 | 1.0 | MEDIUM | k[n] factorization patterns? |
| 7 | 1.0 | MEDIUM | EC point relationships? |
| 8 | 1.0 | MEDIUM | Binary patterns in k[n]? |
| 9 | 1.0 | MEDIUM | Modular arithmetic patterns? |
| 10 | 0.5 | LOW | Ratio analysis? |
| 11 | 0.5 | MEDIUM | Sign pattern formula? |
| 12 | 0.5 | MEDIUM | Magnitude growth rate? |
| **TOTAL** | **12.0** | | |

---

## Execution Order

**Phase A (Critical Path)**: Tasks 1, 2, 3 (5 hours)
**Phase B (Constraints)**: Tasks 5, 4 (2.5 hours)
**Phase C (Deep Analysis)**: Tasks 6, 7, 8, 9 (4 hours)
**Phase D (Quick Wins)**: Tasks 10, 11, 12 (1.5 hours)

---

## Output Format

Each task should produce:
1. Markdown file with analysis
2. Python script if computation needed
3. Summary of verified vs unverified claims
4. Next steps recommendation

---

**Status**: READY FOR EXECUTION
**Created by**: Dell Orchestrator
**For**: Local LLM execution
