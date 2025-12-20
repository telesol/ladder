#!/usr/bin/env python3
"""
Analyze bit patterns and mathematical structure of m values.
Looking for construction patterns to derive m[71].
"""

import json
from math import gcd, log2

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

print("=" * 80)
print("M-VALUE STRUCTURAL ANALYSIS")
print("=" * 80)

# Key m values for n ≡ 2 (mod 3)
key_n = [50, 53, 56, 59, 62, 65, 68]
for n in key_n:
    m = m_seq[n-2]
    bits = m.bit_length()
    ratio = m / (2**n)

    # Check for simple forms
    # Is m close to 2^k for some k?
    log_m = log2(m)
    nearest_power = round(log_m)

    # Decompose m = a * 2^k + b
    for k in range(bits-10, bits):
        a = m >> k
        b = m - (a << k)
        if a < 100 and b < 10**15:
            print(f"n={n}: m = {a} × 2^{k} + {b}")
            break

    print(f"n={n}: m = {m}")
    print(f"       bits = {bits}, m/2^n = {ratio:.6f}")
    print(f"       log2(m) = {log_m:.4f}")
    print(f"       binary: ...{bin(m)[-20:]}")
    print()

# Focus on n=62 since n=71 mod 9 = 8 same as n=62
print("=" * 80)
print("FOCUS ON n=62 (n mod 9 = 8, d=2)")
print("=" * 80)

m_62 = m_seq[60]
print(f"\nm[62] = {m_62}")
print(f"Factorization: 2 × 3 × 281 × 373 × 2843 × 10487 × 63199")

# Check relationship to powers of 2
print(f"\n2^60 = {2**60}")
print(f"m[62] = 2^60 + {m_62 - 2**60}")
print(f"m[62] = 2^61 - {2**61 - m_62}")

# Check if m[62] = some_constant × 2^k
for k in range(55, 62):
    if m_62 % (2**k) == 0:
        print(f"m[62] = {m_62 // (2**k)} × 2^{k}")
    else:
        q = m_62 // (2**k)
        r = m_62 % (2**k)
        print(f"m[62] = {q} × 2^{k} + {r}")

# Analyze the sequence progression
print("\n" + "=" * 80)
print("M-VALUE PROGRESSION FOR n ≡ 2 (mod 3)")
print("=" * 80)

prev_m = None
for n in [50, 53, 56, 59, 62, 65, 68]:
    m = m_seq[n-2]
    d = d_seq[n-2]
    if prev_m:
        ratio = m / prev_m
        print(f"n={n}: m = {m:.6e}, d={d}, ratio from prev = {ratio:.4f}")
    else:
        print(f"n={n}: m = {m:.6e}, d={d}")
    prev_m = m

# Pattern prediction for n=71
print("\n" + "=" * 80)
print("PATTERN PREDICTION FOR n=71")
print("=" * 80)

# If d=2 (based on n mod 9 = 8 pattern)
# m[71] should be in range [6.47e+20, 1.04e+21]
# What could construct this?

m_68 = m_seq[66]
m_65 = m_seq[63]
m_62 = m_seq[60]

print(f"\nRatios:")
print(f"  m[68]/m[65] = {m_68/m_65:.4f}")
print(f"  m[65]/m[62] = {m_65/m_62:.4f}")
print(f"  m[68]/m[62] = {m_68/m_62:.4f}")

# If similar growth pattern continues
predicted_m71_from_68 = int(m_68 * (m_68/m_65))
predicted_m71_from_65 = int(m_65 * (m_68/m_62))

print(f"\nPredicted m[71]:")
print(f"  From m[68] × (m[68]/m[65]) = {predicted_m71_from_68:.6e}")
print(f"  From m[65] × (m[68]/m[62]) = {predicted_m71_from_65:.6e}")

# Check if these are in valid range for d=2
k_70 = 970436974005023690481
base = 2*k_70 + 2**71
k71_min = 2**70
k71_max = 2**71 - 1

m_min_d2 = (base - k71_max) // 3 + 1
m_max_d2 = (base - k71_min) // 3

print(f"\nValid m[71] range for d=2: [{m_min_d2:.6e}, {m_max_d2:.6e}]")

# More specific analysis: check divisibility by small primes
print("\n" + "=" * 80)
print("DIVISIBILITY ANALYSIS")
print("=" * 80)

def check_divisibility(m, name):
    divisors = []
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 22, 23]:
        if m % p == 0:
            divisors.append(p)
    print(f"{name} divisible by: {divisors}")

for n in [62, 65, 68]:
    m = m_seq[n-2]
    check_divisibility(m, f"m[{n}]")

# Check if m values follow a pattern based on π or other constants
print("\n" + "=" * 80)
print("CONSTANT-BASED CONSTRUCTION CHECK")
print("=" * 80)

# π convergent ratios
pi_conv_ratios = [22/7, 333/106, 355/113, 103993/33102]
# e convergent ratios
e_conv_ratios = [8/3, 11/4, 19/7, 87/32]

for n in [62, 65, 68]:
    m = m_seq[n-2]
    print(f"\nn={n}: m = {m:.6e}")

    # Check if m/2^n is close to any constant ratio
    ratio = m / (2**n)
    for name, const in [("1/π", 1/3.14159265359), ("1/e", 1/2.71828182846),
                        ("1/√2", 1/1.41421356237), ("1/φ", 1/1.61803398875)]:
        if abs(ratio - const) < 0.01:
            print(f"  m/2^n ≈ {name} ({const:.6f})")
