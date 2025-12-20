#!/usr/bin/env python3
"""
Analyze the d-sequence pattern based on n mod 9.
Looking for correlation between n mod 9 and d[n].
"""

import json

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

d_seq = data['d_seq']
m_seq = data['m_seq']

print("=" * 80)
print("D-SEQUENCE PATTERN BY N MOD 9")
print("=" * 80)

# d_seq[i] = d[i+2], so d_seq[68] = d[70]
# We have d[2] through d[70]

# Group by n mod 9
mod9_groups = {i: [] for i in range(9)}
for i, d in enumerate(d_seq):
    n = i + 2  # d_seq[i] = d[i+2]
    mod9 = n % 9
    mod9_groups[mod9].append((n, d, m_seq[i]))

print("\n### d[n] grouped by n mod 9 ###\n")
for mod_val in range(9):
    print(f"n ≡ {mod_val} (mod 9):")
    entries = mod9_groups[mod_val]
    # Show last few entries
    for n, d, m in entries[-5:]:
        print(f"  n={n}: d={d}, m={m:.4e}")
    print()

# Focus on n ≡ 8 (mod 9) since that's where n=62, n=71 are
print("=" * 80)
print("FOCUS: n ≡ 8 (mod 9) - includes n=62 and n=71")
print("=" * 80)
print()

for n, d, m in mod9_groups[8]:
    print(f"n={n}: d={d}, m/2^n = {m / (2**n):.6f}")

# Also look at n ≡ 2 (mod 3) pattern
print("\n" + "=" * 80)
print("n ≡ 2 (mod 3) pattern")
print("=" * 80)
print()

for i, d in enumerate(d_seq):
    n = i + 2
    if n % 3 == 2 and n >= 50:
        m = m_seq[i]
        print(f"n={n}: d={d}, m/2^n = {m / (2**n):.6f}, m = {m:.6e}")

# Key observation: n mod 9 gives more specific prediction
print("\n" + "=" * 80)
print("KEY OBSERVATION")
print("=" * 80)

# n=62 mod 9 = 8, d=2
# n=65 mod 9 = 2, d=5
# n=68 mod 9 = 5, d=1
# n=71 mod 9 = 8 -> expect d=2?

print("""
n=62: n mod 9 = 8, d[62] = 2
n=65: n mod 9 = 2, d[65] = 5
n=68: n mod 9 = 5, d[68] = 1
n=71: n mod 9 = 8 -> expect d = 2? (same as n=62)

This suggests n=71 has d=2!
""")

# Find all n ≡ 8 (mod 9) and check their d values
print("All n ≡ 8 (mod 9) cases:")
for n, d, m in mod9_groups[8]:
    print(f"  n={n}: d={d}")

# Count d-value frequencies for n ≡ 8 (mod 9)
d_counts = {}
for n, d, m in mod9_groups[8]:
    d_counts[d] = d_counts.get(d, 0) + 1
print(f"\nFrequency of d values for n ≡ 8 (mod 9): {d_counts}")
