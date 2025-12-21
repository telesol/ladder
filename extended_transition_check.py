#!/usr/bin/env python3
"""
Extended transition check - look for additional phase transitions
Check: n=33 (2^5 + 1), n=65 (2^6 + 1, Fermat F_3)
"""

import json
from sympy import factorint

# Extended k values
k_extended = {
    1: 0x1,
    2: 0x3,
    3: 0x7,
    4: 0x8,
    5: 0x15,
    6: 0x31,
    7: 0x4c,
    8: 0xe0,
    9: 0x1d3,
    10: 0x202,
    11: 0x483,
    12: 0xa7b,
    13: 0x1460,
    14: 0x2930,
    15: 0x68f3,
    16: 0xc936,
    17: 0x1764f,
    18: 0x3080d,
    19: 0x5749f,
    20: 0xd2c55,
    25: 0x1fa5ee5,
    30: 0x3d94cd64,
    33: 0x1a96ca8d8,
    35: 0x4aed21170,
    40: 0xe9ae4933d6,
    50: 0x22bd43c2e9354,
    65: 0x1a838b13505b26867,
    70: 0x349b84b6431a6c4ef1,
}

# Load m and d sequences
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)
    m_seq = data['m_seq']
    d_seq = data['d_seq']

def compute_adj(n):
    """Compute adj[n] = k[n] - 2*k[n-1]"""
    if n-1 not in k_extended:
        return None
    return k_extended[n] - 2 * k_extended[n-1]

def check_fermat_related():
    """Check Fermat and Fermat-related numbers"""
    fermat_candidates = [
        (3, "2^1 + 1", "Fermat F_0"),
        (5, "2^2 + 1", "Fermat F_1"),
        (17, "2^4 + 1", "Fermat F_2"),
        (33, "2^5 + 1", "NOT Fermat (2^(2^k)+1 form)"),
        (65, "2^6 + 1", "NOT Fermat (2^(2^k)+1 form)"),
        (257, "2^8 + 1", "Fermat F_3"),
    ]

    print("FERMAT AND FERMAT-RELATED NUMBERS")
    print("=" * 80)
    for n, formula, classification in fermat_candidates:
        if n in k_extended:
            k_val = k_extended[n]
            factors = factorint(k_val)
            factor_str = " × ".join(
                f"{p}^{e}" if e > 1 else str(p)
                for p, e in sorted(factors.items())
            )

            # Check for special structure
            has_high_powers = any(exp >= 3 for exp in factors.values())

            print(f"\nn = {n} = {formula} ({classification})")
            print(f"  k[{n}] = {k_val}")
            print(f"  Factorization: {factor_str}")
            print(f"  Distinct primes: {len(factors)}")
            print(f"  Has high powers (≥3): {has_high_powers}")

            adj = compute_adj(n)
            if adj is not None:
                print(f"  adj[{n}] = {adj:+d}")

            # Check if contains n as factor
            if n in factors:
                print(f"  ⚠️  Contains {n} as factor!")

def check_power_of_2_thresholds():
    """Check when k[n] crosses powers of 2"""
    thresholds = [
        (16, 2**16),
        (24, 2**24),
        (32, 2**32),
        (40, 2**40),
        (48, 2**48),
        (64, 2**64),
    ]

    print("\n" + "=" * 80)
    print("POWER OF 2 THRESHOLD CROSSINGS")
    print("=" * 80)

    for bit_size, threshold in thresholds:
        print(f"\n2^{bit_size} = {threshold}")

        # Find first n where k[n] > threshold
        first_above = None
        for n in sorted(k_extended.keys()):
            if k_extended[n] > threshold:
                first_above = n
                break

        if first_above:
            print(f"  First k[n] > 2^{bit_size}: n={first_above}")
            print(f"    k[{first_above}] = {k_extended[first_above]}")

            # Check if special
            if first_above in [3, 5, 17, 33, 65, 257]:
                print(f"    ⚠️  n={first_above} is Fermat-related!")

def check_sign_pattern_extended():
    """Check sign pattern for extended range"""
    print("\n" + "=" * 80)
    print("EXTENDED SIGN PATTERN CHECK")
    print("=" * 80)

    # Get all n values where we have consecutive k values
    valid_n = []
    for n in sorted(k_extended.keys()):
        if n-1 in k_extended and n >= 2:
            valid_n.append(n)

    print(f"\nChecking {len(valid_n)} values with consecutive k[n-1], k[n]")
    print()

    # Expected ++- pattern
    pattern_matches = []
    for n in valid_n:
        adj = compute_adj(n)
        sign = '+' if adj > 0 else '-'

        idx = (n - 2) % 3
        expected_sign = ['+', '+', '-'][idx]

        match = (sign == expected_sign)
        pattern_matches.append((n, sign, expected_sign, match, adj))

    # Print results
    for n, sign, expected, match, adj in pattern_matches:
        match_str = "✓" if match else "✗"
        print(f"n={n:2d}: exp={expected}, act={sign}, {match_str}, adj={adj:+15d}")

    # Count breaks
    total = len(pattern_matches)
    matches = sum(1 for _, _, _, m, _ in pattern_matches if m)
    breaks = total - matches

    print(f"\nTotal: {total}, Matches: {matches}, Breaks: {breaks}")
    print(f"Match rate: {matches/total*100:.1f}%")

    # Find consecutive match sequences
    consecutive = 0
    max_consecutive = 0
    sequences = []
    seq_start = None

    for n, sign, expected, match, adj in pattern_matches:
        if match:
            if consecutive == 0:
                seq_start = n
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            if consecutive > 0:
                sequences.append((seq_start, n-1, consecutive))
            consecutive = 0

    if consecutive > 0:
        sequences.append((seq_start, pattern_matches[-1][0], consecutive))

    print(f"\nLongest consecutive match sequence: {max_consecutive}")
    print("\nAll match sequences (≥3):")
    for start, end, length in sequences:
        if length >= 3:
            print(f"  n={start} to n={end}: {length} consecutive matches")

def check_d_pattern_extended():
    """Check d[n] pattern in extended range"""
    print("\n" + "=" * 80)
    print("D[N] PATTERN IN EXTENDED RANGE")
    print("=" * 80)

    valid_n = [n for n in sorted(k_extended.keys()) if n >= 4 and n <= 70]

    d_values = []
    for n in valid_n:
        if n-2 < len(d_seq):
            d_val = d_seq[n-2]
            d_values.append((n, d_val))

    # Group by d value
    from collections import Counter
    d_counter = Counter(d for n, d in d_values)

    print("\nD-value distribution:")
    for d, count in sorted(d_counter.items()):
        percentage = count / len(d_values) * 100
        print(f"  d={d}: {count} occurrences ({percentage:.1f}%)")

    # Check d=1 dominance after n=17
    before_17 = [(n, d) for n, d in d_values if n < 17]
    at_after_17 = [(n, d) for n, d in d_values if n >= 17]

    d1_before = sum(1 for n, d in before_17 if d == 1)
    d1_after = sum(1 for n, d in at_after_17 if d == 1)

    print(f"\nBefore n=17: d=1 in {d1_before}/{len(before_17)} = {d1_before/len(before_17)*100:.1f}%")
    print(f"At/After n=17: d=1 in {d1_after}/{len(at_after_17)} = {d1_after/len(at_after_17)*100:.1f}%")

def main():
    check_fermat_related()
    check_power_of_2_thresholds()
    check_sign_pattern_extended()
    check_d_pattern_extended()

if __name__ == '__main__':
    main()
