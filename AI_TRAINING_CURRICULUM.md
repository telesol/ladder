# Local AI Training Curriculum - Bitcoin Puzzle Mathematics

**Purpose:** Train local AI to understand, reproduce, and extend the mathematical analysis of Bitcoin puzzle keys.

---

## LEVEL 1: Foundation (Must Pass All)

### Exercise 1.1: Basic Key Properties
**Task:** Given puzzle number N, state the valid range for key k_N.

**Example:**
- Input: N = 10
- Expected: k_10 must be in range [512, 1023] because 2^9 = 512 and 2^10 - 1 = 1023

**Test Cases:**
1. N = 5 → Range = ?
2. N = 20 → Range = ?
3. N = 71 → Range = ?

---

### Exercise 1.2: Key Factorization
**Task:** Factorize the given key and identify any special properties.

**Example:**
- Input: k_11 = 1155
- Expected: 1155 = 3 × 5 × 7 × 11 (includes puzzle number 11 as factor)

**Test Cases:**
1. k_5 = 21 → Factors = ?
2. k_6 = 49 → Factors = ?
3. k_17 = 95823 → Factors = ?

---

### Exercise 1.3: Position in Range
**Task:** Calculate where a key sits in its valid range (as percentage).

**Formula:** position = (k_N - 2^(N-1)) / (2^N - 1 - 2^(N-1)) × 100%

**Example:**
- Input: k_4 = 8, N = 4
- Calculation: (8 - 8) / (15 - 8) × 100% = 0%
- Expected: k_4 is at 0% of its range (minimum possible value)

**Test Cases:**
1. k_3 = 7, N = 3 → Position = ?
2. k_69 = 297274491920375905804, N = 69 → Position = ?
3. k_70 = 970436974005023690481, N = 70 → Position = ?

---

## LEVEL 2: Pattern Recognition (Must Pass 4/5)

### Exercise 2.1: Verify Exact Relationships
**Task:** Verify or disprove the following claimed relationship.

**Example:**
- Claim: k_5 = k_2 × k_3
- Given: k_2 = 3, k_3 = 7, k_5 = 21
- Verification: 3 × 7 = 21 = k_5 ✓ VERIFIED

**Test Cases:**
1. Claim: k_6 = k_3² (given k_3 = 7, k_6 = 49)
2. Claim: k_8 = k_4 × k_3 × 4 (given k_4 = 8, k_3 = 7, k_8 = 224)
3. Claim: k_7 = k_2 × k_5 (given k_2 = 3, k_5 = 21, k_7 = 76)

---

### Exercise 2.2: Linear Recurrence Test
**Task:** Test if the linear recurrence k_n = a×k_{n-1} + b×k_{n-2} holds.

**Example:**
- Test: k_3 = -4×k_2 + 19×k_1
- Given: k_1 = 1, k_2 = 3, k_3 = 7
- Calculation: -4×3 + 19×1 = -12 + 19 = 7 = k_3 ✓

**Test Cases:**
1. Verify: k_4 = -7×k_3 + 19×k_2 (given k_2=3, k_3=7, k_4=8)
2. Verify: k_5 = -14×k_4 + 19×k_3 (given k_3=7, k_4=8, k_5=21)
3. Test: Does k_7 = a×k_6 + 19×k_5 for any integer a? (given k_5=21, k_6=49, k_7=76)

---

### Exercise 2.3: Normalized Delta Calculation
**Task:** Calculate the normalized delta between consecutive keys.

**Formula:** Normalized_Delta = (k_{n+1} - k_n) / 2^n

**Example:**
- Input: k_60 = 1135041350219496382, k_61 = 1425787542618654982, n = 60
- Delta = 1425787542618654982 - 1135041350219496382 = 290746192399158600
- Normalized = 290746192399158600 / 2^60 = 0.252

**Test Cases:**
1. k_1=1, k_2=3 → Normalized delta = ?
2. k_9=467, k_10=514 → Normalized delta = ?
3. k_69=297274491920375905804, k_70=970436974005023690481 → Normalized delta = ?

---

### Exercise 2.4: Affine Model Verification
**Task:** Given the affine equation y = A×x + C (mod 256), compute C.

**A multipliers:** Lane 0: A=1, Lane 1: A=91, Lane 5: A=169

**Example:**
- Lane 1, transition 69→70
- x = byte 1 of k_69 = 126
- y = byte 1 of k_70 = 78
- C = (y - A×x) mod 256 = (78 - 91×126) mod 256 = (78 - 11466) mod 256 = 132

**Test Cases:**
1. Lane 0 (A=1): x=12, y=241 → C = ?
2. Lane 1 (A=91): x=104, y=53 → C = ?
3. Lane 5 (A=169): x=177, y=215 → C = ?

---

### Exercise 2.5: Bridge Ratio Analysis
**Task:** Calculate the ratio between bridge puzzles and compare to expected.

**Expected ratio for 5-step jump:** ~2^5 = 32

