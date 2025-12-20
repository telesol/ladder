#!/usr/bin/env python3
"""
Correct derivation of offset[71] using the proper formula.

Key insight: offset[n] = -k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]
where adj[n] = 2^n - m[n]*k[d[n]]
"""

import json

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
k_base = {int(k): v for k, v in data['k_base'].items()}

k = k_base.copy()

def get_m(n):
    return m_seq[n - 2]

def get_d(n):
    return d_seq[n - 2]

def get_k(n):
    if n in k:
        return k[n]
    k_prev = get_k(n - 1)
    m_n = get_m(n)
    d_n = get_d(n)
    k_d = get_k(d_n)
    k[n] = 2 * k_prev + (2**n) - m_n * k_d
    return k[n]

# Compute all k values
for n in range(1, 71):
    get_k(n)

def get_adj(n):
    """adj[n] = 2^n - m[n]*k[d[n]]"""
    return (2**n) - get_m(n) * get_k(get_d(n))

def compute_offset(n):
    """offset[n] = -k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]"""
    return -k[n-3] + 4*get_adj(n-2) + 2*get_adj(n-1) + get_adj(n)

# Verify the offset formula
print("=" * 80)
print("VERIFYING CORRECTED OFFSET FORMULA")
print("offset[n] = -k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]")
print("=" * 80)

all_match = True
for n in range(34, 71):
    computed = compute_offset(n)
    actual = k[n] - 9*k[n-3]
    if computed != actual:
        print(f"n={n}: MISMATCH computed={computed}, actual={actual}")
        all_match = False

if all_match:
    print("\n✓ ALL OFFSETS MATCH (n=34 to n=70)")

# Now express offset[71] in terms of m[71] and d[71]
print("\n" + "=" * 80)
print("DERIVING OFFSET[71]")
print("=" * 80)

print("\noffset[71] = -k[68] + 4*adj[69] + 2*adj[70] + adj[71]")
print("          = -k[68] + 4*(2^69 - m[69]*k[d[69]]) + 2*(2^70 - m[70]*k[d[70]]) + (2^71 - m[71]*k[d[71]])")

k_68 = k[68]
two_69 = 2**69
two_70 = 2**70
two_71 = 2**71
m_69 = get_m(69)
d_69 = get_d(69)
k_d69 = get_k(d_69)
m_70 = get_m(70)
d_70 = get_d(70)
k_d70 = get_k(d_70)

adj_69 = two_69 - m_69 * k_d69
adj_70 = two_70 - m_70 * k_d70

print(f"\nKnown values:")
print(f"  k[68] = {k_68}")
print(f"  2^69 = {two_69}")
print(f"  2^70 = {two_70}")
print(f"  2^71 = {two_71}")
print(f"  m[69] = {m_69}, d[69] = {d_69}, k[d[69]] = {k_d69}")
print(f"  m[70] = {m_70}, d[70] = {d_70}, k[d[70]] = {k_d70}")

print(f"\nComputed:")
print(f"  adj[69] = 2^69 - m[69]*k[d[69]] = {two_69} - {m_69*k_d69} = {adj_69}")
print(f"  adj[70] = 2^70 - m[70]*k[d[70]] = {two_70} - {m_70*k_d70} = {adj_70}")

# Partial offset (without adj[71])
partial = -k_68 + 4*adj_69 + 2*adj_70 + two_71
print(f"\n  -k[68] + 4*adj[69] + 2*adj[70] + 2^71 = {partial}")

print("\nSo: offset[71] = partial - m[71]*k[d[71]]")
print(f"    offset[71] = {partial} - m[71]*k[d[71]]")

# Now use the bridge constraint
print("\n" + "=" * 80)
print("BRIDGE CONSTRAINT ANALYSIS")
print("=" * 80)

# We know k[75] and k[80] from the puzzle solutions
k_75 = 31464123230573852164
k_80 = 1105520030589234487939456

print(f"\nKnown puzzle solutions:")
print(f"  k[75] = {k_75}")
print(f"  k[80] = {k_80}")

# From 3-step recursion:
# k[71] = 9*k[68] + offset[71]
# k[72] = 9*k[69] + offset[72]
# k[73] = 9*k[70] + offset[73]
# k[74] = 9*k[71] + offset[74]
# k[75] = 9*k[72] + offset[75]

# Let's define:
# k[72] = 9*k[69] + off[72]
# k[75] = 9*k[72] + off[75] = 9*(9*k[69] + off[72]) + off[75] = 81*k[69] + 9*off[72] + off[75]

