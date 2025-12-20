#!/usr/bin/env python3
"""
Search for valid (m[71], d[71]) pairs using the derived equation.
k[71] = 4,302,057,189,444,869,987,810 - m[71]*k[d[71]]

Strategy: For each d, compute the m-range and search for patterns.
"""

import sqlite3

# Load all known k-values
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
K = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

K71_BASE = 4302057189444869987810
K71_MIN = 2**70
K71_MAX = 2**71 - 1

print("=" * 80)
print("SEARCHING FOR VALID (m[71], d[71]) PAIRS")
print("=" * 80)
print(f"\nk[71] = {K71_BASE:,} - m[71]*k[d[71]]")
print(f"k[71] must be in [{K71_MIN:,}, {K71_MAX:,}]")

print("\n" + "-" * 80)
print("CANDIDATE d-VALUES AND m-RANGES")
print("-" * 80)

candidates = []
for d in range(1, 21):
    k_d = K.get(d)
    if k_d is None:
        continue
    
    # k[71] = K71_BASE - m*k_d
    # For k[71] >= K71_MIN: m <= (K71_BASE - K71_MIN) / k_d
    # For k[71] <= K71_MAX: m >= (K71_BASE - K71_MAX) / k_d
    
    m_max = (K71_BASE - K71_MIN) / k_d
    m_min = (K71_BASE - K71_MAX) / k_d
    
    if m_max < 0:
        continue
    
    m_min_int = max(1, int(m_min) + 1 if m_min > 0 else 1)
    m_max_int = int(m_max)
    
    if m_max_int >= m_min_int:
        count = m_max_int - m_min_int + 1
        candidates.append((d, m_min_int, m_max_int, count))
        print(f"d={d:2d}: k[{d}]={k_d:,}")
        print(f"       m[71] ∈ [{m_min_int:,}, {m_max_int:,}]")
        print(f"       Count: {count:,} candidates")
        print()

print("-" * 80)
print("TOTAL SEARCH SPACE")
print("-" * 80)
total = sum(c[3] for c in candidates)
print(f"Total candidates: {total:,}")
print("This is too large for brute force!")

print("\n" + "-" * 80)
print("PATTERN-BASED REDUCTION")
print("-" * 80)

# Load m-sequence to analyze patterns
import json
with open('/home/solo/LA/data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']

print("\nRecent m-values (n=60..70):")
for n in range(60, 71):
    m = m_seq[n-2]
    print(f"  m[{n}] = {m:,}")

# Check if m[71] follows a pattern from recent values
m70 = m_seq[70-2]
m69 = m_seq[69-2]
m68 = m_seq[68-2]

print(f"\nRatio analysis:")
print(f"  m[70]/m[69] = {m70/m69:.4f}")
print(f"  m[69]/m[68] = {m69/m68:.4f}")
print(f"  m[68]/m[67] = {m68/m_seq[67-2]:.4f}")

# Estimate m[71] from ratios (for reference, NOT assumption!)
avg_ratio = (m70/m69 + m69/m68) / 2
m71_estimate = int(m70 * avg_ratio)
print(f"\n  Average ratio: {avg_ratio:.4f}")
print(f"  Estimated m[71] (for reference): {m71_estimate:,}")
print(f"  BUT this is an ESTIMATE, not the formula!")

print("\n" + "-" * 80)
print("WHAT WE NEED")
print("-" * 80)
print("""
To find m[71], we need:
1. The generation RULE for m[n] (not ratio extrapolation!)
2. OR: Check if m[71] has special structure (19×prime, etc.)
3. OR: Use constraints from k[75] to narrow down

The models are working on finding the rule.
Once found, we can COMPUTE m[71] exactly.
""")
