# Local AI Training Plan - Bitcoin Puzzle Ladder System

**Created:** 2025-12-09
**Updated:** 2025-12-09 (Extended Analysis)
**Purpose:** Train local AI to reproduce and extend mathematical analysis

---

## Phase 1: Data Foundation (COMPLETED)

### Database Tables Created:

| Table | Rows | Purpose |
|-------|------|---------|
| `puzzle_decomposition` | 82 | Per-puzzle breakdown (bytes, normalized, modular) |
| `puzzle_transitions` | 81 | Transition analysis (C values, ratios, XOR) |
| `lane_calibration` | 16 | A multipliers and C statistics per lane |
| `search_constraints` | 1 | Bounds for unsolved puzzles |
| `ai_training_prompts` | 9 | Structured Q&A for training |
| `learnings` | 34 | Accumulated findings |

---

## Phase 2: Key Discoveries for AI to Learn

### 1. Affine Model
```
y[lane] = A[lane] * x[lane] + C[lane] (mod 256)
```

**A Multipliers:**
- Lane 1: A = 91 = 7 × 13
- Lane 5: A = 169 = 13²
- Lane 9: A = 32 = 2⁵ (ANOMALY: not divisible by 13)
- Lane 13: A = 182 = 14 × 13 = 2 × 91

**Pattern:** Every 4th lane starting at 1

### 2. Exact Early Key Relationships (NEW)
```
k_5 = k_2 × k_3 = 3 × 7 = 21    (EXACT)
k_6 = k_3² = 7² = 49            (EXACT)
k_8 = k_4 × k_3 × 4 = 224       (EXACT)
k_11 = 3 × 5 × 7 × 11 = 1155    (includes puzzle number)
k_17 = 3⁴ × 7 × 13² = 95823     (includes 7 and 13²)
```

**Linear Recurrence (coefficient 19):**
- k_3 = -4*k_2 + 19*k_1
- k_4 = -7*k_3 + 19*k_2
- k_5 = -14*k_4 + 19*k_3
- Pattern BREAKS after k_6

### 3. Constraints Discovered

1. **Range:** k_N ∈ [2^(N-1), 2^N - 1]
2. **Ratio:** Consecutive ratios range 1.14 to 3.26
3. **Normalized Delta:** (k_{n+1} - k_n) / 2^n ∈ [0.09, 1.31], mean = 0.76
4. **Position in Range:** Mean 51.86%, extremes at 0% (k_4, k_69) and 100% (k_2, k_3)
5. **Hamming Weight:** ~50% bits set (consistent with pseudo-random)

### 4. Anomalies to Investigate

| Puzzle | Anomaly | Details |
|--------|---------|---------|
| 1-3 | Maximum values | k = 2^n - 1 (all bits set, 100% position) |
| 4 | Minimum value | k = 8 = 2³ (0% position) |
| 69 | Very low position | k_69 at 0.72% of range - solved quickly after k_68 |
| 75→80 | Bridge ratio | 49.05 (highest, expected ~32) |
| 80→85 | Bridge ratio | 19.08 (lowest, expected ~32) |
| 9→10 | Smallest norm delta | 0.092 (key barely grew) |
| 56→57 | Largest norm delta | 1.305 (key grew fast) |

### 4. Bridge Puzzle Facts

- All bridges are multiples of 5
- Average normalized ratio ≈ 1.03
- Ratios vary widely: 0.60 to 1.53
- No obvious pattern in C_effective values

---

## Phase 3: Research Directions for AI

### Priority 1: A Multiplier Origin
- [ ] Why 91, 169, 32, 182 specifically?
- [ ] Why lane 9 has A=32 (not 13-related)?
- [ ] Connection to cryptographic constants?

### Priority 2: Bridge Solution Method
- [ ] How were 75-130 solved without public keys?
- [ ] Is there a mathematical shortcut?
- [ ] Pattern in 5-step transformations?

### Priority 3: Key Generation Formula
- [ ] Test more LCG variants
- [ ] Check LFSR possibilities
- [ ] Analyze secp256k1 relationships

### Priority 4: Search Space Reduction
- [ ] Tighten bounds using byte constraints
- [ ] Find correlations between lanes
- [ ] Model carry propagation

