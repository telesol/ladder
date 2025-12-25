#!/usr/bin/env python3
"""
Ladder Generator: Reverse-engineer and implement the key generation algorithm
=============================================================================
Based on Wave 20 model consensus: d[n] is chosen to MINIMIZE |m[n]|.
"""

import sqlite3
from typing import Dict, Tuple

def load_known_keys() -> Dict[int, int]:
    """Load all known keys from the database."""
    conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
    cursor = conn.cursor()
    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id")
    keys = {}
    for row in cursor.fetchall():
        puzzle_id = row[0]
        priv_hex = row[1]
        if puzzle_id is not None:
            keys[int(puzzle_id)] = int(priv_hex, 16)
    conn.close()
    return keys


def compute_d_minimizing_m(k: Dict[int, int], n: int) -> Tuple[int, int]:
    """
    Compute d[n] and m[n] using d-minimization rule.
    d[n] is chosen to MINIMIZE |m[n]|.
    
    From recurrence: k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
    Rearranged: m[n]*k[d[n]] = 2*k[n-1] + 2^n - k[n]
    So: m[n] = (2*k[n-1] + 2^n - k[n]) / k[d[n]]
    """
    if n not in k or (n-1) not in k:
        return (-1, -1)

    numerator = 2 * k[n-1] + (2**n) - k[n]
    
    best_d = -1
    best_m = None

    for d in range(1, n):
        if d not in k:
            continue
        if k[d] == 0:
            continue
        if numerator % k[d] == 0:
            m = numerator // k[d]
            if best_m is None or abs(m) < abs(best_m):
                best_d = d
                best_m = m

    return (best_d, best_m if best_m is not None else -1)


def verify_recurrence(k: Dict[int, int], n: int, d: int, m: int) -> bool:
    """Verify that k[n] = 2*k[n-1] + 2^n - m*k[d]."""
    if n not in k or (n-1) not in k or d not in k:
        return False
    computed = 2 * k[n-1] + (2**n) - m * k[d]
    return computed == k[n]


def analyze_all_keys(k: Dict[int, int]) -> Dict[int, Tuple[int, int, bool]]:
    """Analyze d[n] and m[n] for all known keys."""
    results = {}
    puzzle_ids = sorted([p for p in k.keys() if p is not None])

    for n in puzzle_ids:
        if n < 2:
            continue
        if (n-1) not in k:
            continue

        d, m = compute_d_minimizing_m(k, n)
        if d > 0:
            valid = verify_recurrence(k, n, d, m)
            results[n] = (d, m, valid)

    return results


def forward_generate(k_init: Dict[int, int], n_max: int) -> Dict[int, int]:
    """
    Generate keys forward using the ladder recurrence.
    Uses d-minimization: choose d that gives smallest |m|.
    """
    k = dict(k_init)

    for n in range(4, n_max + 1):
        if n in k:
            continue
        if (n-1) not in k:
            print(f"  Cannot compute k[{n}]: k[{n-1}] unknown")
            break

        # Try all possible d values and find valid (d, m, k[n]) tuples
        candidates = []
        base = 2 * k[n-1] + (2**n)

        for d in range(1, n):
            if d not in k or k[d] == 0:
                continue

            # k[n] = base - m*k[d]
            # For valid range: 2^(n-1) <= k[n] < 2^n
            # => 2^(n-1) <= base - m*k[d] < 2^n
            # => base - 2^n < m*k[d] <= base - 2^(n-1)
            
            lower_bound = 2**(n-1)
            upper_bound = 2**n - 1
            
            # m*k[d] must be in range (base - upper_bound, base - lower_bound]
            min_product = base - upper_bound
            max_product = base - lower_bound
            
            # Find integer m values
            m_min = (min_product // k[d]) + 1
            m_max = max_product // k[d]
            
            for m in range(max(1, m_min), m_max + 1):
                k_n = base - m * k[d]
                if lower_bound <= k_n <= upper_bound:
                    candidates.append((d, m, k_n))

        if not candidates:
            print(f"  No valid candidates for k[{n}]")
            break

        # Choose candidate with smallest |m| (d-minimization)
        best = min(candidates, key=lambda x: abs(x[1]))
        d, m, k_n = best
        k[n] = k_n
        # print(f"  k[{n}] = {k_n} (d={d}, m={m})")

    return k


def main():
    print("="*70)
    print("LADDER GENERATOR: Analyzing d[n] and m[n] patterns")
    print("="*70)

    k = load_known_keys()
    print(f"\nLoaded {len(k)} known keys")
    print(f"Range: puzzle {min(k.keys())} to {max(k.keys())}")
    
    # Analyze all consecutive keys
    results = analyze_all_keys(k)
    
    # Count valid
    valid_count = sum(1 for n, (d, m, v) in results.items() if v)
    print(f"Recurrence verified: {valid_count}/{len(results)} ({100*valid_count/len(results):.1f}%)")
    
    # Show d[n] distribution
    d_counts = {}
    for n, (d, m, valid) in results.items():
        if d not in d_counts:
            d_counts[d] = 0
        d_counts[d] += 1
    
    print("\nd[n] value distribution:")
    for d, count in sorted(d_counts.items()):
        print(f"  d={d}: {count} times ({100*count/len(results):.1f}%)")
    
    # Show full sequence for n=2-70
    print("\n" + "="*70)
    print("d[n], m[n] SEQUENCE (n=2 to 70)")
    print("="*70)
    print("{:<5} {:>6} {:>25} {:>6}".format("n", "d[n]", "m[n]", "valid"))
    print("-" * 50)
    
    for n in sorted(results.keys()):
        if n > 70:
            break
        d, m, valid = results[n]
        check = "OK" if valid else "FAIL"
        print(f"{n:<5} {d:>6} {m:>25} {check:>6}")

    # Test forward generation
    print("\n" + "="*70)
    print("TESTING FORWARD GENERATION")
    print("="*70)
    
    # Bootstrap
    bootstrap = {1: 1, 2: 3, 3: 7}
    
    # Generate forward to n=70
    generated = forward_generate(bootstrap, 70)
    
    # Compare with actual
    matches = 0
    mismatches = []
    for n in range(1, 71):
        if n in k and n in generated:
            if generated[n] == k[n]:
                matches += 1
            else:
                mismatches.append((n, generated[n], k[n]))
    
    print(f"\nMatches: {matches}/70")
    if mismatches:
        print(f"Mismatches ({len(mismatches)}):")
        for n, gen, actual in mismatches[:10]:
            print(f"  n={n}: generated={gen}, actual={actual}")


if __name__ == "__main__":
    main()
