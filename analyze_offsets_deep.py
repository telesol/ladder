#!/usr/bin/env python3
"""
Deep analysis of mod-3 recursion offsets
========================================

offset[n] = k[n] - 9 × k[n-3]

Goal: Find the formula that generates these offsets.
"""

import sqlite3

# Load k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

# Compute offsets
offsets = {}
for n in range(10, 71):
    if n in k and n-3 in k:
        offsets[n] = k[n] - 9 * k[n-3]

print("=" * 80)
print("DEEP ANALYSIS OF MOD-3 RECURSION OFFSETS")
print("=" * 80)

# Group by n mod 3
print("\n### OFFSETS GROUPED BY n mod 3 ###")
for r in [0, 1, 2]:
    print(f"\n--- n ≡ {r} (mod 3) ---")
    for n in range(10 + r, 31, 3):
        if n in offsets:
            print(f"  offset[{n:2}] = {offsets[n]:>12}")

# Check if offsets relate to earlier k values
print("\n### OFFSET AS LINEAR COMBINATION OF k VALUES ###")
print("Testing: offset[n] = a×k[i] + b for small |a|, |b|")

for n in range(10, 21):
    off = offsets[n]
    found = []
    for i in range(1, n):
        for a in range(-100, 101):
            if a != 0:
                b = off - a * k[i]
                if abs(b) < 100:
                    found.append((a, i, b, abs(a) + abs(b)))

    if found:
        found.sort(key=lambda x: x[3])  # Sort by simplicity
        best = found[0]
        a, i, b, _ = best
        print(f"  offset[{n:2}] = {a:>4}×k[{i}] + {b:>4} = {a}×{k[i]} + {b} = {a*k[i] + b}")

# Check offset[n] / k[j] ratios
print("\n### OFFSET RATIOS ###")
print("offset[n] / k[n-3] ratio:")
for n in range(10, 26):
    if n in offsets and n-3 in k:
        ratio = offsets[n] / k[n-3]
        print(f"  offset[{n:2}] / k[{n-3}] = {offsets[n]:>12} / {k[n-3]:>10} = {ratio:>10.4f}")

# Check offset[n] / 2^something
print("\n### OFFSET / 2^m ANALYSIS ###")
for n in range(10, 21):
    off = abs(offsets[n])
    sign = '+' if offsets[n] >= 0 else '-'

    # Find highest power of 2 that divides
    pow2 = 0
    temp = off
    while temp % 2 == 0 and temp > 0:
        pow2 += 1
        temp //= 2

    quotient = off // (2**pow2) if pow2 > 0 else off
    print(f"  offset[{n:2}] = {sign}2^{pow2} × {quotient}")

# Consecutive offset differences
print("\n### CONSECUTIVE OFFSET DIFFERENCES ###")
print("offset[n] - offset[n-1]:")
prev_off = None
for n in range(10, 26):
    if n in offsets:
        if prev_off is not None:
            diff = offsets[n] - prev_off
            print(f"  offset[{n}] - offset[{n-1}] = {diff}")
        prev_off = offsets[n]

# Offset ratios between same mod 3 class
print("\n### RATIOS WITHIN MOD-3 CLASS ###")
print("offset[n] / offset[n-3]:")
for n in range(13, 31):
    if n in offsets and n-3 in offsets and offsets[n-3] != 0:
        ratio = offsets[n] / offsets[n-3]
        print(f"  offset[{n}] / offset[{n-3}] = {offsets[n]} / {offsets[n-3]} = {ratio:.4f}")

# Check if offsets follow k[n] = 2k[n-1] + something pattern
print("\n### OFFSET DOUBLING PATTERN ###")
print("offset[n] vs 2×offset[n-1]:")
for n in range(11, 21):
    if n in offsets and n-1 in offsets:
        expected = 2 * offsets[n-1]
        actual = offsets[n]
        diff = actual - expected
        print(f"  offset[{n}] = 2×offset[{n-1}] + ({diff}) = 2×{offsets[n-1]} + {diff}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
KEY OBSERVATIONS:
1. Offsets can be expressed as small multiples of k[i] plus small constants
2. Powers of 2 appear in factorizations
3. Ratios within mod-3 classes are irregular

HYPOTHESIS:
The offset might be: offset[n] = f(n, k[earlier values], m[earlier values])

NEXT STEPS:
1. Check if offsets involve m-sequence values
2. Look for convergent expressions
3. Test if offsets = g(n) × k[h(n)] for some functions g, h
""")
