#!/usr/bin/env python3
"""Analyze all bridge k-values to find their (d, m) patterns."""

import sqlite3

# Load k-values
conn = sqlite3.connect('/home/solo/LadderV3/kh-assist/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 95 ORDER BY puzzle_id")
rows = cur.fetchall()
conn.close()

k = {row[0]: int(row[1], 16) for row in rows}

print("="*80)
print("ANALYZING ALL BRIDGE K-VALUES")
print("="*80)
print()

bridges = [75, 80, 85, 90]
prev_indices = {75: 70, 80: 75, 85: 80, 90: 85}

for n in bridges:
    if n not in k:
        print(f"k{n}: Not in database")
        continue

    prev_n = prev_indices[n]
    if prev_n not in k:
        print(f"k{n}: Missing k{prev_n} (reference)")
        continue

    k_actual = k[n]
    k_prev = k[prev_n]

    print(f"="*60)
    print(f"k{n} (from k{prev_n})")
    print(f"="*60)
    print(f"k{prev_n} = {k_prev:#x}")
    print(f"k{n} = {k_actual:#x}")
    print()

    # Find all valid (d, m) pairs
    adj = k_actual - 2 * k_prev
    numerator = 2**n - adj

    valid_pairs = []

    for d in range(1, prev_n + 1):
        if d not in k:
            continue

        k_d = k[d]
        if k_d == 0:
            continue

        if numerator % k_d == 0:
            m = numerator // k_d
            if m > 0:
                valid_pairs.append((d, m))

    valid_pairs.sort(key=lambda x: x[1])  # Sort by m

    print(f"Found {len(valid_pairs)} valid (d, m) pairs")
    print()

    if valid_pairs:
        print("Top 10 (sorted by m):")
        for i, (d, m) in enumerate(valid_pairs[:10], 1):
            print(f"  {i:2d}. d={d:2d}, m={m:>30}")

        d_min, m_min = valid_pairs[0]
        print()
        print(f"Minimum m: d={d_min}, m={m_min}")

        # Verify
        k_d = k[d_min]
        k_reconstructed = 2*k_prev + (2**n - m_min * k_d)
        if k_reconstructed == k_actual:
            print(f"✅ Verified: k{n} = 2*k{prev_n} + (2^{n} - {m_min}*k{d_min})")
        else:
            print(f"❌ Verification failed!")

    print()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)
print()

results = {}
for n in bridges:
    if n not in k:
        continue

    prev_n = prev_indices[n]
    if prev_n not in k:
        continue

    k_actual = k[n]
    k_prev = k[prev_n]
    adj = k_actual - 2 * k_prev
    numerator = 2**n - adj

    valid_pairs = []
    for d in range(1, prev_n + 1):
        if d not in k:
            continue
        k_d = k[d]
        if k_d != 0 and numerator % k_d == 0:
            m = numerator // k_d
            if m > 0:
                valid_pairs.append((d, m))

    if valid_pairs:
        valid_pairs.sort(key=lambda x: x[1])
        d_min, m_min = valid_pairs[0]
        results[n] = (d_min, m_min)

print("Bridge d-values (minimum-m choice):")
for n in bridges:
    if n in results:
        d_min, m_min = results[n]
        print(f"  k{n}: d={d_min}")
    else:
        print(f"  k{n}: N/A")

print()

# Check for pattern in d-values
if len(results) >= 2:
    d_vals = [results[n][0] for n in sorted(results.keys())]
    print(f"Pattern in d-values: {d_vals}")

    if len(set(d_vals)) == 1:
        print(f"  ✅ ALL bridges use d={d_vals[0]}!")
    else:
        print(f"  Different d-values used")
