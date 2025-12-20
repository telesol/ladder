#!/usr/bin/env python3
"""
Analyze m-value growth patterns to find the exact construction rule.
"""

import json

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

print("=" * 80)
print("M-SEQUENCE GROWTH PATTERN ANALYSIS")
print("=" * 80)

# For d=1 cases only
print("\n### Growth for d=1 cases ###\n")
d1_values = []
for n in range(4, 71):
    idx = n - 2
    if idx < len(d_seq) and d_seq[idx] == 1:
        m_n = m_seq[idx]
        d1_values.append((n, m_n))

print(f"Found {len(d1_values)} cases with d=1\n")

# Look at ratios between consecutive d=1 cases
print("Consecutive d=1 ratios:")
for i in range(1, len(d1_values)):
    n_curr, m_curr = d1_values[i]
    n_prev, m_prev = d1_values[i-1]
    gap = n_curr - n_prev
    ratio = m_curr / m_prev
    if n_curr >= 50:
        print(f"m[{n_curr}]/m[{n_prev}] = {ratio:.6f} (gap={gap})")

# Look at m[n] / 2^n relationship for d=1
print("\n### m[n] / 2^n for d=1 cases ###\n")
for n, m_n in d1_values[-10:]:
    ratio = m_n / (2**n)
    print(f"n={n}: m[{n}]/2^{n} = {ratio:.10f}")

# For n=68 (d=1), analyze the structure
print("\n" + "=" * 80)
print("DETAILED ANALYSIS OF RECENT d=1 CASES")
print("=" * 80)

for n, m_n in d1_values[-5:]:
    print(f"\nm[{n}] = {m_n}")
    print(f"  bit_length = {m_n.bit_length()}")
    print(f"  m[{n}] / 2^{n} = {m_n / 2**n:.10f}")
    print(f"  m[{n}] / 2^(n-1) = {m_n / 2**(n-1):.10f}")

    # Check some specific patterns
    two_n = 2**n
    diff = two_n - m_n
    print(f"  2^{n} - m[{n}] = {diff}")
    if abs(diff) < 10**15:
        print(f"    (small difference!)")

# Check if m[n] = 2^n - small_value pattern
print("\n### Checking m[n] = 2^n - small pattern ###\n")
for n, m_n in d1_values[-10:]:
    two_n = 2**n
    diff = two_n - m_n
    print(f"n={n}: 2^{n} - m[{n}] = {diff}")
    print(f"       log2(|diff|) ≈ {abs(diff).bit_length() if diff != 0 else 0}")

# For d=2 cases
print("\n" + "=" * 80)
print("ANALYSIS OF d=2 CASES")
print("=" * 80)

d2_values = []
for n in range(4, 71):
    idx = n - 2
    if idx < len(d_seq) and d_seq[idx] == 2:
        m_n = m_seq[idx]
        d2_values.append((n, m_n))

print(f"\nFound {len(d2_values)} cases with d=2\n")

for n, m_n in d2_values[-5:]:
    print(f"m[{n}] = {m_n}, bit_length = {m_n.bit_length()}")

# Pattern: m[n] ratio to 2^n
print("\n### m[n] / 2^n for recent d=2 cases ###")
for n, m_n in d2_values[-5:]:
    ratio = m_n / (2**n)
    print(f"n={n}: m[{n}]/2^{n} = {ratio:.10f}")
