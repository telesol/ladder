#!/usr/bin/env python3
"""
TEST: Can we generate k[1..70] from scratch using the greedy rule?
If yes, we can compute k[71] directly!
"""

import sqlite3

def ceil_div(a, b):
    return (a + b - 1) // b

# Load actual k-values from database
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
K_DB = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

print("=" * 80)
print("GENERATING K-SEQUENCE FROM SCRATCH USING GREEDY RULE")
print("=" * 80)

# Start with k[1] = 1
K = {1: 1}

matches = 0
mismatches = 0

for n in range(2, 71):
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
        print(f"n={n:2d}: d={d_n}, m={m_n:,}")
        print(f"       k_computed = {k_n:,}")
        print(f"       k_database = {k_db:,}")
        print(f"       {status}")
        print()

print("=" * 80)
print(f"RESULTS: {matches}/69 matches, {mismatches}/69 mismatches")
print("=" * 80)

if matches == 69:
    print("\n🎉 GREEDY RULE GENERATES THE SEQUENCE! 🎉")
    print("\nComputing k[71]...")

    n = 71
    power_2n = 2 ** n

    best_d = None
    best_m = float('inf')

    for d in range(1, n):
        if d in K:
            m_candidate = ceil_div(power_2n, K[d])
            if m_candidate < best_m:
                best_m = m_candidate
                best_d = d

    d_71 = best_d
    m_71 = best_m
    adj_71 = power_2n - m_71 * K[d_71]
    k_71 = 2 * K[70] + adj_71

    print(f"\nd[71] = {d_71}")
    print(f"m[71] = {m_71:,}")
    print(f"adj[71] = {adj_71:,}")
    print(f"k[71] = {k_71:,}")
    print(f"k[71] hex = {hex(k_71)}")
