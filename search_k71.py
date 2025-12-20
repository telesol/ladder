#!/usr/bin/env python3
"""
Search for k[71] using the verified mathematical constraints:

1. k[71] = 9 * k[68] + offset[71]  (mod-3 recursion)
2. adj[71] = k[71] - 2*k[70]
3. N_71 = 2^71 - adj[71]
4. d[71] = max{i : k[i] | N_71}  (VERIFIED)
5. m[71] = N_71 / k[d[71]]

Constraint: N_71 must be divisible by at least one k[i] for i < 71
"""

import json
import sqlite3
from math import gcd, isqrt

def load_data():
    conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
    cursor = conn.cursor()
    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
    rows = cursor.fetchall()
    conn.close()

    k_seq = {}
    for puzzle_id, hex_val in rows:
        k_seq[puzzle_id] = int(hex_val, 16)

    return k_seq

def get_divisor_index(N, K, max_idx):
    """Find max i such that k[i] divides N."""
    d = 1
    for i in range(1, max_idx):
        if i in K and K[i] != 0 and N % K[i] == 0:
            d = i
    return d

def analyze_offsets(K):
    """Analyze offset pattern from known data."""
    print("Offset Analysis for mod-3 recursion:")
    print("-" * 60)

    offsets = {}
    for n in range(13, 71):
        if n in K and (n-3) in K:
            offset = K[n] - 9 * K[n-3]
            offsets[n] = offset

            if n >= 65:  # Show recent offsets
                print(f"offset[{n}] = k[{n}] - 9*k[{n-3}] = {offset:,}")

    return offsets

def check_candidate(K, k71_candidate):
    """Check if k[71] candidate satisfies all constraints."""
    k70 = K[70]
    k68 = K[68]

    # Constraint 1: Compute adj
    adj_71 = k71_candidate - 2 * k70

    # Constraint 2: Compute N_71
    N_71 = (2**71) - adj_71

    # Constraint 3: Check divisibility
    d_71 = get_divisor_index(N_71, K, 71)

    if d_71 == 1 and K[1] == 1:
        # k[1]=1 always divides, check if there's a better divisor
        divisors = [(i, K[i]) for i in range(2, 71)
                    if i in K and K[i] != 0 and N_71 % K[i] == 0]
        if divisors:
            d_71 = max(d for d, _ in divisors)

    # Constraint 4: Compute m
    m_71 = N_71 // K[d_71] if K[d_71] != 0 else float('inf')

    # Constraint 5: Offset from mod-3
    offset_71 = k71_candidate - 9 * k68

    return {
        'k71': k71_candidate,
        'adj': adj_71,
        'N_71': N_71,
        'd': d_71,
        'm': m_71,
        'offset': offset_71,
        'valid': d_71 > 1  # Better than just k[1]=1
    }

def main():
    K = load_data()

    print("=" * 80)
    print("SEARCHING FOR k[71] USING VERIFIED CONSTRAINTS")
    print("=" * 80)
    print()

    print(f"Known values:")
    print(f"  k[68] = {K[68]:,}")
    print(f"  k[69] = {K[69]:,}")
    print(f"  k[70] = {K[70]:,}")
    print()

    # Analyze recent offsets to understand pattern
    offsets = analyze_offsets(K)
    print()

    # k[71] range: 2^70 to 2^71 - 1
    k71_min = 2**70
    k71_max = 2**71 - 1

    print(f"k[71] must be in range: [{k71_min:,}, {k71_max:,}]")
    print(f"That's a range of {k71_max - k71_min:,} values")
    print()

    # From mod-3: k[71] = 9 * k[68] + offset[71]
    k71_from_mod3 = 9 * K[68]
    print(f"From mod-3 base: 9 * k[68] = {k71_from_mod3:,}")

    # Recent offset range (look at last few)
    recent_offsets = [offsets[n] for n in range(65, 71) if n in offsets]
    offset_min = min(recent_offsets)
    offset_max = max(recent_offsets)
    print(f"Recent offset range: [{offset_min:,}, {offset_max:,}]")
    print()

    # Try a few offset values to see what we get
    print("Testing candidate k[71] values with various offsets:")
    print("-" * 80)

    test_offsets = [0, offset_min, offset_max,
                    offsets.get(68, 0), offsets.get(69, 0), offsets.get(70, 0)]

    for test_offset in sorted(set(test_offsets)):
        k71_test = k71_from_mod3 + test_offset

        # Check if in valid range
        if k71_min <= k71_test <= k71_max:
            result = check_candidate(K, k71_test)
            valid_mark = "✓" if result['valid'] else "✗"
            print(f"offset={test_offset:>15,}: k[71]={k71_test:,}")
            print(f"  d={result['d']}, m={result['m']:,}, adj={result['adj']:,} {valid_mark}")

    print()
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()
    print("To find k[71], we need to find an offset such that:")
    print("  1. k[71] = 9*k[68] + offset is in [2^70, 2^71)")
    print("  2. N_71 = 2^71 - (k[71] - 2*k[70]) has a non-trivial divisor from k[1..70]")
    print()
    print("The search space is constrained by the offset pattern.")
    print("Next step: Analyze what values of offset[71] make N_71 divisible by larger k[i].")

if __name__ == "__main__":
    main()
