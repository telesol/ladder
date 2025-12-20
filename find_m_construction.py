#!/usr/bin/env python3
"""
Find the exact construction of m[62], m[65], m[68] from extended convergents.
Goal: Discover the pattern to derive m[71].
"""

import json
from math import gcd
from itertools import combinations, product as cartesian_product

# Extended convergent generation
def cf_convergents(cf_terms, n_terms=40):
    """Generate convergents from continued fraction terms."""
    p = [0, 1]
    q = [1, 0]
    nums, dens = [], []
    for i, a in enumerate(cf_terms[:n_terms]):
        p_new = a * p[-1] + p[-2]
        q_new = a * q[-1] + q[-2]
        p.append(p_new)
        q.append(q_new)
        nums.append(p_new)
        dens.append(q_new)
    return nums, dens

# Continued fractions (extended)
pi_cf = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2, 1, 84, 2, 1, 1, 15, 3, 13, 1, 4]
e_cf = [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, 1, 1, 12, 1, 1, 14, 1, 1, 16, 1, 1, 18, 1, 1, 20]
sqrt2_cf = [1] + [2] * 50
phi_cf = [1] * 50
ln2_cf = [0, 1, 2, 3, 1, 6, 3, 1, 1, 2, 1, 1, 1, 1, 3, 10, 1, 1, 1, 2, 1, 1, 1, 1, 3, 1, 14, 1, 3]

pi_n, pi_d = cf_convergents(pi_cf, 25)
e_n, e_d = cf_convergents(e_cf, 25)
sqrt2_n, sqrt2_d = cf_convergents(sqrt2_cf, 35)
phi_n, phi_d = cf_convergents(phi_cf, 35)
ln2_n, ln2_d = cf_convergents(ln2_cf, 20)

# All convergents combined
all_convs = {
    'π_n': pi_n, 'π_d': pi_d,
    'e_n': e_n, 'e_d': e_d,
    '√2_n': sqrt2_n, '√2_d': sqrt2_d,
    'φ_n': phi_n, 'φ_d': phi_d,
    'ln2_n': ln2_n, 'ln2_d': ln2_d
}

# Target m-values
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']

targets = {
    62: m_seq[60],  # 1184962853718958602
    65: m_seq[63],  # 1996402169071970173
    68: m_seq[66],  # 340563526170809298635
}

print("=" * 80)
print("FINDING M-VALUE CONSTRUCTIONS")
print("=" * 80)

