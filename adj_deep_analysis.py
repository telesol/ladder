#!/usr/bin/env python3
"""
Deep adj[n] Pattern Analysis
============================
Find deeper mathematical relationships in adj[n] sequence
"""

import json
import math
import sqlite3
from fractions import Fraction

# Load k-values from database
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT puzzle_id, priv_hex
    FROM keys
    WHERE puzzle_id BETWEEN 1 AND 70
    ORDER BY puzzle_id
""")
rows = cursor.fetchall()
conn.close()

k_seq = {0: 0}
for puzzle_id, priv_hex in rows:
    k_seq[puzzle_id] = int(priv_hex, 16)

# Compute adj[n]
adj = {}
for n in range(2, 71):
    if n in k_seq and (n-1) in k_seq:
        adj[n] = k_seq[n] - 2 * k_seq[n-1]

# Load m and d sequences
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']
d_seq = data['d_seq']

# Build m and d dicts (1-indexed)
m = {}
d = {}
for i in range(len(m_seq)):
    n = i + 2
    m[n] = m_seq[i]
    d[n] = d_seq[i]

print("=" * 80)
print("DEEP adj[n] PATTERN ANALYSIS")
print("=" * 80)
print()

# ============================================================================
# Pattern 1: adj[n] vs 2^n - N[n]
# ============================================================================

print("PATTERN 1: Relationship with N[n] = 2^n - adj[n]")
print("-" * 80)

# From the formula: m[n] = (2^n - adj[n]) / k[d[n]]
# So: 2^n - adj[n] = m[n] * k[d[n]]
# Thus: adj[n] = 2^n - m[n] * k[d[n]]

print("Verifying: adj[n] = 2^n - m[n] * k[d[n]]")
print()

mismatches = 0
for n in range(2, min(32, max(adj.keys())+1)):
    if n in adj and n in m and n in d and d[n] in k_seq:
        computed = 2**n - m[n] * k_seq[d[n]]
        actual = adj[n]

        if computed == actual:
            status = "✓"
        else:
            status = "✗"
            mismatches += 1

        print(f"  {status} adj[{n:2d}] = 2^{n:2d} - {m[n]:15,d} × k[{d[n]}]  = {actual:20,d}")

print()
if mismatches == 0:
    print("✓ Formula verified for all tested values!")
else:
    print(f"✗ {mismatches} mismatches found")
print()

# ============================================================================
# Pattern 2: adj[n] and m[n] relationships
# ============================================================================

print("PATTERN 2: Direct relationships between adj[n] and m-values")
print("-" * 80)

# Check if adj[n] appears in m-sequence or relates to m-values
print("Cases where |adj[n]| = m[k] for some k:")
adj_abs = {n: abs(adj[n]) for n in adj}
m_set = set(m.values())

for n in range(2, min(32, max(adj.keys())+1)):
    if n in adj_abs:
        if adj_abs[n] in m_set:
            # Find which m[k] matches
            for k in m:
                if m[k] == adj_abs[n]:
                    print(f"  adj[{n:2d}] = ±{adj_abs[n]:12,d} = m[{k}]")
                    break

print()

# Check if adj[n] = m[n] ± offset
print("Cases where adj[n] = ±m[n] or adj[n] = ±m[k]:")
for n in range(2, min(20, max(adj.keys())+1)):
    if n in adj and n in m:
        if abs(adj[n]) == m[n]:
            print(f"  adj[{n:2d}] = ±m[{n}]  ({adj[n]:10,d})")
        # Check adj[n] = m[k] for nearby k
        for k in range(max(2, n-5), min(n+5, max(m.keys())+1)):
            if k in m and k != n:
                if abs(adj[n]) == m[k]:
                    print(f"  adj[{n:2d}] = ±m[{k}]  ({adj[n]:10,d})")

print()

# ============================================================================
# Pattern 3: Divisibility patterns
# ============================================================================

print("PATTERN 3: Divisibility by k[i] values")
print("-" * 80)

# Check if adj[n] is divisible by k[1..8]
print("Checking divisibility of adj[n] by k[1] through k[8]:")
print()

divisibility_matrix = []
for n in range(2, min(32, max(adj.keys())+1)):
    if n in adj:
        divisors = []
        for i in range(1, 9):
            if i in k_seq and k_seq[i] != 0:
                if adj[n] % k_seq[i] == 0:
                    divisors.append(i)
        divisibility_matrix.append((n, divisors))

for n, divisors in divisibility_matrix[:20]:
    if divisors:
        div_str = ', '.join(f"k[{i}]" for i in divisors)
        quotients = ', '.join(f"{adj[n]//k_seq[i]}" for i in divisors)
        print(f"  adj[{n:2d}] divisible by: {div_str}  (quotients: {quotients})")

print()

# ============================================================================
# Pattern 4: Relationship with d[n]
# ============================================================================

print("PATTERN 4: Relationship between adj[n] and d[n]")
print("-" * 80)

# Group by d[n] value
from collections import defaultdict
by_d = defaultdict(list)
for n in range(2, min(71, max(adj.keys())+1)):
    if n in adj and n in d:
        by_d[d[n]].append(n)

print("adj[n] patterns grouped by d[n]:")
print()

for d_val in sorted(by_d.keys())[:8]:  # Show first 8 d-values
    ns = by_d[d_val][:5]  # Show first 5 examples
    print(f"d[n] = {d_val} (k[{d_val}] = {k_seq[d_val]:,}):")
    for n in ns:
        print(f"  adj[{n:2d}] = {adj[n]:20,d}  (m[{n}] = {m[n]:12,d})")
    print()

# ============================================================================
# Pattern 5: Ratio patterns
# ============================================================================

print("PATTERN 5: Ratio patterns adj[n] / adj[n-1]")
print("-" * 80)

ratios = []
for n in range(3, min(31, max(adj.keys())+1)):
    if n in adj and (n-1) in adj and adj[n-1] != 0:
        ratio = adj[n] / adj[n-1]
        ratios.append((n, ratio))

print("Ratios adj[n] / adj[n-1]:")
for n, ratio in ratios[:20]:
    print(f"  adj[{n:2d}] / adj[{n-1:2d}] = {ratio:12.6f}")

print()

# Check for exponential growth
print("Testing exponential growth: adj[n] ≈ C × r^n")
print()

# Use least squares to find best fit C × r^n
import numpy as np

n_vals = []
log_adj = []
for n in range(2, min(31, max(adj.keys())+1)):
    if n in adj and adj[n] > 0:
        n_vals.append(n)
        log_adj.append(math.log(adj[n]))

if len(n_vals) > 10:
    # Fit log(adj[n]) = log(C) + n*log(r)
    coeffs = np.polyfit(n_vals, log_adj, 1)
    log_r = coeffs[0]
    log_C = coeffs[1]
    r = math.exp(log_r)
    C = math.exp(log_C)

    print(f"Best fit: adj[n] ≈ {C:.6f} × {r:.6f}^n")
    print(f"log(r) = {log_r:.6f}, r ≈ {r:.6f}")
    print(f"r ≈ 2^{math.log2(r):.6f}")
    print()

# ============================================================================
# Pattern 6: adj[n] mod 2^n patterns
# ============================================================================

print("PATTERN 6: adj[n] mod 2^n patterns")
print("-" * 80)

print("adj[n] mod 2^n:")
for n in range(2, min(21, max(adj.keys())+1)):
    if n in adj:
        mod_val = adj[n] % (2**n)
        # Also show as percentage of 2^n
        pct = (abs(mod_val) / (2**n)) * 100
        print(f"  adj[{n:2d}] mod 2^{n:2d} = {mod_val:15,d}  ({pct:6.2f}% of 2^{n})")

print()

# ============================================================================
# Pattern 7: Relationship with k[n] mod patterns
# ============================================================================

print("PATTERN 7: Compare adj[n] mod 3 with k[n] mod 3")
print("-" * 80)

print("n  | k[n] mod 3 | adj[n] mod 3 | 2*k[n-1] mod 3")
print("---|------------|--------------|----------------")
for n in range(2, min(21, max(adj.keys())+1)):
    if n in k_seq and n in adj and (n-1) in k_seq:
        k_mod = k_seq[n] % 3
        adj_mod = adj[n] % 3
        two_k_prev_mod = (2 * k_seq[n-1]) % 3

        # Since k[n] = 2*k[n-1] + adj[n], verify:
        # k[n] mod 3 = (2*k[n-1] + adj[n]) mod 3
        expected_k_mod = (two_k_prev_mod + adj_mod) % 3

        status = "✓" if expected_k_mod == k_mod else "✗"

        print(f"{n:2d} | {k_mod:10d} | {adj_mod:12d} | {two_k_prev_mod:14d}  {status}")

print()

# ============================================================================
# Pattern 8: Check if adj[n] = f(n) for small n
# ============================================================================

print("PATTERN 8: Direct formulas for small n (n=2-10)")
print("-" * 80)

# Try to find patterns like adj[n] = a*n^2 + b*n + c or similar

print("Looking for polynomial or simple formulas:")
print()

# For n=2-4 (Mersenne region)
print("Mersenne region (n=2,3):")
print(f"  adj[2] = {adj[2]} = 2^2 - 3 = 1  ✓")
print(f"  adj[3] = {adj[3]} = 2^3 - 7 = 1  ✓")
print(f"  Pattern: adj[n] = 2^n - k[n] = 1 for n=2,3")
print()

# For n=4-10
print("Post-Mersenne region (n=4-10):")
for n in range(4, 11):
    if n in adj:
        # Try various formulas
        formulas = []

        # Check against powers of 2
        for exp in range(0, 10):
            if adj[n] == 2**exp or adj[n] == -(2**exp):
                formulas.append(f"±2^{exp}")

        # Check against small multiples of primes
        for p in [3, 5, 7, 11, 13, 17, 19, 23]:
            for mult in range(1, 10):
                if abs(adj[n]) == mult * p:
                    formulas.append(f"±{mult}×{p}")

        if formulas:
            print(f"  adj[{n}] = {adj[n]:6d} = {formulas[0]}")
        else:
            print(f"  adj[{n}] = {adj[n]:6d}")

print()

# ============================================================================
# Pattern 9: Differences and second differences
# ============================================================================

print("PATTERN 9: First and second differences")
print("-" * 80)

print("Δadj[n] = adj[n] - adj[n-1]:")
for n in range(3, min(21, max(adj.keys())+1)):
    if n in adj and (n-1) in adj:
        diff1 = adj[n] - adj[n-1]
        print(f"  Δadj[{n:2d}] = adj[{n:2d}] - adj[{n-1:2d}] = {diff1:15,d}")

print()

print("Δ²adj[n] = Δadj[n] - Δadj[n-1]:")
for n in range(4, min(21, max(adj.keys())+1)):
    if n in adj and (n-1) in adj and (n-2) in adj:
        diff1_n = adj[n] - adj[n-1]
        diff1_prev = adj[n-1] - adj[n-2]
        diff2 = diff1_n - diff1_prev
        print(f"  Δ²adj[{n:2d}] = {diff2:20,d}")

print()

print("=" * 80)
print("DEEP ANALYSIS COMPLETE")
print("=" * 80)
