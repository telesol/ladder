#!/usr/bin/env python3
"""
Smart search for k[71] with offset constraints.

Key insight: offset[n] pattern shows roughly 2x growth per step
offset[68] = -55e18, offset[69] = -120e18, offset[70] = -223e18

Estimate offset[71] in range [-300e18, -600e18] based on trend
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
    base = 9 * k68

    # Recent offsets
    offset_68 = K[68] - 9 * K[65]
    offset_69 = K[69] - 9 * K[66]
    offset_70 = K[70] - 9 * K[67]

    print("Recent offsets (quintillions):")
    print(f"  offset[68] = {offset_68 / 1e18:.1f} × 10^18")
    print(f"  offset[69] = {offset_69 / 1e18:.1f} × 10^18")
    print(f"  offset[70] = {offset_70 / 1e18:.1f} × 10^18")
    print()

    # Pattern: offsets roughly double each step
    # Let's search a wide range around the expected pattern
    ratio_69_68 = offset_69 / offset_68  # ~2.17
    ratio_70_69 = offset_70 / offset_69  # ~1.86

    avg_ratio = (ratio_69_68 + ratio_70_69) / 2
    print(f"Growth ratios: {ratio_69_68:.2f}, {ratio_70_69:.2f}")
    print(f"Average ratio: {avg_ratio:.2f}")
    print()

    # Estimate offset[71] range (offset is negative!)
    offset_estimate = offset_70 * avg_ratio
    # Note: more negative = 3.0x, less negative = 1.5x
    offset_more_neg = int(offset_70 * 3.0)  # More negative bound
    offset_less_neg = int(offset_70 * 1.5)  # Less negative bound

    print(f"Offset[71] estimate: {offset_estimate / 1e18:.1f} × 10^18")
    print(f"Search range: [{offset_more_neg / 1e18:.1f}, {offset_less_neg / 1e18:.1f}] × 10^18")
    print()

    # Valid k[71] range constraint
    valid_offset_min = k71_min - base
    valid_offset_max = k71_max - base

    print(f"Valid offset range for k[71] in [2^70, 2^71):")
    print(f"  [{valid_offset_min / 1e18:.1f}, {valid_offset_max / 1e18:.1f}] × 10^18")
    print()

    # Actual search range is intersection (correctly handling negatives)
    search_low = max(offset_more_neg, valid_offset_min)
    search_high = min(offset_less_neg, valid_offset_max)

    if search_low > search_high:
        print("ERROR: No valid search range exists!")
        print(f"  search_low = {search_low / 1e18:.1f} × 10^18")
        print(f"  search_high = {search_high / 1e18:.1f} × 10^18")
        return

    print(f"Actual search range: [{search_low / 1e18:.1f}, {search_high / 1e18:.1f}] × 10^18")
    print()

    # For each target divisor, find candidates
    print("=" * 80)
    print("Finding candidates with higher d values")
    print("=" * 80)

    candidates = []

    # Focus on higher d values (more constraining)
    for d in range(5, 30):
        if d not in K:
            continue

        kd = K[d]
        target_mod = (two_71 + 2*k70) % kd
        offset_mod = (target_mod - base) % kd

        # Find offsets in search range
        m_start = (search_low - offset_mod) // kd
        if offset_mod + m_start * kd < search_low:
            m_start += 1

        m_end = (search_high - offset_mod) // kd

        for m in range(m_start, m_end + 1):
            offset = offset_mod + m * kd
            if search_low <= offset <= search_high:
                k71 = base + offset
                if k71_min <= k71 <= k71_max:
                    adj = k71 - 2*k70
                    N = two_71 - adj

                    # Verify divisibility and find actual d
                    actual_d = get_max_divisor_index(N, K, 71)
                    m_val = N // K[actual_d]

                    candidates.append((actual_d, m_val, offset, k71))

    print(f"\nFound {len(candidates)} candidates")

    if candidates:
        # Remove duplicates and sort by d
        unique = {}
        for c in candidates:
            k = c[3]  # k71 value
            if k not in unique or c[0] > unique[k][0]:
                unique[k] = c

        candidates = list(unique.values())
        candidates.sort(key=lambda x: (-x[0], abs(x[2] - offset_estimate)))

        print("\nTop candidates (by highest d, then closest to expected offset):")
        for actual_d, m_val, offset, k71 in candidates[:15]:
            ratio = offset / offset_70
            print(f"d={actual_d:2d}: offset={offset/1e18:.1f}×10^18 (ratio={ratio:.2f})")
            print(f"       m={m_val:,}")
            print(f"       k[71]={k71}")
            print()

if __name__ == "__main__":
    main()
