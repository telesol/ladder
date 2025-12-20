#!/usr/bin/env python3
"""
Systematic search for k[71] by finding offsets that give non-trivial d values.

Key insight: N_71 = 2^71 - adj[71] must be divisible by k[d] where d > 1
We can reverse the search: for each k[d], find what adj[71] would make N_71 divisible
"""

import sqlite3

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

def main():
    K = load_data()

    k68 = K[68]
    k70 = K[70]

    # k[71] range
    k71_min = 2**70
    k71_max = 2**71 - 1

    print("=" * 80)
    print("SYSTEMATIC SEARCH: Find offsets where k[d] | N_71")
    print("=" * 80)
    print()

    # For N_71 = 2^71 - adj to be divisible by k[d]:
    # 2^71 ≡ adj (mod k[d])
    # adj = k[71] - 2*k[70]
    # So we need: 2^71 ≡ k[71] - 2*k[70] (mod k[d])
    # k[71] ≡ 2^71 + 2*k[70] (mod k[d])

    two_71 = 2**71

    candidates = []

    print("For each d, finding k[71] values that make N_71 divisible by k[d]:")
    print("-" * 80)

    for d in range(2, 15):  # Check d from 2 to 14
        if d not in K:
            continue

        kd = K[d]

        # k[71] ≡ 2^71 + 2*k[70] (mod k[d])
        target_mod = (two_71 + 2*k70) % kd

        # k[71] = 9*k[68] + offset
        base = 9 * k68

        # Find offset such that base + offset ≡ target_mod (mod k[d])
        # offset ≡ target_mod - base (mod k[d])
        offset_mod = (target_mod - base) % kd

        # The smallest positive offset that works
        offset_candidate = offset_mod

        # But offset is likely negative based on pattern, so try negative versions
        # offset_candidate - kd, offset_candidate - 2*kd, etc.

        print(f"\nd={d}: k[{d}]={kd:,}")
        print(f"  Need k[71] ≡ {target_mod:,} (mod {kd:,})")
        print(f"  Base 9*k[68] = {base:,}")
        print(f"  Base mod k[{d}] = {base % kd:,}")
        print(f"  Required offset mod k[{d}] = {offset_mod:,}")

        # Generate candidate k[71] values
        k71_candidates = []

        # Try positive and negative offsets
        for mult in range(-1000, 1000):
            offset = offset_mod + mult * kd
            k71 = base + offset

            if k71_min <= k71 <= k71_max:
                k71_candidates.append((offset, k71))

        if k71_candidates:
            # Sort by absolute offset
            k71_candidates.sort(key=lambda x: abs(x[0]))

            print(f"  Found {len(k71_candidates)} valid k[71] values in range")
            print(f"  Smallest |offset|:")
            for offset, k71 in k71_candidates[:3]:
                adj = k71 - 2*k70
                N = two_71 - adj

                # Verify divisibility
                if N % kd == 0:
                    m = N // kd
                    candidates.append((d, m, offset, k71))
                    print(f"    offset={offset:,}: k[71]={k71:,}")
                    print(f"      m={m:,}, adj={adj:,}")
                else:
                    print(f"    ERROR: N_71 not divisible by k[{d}]!")

    print()
    print("=" * 80)
    print(f"FOUND {len(candidates)} CANDIDATE SOLUTIONS")
    print("=" * 80)

    if candidates:
        print("\nCandidates sorted by d (highest first):")
        candidates.sort(key=lambda x: -x[0])
        for d, m, offset, k71 in candidates[:10]:
            print(f"d={d:2d}: m={m:,}")
            print(f"       offset={offset:,}")
            print(f"       k[71]={k71}")
            print()

if __name__ == "__main__":
    main()
