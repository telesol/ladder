#!/usr/bin/env python3
"""Analyze what (d, m) values would generate the actual k75."""

import sqlite3

# Load k-values
conn = sqlite3.connect('/home/solo/LadderV3/kh-assist/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 95 ORDER BY puzzle_id")
rows = cur.fetchall()
conn.close()

k = {row[0]: int(row[1], 16) for row in rows}

print("="*80)
print("ANALYZING ACTUAL K75")
print("="*80)
print()

n = 75
k_actual = k[75]
k_prev = k[70]

print(f"k70 = {k_prev:#x}")
print(f"k75 = {k_actual:#x}")
print()

# Master formula: k_n = 2*k_{n-1} + (2^n - m*k_d)
# For bridges, n-1 is not sequential, so we use k70 as "previous"

# Reverse engineer to find all valid (d, m) pairs
adj = k_actual - 2 * k_prev
numerator = 2**n - adj

print(f"Adjustment: k75 - 2*k70 = {adj:#x}")
print(f"Numerator: 2^75 - adj = {numerator:#x}")
print()

# Find all (d, m) where m*k_d = numerator
print("Valid (d, m) pairs that would generate actual k75:")
print("-" * 60)

valid_pairs = []

for d in range(1, 71):
    if d not in k:
        continue

    k_d = k[d]
    if k_d == 0:
        continue

    if numerator % k_d == 0:
        m = numerator // k_d
        if m > 0:
            valid_pairs.append((d, m, k_d))

# Sort by m
valid_pairs.sort(key=lambda x: x[1])

if valid_pairs:
    print(f"Found {len(valid_pairs)} valid pairs:")
    print()

    for i, (d, m, k_d) in enumerate(valid_pairs[:20], 1):
        print(f"{i:2d}. d={d:2d}, m={m:>30}, k_d={k_d:#x}")

    print()
    print("Minimum m pair:")
    d_min, m_min, k_d_min = valid_pairs[0]
    print(f"  d={d_min}, m={m_min}")

    # Verify
    k_reconstructed = 2*k_prev + (2**n - m_min * k_d_min)
    print(f"\nVerification:")
    print(f"  k75 = 2*k70 + (2^75 - {m_min}*k{d_min})")
    print(f"      = {k_reconstructed:#x}")
    print(f"  Match: {k_reconstructed == k_actual}")
else:
    print("No valid (d, m) pairs found!")

print()

# Compare with what minimum-m algorithm predicted
print("="*80)
print("COMPARISON WITH MINIMUM-M PREDICTION")
print("="*80)
print()

# The algorithm predicted: d=74, m=3
# But k74 doesn't exist in the known data, so it used k70 as reference

print("Minimum-m algorithm predicted (from previous run): d=74, m=3")
print("This would require k74, which we don't have in database (it's a gap).")
print()

print("If we only consider d=1 to 70 (known values):")
if valid_pairs:
    d_min, m_min, _ = valid_pairs[0]
    print(f"  Minimum m: d={d_min}, m={m_min}")
    print(f"  This is a HUGE m-value! Not minimized at all!")

print()

# Check if there's a pattern in the d-value
print("="*80)
print("PATTERN ANALYSIS")
print("="*80)
print()

if valid_pairs:
    print("Distribution of d-values:")
    d_values = [d for d, _, _ in valid_pairs]
    print(f"  Min d: {min(d_values)}")
    print(f"  Max d: {max(d_values)}")
    print(f"  All d-values: {d_values[:20]}")

print()

# Check convergent pattern
print("Checking if d or m relate to convergent indices:")
import json
try:
    with open('/home/solo/LadderV3/kh-assist/data_for_csolver.json') as f:
        data = json.load(f)

    m_seq_known = data['m_seq']
    d_seq_known = data['d_seq']

    print("\nFor reference, known d and m sequences (n=2-70):")
    print(f"  Last 5 d-values: {d_seq_known[-5:]}")
    print(f"  Last 5 m-values: {m_seq_known[-5:]}")
except:
    pass
