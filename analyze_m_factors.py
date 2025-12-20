#!/usr/bin/env python3
"""
Factor analysis of m-values for n ≡ 2 (mod 3) to find construction pattern.
"""

import json
from math import gcd

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

# Key convergents for factorization analysis
pi_num = [3, 22, 333, 355, 103993, 104348, 208341, 312689, 833719, 1146408, 4272943, 5419351]
pi_den = [1, 7, 106, 113, 33102, 33215, 66317, 99532, 265381, 364913, 1360120, 1725033]
sqrt2_num = [1, 3, 7, 17, 41, 99, 239, 577, 1393, 3363, 8119, 19601, 47321, 114243, 275807, 665857]
sqrt2_den = [1, 2, 5, 12, 29, 70, 169, 408, 985, 2378, 5741, 13860, 33461, 80782, 195025, 470832]
e_num = [2, 3, 8, 11, 19, 87, 106, 193, 1264, 1457, 2721, 23225, 25946, 49171, 517656]
e_den = [1, 1, 3, 4, 7, 32, 39, 71, 465, 536, 1001, 8544, 9545, 18089, 190435]
ln2_num = [0, 1, 2, 9, 11, 75, 236, 311, 547, 1641, 2188, 3829, 5470, 9299, 32966]
ln2_den = [1, 1, 3, 13, 16, 109, 341, 450, 791, 2373, 3164, 5537, 8701, 13441, 47684]

# Primes to check
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

def small_factors(n, max_factor=1000):
    """Get small prime factors."""
    factors = []
    temp = n
    for p in primes:
        if p > max_factor:
            break
        while temp % p == 0:
            factors.append(p)
            temp //= p
    return factors, temp

print("=" * 80)
print("FACTOR ANALYSIS OF M-VALUES FOR n ≡ 2 (mod 3)")
print("=" * 80)

# Analyze each n ≡ 2 (mod 3) case
mod2_cases = []
for n in range(50, 71):
    if n % 3 == 2:
        idx = n - 2
        m_n = m_seq[idx]
        d_n = d_seq[idx]
        mod2_cases.append((n, m_n, d_n))

print("\n### Full Factor Analysis ###\n")

for n, m_n, d_n in mod2_cases:
    print(f"n={n}, m[{n}] = {m_n}, d={d_n}")

    # Small prime factors
    factors, remainder = small_factors(m_n, 1000)
    if factors:
        print(f"  Small factors: {factors}")
        print(f"  Remainder: {remainder}")

    # Check divisibility by key convergents
    for name, conv_list in [("17", [17]), ("19", [19]), ("22", [22]),
                            ("√2_num", sqrt2_num[:10]), ("π_num", pi_num[:8])]:
        for i, c in enumerate(conv_list):
            if c > 1 and m_n % c == 0:
                quotient = m_n // c
                if len(conv_list) == 1:
                    print(f"  Divisible by {name}: m = {name} × {quotient}")
                else:
                    print(f"  Divisible by {name}[{i}]={c}: m = {c} × {quotient}")

    # Check m/2^n ratio
    ratio = m_n / (2**n)
    print(f"  m/2^n = {ratio:.6f}")
    print()

# Look for patterns in consecutive m-values
print("\n" + "=" * 80)
print("RATIO ANALYSIS: m[n+3] / m[n]")
print("=" * 80 + "\n")

for i in range(len(mod2_cases) - 1):
    n1, m1, d1 = mod2_cases[i]
    n2, m2, d2 = mod2_cases[i + 1]
    ratio = m2 / m1
    print(f"m[{n2}] / m[{n1}] = {ratio:.6f} (d: {d1} → {d2})")

# Analyze the d-value pattern
print("\n" + "=" * 80)
print("D-VALUE PATTERN ANALYSIS")
print("=" * 80)

print("\nFor n ≡ 2 (mod 3), d-values are:")
d_pattern = [d for (n, m, d) in mod2_cases]
print(f"d = {d_pattern}")

# Check if d depends on n mod 9
print("\nCheck n mod 9:")
for n, m, d in mod2_cases:
    print(f"n={n}, n mod 9 = {n % 9}, d={d}")

# Check n mod 12
print("\nCheck n mod 12:")
for n, m, d in mod2_cases:
    print(f"n={n}, n mod 12 = {n % 12}, d={d}")

# Based on pattern, predict d[71]
print("\n" + "=" * 80)
print("PREDICTION FOR d[71]")
print("=" * 80)

print("\nPattern observed for n ≡ 2 (mod 3):")
print("n=50 (mod 9 = 5): d=1")
print("n=53 (mod 9 = 8): d=1")
print("n=56 (mod 9 = 2): d=1")
print("n=59 (mod 9 = 5): d=1")
print("n=62 (mod 9 = 8): d=2")
print("n=65 (mod 9 = 2): d=5")
print("n=68 (mod 9 = 5): d=1")
print()
print("For n=71: n mod 9 = 8")
print("Looking at n mod 9 = 8 cases: n=53 had d=1, n=62 had d=2")
print("So d[71] could be 1 or 2 based on n mod 9 = 8 pattern")

# Compute valid m[71] ranges for each d
print("\n" + "=" * 80)
print("VALID m[71] RANGES")
print("=" * 80)

# Known values
k_70 = 970436974005023690481
two_71 = 2**71
k = {1: 1, 2: 3, 3: 7, 5: 21}

# k[71] must be in [2^70, 2^71)
k71_min = 2**70
k71_max = 2**71 - 1

# k[71] = 2*k[70] + 2^71 - m[71]*k[d[71]]
# m[71] = (2*k[70] + 2^71 - k[71]) / k[d[71]]

base = 2*k_70 + two_71

for d, k_d in k.items():
    m71_min = (base - k71_max) // k_d
    m71_max = (base - k71_min) // k_d
    if m71_min < 0:
        m71_min = 0
    print(f"\nd={d} (k[{d}]={k_d}):")
    print(f"  m[71] ∈ [{m71_min}, {m71_max}]")
    print(f"  m[71]/2^71 ∈ [{m71_min/two_71:.6f}, {m71_max/two_71:.6f}]")

    # Check if recent m-values for this d-type fall in similar ratio range
    matching_ratios = []
    for n, m_n, d_n in mod2_cases:
        if d_n == d:
            matching_ratios.append(m_n / (2**n))
    if matching_ratios:
        avg_ratio = sum(matching_ratios) / len(matching_ratios)
        print(f"  Historical avg ratio for d={d}: {avg_ratio:.6f}")
        predicted_m71 = int(avg_ratio * two_71)
        print(f"  Predicted m[71] based on avg: {predicted_m71}")