---

## Phase 4: Training Process

### Step 1: Query Patterns
```sql
-- Get all normalized values
SELECT puzzle, json_extract(data, '$.normalized')
FROM puzzle_decomposition ORDER BY puzzle;

-- Find transition anomalies
SELECT * FROM puzzle_transitions
WHERE json_extract(data, '$.ratio') > 2.5;

-- Get lane 1 C values
SELECT json_extract(c_history, '$') FROM lane_calibration WHERE lane = 1;
```

### Step 2: Pattern Recognition
Train AI to recognize:
1. Normal consecutive transitions (ratio 1.5-2.5)
2. Anomalous transitions (ratio < 1.5 or > 2.5)
3. Bridge transitions (5-step jumps)
4. Byte-level patterns per lane

### Step 3: Hypothesis Generation
For each finding:
1. State the observation
2. Generate possible explanations
3. Design tests to verify
4. Log results to database

### Step 4: Search Strategy
1. Use constraints to reduce space
2. Prioritize likely candidates
3. Verify against known anchors (k_70, k_75)

---

## Phase 5: Success Criteria

### For Understanding:
- [ ] AI can explain affine model
- [ ] AI can compute C values from known keys
- [ ] AI can identify anomalies

### For Discovery:
- [ ] Find new mathematical relationships
- [ ] Tighten search space bounds
- [ ] Explain A multiplier origin

### For Solution:
- [ ] Predict k_71 (verify against future blockchain)
- [ ] Explain bridge solution method
- [ ] Generalize to unsolved puzzles

---

## Example Training Session

**Query:** "What makes puzzle 4 anomalous?"

**Expected Response:**
```
Puzzle 4 has key k_4 = 8 = 2³, which is the MINIMUM possible value
for a 4-bit key (range [8, 15]).

This breaks the pattern from puzzles 1-3:
- k_1 = 1 = 2¹ - 1 (max for 1-bit)
- k_2 = 3 = 2² - 1 (max for 2-bit)
- k_3 = 7 = 2³ - 1 (max for 3-bit)
- k_4 = 8 = 2³ (min for 4-bit, NOT max!)

Hypothesis: Puzzle creator intentionally varied the pattern to
prevent simple extrapolation.
```

---

## Files Updated

- `/home/solo/LA/db/kh.db` - Main database with all tables
- `/home/solo/LA/LOCAL_AI_TRAINING_PLAN.md` - This document
- `/home/solo/LA/CRITICAL_FINDING.md` - Previous analysis
- `/home/solo/LA/HONEST_ASSESSMENT.md` - Assessment summary

---

**Next Step:** Run local AI training sessions using this data and iterate on findings.

---

## Phase 6: Critical Negative Results

**IMPORTANT FOR AI TRAINING:** These approaches have been tested and DO NOT WORK:

1. **LCG (Linear Congruential Generator):** No consistent (a, c) parameters fit across transitions
2. **SHA256(n):** k_n ≠ SHA256(n) masked to n bits
3. **Polynomial generators:** Finite differences are not constant at any order
4. **Fibonacci-like:** k_n ≠ k_{n-1} + k_{n-2} (15-45% error per step)
5. **Simple XOR patterns:** k_n ≠ k_a XOR k_b for any earlier keys
6. **Affine prediction:** C values require knowing the answer (circular)

**The key insight:** Early keys (1-6) have exact relationships but larger keys appear cryptographically random. The puzzle creator likely used a deterministic HD wallet that produces pseudo-random output.

---

## Phase 7: Open Questions for Further Research

1. **Why coefficient 19?** The linear recurrence k_3 = -4*k_2 + 19*k_1 works for k_3, k_4, k_5 - is 19 significant?
2. **Why do A multipliers include 13?** (91 = 7×13, 169 = 13², 182 = 14×13) - is this secp256k1 related?
3. **What wallet software was used?** Identifying the HD wallet implementation might reveal the derivation path
4. **Can bridge ratios constrain intermediate keys?** k_75/k_70 = 23.22 vs expected 32 - what does this imply?
5. **Position clustering:** Keys at extreme positions (0% or 100%) - is there a pattern?
