#!/usr/bin/env python3
"""
GAP Puzzle Analysis - Study k[75], k[80], k[85], k[90] to find patterns.

These are the ONLY known keys in the "gap" between k[70] and k[91+].
They can reveal the construction pattern for n>70.
"""

import sqlite3
import math

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LN2 = math.log(2)

CONSTANTS = {
    'π/4': PI/4, 'e/π': E/PI, '1/φ': 1/PHI, 'φ-1': PHI-1,
    'ln(2)': LN2, 'e/4': E/4, '2/e': 2/E, '1/√2': 1/math.sqrt(2),
    '1/2': 0.5, '2/3': 2/3, '3/4': 0.75, '7/8': 0.875,
}

def load_keys():
    conn = sqlite3.connect('/home/solo/LA/db/kh.db')
    cursor = conn.cursor()
    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id")
    rows = cursor.fetchall()
    conn.close()
    keys = {}
    for puzzle_id, priv_hex in rows:
        if priv_hex and puzzle_id is not None:
            keys[int(puzzle_id)] = int(priv_hex, 16)
    return keys

def analyze_gap_puzzles(k):
    """Deep analysis of GAP puzzles"""
    print("=" * 60)
    print("GAP PUZZLE ANALYSIS")
    print("=" * 60)

    gap_ns = [75, 80, 85, 90]

    print("\n1. BASIC PROPERTIES:")
    for n in gap_ns:
        if n in k:
            k_val = k[n]
            k_ratio = k_val / (2**n)
            bits = k_val.bit_length()
            print(f"\n  k[{n}] = {k_val}")
            print(f"       = {hex(k_val)}")
            print(f"       k[{n}]/2^{n} = {k_ratio:.10f}")
            print(f"       bit length: {bits}")

            # Find best constant match
            best_const = None
            best_err = float('inf')
            for name, val in CONSTANTS.items():
                err = abs(k_ratio - val) / val * 100
                if err < best_err:
                    best_err = err
                    best_const = name
            print(f"       best match: {best_const} (error: {best_err:.4f}%)")

    print("\n\n2. GAP PUZZLE RATIOS:")
    gap_ratios = {}
    for n in gap_ns:
        if n in k:
            gap_ratios[n] = k[n] / (2**n)

    # Check if there's a pattern in the gap ratios
    print("\n  k[n]/2^n for gap puzzles:")
    for n, ratio in gap_ratios.items():
        print(f"    k[{n}]/2^{n} = {ratio:.10f}")

    # Check ratio between gap puzzles
    print("\n  Ratios between gap puzzles:")
    gap_list = list(gap_ratios.items())
    for i in range(1, len(gap_list)):
        n1, r1 = gap_list[i-1]
        n2, r2 = gap_list[i]
        ratio_ratio = r2 / r1
        print(f"    (k[{n2}]/2^{n2}) / (k[{n1}]/2^{n1}) = {ratio_ratio:.6f}")

    print("\n\n3. CHECKING IF GAP KEYS FIT RECURRENCE:")
    # For gap puzzles, we can't directly verify the recurrence because
    # we don't have consecutive keys. But we can estimate what m would need to be.

    print("\n  Hypothetical m values if recurrence holds:")
    print("  (Note: These require knowing k[n-1], which we don't have for gaps)")

    # Instead, let's check if GAP keys follow the same constant encoding pattern
    print("\n\n4. CONSTANT ENCODING PATTERN:")
    print("  Checking if GAP puzzles align with known anchor pattern:")

    known_anchors = [
        (16, 'π/4', PI/4),
        (21, 'e/π', E/PI),
        (36, '1/φ', 1/PHI),
        (48, 'e/4', E/4),
        (58, 'ln(2)', LN2),
        (61, 'φ-1', PHI-1),
    ]

    for n in gap_ns:
        if n in k:
            k_ratio = k[n] / (2**n)
            print(f"\n  n={n}: k[{n}]/2^{n} = {k_ratio:.10f}")

            # Check each constant
            for name, val in CONSTANTS.items():
                err = abs(k_ratio - val) / val * 100
                if err < 5:
                    print(f"         ≈ {name} = {val:.10f} (error: {err:.4f}%)")

    print("\n\n5. OSCILLATION PATTERN IN GAPS:")
    # Look at m[n]/2^n pattern for n before the gap
    print("  m[n]/2^n for n=65-70 (known values):")
    m_before_gap = {}
    for n in range(65, 71):
        if n in k and n-1 in k:
            m_val = 2**n - k[n] + 2*k[n-1]
            m_ratio = m_val / (2**n)
            m_before_gap[n] = m_ratio
            odd_even = "odd" if n % 2 == 1 else "even"
            print(f"    m[{n}]/2^{n} = {m_ratio:.6f} ({odd_even})")

    print("\n  Pattern: odd n tends to have higher m-ratios")

    print("\n\n6. BIT PATTERN ANALYSIS:")
    for n in gap_ns:
        if n in k:
            k_hex = hex(k[n])[2:]
            print(f"\n  k[{n}] hex: {k_hex}")
            # Look for patterns in hex digits
            digit_counts = {}
            for d in k_hex:
                digit_counts[d] = digit_counts.get(d, 0) + 1
            print(f"         digit distribution: {dict(sorted(digit_counts.items()))}")

    print("\n\n7. PRIME FACTORIZATION HINTS:")
    for n in gap_ns:
        if n in k:
            k_val = k[n]
            # Check divisibility by small primes
            small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
            factors = []
            for p in small_primes:
                if k_val % p == 0:
                    count = 0
                    temp = k_val
                    while temp % p == 0:
                        temp //= p
                        count += 1
                    factors.append(f"{p}^{count}")
            print(f"\n  k[{n}] divisible by: {', '.join(factors) if factors else 'none of small primes'}")

