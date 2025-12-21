#!/usr/bin/env python3
"""
Gap Puzzle Constraint Analysis

For gap puzzles (75, 80, 85, 90), we don't have k[n-1].
But we CAN derive constraints on k[n-1], m[n], and d[n].

Given:
- k[n] is known
- k[d] is known for d ∈ {1, 2, 3, 4, ...}
- Bit length constraint: k[n-1] ∈ [2^(n-2), 2^(n-1) - 1]
- Formula: k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]

We can solve for k[n-1]:
  k[n-1] = (k[n] + m[n]*k[d[n]] - 2^n) / 2

For k[n-1] to be in valid range:
  2^(n-2) <= (k[n] + m[n]*k[d[n]] - 2^n) / 2 <= 2^(n-1) - 1

Solving for m[n]:
  (2^(n-1) + 2^n - k[n]) / k[d[n]] <= m[n] <= (2^n + 2^n - k[n] - 2) / k[d[n]]
  (3*2^(n-1) - k[n]) / k[d[n]] <= m[n] <= (2^(n+1) - k[n] - 2) / k[d[n]]
"""
import sqlite3
import json
from pathlib import Path
import math

# Load known k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 161):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

# Load m and d values for reference
data_file = Path('data_for_csolver.json')
if data_file.exists():
    with open(data_file) as f:
        data = json.load(f)
        m_seq = data.get('m_seq', [])
        d_seq = data.get('d_seq', [])
else:
    m_seq = []
    d_seq = []

print("=" * 80)
print("GAP PUZZLE CONSTRAINT ANALYSIS")
print("=" * 80)
print()

# For each gap puzzle, compute valid (m, d, k_prev) combinations
gap_puzzles = [75, 80, 85, 90]

for n in gap_puzzles:
    k_n = k_values[n]
    print(f"### n = {n}, k[{n}] = {k_n} ###")
    print()

    # k[n-1] must be in [2^(n-2), 2^(n-1) - 1]
    k_prev_min = 2**(n-2)
    k_prev_max = 2**(n-1) - 1

    print(f"k[{n-1}] must be in [{k_prev_min}, {k_prev_max}]")
    print(f"Range size: {k_prev_max - k_prev_min + 1} = 2^{n-2}")
    print()

    # For each possible d value
    valid_combinations = []

    for d in [1, 2, 3, 4, 5, 6, 7, 8]:
        if d not in k_values:
            continue
        k_d = k_values[d]

        # m[n] bounds from bit-length constraint on k[n-1]
        # k[n-1] = (k[n] + m*k[d] - 2^n) / 2
        # For k[n-1] >= k_prev_min:
        #   (k[n] + m*k[d] - 2^n) / 2 >= 2^(n-2)
        #   k[n] + m*k[d] - 2^n >= 2^(n-1)
        #   m*k[d] >= 2^(n-1) + 2^n - k[n] = 3*2^(n-1) - k[n]
        #   m >= (3*2^(n-1) - k[n]) / k[d]

        # For k[n-1] <= k_prev_max:
        #   (k[n] + m*k[d] - 2^n) / 2 <= 2^(n-1) - 1
        #   k[n] + m*k[d] - 2^n <= 2^n - 2
        #   m*k[d] <= 2^n - 2 + 2^n - k[n] = 2^(n+1) - k[n] - 2
        #   m <= (2^(n+1) - k[n] - 2) / k[d]

        m_min = (3 * 2**(n-1) - k_n) / k_d
        m_max = (2**(n+1) - k_n - 2) / k_d

        # m must be positive integer
        m_min_int = max(1, int(math.ceil(m_min)))
        m_max_int = int(math.floor(m_max))

        if m_max_int >= m_min_int:
            num_valid_m = m_max_int - m_min_int + 1
            print(f"d = {d}: m ∈ [{m_min_int}, {m_max_int}] ({num_valid_m} valid values)")

            # Show first few valid m values and corresponding k[n-1]
            for m in range(m_min_int, min(m_min_int + 3, m_max_int + 1)):
                k_prev = (k_n + m * k_d - 2**n) // 2
                # Check if k[n-1] is actually in range
                if k_prev_min <= k_prev <= k_prev_max:
                    # Also check that k_prev has correct bit length
                    if k_prev.bit_length() == n - 1:
                        valid_combinations.append((d, m, k_prev))
                        print(f"      m = {m}: k[{n-1}] = {k_prev}")
                        if len(valid_combinations) >= 3:
                            print(f"      ...")
                            break
        else:
            print(f"d = {d}: No valid m values")

    print()

    # Check if any combination matches known patterns
    if valid_combinations:
        print(f"Total valid (d, m) combinations: many (sampling shown above)")
        print()

        # Check: which d is most likely based on d[n] patterns for n < 70?
        # d[n] distribution: 43.5% d=1, 29% d=2
        print("Based on d[n] distribution for n <= 70:")
        print("  - Most likely: d = 1 (43.5% historical)")
        print("  - Second: d = 2 (29% historical)")
        print()

    print("-" * 80)
    print()

# Now test if there's a pattern in how m[n] relates to n for gaps
print("### Looking for m[n] pattern at gaps ###")
print()
print("Historical m[n] values at multiples of 5:")
for n in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]:
    i = n - 2
    if 0 <= i < len(m_seq):
        m = m_seq[i]
        log2_m = math.log2(m) if m > 0 else 0
        print(f"m[{n:2d}] = {m:20d} (log2 = {log2_m:6.2f})")

print()
print("Extrapolating log2(m[n]) ~ n pattern:")
# log2(m[n]) roughly follows a pattern
log2_m_values = []
for n in range(5, 71, 5):
    i = n - 2
    if 0 <= i < len(m_seq) and m_seq[i] > 0:
        log2_m_values.append((n, math.log2(m_seq[i])))

if len(log2_m_values) >= 2:
    # Simple linear regression
    sum_n = sum(x[0] for x in log2_m_values)
    sum_log2 = sum(x[1] for x in log2_m_values)
    sum_n2 = sum(x[0]**2 for x in log2_m_values)
    sum_n_log2 = sum(x[0] * x[1] for x in log2_m_values)
    n_pts = len(log2_m_values)

    slope = (n_pts * sum_n_log2 - sum_n * sum_log2) / (n_pts * sum_n2 - sum_n**2)
    intercept = (sum_log2 - slope * sum_n) / n_pts

    print(f"Linear fit: log2(m[n]) ≈ {slope:.4f}*n + {intercept:.4f}")
    print()

    # Predict m for gaps
    for n in [75, 80, 85, 90]:
        predicted_log2_m = slope * n + intercept
        predicted_m = 2 ** predicted_log2_m
        print(f"Predicted m[{n}] ≈ {predicted_m:.2e} (log2 ≈ {predicted_log2_m:.2f})")

print()
print("=" * 80)
print("KEY INSIGHT")
print("=" * 80)
print()
print("For gap puzzles, there are MANY valid (d, m, k[n-1]) combinations.")
print("The bit-length constraint alone is not enough to uniquely determine")
print("which values were used.")
print()
print("To find the ACTUAL values, we need:")
print("1. A pattern in m[n] = M(n) that predicts m for any n")
print("2. A pattern in d[n] = D(n) that predicts d for any n")
print("3. Or: additional constraints from the puzzle structure")
print()
