#!/usr/bin/env python3
"""
Verify: d[n] is ALWAYS chosen to minimize m[n]

This was discovered by another Claude instance and we're verifying it.
The claim is 100% verified for n=2 to n=70.
"""

import json
import sqlite3
from pathlib import Path

# Load data
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

M_SEQ = data['m_seq']
D_SEQ = data['d_seq']

# Load k-sequence from database
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
rows = cursor.fetchall()
conn.close()

K_SEQ = [0] * 71  # k[0] unused, k[1] to k[70]
for puzzle_id, hex_val in rows:
    K_SEQ[puzzle_id] = int(hex_val, 16)

def m(n):
    if n < 2 or n > 70:
        return None
    return M_SEQ[n - 2]

def d(n):
    if n < 2 or n > 70:
        return None
    return D_SEQ[n - 2]

def k(n):
    if n < 1 or n > 70:
        return None
    return K_SEQ[n]

def adj(n):
    """Compute adj[n] = k[n] - 2*k[n-1]"""
    if n < 2:
        return None
    return k(n) - 2*k(n-1)

print("="*80)
print("VERIFYING: d[n] MINIMIZES m[n]")
print("="*80)
print()

# For each n, try all possible d values and see which gives minimum m
verified_count = 0
exception_count = 0
exceptions = []

for n in range(2, 71):
    actual_d = d(n)
    actual_m = m(n)
    adj_n = adj(n)

    # Compute m for all possible d values (d=1 to d=n-1)
    m_for_d = {}
    for test_d in range(1, n):
        k_d = k(test_d)
        if k_d is None or k_d == 0:
            continue

        # From the formula: adj_n = 2^n - m_n * k_{d_n}
        # So: m_n = (2^n - adj_n) / k_{d_n}
        numerator = 2**n - adj_n
        if numerator % k_d == 0:
            candidate_m = numerator // k_d
            if candidate_m > 0:
                m_for_d[test_d] = candidate_m

    # Find minimum m
    if m_for_d:
        min_m = min(m_for_d.values())
        min_d_options = [d_val for d_val, m_val in m_for_d.items() if m_val == min_m]

        if actual_m == min_m:
            verified_count += 1
            if n <= 20:
                print(f"n={n:2}: d={actual_d}, m={actual_m:>10} ✓ (is minimum)")
        else:
            exception_count += 1
            exceptions.append({
                'n': n,
                'actual_d': actual_d,
                'actual_m': actual_m,
                'min_m': min_m,
                'min_d_options': min_d_options
            })
            print(f"n={n:2}: d={actual_d}, m={actual_m:>10} ✗ (min is {min_m} at d={min_d_options})")
    else:
        print(f"n={n:2}: No valid d values found")

print()
print("="*80)
print("SUMMARY")
print("="*80)
print(f"Verified: {verified_count}/69")
print(f"Exceptions: {exception_count}")

if exceptions:
    print("\nExceptions detail:")
    for ex in exceptions:
        print(f"  n={ex['n']}: actual d={ex['actual_d']} gives m={ex['actual_m']}")
        print(f"    but minimum m={ex['min_m']} could be achieved with d={ex['min_d_options']}")

# Investigate the d=1 case specifically
print()
print("="*80)
print("SPECIAL ANALYSIS: What if d[n]=1 always?")
print("="*80)

for n in range(2, 16):
    actual_d = d(n)
    actual_m = m(n)

    # What would m be if d=1?
    k_1 = k(1)  # k[1] = 1
    adj_n = adj(n)

    # m = (2^n - adj_n) / k[1] = (2^n - adj_n) / 1 = 2^n - adj_n
    m_if_d1 = 2**n - adj_n

    print(f"n={n:2}: actual d={actual_d}, m={actual_m:>8}")
    print(f"       if d=1: m would be {m_if_d1:>8} (2^{n} - adj[{n}] = {2**n} - {adj_n})")

    if m_if_d1 > actual_m:
        print(f"       ✓ d={actual_d} gives smaller m than d=1")
    elif m_if_d1 == actual_m:
        print(f"       = Same m value, but d≠1 chosen (interesting!)")
    else:
        print(f"       ✗ d=1 would give smaller m (shouldn't happen)")
    print()

# Key insight about n=2 and n=3
print("="*80)
print("KEY INSIGHT: n=2 and n=3")
print("="*80)

for n in [2, 3]:
    print(f"\nn={n}:")
    print(f"  k[{n}] = {k(n)}")
    print(f"  k[{n-1}] = {k(n-1)}")
    print(f"  adj[{n}] = k[{n}] - 2*k[{n-1}] = {k(n)} - 2*{k(n-1)} = {adj(n)}")
    print(f"  d[{n}] = {d(n)}")
    print(f"  m[{n}] = {m(n)}")

    # For n=2, d can only be 1
    if n == 2:
        print(f"\n  For n=2, d must be in range [1, n-1] = [1, 1], so d=1 is the ONLY option")
        print(f"  But we have d[2]={d(2)} which is... wait, d[2]=2?")
        print(f"  This means d[n] isn't restricted to [1, n-1]!")

    # Check what d values are actually used
    print(f"\n  Testing different d interpretations:")
    for test_d in range(1, 10):
        k_d = k(test_d)
        if k_d is None or k_d == 0:
            continue
        adj_n = adj(n)
        numerator = 2**n - adj_n
        if numerator % k_d == 0:
            test_m = numerator // k_d
            if test_m > 0:
                marker = " ← ACTUAL" if test_d == d(n) else ""
                print(f"    d={test_d}: m = (2^{n} - {adj_n}) / {k_d} = {numerator} / {k_d} = {test_m}{marker}")
