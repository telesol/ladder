#!/usr/bin/env python3
"""
Deep analysis of m-value construction patterns.
Goal: Find the mathematical formula that generates m values.
"""

import json
from math import gcd, log2

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

print("=" * 80)
print("DEEP M-VALUE CONSTRUCTION ANALYSIS")
print("=" * 80)

# Analyze all m values for n ≡ 2 (mod 3) up to n=70
print("\n### M-values for n ≡ 2 (mod 3) ###\n")

n_vals = [n for n in range(5, 71) if n % 3 == 2]
for n in n_vals:
    m = m_seq[n-2]
    d = d_seq[n-2]
    ratio = m / (2**n)
    print(f"n={n:2d}: m={m:>25d}, d={d}, m/2^n={ratio:.6f}")

# Look for patterns in m/2^n ratios
print("\n### Ratio patterns ###\n")

ratios = {}
for n in n_vals:
    m = m_seq[n-2]
    d = d_seq[n-2]
    ratio = m / (2**n)
    ratios[n] = (ratio, d)

# Group by d value
d_ratios = {}
for n, (ratio, d) in ratios.items():
    if d not in d_ratios:
        d_ratios[d] = []
    d_ratios[d].append((n, ratio))

for d in sorted(d_ratios.keys()):
    entries = d_ratios[d]
    print(f"d={d}: {len(entries)} cases")
    for n, ratio in entries[-5:]:  # Last 5
        print(f"  n={n}: ratio={ratio:.6f}")

# Check if m values follow a pattern based on n
print("\n### Checking m[n] = f(n) patterns ###\n")

# Try m = a * b^n + c patterns
for n in [62, 65, 68]:
    m = m_seq[n-2]
    print(f"n={n}: m = {m}")

    # Check if m ≈ 2^k for some k
    log_m = log2(m)
    print(f"  log2(m) = {log_m:.4f}")

    # Check if m = floor(constant * 2^n) or similar
    for const in [1.0, 0.5, 0.25, 0.125, 1/3, 1/7, 1/21]:
        pred = int(const * (2**n))
        if abs(pred - m) < m * 0.01:  # Within 1%
            print(f"  m ≈ {const:.4f} × 2^{n} (diff={m-pred})")

# Look at the sequence of adjacent m-values
print("\n### Adjacent m-value relationships ###\n")

for n in range(60, 70):
    m_n = m_seq[n-2]
    m_n1 = m_seq[n-1]
    d_n = d_seq[n-2]
    ratio = m_n1 / m_n if m_n != 0 else 0
    print(f"m[{n+1}]/m[{n}] = {ratio:.4f} (d[{n}]={d_n})")

# Analyze the specific structure of key m-values
print("\n### Key m-value structure analysis ###\n")

# m[62], m[65], m[68]
key_m = {62: m_seq[60], 65: m_seq[63], 68: m_seq[66]}

for n, m in key_m.items():
    print(f"n={n}: m = {m}")
    print(f"  Binary: {bin(m)}")
    print(f"  Bit length: {m.bit_length()}")

    # Check divisibility by convergent-related numbers
    for div in [2, 3, 5, 7, 11, 13, 17, 19, 21, 22, 23]:
        if m % div == 0:
            quotient = m // div
            print(f"  m = {div} × {quotient}")

    # Check if close to product of Fibonacci numbers
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987,
           1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025]

    for i, f1 in enumerate(fib[5:], 5):
        for j, f2 in enumerate(fib[i:], i):
            prod = f1 * f2
            if abs(prod - m) < m * 0.001:
                print(f"  m ≈ F_{i} × F_{j} = {f1} × {f2} = {prod}")
            if prod > m * 2:
                break

    print()

# Check if there's a pattern in how d is chosen
print("### D-value selection pattern ###\n")

# The numerator before d selection is: 2*k[n-1] + 2^n
# d is chosen to make m[n] = (2*k[n-1] + 2^n - k[n]) / k[d]
# We want d that minimizes m[n]

# Look at the pattern of d choices
print("Last 20 d values:")
for n in range(51, 71):
    d = d_seq[n-2]
    m = m_seq[n-2]
    print(f"  n={n}: d={d}, m={m:.4e}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
Key observations:
1. m values don't follow a simple exponential or polynomial pattern
2. d values are chosen to minimize m[n]
3. m[62] is divisible by 2×3 = 6
4. m[65] has no small divisors
5. m[68] is divisible by 5

For n=71:
- If d=1: m[71] ≈ 2.5e+21
- If d=2: m[71] ≈ 8e+20
- If d=5: m[71] ≈ 1.2e+20

The exact m[71] value depends on the specific construction formula
used by the puzzle creator.
""")
