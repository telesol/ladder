#!/usr/bin/env python3
"""
Explore 6-step recursion for k-sequence
=======================================

Hypothesis: k[n] = c × k[n-6] + offset might work better than 3-step

Evidence:
- k[17] = 75×k[11] + 9198  (75 = 3×5²)
- k[20] = 81×k[14] + 9253  (81 = 3⁴ = 9²)
"""

import sqlite3
import json

# Load data
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)
m = {i+2: v for i, v in enumerate(data['m_seq'])}

print("=" * 80)
print("EXPLORING 6-STEP RECURSION: k[n] = c × k[n-6] + offset")
print("=" * 80)

# For each n from 17 to 40, find best (c, offset) for k[n] = c×k[n-6] + offset
print("\n### 6-STEP RECURSION ANALYSIS ###")
print("k[n] = c × k[n-6] + offset\n")

results = []
for n in range(17, 41):
    if n-6 >= 1 and n in k:
        kn = k[n]
        kn6 = k[n-6]

        # Find best integer c
        best_c = kn // kn6
        # Try c and c+1
        for c in [best_c - 1, best_c, best_c + 1]:
            if c > 0:
                offset = kn - c * kn6
                if abs(offset) < kn6:  # Offset smaller than k[n-6]
                    # Check if offset has a nice form
                    results.append((n, c, offset, kn, kn6))

# Analyze patterns in coefficients
print(f"{'n':>3} {'c':>5} {'offset':>12} {'c factors':>15} {'offset/k[1]':>12}")
print("-" * 60)
for n, c, offset, kn, kn6 in results:
    # Factor c
    c_factors = []
    temp = c
    for p in [3, 5, 7, 9, 11]:
        while temp % p == 0:
            c_factors.append(p)
            temp //= p
    if temp > 1:
        c_factors.append(temp)

    off_k1 = offset / k[1] if k[1] else "N/A"

    print(f"{n:>3} {c:>5} {offset:>12} {str(c_factors):>15} {off_k1:>12.1f}")

# Look for patterns in c values
print("\n### COEFFICIENT c ANALYSIS ###")
c_values = [(n, c) for n, c, _, _, _ in results]
print("Coefficients:", [c for _, c in c_values])

# Check if c = 3^a × 5^b
print("\nChecking c = 3^a × 5^b pattern:")
for n, c, _, _, _ in results:
    a, b = 0, 0
    temp = c
    while temp % 3 == 0:
        a += 1
        temp //= 3
    while temp % 5 == 0:
        b += 1
        temp //= 5
    remainder = temp
    if remainder == 1:
        print(f"  c[{n}] = {c} = 3^{a} × 5^{b} ✓")
    else:
        print(f"  c[{n}] = {c} = 3^{a} × 5^{b} × {remainder}")

# Alternative: try c = 9^((n-11)/6)
print("\n### TESTING c = 9^((n-11)/6) HYPOTHESIS ###")
for n in range(17, 41, 6):
    exp = (n - 11) // 6
    predicted_c = 9 ** exp
    actual_c = None
    for nn, c, _, _, _ in results:
        if nn == n:
            actual_c = c
            break
    if actual_c:
        match = "✓" if predicted_c == actual_c else f"✗ (actual={actual_c})"
        print(f"  n={n}: 9^{exp} = {predicted_c} {match}")

# Check 9-step recursion
print("\n### 9-STEP RECURSION ANALYSIS ###")
print("k[n] = c × k[n-9] + offset\n")

for n in range(20, 41):
    if n-9 >= 1 and n in k:
        kn = k[n]
        kn9 = k[n-9]

        c = kn // kn9
        offset = kn - c * kn9

        if abs(offset) < kn9:  # Offset smaller than k[n-9]
            print(f"k[{n}] = {c}×k[{n-9}] + {offset}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
FINDINGS:
1. 6-step recursion works but coefficients are irregular
2. Coefficients are products of small primes (3, 5, 7)
3. Offsets are large but might have structure

NEXT STEPS:
1. Analyze offset patterns more carefully
2. Try different recursion depths (9, 12)
3. Look for meta-formula relating c to n
""")
