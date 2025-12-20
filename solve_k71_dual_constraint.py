#!/usr/bin/env python3
"""
Solve for k[71] using BOTH k[75] and k[80] constraints.

From the main formula chain:
k[75] = 32*k[70] + 5*2^75 - (16*m[71]*k[d[71]] + 8*m[72]*k[d[72]] + ...)
k[80] = 32*k[75] + 5*2^80 - (16*m[76]*k[d[76]] + 8*m[77]*k[d[77]] + ...)

Also from 3-step:
k[71] = 9*k[68] + offset[71]
k[74] = 9*k[71] + offset[74]
k[77] = 9*k[74] + offset[77]
k[80] = 9*k[77] + offset[80]

So: k[80] = 9^4*k[68] + 9^3*offset[71] + 9^2*offset[74] + 9*offset[77] + offset[80]
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
print("DUAL CONSTRAINT ANALYSIS FOR k[71]")
print("=" * 80)

# Constraint from k[75]: 5-term chain
constraint_75 = 32*k[70] + 5*(2**75) - k_75
print(f"\nConstraint from k[75]:")
print(f"16*m[71]*k[d[71]] + 8*m[72]*k[d[72]] + 4*m[73]*k[d[73]] + 2*m[74]*k[d[74]] + m[75]*k[d[75]] = {constraint_75}")

# Constraint from k[80]: 3-step chain
# k[80] = 9^4*k[68] + 729*offset[71] + 81*offset[74] + 9*offset[77] + offset[80]
constraint_80 = k_80 - (9**4)*k[68]
print(f"\nConstraint from k[80]:")
print(f"729*offset[71] + 81*offset[74] + 9*offset[77] + offset[80] = {constraint_80}")

# offset[71] = 2,322,972,793,525,025,629,385 - m[71]*k[d[71]]
partial_offset_71 = 2322972793525025629385
print(f"\noffset[71] = {partial_offset_71} - m[71]*k[d[71]]")

# Let's try to narrow down d[71]
print("\n" + "=" * 80)
print("ANALYZING d[71] OPTIONS")
print("=" * 80)

# From constraint_75 and historical ratios, let's estimate the total weighted m-sum
# If we assume m[n]/2^n ≈ 0.5-1.5 typically, and weights are 16,8,4,2,1
# The average weighted contribution is dominated by m[71]

# For d[71]=1: m[71] ≈ constraint_75 / 16 when others are small
# For d[71]=2: m[71] ≈ constraint_75 / 48 (since k[2]=3)

for d71 in [1, 2, 5]:
    k_d71 = get_k(d71)
    # Approximate m[71] by assuming it dominates the constraint
    approx_m71 = constraint_75 / (16 * k_d71)
    ratio = approx_m71 / (2**71)
    print(f"\nd[71]={d71} (k={k_d71}):")
    print(f"  If m[71] dominates: m[71] ≈ {approx_m71:.2e}")
    print(f"  Ratio m[71]/2^71 ≈ {ratio:.4f}")

    # Check if this is in valid range
    m71_min = 1940873948010047380963 if d71 == 1 else (646957982670015793654 if d71 == 2 else 92422568952859399093)
    m71_max = 3121465568727458684386 if d71 == 1 else (1040488522909152894795 if d71 == 2 else 148641217558450413542)

    if m71_min <= approx_m71 <= m71_max:
        print(f"  ✓ IN VALID RANGE [{m71_min:.2e}, {m71_max:.2e}]")
    else:
        print(f"  ✗ OUT OF RANGE [{m71_min:.2e}, {m71_max:.2e}]")

# Now let's try a more refined approach
# Use the 3-step offset constraint more directly

print("\n" + "=" * 80)
print("OFFSET-BASED ANALYSIS")
print("=" * 80)

# offset[71] must satisfy: 729*offset[71] + 81*offset[74] + 9*offset[77] + offset[80] = constraint_80
# If all offsets are roughly the same magnitude: offset ≈ constraint_80 / (729+81+9+1) = constraint_80 / 820

avg_offset = constraint_80 / 820
print(f"\nIf offsets ~equal: avg offset ≈ {avg_offset:.2e}")

# offset[71] = partial_offset_71 - m[71]*k[d[71]]
# If offset[71] ≈ avg_offset:
# m[71]*k[d[71]] ≈ partial_offset_71 - avg_offset

target_m_kd = partial_offset_71 - avg_offset
print(f"m[71]*k[d[71]] ≈ {partial_offset_71} - {avg_offset:.2e} = {target_m_kd:.2e}")

for d71 in [1, 2, 5]:
    k_d71 = get_k(d71)
    m71_estimate = target_m_kd / k_d71
    ratio = m71_estimate / (2**71)
    print(f"\nd[71]={d71}: m[71] ≈ {m71_estimate:.2e}, ratio = {ratio:.4f}")

# Historical offset magnitudes for guidance
print("\n### Historical offset magnitudes ###")
for n in range(65, 71):
    offset_n = k[n] - 9*k[n-3]
    print(f"offset[{n}] = {offset_n:.2e}")

# Use the 3-step recursion directly to estimate k[71]
print("\n" + "=" * 80)
print("DIRECT 3-STEP ESTIMATION")
print("=" * 80)

# k[80] = 9^4*k[68] + 729*offset[71] + 81*offset[74] + 9*offset[77] + offset[80]
# k[71] = 9*k[68] + offset[71]

# If we assume offsets scale roughly as geometric with ratio r:
# offset[74] ≈ r^3 * offset[71]
# offset[77] ≈ r^6 * offset[71]
# offset[80] ≈ r^9 * offset[71]

# Then: 729 + 81*r^3 + 9*r^6 + r^9 = constraint_80 / offset[71]

# Let's solve for r assuming offset[71] is in a reasonable range
print("\nTesting geometric offset ratios:")

# offset[71] range from valid k[71] range
k71_min = 2**70
k71_max = 2**71 - 1
offset71_min = k71_min - 9*k[68]
offset71_max = k71_max - 9*k[68]

print(f"offset[71] range: [{offset71_min:.2e}, {offset71_max:.2e}]")

# Test a few offset[71] values and see if constraint_80 can be satisfied
for offset_71_test in [offset71_min, (offset71_min + offset71_max)//2, offset71_max]:
    # constraint_80 = 729*offset_71 + 81*offset_74 + 9*offset_77 + offset_80
    remaining = constraint_80 - 729*offset_71_test
    # If offsets double every 3 steps (roughly):
    # remaining ≈ 81*2*offset_71 + 9*4*offset_71 + 8*offset_71 = (162 + 36 + 8)*offset_71 = 206*offset_71
    avg_other_offset = remaining / 91  # 81 + 9 + 1

    print(f"\noffset[71] = {offset_71_test:.4e}:")
    print(f"  Remaining for offset[74,77,80] = {remaining:.4e}")
    print(f"  Avg of remaining offsets = {avg_other_offset:.4e}")

    # Compute implied k[71]
    k71_implied = 9*k[68] + offset_71_test
    print(f"  Implied k[71] = {k71_implied}")
    print(f"  k[71] / 2^71 = {k71_implied / (2**71):.6f}")

    # Check if in valid range
    if k71_min <= k71_implied < 2**71:
        print(f"  ✓ Valid 71-bit key")
    else:
        print(f"  ✗ Invalid range")
