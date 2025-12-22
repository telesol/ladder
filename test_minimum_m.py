#!/usr/bin/env python3
"""Check if d[n] is chosen to minimize m[n]."""

import json
import sqlite3

# Load m and d sequences
with open('/home/solo/LadderV3/kh-assist/data_for_csolver.json') as f:
    data = json.load(f)

m_list = data['m_seq']
d_list = data['d_seq']
m_seq = {n: m_list[n-2] for n in range(2, 2 + len(m_list))}
d_seq = {n: d_list[n-2] for n in range(2, 2 + len(d_list))}

# Load k values from database
conn = sqlite3.connect('/home/solo/LadderV3/kh-assist/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70")
k_seq = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

print("="*80)
print("HYPOTHESIS: d[n] is chosen to MINIMIZE m[n]")
print("="*80)
print()

matches = 0
total = 0

for n in range(2, 71):
    if n not in k_seq or n-1 not in k_seq:
        continue

    k_n = k_seq[n]
    k_prev = k_seq[n-1]
    adj = k_n - 2 * k_prev

    # Find all valid (d, m) pairs
    valid_pairs = []
    for d_candidate in range(1, n):
        if d_candidate not in k_seq:
            continue
        k_d = k_seq[d_candidate]
        numerator = 2**n - adj
        if numerator % k_d == 0:
            m_candidate = numerator // k_d
            if m_candidate > 0:
                valid_pairs.append((d_candidate, m_candidate))

    if not valid_pairs:
        continue

    total += 1

    # Find the pair with minimum m
    min_m_pair = min(valid_pairs, key=lambda x: x[1])
    actual_d = d_seq[n]
    actual_m = m_seq[n]

    # Check if actual matches minimum
    is_minimum = (actual_d, actual_m) == min_m_pair

    if is_minimum:
        matches += 1
        status = "✓ MINIMUM"
    else:
        status = f"✗ minimum would be d={min_m_pair[0]}, m={min_m_pair[1]}"

    if len(valid_pairs) > 1:  # Only show when there's a choice
        print(f"n={n:2d}: actual (d={actual_d}, m={actual_m:>12}), valid pairs: {valid_pairs[:5]}")
        print(f"       {status}")
        print()

print("="*80)
print(f"RESULT: {matches}/{total} cases where actual d gives minimum m ({100*matches/total:.1f}%)")
print("="*80)
