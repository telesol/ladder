#!/usr/bin/env python3
"""
Explore multiplicative relationships in k[n] sequence.
Can k[n] be expressed as products/powers of earlier k values?
"""

import sqlite3
from math import gcd, isqrt

# Load known k values
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id")
k = {}
for row in cursor.fetchall():
    k[int(row[0])] = int(row[1], 16)
conn.close()

print("="*70)
print("MULTIPLICATIVE STRUCTURE IN K[N]")
print("="*70)

# For each k[n], check if it's a product of earlier k values
print("\n--- Check: k[n] = k[i] × k[j] for some i,j < n ---")
for n in range(4, 31):
    if n not in k:
        continue
    kn = k[n]

    found = []
    for i in range(1, n):
        if i not in k:
            continue
        for j in range(i, n):
            if j not in k:
                continue
            if k[i] * k[j] == kn:
                found.append(f"k[{i}] × k[{j}] = {k[i]} × {k[j]}")

    if found:
        print(f"k[{n}] = {kn}: {found}")

# Check for k[n] = k[i]^2
print("\n--- Check: k[n] = k[i]² for some i < n ---")
for n in range(4, 31):
    if n not in k:
        continue
    kn = k[n]

    for i in range(1, n):
        if i not in k:
            continue
        if k[i] * k[i] == kn:
            print(f"k[{n}] = {kn} = k[{i}]² = {k[i]}²")

# Check for k[n] = 2^a × k[i]
print("\n--- Check: k[n] = 2^a × k[i] for some a, i < n ---")
for n in range(4, 31):
    if n not in k:
        continue
    kn = k[n]

    found = []
    for i in range(1, n):
        if i not in k or k[i] == 0:
            continue
        if kn % k[i] == 0:
            ratio = kn // k[i]
            # Check if ratio is power of 2
            if ratio > 0 and (ratio & (ratio - 1)) == 0:
                a = (ratio).bit_length() - 1
                found.append(f"2^{a} × k[{i}]")

    if found:
        print(f"k[{n}] = {kn}: {found}")

# Check for divisibility: k[n] divisible by k[i]
print("\n--- Divisibility: which k[i] divide k[n]? ---")
for n in range(4, 21):
    if n not in k:
        continue
    kn = k[n]

    divisors = []
    for i in range(1, n):
        if i in k and k[i] != 0 and kn % k[i] == 0:
            divisors.append((i, k[i], kn // k[i]))

    print(f"k[{n}] = {kn}: divisible by k[{[d[0] for d in divisors]}]")
    for d, ki, quot in divisors:
        print(f"       k[{n}] / k[{d}] = {kn} / {ki} = {quot}")

# Check relationship between consecutive k values
print("\n--- Ratios k[n]/k[n-1] ---")
for n in range(2, 31):
    if n in k and n-1 in k:
        ratio = k[n] / k[n-1]
        print(f"k[{n}]/k[{n-1}] = {k[n]}/{k[n-1]} = {ratio:.6f}")

# Check if k[n] - 2*k[n-1] (= adj[n]) has structure
print("\n--- adj[n] = k[n] - 2*k[n-1] factorization ---")
for n in range(2, 21):
    if n in k and n-1 in k:
        adj = k[n] - 2*k[n-1]

        # Factor adj
        factors = []
        temp = abs(adj)
        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
            while temp % p == 0:
                factors.append(p)
                temp //= p
        if temp > 1:
            factors.append(temp)

        sign = "+" if adj >= 0 else "-"
        print(f"adj[{n:2d}] = {sign}{abs(adj):10d} = {sign}{'×'.join(map(str, factors)) if factors else '0'}")

# Key insight: check GCD structure
print("\n--- GCD(k[n], k[m]) for m < n ---")
for n in range(4, 16):
    if n not in k:
        continue
    gcds = []
    for m in range(1, n):
        if m in k:
            g = gcd(k[n], k[m])
            if g > 1:
                gcds.append((m, g))
    print(f"GCDs with k[{n}]={k[n]}: {gcds}")
