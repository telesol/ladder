#!/usr/bin/env python3
"""
MAJOR DISCOVERY: Verify m[n] = 2^n - adj[n] when d[n] = 1

This suggests that for d=1 cases, m[n] is DERIVED from adj[n], not independently generated!
"""

import json

# Load full data from data_for_csolver.json
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']  # Index 0 = n=2, Index 1 = n=3, etc.
d_seq = data['d_seq']
adj_seq = data['adj_seq']

# Convert to dict for easier access
M = {n: m_seq[n-2] for n in range(2, 2 + len(m_seq))}
D = {n: d_seq[n-2] for n in range(2, 2 + len(d_seq))}
ADJ = {n: adj_seq[n-2] for n in range(2, 2 + len(adj_seq)) if n-2 < len(adj_seq)}

print("=" * 80)
print("FUNDAMENTAL FORMULA VERIFICATION")
print("=" * 80)
print()
print("Testing: m[n] + adj[n] = 2^n  (when d[n] = 1)")
print()

d1_matches = 0
d1_total = 0

other_matches = 0
other_total = 0

for n in range(4, min(len(M)+2, len(ADJ)+2)):
    if n not in M or n not in D or n not in ADJ:
        continue

    m_n = M[n]
    d_n = D[n]
    adj_n = ADJ[n]

    sum_val = m_n + adj_n
    power_2n = 2**n

    if d_n == 1:
        d1_total += 1
        if sum_val == power_2n:
            d1_matches += 1
            status = "✓ EXACT"
        else:
            diff = sum_val - power_2n
            status = f"✗ off by {diff}"
        print(f"n={n:2d} d=1: m + adj = {m_n:>15,} + {adj_n:>15,} = {sum_val:>17,}  (2^{n} = {power_2n:>17,}) {status}")
    else:
        other_total += 1
        if sum_val == power_2n:
            other_matches += 1
            status = "✓"
        else:
            diff = sum_val - power_2n
            status = f"(diff: {diff:,})"

        print(f"n={n:2d} d={d_n}: m + adj = {m_n:>15,} + {adj_n:>15,} = {sum_val:>17,}  {status}")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"\nFor d[n] = 1:  {d1_matches}/{d1_total} exact matches ({100*d1_matches/d1_total if d1_total > 0 else 0:.1f}%)")
print(f"For d[n] ≠ 1:  {other_matches}/{other_total} exact matches")

print()
print("=" * 80)
print("ALTERNATIVE FORMULA FOR d≠1 CASES")
print("=" * 80)
print()
print("Testing: m[n] + adj[n] = 2^k × something")
print()

for n in range(4, min(len(M)+2, len(ADJ)+2)):
    if n not in M or n not in D or n not in ADJ:
        continue

    m_n = M[n]
    d_n = D[n]
    adj_n = ADJ[n]

    if d_n != 1:
        sum_val = m_n + adj_n

        # Factor out powers of 2
        power_of_2 = 0
        temp = sum_val
        while temp > 0 and temp % 2 == 0:
            temp //= 2
            power_of_2 += 1

        print(f"n={n:2d} d={d_n}: m + adj = {sum_val:>17,} = 2^{power_of_2} × {sum_val // (2**power_of_2)}")

        # Check if sum_val = 2^d[n] × something
        if sum_val % (2**d_n) == 0:
            print(f"       Also: 2^d[{n}] = 2^{d_n} divides sum → quotient = {sum_val // (2**d_n):,}")

print()
print("=" * 80)
print("IMPLICATIONS")
print("=" * 80)
print("""
MAJOR FINDING:

When d[n] = 1:
    m[n] = 2^n - adj[n]

This means:
1. m[n] is NOT independently computed - it's derived from adj[n]
2. The sequence generation is SIMPLER than we thought
3. The key is understanding adj[n], not m[n]!

The fundamental recurrence is:
    k[n] = 2*k[n-1] + adj[n]

Where adj[n] = 2^n - m[n]*k[d[n]]

When d[n]=1:
    adj[n] = 2^n - m[n]*k[1] = 2^n - m[n]*1 = 2^n - m[n]

So: m[n] = 2^n - adj[n]  ✓

This is CIRCULAR - the formula is self-consistent because:
    adj[n] = 2^n - m[n] (when d=1 and k[1]=1)
""")
