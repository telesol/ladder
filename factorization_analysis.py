#!/usr/bin/env python3
"""
Complete factorization analysis of m[62], m[65], m[68].
Looking for convergent patterns and mathematical relationships.

MODEL: Claude Opus 4.5
DATE: 2025-12-20
"""

import json
from math import gcd, sqrt

# Verified prime factorizations (from GNU factor)
factorizations = {
    62: [2, 3, 281, 373, 2843, 10487, 63199],
    65: [24239, 57283, 1437830129],
    68: [5, 1153, 1861, 31743327447619]
}

# Convergents of mathematical constants
# π convergents: p/q where p is numerator, q is denominator
pi_convergents = {
    'num': [3, 22, 333, 355, 103993, 104348, 208341, 312689, 833719, 1146408,
            4272943, 5419351, 80143857, 165707065, 245850922, 411557987,
            1068966896, 2549491779, 6167950454, 14885392687],
    'den': [1, 7, 106, 113, 33102, 33215, 66317, 99532, 265381, 364913,
            1360120, 1725033, 25510582, 52746197, 78256779, 131002976,
            340262731, 811528438, 1963319607, 4738167652]
}

# e convergents
e_convergents = {
    'num': [2, 3, 8, 11, 19, 87, 106, 193, 1264, 1457, 2721, 23225, 25946,
            49171, 517656, 566827, 1084483, 13580623, 14665106, 28245729],
    'den': [1, 1, 3, 4, 7, 32, 39, 71, 465, 536, 1001, 8544, 9545, 18089,
            190435, 208524, 398959, 4996032, 5394991, 10391023]
}

# √2 convergents
sqrt2_convergents = {
    'num': [1, 3, 7, 17, 41, 99, 239, 577, 1393, 3363, 8119, 19601, 47321,
            114243, 275807, 665857, 1607521, 3880899, 9369319, 22619537],
    'den': [1, 2, 5, 12, 29, 70, 169, 408, 985, 2378, 5741, 13860, 33461,
            80782, 195025, 470832, 1136689, 2744210, 6625109, 15994428]
}

# φ (golden ratio) convergents - Fibonacci numbers
phi_convergents = {
    'num': [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987,
            1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025,
            121393, 196418, 317811, 514229, 832040, 1346269, 2178309],
    'den': [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987,
            1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025,
            121393, 196418, 317811, 514229, 832040, 1346269]
}

# ln(2) convergents
ln2_convergents = {
    'num': [0, 1, 2, 9, 11, 75, 236, 311, 547, 1641, 2188, 3829, 5470,
            9299, 23068, 32367, 87802, 120169, 327309, 1308905],
    'den': [1, 1, 3, 13, 16, 109, 341, 450, 791, 2373, 3164, 5537, 7910,
            13447, 33351, 46798, 127047, 173845, 474837, 1899348]
}

print("=" * 80)
print("FACTORIZATION ANALYSIS")
print("=" * 80)
print("Model: Claude Opus 4.5")
print("Date: 2025-12-20")
print()

# Print factorizations
for n, factors in factorizations.items():
    product = 1
    for f in factors:
        product *= f
    print(f"m[{n}] = {' × '.join(map(str, factors))}")
    print(f"       = {product}")
    print(f"       Number of prime factors: {len(factors)}")
    print()

# Check if any factor is a convergent
print("=" * 80)
print("CHECKING FACTORS AGAINST CONVERGENTS")
print("=" * 80)

all_convergents = {}
for name, conv in [('π_num', pi_convergents['num']), ('π_den', pi_convergents['den']),
                   ('e_num', e_convergents['num']), ('e_den', e_convergents['den']),
                   ('√2_num', sqrt2_convergents['num']), ('√2_den', sqrt2_convergents['den']),
                   ('φ_num', phi_convergents['num']), ('φ_den', phi_convergents['den']),
                   ('ln2_num', ln2_convergents['num']), ('ln2_den', ln2_convergents['den'])]:
    for i, c in enumerate(conv):
        if c > 1:
            all_convergents[c] = f"{name}[{i}]"

