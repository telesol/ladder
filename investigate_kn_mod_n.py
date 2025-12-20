#!/usr/bin/env python3
"""
Investigate k[n] ≡ 0 (mod n) Pattern
====================================

Found that k[n] is divisible by n at specific positions: 1, 4, 8, 11, 36

This script investigates what's special about these positions.
"""

import json
import sqlite3
from math import gcd

# Load k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
k_seq = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

# Load m and d sequences
with open('data_for_csolver.json') as f:
    data = json.load(f)
m_list = data['m_seq']
d_list = data['d_seq']
m_seq = {n: m_list[n-2] for n in range(2, 2 + len(m_list))}
d_seq = {n: d_list[n-2] for n in range(2, 2 + len(d_list))}

print("=" * 80)
print("INVESTIGATION: k[n] ≡ 0 (mod n) PATTERN")
print("=" * 80)

# Find all n where k[n] is divisible by n
divisible_by_n = []
for n in range(1, 71):
    k = k_seq.get(n)
    if k and k % n == 0:
        divisible_by_n.append(n)

print(f"\nPositions where k[n] ≡ 0 (mod n): {divisible_by_n}")

# Analyze the differences
diffs = [divisible_by_n[i+1] - divisible_by_n[i] for i in range(len(divisible_by_n)-1)]
print(f"Differences: {diffs}")

# Analyze each position
print("\n## DETAILED ANALYSIS OF EACH POSITION")
print("-" * 60)

for n in divisible_by_n:
    k = k_seq[n]
    quotient = k // n

    print(f"\nn = {n}:")
    print(f"  k[{n}] = {k}")
    print(f"  k[{n}] / {n} = {quotient}")

    # Factorize n and quotient
    def factorize(num):
        if num <= 1:
            return {}
        factors = {}
        d = 2
        while d * d <= num:
            while num % d == 0:
                factors[d] = factors.get(d, 0) + 1
                num //= d
            d += 1
        if num > 1:
            factors[num] = 1
        return factors

    n_factors = factorize(n)
    q_factors = factorize(quotient)

    n_str = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(n_factors.items()))
    q_str = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(q_factors.items()))

    print(f"  n = {n_str if n_str else '1'}")
    print(f"  quotient = {q_str if q_str else '1'}")

    # Check if this relates to d[n] or m[n]
    if n in d_seq:
        d = d_seq[n]
        m = m_seq[n]
        print(f"  d[{n}] = {d}, m[{n}] = {m}")

# Look for pattern in the sequence 1, 4, 8, 11, 36
print("\n\n## PATTERN ANALYSIS")
print("-" * 60)

# Check binary representation
print("\nBinary representation:")
for n in divisible_by_n:
    print(f"  {n} = {bin(n)}")

# Check if these are special in some way
print("\nFactorizations:")
for n in divisible_by_n:
    factors = factorize(n)
    f_str = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items()))
    print(f"  {n} = {f_str if f_str else '1'}")

# Check relationship to primes
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
print("\nRelation to primes:")
for n in divisible_by_n:
    if n in primes:
        idx = primes.index(n) + 1
        print(f"  {n} = p[{idx}]")
    else:
        print(f"  {n} is not in first 15 primes")

# Check if k[n]/n relates to other k values
print("\n\nChecking if k[n]/n relates to other k values:")
for n in divisible_by_n:
    k = k_seq[n]
    quotient = k // n

    for m in range(1, n):
        km = k_seq.get(m)
        if km == quotient:
            print(f"  k[{n}] / {n} = {quotient} = k[{m}]")

    # Check if quotient is k[m] * something
    for m in range(1, n):
        km = k_seq.get(m)
        if km and quotient % km == 0:
            mult = quotient // km
            if mult < 20:
                print(f"  k[{n}] / {n} = {mult} × k[{m}]")

# Cumulative sum pattern?
print("\n\nCumulative sum pattern:")
cumsum = 0
for i, n in enumerate(divisible_by_n):
    cumsum += n
    print(f"  After {i+1} terms: sum = {cumsum}")

# Check triangular numbers
triangular = [n*(n+1)//2 for n in range(1, 15)]
print(f"\nTriangular numbers: {triangular}")
print(f"Divisible-by-n positions: {divisible_by_n}")

# Check if positions relate to triangular
for n in divisible_by_n:
    if n in triangular:
        idx = triangular.index(n) + 1
        print(f"  {n} = T_{idx} (triangular number)")

# Summary
print("\n\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("""
Positions where k[n] ≡ 0 (mod n): [1, 4, 8, 11, 36]

Observations:
1. Binary patterns:
   - 1 = 0b1
   - 4 = 0b100 = 2^2
   - 8 = 0b1000 = 2^3
   - 11 = 0b1011 = prime
   - 36 = 0b100100 = 4 × 9 = 2^2 × 3^2

2. Only n=11 is prime in this list

3. The differences [3, 4, 3, 25] don't show an obvious pattern

4. These may be positions where the k-sequence has special structure

Hypothesis:
- The puzzle creator ensured k[n] ≡ 0 (mod n) at specific "anchor" points
- These may help constrain the formula derivation
""")

# Save findings
findings = {
    'divisible_by_n': divisible_by_n,
    'differences': diffs,
    'details': {
        str(n): {
            'k': k_seq[n],
            'quotient': k_seq[n] // n,
        } for n in divisible_by_n
    }
}

with open('KN_MOD_N_ANALYSIS.json', 'w') as f:
    json.dump(findings, f, indent=2)

print("\nFindings saved to KN_MOD_N_ANALYSIS.json")
