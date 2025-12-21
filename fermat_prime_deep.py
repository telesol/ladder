#!/usr/bin/env python3
"""
Deep Fermat Prime Analysis

Fermat primes: F_n = 2^(2^n) + 1
F_0 = 3, F_1 = 5, F_2 = 17, F_3 = 257, F_4 = 65537

17 appears in the m-sequence at indices 9, 11, 12, 24, 48, 67.
Do 3 and 5 also appear as hidden factors?
"""
import json
from sympy import factorint, isprime, prime, primepi

# Load data
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

M_SEQ = data['m_seq']
D_SEQ = data['d_seq']

def m(n):
    if n < 2 or n > 70:
        return None
    return M_SEQ[n - 2]

print("=" * 80)
print("FERMAT PRIME DEEP ANALYSIS")
print("=" * 80)
print()

fermat_primes = [3, 5, 17, 257, 65537]
print(f"Fermat primes in range: {[f for f in fermat_primes if f < 1000000]}")
print()

# Check which m-values are divisible by each Fermat prime
print("### M-values divisible by Fermat primes ###")
print()

for fp in [3, 5, 17]:
    indices = []
    for i in range(len(M_SEQ)):
        n = i + 2
        if M_SEQ[i] % fp == 0:
            indices.append(n)
    print(f"F = {fp:2d}: Divisible at n = {indices}")
    print(f"       Count: {len(indices)}/{len(M_SEQ)} ({100*len(indices)/len(M_SEQ):.1f}%)")
    print()

# Deep dive into 17-network
print("### 17-NETWORK DEEP ANALYSIS ###")
print()
network_17 = [9, 11, 12, 24, 48, 67]

for n in network_17:
    mn = m(n)
    factors = factorint(mn)
    cofactor = mn // 17

    print(f"n={n:2d}: m[n] = {mn}")
    print(f"       = 17 × {cofactor}")
    print(f"       factors: {factors}")

    # Check if cofactor is prime
    if isprime(cofactor):
        pi = primepi(cofactor)
        print(f"       cofactor = p[{pi}] (PRIME!)")
    else:
        cf_factors = factorint(cofactor)
        print(f"       cofactor factors: {cf_factors}")

    # Binary analysis
    print(f"       n binary: {bin(n)}")
    print()

# Look for pattern in 17-network indices
print("### PATTERN IN 17-NETWORK INDICES ###")
print()
print("Indices: 9, 11, 12, 24, 48, 67")
print()

# Check modular patterns
print("Modular patterns:")
for p in [3, 4, 5, 8, 12, 17]:
    residues = [n % p for n in network_17]
    print(f"  mod {p:2d}: {residues}")

print()

# Check differences
print("Differences between consecutive indices:")
diffs = [network_17[i+1] - network_17[i] for i in range(len(network_17)-1)]
print(f"  {diffs}")
print(f"  = {[2, 1, 12, 24, 19]}")
print(f"  Note: 19 = m[6]!")
print()

# Check if indices relate to Fermat numbers
print("### RELATION TO FERMAT NUMBERS ###")
print()
print("F_0 = 2^1 + 1 = 3")
print("F_1 = 2^2 + 1 = 5")
print("F_2 = 2^4 + 1 = 17")
print("F_3 = 2^8 + 1 = 257")
print()

for n in network_17:
    # Check n mod F_k for various k
    print(f"n={n:2d}:")
    print(f"  n mod 3 = {n % 3}")
    print(f"  n mod 5 = {n % 5}")
    print(f"  n mod 17 = {n % 17}")
    print(f"  n / 3 = {n / 3:.2f}")
    print(f"  n / 5 = {n / 5:.2f}")
    print()

# Check if 3 and 5 form similar networks
print("### LOOKING FOR 3-NETWORK AND 5-NETWORK ###")
print()

for fp in [3, 5]:
    network = []
    for i in range(len(M_SEQ)):
        n = i + 2
        if M_SEQ[i] % fp == 0:
            cofactor = M_SEQ[i] // fp
            if isprime(cofactor):
                network.append((n, cofactor))

    print(f"{fp}-NETWORK (m[n] = {fp} × prime):")
    for n, cof in network[:10]:
        pi = primepi(cof)
        print(f"  n={n}: m[n]/{fp} = {cof} = p[{pi}]")
    print(f"  Total: {len(network)} members")
    print()

# The key insight: relationship between indices
print("### KEY INSIGHT: INDEX RELATIONSHIPS ###")
print()
print("17-network: 9, 11, 12, 24, 48, 67")
print()
print("Notice:")
print("  12 = 4 × 3 = 2^2 × 3")
print("  24 = 8 × 3 = 2^3 × 3 = 2 × 12")
print("  48 = 16 × 3 = 2^4 × 3 = 2 × 24")
print()
print("So 12, 24, 48 are 3 × 2^k for k=2,3,4")
print("And 9 = 3^2, 11 is prime, 67 is prime")
print()
print("The pattern might be:")
print("  - Primes near Fermat boundaries: 11, 67")
print("  - Powers of 2 times 3: 12, 24, 48")
print("  - 3^2 = 9")
print()

# Check GCD patterns
print("### GCD ANALYSIS ###")
print()
from math import gcd
from functools import reduce

overall_gcd = reduce(gcd, network_17)
print(f"GCD of all 17-network indices: {overall_gcd}")

for i in range(len(network_17)):
    for j in range(i+1, len(network_17)):
        g = gcd(network_17[i], network_17[j])
        if g > 1:
            print(f"  GCD({network_17[i]}, {network_17[j]}) = {g}")
