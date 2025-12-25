#!/usr/bin/env python3
"""Test if d[n] is always the divisor with largest k[d]."""

import sqlite3

# Load k values
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id")
k = {}
for row in cursor.fetchall():
    k[int(row[0])] = int(row[1], 16)
conn.close()

print(f"Testing hypothesis: d[n] = argmax{{d : k[d] | (2^n - adj[n])}}")
print(f"Loaded {len(k)} keys")
print("="*70)

matches = 0
mismatches = 0
details = []

for n in sorted(k.keys()):
    if n <= 1 or n-1 not in k:
        continue

    adj_n = k[n] - 2 * k[n-1]
    numerator = 2**n - adj_n

    # Find all valid d's (where k[d] divides numerator)
    valid_d = []
    for d in range(1, n):
        if d not in k or k[d] == 0:
            continue
        if numerator % k[d] == 0:
            m_d = numerator // k[d]
            valid_d.append((d, k[d], m_d))

    if not valid_d:
        continue

    # Find d with largest k[d]
    largest_d = max(valid_d, key=lambda x: x[1])

    # Find actual d (minimal |m|)
    actual_d = min(valid_d, key=lambda x: abs(x[2]))

    # Do they match?
    if largest_d[0] == actual_d[0]:
        matches += 1
        result = "MATCH"
    else:
        mismatches += 1
        result = "MISMATCH"
        details.append({
            'n': n,
            'largest_d': largest_d,
            'actual_d': actual_d,
            'all_valid': valid_d
        })

    if n <= 20 or result == "MISMATCH":
        print(f"n={n:3d}: {result}")
        print(f"       largest k[d]: d={largest_d[0]}, k[d]={largest_d[1]}, m={largest_d[2]}")
        print(f"       minimal |m|:  d={actual_d[0]}, k[d]={actual_d[1]}, m={actual_d[2]}")

print("="*70)
print(f"RESULTS: {matches} matches, {mismatches} mismatches")
print(f"Hypothesis success rate: {100*matches/(matches+mismatches):.1f}%")

if mismatches > 0:
    print(f"\nMISMATCH ANALYSIS:")
    for d in details[:5]:
        print(f"  n={d['n']}: largest_d={d['largest_d'][0]}, actual_d={d['actual_d'][0]}")
        print(f"    All valid d's: {[(x[0], x[1], x[2]) for x in d['all_valid'][:5]]}")
