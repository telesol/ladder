#!/usr/bin/env python3
"""
Explore B-Solver's continued fraction hypothesis
Does norm_m converge? Is it approximating an irrational?
"""

import sqlite3
from math import sqrt, pi, e
from fractions import Fraction

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

def continued_fraction_convergents(x, n_terms):
    """Generate convergents of x's continued fraction"""
    convergents = []
    a = []
    xi = x
    for _ in range(n_terms):
        ai = int(xi)
        a.append(ai)
        if xi - ai < 1e-10:
            break
        xi = 1 / (xi - ai)

    # Compute convergents p/q
    p = [0, 1]
    q = [1, 0]
    for i, ai in enumerate(a):
        p_i = ai * p[-1] + p[-2]
        q_i = ai * q[-1] + q[-2]
        p.append(p_i)
        q.append(q_i)
        if q_i > 0:
            convergents.append((p_i, q_i, p_i / q_i))

    return convergents, a

def main():
    keys = load_keys()
    k = [0] + [keys.get(i, 0) for i in range(1, 71)]

    print("=" * 70)
    print("CONTINUED FRACTION EXPLORATION")
    print("=" * 70)

    # Compute norm_m sequence
    norm_m_list = []
    for n in range(2, 71):
        m, d = compute_m_d(k, n)
        if m and d:
            norm_m = m / (1 << (n - d))
            norm_m_list.append(norm_m)

    # Check convergence
    print("\n=== Does norm_m converge? ===")
    print("Running averages:")
    for window in [5, 10, 20, 30, 50]:
        if len(norm_m_list) >= window:
            avg = sum(norm_m_list[-window:]) / window
            print(f"  Last {window} values avg: {avg:.6f}")

    overall_avg = sum(norm_m_list) / len(norm_m_list)
    print(f"\nOverall average: {overall_avg:.6f}")

    # Compare to known constants
    print("\n=== Compare to known constants ===")
    constants = [
        ("sqrt(2)", sqrt(2)),
        ("sqrt(3)", sqrt(3)),
        ("phi (golden)", (1 + sqrt(5)) / 2),
        ("pi/2", pi / 2),
        ("e/2", e / 2),
        ("ln(2)*2", 0.693147 * 2),
        ("5/3", 5/3),
        ("12/7", 12/7),
    ]

    for name, val in constants:
        diff = abs(overall_avg - val)
        print(f"  {name} = {val:.6f}, diff from avg = {diff:.6f}")

    # What if norm_m is continued fraction convergents of something?
    print("\n=== Continued fraction of norm_m average ===")
    convergents, cf_terms = continued_fraction_convergents(overall_avg, 15)
    print(f"Continued fraction terms: {cf_terms}")
    print("Convergents:")
    for i, (p, q, val) in enumerate(convergents[:10]):
        print(f"  {p}/{q} = {val:.6f}")

    # Look at the actual norm_m fractions
    print("\n=== First 15 norm_m as fractions ===")
    for i, n in enumerate(range(2, 17)):
        m, d = compute_m_d(k, n)
        if m and d:
            norm = m / (1 << (n - d))
            frac = Fraction(norm).limit_denominator(1024)
            # Also compute exact fraction
            exact_num = m
            exact_denom = 1 << (n - d)
            print(f"n={n:2d}: m={m:6d}, d={d}, exact={exact_num}/{exact_denom:4d}, ~{frac}, val={norm:.6f}")

    # What are the NUMERATORS when d=1?
    print("\n=== Pattern in numerators when d=1 ===")
    print("(Looking for sequence: 3, 7, 22, 493, 1921, 8342, ...)")
    d1_m = []
    for n in range(2, 30):
        m, d = compute_m_d(k, n)
        if d == 1:
            d1_m.append((n, m))
            print(f"n={n:2d}: m={m}")

    # Check differences between consecutive d=1 values
    print("\n=== Differences/ratios between d=1 m values ===")
    for i in range(1, min(10, len(d1_m))):
        n_prev, m_prev = d1_m[i-1]
        n_cur, m_cur = d1_m[i]
        if m_prev != 0:
            ratio = m_cur / m_prev
            diff = m_cur - m_prev
            print(f"m[{n_cur}]/m[{n_prev}] = {m_cur}/{m_prev} = {ratio:.4f}, diff = {diff}")

    # Check if m relates to 2^n somehow
    print("\n=== m / 2^(n/2) when d=1 ===")
    for n, m in d1_m[:15]:
        ratio = m / (2 ** (n/2))
        print(f"n={n:2d}: m={m:8d}, m/2^(n/2) = {ratio:.4f}")

    print("\n" + "=" * 70)
    print("EXPLORATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
