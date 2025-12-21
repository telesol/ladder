#!/usr/bin/env python3
"""
PROPER VERIFICATION: Use actual database k values to test greedy rule
Hypothesis: d[n] = argmin over i<n of ceil(2^n / k[i])
            m[n] = ceil(2^n / k[d[n]])
"""

import sqlite3
import json

def ceil_div(a, b):
    return (a + b - 1) // b

# Load known k-values from DATABASE
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
K = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

# Load stored m_seq and d_seq
with open('/home/solo/LA/data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq_stored = data['m_seq']  # Index 0 = n=2
d_seq_stored = data['d_seq']

print("=" * 100)
print("TESTING GREEDY HYPOTHESIS WITH DATABASE K VALUES")
print("Hypothesis: d[n] = argmin ceil(2^n/k[i]), m[n] = ceil(2^n/k[d[n]])")
print("=" * 100)

d_matches = 0
m_matches = 0
both_match = 0

for n in range(2, 71):
    power_2n = 2 ** n

    # Find argmin ceil(2^n / k[i]) over all i < n
    best_d = None
    best_m = float('inf')

    for i in range(1, n):
        if i in K:
            m_candidate = ceil_div(power_2n, K[i])
            if m_candidate < best_m:
                best_m = m_candidate
                best_d = i

    d_computed = best_d
    m_computed = best_m

    # Get stored values
    m_stored = m_seq_stored[n-2]
    d_stored = d_seq_stored[n-2]

    d_ok = d_computed == d_stored
    m_ok = m_computed == m_stored

    if d_ok:
        d_matches += 1
    if m_ok:
        m_matches += 1
    if d_ok and m_ok:
        both_match += 1

    status = "✓" if (d_ok and m_ok) else "✗"

    if n <= 20 or not (d_ok and m_ok):
        print(f"n={n:2d}: d_comp={d_computed:2d} d_stored={d_stored:2d} {'✓' if d_ok else '✗'} | "
              f"m_comp={m_computed:15,d} m_stored={m_stored:15,d} {'✓' if m_ok else '✗'} | {status}")

print()
print("=" * 100)
print(f"RESULTS:")
print(f"  d[n] matches: {d_matches}/69 ({100*d_matches/69:.1f}%)")
print(f"  m[n] matches: {m_matches}/69 ({100*m_matches/69:.1f}%)")
print(f"  Both match:   {both_match}/69 ({100*both_match/69:.1f}%)")
print("=" * 100)

if both_match == 69:
    print("\n🎉 GREEDY RULE VERIFIED! The formula is:")
    print("   d[n] = argmin over i<n of ceil(2^n / k[i])")
    print("   m[n] = ceil(2^n / k[d[n]])")
