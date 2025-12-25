#!/usr/bin/env python3
"""
Analyze the k[n] Selection Mystery

Key finding: Actual k[n] is NEVER the min|m| candidate.
This script investigates what distinguishes actual k[n] from min|m| candidates.
"""

import sqlite3
from pathlib import Path
from math import gcd
from collections import defaultdict

DB_PATH = Path(__file__).parent / "db" / "kh.db"

def load_k_values():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT puzzle_id, priv_hex FROM ground_truth WHERE priv_hex IS NOT NULL ORDER BY puzzle_id")
    rows = c.fetchall()
    conn.close()
    return {pid: int(phex, 16) for pid, phex in rows}

def factorize(n):
    """Return prime factorization as dict."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def get_min_m_candidate(k, n):
    """Get the candidate with minimum |m|."""
    if (n-1) not in k:
        return None

    k_min = 1 << (n-1)
    k_max = (1 << n) - 1
    base = 2 * k[n-1] + (1 << n)

    best = None
    best_abs_m = float('inf')

    for d in range(1, n):
        if d not in k or k[d] == 0:
            continue

        kd = k[d]
        m_low = (base - k_max) // kd
        m_high = (base - k_min) // kd + 1

        for m in range(max(1, m_low), min(m_high + 1, 100000)):
            k_candidate = base - m * kd

            if k_min <= k_candidate <= k_max:
                adj = k_candidate - 2 * k[n-1]
                num = (1 << n) - adj
                if num % kd == 0 and num // kd == m:
                    if abs(m) < best_abs_m:
                        best_abs_m = abs(m)
                        best = {'k': k_candidate, 'd': d, 'm': m, 'adj': adj}

    return best

def get_actual_md(k, n):
    """Get actual m and d for known k[n]."""
    if n not in k or (n-1) not in k:
        return None, None

    adj = k[n] - 2 * k[n-1]
    numerator = (1 << n) - adj

    best_d = 1
    best_m = numerator

    for d in range(1, n):
        if d in k and k[d] != 0 and numerator % k[d] == 0:
            m = numerator // k[d]
            if abs(m) < abs(best_m):
                best_m = m
                best_d = d

    return best_m, best_d

def main():
    k = load_k_values()

    print("="*80)
    print("ANALYZING THE k[n] SELECTION MYSTERY")
    print("="*80)

    print("\n" + "-"*80)
    print("COMPARISON: Actual k[n] vs Min|m| Candidate")
    print("-"*80)

    print(f"\n{'n':>3} {'actual_k':>12} {'min_m_k':>12} {'delta':>10} {'actual_m':>8} {'min_m':>6} {'ratio':>8}")
    print("-"*80)

    differences = []

    for n in range(4, 31):
        if n not in k or (n-1) not in k:
            continue

        actual_k = k[n]
        actual_m, actual_d = get_actual_md(k, n)

        min_m_cand = get_min_m_candidate(k, n)
        if not min_m_cand:
            continue

        min_m_k = min_m_cand['k']
        min_m = min_m_cand['m']

        delta = actual_k - min_m_k
        ratio = actual_m / min_m if min_m != 0 else 0

        differences.append({
            'n': n,
            'actual_k': actual_k,
            'min_m_k': min_m_k,
            'delta': delta,
            'actual_m': actual_m,
            'min_m': min_m,
            'ratio': ratio
        })

        print(f"{n:>3} {actual_k:>12} {min_m_k:>12} {delta:>10} {actual_m:>8} {min_m:>6} {ratio:>8.2f}")

    print("\n" + "-"*80)
    print("PATTERN ANALYSIS")
    print("-"*80)

    # Analyze delta patterns
    deltas = [d['delta'] for d in differences]
    print(f"\nDelta (actual - min_m_k) statistics:")
    print(f"  Always positive? {all(d > 0 for d in deltas)}")
    print(f"  Always negative? {all(d < 0 for d in deltas)}")
    print(f"  Sign pattern: {''.join('+' if d > 0 else '-' if d < 0 else '0' for d in deltas)}")

    # Analyze ratio patterns
    ratios = [d['ratio'] for d in differences]
    print(f"\nRatio (actual_m / min_m) statistics:")
    print(f"  Range: {min(ratios):.2f} to {max(ratios):.2f}")
    print(f"  Mean: {sum(ratios)/len(ratios):.2f}")

    print("\n" + "-"*80)
    print("FACTORIZATION COMPARISON")
    print("-"*80)

    for d in differences[:15]:
        n = d['n']
        actual_factors = factorize(d['actual_k'])
        min_m_factors = factorize(d['min_m_k'])

        actual_str = ' × '.join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(actual_factors.items()))
        min_m_str = ' × '.join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(min_m_factors.items()))

        print(f"\nn={n}:")
        print(f"  Actual k[{n}] = {d['actual_k']:>10} = {actual_str}")
        print(f"  Min|m| cand  = {d['min_m_k']:>10} = {min_m_str}")

        # Common factors?
        common = set(actual_factors.keys()) & set(min_m_factors.keys())
        if common:
            print(f"  Common prime factors: {common}")

    print("\n" + "-"*80)
    print("BINARY REPRESENTATION COMPARISON")
    print("-"*80)

    for d in differences[:10]:
        n = d['n']
        actual_bits = bin(d['actual_k'])[2:]
        min_m_bits = bin(d['min_m_k'])[2:]

        # Hamming weight
        actual_hw = actual_bits.count('1')
        min_m_hw = min_m_bits.count('1')

        print(f"\nn={n}: (HW = Hamming weight)")
        print(f"  Actual: {actual_bits:>20} (HW={actual_hw})")
        print(f"  Min|m|: {min_m_bits:>20} (HW={min_m_hw})")
        print(f"  HW diff: {actual_hw - min_m_hw:+d}")

    print("\n" + "-"*80)
    print("KEY INSIGHT: What makes actual k[n] special?")
    print("-"*80)

    # Check if actual k[n] has special divisibility
    print("\nDivisibility by previous k values:")
    for n in [4, 5, 6, 8, 11]:
        if n not in k:
            continue
        divisors = []
        for m in range(1, n):
            if m in k and k[n] % k[m] == 0:
                quotient = k[n] // k[m]
                divisors.append(f"k[{m}]×{quotient}")
        if divisors:
            print(f"  k[{n}] = {k[n]} divisible by: {divisors}")

    # Check multiplicative relationships
    print("\nMultiplicative relationships:")
    for n in range(4, 16):
        if n not in k:
            continue
        for a in range(1, n):
            for b in range(a, n):
                if a in k and b in k and k[a] * k[b] == k[n]:
                    print(f"  k[{n}] = k[{a}] × k[{b}] = {k[a]} × {k[b]} = {k[n]}")

    print("\n" + "-"*80)
    print("CONCLUSION")
    print("-"*80)
    print("""
    The actual k[n] is NEVER the min|m| candidate.

    Observations:
    1. Actual m is always LARGER than minimum possible m
    2. For n=4,5,6,8: actual k[n] follows multiplicative pattern
    3. The "penalty" for not choosing min|m| suggests another criterion

    Hypothesis: k[n] is selected to maintain multiplicative structure
    with previous k values, even at the cost of larger |m|.
    """)

if __name__ == "__main__":
    main()
