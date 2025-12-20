#!/usr/bin/env python3
"""
Search for m[71] using the k[80] constraint and construction patterns.

Key insight: We can use the k[80] chain constraint to verify candidates.
"""

import sqlite3
import json

# Load known k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

# Load m and d sequences
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']
d_seq = data['d_seq']

print("=" * 80)
print("CONSTRAINED SEARCH FOR m[71]")
print("=" * 80)

# Key values
k_68 = k[68]
k_80 = k[80]

print(f"\nk[68] = {k_68}")
print(f"k[80] = {k_80}")

# The mod-3 chain gives us:
# k[71] = 9*k[68] + off[71]
# k[74] = 9*k[71] + off[74]
# k[77] = 9*k[74] + off[77]
# k[80] = 9*k[77] + off[80]
#
# Combined: k[80] = 6561*k[68] + 729*off[71] + 81*off[74] + 9*off[77] + off[80]

constraint_80 = k_80 - 6561 * k_68
print(f"\nConstraint: 729*off[71] + 81*off[74] + 9*off[77] + off[80] = {constraint_80}")

# Strategy: Assume offset growth patterns from historical data
# For the mod-3 class n ≡ 2 (mod 3): 68, 71, 74, 77, 80
# We have off[68] from the data

# Compute off[68]
off_68 = k_68 - 9 * k[65]
print(f"off[68] = {off_68}")

# Look at growth ratios in the 68-chain
print("\n" + "-" * 80)
print("OFFSET GROWTH ANALYSIS (n ≡ 2 mod 3)")
print("-" * 80)

offsets_mod2 = {}
for n in range(11, 71):
    if n % 3 == 2:
        offsets_mod2[n] = k[n] - 9 * k[n-3]

# Growth ratios
ratios = []
prev_n = None
for n in sorted(offsets_mod2.keys()):
    if prev_n is not None and offsets_mod2[prev_n] != 0:
        ratio = offsets_mod2[n] / offsets_mod2[prev_n]
        ratios.append((n, ratio))
        if n >= 50:
            print(f"off[{n}] / off[{prev_n}] = {ratio:.6f}")
    prev_n = n

# Recent ratios
recent_ratios = [r[1] for r in ratios[-10:]]
avg_ratio = sum(recent_ratios) / len(recent_ratios)
print(f"\nAverage of last 10 ratios: {avg_ratio:.6f}")

# Estimate off[71], off[74], off[77], off[80] using geometric growth
off_71_est = off_68 * avg_ratio
off_74_est = off_71_est * avg_ratio
off_77_est = off_74_est * avg_ratio
off_80_est = off_77_est * avg_ratio

print(f"\nEstimated offsets (geometric model):")
print(f"off[71] ≈ {off_71_est:.0f}")
print(f"off[74] ≈ {off_74_est:.0f}")
print(f"off[77] ≈ {off_77_est:.0f}")
print(f"off[80] ≈ {off_80_est:.0f}")

# Check constraint
constraint_check = 729*off_71_est + 81*off_74_est + 9*off_77_est + off_80_est
print(f"\n729*off[71] + 81*off[74] + 9*off[77] + off[80] ≈ {constraint_check:.0f}")
print(f"Actual constraint: {constraint_80}")
print(f"Difference: {constraint_80 - constraint_check:.0f}")

# Now let's solve for off[71] assuming the ratios are approximately correct
# Let r = avg_ratio. Then:
# 729*x + 81*r*x + 9*r^2*x + r^3*x = constraint_80
# x * (729 + 81*r + 9*r^2 + r^3) = constraint_80
# x = constraint_80 / (729 + 81*r + 9*r^2 + r^3)

r = avg_ratio
coeff = 729 + 81*r + 9*r**2 + r**3
off_71_from_constraint = constraint_80 / coeff

print(f"\n" + "-" * 80)
print("SOLVING FROM CONSTRAINT")
print("-" * 80)
print(f"Using r = {r:.6f}")
print(f"Coefficient = {coeff:.4f}")
print(f"off[71] (from constraint) = {off_71_from_constraint:.0f}")

# Compute corresponding k[71]
k_71_est = 9 * k_68 + int(off_71_from_constraint)
print(f"\nk[71] estimate = 9*k[68] + off[71]")
print(f"             = {9*k_68} + {int(off_71_from_constraint)}")
print(f"             = {k_71_est}")

# Verify bit range
bit_len = k_71_est.bit_length()
print(f"Bit length: {bit_len} (should be 71)")

if 2**70 <= k_71_est <= 2**71 - 1:
    print("✓ In valid 71-bit range!")
else:
    print("✗ Outside valid range!")

# Now compute m[71] for different d values
print("\n" + "=" * 80)
print("COMPUTING m[71] FOR DIFFERENT d VALUES")
print("=" * 80)

base = 2 * k[70] + 2**71

for d in [1, 2, 5]:
    k_d = k[d]
    numerator = base - k_71_est
    if numerator % k_d == 0:
        m_71 = numerator // k_d
        print(f"\nd[71] = {d}: m[71] = {m_71}")

        # Check if m[71] follows patterns
        if m_71 % 17 == 0:
            print(f"  17-network: m[71] = 17 × {m_71 // 17}")
        if m_71 % 22 == 0:
            print(f"  π-network: m[71] = 22 × {m_71 // 22}")
        if m_71 % 113 == 0:
            print(f"  π-network: m[71] = 113 × {m_71 // 113}")
    else:
        print(f"\nd[71] = {d}: NOT DIVISIBLE (remainder = {numerator % k_d})")

# Verification: chain back to k[80]
print("\n" + "=" * 80)
print("VERIFICATION: CHAIN FROM k[71] TO k[80]")
print("=" * 80)

# Use the best d value (d=1 is most common for n≡2 mod 3)
for d_71 in [1, 2, 5]:
    k_d = k[d_71]
    numerator = base - k_71_est
    if numerator % k_d != 0:
        continue

    m_71 = numerator // k_d

    # Compute forward using the formula
    # We need m[72], m[73], m[74], etc. - but we don't have them!
    # Instead, use the offset-based forward propagation

    off_71 = k_71_est - 9 * k_68

    # Estimate k[74], k[77], k[80] using offset growth
    k_74_est = 9 * k_71_est + int(off_71 * r)
    k_77_est = 9 * k_74_est + int(off_71 * r**2)
    k_80_est = 9 * k_77_est + int(off_71 * r**3)

    print(f"\nFor d[71]={d_71}, m[71]={m_71}:")
    print(f"  k[71] = {k_71_est}")
    print(f"  k[74] ≈ {k_74_est} (estimated)")
    print(f"  k[77] ≈ {k_77_est} (estimated)")
    print(f"  k[80] ≈ {k_80_est} (estimated)")
    print(f"  Actual k[80] = {k_80}")
    print(f"  Error: {abs(k_80_est - k_80) / k_80 * 100:.4f}%")

# Final recommendation
print("\n" + "=" * 80)
print("FINAL ANALYSIS")
print("=" * 80)

# The best estimate based on constraint
print(f"\nBest estimate for k[71]: {k_71_est}")
print(f"Hex: {hex(k_71_est)}")

# Corresponding m[71] values
for d_71 in [1, 2, 5]:
    k_d = k[d_71]
    numerator = base - k_71_est
    if numerator % k_d == 0:
        m_71 = numerator // k_d
        print(f"\nIf d[71]={d_71}: m[71] = {m_71}")
