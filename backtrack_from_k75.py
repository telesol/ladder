#!/usr/bin/env python3
"""
Work backwards from known k[75] to constrain k[71].

Key relationships:
- k[72] = 9*k[69] + offset[72]
- k[75] = 9*k[72] + offset[75]

So: k[75] = 9*(9*k[69] + offset[72]) + offset[75] = 81*k[69] + 9*offset[72] + offset[75]

We know k[75] and k[69], so: 9*offset[72] + offset[75] = k[75] - 81*k[69]
"""

import json

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
k_base = {int(k): v for k, v in data['k_base'].items()}

k = k_base.copy()

def get_k(n):
    if n in k:
        return k[n]
    k_prev = get_k(n - 1)
    m_n = m_seq[n - 2]
    d_n = d_seq[n - 2]
    k_d = get_k(d_n)
    k[n] = 2 * k_prev + (2**n) - m_n * k_d
    return k[n]

for n in range(1, 71):
    get_k(n)

k_75 = 31464123230573852164
k_80 = 1105520030589234487939456

print("=" * 80)
print("BACKTRACKING FROM k[75] TO CONSTRAIN k[71]")
print("=" * 80)

# From k[75]
constraint_75 = k_75 - 81*k[69]
print(f"\nk[75] = {k_75}")
print(f"81*k[69] = {81*k[69]}")
print(f"9*offset[72] + offset[75] = {constraint_75}")

# offset[72] = -k[69] + 4*adj[70] + 2*adj[71] + adj[72]
# offset[75] = -k[72] + 4*adj[73] + 2*adj[74] + adj[75]

# adj[n] = 2^n - m[n]*k[d[n]]

# We know adj[70]
adj_70 = 2**70 - m_seq[68] * get_k(d_seq[68])
print(f"\nadj[70] = {adj_70}")

# For adj[71], adj[72], adj[73], adj[74], adj[75], we need m and d values
# These are unknown, but we can express them parametrically

print("\n" + "=" * 80)
print("EXPRESSING OFFSETS IN TERMS OF UNKNOWNS")
print("=" * 80)

# offset[72] = -k[69] + 4*adj[70] + 2*adj[71] + adj[72]
# Let's define:
# adj[71] = 2^71 - m[71]*k[d[71]]
# adj[72] = 2^72 - m[72]*k[d[72]]

partial_offset_72 = -k[69] + 4*adj_70
print(f"\noffset[72] = {partial_offset_72} + 2*adj[71] + adj[72]")
print(f"         = {partial_offset_72} + 2*(2^71 - m[71]*k[d[71]]) + (2^72 - m[72]*k[d[72]])")
print(f"         = {partial_offset_72} + 2*{2**71} + {2**72} - 2*m[71]*k[d[71]] - m[72]*k[d[72]]")
full_offset_72_const = partial_offset_72 + 2*(2**71) + 2**72
print(f"         = {full_offset_72_const} - 2*m[71]*k[d[71]] - m[72]*k[d[72]]")

# Similarly for offset[75]
# offset[75] = -k[72] + 4*adj[73] + 2*adj[74] + adj[75]

# But k[72] depends on k[71]
# k[71] = 9*k[68] + offset[71]
# k[72] = 2*k[71] + 2^72 - m[72]*k[d[72]]

print("\n" + "=" * 80)
print("CONSTRAINT EQUATION")
print("=" * 80)

# 9*offset[72] + offset[75] = constraint_75 = -24,047,769,722,319,874,517,960

# This is getting complex. Let me try a different approach.
# Express everything in terms of k[71].

# From the 3-step formula:
# k[71] = 9*k[68] + offset[71]
# k[72] = 9*k[69] + offset[72]
# k[75] = 9*k[72] + offset[75]

# From k[75] = 9*k[72] + offset[75]:
# offset[75] = k[75] - 9*k[72]

# From k[72] = 9*k[69] + offset[72]:
# We can also write: k[72] = 2*k[71] + 2^72 - m[72]*k[d[72]]

# Substituting:
# 9*(9*k[69] + offset[72]) + offset[75] = k[75]
# 81*k[69] + 9*offset[72] + offset[75] = k[75]
# 9*offset[72] + offset[75] = k[75] - 81*k[69]

print(f"\n9*offset[72] + offset[75] = {constraint_75}")

# Now let's use the relationship:
# offset[72] = k[72] - 9*k[69]
# offset[75] = k[75] - 9*k[72]

# So: 9*(k[72] - 9*k[69]) + (k[75] - 9*k[72]) = constraint_75
# 9*k[72] - 81*k[69] + k[75] - 9*k[72] = constraint_75
# -81*k[69] + k[75] = constraint_75 ✓

# This is a tautology! We need another equation.

# Let's use the main formula chain:
# k[71] = 2*k[70] + 2^71 - m[71]*k[d[71]]
# k[72] = 2*k[71] + 2^72 - m[72]*k[d[72]]
# k[73] = 2*k[72] + 2^73 - m[73]*k[d[73]]
# k[74] = 2*k[73] + 2^74 - m[74]*k[d[74]]
# k[75] = 2*k[74] + 2^75 - m[75]*k[d[75]]

