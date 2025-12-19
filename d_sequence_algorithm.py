#!/usr/bin/env python3
"""
Attack the d-sequence generation algorithm.
Goal: Find a formula that generates d[n] from n.
"""

import json

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

d_seq = data['d_seq']

def d(n):
    if n < 2 or n > 71:
        return None
    return d_seq[n - 2]

print("=" * 70)
print("D-SEQUENCE ALGORITHM SEARCH")
print("=" * 70)

# Key observation: d=4 at n=8,14,16,24,30
# Let's check the binary pattern more carefully

print("\n### Binary analysis of d=4 positions:")
d4_pos = [n for n in range(2, 71) if d(n) == 4]
print(f"d=4 positions: {d4_pos}")
for n in d4_pos:
    print(f"  n={n:3}: bin={bin(n):>10}, n%8={n%8}, n//8={n//8}")

# Check pattern: is d=4 when n ≡ 0 mod 8 or n ≡ 6 mod 8?
print("\n### Testing: d=4 when n%8 in {0, 6}:")
for n in range(2, 71):
    predicted = 4 if n % 8 in {0, 6} else None
    actual = d(n)
    if predicted == 4:
        match = "✓" if actual == 4 else f"✗ (actual={actual})"
        print(f"n={n:3}: n%8={n%8}, predicted=4, actual={actual} {match}")

# Look at which n have d[n] = n%8 or similar
print("\n### Checking d[n] vs n%k for various k:")
for k in [4, 8, 16]:
    matches = sum(1 for n in range(2, 32) if d(n) == (n % k) or d(n) == (n % k + 1))
    print(f"k={k}: {matches}/30 match d[n] == n%k or n%k+1")

# New idea: check if d[n] relates to the position of lowest set bit
print("\n### d[n] vs lowest_bit_position(n):")
print("n   d[n]  lowest_bit  diff")
for n in range(2, 32):
    lowest = (n & -n).bit_length()
    dv = d(n)
    diff = dv - lowest
    match = "✓" if dv == lowest else ""
    print(f"{n:3} {dv:4}  {lowest:10}  {diff:4}  {match}")

# Check against Ruler function (A001511)
print("\n### d[n] vs Ruler function A001511 (1 + trailing zeros):")
print("n   d[n]  ruler  match")
matches = 0
for n in range(2, 32):
    # Ruler function: 1 + number of trailing zeros in binary
    tz = 0
    x = n - 2  # Offset by 2 since d starts at n=2
    while x > 0 and x % 2 == 0:
        tz += 1
        x //= 2
    ruler = tz + 1
    dv = d(n)
    match = "✓" if dv == ruler else ""
    if dv == ruler:
        matches += 1
    print(f"{n:3} {dv:4}  {ruler:5}  {match}")
print(f"Match rate: {matches}/30 = {100*matches/30:.1f}%")

# Check against various functions of n
print("\n### Testing various formulas:")

# Test: d[n] = 1 + v_2(n) where v_2 is 2-adic valuation
def v2(x):
    """2-adic valuation: highest power of 2 dividing x"""
    if x == 0:
        return float('inf')
    count = 0
    while x % 2 == 0:
        x //= 2
        count += 1
    return count

print("\nTest: d[n] = 1 + v_2(n)")
for n in range(2, 20):
    pred = 1 + v2(n)
    print(f"n={n}: predicted={pred}, actual={d(n)}, match={'✓' if pred == d(n) else ''}")

print("\nTest: d[n] = 1 + v_2(n-1)")
for n in range(2, 20):
    pred = 1 + v2(n - 1) if n > 1 else 1
    print(f"n={n}: predicted={pred}, actual={d(n)}, match={'✓' if pred == d(n) else ''}")

# The d-sequence might not be algorithmic - check if it's related to puzzle structure
print("\n" + "=" * 70)
print("CHECKING IF d[n] RELATES TO k-SEQUENCE PROPERTIES")
print("=" * 70)

# Load k values from database
import sqlite3
conn = sqlite3.connect('db/kh.db')
cursor = conn.cursor()
k_values = {}
for row in cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id"):
    k_values[row[0]] = int(row[1], 16)
conn.close()

print("\n### d[n] vs properties of k[n]:")
print("n   d[n]  k[n]            k[n] mod d[n]  k[n]//k[d[n]]")
for n in range(2, 20):
    dv = d(n)
    kn = k_values.get(n, 0)
    kd = k_values.get(dv, 1)
    print(f"{n:3} {dv:4}  {kn:<14}  {kn % dv if dv > 0 else 0:<13}  {kn // kd if kd > 0 else 0}")

# Check if d[n] is the index j such that k[j] divides something related to k[n]
print("\n### Does k[d[n]] divide k[n]?")
for n in range(2, 20):
    dv = d(n)
    kn = k_values.get(n, 0)
    kd = k_values.get(dv, 1)
    if kd > 0 and kn % kd == 0:
        print(f"n={n}: k[{n}]={kn} = k[{dv}]×{kn//kd} = {kd}×{kn//kd} ✓")
    else:
        print(f"n={n}: k[{n}]={kn} not divisible by k[{dv}]={kd}")
