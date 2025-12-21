#!/usr/bin/env python3
"""
HYPOTHESIS: d[n] is chosen such that k[d[n]] divides (2^n - adj[n])
where adj[n] = k[n] - 2*k[n-1]

And among valid divisors, d[n] is the one that minimizes m[n].
"""

import sqlite3
import json
from math import gcd

# Load data
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
K = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

with open('/home/solo/LA/data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']
d_seq = data['d_seq']

print("=" * 100)
print("TESTING DIVISIBILITY HYPOTHESIS")
print("d[n] is chosen such that k[d[n]] divides (2^n - adj[n])")
print("=" * 100)

matches = 0
divisor_found = 0

for n in range(2, 71):
    power_2n = 2 ** n
    k_n = K[n]
    k_prev = K.get(n-1, 0)
    adj_n = k_n - 2 * k_prev

    target = power_2n - adj_n  # This is what needs to be m*k[d]

    d_stored = d_seq[n-2]
    m_stored = m_seq[n-2]

    # Find all d < n where k[d] divides target
    valid_divisors = []
    for d in range(1, n):
        if d in K:
            if target % K[d] == 0:
                m_candidate = target // K[d]
                valid_divisors.append((d, m_candidate))

    # Check if stored d is among valid divisors
    is_valid = any(d == d_stored for d, m in valid_divisors)

    # Find minimum m among valid divisors
    if valid_divisors:
        min_m_entry = min(valid_divisors, key=lambda x: x[1])
        min_m_d, min_m = min_m_entry
        is_minimum = (d_stored == min_m_d and m_stored == min_m)
    else:
        min_m_d, min_m = None, None
        is_minimum = False

    if is_valid:
        divisor_found += 1
    if is_minimum:
        matches += 1

    status = "✓" if is_minimum else "✗"

    if n <= 15 or not is_minimum:
        print(f"n={n:2d}: adj={adj_n:15,d}, target={target:25,d}")
        print(f"       valid_divisors = {valid_divisors[:5]}{'...' if len(valid_divisors) > 5 else ''}")
        print(f"       stored: d={d_stored}, m={m_stored:20,d}")
        print(f"       min_m:  d={min_m_d}, m={min_m if min_m else 'N/A'} {status}")
        print()

print("=" * 100)
print(f"RESULTS:")
print(f"  d[n] divides target: {divisor_found}/69 ({100*divisor_found/69:.1f}%)")
print(f"  d[n] gives min m:    {matches}/69 ({100*matches/69:.1f}%)")
print("=" * 100)

if matches == 69:
    print("\n🎉 FORMULA FOUND! 🎉")
    print("d[n] = argmin{m : k[d] divides (2^n - adj[n])}")
    print("m[n] = (2^n - adj[n]) / k[d[n]]")