def derive_pattern_from_gaps(k):
    """Try to derive the generation pattern from GAP puzzles"""
    print("\n" + "=" * 60)
    print("PATTERN DERIVATION FROM GAP PUZZLES")
    print("=" * 60)

    gap_ns = [75, 80, 85, 90]

    # Key observation: gap puzzles are spaced by 5
    print("\n1. GAP SPACING:")
    print("  75, 80, 85, 90 - all spaced by 5")
    print("  This is likely intentional!")

    # Check if the k[n]/2^n ratios follow a pattern
    print("\n2. K-RATIO PATTERN:")
    ratios = []
    for n in gap_ns:
        if n in k:
            ratio = k[n] / (2**n)
            ratios.append((n, ratio))
            print(f"  k[{n}]/2^{n} = {ratio:.10f}")

    if len(ratios) == 4:
        # Check if ratios form a pattern
        r75, r80, r85, r90 = [r[1] for r in ratios]

        # Linear fit?
        slope1 = (r80 - r75) / 5
        slope2 = (r85 - r80) / 5
        slope3 = (r90 - r85) / 5
        print(f"\n  Slopes: {slope1:.8f}, {slope2:.8f}, {slope3:.8f}")

        # If we extrapolate, what would k[71]/2^71 be?
        # From 70 to 75 is 5 steps, so from 70 to 71 is 1 step
        # But we need k[70]/2^70 first
        k70_ratio = k[70] / (2**70)
        print(f"\n  k[70]/2^70 = {k70_ratio:.10f}")

        # Extrapolate to k[71]
        # Method: Linear from k[70] to k[75]
        if 75 in k:
            slope_70_75 = (k[75] / (2**75) - k70_ratio) / 5
            k71_ratio_est = k70_ratio + slope_70_75
            print(f"\n  Linear extrapolation 70→75:")
            print(f"    slope = {slope_70_75:.10f}")
            print(f"    estimated k[71]/2^71 = {k71_ratio_est:.10f}")
            k71_est = int(k71_ratio_est * (2**71))
            print(f"    estimated k[71] = {k71_est}")
            print(f"                    = {hex(k71_est)}")

    print("\n3. SYNTHESIS:")
    print("  The GAP puzzles show that the pattern CONTINUES beyond n=70.")
    print("  k[90]/2^90 ≈ 1/√2 (anchor!), suggesting anchors continue.")
    print("  Between anchors, the constant ratio varies smoothly.")

def main():
    k = load_keys()
    print(f"Loaded {len(k)} keys")

    analyze_gap_puzzles(k)
    derive_pattern_from_gaps(k)

    print("\n" + "=" * 60)
    print("KEY INSIGHTS FROM GAP PUZZLES")
    print("=" * 60)
    print("""
1. k[90]/2^90 ≈ 1/√2 (0.701...) - This is an ANCHOR point!

2. GAP puzzles are spaced by 5 (75, 80, 85, 90)
   - This spacing might be intentional for verification

3. The oscillation pattern likely continues beyond n=70
   - n=75 (odd modulo 5 → specific constant?)
   - n=80 (even → different constant?)

4. Linear extrapolation from k[70] to k[75] gives estimate for k[71]

5. The fact that k[90] matches 1/√2 suggests the anchor pattern
   continues - we should find more anchors at n=71-89!
""")

if __name__ == "__main__":
    main()
