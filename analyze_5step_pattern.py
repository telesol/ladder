#!/usr/bin/env python3
"""
Analyze 5-step pattern: k[n+5] = 32 * k[n] + offset(n)
Check every 5 and every 10 from 5 to 130
"""

import sqlite3
from decimal import Decimal, getcontext

# High precision for large numbers
getcontext().prec = 100

# Connect to database and get all known keys
conn = sqlite3.connect('db/kh.db')
cursor = conn.cursor()

# Get all known keys
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
rows = cursor.fetchall()
conn.close()

# Build k dictionary
k = {}
for puzzle_id, priv_hex in rows:
    k[puzzle_id] = int(priv_hex, 16)

print("=" * 80)
print("5-STEP BRIDGE PATTERN ANALYSIS")
print("Formula: k[n+5] = 32 * k[n] + offset(n)")
print("=" * 80)
print()

# Analyze all available 5-step pairs
print("ALL 5-STEP OFFSETS (where both k[n] and k[n+5] are known):")
print("-" * 80)
print(f"{'n':>4} {'n+5':>4} {'offset':>50} {'sign':>6} {'n%5':>4} {'n%10':>5}")
print("-" * 80)

offsets = {}
for n in range(1, 130):
    if n in k and (n+5) in k:
        offset = k[n+5] - 32 * k[n]
        offsets[n] = offset
        sign = "+" if offset >= 0 else "-"
        print(f"{n:>4} {n+5:>4} {offset:>50} {sign:>6} {n%5:>4} {n%10:>5}")

print()
print("=" * 80)
print("EVERY 5TH POSITION ANALYSIS (n = 5, 10, 15, ...)")
print("=" * 80)

every5 = []
for n in range(5, 130, 5):
    if n in k:
        every5.append((n, k[n]))

print(f"\nKnown k[n] for n divisible by 5:")
for n, val in every5:
    ratio = val / (2**n)
    print(f"  k[{n:>3}] = {val:>60} | k/2^n = {ratio:.6f}")

print()
print("=" * 80)
print("OFFSET PATTERN BY n mod 10")
print("=" * 80)

# Group offsets by n mod 10
mod10_groups = {i: [] for i in range(10)}
for n, offset in offsets.items():
    mod10_groups[n % 10].append((n, offset))

for mod_val in range(10):
    if mod10_groups[mod_val]:
        print(f"\nn mod 10 = {mod_val}:")
        signs = []
        for n, offset in mod10_groups[mod_val]:
            sign = "+" if offset >= 0 else "-"
            signs.append(sign)
            print(f"  n={n:>3}: offset = {offset:>45}, sign = {sign}")

        # Check consistency
        if len(set(signs)) == 1:
            print(f"  >>> CONSISTENT: All {signs[0]} signs")
        else:
            print(f"  >>> MIXED signs: {signs}")

print()
print("=" * 80)
print("OFFSET MAGNITUDE ANALYSIS (normalized by 2^n)")
print("=" * 80)

print(f"\n{'n':>4} {'offset/2^n':>20} {'offset/2^(n-5)':>20} {'sign':>6}")
print("-" * 60)

for n in sorted(offsets.keys()):
    offset = offsets[n]
    norm1 = float(offset) / (2**n)
    norm2 = float(offset) / (2**(n-5))
    sign = "+" if offset >= 0 else "-"
    print(f"{n:>4} {norm1:>20.6f} {norm2:>20.6f} {sign:>6}")

print()
print("=" * 80)
print("OFFSET AS FUNCTION OF KNOWN KEYS")
print("=" * 80)

# Try to express offset in terms of other k values
print("\nTrying: offset[n] = c * k[something]")
for n in sorted(offsets.keys())[:20]:  # First 20 for readability
    offset = offsets[n]
    print(f"\nn={n}: offset = {offset}")
    # Check if offset is multiple of any k[i]
    for i in range(1, min(n+10, 71)):
        if i in k and k[i] != 0:
            if offset % k[i] == 0:
                mult = offset // k[i]
                if abs(mult) < 1000:  # Reasonable multiplier
                    print(f"  = {mult} * k[{i}]")

print()
print("=" * 80)
print("SIGN PATTERN SUMMARY")
print("=" * 80)

# Collect signs for analysis
signs_by_n = [(n, "+" if offsets[n] >= 0 else "-") for n in sorted(offsets.keys())]
print("\nSign sequence:")
for i, (n, sign) in enumerate(signs_by_n):
    print(f"{sign}", end="")
    if (i+1) % 20 == 0:
        print(f"  (n={signs_by_n[max(0,i-19)][0]}-{n})")
print()

# Pattern analysis
print("\nPattern by position in 5-block:")
for block_pos in range(5):
    block_signs = [s for n, s in signs_by_n if n % 5 == block_pos]
    print(f"  n mod 5 = {block_pos}: {block_signs[:15]}...")

print()
print("=" * 80)
print("5-STEP RATIO ANALYSIS: k[n+5] / k[n]")
print("=" * 80)

print(f"\n{'n':>4} {'n+5':>4} {'k[n+5]/k[n]':>25} {'ratio/32':>15}")
print("-" * 60)

for n in sorted(offsets.keys()):
    if k[n] > 0:
        ratio = k[n+5] / k[n]
        ratio_over_32 = ratio / 32
        print(f"{n:>4} {n+5:>4} {ratio:>25.6f} {ratio_over_32:>15.6f}")

print()
print("=" * 80)
print("GAP PUZZLE SPECIFIC ANALYSIS (75, 80, 85, 90)")
print("=" * 80)

gap_puzzles = [75, 80, 85, 90]
for gp in gap_puzzles:
    if gp in k:
        print(f"\nk[{gp}] = {k[gp]}")
        print(f"  Binary bits: {k[gp].bit_length()}")
        print(f"  Position in range: {100 * (k[gp] - 2**(gp-1)) / (2**(gp-1)):.2f}%")
        print(f"  k[{gp}] mod 3 = {k[gp] % 3}")
        print(f"  k[{gp}] mod 5 = {k[gp] % 5}")
        print(f"  k[{gp}] mod 17 = {k[gp] % 17}")
        if gp - 5 in k:
            offset = k[gp] - 32 * k[gp-5]
            print(f"  offset from k[{gp-5}]: {offset}")
            print(f"  offset/2^{gp}: {offset/(2**gp):.6f}")

print()
print("=" * 80)
print("10-STEP PATTERN: k[n+10] = 1024 * k[n] + ?")
print("=" * 80)

print(f"\n{'n':>4} {'n+10':>5} {'offset10':>50} {'sign':>6}")
print("-" * 80)

offsets10 = {}
for n in range(1, 130):
    if n in k and (n+10) in k:
        offset10 = k[n+10] - 1024 * k[n]
        offsets10[n] = offset10
        sign = "+" if offset10 >= 0 else "-"
        print(f"{n:>4} {n+10:>5} {offset10:>50} {sign:>6}")

print()
print("=" * 80)
print("COMBINED: offset5[n] + offset5[n+5] vs offset10[n]")
print("=" * 80)

for n in sorted(offsets.keys()):
    if (n+5) in offsets and n in offsets10:
        combined = 32 * offsets[n] + offsets[n+5]
        diff = combined - offsets10[n]
        print(f"n={n}: 32*off5[{n}] + off5[{n+5}] = {combined}, off10[{n}] = {offsets10[n]}, diff = {diff}")
