#!/usr/bin/env python3
"""
Verify the relationship between the main formula and the 3-step recursion.

Main formula: k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
3-step recursion: k[n] = 9*k[n-3] + offset[n]

Goal: Understand what offset[n] actually represents.
"""

import json

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
k_base = {int(k): v for k, v in data['k_base'].items()}

# Known offsets from K_FORMULAS_COMPLETE.md (for n=31-70)
known_offsets = {
    31: 53678879, 32: -512907232, 33: -2161020844, 34: -4788424802,
    35: -7728383534, 36: -21849171228, 37: -26946088818, 38: -34044309536,
    39: -57764960883, 40: 101387367595, 41: 135508375819, 42: -18150167970,
    43: -1623051668725, 44: 2280491910748, 45: -6061907885570,
    46: -15279629081813, 47: -18976196699469, 48: 11238806921070,
    49: -53559128104983, 50: -465859435859766, 51: 337906742849889,
    52: 534425494307975, 53: 1263419505968248, 54: -8554470391888177,
    55: -7903070264536840, 56: -16654413450626541, 57: 48475661710376129,
    58: -70431846450483091, 59: 127101703624177016, 60: -109170479978122046,
    61: -374002469168423459, 62: -817260915816573657, 63: -1222142202450997670,
    64: 4967579474010341790, 65: -4606975570506195703, 66: -34592851995373892186,
    67: -27540062615817873350, 68: -55217129595261785870,
    69: -119841466032741115730, 70: -223475518416452616237
}

# First, compute all k values up to 70 using the main formula
k = k_base.copy()

def get_m(n):
    """Get m[n] with proper index shift."""
    return m_seq[n - 2]

def get_d(n):
    """Get d[n] with proper index shift."""
    return d_seq[n - 2]

def get_k(n):
    """Get k[n], computing if needed."""
    if n in k:
        return k[n]
    # Compute using main formula
    k_prev = get_k(n - 1)
    m_n = get_m(n)
    d_n = get_d(n)
    k_d = get_k(d_n)
    k[n] = 2 * k_prev + (2**n) - m_n * k_d
    return k[n]

# Compute k[1] to k[70]
print("=" * 80)
print("COMPUTING K-VALUES AND VERIFYING OFFSETS")
print("=" * 80)

for n in range(1, 71):
    get_k(n)

# Verify the 3-step recursion offsets
print("\n### Verifying 3-step offsets: k[n] = 9*k[n-3] + offset[n] ###\n")
print("n  |  Computed offset         |  Known offset            |  Match?")
print("-" * 75)

matches = 0
mismatches = 0

for n in range(31, 71):
    # Compute offset from 3-step formula
    computed_offset = k[n] - 9 * k[n - 3]
    known = known_offsets.get(n)

    if known is not None:
        match = "✓" if computed_offset == known else "✗"
        if computed_offset == known:
            matches += 1
        else:
            mismatches += 1
        print(f"{n} | {computed_offset:25} | {known:25} | {match}")

print(f"\nMatches: {matches}, Mismatches: {mismatches}")

# Now analyze the adj values (from main formula)
print("\n" + "=" * 80)
print("ANALYZING ADJ VALUES: adj[n] = 2^n - m[n]*k[d[n]]")
print("=" * 80)

print("\nn  |  adj[n]                  |  m[n]                  |  d[n] |  k[d[n]]")
print("-" * 90)

for n in range(31, 41):
    m_n = get_m(n)
    d_n = get_d(n)
    k_d = get_k(d_n)
    adj_n = (2**n) - m_n * k_d
    print(f"{n} | {adj_n:24} | {m_n:22} | {d_n:5} | {k_d}")

# Relationship between adj and offset
print("\n" + "=" * 80)
print("RELATIONSHIP BETWEEN ADJ AND OFFSET")
print("=" * 80)

print("\nFor a single step: k[n] = 2*k[n-1] + adj[n]")
print("For 3 steps: k[n] = 9*k[n-3] + offset[n]")
print("\nExpanding 3 steps:")
print("  k[n-1] = 2*k[n-2] + adj[n-1]")
print("  k[n-2] = 2*k[n-3] + adj[n-2]")
print("  k[n] = 2*k[n-1] + adj[n]")
print("\nSubstituting:")
print("  k[n] = 2*(2*(2*k[n-3] + adj[n-2]) + adj[n-1]) + adj[n]")
print("       = 8*k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]")
print("\nBUT we see k[n] = 9*k[n-3] + offset...")
print("So: 9*k[n-3] + offset = 8*k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]")
print("    offset = k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]")

