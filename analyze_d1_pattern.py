#!/usr/bin/env python3
"""
Analyze m-value pattern specifically for d=1 cases.
If d[71]=1, what pattern does m[71] follow?
"""
import json
import subprocess

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

print("=" * 70)
print("D=1 M-VALUE PATTERN ANALYSIS")
print("=" * 70)
print()

# Collect all d=1 cases
d1_cases = []
for n in range(4, 71):
    d = d_seq[n-2]
    if d == 1:
        m = m_seq[n-2]
        d1_cases.append((n, m))

print(f"Total d=1 cases: {len(d1_cases)}")
print()

print("### All d=1 cases ###")
for n, m in d1_cases:
    print(f"n={n}: m={m}")

print()

# Focus on high-n d=1 cases
print("### High-n d=1 cases (n >= 40) ###")
high_n_d1 = [(n, m) for n, m in d1_cases if n >= 40]
for n, m in high_n_d1:
    print(f"n={n}: m={m}, bits={m.bit_length()}")

print()

# Look for patterns in consecutive d=1 cases
print("### Consecutive d=1 ratios ###")
for i in range(1, len(high_n_d1)):
    n1, m1 = high_n_d1[i-1]
    n2, m2 = high_n_d1[i]
    ratio = m2 / m1 if m1 > 0 else 0
    n_diff = n2 - n1
    print(f"m[{n2}]/m[{n1}] = {ratio:.4f} (Δn={n_diff})")

print()

# Factor recent d=1 m-values
print("### Prime factorization of recent d=1 m-values ###")
for n, m in high_n_d1[-5:]:
    try:
        result = subprocess.run(['factor', str(m)], capture_output=True, text=True, timeout=10)
        print(f"n={n}: {result.stdout.strip()}")
    except:
        print(f"n={n}: {m} (factorization failed)")

print()

# Check for powers of 2 relationship
print("### m vs 2^n relationship for d=1 ###")
for n, m in high_n_d1[-5:]:
    ratio = m / (2**n)
    print(f"n={n}: m/2^n = {ratio:.10f}")

print()

# Check if m relates to n in simple way
print("### m/n^k relationship ###")
for n, m in high_n_d1[-5:]:
    print(f"n={n}: m/n = {m/n:.2e}, m/n^2 = {m/(n*n):.2e}, m/n^3 = {m/(n**3):.2e}")

print()

# For n=71 with d=1, what constraints do we have?
print("### n=71 constraints with d=1 ###")
K = {1: 1, 2: 3, 5: 21, 70: 970436974005023690481}
base = 2 * K[70] + 2**71
min_k71 = 2**70
max_k71 = 2**71 - 1

m71_min = base - max_k71
m71_max = base - min_k71

print(f"m[71] must be in [{m71_min}, {m71_max}]")
print(f"m[71] bit range: [{m71_min.bit_length()}, {m71_max.bit_length()}]")

# What m[71] values would generate by simple growth?
n70, m70 = 70, m_seq[70-2]
d70 = d_seq[70-2]
print(f"m[70] = {m70}, d[70] = {d70}")

# If d[70]=2 and d[71]=1, m might grow differently
# Look at transition from d=2 to d=1 in history
print()
print("### d-value transitions ###")
for i in range(1, len(d_seq)):
    n = i + 2
    if i > 0 and d_seq[i] == 1 and d_seq[i-1] == 2:
        m_curr = m_seq[i]
        m_prev = m_seq[i-1]
        ratio = m_curr / m_prev
        print(f"n={n}: d changed 2→1, m[{n}]/m[{n-1}] = {ratio:.4f}")

print()
print("=" * 70)
print("FINDING: m[71] range for d=1 is [1.94e21, 3.12e21]")
print("Need to find exact construction within this range")
print("=" * 70)