# Expanding:
# k[75] = 2*(2*(2*(2*(2*k[70] + 2^71 - m[71]*k[d[71]]) + 2^72 - m[72]*k[d[72]]) + 2^73 - m[73]*k[d[73]]) + 2^74 - m[74]*k[d[74]]) + 2^75 - m[75]*k[d[75]]

# = 32*k[70] + 16*2^71 + 8*2^72 + 4*2^73 + 2*2^74 + 2^75 - 16*m[71]*k[d[71]] - 8*m[72]*k[d[72]] - 4*m[73]*k[d[73]] - 2*m[74]*k[d[74]] - m[75]*k[d[75]]

# = 32*k[70] + 2^75 + 2^75 + 2^75 + 2^75 + 2^75 - (16*m[71]*k[d[71]] + 8*m[72]*k[d[72]] + 4*m[73]*k[d[73]] + 2*m[74]*k[d[74]] + m[75]*k[d[75]])

# = 32*k[70] + 5*2^75 - (16*m[71]*k[d[71]] + 8*m[72]*k[d[72]] + 4*m[73]*k[d[73]] + 2*m[74]*k[d[74]] + m[75]*k[d[75]])

coeff_k70 = 32
const_term = 5 * (2**75)

print(f"\n### CHAIN FORMULA FROM k[70] TO k[75] ###")
print(f"k[75] = {coeff_k70}*k[70] + {const_term}")
print(f"     - (16*m[71]*k[d[71]] + 8*m[72]*k[d[72]] + 4*m[73]*k[d[73]] + 2*m[74]*k[d[74]] + m[75]*k[d[75]])")

# We know k[70] and k[75]
lhs = k_75
rhs_known = coeff_k70 * k[70] + const_term
unknown_part = rhs_known - lhs

print(f"\n32*k[70] + 5*2^75 = {rhs_known}")
print(f"k[75] = {k_75}")
print(f"\nSum of weighted m-terms:")
print(f"16*m[71]*k[d[71]] + 8*m[72]*k[d[72]] + 4*m[73]*k[d[73]] + 2*m[74]*k[d[74]] + m[75]*k[d[75]] = {unknown_part}")

# This gives us ONE equation with 5 unknowns (m[71] through m[75] and their d values)

# Let's try assuming d[71] through d[75] values based on patterns
print("\n" + "=" * 80)
print("EXPLORING d-VALUE PATTERNS FOR n=71-75")
print("=" * 80)

# n mod 3:
# 71 mod 3 = 2
# 72 mod 3 = 0
# 73 mod 3 = 1
# 74 mod 3 = 2
# 75 mod 3 = 0

print("\n n mod 3:")
for n in range(71, 76):
    print(f"n={n}: n mod 3 = {n % 3}")

# Looking at historical d patterns for each mod class
print("\n### Historical d for n mod 3 = 0 (recent) ###")
for n in range(60, 71):
    if n % 3 == 0:
        print(f"n={n}: d={d_seq[n-2]}")

print("\n### Historical d for n mod 3 = 1 (recent) ###")
for n in range(60, 71):
    if n % 3 == 1:
        print(f"n={n}: d={d_seq[n-2]}")

print("\n### Historical d for n mod 3 = 2 (recent) ###")
for n in range(60, 71):
    if n % 3 == 2:
        print(f"n={n}: d={d_seq[n-2]}")

# Based on patterns, let's assume:
# For n=71 (mod 3 = 2): d could be 1, 2, or 5
# For n=72 (mod 3 = 0): d is likely 1 or 8
# For n=73 (mod 3 = 1): d is likely 2 or 1
# For n=74 (mod 3 = 2): d could be 1, 2, or 5
# For n=75 (mod 3 = 0): d is likely 1 or 2

# Let's try specific combinations and check if the constraint can be satisfied

print("\n" + "=" * 80)
print("TESTING d-VALUE COMBINATIONS")
print("=" * 80)

# Constraint: 16*m[71]*k[d[71]] + 8*m[72]*k[d[72]] + 4*m[73]*k[d[73]] + 2*m[74]*k[d[74]] + m[75]*k[d[75]] = unknown_part

# If all d=1 (k[1]=1):
# 16*m[71] + 8*m[72] + 4*m[73] + 2*m[74] + m[75] = unknown_part

print(f"\nIf all d=1: 16*m[71] + 8*m[72] + 4*m[73] + 2*m[74] + m[75] = {unknown_part}")
avg_m = unknown_part / 31  # (16+8+4+2+1)
print(f"Average m if all equal: {avg_m}")
print(f"This is approximately {avg_m / (2**73):.4f} * 2^73")

# Compare to historical m/2^n ratios
print("\n### Historical m/2^n for n=66-70 ###")
for n in range(66, 71):
    m_n = m_seq[n-2]
    print(f"n={n}: m/2^n = {m_n / (2**n):.6f}")