constraint_75 = k_75 - 81*k[69]
print(f"\nFrom k[75]:")
print(f"  k[75] = 81*k[69] + 9*offset[72] + offset[75]")
print(f"  {k_75} = 81*{k[69]} + 9*offset[72] + offset[75]")
print(f"  9*offset[72] + offset[75] = {constraint_75}")

# For k[80]:
# k[80] = 9^4*k[68] + 9^3*off[71] + 9^2*off[74] + 9*off[77] + off[80]
constraint_80 = k_80 - (9**4)*k[68]
print(f"\nFrom k[80]:")
print(f"  k[80] = 6561*k[68] + 729*offset[71] + 81*offset[74] + 9*offset[77] + offset[80]")
print(f"  729*offset[71] + 81*offset[74] + 9*offset[77] + offset[80] = {constraint_80}")

# The key is that offset[71] depends on m[71], d[71]
# offset[71] = partial - m[71]*k[d[71]]

print("\n" + "=" * 80)
print("OFFSET[71] AS FUNCTION OF m[71], d[71]")
print("=" * 80)

# Let's compute for each possible d value
print("\nFor each possible d[71]:")
for d in [1, 2, 3, 5]:
    k_d = get_k(d)
    print(f"\n  If d[71] = {d}, k[d[71]] = {k_d}:")
    print(f"    offset[71] = {partial} - m[71] * {k_d}")
    print(f"    offset[71] = {partial} - {k_d}*m[71]")

# Now let's think about bounds on m[71]
print("\n" + "=" * 80)
print("BOUNDS ON m[71]")
print("=" * 80)

# k[71] must be in range [2^70, 2^71)
k71_min = 2**70
k71_max = 2**71 - 1

# k[71] = 9*k[68] + offset[71]
# So offset[71] = k[71] - 9*k[68]

offset71_min = k71_min - 9*k[68]
offset71_max = k71_max - 9*k[68]

print(f"\nk[71] range: [{k71_min}, {k71_max})")
print(f"k[68] = {k[68]}")
print(f"9*k[68] = {9*k[68]}")
print(f"\noffset[71] range: [{offset71_min}, {offset71_max})")

# For each d, compute m[71] range
print("\nFor each d[71], m[71] range:")
for d in [1, 2, 3, 5]:
    k_d = get_k(d)
    # offset[71] = partial - k_d * m[71]
    # m[71] = (partial - offset[71]) / k_d
    m71_max_for_this_d = (partial - offset71_min) / k_d
    m71_min_for_this_d = (partial - offset71_max) / k_d
    if m71_min_for_this_d < 0:
        m71_min_for_this_d = 0
    print(f"\n  d[71] = {d} (k[{d}] = {k_d}):")
    print(f"    m[71] ∈ [{int(m71_min_for_this_d)}, {int(m71_max_for_this_d)}]")
    print(f"    m[71] / 2^71 ∈ [{m71_min_for_this_d/two_71:.6f}, {m71_max_for_this_d/two_71:.6f}]")

# Look at patterns in m[n]/2^n for recent values
print("\n" + "=" * 80)
print("PATTERN: m[n]/2^n RATIO FOR n ≡ 2 (mod 3)")
print("=" * 80)

print("\nn=71 is ≡ 2 (mod 3), so compare to n=68,65,62,59,56,53,50...")
for n in [50, 53, 56, 59, 62, 65, 68]:
    m_n = get_m(n)
    d_n = get_d(n)
    ratio = m_n / (2**n)
    print(f"n={n}: m={m_n}, d={d_n}, m/2^n = {ratio:.10f}")

# For n ≡ 2 (mod 3) with d=2
print("\n### n ≡ 2 (mod 3) with d=2 ###")
for n in range(50, 71):
    if n % 3 == 2 and get_d(n) == 2:
        m_n = get_m(n)
        ratio = m_n / (2**n)
        print(f"n={n}: m={m_n}, m/2^n = {ratio:.10f}")

# Let's also check n ≡ 2 (mod 3) with d=1
print("\n### n ≡ 2 (mod 3) with d=1 ###")
for n in range(50, 71):
    if n % 3 == 2 and get_d(n) == 1:
        m_n = get_m(n)
        ratio = m_n / (2**n)
        print(f"n={n}: m={m_n}, m/2^n = {ratio:.10f}")
