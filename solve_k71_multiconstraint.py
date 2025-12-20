#!/usr/bin/env python3
"""
Solve for k[71] using multiple constraints from k[80], k[85], k[90]
===================================================================

We have:
k[80] = 9^4 × k[68] + 729×off[71] + 81×off[74] + 9×off[77] + off[80]
k[85] = 9^5 × k[70] + (terms involving off[73], off[76], ...)

These give us a system to solve.
"""

import sqlite3

# Load known k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

print("=" * 80)
print("MULTI-CONSTRAINT SOLUTION FOR k[71]")
print("=" * 80)

# Key insight: Let's trace ALL chains from known values

# Chain from k[68] to k[80]:
# k[71] = 9×k[68] + off[71]
# k[74] = 9×k[71] + off[74]
# k[77] = 9×k[74] + off[77]
# k[80] = 9×k[77] + off[80]

# Chain from k[69] to k[81]:
# k[72] = 9×k[69] + off[72]
# k[75] = 9×k[72] + off[75] = known!
# k[78] = 9×k[75] + off[78]
# k[81] = 9×k[78] + off[81]

# Chain from k[70] to k[82]:
# k[73] = 9×k[70] + off[73]
# k[76] = 9×k[73] + off[76]
# k[79] = 9×k[76] + off[79]
# k[82] = 9×k[79] + off[82]

# The k[75] chain gives us:
# k[75] = 81×k[69] + 9×off[72] + off[75]
# We know k[75]!

constraint_75 = k[75] - 81 * k[69]
print(f"Constraint from k[75]: 9×off[72] + off[75] = {constraint_75}")

# The k[80] chain:
# k[80] = 9^4×k[68] + 9^3×off[71] + 9^2×off[74] + 9×off[77] + off[80]
constraint_80 = k[80] - (9**4) * k[68]
print(f"Constraint from k[80]: 729×off[71] + 81×off[74] + 9×off[77] + off[80] = {constraint_80}")

# The k[85] chain:
# k[85] = 9^5×k[70] + 9^4×off[73] + 9^3×off[76] + 9^2×off[79] + 9×off[82] + off[85]
constraint_85 = k[85] - (9**5) * k[70]
print(f"Constraint from k[85]: 9^4×off[73] + 9^3×off[76] + ... = {constraint_85}")

# The k[90] chain:
# From k[69]: k[72], k[75], k[78], k[81], k[84], k[87], k[90]
# k[90] = 9^7×k[69] + ...
constraint_90 = k[90] - (9**7) * k[69]
print(f"Constraint from k[90]: (from k[69] chain) = {constraint_90}")

# Key observation: the chains are INDEPENDENT at the base level!
# k[71] chain starts from k[68]
# k[72] chain starts from k[69]
# k[73] chain starts from k[70]

# So k[75] doesn't constrain k[71] directly!
# But k[80] does.

print("\n### ANALYZING k[80] CONSTRAINT ###")
print("729×off[71] + 81×off[74] + 9×off[77] + off[80] = constraint")

# From our offset analysis, we know offsets have patterns.
# Let's use the actual offset values we found for n ≤ 70 to estimate growth.

offsets = {}
for n in range(10, 71):
    offsets[n] = k[n] - 9 * k[n-3]

# Growth analysis by groups of 3
print("\n### OFFSET GROWTH BY MOD-3 CLASS ###")
for r in [0, 1, 2]:
    print(f"\nn ≡ {r} (mod 3):")
    prev = None
    for n in range(60 + r, 71, 3):
        if n in offsets:
            if prev is not None:
                ratio = offsets[n] / offsets[prev] if offsets[prev] != 0 else 0
                print(f"  off[{n}] / off[{prev}] = {ratio:.4f}")
            prev = n

# For n=71 (≡ 2 mod 3), look at the sequence 68→71→74→77→80
print("\n### SEQUENCE n ≡ 2 (mod 3): 68, 71, 74, 77, 80 ###")
print(f"off[68] = {offsets[68]}")
# Estimate off[71] from ratio
ratio_68 = offsets[68] / offsets[65] if offsets[65] != 0 else 2
ratio_65 = offsets[65] / offsets[62] if offsets[62] != 0 else 2
print(f"Ratio off[68]/off[65] = {ratio_68:.4f}")
print(f"Ratio off[65]/off[62] = {ratio_65:.4f}")

# Average ratio in this class
avg_ratio_mod2 = (ratio_68 + ratio_65) / 2
print(f"Average ratio for mod-2 class: {avg_ratio_mod2:.4f}")

# Estimate off[71]
est_off71 = offsets[68] * avg_ratio_mod2
print(f"\nEstimated off[71] = off[68] × {avg_ratio_mod2:.4f} = {est_off71:.0f}")

# Check with constraint
# If off[74] ≈ off[71] × r, off[77] ≈ off[71] × r^2, off[80] ≈ off[71] × r^3
r = avg_ratio_mod2
off71_from_constraint = constraint_80 / (729 + 81 * r + 9 * r**2 + r**3)
print(f"From constraint: off[71] ≈ {off71_from_constraint:.0f}")

# The two estimates should be close!
print(f"\nComparison:")
print(f"  From ratio: {est_off71:.0f}")
print(f"  From constraint: {off71_from_constraint:.0f}")
print(f"  Difference: {abs(est_off71 - off71_from_constraint):.0f}")

# Use constraint estimate for k[71]
k71_est = 9 * k[68] + int(off71_from_constraint)
print(f"\nk[71] estimate = 9×k[68] + off[71]")
print(f"              = {9 * k[68]} + {int(off71_from_constraint)}")
print(f"              = {k71_est}")

# Verify bit range
if 2**70 <= k71_est <= 2**71 - 1:
    print("✓ In valid 71-bit range!")
else:
    print("✗ Outside valid range!")

# Final answer
print("\n" + "=" * 80)
print("ESTIMATED k[71]")
print("=" * 80)
print(f"\nk[71] ≈ {k71_est}")
print(f"\nIn hex: {hex(k71_est)}")
print(f"Bit length: {k71_est.bit_length()}")
