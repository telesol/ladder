#!/usr/bin/env python3
"""
Explore connections to multiple mathematical constants
"""

import sqlite3
from math import pi, e, sqrt, log

# Golden ratio
PHI = (1 + sqrt(5)) / 2

# Famous continued fractions
PI_CF = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1]  # π
E_CF = [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8]  # e
PHI_CF = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # φ (all 1s)
SQRT2_CF = [1, 2, 2, 2, 2, 2, 2, 2, 2, 2]  # √2

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

def cf_convergents(cf_terms, max_n=15):
    """Compute convergents from continued fraction terms"""
    convergents = []
    p = [0, 1]
    q = [1, 0]
    for i, a in enumerate(cf_terms[:max_n]):
        p_i = a * p[-1] + p[-2]
        q_i = a * q[-1] + q[-2]
        p.append(p_i)
        q.append(q_i)
        convergents.append((p_i, q_i))
    return convergents

def main():
    keys = load_keys()
    k = [0] + [keys.get(i, 0) for i in range(1, 71)]

    print("=" * 70)
    print("MULTIPLE CONSTANTS EXPLORATION")
    print("=" * 70)

    # Get m values
    m_vals = []
    for n in range(2, 35):
        m, d = compute_m_d(k, n)
        if m:
            m_vals.append(m)

    print(f"\nFirst 20 m values: {m_vals[:20]}")

    # Get convergent numerators and denominators for each constant
    pi_convs = cf_convergents(PI_CF)
    e_convs = cf_convergents(E_CF)
    phi_convs = cf_convergents(PHI_CF)
    sqrt2_convs = cf_convergents(SQRT2_CF)

    print("\n=== π convergents ===")
    pi_nums = [p for p, q in pi_convs]
    pi_dens = [q for p, q in pi_convs]
    print(f"Numerators: {pi_nums}")
    print(f"Denominators: {pi_dens}")

    print("\n=== e convergents ===")
    e_nums = [p for p, q in e_convs]
    e_dens = [q for p, q in e_convs]
    print(f"Numerators: {e_nums}")
    print(f"Denominators: {e_dens}")

    print("\n=== φ (golden) convergents (Fibonacci!) ===")
    phi_nums = [p for p, q in phi_convs]
    phi_dens = [q for p, q in phi_convs]
    print(f"Numerators: {phi_nums}")
    print(f"Denominators: {phi_dens}")

    # Check which m values appear in which constant's convergents
    print("\n=== Which m values appear in convergents? ===")
    all_pi = set(pi_nums + pi_dens)
    all_e = set(e_nums + e_dens)
    all_phi = set(phi_nums + phi_dens)

    for i, m in enumerate(m_vals[:25]):
        matches = []
        if m in all_pi:
            matches.append("π")
        if m in all_e:
            matches.append("e")
        if m in all_phi:
            matches.append("φ")
        if matches:
            print(f"m[{i+2}] = {m:8d} → appears in: {', '.join(matches)}")
        else:
            print(f"m[{i+2}] = {m:8d}")

    # Check Fibonacci connection (φ convergents are Fibonacci!)
    print("\n=== Fibonacci connection ===")
    fibs = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
    print(f"Fibonacci: {fibs}")
    print(f"Our k values: {[k[i] for i in range(1, 18)]}")
    print()
    fib_set = set(fibs)
    for i in range(1, 18):
        match = "FIBONACCI!" if k[i] in fib_set else ""
        print(f"k[{i:2d}] = {k[i]:6d} {match}")

    # Check if m values relate to Fibonacci
    print("\n=== m values vs Fibonacci ===")
    for i, m in enumerate(m_vals[:15]):
        match = "FIBONACCI!" if m in fib_set else ""
        print(f"m[{i+2}] = {m:6d} {match}")

    # Check ratios between consecutive m values
    print("\n=== Ratios m[n+1]/m[n] vs constants ===")
    for i in range(len(m_vals[:15]) - 1):
        if m_vals[i] != 0:
            ratio = m_vals[i+1] / m_vals[i]
            # Compare to constants
            diffs = {
                'π': abs(ratio - pi),
                'e': abs(ratio - e),
                'φ': abs(ratio - PHI),
                '√2': abs(ratio - sqrt(2)),
                '2': abs(ratio - 2),
                '3': abs(ratio - 3),
            }
            closest = min(diffs, key=diffs.get)
            if diffs[closest] < 0.2:
                print(f"m[{i+3}]/m[{i+2}] = {ratio:.4f} ≈ {closest} ({diffs[closest]:.4f} diff)")

    print("\n" + "=" * 70)
    print("EXPLORATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