print("\n### Verifying this relationship ###\n")

for n in range(34, 41):
    adj_n = (2**n) - get_m(n) * get_k(get_d(n))
    adj_n1 = (2**(n-1)) - get_m(n-1) * get_k(get_d(n-1))
    adj_n2 = (2**(n-2)) - get_m(n-2) * get_k(get_d(n-2))

    derived_offset = k[n-3] + 4*adj_n2 + 2*adj_n1 + adj_n
    actual_offset = k[n] - 9*k[n-3]

    match = "✓" if derived_offset == actual_offset else "✗"
    print(f"n={n}: derived={derived_offset}, actual={actual_offset} {match}")

# Key insight: the offset relationship
print("\n" + "=" * 80)
print("KEY INSIGHT: OFFSET DECOMPOSITION")
print("=" * 80)

print("""
offset[n] = k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]
          = k[n-3] + 4*(2^(n-2) - m[n-2]*k[d[n-2]])
                   + 2*(2^(n-1) - m[n-1]*k[d[n-1]])
                   + (2^n - m[n]*k[d[n]])

          = k[n-3] + 4*2^(n-2) + 2*2^(n-1) + 2^n
                   - 4*m[n-2]*k[d[n-2]] - 2*m[n-1]*k[d[n-1]] - m[n]*k[d[n]]

          = k[n-3] + 2^n + 2^n + 2^n
                   - 4*m[n-2]*k[d[n-2]] - 2*m[n-1]*k[d[n-1]] - m[n]*k[d[n]]

          = k[n-3] + 3*2^n - (4*m[n-2]*k[d[n-2]] + 2*m[n-1]*k[d[n-1]] + m[n]*k[d[n]])
""")

# Verify this final formula
print("\n### Final formula verification ###\n")

for n in range(34, 41):
    m_n = get_m(n)
    m_n1 = get_m(n-1)
    m_n2 = get_m(n-2)
    k_dn = get_k(get_d(n))
    k_dn1 = get_k(get_d(n-1))
    k_dn2 = get_k(get_d(n-2))

    derived = k[n-3] + 3*(2**n) - (4*m_n2*k_dn2 + 2*m_n1*k_dn1 + m_n*k_dn)
    actual = k[n] - 9*k[n-3]

    match = "✓" if derived == actual else "✗"
    print(f"n={n}: {match}")
    if derived != actual:
        print(f"  derived={derived}, actual={actual}")

# Now the key question: what determines offset[71]?
print("\n" + "=" * 80)
print("TO FIND OFFSET[71], WE NEED:")
print("=" * 80)

print("""
offset[71] = k[68] + 3*2^71 - (4*m[69]*k[d[69]] + 2*m[70]*k[d[70]] + m[71]*k[d[71]])

We KNOW:
- k[68] = k[68] (computed)
- 2^71 = known
- m[69], d[69], m[70], d[70] from data

We DON'T KNOW:
- m[71], d[71]

So the question becomes: WHAT IS m[71] and d[71]?
""")

# Print the known values for n=68,69,70
print("\nKnown values:")
print(f"k[68] = {k[68]}")
print(f"m[69] = {get_m(69)}, d[69] = {get_d(69)}, k[d[69]] = {get_k(get_d(69))}")
print(f"m[70] = {get_m(70)}, d[70] = {get_d(70)}, k[d[70]] = {get_k(get_d(70))}")

# The bridge constraint from k[80]
print("\n" + "=" * 80)
print("BRIDGE CONSTRAINT FROM K[80]")
print("=" * 80)

k_80 = 1105520030589234487939456

# k[80] = 9^4 * k[68] + 9^3*off[71] + 9^2*off[74] + 9*off[77] + off[80]
rhs_from_k68 = (9**4) * k[68]
remainder = k_80 - rhs_from_k68

print(f"k[80] = {k_80}")
print(f"9^4 * k[68] = {rhs_from_k68}")
print(f"k[80] - 9^4*k[68] = {remainder}")
print(f"\nThis equals: 9^3*off[71] + 9^2*off[74] + 9*off[77] + off[80]")
print(f"           = 729*off[71] + 81*off[74] + 9*off[77] + off[80]")
