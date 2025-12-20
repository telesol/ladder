#!/usr/bin/env python3
"""
Deep analysis of m-value construction for n ≡ 2 (mod 3).
Goal: Find the exact construction pattern to derive m[71].
"""

import json
from math import gcd, isqrt

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

# Extended convergent lists
def generate_convergents(a_n, n_terms=30):
    """Generate convergent numerators and denominators from continued fraction."""
    p = [0, 1]
    q = [1, 0]
    nums = []
    dens = []
    for i in range(n_terms):
        if i < len(a_n):
            a = a_n[i]
        else:
            break
        p_new = a * p[-1] + p[-2]
        q_new = a * q[-1] + q[-2]
        p.append(p_new)
        q.append(q_new)
        nums.append(p_new)
        dens.append(q_new)
    return nums, dens

# Continued fractions
# π = [3; 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2, ...]
pi_cf = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2, 1, 84, 2, 1, 1, 15, 3, 13]
# e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, ...]
e_cf = [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, 1, 1, 12, 1, 1, 14, 1, 1, 16]
# √2 = [1; 2, 2, 2, 2, ...]
sqrt2_cf = [1] + [2] * 50
# φ = [1; 1, 1, 1, 1, ...]
phi_cf = [1] * 50
# ln(2) = [0; 1, 2, 3, 1, 6, 3, 1, 1, 2, 1, 1, 1, 1, 3, 10, ...]
ln2_cf = [0, 1, 2, 3, 1, 6, 3, 1, 1, 2, 1, 1, 1, 1, 3, 10, 1, 1, 1, 2]

pi_num, pi_den = generate_convergents(pi_cf, 25)
e_num, e_den = generate_convergents(e_cf, 25)
sqrt2_num, sqrt2_den = generate_convergents(sqrt2_cf, 30)
phi_num, phi_den = generate_convergents(phi_cf, 30)
ln2_num, ln2_den = generate_convergents(ln2_cf, 20)

print("=" * 80)
print("DEEP M-VALUE CONSTRUCTION ANALYSIS")
print("=" * 80)

# Focus on n ≡ 2 (mod 3) cases with different d values
cases = [
    (62, 2),  # d=2
    (65, 5),  # d=5
    (68, 1),  # d=1
]

def factor(n, max_iter=10000):
    """Simple factorization."""
    factors = {}
    d = 2
    while d * d <= n and d < max_iter:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def find_convergent_match(m, conv_lists, names, max_combo=3):
    """Try to express m as a product/sum of convergents."""
    matches = []

    # Check single convergents
    for conv_list, name in zip(conv_lists, names):
        for i, c in enumerate(conv_list):
            if c == m:
                matches.append(f"{name}[{i}] = {c}")
            if c > 1 and m % c == 0:
                quotient = m // c
                if quotient < 10**15:  # Reasonable quotient
                    matches.append(f"{name}[{i}] × {quotient} = {c} × {quotient}")

    return matches

print("\n### Detailed Analysis of m[62], m[65], m[68] ###\n")

conv_lists = [pi_num, pi_den, e_num, e_den, sqrt2_num, sqrt2_den, phi_num, phi_den, ln2_num, ln2_den]
conv_names = ["π_n", "π_d", "e_n", "e_d", "√2_n", "√2_d", "φ_n", "φ_d", "ln2_n", "ln2_d"]

for n, d in cases:
    m_n = m_seq[n - 2]
    print(f"n={n}, d={d}, m={m_n}")
    print(f"  m / 2^{n} = {m_n / (2**n):.10f}")
    print(f"  bit_length = {m_n.bit_length()}")

    # Factor
    factors = factor(m_n, 100000)
    print(f"  Small factors: {factors}")

    # Check convergent matches
    matches = find_convergent_match(m_n, conv_lists, conv_names)
    if matches:
        print(f"  Convergent matches:")
        for match in matches[:5]:
            print(f"    {match}")

    # Check if m = 2^n - small_value
    diff = 2**n - m_n
    if abs(diff) < 10**18:
        print(f"  2^{n} - m = {diff}")

    # Check relationship to previous m-values
    if n >= 65:
        prev_m = m_seq[n - 5]  # m[n-3] for same mod class
        ratio = m_n / prev_m
        print(f"  m[{n}] / m[{n-3}] = {ratio:.6f}")

    print()

