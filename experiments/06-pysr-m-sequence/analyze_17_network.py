#!/usr/bin/env python3
"""
Deep analysis of the 17-network indices pattern.
17 appears at: n = 9, 11, 12, 24, 48, 67

Goal: Find the formula that determines WHICH indices contain factor 17.
"""

import json
from sympy import isprime, primepi, factorint

# Load data
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

M_SEQ = data['m_seq']
D_SEQ = data['d_seq']

def m(n):
    if n < 2 or n > 70:
        return None
    return M_SEQ[n - 2]

def d(n):
    if n < 2 or n > 70:
        return None
    return D_SEQ[n - 2]

print("=" * 70)
print("17-NETWORK INDICES ANALYSIS")
print("=" * 70)

# Known 17-network indices
network_17 = [9, 11, 12, 24, 48, 67]

print("\n### Binary representation of 17-network indices:")
for n in network_17:
    print(f"  n={n:3}: bin={bin(n):>10}, popcount={bin(n).count('1')}, d[n]={d(n)}")

# Check differences
print("\n### Differences between consecutive 17-network indices:")
for i in range(1, len(network_17)):
    diff = network_17[i] - network_17[i-1]
    print(f"  {network_17[i]} - {network_17[i-1]} = {diff}")

# Check ratios
print("\n### Ratios of 17-network indices:")
for i in range(1, len(network_17)):
    ratio = network_17[i] / network_17[i-1]
    print(f"  {network_17[i]} / {network_17[i-1]} = {ratio:.4f}")

# Check if indices relate to powers of 2
print("\n### Relationship to powers of 2:")
for n in network_17:
    # Find closest power of 2
    log2 = n.bit_length() - 1
    lower = 2 ** log2
    upper = 2 ** (log2 + 1)

    diff_lower = n - lower
    diff_upper = upper - n

    print(f"  n={n:3}: between 2^{log2}={lower} and 2^{log2+1}={upper}, "
          f"diff from lower={diff_lower}, diff from upper={diff_upper}")

# Check m-values at 17-network indices
print("\n### m-values at 17-network indices:")
print("n    m[n]                   m[n]/17                    cofactor_factors")
print("-" * 80)
for n in network_17:
    mn = m(n)
    cofactor = mn // 17
    factors = factorint(cofactor)
    factor_str = ' × '.join([f'{p}^{e}' if e > 1 else str(p)
                             for p, e in sorted(factors.items())])
    print(f"{n:3}  {mn:<22} {cofactor:<26} {factor_str}")

# Check if cofactors are prime
print("\n### Are cofactors prime?")
for n in network_17:
    mn = m(n)
    cofactor = mn // 17
    if isprime(cofactor):
        pi = primepi(cofactor)
        print(f"  m[{n}]/17 = {cofactor} = p[{pi}] (PRIME)")
    else:
        print(f"  m[{n}]/17 = {cofactor} (COMPOSITE)")

# Formula test: For prime cofactors, is p[something related to n]?
print("\n### Prime cofactor indices:")
print("Testing if cofactor = p[f(n)] for some function f")
for n in [9, 11, 12]:  # Only these have prime cofactors
    mn = m(n)
    cofactor = mn // 17
    pi = primepi(cofactor)
    # Test various relationships
    print(f"  n={n}: cofactor={cofactor}, p[{pi}]")
    print(f"    pi - n = {pi - n}")
    print(f"    pi + n = {pi + n}")
    print(f"    pi * n = {pi * n}")
    print(f"    pi / n = {pi / n:.4f}")

# D-sequence at 17-network
print("\n### D-sequence at 17-network indices:")
for n in network_17:
    dn = d(n)
    print(f"  d[{n}] = {dn}")

# Check: what about indices 9, 11, 12?
# m[9]  = 17 × 29  = 17 × p[10]  → pi = n + 1
# m[11] = 17 × 113 = 17 × p[30]  → pi = n + 19
# m[12] = 17 × 73  = 17 × p[21]  → pi = n + 9

print("\n" + "=" * 70)
print("HYPOTHESIS TEST: m[n] = 17 × p[n + m[k]] for some k")
print("=" * 70)

# For n=9: p[10] = p[9 + 1] = p[9 + m[2]]  since m[2]=1
# For n=11: p[30] = p[11 + 19] = p[11 + m[6]] since m[6]=19
# For n=12: p[21] = p[12 + 9] = p[12 + m[5]] since m[5]=9

print("\nVerifying the formula m[n] = 17 × p[n + m[earlier]]:")
from sympy import prime

tests = [
    (9, 2),   # m[9] = 17 × p[9 + m[2]]
    (11, 6),  # m[11] = 17 × p[11 + m[6]]
    (12, 5),  # m[12] = 17 × p[12 + m[5]]
]

for n, earlier in tests:
    mn = m(n)
    m_earlier = m(earlier)
    target_idx = n + m_earlier
    predicted = 17 * prime(target_idx)
    match = "✓" if predicted == mn else "✗"
    print(f"  m[{n}] = 17 × p[{n} + m[{earlier}]] = 17 × p[{target_idx}] = {predicted} vs {mn} {match}")

# Check the pattern for indices choosing "earlier"
print("\n### Pattern for choosing 'earlier' index:")
print("n=9:  earlier=2, m[2]=1,  d[9]=1")
print("n=11: earlier=6, m[6]=19, d[11]=1")
print("n=12: earlier=5, m[5]=9,  d[12]=2")

print("\n### Does earlier = d[n] + something?")
for n, earlier in tests:
    dn = d(n)
    diff = earlier - dn
    print(f"  n={n}: earlier={earlier}, d[n]={dn}, earlier-d[n]={diff}")

# Test hypothesis: earlier = d[n] + 1
print("\n### Testing: earlier = d[n] + 1")
for n, earlier in tests:
    dn = d(n)
    predicted_earlier = dn + 1
    match = "✓" if predicted_earlier == earlier else "✗"
    print(f"  n={n}: d[n]+1={predicted_earlier}, actual earlier={earlier} {match}")

# Check larger 17-network members
print("\n" + "=" * 70)
print("EXTENDING 17-NETWORK FORMULA TO n=24, 48, 67")
print("=" * 70)

for n in [24, 48, 67]:
    mn = m(n)
    cofactor = mn // 17
    dn = d(n)

    print(f"\nn={n}: m[n]={mn}, m[n]/17={cofactor}, d[n]={dn}")

    # Check if cofactor relates to primes
    if isprime(cofactor):
        pi = primepi(cofactor)
        print(f"  cofactor = p[{pi}] (PRIME)")
        # Test the formula
        for earlier in [2, 5, 6, 9, 11, 12]:
            m_earlier = m(earlier)
            if m_earlier and n + m_earlier == pi:
                print(f"  Formula: m[{n}] = 17 × p[{n} + m[{earlier}]] ✓")
    else:
        factors = factorint(cofactor)
        print(f"  cofactor factors: {factors}")
        # Look for patterns in composite cofactors
        print(f"  11 in factors: {11 in factors}")
        print(f"  cofactor/11 = {cofactor/11 if 11 in factors else 'N/A'}")
