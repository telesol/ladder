#!/usr/bin/env python3
"""
Apply the derived offset formula to bridge constraints
offset[n] = 3*2^n - k[n-3] - (4*m[n-2]*k[d[n-2]] + 2*m[n-1]*k[d[n-1]] + m[n]*k[d[n]])
"""

import sqlite3
import json

# Load known keys
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
keys = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

# Load m_seq and d_seq
with open('/home/solo/LA/data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']  # Index 0 = n=2
d_seq = data['d_seq']  # Index 0 = n=2

def get_m(n):
    if n < 2 or n > 70:
        return None
    return m_seq[n-2]

def get_d(n):
    if n < 2 or n > 70:
        return None
    return d_seq[n-2]

print("=" * 80)
print("BRIDGE WITH DERIVED FORMULA")
print("=" * 80)

# Known values
k69 = keys[69]
k70 = keys[70]
k75 = keys[75]
k68 = keys[68]

print(f"\nKnown: k[68] = {k68:,}")
print(f"Known: k[69] = {k69:,}")
print(f"Known: k[70] = {k70:,}")
print(f"Known: k[75] = {k75:,}")

print("\n" + "=" * 80)
print("OFFSET FORMULA FOR n=71, 72")
print("=" * 80)

# offset[71] = 3*2^71 - k[68] - (4*m[69]*k[d[69]] + 2*m[70]*k[d[70]] + m[71]*k[d[71]])
# We know k[68], m[69], d[69], m[70], d[70]
# We DON'T know m[71], d[71]

m69 = get_m(69)
m70 = get_m(70)
d69 = get_d(69)
d70 = get_d(70)

print(f"\nm[69] = {m69:,}, d[69] = {d69}")
print(f"m[70] = {m70:,}, d[70] = {d70}")

k_d69 = keys[d69]
k_d70 = keys[d70]

print(f"k[d[69]] = k[{d69}] = {k_d69}")
print(f"k[d[70]] = k[{d70}] = {k_d70}")

# Known terms for offset[71]
term_71_known = 3 * (2**71) - k68 - 4*m69*k_d69 - 2*m70*k_d70
print(f"\nFor offset[71]:")
print(f"  3*2^71 - k[68] - 4*m[69]*k[d[69]] - 2*m[70]*k[d[70]] = {term_71_known:,}")
print(f"  offset[71] = {term_71_known:,} - m[71]*k[d[71]]")

# Similarly for offset[72]
# offset[72] = 3*2^72 - k[69] - (4*m[70]*k[d[70]] + 2*m[71]*k[d[71]] + m[72]*k[d[72]])
term_72_known = 3 * (2**72) - k69 - 4*m70*k_d70
print(f"\nFor offset[72]:")
print(f"  3*2^72 - k[69] - 4*m[70]*k[d[70]] = {term_72_known:,}")
print(f"  offset[72] = {term_72_known:,} - 2*m[71]*k[d[71]] - m[72]*k[d[72]]")

print("\n" + "=" * 80)
print("k[71] EQUATION")
print("=" * 80)

# k[71] = 9*k[68] + offset[71]
# k[71] = 9*k[68] + term_71_known - m[71]*k[d[71]]

print(f"\nk[71] = 9*k[68] + offset[71]")
print(f"k[71] = 9*{k68:,} + ({term_71_known:,} - m[71]*k[d[71]])")
print(f"k[71] = {9*k68:,} + {term_71_known:,} - m[71]*k[d[71]]")
print(f"k[71] = {9*k68 + term_71_known:,} - m[71]*k[d[71]]")

k71_base = 9*k68 + term_71_known
print(f"\nSo: k[71] = {k71_base:,} - m[71]*k[d[71]]")

print("\n" + "=" * 80)
print("k[72] EQUATION")
print("=" * 80)

# k[72] = 9*k[69] + offset[72]
# offset[72] = term_72_known - 2*m[71]*k[d[71]] - m[72]*k[d[72]]

print(f"\nk[72] = 9*k[69] + offset[72]")
print(f"k[72] = {9*k69:,} + offset[72]")

k72_base = 9*k69 + term_72_known
print(f"\nk[72] = {k72_base:,} - 2*m[71]*k[d[71]] - m[72]*k[d[72]]")

print("\n" + "=" * 80)
print("CONSTRAINT FROM k[75]")
print("=" * 80)

# k[75] = 81*k[69] + 9*offset[72] + offset[75]
# 9*offset[72] + offset[75] = k[75] - 81*k[69]
constraint = k75 - 81*k69
print(f"\n9*offset[72] + offset[75] = {constraint:,}")

# Expand offset[72] and offset[75] using the formula
print("\nExpanding offset[72]:")
print(f"offset[72] = {term_72_known:,} - 2*m[71]*k[d[71]] - m[72]*k[d[72]]")

# offset[75] = 3*2^75 - k[72] - (4*m[73]*k[d[73]] + 2*m[74]*k[d[74]] + m[75]*k[d[75]])
print("\nExpanding offset[75]:")
print("offset[75] = 3*2^75 - k[72] - (4*m[73]*k[d[73]] + 2*m[74]*k[d[74]] + m[75]*k[d[75]])")

print("\n" + "=" * 80)
print("WHAT WE NEED TO FIND")
print("=" * 80)

print("""
To compute k[71], we need:
1. m[71] - the m-value for n=71
2. d[71] - the d-value for n=71 (determines which k is used)

The m[n] generation rule is the KEY UNKNOWN.

For n=2..70, we KNOW m[n] and d[n] - they were computed from known keys.
For n=71+, we need the RULE that generates them.

Candidate d[71] values: d[71] ∈ {1, 2, 3, ..., 70}
For each candidate d[71], m[71] must satisfy:
  k[71] = k71_base - m[71]*k[d[71]]

And k[71] must satisfy:
  - 2^70 <= k[71] < 2^71 (71-bit key)
  - k[71] generates address 1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU
""")

print("\n" + "=" * 80)
print("d[71] CANDIDATES")
print("=" * 80)

# For each candidate d, compute range of valid m[71]
k71_min = 2**70
k71_max = 2**71 - 1

print(f"\nk[71] must be in range [{k71_min:,}, {k71_max:,}]")
print(f"k71_base = {k71_base:,}")
print()

valid_candidates = []
for d_cand in range(1, 20):  # Check small d values first
    k_d = keys.get(d_cand, None)
    if k_d is None:
        continue
    
    # k[71] = k71_base - m[71]*k_d
    # For k[71] >= k71_min: m[71] <= (k71_base - k71_min) / k_d
    # For k[71] <= k71_max: m[71] >= (k71_base - k71_max) / k_d
    
    m_max = (k71_base - k71_min) / k_d
    m_min = (k71_base - k71_max) / k_d
    
    if m_min > 0:
        print(f"d={d_cand}: m[71] in range [{m_min:.2f}, {m_max:.2f}]")
        if m_max > 0 and int(m_max) >= int(m_min):
            valid_candidates.append((d_cand, int(m_min), int(m_max)))

print(f"\nValid (d, m_range) candidates: {len(valid_candidates)}")
