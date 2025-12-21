#!/usr/bin/env python3
"""
Test: Start with k[1]=1, k[2]=3, k[3]=7 and apply greedy rule.
Does this generate the correct k[4..70]?
"""

import sqlite3

def ceil_div(a, b):
    return (a + b - 1) // b

# Load actual k-values
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
K_DB = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

print("=" * 80)
print("TESTING SEEDED GREEDY: k[1]=1, k[2]=3, k[3]=7 then greedy")
print("=" * 80)

# Seed with actual first 3 values
K = {1: 1, 2: 3, 3: 7}

matches = 0
mismatches = 0

for n in range(4, 71):
    power_2n = 2 ** n

    # Greedy: find d that minimizes ceil(2^n / k[d])
    best_d = None
    best_m = float('inf')

    for d in range(1, n):
        if d in K:
            m_candidate = ceil_div(power_2n, K[d])
            if m_candidate < best_m:
                best_m = m_candidate
                best_d = d

    d_n = best_d
    m_n = best_m

    # Compute adj and k[n]
    adj_n = power_2n - m_n * K[d_n]
    k_n = 2 * K[n-1] + adj_n
    K[n] = k_n

    # Compare with database
    k_db = K_DB.get(n)
    match = (k_n == k_db)

    if match:
        matches += 1
    else:
        mismatches += 1

    status = "✓" if match else "✗"

    if n <= 15 or not match:
        print(f"n={n:2d}: d={d_n}, m={m_n:,}, k_computed={k_n:,}, k_db={k_db:,} {status}")

print()
print("=" * 80)
print(f"RESULTS: {matches}/67 matches (n=4..70)")
print("=" * 80)

if matches == 67:
    print("\n🎉 SEEDED GREEDY WORKS! Computing k[71]...")

    n = 71
    power_2n = 2 ** n

    best_d = None
    best_m = float('inf')

    for d in range(1, n):
        m_candidate = ceil_div(power_2n, K[d])
        if m_candidate < best_m:
            best_m = m_candidate
            best_d = d

    adj_71 = power_2n - best_m * K[best_d]
    k_71 = 2 * K[70] + adj_71

    print(f"\nd[71] = {best_d}")
    print(f"m[71] = {best_m:,}")
    print(f"k[71] = {k_71:,}")
    print(f"k[71] hex = {hex(k_71)}")
