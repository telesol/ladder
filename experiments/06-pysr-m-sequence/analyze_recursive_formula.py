#!/usr/bin/env python3
"""
Research Direction 3: Specify recursive F for d[n]>1 cases

When d[n]=1: m[n] = 2^n - adj[n]
When d[n]>1: m[n] = (2^n - adj[n]) / k[d[n]]

Let's verify and understand the recursive structure.
"""

import json
import sqlite3

# Load m, d, adj sequences
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
adj_seq = data['adj_seq']

D = {n: d_seq[n-2] for n in range(2, 2 + len(d_seq))}
M = {n: m_seq[n-2] for n in range(2, 2 + len(m_seq))}
ADJ = {n: adj_seq[n-2] for n in range(2, 2 + len(adj_seq)) if n-2 < len(adj_seq)}

# Load k-sequence from database
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
rows = cursor.fetchall()
conn.close()

K = {}
for puzzle_id, hex_val in rows:
    K[puzzle_id] = int(hex_val, 16)

print("=" * 80)
print("RECURSIVE FORMULA ANALYSIS FOR d[n]>1 CASES")
print("=" * 80)

print("\nThe fundamental recurrence is:")
print("    adj[n] = 2^n - m[n] * k[d[n]]")
print("\nRearranging:")
print("    m[n] = (2^n - adj[n]) / k[d[n]]")
print()

print("=" * 80)
print("VERIFICATION: m[n] = (2^n - adj[n]) / k[d[n]]")
print("=" * 80)
print()

all_correct = True
for n in range(2, 32):
    if n not in D or n not in M or n not in ADJ:
        continue

    d_n = D[n]
    m_n = M[n]
    adj_n = ADJ[n]

    if d_n not in K:
        print(f"n={n}: d[n]={d_n} not in k-sequence, skipping")
        continue

    k_d = K[d_n]
    power_2n = 2**n

    # Calculate m from formula
    numerator = power_2n - adj_n
    if numerator % k_d == 0:
        calculated_m = numerator // k_d
        if calculated_m == m_n:
            status = "✓"
        else:
            status = f"✗ got {calculated_m}"
            all_correct = False
    else:
        calculated_m = numerator / k_d
        status = f"✗ not divisible: {numerator} / {k_d}"
        all_correct = False

    print(f"n={n:2d} d={d_n}: m = (2^{n} - {adj_n:>12}) / k[{d_n}] = ({power_2n:>12} - {adj_n:>12}) / {k_d:>6} = {calculated_m:>12} {status}")

print(f"\n{'All formulas verified!' if all_correct else 'Some formulas failed!'}")

print("\n" + "=" * 80)
print("THE UNIFIED FORMULA")
print("=" * 80)
print("""
For ALL n ≥ 2:

    m[n] = (2^n - adj[n]) / k[d[n]]

Special case when d[n]=1:
    m[n] = (2^n - adj[n]) / k[1] = (2^n - adj[n]) / 1 = 2^n - adj[n]

This unifies both cases!

The formula works because:
    adj[n] = k[n] - 2*k[n-1]  (definition)
    k[n] = 2*k[n-1] + adj[n]  (rearranged)
    adj[n] = 2^n - m[n]*k[d[n]]  (from d-formula)

So all three sequences (k, m, d, adj) are interconnected.
""")

print("=" * 80)
print("FORMULA FOR d[n] > 1 CASES SPECIFICALLY")
print("=" * 80)
print()

print("For d[n] > 1, we have:")
print("    m[n] = (2^n - adj[n]) / k[d[n]]")
print()
print("The key is that k[d[n]] divides (2^n - adj[n]).")
print("This divisibility is what DEFINES d[n]:")
print("    d[n] = max{i : k[i] | (2^n - adj[n])}")
print()

print("Examples for d[n] > 1:")
print("-" * 70)
for n in range(2, 32):
    d_n = D.get(n, 0)
    if d_n > 1 and n in ADJ and d_n in K:
        m_n = M[n]
        adj_n = ADJ[n]
        k_d = K[d_n]
        power_2n = 2**n

        print(f"n={n:2d}: d={d_n}, k[{d_n}]={k_d}")
        print(f"       m[{n}] = (2^{n} - {adj_n}) / {k_d}")
        print(f"            = ({power_2n} - {adj_n}) / {k_d}")
        print(f"            = {power_2n - adj_n} / {k_d}")
        print(f"            = {m_n}")
        print()

print("=" * 80)
print("THE e-RATIO PATTERN")
print("=" * 80)

# Check if the e-ratio (m[26]/m[25] ≈ e) is consistent with the formula
m_25 = M[25]
m_26 = M[26]
ratio = m_26 / m_25

print(f"\nm[26] / m[25] = {m_26} / {m_25} = {ratio:.10f}")
print(f"e = 2.7182818284...")
print(f"Error = {abs(ratio - 2.7182818284) / 2.7182818284 * 100:.2f}%")
print()

# Can we derive this ratio from the formula?
print("From the formula:")
print(f"m[25] = (2^25 - adj[25]) / k[d[25]]")
print(f"      = (2^25 - {ADJ[25]}) / k[{D[25]}]")
print(f"      = ({2**25} - {ADJ[25]}) / {K[D[25]]}")
print(f"      = {2**25 - ADJ[25]} / {K[D[25]]}")
print(f"      = {m_25}")
print()
print(f"m[26] = (2^26 - adj[26]) / k[d[26]]")
print(f"      = (2^26 - {ADJ[26]}) / k[{D[26]}]")
print(f"      = ({2**26} - {ADJ[26]}) / {K[D[26]]}")
print(f"      = {2**26 - ADJ[26]} / {K[D[26]]}")
print(f"      = {m_26}")
print()

# The ratio
print("The e-ratio emerges from:")
print(f"m[26]/m[25] = (2^26 - adj[26]) / (2^25 - adj[25])")
print(f"            = {2**26 - ADJ[26]} / {2**25 - ADJ[25]}")
print(f"            = {(2**26 - ADJ[26]) / (2**25 - ADJ[25]):.10f}")
print()
print("Note: Both d[25]=1 and d[26]=1, so k[d[n]]=1 cancels out!")

print("\n" + "=" * 80)
print("SUMMARY: THE COMPLETE FORMULA SYSTEM")
print("=" * 80)
print("""
1. BOOTSTRAP (n=1,2,3):
   k[1] = 1, k[2] = 3, k[3] = 7 (Mersenne numbers: 2^n - 1)
   d[2] = 2, d[3] = 3 (self-reference)
   m[2] = m[3] = 1

2. UNIFIED FORMULA (n ≥ 4):
   m[n] = (2^n - adj[n]) / k[d[n]]

   Where:
   - adj[n] = k[n] - 2*k[n-1]
   - d[n] = max{i : k[i] | (2^n - adj[n])}

3. RECONSTRUCTION:
   k[n] = 2*k[n-1] + adj[n]
        = 2*k[n-1] + 2^n - m[n]*k[d[n]]

4. SPECIAL CASE (d[n]=1):
   m[n] = 2^n - adj[n]  (since k[1]=1)

The system is SELF-CONSISTENT but CIRCULAR:
- m depends on adj and d
- d depends on adj (via divisibility)
- adj depends on k
- k depends on adj (via recurrence)

To break the cycle, we need the INITIAL conditions (k[1-70])
and derive the PATTERN that generates them.
""")
