#!/usr/bin/env python3
"""
VERIFY THE GREEDY RULE:
m[n] = ceil(2^n / k[d[n]])
d[n] = argmin over i<n of ceil(2^n / k[i])
"""

import sqlite3
import math
import json

# Load known k-values
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
K_DB = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

# Load m_seq and d_seq for comparison
with open('/home/solo/LA/data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq_stored = data['m_seq']  # Index 0 = n=2
d_seq_stored = data['d_seq']

def ceil_div(a, b):
    return (a + b - 1) // b

print("=" * 80)
print("VERIFYING GREEDY RULE: m[n] = ceil(2^n / k[d[n]])")
print("=" * 80)

# Compute k[n] using the greedy rule
K = {1: 1}  # Start with k[1] = 1

matches = 0
mismatches = 0

for n in range(2, 71):
    # Step 1: Find d[n] = argmin of ceil(2^n / k[i])
    power_2n = 2 ** n
    best_d = None
    best_m = float('inf')
    
    for i in range(1, n):
        if i in K:
            m_candidate = ceil_div(power_2n, K[i])
            if m_candidate < best_m:
                best_m = m_candidate
                best_d = i
    
    d_n = best_d
    m_n = best_m
    
    # Step 2: Compute adj[n]
    adj_n = power_2n - m_n * K[d_n]
    
    # Step 3: Compute k[n]
    k_n = 2 * K[n-1] + adj_n
    K[n] = k_n
    
    # Compare with stored values
    m_stored = m_seq_stored[n-2] if n-2 < len(m_seq_stored) else None
    d_stored = d_seq_stored[n-2] if n-2 < len(d_seq_stored) else None
    k_db = K_DB.get(n)
    
    if m_n == m_stored and k_n == k_db:
        matches += 1
        status = "✓"
    else:
        mismatches += 1
        status = "✗"
    
    if n <= 15 or n >= 65 or status == "✗":
        print(f"n={n:2d}: m={m_n:20,} d={d_n} k={k_n:30,} | stored m={m_stored} d={d_stored} | DB k={k_db} {status}")

print("\n" + "=" * 80)
print(f"RESULTS: {matches} matches, {mismatches} mismatches out of 69")
print("=" * 80)

if mismatches == 0:
    print("\n🎉 RULE VERIFIED 100%! 🎉")
    print("\nNow computing m[71]...")
    
    # Compute m[71]
    power_71 = 2 ** 71
    best_d = None
    best_m = float('inf')
    
    for i in range(1, 71):
        if i in K:
            m_candidate = ceil_div(power_71, K[i])
            if m_candidate < best_m:
                best_m = m_candidate
                best_d = i
    
    print(f"\nm[71] = {best_m:,}")
    print(f"d[71] = {best_d}")
    print(f"k[d[71]] = k[{best_d}] = {K[best_d]:,}")
    
    # Compute k[71]
    adj_71 = power_71 - best_m * K[best_d]
    k_71 = 2 * K[70] + adj_71
    
    print(f"\nadj[71] = {adj_71:,}")
    print(f"k[71] = 2*k[70] + adj[71] = {k_71:,}")
    print(f"k[71] hex = {hex(k_71)}")
