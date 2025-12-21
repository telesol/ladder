#!/usr/bin/env python3
"""
Investigate n=2 and n=3 base cases
These are special because we're defining k[n] at the same time
"""

import sqlite3
import json

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

print("=" * 80)
print("BASE CASE ANALYSIS: n=2 and n=3")
print("=" * 80)

for n in [2, 3]:
    print(f"\n{'='*40}")
    print(f"n = {n}")
    print(f"{'='*40}")

    power_2n = 2 ** n
    k_n = K[n]
    k_prev = K.get(n-1, 0)
    adj_n = k_n - 2 * k_prev

    d_stored = d_seq[n-2]
    m_stored = m_seq[n-2]

    print(f"2^{n} = {power_2n}")
    print(f"k[{n}] = {k_n}")
    print(f"k[{n-1}] = {k_prev}")
    print(f"adj[{n}] = k[{n}] - 2*k[{n-1}] = {k_n} - 2*{k_prev} = {adj_n}")
    print(f"target = 2^{n} - adj[{n}] = {power_2n} - {adj_n} = {power_2n - adj_n}")
    print()
    print(f"Stored: d[{n}] = {d_stored}, m[{n}] = {m_stored}")
    print()

    # Check if stored values are consistent
    # m[n] * k[d[n]] = target
    k_d = K.get(d_stored)
    if k_d:
        computed_target = m_stored * k_d
        print(f"m[{n}] * k[d[{n}]] = {m_stored} * {k_d} = {computed_target}")
        print(f"Expected target = {power_2n - adj_n}")
        print(f"Match: {computed_target == power_2n - adj_n}")
    else:
        print(f"k[{d_stored}] not available yet (self-referential!)")

    # For n=2: d=2 means k[2] is used before it's defined
    # This suggests d=n is the bootstrap convention
    if d_stored == n:
        print()
        print(f"SPECIAL: d[{n}] = {n} (self-reference!)")
        print("This means the formula m[n]*k[d[n]] = target is being solved for k[n] itself!")
        print(f"From target = m[{n}]*k[{n}]:")
        print(f"  {power_2n - adj_n} = {m_stored} * k[{n}]")
        print(f"  k[{n}] = {(power_2n - adj_n) // m_stored}")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("""
For n=2,3: d[n] = n is a BOOTSTRAP convention.
Instead of choosing d to minimize m, the formula defines k[n] directly:

  adj[n] = k[n] - 2*k[n-1]
  2^n - adj[n] = m[n] * k[n]   (using d[n]=n)
  2^n - k[n] + 2*k[n-1] = m[n] * k[n]
  2^n + 2*k[n-1] = k[n] * (m[n] + 1)
  k[n] = (2^n + 2*k[n-1]) / (m[n] + 1)

For n=2: k[2] = (4 + 2*1) / (1+1) = 6/2 = 3 ✓
For n=3: k[3] = (8 + 2*3) / (1+1) = 14/2 = 7 ✓
""")
