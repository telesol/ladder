#!/usr/bin/env python3
"""
BRIDGE MATH: Compute constraints from k[75] back to k[71]
NO ASSUMPTIONS - only computation from known values
"""

import sqlite3

# Load known keys
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()

# Get all known keys
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
keys = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

print("=" * 80)
print("BRIDGE MATH: Computing constraints from known anchor points")
print("=" * 80)

# Known values
k69 = keys[69]
k70 = keys[70]
k75 = keys[75]
k80 = keys[80]

print(f"\nKNOWN VALUES (from database):")
print(f"k[69] = {k69:,}")
print(f"k[70] = {k70:,}")
print(f"k[75] = {k75:,}")
print(f"k[80] = {k80:,}")

print("\n" + "=" * 80)
print("CONSTRAINT 1: From k[75]")
print("=" * 80)

# k[75] = 9*k[72] + offset[75]
# k[72] = 9*k[69] + offset[72]
# Therefore: k[75] = 81*k[69] + 9*offset[72] + offset[75]

constraint1 = k75 - 81 * k69
print(f"\nk[75] = 81*k[69] + 9*offset[72] + offset[75]")
print(f"Therefore: 9*offset[72] + offset[75] = k[75] - 81*k[69]")
print(f"           9*offset[72] + offset[75] = {constraint1:,}")

print("\n" + "=" * 80)
print("CONSTRAINT 2: From k[80]")
print("=" * 80)

# Similar chain from k[80] back
# k[80] = 9*k[77] + offset[80]
# k[77] = 9*k[74] + offset[77]
# k[74] = 9*k[71] + offset[74]
# So: k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]

# But also:
# k[77] = 9*k[74] + offset[77]
# k[74] = 9*k[71] + offset[74]
# k[71] = 9*k[68] + offset[71]
# k[68] is KNOWN!

k68 = keys[68]
print(f"\nk[68] = {k68:,}")

# Chain: k[71] = 9*k[68] + offset[71]
# So k[80] involves offset[71], offset[74], offset[77], offset[80]

# Let's compute what we can from known offsets
print("\n" + "=" * 80)
print("KNOWN OFFSETS (n=31 to 70)")
print("=" * 80)

offsets = {}
for n in range(34, 71):  # Need k[n-3] to exist
    if n in keys and (n-3) in keys:
        offsets[n] = keys[n] - 9 * keys[n-3]

print("\nOffset[n] = k[n] - 9*k[n-3]:")
print("-" * 50)
for n in sorted(offsets.keys())[-15:]:  # Last 15
    print(f"offset[{n}] = {offsets[n]:,}")

print("\n" + "=" * 80)
print("OFFSET RATIOS (consecutive)")
print("=" * 80)

print("\noffset[n] / offset[n-1]:")
for n in range(57, 71):
    if n in offsets and (n-1) in offsets and offsets[n-1] != 0:
        ratio = offsets[n] / offsets[n-1]
        print(f"offset[{n}] / offset[{n-1}] = {ratio:.6f}")

print("\n" + "=" * 80)
print("OFFSET DIFFERENCES")
print("=" * 80)

print("\noffset[n] - offset[n-1]:")
for n in range(63, 71):
    if n in offsets and (n-1) in offsets:
        diff = offsets[n] - offsets[n-1]
        print(f"offset[{n}] - offset[{n-1}] = {diff:,}")

print("\n" + "=" * 80)
print("3-STEP OFFSET PATTERN")
print("=" * 80)

print("\noffset[n] / offset[n-3]:")
for n in range(60, 71):
    if n in offsets and (n-3) in offsets and offsets[n-3] != 0:
        ratio = offsets[n] / offsets[n-3]
        print(f"offset[{n}] / offset[{n-3}] = {ratio:.6f}")

print("\n" + "=" * 80)
print("KEY CONSTRAINT EQUATION")
print("=" * 80)
print(f"\n9*offset[72] + offset[75] = {constraint1:,}")
print("\nTo solve, we need the GENERATION RULE for offset[n]")
print("NOT an assumption about ratios!")
