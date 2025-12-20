#!/usr/bin/env python3
"""
Analyze what determines d[n] - the key insight is d is chosen to MINIMIZE m[n].

For k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
=> m[n] = (2*k[n-1] + 2^n - k[n]) / k[d[n]]

d is chosen such that m[n] is MINIMAL (and positive integer).
"""

import json

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
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

# Compute all k values
for n in range(1, 71):
    get_k(n)

print("=" * 80)
print("ANALYSIS: WHAT DETERMINES d[n]?")
print("=" * 80)

print("\nFor n ≡ 2 (mod 3), analyzing divisibility of (2*k[n-1] + 2^n - k[n]) by k[d]:\n")

# For each n ≡ 2 (mod 3), check which d values divide the numerator
for n in range(50, 71):
    if n % 3 == 2:
        numerator = 2*k[n-1] + (2**n) - k[n]
        m_actual = m_seq[n-2]
        d_actual = d_seq[n-2]

        print(f"n={n}: numerator = {numerator}")

        # Check divisibility by each possible k[d]
        divisibilities = []
        for d in [1, 2, 3, 4, 5, 6, 7, 8]:
            k_d = get_k(d)
            if numerator % k_d == 0:
                m_for_d = numerator // k_d
                divisibilities.append((d, k_d, m_for_d))

        print(f"  Divisible by: ", end="")
        for d, k_d, m_for_d in divisibilities:
            marker = " ← CHOSEN" if d == d_actual else ""
            print(f"d={d}(k={k_d})->m={m_for_d}{marker}, ", end="")
        print()

        # Verify d is chosen to minimize m
        if divisibilities:
            min_m = min(m for d, k_d, m in divisibilities if m > 0)
            chosen_m = m_actual
            if chosen_m == min_m:
                print(f"  ✓ d={d_actual} gives minimum m={chosen_m}")
            else:
                print(f"  ✗ d={d_actual} does NOT give minimum m! chosen={chosen_m}, min={min_m}")
        print()

# Now analyze what makes the numerator divisible by k[2]=3 or k[5]=21
print("\n" + "=" * 80)
print("DIVISIBILITY PATTERN ANALYSIS")
print("=" * 80)

print("\nFor n ≡ 2 (mod 3), check numerator mod 3 and mod 21:\n")

for n in range(50, 71):
    if n % 3 == 2:
        numerator = 2*k[n-1] + (2**n) - k[n]
        mod3 = numerator % 3
        mod7 = numerator % 7
        mod21 = numerator % 21
        d_actual = d_seq[n-2]
        print(f"n={n}: num mod 3 = {mod3}, num mod 7 = {mod7}, num mod 21 = {mod21}, d={d_actual}")

# For n=71, we need to predict what d[71] will be
print("\n" + "=" * 80)
print("PREDICTING d[71]")
print("=" * 80)

# For k[71], we don't know it yet, but we can analyze the structure
# The key insight: d[n] is determined by what k[d] divides (2*k[n-1] + 2^n - k[n])

# Since we don't know k[71], let's think about this differently
# For n=71:
# k[71] = 2*k[70] + 2^71 - m[71]*k[d[71]]

# If d[71] = 1: m[71] = 2*k[70] + 2^71 - k[71]
# If d[71] = 2: m[71] = (2*k[70] + 2^71 - k[71]) / 3
# If d[71] = 5: m[71] = (2*k[70] + 2^71 - k[71]) / 21

# The choice of d depends on whether (2*k[70] + 2^71 - k[71]) is divisible by 3, 7, 21, etc.

# We can compute 2*k[70] + 2^71 mod 3, mod 7, mod 21
base_71 = 2*k[70] + 2**71

print(f"\nFor n=71:")
print(f"2*k[70] + 2^71 = {base_71}")
print(f"  mod 3 = {base_71 % 3}")
print(f"  mod 7 = {base_71 % 7}")
print(f"  mod 21 = {base_71 % 21}")

# k[71] must be in range [2^70, 2^71), and we can check what values of k[71] mod 3, 7, 21
# would make the numerator divisible by 3, 7, 21

print("\nFor d=2 (k[2]=3) to be optimal, we need (2*k[70] + 2^71 - k[71]) mod 3 = 0")
print(f"Since (2*k[70] + 2^71) mod 3 = {base_71 % 3}, we need k[71] mod 3 = {base_71 % 3}")

print("\nFor d=5 (k[5]=21) to be possible, we need (2*k[70] + 2^71 - k[71]) mod 21 = 0")
print(f"Since (2*k[70] + 2^71) mod 21 = {base_71 % 21}, we need k[71] mod 21 = {base_71 % 21}")

# Check historical pattern of k[n] mod 3 and mod 21 for n ≡ 2 (mod 3)
print("\n### Historical k[n] mod 3 and mod 21 for n ≡ 2 (mod 3) ###")
for n in range(50, 71):
    if n % 3 == 2:
        d_n = d_seq[n-2]
        print(f"n={n}: k[{n}] mod 3 = {k[n] % 3}, mod 21 = {k[n] % 21}, d={d_n}")
