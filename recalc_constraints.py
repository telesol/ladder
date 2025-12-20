#!/usr/bin/env python3
"""
Recalculate the bridge constraints using correct k[75] and k[80] values from database.
"""

import json

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
k_base = {int(k): v for k, v in data['k_base'].items()}

k = k_base.copy()
def get_k(n):
    if n in k: return k[n]
    k_prev = get_k(n - 1)
    m_n = m_seq[n - 2]
    d_n = d_seq[n - 2]
    k_d = get_k(d_n)
    k[n] = 2 * k_prev + (2**n) - m_n * k_d
    return k[n]

for n in range(1, 71):
    get_k(n)

# Correct values from database
k_75 = int('4c5ce114686a1336e07', 16)  # 22538323240989823823367
k_80 = int('ea1a5c66dcc11b5ad180', 16)  # 1105520030589234487939456

print("=" * 80)
print("RECALCULATING BRIDGE CONSTRAINTS")
print("=" * 80)
print(f"k[75] = {k_75}")
print(f"k[80] = {k_80}")
print(f"k[75] bit length: {k_75.bit_length()}")
print(f"k[80] bit length: {k_80.bit_length()}")

# Key known values
k_68 = k[68]
k_69 = k[69]
k_70 = k[70]

print(f"\nk[68] = {k_68}")
print(f"k[69] = {k_69}")
print(f"k[70] = {k_70}")

# 3-step recursion: k[n] = 9*k[n-3] + offset[n]
# So:
# k[71] = 9*k[68] + offset[71]
# k[72] = 9*k[69] + offset[72]
# k[73] = 9*k[70] + offset[73]
# k[74] = 9*k[71] + offset[74]
# k[75] = 9*k[72] + offset[75]

# Expanding:
# k[75] = 9*k[72] + offset[75]
# k[72] = 9*k[69] + offset[72]
# So: k[75] = 81*k[69] + 9*offset[72] + offset[75]

# Calculate what 9*offset[72] + offset[75] should be
constraint_75 = k_75 - 81*k_69
print(f"\nConstraint from k[75]:")
print(f"  k[75] = 81*k[69] + 9*offset[72] + offset[75]")
print(f"  81*k[69] = {81*k_69}")
print(f"  9*offset[72] + offset[75] = {constraint_75}")

# For k[80]:
# k[80] = 9*k[77] + offset[80]
# k[77] = 9*k[74] + offset[77]
# k[74] = 9*k[71] + offset[74]
# k[71] = 9*k[68] + offset[71]
#
# k[80] = 9*(9*(9*(9*k[68] + offset[71]) + offset[74]) + offset[77]) + offset[80]
# k[80] = 6561*k[68] + 729*offset[71] + 81*offset[74] + 9*offset[77] + offset[80]

constraint_80 = k_80 - 6561*k_68
print(f"\nConstraint from k[80]:")
print(f"  k[80] = 6561*k[68] + 729*offset[71] + 81*offset[74] + 9*offset[77] + offset[80]")
print(f"  6561*k[68] = {6561*k_68}")
print(f"  729*offset[71] + 81*offset[74] + 9*offset[77] + offset[80] = {constraint_80}")

# Historical offset values
print("\n" + "=" * 80)
print("HISTORICAL OFFSETS")
print("=" * 80)

offsets = {}
for n in range(31, 71):
    offsets[n] = k[n] - 9*k[n-3]

for n in range(65, 71):
    print(f"offset[{n}] = {offsets[n]:.6e}")

# Offset trends
print("\nOffset ratios (doubling pattern):")
for n in range(66, 71):
    ratio = offsets[n] / offsets[n-1]
    print(f"  offset[{n}]/offset[{n-1}] = {ratio:.4f}")

# Predict offset[71] based on trend
# The offsets are negative and roughly doubling
predicted_offset_71 = offsets[70] * 2
print(f"\nPredicted offset[71] (2x trend) = {predicted_offset_71:.6e}")

# Valid offset[71] range for k[71] in [2^70, 2^71)
k71_min = 2**70
k71_max = 2**71 - 1
offset71_min = k71_min - 9*k_68
offset71_max = k71_max - 9*k_68

print(f"\nValid offset[71] range:")
print(f"  min: {offset71_min:.6e}")
print(f"  max: {offset71_max:.6e}")

# If we assume offset[74], offset[77], offset[80] follow similar patterns
# Let's estimate them and solve for offset[71]
print("\n" + "=" * 80)
print("ESTIMATING offset[71] FROM k[80] CONSTRAINT")
print("=" * 80)

# Assuming offsets roughly double each step (with alternating signs)
# offset[71] ≈ 2*offset[70] = -4.5e+20
# offset[74] ≈ 8*offset[71] ≈ -3.6e+21
# offset[77] ≈ 64*offset[71] ≈ -2.9e+22
# offset[80] ≈ 512*offset[71] ≈ -2.3e+23

# 729*offset[71] + 81*offset[74] + 9*offset[77] + offset[80] = constraint_80
# 729*x + 81*8*x + 9*64*x + 512*x = constraint_80
# 729*x + 648*x + 576*x + 512*x = constraint_80
# 2465*x ≈ constraint_80
# x ≈ constraint_80 / 2465

rough_offset_71 = constraint_80 / 2465
print(f"Rough estimate of offset[71] = {rough_offset_71:.6e}")

# Better estimation: use the actual doubling ratios observed
# The ratios vary: 0.80, 2.01, 2.17, 1.86
avg_ratio = 2.0

# offset[72] ≈ 2*offset[71]
# offset[73] ≈ 4*offset[71]
# offset[74] ≈ 8*offset[71]
# etc.

# For the k[80] constraint:
# 729*off[71] + 81*off[74] + 9*off[77] + off[80]
# = 729*x + 81*(8*x) + 9*(64*x) + (512*x)
# = 729*x + 648*x + 576*x + 512*x
# = 2465*x

# This gives x = constraint_80 / 2465
est_offset_71 = constraint_80 / 2465
print(f"\nUsing doubling assumption:")
print(f"  offset[71] ≈ {est_offset_71:.6e}")

# Check if this is in valid range
if offset71_min <= est_offset_71 <= offset71_max:
    print("  ✓ In valid range!")

    # Calculate corresponding k[71]
    k_71_est = 9*k_68 + int(est_offset_71)
    print(f"  k[71] ≈ {k_71_est}")
    print(f"  k[71] bit length: {k_71_est.bit_length()}")
else:
    print(f"  ✗ Out of valid range [{offset71_min:.6e}, {offset71_max:.6e}]")

# Let's also solve more carefully
# If offset[n+3] = r * offset[n] for some ratio r
# Then offset[74] = r^1 * offset[71]
# offset[77] = r^2 * offset[71]
# offset[80] = r^3 * offset[71]
#
# 729*x + 81*r*x + 9*r^2*x + r^3*x = constraint_80
# x*(729 + 81*r + 9*r^2 + r^3) = constraint_80

print("\n" + "=" * 80)
print("SOLVING FOR offset[71] WITH DIFFERENT GROWTH RATES")
print("=" * 80)

for r in [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 8.0]:
    coef = 729 + 81*r + 9*(r**2) + (r**3)
    offset_71_solution = constraint_80 / coef
    k_71_solution = 9*k_68 + int(offset_71_solution)

    in_range = k71_min <= k_71_solution <= k71_max
    range_str = "✓" if in_range else "✗"

    print(f"r={r}: offset[71]={offset_71_solution:.6e}, k[71]={k_71_solution:.6e} {range_str}")
