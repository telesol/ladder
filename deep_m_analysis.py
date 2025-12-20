#!/usr/bin/env python3
"""
Deep analysis of m-sequence patterns for deriving m[71].
"""

import json

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

def factor_partial(n, max_factor=10000):
    """Extract small factors up to max_factor."""
    factors = []
    orig = n
    for p in range(2, min(max_factor, int(n**0.5) + 1)):
        while n % p == 0:
            factors.append(p)
            n //= p
    return factors, n

# Key convergents
sqrt2_num = [1, 3, 7, 17, 41, 99, 239, 577, 1393, 3363, 8119, 19601, 47321, 114243, 275807, 665857, 1607521, 3880899, 9369319, 22619537, 54608393, 131836323, 318281039, 768398401, 1855077841]
sqrt2_den = [1, 2, 5, 12, 29, 70, 169, 408, 985, 2378, 5741, 13860, 33461, 80782, 195025, 470832, 1136689, 2744210, 6625109, 15994428, 38613965, 93222358, 225058681, 543339720, 1311738121]

pi_num = [3, 22, 333, 355, 103993, 104348, 208341, 312689, 833719, 1146408, 4272943, 5419351, 80143857, 165707065, 245850922]
pi_den = [1, 7, 106, 113, 33102, 33215, 66317, 99532, 265381, 364913, 1360120, 1725033, 25510582, 52746197, 78256779]

e_num = [2, 3, 8, 11, 19, 87, 106, 193, 1264, 1457, 2721, 23225, 25946, 49171, 517656]
e_den = [1, 1, 3, 4, 7, 32, 39, 71, 465, 536, 1001, 8544, 9545, 18089, 190435]

ln2_num = [0, 1, 2, 9, 11, 75, 236, 311, 547, 1641, 2188, 3829, 5470, 9299, 32966]
ln2_den = [1, 1, 3, 13, 16, 109, 341, 450, 791, 2373, 3164, 5537, 8701, 13441, 47684]

print("=" * 80)
print("DEEP M-SEQUENCE ANALYSIS FOR n=71")
print("=" * 80)

# Analyze recent m-values for n ≡ 2 (mod 3)
print("\n### M-values for n ≡ 2 (mod 3) ###\n")
for n in range(50, 71):
    if n % 3 == 2:
        idx = n - 2
        if idx < len(m_seq):
            m_n = m_seq[idx]
            d_n = d_seq[idx]
            factors, remainder = factor_partial(m_n, 1000)
            print(f"n={n}: m={m_n}, d={d_n}")
            if factors:
                print(f"      factors: {factors}, remainder: {remainder}")

            # Check for 17 factor
            if 17 in factors:
                quotient = m_n // 17
                print(f"      17-network: m = 17 × {quotient}")

            # Check for 19 factor (e-network)
            if 19 in factors:
                quotient = m_n // 19
                print(f"      19-network: m = 19 × {quotient}")
            print()

# Look at ratios between consecutive m-values in same mod class
print("\n### Ratio analysis for n ≡ 2 (mod 3) ###\n")
prev_m = None
prev_n = None
for n in range(50, 71):
    if n % 3 == 2:
        idx = n - 2
        if idx < len(m_seq):
            m_n = m_seq[idx]
            if prev_m is not None and prev_m != 0:
                ratio = m_n / prev_m
                print(f"m[{n}] / m[{prev_n}] = {ratio:.6f}")
            prev_m = m_n
            prev_n = n

# Now look at the relationship with d-sequence
print("\n### Relationship between m and d ###\n")
print("For n ≡ 2 (mod 3), looking at (m, d) pairs:")
for n in range(4, 71):
    if n % 3 == 2:
        idx = n - 2
        if idx < len(m_seq):
            m_n = m_seq[idx]
            d_n = d_seq[idx]
            print(f"n={n:2d}: d={d_n}, log2(m)≈{m_n.bit_length()}")

# Key insight: check if m-values are products of convergents at specific indices
print("\n" + "=" * 80)
print("TESTING PRODUCT HYPOTHESIS")
print("=" * 80)

# For n=68 (d=1, n%3=2): m=340563526170809298635
# Check if this is a product of convergents

m_68 = m_seq[66]  # n=68 -> idx=66
print(f"\nm[68] = {m_68}")

# Try to find if m_68 = A × B where A, B are convergents
# Since m_68 is huge, we check if it's divisible by known convergents
for name, conv_list in [("√2_num", sqrt2_num), ("√2_den", sqrt2_den),
                         ("π_num", pi_num), ("π_den", pi_den),
                         ("e_num", e_num), ("e_den", e_den)]:
    for i, c in enumerate(conv_list):
        if c > 1 and m_68 % c == 0:
            quotient = m_68 // c
            print(f"  m[68] = {name}[{i}] × {quotient} = {c} × {quotient}")

# Same for m[70]
m_70 = m_seq[68]
print(f"\nm[70] = {m_70}")
for name, conv_list in [("√2_num", sqrt2_num), ("√2_den", sqrt2_den),
                         ("π_num", pi_num), ("π_den", pi_den),
                         ("e_num", e_num), ("e_den", e_den)]:
    for i, c in enumerate(conv_list):
        if c > 1 and m_70 % c == 0:
            quotient = m_70 // c
            print(f"  m[70] = {name}[{i}] × {quotient} = {c} × {quotient}")

# Check the 17-network hypothesis more carefully
print("\n" + "=" * 80)
print("17-NETWORK ANALYSIS")
print("=" * 80)

for n in range(60, 71):
    idx = n - 2
    if idx < len(m_seq):
        m_n = m_seq[idx]
        if m_n % 17 == 0:
            quotient = m_n // 17
            print(f"m[{n}] = 17 × {quotient}")
            # Check if quotient is divisible by other convergents
            for name, conv_list in [("√2_num", sqrt2_num), ("π_den", pi_den)]:
                for i, c in enumerate(conv_list):
                    if c > 1 and quotient % c == 0:
                        q2 = quotient // c
                        print(f"       = 17 × {name}[{i}] × {q2}")
                        print(f"       = 17 × {c} × {q2}")

# Hypothesis: m[71] might follow pattern from m[67]
print("\n" + "=" * 80)
print("EXTENDING THE PATTERN TO n=71")
print("=" * 80)

m_67 = m_seq[65]
print(f"\nm[67] = {m_67}")
print(f"m[67] / 17 = {m_67 // 17}")
print(f"m[67] % 17 = {m_67 % 17}")

if m_67 % 17 == 0:
    q67 = m_67 // 17
    print(f"\nm[67] = 17 × {q67}")
    if q67 % 2 == 0:
        print(f"     = 17 × 2 × {q67 // 2}")
        print(f"     = 34 × {q67 // 2}")

# The key question: what is the pattern in q67, q70, etc.?
print("\n### Looking for quotient patterns ###")
for n in [67, 68, 70]:
    idx = n - 2
    m_n = m_seq[idx]
    if m_n % 17 == 0:
        q = m_n // 17
        print(f"m[{n}] / 17 = {q}")
        print(f"          bit_length = {q.bit_length()}")