for n, factors in factorizations.items():
    print(f"\nm[{n}] factors:")
    for f in factors:
        if f in all_convergents:
            print(f"  {f} = {all_convergents[f]} ✓ CONVERGENT MATCH!")
        else:
            # Check if factor is close to any convergent
            closest = None
            min_diff = float('inf')
            for c, name in all_convergents.items():
                diff = abs(c - f)
                if diff < min_diff:
                    min_diff = diff
                    closest = (c, name)
            if closest and min_diff < f * 0.01:  # Within 1%
                print(f"  {f} ≈ {closest[0]} = {closest[1]} (diff={min_diff})")
            else:
                print(f"  {f} - no direct convergent match")

# Check for products of convergents
print("\n" + "=" * 80)
print("CHECKING FOR PRODUCTS OF CONVERGENTS")
print("=" * 80)

for n, factors in factorizations.items():
    m = 1
    for f in factors:
        m *= f

    # Check if m is a product of two convergents
    for c1, name1 in all_convergents.items():
        if c1 > 1 and m % c1 == 0:
            quotient = m // c1
            if quotient in all_convergents:
                print(f"m[{n}] = {name1} × {all_convergents[quotient]} = {c1} × {quotient}")

# Analyze factor relationships
print("\n" + "=" * 80)
print("FACTOR RELATIONSHIP ANALYSIS")
print("=" * 80)

for n, factors in factorizations.items():
    print(f"\nm[{n}] factors: {factors}")

    # Check for arithmetic relationships between factors
    for i, f1 in enumerate(factors):
        for j, f2 in enumerate(factors[i+1:], i+1):
            ratio = f2 / f1 if f1 > 0 else 0
            diff = f2 - f1
            print(f"  {f2}/{f1} = {ratio:.4f}, {f2}-{f1} = {diff}")

# Check GCDs between factorizations
print("\n" + "=" * 80)
print("GCD ANALYSIS BETWEEN M-VALUES")
print("=" * 80)

m_values = {}
for n, factors in factorizations.items():
    m = 1
    for f in factors:
        m *= f
    m_values[n] = m

for n1 in [62, 65, 68]:
    for n2 in [65, 68]:
        if n1 < n2:
            g = gcd(m_values[n1], m_values[n2])
            print(f"gcd(m[{n1}], m[{n2}]) = {g}")

# Special number analysis
print("\n" + "=" * 80)
print("SPECIAL NUMBER PATTERNS")
print("=" * 80)

for n, factors in factorizations.items():
    print(f"\nm[{n}]:")
    for f in factors:
        # Is it a Mersenne number (2^p - 1)?
        for p in range(2, 64):
            if f == (2**p - 1):
                print(f"  {f} = 2^{p} - 1 (Mersenne)")
                break

        # Is it 2^p + 1?
        for p in range(2, 64):
            if f == (2**p + 1):
                print(f"  {f} = 2^{p} + 1")
                break

        # Is it a triangular number?
        n_tri = int((sqrt(8*f + 1) - 1) / 2)
        if n_tri * (n_tri + 1) // 2 == f:
            print(f"  {f} = T_{n_tri} (triangular)")

        # Is it close to a power of 2?
        import math
        log2_f = math.log2(f) if f > 0 else 0
        if abs(log2_f - round(log2_f)) < 0.01:
            print(f"  {f} ≈ 2^{round(log2_f)}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
Verified Factorizations:
- m[62] = 2 × 3 × 281 × 373 × 2843 × 10487 × 63199 (7 prime factors)
- m[65] = 24239 × 57283 × 1437830129 (3 prime factors)
- m[68] = 5 × 1153 × 1861 × 31743327447619 (4 prime factors)

Key Observations:
1. All three m-values are coprime (GCD = 1)
2. m[62] has small factors (2, 3), m[68] has small factor (5)
3. m[65] has only large prime factors
4. Number of prime factors varies: 7, 3, 4
""")
