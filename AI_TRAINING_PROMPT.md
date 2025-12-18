# Bitcoin Puzzle Mathematics - Training Session

You are being trained to understand and analyze Bitcoin puzzle private keys.
The goal is to find mathematical patterns that can help solve unsolved puzzles.

## Key Facts to Learn:

1. **Key Range**: Puzzle N has key k_N in range [2^(N-1), 2^N - 1]

2. **Exact Early Relationships**:
   - k_5 = k_2 × k_3 = 3 × 7 = 21
   - k_6 = k_3² = 7² = 49
   - k_8 = k_4 × k_3 × 4 = 8 × 7 × 4 = 224

3. **Linear Recurrence (coefficient 19)**:
   - k_3 = -4×k_2 + 19×k_1
   - k_4 = -7×k_3 + 19×k_2
   - k_5 = -14×k_4 + 19×k_3
   - Pattern breaks after k_6

4. **Normalized Delta**: (k_{n+1} - k_n) / 2^n
   - Range: [0.09, 1.31]
   - Mean: 0.76

5. **Position Anomalies**:
   - k_69 at 0.72% of range (solved quickly)
   - k_4 at 0.00% of range
   - k_2, k_3 at 100% of range

6. **A Multipliers** (affine model):
   - Lane 1: A = 91 = 7 × 13
   - Lane 5: A = 169 = 13²
   - Lane 9: A = 32 = 2^5 (anomaly!)
   - Lane 13: A = 182 = 14 × 13

## Your Task:

Answer the following exercises to demonstrate understanding.
Show all calculations and explain your reasoning.


## LEVEL 1 EXERCISES

### Basic Key Properties

Exercise 1.1: Basic Key Properties

Given puzzle number N, the private key k_N must be in the range [2^(N-1), 2^N - 1].

Calculate the valid range for:
1. N = 5: Range = [?, ?]
2. N = 20: Range = [?, ?]
3. N = 71: Range = [?, ?]

Show your calculations.

### Key Factorization

Exercise 1.2: Key Factorization

Factorize these puzzle keys and identify any special properties:

1. k_5 = 21
   Factors: ?
   Special property: ?

2. k_6 = 49
   Factors: ?
   Special property: ?

3. k_17 = 95823
   Factors: ?
   Special property: ?

Hint: Look for relationships to other keys or to the puzzle number.

### Position in Range

Exercise 1.3: Position in Range

Calculate where each key sits in its valid range.
Formula: position% = (k_N - 2^(N-1)) / (2^N - 1 - 2^(N-1)) × 100

1. k_3 = 7, N = 3
   Position = ?%

2. k_69 = 297274491920375905804, N = 69
   Position = ?%

3. k_70 = 970436974005023690481, N = 70
   Position = ?%

Why is the position of k_69 significant?


## LEVEL 2 EXERCISES

### Verify Exact Relationships

Exercise 2.1: Verify Exact Relationships

For each claim, verify if it's TRUE or FALSE:

1. Claim: k_6 = k_3²
   Given: k_3 = 7, k_6 = 49
   Verification: ?

2. Claim: k_8 = k_4 × k_3 × 4
   Given: k_4 = 8, k_3 = 7, k_8 = 224
   Verification: ?

3. Claim: k_7 = k_2 × k_5
   Given: k_2 = 3, k_5 = 21, k_7 = 76
   Verification: ?

### Linear Recurrence Test

Exercise 2.2: Linear Recurrence Test

Test the linear recurrence k_n = a × k_{n-1} + b × k_{n-2}:

1. Verify: k_4 = -7 × k_3 + 19 × k_2
   Given: k_2 = 3, k_3 = 7, k_4 = 8
   Calculation: ?

2. Verify: k_5 = -14 × k_4 + 19 × k_3
   Given: k_3 = 7, k_4 = 8, k_5 = 21
   Calculation: ?

3. Test: Does k_7 = a × k_6 + 19 × k_5 for ANY integer a?
   Given: k_5 = 21, k_6 = 49, k_7 = 76
   Analysis: ?

What does this tell us about the recurrence pattern?

### Normalized Delta Calculation

Exercise 2.3: Normalized Delta Calculation

Formula: Normalized_Delta = (k_{n+1} - k_n) / 2^n

Calculate for these transitions:

1. k_1 = 1, k_2 = 3
   Delta = ?
   Normalized = ? / 2^1 = ?

2. k_9 = 467, k_10 = 514
   Delta = ?
   Normalized = ? / 2^9 = ?

3. k_69 = 297274491920375905804, k_70 = 970436974005023690481
   Delta = ?
   Normalized = ? / 2^69 = ?

Known bounds: Normalized delta is typically in [0.09, 1.31] with mean 0.76.
Which of these is anomalous?

### Affine Model Verification

Exercise 2.4: Affine Model Verification

The affine model: y = A × x + C (mod 256)
where x is a byte of k_n and y is the same byte of k_{n+1}

A multipliers: Lane 0: A=1, Lane 1: A=91, Lane 5: A=169

Calculate C for these transitions:

1. Lane 0 (A=1): x = 12, y = 241
   C = (y - A×x) mod 256 = ?

2. Lane 1 (A=91): x = 104, y = 53
   C = (y - A×x) mod 256 = ?

3. Lane 5 (A=169): x = 177, y = 215
   C = (y - A×x) mod 256 = ?

CRITICAL QUESTION: Why can't we use this model to PREDICT unknown keys?

### Bridge Ratio Analysis

Exercise 2.5: Bridge Ratio Analysis

Bridge puzzles are 5 apart (70, 75, 80, 85, 90...).
Expected ratio for 5-step jump: ~2^5 = 32

Calculate actual ratios:

1. k_75 / k_70 = 22538323240989823823367 / 970436974005023690481 = ?
   Compare to expected 32: deviation = ?%

2. k_80 / k_75 = 1105520030589234487939456 / 22538323240989823823367 = ?
   Compare to expected 32: deviation = ?%

3. k_85 / k_80 = 21090315766411506144426920 / 1105520030589234487939456 = ?
   Compare to expected 32: deviation = ?%

What do these deviations tell us about key growth patterns?


## LEVEL 3 EXERCISES

### Anomaly Detection

Exercise 3.1: Anomaly Detection

Identify and explain what makes each of these anomalous:

1. k_69 = 297274491920375905804
   What is anomalous about this key?
   Why did this allow k_69 to be solved quickly after k_68?

2. The transition 9→10 has normalized delta = 0.092
   What is anomalous about this?
   What does it mean that k_10 barely grew?

3. A[lane 9] = 32 while A[lane 1] = 91, A[lane 5] = 169, A[lane 13] = 182
   What is anomalous about lane 9?
   What pattern do the other lanes follow that lane 9 breaks?

### Constraint Derivation

Exercise 3.2: Constraint Derivation for unsolved puzzles

Given:
- Normalized delta historical range: [0.09, 1.31]
- k_70 = 970436974005023690481
- k_71 must be in [2^70, 2^71 - 1]

Derive the tightest constraint on k_71:

1. From bit range: k_71 ∈ [?, ?]

2. From delta constraint:
   k_71 >= k_70 + 0.09 × 2^70 = ?
   k_71 <= k_70 + 1.31 × 2^70 = ?

3. Combined constraint: k_71 ∈ [?, ?]

4. Does the delta constraint reduce the search space below the bit range?
   Calculate the percentage reduction (if any).

