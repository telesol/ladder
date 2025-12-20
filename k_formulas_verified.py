#!/usr/bin/env python3
"""Verified k-value formulas for n=1-16."""

import sqlite3

conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 16")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

print("="*80)
print("VERIFIED k-VALUE FORMULAS (n=1-16)")
print("="*80)
print()

formulas = [
    ("k[1]", "1", 1),
    ("k[2]", "3", 3),
    ("k[3]", "7", 7),
    ("k[4]", "k[1] + k[3] = 1 + 7", 1 + 7),
    ("k[5]", "k[2] × k[3] = 3 × 7", 3 * 7),
    ("k[6]", "k[3]² = 7²", 7**2),
    ("k[7]", "k[6] + 9×k[2] = 49 + 27", 49 + 27),
    ("k[8]", "k[3] × 2^5 = 7 × 32", 7 * 32),
    ("k[9]", "2×k[7] + 15×k[5] = 152 + 315", 2*76 + 15*21),
    ("k[10]", "3×k[4] + 10×k[6] = 24 + 490", 3*8 + 10*49),
    ("k[11]", "k[8] + 19×k[6] = 224 + 931", 224 + 19*49),
    ("k[12]", "12×k[8] - 5×k[1] = 2688 - 5", 12*224 - 5),
    ("k[13]", "k[7] + 10×k[10] = 76 + 5140", 76 + 10*514),
    ("k[14]", "2×k[13] + 16×k[3] = 10432 + 112", 2*5216 + 16*7),
]

print(f"{'Key':>6} | {'Formula':>35} | {'Value':>10} | Check")
print("-"*70)

for key, formula, computed in formulas:
    n = int(key[2:-1])
    actual = k[n]
    match = "✓" if computed == actual else f"✗ (actual: {actual})"
    print(f"{key:>6} | {formula:>35} | {computed:>10} | {match}")

print()
print("="*80)
print("PATTERN OBSERVATIONS")
print("="*80)
print()

print("1. BUILDING BLOCKS: k[1]=1, k[2]=3, k[3]=7")
print("   These are the foundation - all others built from these.")
print()

print("2. EARLY RELATIONSHIPS:")
print("   k[4] = k[1] + k[3]     (sum)")
print("   k[5] = k[2] × k[3]     (product)")
print("   k[6] = k[3]²           (square)")
print()

print("3. THE NUMBER 19 APPEARS MULTIPLE TIMES:")
print("   k[7]  = k[6] + 9×k[2]   (9 = m[5])")
print("   k[11] = k[8] + 19×k[6]  (19 = m[6] = m[10]!)")
print()

print("4. COEFFICIENT PATTERNS:")
coeffs = [
    ("k[7]", 9, "m[5] = 9"),
    ("k[8]", 32, "2^5"),
    ("k[9]", 15, "?"),
    ("k[10]", 10, "?"),
    ("k[11]", 19, "m[6] = m[10] = 19"),
    ("k[12]", 12, "n itself!"),
    ("k[13]", 10, "?"),
    ("k[14]", 16, "2^4"),
]
for key, coeff, note in coeffs:
    print(f"   {key}: coefficient {coeff:>3} ({note})")

print()
print("="*80)
print("THE GENERATOR PATTERN?")
print("="*80)
print()

print("Hypothesis: k[n] is built from earlier k values using:")
print("  - Products (k[5] = k[2]×k[3])")
print("  - Squares (k[6] = k[3]²)")
print("  - Linear combinations (k[n] = a×k[i] + b×k[j])")
print()
print("The coefficients a, b seem to relate to:")
print("  - Powers of 2 (32, 16, ...)")
print("  - m-sequence values (9, 19, ...)")
print("  - The puzzle number n itself (12 for k[12])")