**Example:**
- k_70 = 970436974005023690481
- k_75 = 22538323240989823823367
- Ratio = k_75 / k_70 = 23.22 (vs expected 32)

**Test Cases:**
1. k_75 / k_70 = ? (compare to 32)
2. k_80 / k_75 = ? (compare to 32)
3. k_85 / k_80 = ? (compare to 32)

---

## LEVEL 3: Analysis & Reasoning (Must Pass 3/4)

### Exercise 3.1: Anomaly Detection
**Task:** Identify what makes the given puzzle anomalous.

**Example:**
- Input: Puzzle 4 with k_4 = 8
- Expected Analysis:
  - k_4 = 8 is the MINIMUM value in range [8, 15]
  - Previous pattern: k_1, k_2, k_3 were all MAXIMUM values
  - This breaks the pattern intentionally

**Test Cases:**
1. What makes k_69 anomalous? (Hint: position in range)
2. What makes the transition 9→10 anomalous? (Hint: normalized delta)
3. What makes A[lane 9] = 32 anomalous? (Hint: other A values)

---

### Exercise 3.2: Constraint Derivation
**Task:** Given observed bounds, derive constraints for unsolved puzzles.

**Given:**
- Normalized delta range: [0.09, 1.31]
- k_70 = 970436974005023690481
- k_71 must be in [2^70, 2^71 - 1]

**Expected:** Derive the tightest constraint on k_71.

---

### Exercise 3.3: Pattern Extension
**Task:** Test if a pattern extends to higher puzzles.

**Given:** k_5 = k_2 × k_3 = 3 × 7 = 21

**Question:** Does any similar relationship k_n = k_a × k_b hold for n > 6?

**Approach:**
1. For each n from 7 to 20
2. Test all pairs (a, b) where a < b < n
3. Report any exact matches

---

### Exercise 3.4: Hypothesis Generation
**Task:** Propose and test a new mathematical hypothesis.

**Example Hypothesis:** "Keys divisible by their puzzle number tend to be at low positions in their range"

**Test:**
1. Identify keys divisible by N: k_1, k_4, k_8, k_11
2. Calculate their positions: 0%, 0%, 75%, 12.8%
3. Conclusion: 2 of 4 are at very low positions, 1 high - hypothesis partially supported

**Your Task:** Propose a hypothesis about the relationship between:
- The number 13 appearing in A multipliers (91=7×13, 169=13², 182=14×13)
- Any property of the keys or transitions

---

## LEVEL 4: Discovery (Bonus)

### Exercise 4.1: Find New Patterns
**Task:** Discover a mathematical pattern not documented in the training materials.

**Requirements:**
1. State the pattern clearly
2. Provide evidence (at least 3 examples)
3. Test if pattern holds beyond examples
4. Propose why this pattern might exist

---

### Exercise 4.2: Search Space Reduction
**Task:** Propose a method to reduce the search space for unsolved puzzles.

**Current:** 2^70 possibilities
**Goal:** Reduce to 2^60 or less with mathematical justification

---

### Exercise 4.3: Predict Bridge Behavior
**Task:** Using k_70, k_75, k_80, predict k_85 bounds BEFORE looking at actual value.

**After prediction:** Compare to actual k_85 and analyze error.

---

## EVALUATION CRITERIA

### Passing Scores:
- **Level 1:** Must pass ALL exercises (foundation knowledge)
- **Level 2:** Must pass 4 of 5 exercises (pattern recognition)
- **Level 3:** Must pass 3 of 4 exercises (analysis ability)
- **Level 4:** Bonus points for any discoveries

### Grading:
- **Correct answer:** Full credit
- **Correct method, arithmetic error:** 80% credit
- **Partial understanding:** 50% credit
- **Wrong approach:** 0% credit

---

## REFERENCE DATA

### Known Keys (for exercises):
```
k_1 = 1
k_2 = 3
k_3 = 7
k_4 = 8
k_5 = 21
k_6 = 49
k_7 = 76
k_8 = 224
k_9 = 467
k_10 = 514
k_11 = 1155
k_17 = 95823
k_69 = 297274491920375905804
k_70 = 970436974005023690481
k_75 = 22538323240989823823367
k_80 = 1105520030589234487939456
k_85 = 21090315766411506144426920
k_90 = 868012190417726402719548863
```

### A Multipliers:
```
Lane 0: A = 1
Lane 1: A = 91 = 7 × 13
Lane 5: A = 169 = 13²
Lane 9: A = 32 = 2^5
Lane 13: A = 182 = 14 × 13
All other lanes: A = 1
```

### Key Statistics:
- Normalized delta mean: 0.762
- Normalized delta range: [0.092, 1.305]
- Position mean: 51.86%
- Low position keys: 4, 10, 38, 50, 69, 85
- High position keys: 2, 3, 25, 30, 31, 57, 60, 63, 64

---

**Document Version:** 1.0
**Created:** 2025-12-09
**For:** Local AI Training
