#!/usr/bin/env python3
"""
Deep analysis of d-sequence to find the generation rule.
d[n] determines which previous k is used in the formula.
"""

import sqlite3
import json
from collections import Counter

# Load data
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
K = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

with open('/home/solo/LA/data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']  # Index 0 = n=2
d_seq = data['d_seq']

print("=" * 100)
print("D-SEQUENCE DEEP ANALYSIS")
print("=" * 100)

# Basic distribution
d_counter = Counter(d_seq)
print("\n1. D-VALUE DISTRIBUTION:")
for d, count in sorted(d_counter.items()):
    print(f"   d={d}: {count} times ({100*count/len(d_seq):.1f}%)")

# Look at which n uses which d
print("\n2. WHICH N USES WHICH D:")
for d in sorted(set(d_seq)):
    ns = [i+2 for i, x in enumerate(d_seq) if x == d]
    print(f"   d={d}: n = {ns[:20]}{'...' if len(ns) > 20 else ''}")

# Check relationship between d[n] and n
print("\n3. D[N] VS N RELATIONSHIP:")
for i, n in enumerate(range(2, 15)):
    d = d_seq[i]
    m = m_seq[i]
    power_2n = 2**n
    k_d = K[d]
    ratio = power_2n / k_d
    adj = power_2n - m * k_d
    print(f"   n={n:2d}: d={d}, m={m:6d}, 2^n={power_2n:6d}, k[d]={k_d:5d}, 2^n/k[d]={ratio:10.2f}, adj={adj:6d}")

# Check if d relates to binary representation of n
print("\n4. D[N] VS BINARY OF N:")
for i, n in enumerate(range(2, 25)):
    d = d_seq[i]
    print(f"   n={n:2d} ({bin(n):>8s}): d={d} ({bin(d):>8s})")

# Check if d relates to factors of n
print("\n5. D[N] VS FACTORS/PROPERTIES OF N:")
def factors(n):
    return [i for i in range(1, n+1) if n % i == 0]

for i, n in enumerate(range(2, 25)):
    d = d_seq[i]
    f = factors(n)
    is_prime = len(f) == 2
    print(f"   n={n:2d}: d={d}, prime={is_prime}, factors={f}")

# Check if there's a pattern with n mod something
print("\n6. D[N] VS N MOD K:")
for mod in [2, 3, 4, 5, 6, 7, 8]:
    print(f"\n   n mod {mod}:")
    for r in range(mod):
        ns = [n for n in range(2, 71) if n % mod == r]
        ds = [d_seq[n-2] for n in ns if n-2 < len(d_seq)]
        d_dist = Counter(ds)
        print(f"      r={r}: d_distribution = {dict(d_dist)}")

# Check if d[n] = n - some_offset
print("\n7. D[N] AS N - OFFSET:")
for i, n in enumerate(range(2, 25)):
    d = d_seq[i]
    offset = n - d
    print(f"   n={n:2d}: d={d}, n-d={offset}")

# Look for recurrence in d itself
print("\n8. D-SEQUENCE DIFFERENCES:")
print(f"   d: {d_seq[:20]}")
d_diff = [d_seq[i+1] - d_seq[i] for i in range(len(d_seq)-1)]
print(f"   Δd: {d_diff[:20]}")

# Check if d relates to position of highest set bit
print("\n9. D[N] VS BIT POSITION:")
def highest_bit_pos(x):
    return x.bit_length() - 1 if x > 0 else 0

for i, n in enumerate(range(2, 25)):
    d = d_seq[i]
    m = m_seq[i]
    hb_n = highest_bit_pos(n)
    hb_m = highest_bit_pos(m)
    hb_d = highest_bit_pos(d)
    print(f"   n={n:2d}: d={d}, m={m:6d}, hb(n)={hb_n}, hb(m)={hb_m}, hb(d)={hb_d}")
