#!/usr/bin/env python3
"""
Verify and extend the hypothesized prime index formulas for m-sequence.

Hypotheses from coordination note:
- m[9]  = p[7] × p[10] = 17 × 29 = 493
- m[11] = p[7] × p[n+m[6]] = 17 × p[11+19] = 17 × p[30] = 17 × 113 = 1921
- m[12] = p[7] × p[n+m[5]] = 17 × p[12+9] = 17 × p[21] = 17 × 73 = 1241

Goal: Verify these and find more patterns.
"""

import json
from sympy import prime, primepi, factorint

# Load the data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']  # m[2] is at index 0
d_seq = data['d_seq']  # d[2] is at index 0

def m(n):
    """Get m[n] (n starts at 2)"""
    return m_seq[n - 2]

def d(n):
    """Get d[n] (n starts at 2)"""
    return d_seq[n - 2]

print("=" * 70)
print("VERIFYING HYPOTHESIZED PRIME INDEX FORMULAS")
print("=" * 70)

# Verify the known hypotheses
print("\n### Hypothesis 1: m[9] = p[7] × p[10]")
p7, p10 = prime(7), prime(10)
print(f"p[7] = {p7}, p[10] = {p10}")
print(f"p[7] × p[10] = {p7 * p10}")
print(f"m[9] = {m(9)}")
print(f"MATCH: {p7 * p10 == m(9)}")

print("\n### Hypothesis 2: m[11] = p[7] × p[n + m[6]]")
n = 11
idx = n + m(6)  # 11 + 19 = 30
print(f"n = {n}, m[6] = {m(6)}, n + m[6] = {idx}")
print(f"p[7] = {p7}, p[{idx}] = {prime(idx)}")
print(f"p[7] × p[{idx}] = {p7 * prime(idx)}")
print(f"m[11] = {m(11)}")
print(f"MATCH: {p7 * prime(idx) == m(11)}")

print("\n### Hypothesis 3: m[12] = p[7] × p[n + m[5]]")
n = 12
idx = n + m(5)  # 12 + 9 = 21
print(f"n = {n}, m[5] = {m(5)}, n + m[5] = {idx}")
print(f"p[7] = {p7}, p[{idx}] = {prime(idx)}")
print(f"p[7] × p[{idx}] = {p7 * prime(idx)}")
print(f"m[12] = {m(12)}")
print(f"MATCH: {p7 * prime(idx) == m(12)}")

print("\n" + "=" * 70)
print("SEARCHING FOR MORE PRIME INDEX PATTERNS")
print("=" * 70)

# For each m value that contains 17, check if the cofactor's prime index
# relates to n and earlier m values
print("\n### Values containing p[7]=17:")
for n in range(2, 71):
    mv = m(n)
    factors = factorint(mv)
    if 17 in factors:
        cofactor = mv // (17 ** factors[17])
        # Check if cofactor is prime
        cofactor_factors = factorint(cofactor)
        if len(cofactor_factors) == 1 and list(cofactor_factors.values())[0] == 1:
            # Cofactor is prime, find its index
            cf_prime = list(cofactor_factors.keys())[0]
            cf_index = primepi(cf_prime)
            print(f"\nn={n}: m[{n}] = {mv} = 17^{factors[17]} × {cofactor}")
            print(f"  Cofactor {cofactor} is prime, index = {cf_index}")
            # Check various formulas
            for earlier_n in range(2, n):
                if n + m(earlier_n) == cf_index:
                    print(f"  *** MATCH: n + m[{earlier_n}] = {n} + {m(earlier_n)} = {cf_index} ***")
                if n - m(earlier_n) == cf_index:
                    print(f"  *** MATCH: n - m[{earlier_n}] = {n} - {m(earlier_n)} = {cf_index} ***")
                if n * earlier_n == cf_index:
                    print(f"  *** MATCH: n × {earlier_n} = {cf_index} ***")

print("\n" + "=" * 70)
print("ANALYZING D-SEQUENCE PATTERNS")
print("=" * 70)

print("\n### D-sequence values:")
for n in range(2, 32):
    print(f"d[{n}] = {d(n)}", end="  ")
    if (n - 1) % 10 == 0:
        print()

print("\n\n### D-sequence distribution:")
from collections import Counter
d_counts = Counter(d_seq)
for val, count in sorted(d_counts.items()):
    print(f"d={val}: {count} times ({100*count/len(d_seq):.1f}%)")

print("\n### Checking d[n] vs binary representation of n:")
print("n   d[n]  bin(n)         popcount  trailing_zeros  highest_bit")
for n in range(2, 32):
    bn = bin(n)[2:]
    popcount = bn.count('1')
    trailing = len(bn) - len(bn.rstrip('0'))
    highest = len(bn)
    print(f"{n:3} {d(n):4}  {bn:>12}  {popcount:8}  {trailing:14}  {highest:11}")

print("\n### Checking if d[n] relates to powers of 2:")
print("n   d[n]  2^d[n]  n mod 2^d[n]  n // 2^d[n]")
for n in range(2, 32):
    dv = d(n)
    pow2d = 2 ** dv
    print(f"{n:3} {dv:4}  {pow2d:5}  {n % pow2d:11}  {n // pow2d:10}")

print("\n" + "=" * 70)
print("CHECKING OEIS-LIKE PATTERNS")
print("=" * 70)

# Check if d-sequence follows any simple rule
print("\n### Testing d[n] = f(n) hypotheses:")

# Hypothesis: d[n] related to highest power of 2 dividing something
def highest_power_of_2(x):
    if x == 0:
        return 0
    count = 0
    while x % 2 == 0:
        x //= 2
        count += 1
    return count

print("\nTesting: d[n] = 1 + highest_power_of_2(n-1)")
matches = 0
for n in range(2, 32):
    predicted = 1 + highest_power_of_2(n - 1)
    actual = d(n)
    match = "✓" if predicted == actual else "✗"
    if predicted == actual:
        matches += 1
    print(f"n={n}: predicted={predicted}, actual={actual} {match}")
print(f"Match rate: {matches}/30 = {100*matches/30:.1f}%")

# Another hypothesis: d[n] related to digit sum or other properties
print("\n\nTesting: d[n] = popcount(n) (number of 1s in binary)")
matches = 0
for n in range(2, 32):
    predicted = bin(n).count('1')
    actual = d(n)
    match = "✓" if predicted == actual else "✗"
    if predicted == actual:
        matches += 1
print(f"Match rate: {matches}/30 = {100*matches/30:.1f}%")