# Now analyze the formula structure more carefully
print("\n" + "=" * 80)
print("ANALYZING THE NUMERATOR PATTERN")
print("=" * 80)

# The numerator is: 2*k[n-1] + 2^n - k[n]
# For d to be chosen, this must be divisible by k[d]

# Let's compute the numerators for our cases
k_base = {int(k): v for k, v in data['k_base'].items()}
k = k_base.copy()

def get_k(n):
    if n in k:
        return k[n]
    k_prev = get_k(n - 1)
    m_n = m_seq[n - 2]
    d_n = d_seq[n - 2]
    k_d = get_k(d_n)
    k[n] = 2 * k_prev + (2**n) - m_n * k_d
    return k[n]

for n in range(1, 71):
    get_k(n)

print("\n### Numerators for n ≡ 2 (mod 3) ###\n")
for n in [62, 65, 68]:
    numerator = 2*k[n-1] + 2**n - k[n]
    d_actual = d_seq[n-2]
    k_d = get_k(d_actual)
    m_actual = m_seq[n-2]

    print(f"n={n}:")
    print(f"  numerator = {numerator}")
    print(f"  d = {d_actual}, k[d] = {k_d}")
    print(f"  m = numerator / k[d] = {m_actual}")

    # Factor the numerator
    factors = factor(numerator, 100000)
    print(f"  numerator small factors: {factors}")

    # Check what the numerator would be if expressed differently
    print()

# Key insight: The numerator's factorization determines d
# And then m = numerator / k[d]

print("\n" + "=" * 80)
print("PREDICTING FOR n=71")
print("=" * 80)

# For n=71, we need to find what k[71] gives a numerator that follows the pattern
# The numerator will be: 2*k[70] + 2^71 - k[71]

# We know 2*k[70] + 2^71 = 4,302,057,189,444,869,987,810

base_71 = 2*k[70] + 2**71
print(f"\n2*k[70] + 2^71 = {base_71}")
print(f"  mod 3 = {base_71 % 3}")
print(f"  mod 7 = {base_71 % 7}")
print(f"  mod 21 = {base_71 % 21}")

# For the pattern to continue:
# If k[71] ≡ 2 (mod 3), then d[71] = 2
# If k[71] ≡ 20 (mod 21), then d[71] = 5

# Looking at historical k[n] mod 3 for n ≡ 2 (mod 3):
print("\n### Historical k[n] mod 3 and mod 21 ###")
for n in [62, 65, 68]:
    print(f"n={n}: k mod 3 = {k[n] % 3}, mod 21 = {k[n] % 21}, d = {d_seq[n-2]}")

# The pattern seems to be that k[n] mod 3 varies
# k[62] mod 3 = 0, d = 2
# k[65] mod 3 = 2, d = 5 (but numerator is div by 21!)
# k[68] mod 3 = 1, d = 1

# So the key is the NUMERATOR's divisibility, not k's divisibility
print("\n### Actual Pattern: Numerator divisibility determines d ###")
print("For n=62: numerator ≡ 0 (mod 3) but NOT mod 21 → d=2")
print("For n=65: numerator ≡ 0 (mod 21) → d=5")
print("For n=68: numerator ≢ 0 (mod 3) → d=1")

print("\nFor n=71, the numerator = base_71 - k[71]")
print("If k[71] ≡ base_71 (mod 3) = 2, then numerator ≡ 0 (mod 3)")
print("If k[71] ≡ base_71 (mod 21) = 20, then numerator ≡ 0 (mod 21)")
