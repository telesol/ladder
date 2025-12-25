#!/usr/bin/env python3
"""
Explore the divisibility structure more deeply.
Question: What determines which k[d] divide (2^n - adj[n])?
"""

import sqlite3
from math import gcd

# Load known k values
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id")
k = {}
for row in cursor.fetchall():
    k[int(row[0])] = int(row[1], 16)
conn.close()

print("="*70)
print("DIVISIBILITY STRUCTURE ANALYSIS")
print("="*70)

# For each n, compute the numerator and analyze its divisors
print("\n--- Numerator = 2^n - adj[n] = m[n] * k[d[n]] ---")
print("n    numerator           k[d]      m[n]   d[n]  prime factors of numerator")

for n in range(2, 31):
    if n not in k or n-1 not in k:
        continue

    adj_n = k[n] - 2*k[n-1]
    numerator = 2**n - adj_n

    # Find best d
    best_d, best_m, best_kd = None, None, 0
    for d in range(1, n):
        if d not in k or k[d] == 0:
            continue
        if numerator % k[d] == 0:
            m_d = numerator // k[d]
            if best_d is None or k[d] > best_kd:
                best_d, best_m, best_kd = d, m_d, k[d]

    # Simple factorization for small primes
    factors = []
    temp = abs(numerator)
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        count = 0
        while temp % p == 0:
            temp //= p
            count += 1
        if count > 0:
            factors.append(f"{p}^{count}" if count > 1 else str(p))
    if temp > 1:
        factors.append(f"...{temp}")

    print(f"{n:2d}   {numerator:18d}   {best_kd:8d}  {best_m:8d}  {best_d:4d}  {' * '.join(factors)}")

# Now check: is there a pattern in GCD(numerator, k[d]) for various d?
print("\n" + "="*70)
print("GCD ANALYSIS: gcd(2^n - adj[n], k[d]) for each d")
print("="*70)

for n in range(4, 16):
    if n not in k or n-1 not in k:
        continue

    adj_n = k[n] - 2*k[n-1]
    numerator = 2**n - adj_n

    print(f"\nn={n}: numerator = {numerator}")
    gcds = []
    for d in range(1, n):
        if d in k:
            g = gcd(abs(numerator), k[d])
            is_divisor = "DIVIDES" if g == k[d] else ""
            gcds.append((d, k[d], g, is_divisor))

    for d, kd, g, div in gcds:
        print(f"  d={d}: k[{d}]={kd:6d}, gcd={g:6d} {div}")

# Check if k[n] values have special structure
print("\n" + "="*70)
print("K[N] STRUCTURE ANALYSIS")
print("="*70)

print("\nn    k[n]           binary                              bits  trailing_zeros")
for n in range(1, 31):
    if n not in k:
        continue
    kn = k[n]
    binary = bin(kn)[2:]
    bits = len(binary)
    trailing = len(binary) - len(binary.rstrip('0'))
    print(f"{n:2d}   {kn:12d}   {binary:>35s}   {bits:2d}   {trailing}")

# Check odd/even pattern
print("\n--- Odd/Even pattern of k[n] ---")
pattern = ""
for n in range(1, 71):
    if n in k:
        pattern += "O" if k[n] % 2 == 1 else "E"
print(f"Pattern: {pattern}")

# Check divisibility by small primes
print("\n--- k[n] mod small primes ---")
print("n    k[n]         mod3  mod7  mod11  mod13")
for n in range(1, 21):
    if n in k:
        print(f"{n:2d}   {k[n]:12d}   {k[n]%3:3d}  {k[n]%7:3d}  {k[n]%11:4d}  {k[n]%13:4d}")
