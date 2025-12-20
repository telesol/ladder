#!/usr/bin/env python3
"""
Compute all offsets for n=10-70 using the mod-3 recursion.
offset[n] = k[n] - 9 * k[n-3]

Then factor each offset to find patterns.
"""

import sqlite3
from sympy import factorint

def load_k_sequence():
    """Load k-sequence from database."""
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
    K = load_k_sequence()

    print("=" * 80)
    print("OFFSET ANALYSIS: offset[n] = k[n] - 9 * k[n-3]")
    print("=" * 80)
    print()

    offsets = {}
    prime_counts = {}

    for n in range(10, 71):
        if n not in K or (n-3) not in K:
            continue

        offset = K[n] - 9 * K[n-3]
        offsets[n] = offset

        # Factor the absolute value
        abs_offset = abs(offset)
        if abs_offset > 0:
            factors = factorint(abs_offset)
        else:
            factors = {}

        # Track which primes appear
        for p in factors:
            prime_counts[p] = prime_counts.get(p, 0) + 1

        # Format factors
        if factors:
            factor_str = " × ".join([f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items())])
        else:
            factor_str = "0"

        sign = "-" if offset < 0 else "+"

        # Check for 17 or 19
        has_17 = 17 in factors
        has_19 = 19 in factors
        marker = ""
        if has_17 and has_19:
            marker = " [17,19]"
        elif has_17:
            marker = " [17]"
        elif has_19:
            marker = " [19]"

        print(f"n={n:2d}: offset = {sign}{abs_offset:>20,} = {sign}{factor_str}{marker}")

    print()
    print("=" * 80)
    print("PRIME FREQUENCY IN OFFSETS")
    print("=" * 80)

    for prime, count in sorted(prime_counts.items()):
        pct = 100 * count / len(offsets)
        print(f"  {prime:5d}: appears {count:2d} times ({pct:.1f}%)")

    print()
    print("=" * 80)
    print("17 vs 19 BY n mod 6")
    print("=" * 80)

    mod6_17 = {r: 0 for r in range(6)}
    mod6_19 = {r: 0 for r in range(6)}
    mod6_total = {r: 0 for r in range(6)}

    for n, offset in offsets.items():
        abs_offset = abs(offset)
        if abs_offset == 0:
            continue
        factors = factorint(abs_offset)
        r = n % 6
        mod6_total[r] += 1
        if 17 in factors:
            mod6_17[r] += 1
        if 19 in factors:
            mod6_19[r] += 1

    for r in range(6):
        if mod6_total[r] > 0:
            print(f"  n ≡ {r} (mod 6): 17 appears {mod6_17[r]}/{mod6_total[r]}, 19 appears {mod6_19[r]}/{mod6_total[r]}")

    print()
    print("=" * 80)
    print("SIGN PATTERN")
    print("=" * 80)

    sign_pattern = []
    for n in range(10, 71):
        if n in offsets:
            sign_pattern.append("+" if offsets[n] >= 0 else "-")

    print(f"Pattern: {''.join(sign_pattern)}")
    print(f"Length: {len(sign_pattern)}")

    # Check for repeating patterns
    for period in [3, 6, 9, 12]:
        matches = 0
        total = 0
        for i in range(period, len(sign_pattern)):
            if sign_pattern[i] == sign_pattern[i - period]:
                matches += 1
            total += 1
        if total > 0:
            print(f"Period {period}: {matches}/{total} = {100*matches/total:.1f}% match")

    # Save offsets to file
    print()
    print("Saving offsets to offsets_n10_n70.txt...")
    with open('/home/rkh/ladder/offsets_n10_n70.txt', 'w') as f:
        f.write("# Offsets for mod-3 recursion: offset[n] = k[n] - 9 * k[n-3]\n")
        f.write("# n, offset, factorization\n")
        for n in sorted(offsets.keys()):
            offset = offsets[n]
            abs_offset = abs(offset)
            if abs_offset > 0:
                factors = factorint(abs_offset)
                factor_str = " * ".join([f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items())])
            else:
                factor_str = "0"
            sign = "-" if offset < 0 else ""
            f.write(f"{n},{offset},{sign}{factor_str}\n")

    print("Done!")

if __name__ == "__main__":
    main()