def find_divisors(m, conv_dict, max_check=10**12):
    """Find convergents that divide m."""
    divisors = []
    for name, conv_list in conv_dict.items():
        for i, c in enumerate(conv_list):
            if 1 < c <= max_check and m % c == 0:
                divisors.append((name, i, c, m // c))
    return divisors

def find_two_factor_product(m, conv_dict, max_val=10**12):
    """Find if m = c1 * c2 for two convergents."""
    all_vals = []
    for name, conv_list in conv_dict.items():
        for i, c in enumerate(conv_list):
            if 1 < c <= max_val:
                all_vals.append((name, i, c))

    # Check pairs
    for (n1, i1, c1), (n2, i2, c2) in combinations(all_vals, 2):
        if c1 * c2 == m:
            return [(n1, i1, c1), (n2, i2, c2)]

    # Check squares
    for (n1, i1, c1) in all_vals:
        if c1 * c1 == m:
            return [(n1, i1, c1), (n1, i1, c1)]

    return None

print("\n### Analyzing target m-values ###\n")

for n, m in targets.items():
    print(f"n={n}: m = {m}")
    print(f"  bit_length = {m.bit_length()}")
    print(f"  m / 2^{n} = {m / (2**n):.10f}")

    # Find single convergent divisors
    divisors = find_divisors(m, all_convs)
    if divisors:
        print(f"  Convergent divisors:")
        for name, idx, c, quotient in divisors[:10]:
            print(f"    m = {name}[{idx}]={c} × {quotient}")

    # Try to find two-factor product
    two_factor = find_two_factor_product(m, all_convs)
    if two_factor:
        print(f"  Two-factor: m = {two_factor[0][2]} × {two_factor[1][2]}")

    print()

# Now look for patterns in the quotients
print("\n" + "=" * 80)
print("ANALYZING QUOTIENT PATTERNS")
print("=" * 80)

for n, m in targets.items():
    print(f"\nn={n}: m = {m}")

    # Check if m is close to 2^n or related powers
    for exp in range(n-5, n+5):
        diff = abs(m - 2**exp)
        if diff < m / 10:
            sign = "+" if 2**exp > m else "-"
            print(f"  m ≈ 2^{exp} {sign} {abs(2**exp - m)}")

    # Check if m = a * 2^k + b for small a, b
    for k in range(50, n):
        quotient = m // (2**k)
        remainder = m % (2**k)
        if quotient < 1000 and remainder < 10**15:
            print(f"  m = {quotient} × 2^{k} + {remainder}")

# Check for relationships between consecutive m-values
print("\n" + "=" * 80)
print("INTER-M RELATIONSHIPS")
print("=" * 80)

m_62 = targets[62]
m_65 = targets[65]
m_68 = targets[68]

print(f"\nm[65] / m[62] = {m_65 / m_62:.10f}")
print(f"m[68] / m[65] = {m_68 / m_65:.10f}")
print(f"m[68] / m[62] = {m_68 / m_62:.10f}")

# Check GCDs
print(f"\ngcd(m[62], m[65]) = {gcd(m_62, m_65)}")
print(f"gcd(m[65], m[68]) = {gcd(m_65, m_68)}")
print(f"gcd(m[62], m[68]) = {gcd(m_62, m_68)}")

# Check if m[n] = f(n) * g(earlier_m)
print("\n### Checking self-referential patterns ###")
for n, m in targets.items():
    # Check if m[n] is divisible by earlier m values
    for earlier_n in range(4, n):
        earlier_m = m_seq[earlier_n - 2]
        if earlier_m > 1 and m % earlier_m == 0:
            quotient = m // earlier_m
            if quotient < 10**15:
                print(f"m[{n}] = m[{earlier_n}] × {quotient} = {earlier_m} × {quotient}")

# Generate candidate m[71] values based on patterns
print("\n" + "=" * 80)
print("GENERATING m[71] CANDIDATES")
print("=" * 80)

# Based on analysis, try some construction patterns
# For d=2: m[71] ∈ [6.47e+20, 1.04e+21]

m71_candidates = []

# Pattern 1: m[71] = constant × 2^k
for const in [1, 2, 3, 5, 7, 11, 13, 17, 19, 22, 23]:
    for k in range(60, 72):
        m = const * (2**k)
        if 6.47e20 <= m <= 1.04e21:
            m71_candidates.append((m, f"{const} × 2^{k}"))

# Pattern 2: m[71] based on ratio to m[68]
for ratio in [1.5, 2.0, 2.5, 3.0]:
    m = int(m_68 * ratio)
    if 6.47e20 <= m <= 1.04e21:
        m71_candidates.append((m, f"m[68] × {ratio}"))

# Pattern 3: Convergent products
for name1, convs1 in all_convs.items():
    for name2, convs2 in all_convs.items():
        for i, c1 in enumerate(convs1[:15]):
            for j, c2 in enumerate(convs2[:15]):
                m = c1 * c2
                if 6.47e20 <= m <= 1.04e21:
                    m71_candidates.append((m, f"{name1}[{i}]×{name2}[{j}] = {c1}×{c2}"))

print(f"\nGenerated {len(m71_candidates)} candidates for m[71] (d=2 range)")
print("\nTop candidates:")
for m, desc in sorted(m71_candidates, key=lambda x: x[0])[:20]:
    print(f"  m = {m:.6e}: {desc}")
