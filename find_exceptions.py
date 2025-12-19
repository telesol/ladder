#!/usr/bin/env python3
"""Find the cases that don't follow minimum-m rule."""

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
print("FINDING EXCEPTIONS TO MINIMUM-M RULE")
print("="*80)
print()

exceptions = []

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

    # Find the pair with minimum m
    min_m_pair = min(valid_pairs, key=lambda x: x[1])
    actual_d = d_seq[n]
    actual_m = m_seq[n]

    # Check if actual matches minimum
    is_minimum = (actual_d, actual_m) == min_m_pair

    if not is_minimum and len(valid_pairs) > 1:
        exceptions.append({
            'n': n,
            'actual': (actual_d, actual_m),
            'minimum': min_m_pair,
            'valid_pairs': valid_pairs
        })

print(f"Found {len(exceptions)} exceptions:\n")

for e in exceptions:
    n = e['n']
    print(f"n={n}:")
    print(f"  Actual:  d={e['actual'][0]}, m={e['actual'][1]}")
    print(f"  Minimum: d={e['minimum'][0]}, m={e['minimum'][1]}")
    print(f"  All valid pairs: {e['valid_pairs']}")
    print()

# Also check which n values have only ONE valid pair (forced choice)
print("="*80)
print("N VALUES WITH ONLY ONE VALID PAIR (no choice)")
print("="*80)
forced = []
for n in range(2, 71):
    if n not in k_seq or n-1 not in k_seq:
        continue

    k_n = k_seq[n]
    k_prev = k_seq[n-1]
    adj = k_n - 2 * k_prev

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

    if len(valid_pairs) == 1:
        forced.append(n)

print(f"n values with only one valid pair: {forced}")
print(f"Count: {len(forced)}")
