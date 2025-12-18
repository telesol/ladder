#!/usr/bin/env python3
"""
Deep analysis of normalized m values: m_n / 2^(n-d_n)
Looking for: fractions, recurring patterns, simple sequences
"""

import sqlite3
from fractions import Fraction

def load_keys():
    conn = sqlite3.connect("db/kh.db")
    cur = conn.cursor()
    cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
    rows = cur.fetchall()
    conn.close()
    return {r[0]: int(r[1], 16) for r in rows}

def compute_m_d(k, n):
    """Find m_n and d_n"""
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
    print("NORMALIZED M-VALUE DEEP ANALYSIS")
    print("=" * 70)

    norm_m_list = []
    m_list = []
    d_list = []

    for n in range(2, 71):
        m, d = compute_m_d(k, n)
        if m and d:
            norm_m = m / (1 << (n - d))
            norm_m_list.append(norm_m)
            m_list.append(m)
            d_list.append(d)

    # Print first 30 normalized m values
    print("\n=== Normalized m values (first 30) ===")
    print("n    m           d    norm_m        as_fraction")
    print("-" * 60)
    for i, n in enumerate(range(2, 32)):
        if i < len(norm_m_list):
            m, d = m_list[i], d_list[i]
            nm = norm_m_list[i]
            # Try to express as simple fraction
            frac = Fraction(nm).limit_denominator(1000)
            print(f"{n:3d}  {m:10d}  {d:2d}  {nm:12.6f}  {frac}")

    # Look for patterns in norm_m
    print("\n=== Pattern search in norm_m ===")

    # Check if norm_m values cluster around specific values
    clusters = {}
    for nm in norm_m_list:
        # Round to 2 decimal places
        rounded = round(nm * 4) / 4  # Quarter steps
        clusters[rounded] = clusters.get(rounded, 0) + 1

    print("\nClustering (quarter steps):")
    for v in sorted(clusters.keys()):
        print(f"  {v:.2f}: {clusters[v]} occurrences")

    # Check if there's a period in the sequence
    print("\n=== Periodicity check ===")
    for period in range(2, 20):
        diffs = []
        for i in range(period, min(40, len(norm_m_list))):
            diff = abs(norm_m_list[i] - norm_m_list[i - period])
            diffs.append(diff)
        avg_diff = sum(diffs) / len(diffs) if diffs else 0
        if avg_diff < 0.5:  # Low average difference suggests periodicity
            print(f"Period {period}: avg diff = {avg_diff:.4f}")

    # Check consecutive ratios
    print("\n=== Consecutive ratios norm_m[n] / norm_m[n-1] ===")
    for i in range(1, min(25, len(norm_m_list))):
        if norm_m_list[i-1] != 0:
            ratio = norm_m_list[i] / norm_m_list[i-1]
            print(f"n={i+3}: {norm_m_list[i]:.4f} / {norm_m_list[i-1]:.4f} = {ratio:.4f}")

    # Check if norm_m relates to n in a simple way
    print("\n=== norm_m vs f(n) ===")
    print("Testing: norm_m = a*n + b, norm_m = a/n + b, etc.")

    # Linear fit
    n_vals = list(range(2, 2 + len(norm_m_list)))
    mean_n = sum(n_vals) / len(n_vals)
    mean_nm = sum(norm_m_list) / len(norm_m_list)

    # Check simple functions of n
    for n, nm in zip(range(2, 20), norm_m_list[:18]):
        fn1 = 2 - 1/n  # approaches 2
        fn2 = 1 + 1/n  # approaches 1
        fn3 = n % 3 / 2 + 1  # periodic
        print(f"n={n:2d}: norm_m={nm:.4f}, 2-1/n={fn1:.4f}, 1+1/n={fn2:.4f}")

    # Check d values distribution
    print("\n=== d_n distribution ===")
    d_counts = {}
    for d in d_list:
        d_counts[d] = d_counts.get(d, 0) + 1
    for d in sorted(d_counts.keys()):
        print(f"d={d}: {d_counts[d]} times ({100*d_counts[d]/len(d_list):.1f}%)")

    # Check if there's a pattern in when d changes
    print("\n=== d_n sequence (first 50) ===")
    print("".join(str(d) for d in d_list[:50]))

    # Look for runs of same d
    print("\n=== Runs of same d value ===")
    runs = []
    current_d = d_list[0]
    run_len = 1
    for d in d_list[1:]:
        if d == current_d:
            run_len += 1
        else:
            runs.append((current_d, run_len))
            current_d = d
            run_len = 1
    runs.append((current_d, run_len))
    print(f"Runs: {runs[:20]}...")
    print(f"Max run length: {max(r[1] for r in runs)}")
    print(f"Average run length: {sum(r[1] for r in runs)/len(runs):.2f}")

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
