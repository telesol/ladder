#!/usr/bin/env python3
"""
Test: Does minimizing |m| actually select the correct k[n]?

The coder claimed this works, but generated k[4]=29 when actual k[4]=8.
Let's test against real data.
"""

import sqlite3
import os

DB_PATH = "/home/rkh/ladder/db/kh.db"

def load_k_values():
    """Load actual k values from database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Use ground_truth table with priv_hex
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
        # Convert hex to int
        if priv_hex.startswith('0x'):
            k[puzzle_id] = int(priv_hex, 16)
        else:
            k[puzzle_id] = int(priv_hex, 16)
    return k

def compute_candidates(k, n, max_candidates=1000):
    """
    For k[n], find all valid candidates that satisfy the recurrence
    with some valid d and integer m.

    Recurrence: k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]

    For each possible d (1 to n-1), and for integer m values,
    compute candidate = 2*k[n-1] + 2^n - m*k[d]
    """
    candidates = []
    base = 2 * k[n-1] + (1 << n)  # 2*k[n-1] + 2^n

    # For each valid d
    for d in range(1, n):
        kd = k[d]
        # m can be positive or negative
        # candidate = base - m*kd
        # For candidate > 0: m < base/kd
        # For reasonable range, check m from -100 to base/kd + 100
        max_m = base // kd + 100
        min_m = -100

        for m in range(min_m, max_m + 1):
            candidate = base - m * kd
            if candidate > 0:
                # Verify this is actually valid
                adj = candidate - 2 * k[n-1]
                numerator = (1 << n) - adj
                if numerator % kd == 0:
                    m_check = numerator // kd
                    if m_check == m:
                        candidates.append({
                            'k': candidate,
                            'd': d,
                            'm': m,
                            'kd': kd,
                            '|m|': abs(m)
                        })

    return candidates

def main():
    k = load_k_values()
    print(f"Loaded {len(k)} k values")
    print(f"k[1..10]: {[k.get(i) for i in range(1, 11)]}")
    print()

    # Test for n=4 to 20
    results = []
    for n in range(4, min(21, max(k.keys()) + 1)):
        if n not in k:
            continue

        actual_k = k[n]

        # Get all valid candidates
        candidates = compute_candidates(k, n)

        if not candidates:
            print(f"n={n}: NO CANDIDATES FOUND!")
            continue

        # Find candidate with minimum |m|
        min_m_candidate = min(candidates, key=lambda x: x['|m|'])

        # Find the actual one
        actual_candidate = None
        for c in candidates:
            if c['k'] == actual_k:
                actual_candidate = c
                break

        if actual_candidate is None:
            print(f"n={n}: ACTUAL k={actual_k} NOT IN CANDIDATES!")
            continue

        match = (min_m_candidate['k'] == actual_k)
        results.append(match)

        if not match:
            print(f"n={n}: MISMATCH!")
            print(f"  Actual: k={actual_k}, m={actual_candidate['m']}, d={actual_candidate['d']}")
            print(f"  Min |m|: k={min_m_candidate['k']}, m={min_m_candidate['m']}, d={min_m_candidate['d']}")

            # Show all candidates with small |m|
            small_m = sorted([c for c in candidates if c['|m|'] <= 5], key=lambda x: x['|m|'])
            print(f"  Candidates with |m|<=5: {len(small_m)}")
            for c in small_m[:10]:
                marker = " <-- ACTUAL" if c['k'] == actual_k else ""
                print(f"    k={c['k']}, m={c['m']}, d={c['d']}, kd={c['kd']}{marker}")
        else:
            print(f"n={n}: MATCH - k={actual_k}, m={actual_candidate['m']}, d={actual_candidate['d']}")

    print()
    print(f"Results: {sum(results)}/{len(results)} matches ({100*sum(results)/len(results):.1f}%)")

    if sum(results) < len(results):
        print("\n==> 'Minimize |m|' does NOT uniquely determine k[n]!")
        print("==> Need additional constraint to break ties or select among candidates.")

if __name__ == "__main__":
    main()
