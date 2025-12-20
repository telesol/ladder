#!/usr/bin/env python3
"""
Use known k[75], k[80], k[85], k[90] to constrain unknowns
==========================================================

We know: k[75], k[80], k[85], k[90]
We don't know: k[71-74], k[76-79], k[81-84], k[86-89]

Using k[n] = 9 × k[n-3] + offset[n]:
k[75] = 9 × k[72] + offset[75]
k[72] = 9 × k[69] + offset[72]

So: k[75] = 81 × k[69] + 9×offset[72] + offset[75]

This constrains offset[72] + offset[75]/9!
"""

import sqlite3

# Load known k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

print("=" * 80)
print("USING KNOWN k[75], k[80], k[85], k[90] TO CONSTRAIN UNKNOWNS")
print("=" * 80)

# Known values
print("\n### KNOWN VALUES ###")
for n in [69, 70, 75, 80, 85, 90]:
    if n in k:
        print(f"k[{n}] = {k[n]}")

# From k[75], constrain k[72] and offsets
print("\n### CONSTRAINT FROM k[75] ###")
print("k[75] = 9 × k[72] + offset[75]")
print("k[72] = 9 × k[69] + offset[72]")
print()
print("Substituting:")
print("k[75] = 81 × k[69] + 9×offset[72] + offset[75]")
print()

k69 = k[69]
k75 = k[75]
constraint75 = k75 - 81 * k69
print(f"k[75] - 81×k[69] = {k75} - 81×{k69}")
print(f"                 = {k75} - {81 * k69}")
print(f"                 = {constraint75}")
print()
print(f"Therefore: 9×offset[72] + offset[75] = {constraint75}")

# Similarly for k[78] (unknown but can chain)
# k[78] = 9 × k[75] + offset[78]
# We know k[75]!

print("\n### CHAIN FROM k[75] TO k[78] ###")
print("k[78] = 9 × k[75] + offset[78]")
print(f"      = 9 × {k75} + offset[78]")
print(f"      = {9 * k75} + offset[78]")

# And k[80] = 9 × k[77] + offset[80]
# k[77] = 9 × k[74] + offset[77]
# k[74] = 9 × k[71] + offset[74]
# k[71] = 9 × k[68] + offset[71]

print("\n### CONSTRAINT FROM k[80] ###")
print("k[80] = 9^4 × k[68] + 9^3×offset[71] + 9^2×offset[74] + 9×offset[77] + offset[80]")

k68 = k[68]
k80 = k[80]
constraint80 = k80 - (9**4) * k68
print(f"k[80] - 9^4×k[68] = {k80} - {9**4 * k68}")
print(f"                  = {constraint80}")
print()
print("This is the sum: 729×offset[71] + 81×offset[74] + 9×offset[77] + offset[80]")

# From k[75]: 9×offset[72] + offset[75] = constraint75
# From k[80]: 729×offset[71] + 81×offset[74] + 9×offset[77] + offset[80] = constraint80

print("\n### WHAT THIS TELLS US ###")
print(f"""
Constraint 1 (from k[75]):
  9×offset[72] + offset[75] = {constraint75}

Constraint 2 (from k[80]):
  729×offset[71] + 81×offset[74] + 9×offset[77] + offset[80] = {constraint80}

These are VERY large numbers!

Let me check if offsets at this scale have a pattern...
""")

# Analyze recent offsets to estimate magnitude
print("### OFFSET MAGNITUDES ###")
offsets = {}
for n in range(60, 71):
    if n in k and n-3 in k:
        offsets[n] = k[n] - 9 * k[n-3]
        print(f"offset[{n}] = {offsets[n]}")

# Estimate offset[71] magnitude
print("\n### OFFSET MAGNITUDE ESTIMATE ###")
print("Offset growth appears roughly linear in log scale")

import math
for n in [68, 69, 70]:
    if n in offsets:
        log_abs = math.log10(abs(offsets[n]))
        print(f"log10(|offset[{n}]|) = {log_abs:.2f}")

# Rough estimate
print("\nEstimate: |offset[71]| ≈ 10^20 to 10^21")
print("This means k[71] ≈ 9×k[68] ± 10^20")

# Check the range
print("\n### k[71] RANGE CHECK ###")
k68 = k[68]
base = 9 * k68
print(f"9 × k[68] = {base}")
print(f"k[71] must be in range [2^70, 2^71-1]")
print(f"  Min: {2**70}")
print(f"  Max: {2**71 - 1}")
print(f"  9×k[68] = {base}")
print()

if 2**70 <= base <= 2**71 - 1:
    print("9×k[68] is WITHIN the valid range for k[71]!")
    print(f"offset[71] must be between {2**70 - base} and {2**71 - 1 - base}")
else:
    print("9×k[68] is OUTSIDE the valid range")
    if base < 2**70:
        print(f"offset[71] must be at least {2**70 - base}")
    else:
        print(f"offset[71] must be at most {2**71 - 1 - base}")
