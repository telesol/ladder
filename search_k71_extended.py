#!/usr/bin/env python3
"""
Extended search for k[71] with realistic offset magnitudes.

Recent offsets are in the range -4e18 to -223e18 (trillions)
We need to search that space while respecting divisibility constraints.
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

def get_max_divisor_index(N, K, max_idx):
    """Find max i such that k[i] divides N."""
    d = 1
    for i in range(1, max_idx):
        if i in K and K[i] != 0 and N % K[i] == 0:
            d = i
    return d

def main():
    K = load_data()

    k68 = K[68]
    k70 = K[70]

    # k[71] range
    k71_min = 2**70
    k71_max = 2**71 - 1

    two_71 = 2**71

    # Recent offsets for reference
    print("Recent offsets:")
    for n in range(65, 71):
        offset = K[n] - 9 * K[n-3]
        print(f"  offset[{n}] = {offset:,}")

    # Estimate offset[71] from the pattern
    # The offsets seem to grow roughly 2x each step
    offset_70 = K[70] - 9 * K[67]
    offset_69 = K[69] - 9 * K[66]

    # Estimate: offset[71] ≈ 2 * offset[70] (rough guess)
    estimated_offset = 2 * offset_70

    print()
    print(f"Estimated offset[71] ≈ {estimated_offset:,}")
    print()

    # But the key constraint is: N_71 must be divisible by k[d] for some d > 1
    # N_71 = 2^71 - adj = 2^71 - (k[71] - 2*k[70])

    # For each target divisor d, find what k[71] would need to be
    print("=" * 80)
    print("For each d, finding k[71] values that give divisibility")
    print("AND have offset in the estimated range")
    print("=" * 80)

    base = 9 * k68
    offset_low = int(1.5 * offset_70)   # ~1.5x to 3x the previous offset
    offset_high = int(3.0 * offset_70)

    print(f"Searching offset range: [{offset_low:,}, {offset_high:,}]")
    print()

    best_candidates = []

    for d in range(2, 20):
        if d not in K:
            continue

        kd = K[d]

        # For N_71 to be divisible by k[d]:
        # 2^71 - adj ≡ 0 (mod k[d])
        # adj ≡ 2^71 (mod k[d])
        # k[71] - 2*k[70] ≡ 2^71 (mod k[d])
        # k[71] ≡ 2^71 + 2*k[70] (mod k[d])

        target_mod = (two_71 + 2*k70) % kd

        # k[71] = base + offset where offset is in [offset_low, offset_high]
        # We need (base + offset) ≡ target_mod (mod k[d])
        # offset ≡ target_mod - base (mod k[d])

        offset_mod = (target_mod - base) % kd

        # Find all offsets in our range that satisfy this modular constraint
        # offset = offset_mod + m*k[d] for integer m

        # Find the smallest m such that offset_mod + m*k[d] >= offset_low
        m_start = (offset_low - offset_mod) // kd
        if offset_mod + m_start * kd < offset_low:
            m_start += 1

        # Find the largest m such that offset_mod + m*k[d] <= offset_high
        m_end = (offset_high - offset_mod) // kd

        count = 0
        for m in range(m_start, m_end + 1):
            offset = offset_mod + m * kd
            if offset_low <= offset <= offset_high:
                k71 = base + offset
                if k71_min <= k71 <= k71_max:
                    adj = k71 - 2*k70
                    N = two_71 - adj

                    # Verify and find actual d
                    actual_d = get_max_divisor_index(N, K, 71)
                    m_val = N // K[actual_d]

                    best_candidates.append((actual_d, m_val, offset, k71))
                    count += 1

                    if count <= 2:
                        print(f"d={d:2d}: offset={offset:,}, k[71]={k71}")
                        print(f"       actual_d={actual_d}, m={m_val:,}")

        if count > 2:
            print(f"d={d:2d}: ... and {count-2} more candidates")

    print()
    print("=" * 80)
    print(f"TOTAL: {len(best_candidates)} candidates in estimated offset range")
    print("=" * 80)

    if best_candidates:
        # Sort by actual d (highest first)
        best_candidates.sort(key=lambda x: -x[0])

        print("\nTop 10 candidates by d:")
        for actual_d, m_val, offset, k71 in best_candidates[:10]:
            print(f"d={actual_d:2d}: m={m_val:,}")
            print(f"       offset={offset:,}")
            print(f"       k[71]={k71}")
            print()

if __name__ == "__main__":
    main()
