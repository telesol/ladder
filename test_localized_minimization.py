#!/usr/bin/env python3
"""
Test: Localized Minimization with Memory Window

Hypothesis from 8-hour deep exploration session:
- k[n] is selected by minimizing |m[n]| within a "memory window" of recent d values
- Window size = 5 (only consider d ∈ [n-5, n-1])

This test checks if this rule UNIQUELY determines k[n] from k[1..n-1].
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "db" / "kh.db"

def load_k_values():
    """Load known k values from database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT puzzle_id, priv_hex
        FROM ground_truth
        WHERE priv_hex IS NOT NULL
        ORDER BY puzzle_id
    """)
    rows = c.fetchall()
    conn.close()

    k = {}
    for puzzle_id, priv_hex in rows:
        k[puzzle_id] = int(priv_hex, 16)
    return k

def find_d_and_m(k, n):
    """Find actual d[n] and m[n] for known k[n]."""
    if n not in k or (n-1) not in k:
        return None, None

    adj_n = k[n] - 2 * k[n-1]
    numerator = (1 << n) - adj_n

    best_d = 1
    best_m = numerator  # m when d=1 (k[1]=1)

    for d in range(1, n):
        if d in k and k[d] != 0 and numerator % k[d] == 0:
            m = numerator // k[d]
            if abs(m) < abs(best_m):
                best_m = m
                best_d = d

    return best_d, best_m

def test_localized_minimization(k, window_size=5):
    """
    Test if k[n] is uniquely determined by minimizing |m[n]|
    within a memory window.

    For each n, we:
    1. Only consider d ∈ [max(1, n-window_size), n-1]
    2. Find all (k_candidate, d, m) where m is integer
    3. Select k_candidate that minimizes |m|
    4. Check if it matches actual k[n]
    """
    print(f"\n{'='*60}")
    print(f"Testing Localized Minimization with Window Size = {window_size}")
    print(f"{'='*60}")

    matches = 0
    total = 0

    for n in range(4, 31):  # Start at 4 (n=1,2,3 are bootstrap)
        if n not in k or (n-1) not in k:
            continue

        actual_k = k[n]
        actual_d, actual_m = find_d_and_m(k, n)

        # Find candidates within memory window
        d_min = max(1, n - window_size)
        d_max = n - 1

        best_candidates = []
        min_abs_m = float('inf')

        # For each d in window, find all valid k candidates
        for d in range(d_min, d_max + 1):
            if d not in k or k[d] == 0:
                continue

            kd = k[d]
            base = 2 * k[n-1] + (1 << n)  # 2*k[n-1] + 2^n

            # k[n] must be in [2^(n-1), 2^n)
            k_min = 1 << (n-1)
            k_max = (1 << n) - 1

            # From: k[n] = base - m*k[d]
            # k_min <= base - m*k[d] <= k_max
            # (base - k_max) / k[d] <= m <= (base - k_min) / k[d]

            m_upper = (base - k_min) // kd + 1
            m_lower = (base - k_max) // kd - 1

            for m in range(max(1, m_lower), m_upper + 1):
                k_candidate = base - m * kd

                if k_min <= k_candidate <= k_max:
                    # Verify this is truly valid (m is integer for adj)
                    adj = k_candidate - 2 * k[n-1]
                    num = (1 << n) - adj
                    if num % kd == 0:
                        calc_m = num // kd
                        if calc_m == m:
                            if abs(m) < min_abs_m:
                                min_abs_m = abs(m)
                                best_candidates = [(k_candidate, d, m)]
                            elif abs(m) == min_abs_m:
                                best_candidates.append((k_candidate, d, m))

        # Check if actual k[n] is among best candidates
        found = False
        for cand_k, cand_d, cand_m in best_candidates:
            if cand_k == actual_k:
                found = True
                break

        total += 1
        if found:
            matches += 1
            status = "MATCH"
        else:
            status = "FAIL"
            # Show what we expected vs got
            if best_candidates:
                print(f"n={n}: {status}")
                print(f"  Actual: k={actual_k}, d={actual_d}, |m|={abs(actual_m)}")
                print(f"  Best candidates ({len(best_candidates)}): min|m|={min_abs_m}")
                for cand_k, cand_d, cand_m in best_candidates[:3]:
                    print(f"    k={cand_k}, d={cand_d}, m={cand_m}")

    print(f"\nResults: {matches}/{total} matches ({100*matches/total:.1f}%)")
    return matches, total

def main():
    print("Loading k values from database...")
    k = load_k_values()
    print(f"Loaded {len(k)} k values")

    # Show actual d values for reference
    print("\nActual d[n] and m[n] values:")
    for n in range(4, 21):
        if n in k:
            d, m = find_d_and_m(k, n)
            print(f"  n={n}: d={d}, m={m}, k={k[n]}")

    # Test with different window sizes
    for window in [3, 5, 7, 10, 15, 20]:
        test_localized_minimization(k, window)

    # Key insight test: does d-minimization WITHIN the window match actual d?
    print("\n" + "="*60)
    print("Testing: Does actual d[n] minimize |m| within its window?")
    print("="*60)

    for window in [3, 5, 10]:
        matches = 0
        total = 0
        for n in range(4, 31):
            if n not in k or (n-1) not in k:
                continue

            actual_d, actual_m = find_d_and_m(k, n)
            if actual_d is None:
                continue

            d_min = max(1, n - window)

            # Check if actual_d is in window
            if actual_d >= d_min:
                total += 1
                # Find min |m| within window
                min_m_in_window = float('inf')
                for d in range(d_min, n):
                    if d not in k or k[d] == 0:
                        continue
                    adj = k[n] - 2*k[n-1]
                    num = (1 << n) - adj
                    if num % k[d] == 0:
                        m = abs(num // k[d])
                        min_m_in_window = min(min_m_in_window, m)

                if abs(actual_m) == min_m_in_window:
                    matches += 1

        print(f"Window={window}: {matches}/{total} cases where actual d minimizes |m| in window")

if __name__ == "__main__":
    main()
