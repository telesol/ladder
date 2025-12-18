#!/usr/bin/env python3
"""
Explore the TRANSITION point at n=5.
Why do we go from pure π convergents (3,7,22) to something else?

Key insight: Maybe the transition ISN'T random - maybe there's a rule
that connects to the NEXT mathematical constant!
"""

import sqlite3
from math import pi, sqrt, e
from fractions import Fraction

PHI = (1 + sqrt(5)) / 2

def load_keys():
    conn = sqlite3.connect("db/kh.db")
    cur = conn.cursor()
    cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
    rows = cur.fetchall()
    conn.close()
    return {r[0]: int(r[1], 16) for r in rows}

def compute_m_d(k, n):
    adj_n = k[n] - 2 * k[n-1]
    best_d, best_m = None, None
    best_m_abs = float('inf')
    for d in range(1, min(n, 9)):
        if k[d] == 0:
            continue
        numerator = (1 << n) - adj_n
        if numerator % k[d] == 0:
            m = numerator // k[d]
            if abs(m) < best_m_abs:
                best_m = m
                best_d = d
                best_m_abs = abs(m)
    return best_m, best_d

def main():
    keys = load_keys()
    k = [0] + [keys.get(i, 0) for i in range(1, 71)]

    print("=" * 70)
    print("TRANSITION POINT EXPLORATION")
    print("=" * 70)

    # Get m, d sequences
    m_vals = []
    d_vals = []
    adj_vals = []
    for n in range(2, 35):
        m, d = compute_m_d(k, n)
        adj_n = k[n] - 2 * k[n-1]
        m_vals.append(m)
        d_vals.append(d)
        adj_vals.append(adj_n)

    # Focus on n=4 to n=5 transition
    print("\n=== THE CRITICAL TRANSITION (n=4 → n=5) ===")
    print()
    print("n=4 is the LAST pure π convergent (m=22, d=1)")
    print("n=5 is the FIRST 'complex' value (m=9, d=2)")
    print()

    for n in range(2, 10):
        idx = n - 2
        print(f"n={n}: k[{n}]={k[n]:8d}, m={m_vals[idx]:6d}, d={d_vals[idx]}, adj={adj_vals[idx]:+8d}")

    # What's special about m[5]=9?
    print("\n=== WHAT IS m[5]=9? ===")
    m5 = 9
    print(f"m[5] = {m5}")
    print(f"  9 = 3² (perfect square of m[2]!)")
    print(f"  9 = k[2]² / 1 = 3²")
    print(f"  9 = m[2]² = 3²")
    print(f"  9 appears in: √2 convergents? e convergents?")

    # Check: is m[5] = m[2]²?
    print(f"\n  m[2]² = {m_vals[0]}² = {m_vals[0]**2}")
    print(f"  m[5] = {m_vals[3]}")
    print(f"  Match: {m_vals[0]**2 == m_vals[3]}")

    # What about other squared relationships?
    print("\n=== SQUARED RELATIONSHIPS ===")
    for i in range(len(m_vals[:15])):
        for j in range(i+1, len(m_vals[:15])):
            if m_vals[i]**2 == m_vals[j]:
                print(f"m[{j+2}] = m[{i+2}]² = {m_vals[i]}² = {m_vals[j]}")

    # What about m[6]=19?
    print("\n=== WHAT IS m[6]=19? ===")
    print("m[6] = 19")
    print("  19 is PRIME")
    print("  19 appears in e convergents!")

    # e convergents
    e_cf = [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8]
    p = [0, 1]
    q = [1, 0]
    print("\n  e convergents (p/q):")
    for i, a in enumerate(e_cf[:10]):
        p_i = a * p[-1] + p[-2]
        q_i = a * q[-1] + q[-2]
        p.append(p_i)
        q.append(q_i)
        print(f"    {p_i}/{q_i} = {p_i/q_i:.6f}")

    all_e = set(p[2:]) | set(q[2:])
    print(f"\n  All e convergent values: {sorted(all_e)[:20]}")
    print(f"  Is 19 in e convergents? {19 in all_e}")

    # What about m[7]=50?
    print("\n=== WHAT IS m[7]=50? ===")
    print("m[7] = 50")
    print("  50 = 2 × 25 = 2 × 5²")
    print("  50 = m[6] × 2 + 12 = 19 × 2 + 12")
    print(f"  50/19 = {50/19:.6f} ≈ e ({e:.6f})")

    # Pattern check: do consecutive m values relate by π, e, or φ?
    print("\n=== CONSECUTIVE m RATIOS vs CONSTANTS ===")
    for i in range(12):
        if m_vals[i] != 0:
            ratio = m_vals[i+1] / m_vals[i]
            pi_err = abs(ratio - pi)
            e_err = abs(ratio - e)
            phi_err = abs(ratio - PHI)
            half_err = abs(ratio - 0.5)
            third_err = abs(ratio - 1/3)
            two_err = abs(ratio - 2)

            best = min([
                ("π", pi_err), ("e", e_err), ("φ", phi_err),
                ("1/2", half_err), ("1/3", third_err), ("2", two_err)
            ], key=lambda x: x[1])

            print(f"m[{i+3}]/m[{i+2}] = {m_vals[i+1]:6d}/{m_vals[i]:6d} = {ratio:8.4f} | closest: {best[0]:4s} (err={best[1]:.4f})")

    # HYPOTHESIS: Cycling through constants
    print("\n=== HYPOTHESIS: CONSTANT CYCLING ===")
    print("""
What if the sequence cycles through:
  π → e → φ → π → e → φ → ...

Let's check which constant each transition approximates:
""")

    for i in range(15):
        if m_vals[i] != 0:
            ratio = m_vals[i+1] / m_vals[i]
            candidates = [("π", pi), ("e", e), ("φ", PHI)]
            closest = min(candidates, key=lambda x: abs(ratio - x[1]))
            if abs(ratio - closest[1]) < 0.5:
                print(f"  n={i+2}→{i+3}: ratio={ratio:.4f} ≈ {closest[0]}")

    # Look at d-sequence around transition
    print("\n=== d-SEQUENCE AROUND TRANSITION ===")
    print("d values:", d_vals[:12])
    print()
    print("Note: d=1 for n=2,3,4 (π phase)")
    print("      d=2 for n=5,6,7 (transition to e?)")
    print("      d jumps at n=8,10 (anomalies?)")

    # What determines d?
    print("\n=== WHY DOES d CHANGE? ===")
    print("d is chosen to minimize |m|.")
    print("Let's see what m would be for different d choices at n=5:")
    n = 5
    adj_5 = k[5] - 2 * k[4]
    print(f"\nn=5: k[5]={k[5]}, k[4]={k[4]}, adj={adj_5}")
    for d in range(1, 5):
        if k[d] != 0:
            num = (1 << n) - adj_5
            if num % k[d] == 0:
                m = num // k[d]
                print(f"  d={d}: m = {num}/{k[d]} = {m}")

    # What about the sums?
    print("\n=== SUM RELATIONSHIPS ===")
    print(f"m[2] + m[3] = {m_vals[0]} + {m_vals[1]} = {m_vals[0] + m_vals[1]}")
    print(f"m[3] + m[4] = {m_vals[1]} + {m_vals[2]} = {m_vals[1] + m_vals[2]}")
    print(f"m[4] + m[5] = {m_vals[2]} + {m_vals[3]} = {m_vals[2] + m_vals[3]}")
    print(f"m[2] + m[3] + m[4] = {sum(m_vals[:3])}")

    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print("""
1. m[5] = 9 = m[2]² = 3² (SQUARE of first π convergent!)
2. m[6] = 19 (appears in e convergents)
3. m[7]/m[6] = 50/19 ≈ e
4. The sequence seems to CYCLE through mathematical constants
5. d changes from 1 to 2 at n=5 - the "transition point"

HYPOTHESIS: The creator used π to seed (n=2,3,4), then switched
to a pattern that incorporates e and other constants!
""")

if __name__ == "__main__":
    main()
