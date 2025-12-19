#!/usr/bin/env python3
"""Verify the core formula and find patterns."""

import json
import sqlite3

# Load m and d sequences
with open('/home/solo/LA/data_for_csolver.json') as f:
    data = json.load(f)

m_list = data['m_seq']
d_list = data['d_seq']
m_seq = {n: m_list[n-2] for n in range(2, 2 + len(m_list))}
d_seq = {n: d_list[n-2] for n in range(2, 2 + len(d_list))}

# Load k values from database
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70")
k_seq = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

print("="*80)
print("CORE FORMULA VERIFICATION")
print("="*80)
print()
print("Formula: k_n = 2 × k_{n-1} + adj_n")
print("Where:   adj_n = 2^n - m_n × k_{d_n}")
print()

all_match = True
for n in range(2, 71):
    if n not in k_seq or n-1 not in k_seq:
        continue

    k_n = k_seq[n]
    k_prev = k_seq[n-1]
    m = m_seq[n]
    d = d_seq[n]
    k_d = k_seq[d]

    # Calculate what adj should be
    adj = k_n - 2 * k_prev

    # Verify: adj = 2^n - m × k_d
    expected_adj = 2**n - m * k_d

    match = adj == expected_adj
    all_match = all_match and match

    if n <= 20 or not match:
        status = "✓" if match else "✗"
        print(f"n={n:2d}: k={k_n:>15}, adj={adj:>10}, 2^n - m×k_d = {expected_adj:>10} {status}")

print()
print(f"All formulas match: {all_match}")

print()
print("="*80)
print("DERIVED: m_n = (2^n - adj_n) / k_{d_n}")
print("="*80)
print()

print("Checking if m_n can be expressed using only n and k values:")
for n in range(2, 25):
    k_n = k_seq[n]
    k_prev = k_seq[n-1]
    m = m_seq[n]
    d = d_seq[n]
    k_d = k_seq[d]

    adj = k_n - 2 * k_prev

    # m = (2^n - adj) / k_d
    numerator = 2**n - adj
    if numerator % k_d == 0:
        computed_m = numerator // k_d
        assert computed_m == m, f"Mismatch at n={n}"
        print(f"n={n:2d}: m = (2^{n} - {adj}) / k[{d}] = {numerator} / {k_d} = {m}")

print()
print("="*80)
print("KEY INSIGHT: How is d_n determined?")
print("="*80)
print()

# The d sequence determines which k value to use
# Let's look for patterns in d

print("d[n] values grouped by value:")
from collections import defaultdict
d_groups = defaultdict(list)
for n in range(2, 71):
    d_groups[d_seq[n]].append(n)

for d, ns in sorted(d_groups.items()):
    print(f"  d={d}: {ns[:20]}{'...' if len(ns) > 20 else ''}")

print()
print("="*80)
print("CHECKING: Is d[n] deterministic from k values?")
print("="*80)
print()

# For each n, check which k[d] would give integer m
for n in range(4, 20):
    k_n = k_seq[n]
    k_prev = k_seq[n-1]
    adj = k_n - 2 * k_prev

    valid_d = []
    for d_candidate in range(1, n):
        k_d = k_seq[d_candidate]
        numerator = 2**n - adj
        if numerator % k_d == 0:
            m_candidate = numerator // k_d
            if m_candidate > 0:
                valid_d.append((d_candidate, m_candidate))

    actual_d = d_seq[n]
    actual_m = m_seq[n]

    print(f"n={n:2d}: actual d={actual_d}, m={actual_m}")
    print(f"       valid (d,m) pairs: {valid_d}")
    print()
