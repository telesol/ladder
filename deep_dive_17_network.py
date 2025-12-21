#!/usr/bin/env python3
"""
Deep Dive: The 17-Network Hidden Building Block

BREAKTHROUGH DISCOVERY:
m[9] = 17 × p[9 + m[2]] = 17 × p[10] = 493 ✓
m[11] = 17 × p[11 + m[6]] = 17 × p[30] = 1921 ✓
m[12] = 17 × p[12 + m[5]] = 17 × p[21] = 1241 ✓

This suggests m-values use earlier m-values as INDICES into the prime sequence!

Goal: Extend this pattern to predict m[71].
"""
import subprocess
import json
from sympy import prime, isprime, primepi, factorint
from datetime import datetime

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

print("=" * 80)
print("17-NETWORK DEEP DIVE - EXTENSION TO n=71")
print("=" * 80)
print()

# Verified 17-network formulas
print("### VERIFIED 17-NETWORK FORMULAS ###")
print()
verified_formulas = [
    (9, 2, "m[9] = 17 × p[9 + m[2]] = 17 × p[10] = 493"),
    (11, 6, "m[11] = 17 × p[11 + m[6]] = 17 × p[30] = 1921"),
    (12, 5, "m[12] = 17 × p[12 + m[5]] = 17 × p[21] = 1241"),
]

for n, earlier, formula in verified_formulas:
    mn = m(n)
    m_earlier = m(earlier)
    computed = 17 * prime(n + m_earlier)
    match = "✓" if computed == mn else "✗"
    print(f"{formula} {match}")

print()

# Look for the pattern in "earlier" selection
print("### PATTERN IN 'EARLIER' SELECTION ###")
print()
print("For n=9: earlier=2, d[9]=1, n mod 3 = 0")
print("For n=11: earlier=6, d[11]=1, n mod 3 = 2")
print("For n=12: earlier=5, d[12]=2, n mod 3 = 0")
print()

# Test more hypotheses for "earlier" selection
print("### TESTING HYPOTHESES FOR 'EARLIER' SELECTION ###")
print()

# Hypothesis 1: earlier relates to n mod something
for n, earlier, _ in verified_formulas:
    print(f"n={n}: earlier={earlier}")
    print(f"  n mod 2 = {n % 2}, n mod 3 = {n % 3}, n mod 4 = {n % 4}")
    print(f"  earlier mod 2 = {earlier % 2}, earlier mod 3 = {earlier % 3}")
    print(f"  n - earlier = {n - earlier}")
    print(f"  d[n] = {d(n)}, d[earlier] = {d(earlier)}")
    print()

# Now extend: For n=71 (prime!), if 17-network applies...
print("### EXTENSION TO n=71 ###")
print()
print("n=71 is PRIME. The 17-network might apply if:")
print("  m[71] = 17 × p[71 + m[earlier]]")
print()

# What values of "earlier" give reasonable results?
print("Testing possible 'earlier' values for n=71:")
print()

# Constraints on m[71]:
# If d[71]=1: m[71] ∈ [1.94e21, 3.12e21]
# If d[71]=2: m[71] ∈ [6.47e20, 1.04e21]
m71_ranges = {
    1: (1.94e21, 3.12e21),
    2: (6.47e20, 1.04e21),
    5: (9.24e19, 1.49e20),
    8: (8.66e18, 1.39e19),
}

print("If 17-network applies: m[71] = 17 × p[71 + m[earlier]]")
print()

for earlier in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
    m_earlier = m(earlier)
    prime_index = 71 + m_earlier
    # Compute 17 * p[prime_index]
    # For large prime indices, we need to estimate
    try:
        p = prime(prime_index)
        m71_candidate = 17 * p
        print(f"earlier={earlier}: m[earlier]={m_earlier}, prime_index={prime_index}")
        print(f"  p[{prime_index}] ≈ {p}")
        print(f"  m[71] candidate = 17 × {p} = {m71_candidate}")

        # Check if this fits any d-range
        for d_val, (lo, hi) in m71_ranges.items():
            if lo <= m71_candidate <= hi:
                print(f"  ✓ Fits d[71]={d_val} range [{lo:.2e}, {hi:.2e}]")
        print()
    except Exception as e:
        print(f"earlier={earlier}: Error computing prime({prime_index}): {e}")
        print()

# Alternative: What if the formula changes for large n?
print()
print("### COMPOSITE COFACTOR PATTERN (n=24, 48, 67) ###")
print()

# For larger 17-network members, cofactors are composite
# Let's analyze the structure
for n in [24, 48, 67]:
    mn = m(n)
    cofactor = mn // 17
    factors = factorint(cofactor)
    print(f"n={n}: m[n]={mn}")
    print(f"  m[n]/17 = {cofactor}")
    print(f"  factors = {factors}")

    # Check for patterns in factors
    if 11 in factors:
        print(f"  11 appears! (11 = m[11] mod 100?)")
    if 37 in factors:
        print(f"  37 appears! (37 is prime)")
    if 673 in factors:
        print(f"  673 appears! (673 is prime)")
    print()

# The key insight: Are cofactors related to combinations of earlier m-values?
print("### TESTING COFACTOR = COMBINATION OF M-VALUES ###")
print()

for n in [24, 48, 67]:
    mn = m(n)
    cofactor = mn // 17
    print(f"n={n}: cofactor = {cofactor}")

    # Test if cofactor = m[a] * m[b] for some a, b
    found_match = False
    for a in range(2, 15):
        for b in range(a, 15):
            ma = m(a)
            mb = m(b)
            if ma and mb:
                product = ma * mb
                if cofactor % product == 0:
                    quotient = cofactor // product
                    if quotient < 10000 and quotient > 0:
                        print(f"  cofactor = m[{a}] × m[{b}] × {quotient} = {ma} × {mb} × {quotient}")
                        found_match = True

    if not found_match:
        print(f"  No simple m-product pattern found")
    print()

print("=" * 80)
print("KEY INSIGHT")
print("=" * 80)
print()
print("The 17-NETWORK is a hidden building block where:")
print("  m[n] = 17 × f(n, earlier_m_values)")
print()
print("For small n (9, 11, 12):")
print("  f = p[n + m[earlier]] (prime at recursive index)")
print()
print("For larger n (24, 48, 67):")
print("  f = composite involving earlier m-value products")
print()
print("This suggests the construction algorithm uses:")
print("1. Mathematical constants (π, e, √3) for n=2-6")
print("2. Recursive m-combinations for n=7-12")
print("3. 17-network for specific indices")
print("4. Building block multiplication for n>12")
print()
