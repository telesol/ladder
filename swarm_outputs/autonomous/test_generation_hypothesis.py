#!/usr/bin/env python3
"""
Test: Was k[n] generated algorithmically (PRNG, hash, etc.) rather than by formula?

The puzzle creator in 2015 needed to generate 160 keys.
The recurrence relation might be a PROPERTY we discovered, not the generation method.

Tests:
1. Check if k[n] mod (2^32-1) or mod (2^64-1) shows any pattern (PRNG indicators)
2. Check if consecutive k differences follow PRNG patterns
3. Check if k[n] has structure in binary representation
4. Test if there's a common mathematical constant involved
"""

import sqlite3
from math import gcd, log, sqrt, pi, e

DB_PATH = "/home/rkh/ladder/db/kh.db"

def load_k_values():
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
        if priv_hex.startswith('0x'):
            k[puzzle_id] = int(priv_hex, 16)
        else:
            k[puzzle_id] = int(priv_hex, 16)
    return k

def analyze_binary_patterns(k):
    """Check for patterns in binary representation"""
    print("=== Binary Pattern Analysis ===\n")

    for n in range(1, min(21, max(k.keys()) + 1)):
        if n not in k:
            continue

        val = k[n]
        bits = bin(val)[2:]
        hamming = bits.count('1')
        bit_len = len(bits)
        density = hamming / bit_len

        # Check for runs of 1s or 0s
        max_run_1 = max([len(s) for s in bits.split('0')], default=0)
        max_run_0 = max([len(s) for s in bits.split('1')], default=0)

        print(f"k[{n:>2}] = {val:>12} = 0b{bits[:30]}{'...' if len(bits)>30 else ''}")
        print(f"       bits={bit_len:>2}, hamming={hamming:>2}, density={density:.3f}, max_run_1={max_run_1}, max_run_0={max_run_0}")

def test_lcg_detection(k):
    """Test if k values could come from an LCG (Linear Congruential Generator)"""
    print("\n=== LCG Detection ===")
    print("Testing if k[n+1] = (a*k[n] + c) mod m for some a,c,m\n")

    # Try common LCG moduli
    moduli = [2**31, 2**32, 2**31 - 1, 2**32 - 5]

    for mod in moduli:
        print(f"Testing mod = {mod}:")
        # For consecutive k values, check if there's a consistent multiplier
        for n in range(1, min(10, max(k.keys()))):
            if n in k and (n+1) in k:
                k1 = k[n] % mod
                k2 = k[n+1] % mod
                if k1 != 0:
                    # If k2 = a*k1 + c (mod m), then a = (k2 - c) / k1
                    # Try c = 0 first
                    a_approx = k2 * pow(k1, -1, mod) % mod if gcd(k1, mod) == 1 else None
                    if a_approx:
                        print(f"  k[{n+1}] / k[{n}] mod {mod} = {a_approx}")

def test_mathematical_constants(k):
    """Check if k values relate to mathematical constants"""
    print("\n=== Mathematical Constants ===\n")

    # Ratios between consecutive k values
    print("Ratios k[n+1]/k[n]:")
    for n in range(1, min(20, max(k.keys()))):
        if n in k and (n+1) in k:
            ratio = k[n+1] / k[n]
            # Compare to constants
            diff_e = abs(ratio - e)
            diff_pi = abs(ratio - pi)
            diff_phi = abs(ratio - (1 + sqrt(5))/2)
            diff_2 = abs(ratio - 2)
            diff_sqrt2 = abs(ratio - sqrt(2))

            closest = min([('e', diff_e), ('π', diff_pi), ('φ', diff_phi), ('2', diff_2), ('√2', diff_sqrt2)], key=lambda x: x[1])
            print(f"  k[{n+1}]/k[{n}] = {ratio:.6f} (closest: {closest[0]}, diff={closest[1]:.4f})")

def test_gcd_structure(k):
    """Analyze GCD structure between k values"""
    print("\n=== GCD Structure ===\n")

    for n in range(2, min(20, max(k.keys()))):
        if n not in k:
            continue

        # Find GCDs with all previous k values
        gcds = []
        for m in range(1, n):
            if m in k:
                g = gcd(k[n], k[m])
                if g > 1:
                    gcds.append((m, g))

        if gcds:
            print(f"k[{n}] = {k[n]}: gcd with {gcds}")
        else:
            print(f"k[{n}] = {k[n]}: coprime with all previous")

def test_difference_patterns(k):
    """Analyze difference patterns"""
    print("\n=== Difference Patterns ===\n")

    # First differences
    diffs = []
    for n in range(2, min(30, max(k.keys()))):
        if n in k and (n-1) in k:
            d = k[n] - k[n-1]
            diffs.append((n, d))

    print("First differences k[n] - k[n-1]:")
    for n, d in diffs[:15]:
        print(f"  k[{n}] - k[{n-1}] = {d}")

    # Second differences
    print("\nSecond differences:")
    for i in range(len(diffs)-1):
        n1, d1 = diffs[i]
        n2, d2 = diffs[i+1]
        dd = d2 - d1
        print(f"  Δ²k[{n2}] = {dd}")
        if i >= 10:
            break

def test_power_of_2_proximity(k):
    """Check how close k[n] is to 2^(n-1)"""
    print("\n=== Proximity to 2^(n-1) ===\n")

    for n in range(1, min(25, max(k.keys()) + 1)):
        if n not in k:
            continue

        target = 2**(n-1)
        ratio = k[n] / target
        offset = k[n] - target
        pct = 100 * offset / target

        print(f"k[{n:>2}] / 2^{n-1:>2} = {ratio:.6f}  (offset = {pct:+.2f}%)")

def main():
    k = load_k_values()
    print(f"Loaded {len(k)} k values\n")

    analyze_binary_patterns(k)
    test_mathematical_constants(k)
    test_gcd_structure(k)
    test_difference_patterns(k)
    test_power_of_2_proximity(k)
    # test_lcg_detection(k)  # Too slow for large moduli

if __name__ == "__main__":
    main()
