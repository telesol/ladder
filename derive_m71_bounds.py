#!/usr/bin/env python3
"""
Derive precise bounds on m[71] from the constraint that k[71] must be 71 bits.
"""

import sqlite3

# Load known k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

print("=" * 80)
print("PRECISE BOUNDS ON m[71]")
print("=" * 80)

k_70 = k[70]
two_71 = 2**71
two_70 = 2**70

print(f"\nk[70] = {k_70}")
print(f"2^70 = {two_70}")
print(f"2^71 = {two_71}")
print(f"2*k[70] + 2^71 = {2*k_70 + two_71}")

# k[71] must be in [2^70, 2^71 - 1]
k71_min = two_70
k71_max = two_71 - 1

print(f"\nk[71] range: [{k71_min}, {k71_max}]")

# Formula: k[71] = 2*k[70] + 2^71 - m[71] * k[d[71]]
# Rearranged: m[71] = (2*k[70] + 2^71 - k[71]) / k[d[71]]

base = 2 * k_70 + two_71

print("\n" + "-" * 80)
print("CASE 1: d[71] = 1 (k[1] = 1)")
print("-" * 80)

# m[71] = base - k[71]
m71_max_d1 = base - k71_min
m71_min_d1 = base - k71_max

print(f"m[71] range if d=1: [{m71_min_d1}, {m71_max_d1}]")
print(f"Midpoint: {(m71_min_d1 + m71_max_d1) // 2}")

print("\n" + "-" * 80)
print("CASE 2: d[71] = 2 (k[2] = 3)")
print("-" * 80)

k_2 = k[2]
# m[71] * 3 = base - k[71]
# For this to be valid, (base - k[71]) must be divisible by 3

# Check divisibility
print(f"\nChecking (base - k[71]) divisibility by 3:")
print(f"base mod 3 = {base % 3}")
print(f"k71_min mod 3 = {k71_min % 3}")
print(f"k71_max mod 3 = {k71_max % 3}")

# Find k[71] values that make (base - k[71]) divisible by 3
base_mod3 = base % 3
valid_k71_mod3 = base_mod3  # k[71] ≡ base (mod 3) for divisibility

print(f"\nFor d=2, k[71] ≡ {valid_k71_mod3} (mod 3)")

# Adjust range to valid k[71] values
# Find first k71_min that satisfies k[71] ≡ valid_k71_mod3 (mod 3)
k71_min_d2 = k71_min + (valid_k71_mod3 - k71_min % 3) % 3
k71_max_d2 = k71_max - (k71_max % 3 - valid_k71_mod3) % 3
if k71_max_d2 > k71_max:
    k71_max_d2 -= 3

m71_max_d2 = (base - k71_min_d2) // 3
m71_min_d2 = (base - k71_max_d2) // 3

print(f"Valid k[71] range for d=2: [{k71_min_d2}, {k71_max_d2}]")
print(f"m[71] range if d=2: [{m71_min_d2}, {m71_max_d2}]")
print(f"Midpoint: {(m71_min_d2 + m71_max_d2) // 2}")

print("\n" + "-" * 80)
print("CASE 3: d[71] = 5 (k[5] = 21)")
print("-" * 80)

k_5 = k[5]
base_mod21 = base % 21
valid_k71_mod21 = base_mod21

print(f"For d=5, k[71] ≡ {valid_k71_mod21} (mod 21)")

k71_min_d5 = k71_min + (valid_k71_mod21 - k71_min % 21) % 21
k71_max_d5 = k71_max - (k71_max % 21 - valid_k71_mod21) % 21
if k71_max_d5 > k71_max:
    k71_max_d5 -= 21

if k71_min_d5 <= k71_max_d5:
    m71_max_d5 = (base - k71_min_d5) // 21
    m71_min_d5 = (base - k71_max_d5) // 21
    print(f"Valid k[71] range for d=5: [{k71_min_d5}, {k71_max_d5}]")
    print(f"m[71] range if d=5: [{m71_min_d5}, {m71_max_d5}]")
    print(f"Midpoint: {(m71_min_d5 + m71_max_d5) // 2}")
else:
    print("No valid k[71] for d=5")

print("\n" + "=" * 80)
print("WHICH d[71] IS MOST LIKELY?")
print("=" * 80)

# From FORMULA_PATTERNS.md:
# For n % 3 = 2:
#   If d=1: Operation = PRODUCT, Constant = √2
#   If d=2: Constant = ln2

print("\nBased on FORMULA_PATTERNS.md for n=71 (n%3=2):")
print("  d=1 → PRODUCT operation, √2 constant")
print("  d=2 → ln2 constant")

# d-sequence statistics for n ≡ 2 (mod 3)
import json
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)
d_seq = data['d_seq']

d_counts = {}
for n in range(4, 71):
    if n % 3 == 2:
        idx = n - 2
        if idx < len(d_seq):
            d_n = d_seq[idx]
            d_counts[d_n] = d_counts.get(d_n, 0) + 1

print(f"\nD-sequence distribution for n ≡ 2 (mod 3):")
for d_val, count in sorted(d_counts.items()):
    print(f"  d={d_val}: {count} times")

# Most common d for n ≡ 2 (mod 3)
most_common_d = max(d_counts, key=d_counts.get)
print(f"\nMost common d for n≡2 (mod 3): d={most_common_d}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

if most_common_d == 1:
    print(f"\nMost likely d[71] = 1")
    print(f"m[71] range: [{m71_min_d1}, {m71_max_d1}]")
    print(f"Expected m[71] ≈ {(m71_min_d1 + m71_max_d1) // 2}")
elif most_common_d == 2:
    print(f"\nMost likely d[71] = 2")
    print(f"m[71] range: [{m71_min_d2}, {m71_max_d2}]")
    print(f"Expected m[71] ≈ {(m71_min_d2 + m71_max_d2) // 2}")

# But we also need to check: which gives an m[71] matching convergent patterns?
print("\n" + "=" * 80)
print("CHECKING CONVERGENT PATTERNS IN RANGES")
print("=" * 80)

# The 17-network pattern: m[n] = 17 × something
# For √2 products: m = 17 × p where p is a prime or √2 convergent

print("\nIf d=1, looking for m[71] = 17 × prime in range:")
m71_mid_d1 = (m71_min_d1 + m71_max_d1) // 2
quotient_d1 = m71_mid_d1 // 17
print(f"  Midpoint / 17 ≈ {quotient_d1}")

print("\nIf d=2, looking for m[71] = 17 × prime in range:")
m71_mid_d2 = (m71_min_d2 + m71_max_d2) // 2
quotient_d2 = m71_mid_d2 // 17
print(f"  Midpoint / 17 ≈ {quotient_d2}")

# Also check recent d values for n near 71
print("\n" + "-" * 80)
print("Recent d values for context:")
for n in [65, 66, 67, 68, 69, 70]:
    idx = n - 2
    print(f"  d[{n}] = {d_seq[idx]}, n%3 = {n%3}")
