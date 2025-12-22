#!/usr/bin/env python3
"""
GAP PUZZLE DIRECT FORMULA ANALYSIS

CRITICAL INSIGHT: k[75], k[80], k[85], k[90] were generated WITHOUT k[71-74], k[76-79], etc.
This PROVES a direct formula k[n] = f(n) exists that doesn't require intermediate keys.

We analyze the 5 GAP keys to reverse-engineer the direct formula.
"""

import sqlite3
import math
from decimal import Decimal, getcontext
from fractions import Fraction

getcontext().prec = 100

# Database connection
DB_PATH = "/home/solo/LA/db/kh.db"

def get_keys(puzzle_ids):
    """Load keys from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    keys = {}
    for pid in puzzle_ids:
        cursor.execute("SELECT priv_hex FROM keys WHERE puzzle_id=?", (pid,))
        result = cursor.fetchone()
        if result:
            keys[pid] = int(result[0], 16)

    conn.close()
    return keys

def analyze_position_in_range(n, k):
    """Analyze where k sits in the range [2^(n-1), 2^n - 1]"""
    min_val = 2**(n-1)
    max_val = 2**n - 1
    range_size = max_val - min_val + 1
    offset = k - min_val
    position_pct = (offset / range_size) * 100

    print(f"\nn={n}:")
    print(f"  k[{n}] = {k}")
    print(f"  Range: [{min_val}, {max_val}]")
    print(f"  Offset from min: {offset}")
    print(f"  Position: {position_pct:.6f}%")
    print(f"  Binary: {bin(k)}")
    print(f"  Bit count: {k.bit_length()} bits")

    return {
        'n': n,
        'k': k,
        'min': min_val,
        'max': max_val,
        'offset': offset,
        'position_pct': position_pct,
        'range_size': range_size
    }

def test_alpha_formula(keys):
    """Test hypothesis: k[n] = floor(α × 2^n) for some constant α"""
    print("\n" + "="*80)
    print("HYPOTHESIS 1: k[n] = floor(α × 2^n)")
    print("="*80)

    alphas = {}
    for n, k in keys.items():
        alpha = Decimal(k) / Decimal(2**n)
        alphas[n] = alpha
        print(f"n={n}: α = k[{n}]/2^{n} = {alpha}")

    # Check if α is constant
    alpha_values = list(alphas.values())
    alpha_min = min(alpha_values)
    alpha_max = max(alpha_values)
    alpha_avg = sum(alpha_values) / len(alpha_values)

    print(f"\nα range: [{alpha_min}, {alpha_max}]")
    print(f"α average: {alpha_avg}")
    print(f"α variation: {alpha_max - alpha_min}")

    if alpha_max - alpha_min < 0.0001:
        print("✓ α appears CONSTANT - strong evidence for this formula!")
        return True, alpha_avg
    else:
        print("✗ α varies significantly - this formula doesn't fit")
        return False, None

def test_ratio_patterns(keys):
    """Test if k[5n]/k[n] follows a pattern"""
    print("\n" + "="*80)
    print("HYPOTHESIS 2: k[5n]/k[n] ratio analysis")
    print("="*80)

    # Get additional keys for ratio testing
    all_keys = get_keys(list(range(1, 20)) + [70, 75, 80, 85, 90])

    ratios = {}
    for n in [14, 15, 16, 17, 18]:
        if n in all_keys and 5*n in all_keys:
            ratio = Decimal(all_keys[5*n]) / Decimal(all_keys[n])
            ratios[n] = ratio
            print(f"k[{5*n}]/k[{n}] = {ratio}")

            # Expected ratio if purely exponential: 2^(5n)/2^n = 2^(4n)
            expected = Decimal(2**(4*n))
            actual_vs_expected = ratio / expected
            print(f"  Ratio/2^(4n) = {actual_vs_expected}")

    return ratios

def test_polynomial_mod(keys):
    """Test hypothesis: k[n] = polynomial(n) mod 2^n + 2^(n-1)"""
    print("\n" + "="*80)
    print("HYPOTHESIS 3: k[n] = poly(n) mod 2^n + 2^(n-1)")
    print("="*80)

    for n, k in keys.items():
        min_val = 2**(n-1)
        offset = k - min_val

        print(f"\nn={n}:")
        print(f"  offset = k[{n}] - 2^{n-1} = {offset}")
        print(f"  offset hex: {hex(offset)}")
        print(f"  offset / 2^{n-1} = {Decimal(offset) / Decimal(2**(n-1))}")

def test_gap_step_relationships(keys):
    """Test relationships between consecutive GAP keys"""
    print("\n" + "="*80)
    print("HYPOTHESIS 4: GAP step relationships (n+5 pattern)")
    print("="*80)

    gap_keys = sorted(keys.items())

    for i in range(len(gap_keys) - 1):
        n1, k1 = gap_keys[i]
        n2, k2 = gap_keys[i+1]

        print(f"\n{n1} → {n2} (step of {n2-n1}):")
        print(f"  k[{n2}]/k[{n1}] = {Decimal(k2)/Decimal(k1)}")
        print(f"  2^{n2}/2^{n1} = {2**(n2-n1)}")

        # Normalized ratio (remove exponential growth)
        normalized = (Decimal(k2)/Decimal(2**n2)) / (Decimal(k1)/Decimal(2**n1))
        print(f"  Normalized ratio: {normalized}")

def test_bit_patterns(keys):
    """Analyze bit patterns in the keys"""
    print("\n" + "="*80)
    print("BIT PATTERN ANALYSIS")
    print("="*80)

    for n, k in keys.items():
        binary = bin(k)[2:]

        print(f"\nn={n}: {binary}")
        print(f"  Length: {len(binary)} bits")
        print(f"  Ones: {binary.count('1')}")
        print(f"  Zeros: {binary.count('0')}")
        print(f"  Leading: {binary[:10]}...")
        print(f"  Trailing: ...{binary[-10:]}")

def test_hash_prng_fingerprints(keys):
    """Look for fingerprints of hash/PRNG generation"""
    print("\n" + "="*80)
    print("HASH/PRNG FINGERPRINT ANALYSIS")
    print("="*80)

    for n, k in keys.items():
        # Check byte distribution (random should be ~uniform)
        hex_str = hex(k)[2:].zfill((n+3)//4)
        byte_counts = {}

        for i in range(0, len(hex_str), 2):
            if i+1 < len(hex_str):
                byte_val = int(hex_str[i:i+2], 16)
                byte_counts[byte_val] = byte_counts.get(byte_val, 0) + 1

        print(f"\nn={n}:")
        print(f"  Unique bytes: {len(byte_counts)}/{len(hex_str)//2}")
        print(f"  Most common byte: {max(byte_counts.values())} occurrences")

        # Check for patterns in consecutive differences
        if n in [70, 75, 80, 85, 90]:
            # Convert to bytes and check entropy
            num_bytes = (k.bit_length() + 7) // 8
            print(f"  Byte length: {num_bytes}")

def test_mathematical_constants(keys):
    """Test if keys relate to mathematical constants"""
    print("\n" + "="*80)
    print("MATHEMATICAL CONSTANTS ANALYSIS")
    print("="*80)

    # Test against π, e, φ, √2, etc.
    constants = {
        'π': Decimal('3.14159265358979323846264338327950288419716939937510'),
        'e': Decimal('2.71828182845904523536028747135266249775724709369995'),
        'φ': Decimal('1.61803398874989484820458683436563811772030917980576'),
        '√2': Decimal('1.41421356237309504880168872420969807856967187537694'),
        'ln(2)': Decimal('0.69314718055994530941723212145817656807550013436025'),
    }

    for n, k in keys.items():
        alpha = Decimal(k) / Decimal(2**n)

        print(f"\nn={n}: α = {alpha}")

        for name, const in constants.items():
            if abs(alpha - const) < 0.1:
                print(f"  Close to {name}: diff = {abs(alpha - const)}")

def test_convergent_patterns(keys):
    """Test for convergent fraction patterns (from π/e/φ approximations)"""
    print("\n" + "="*80)
    print("CONVERGENT FRACTION ANALYSIS")
    print("="*80)

    for n, k in keys.items():
        min_val = 2**(n-1)
        offset = k - min_val

        # Try to express offset as a fraction
        frac = Fraction(offset).limit_denominator(10000)

        print(f"\nn={n}:")
        print(f"  offset ≈ {frac.numerator}/{frac.denominator}")

        # Check if denominator has special meaning
        if frac.denominator in [7, 22, 113, 355]:  # Known π convergents
            print(f"  !! Denominator {frac.denominator} is a π convergent!")

def main():
    print("="*80)
    print("GAP PUZZLE DIRECT FORMULA ANALYSIS")
    print("="*80)
    print("\nCRITICAL: These keys were generated WITHOUT intermediate values!")
    print("This PROVES a direct formula k[n] = f(n) exists.\n")

    # Load GAP keys
    gap_puzzles = [70, 75, 80, 85, 90]
    keys = get_keys(gap_puzzles)

    print(f"\nLoaded {len(keys)} GAP keys:")
    for n in sorted(keys.keys()):
        print(f"  k[{n}] = {keys[n]}")

    # Position analysis
    print("\n" + "="*80)
    print("POSITION IN RANGE ANALYSIS")
    print("="*80)

    positions = []
    for n in sorted(keys.keys()):
        pos_data = analyze_position_in_range(n, keys[n])
        positions.append(pos_data)

    # Test all hypotheses
    constant_alpha, alpha_value = test_alpha_formula(keys)
    test_ratio_patterns(keys)
    test_polynomial_mod(keys)
    test_gap_step_relationships(keys)
    test_bit_patterns(keys)
    test_hash_prng_fingerprints(keys)
    test_mathematical_constants(keys)
    test_convergent_patterns(keys)

    # SUMMARY
    print("\n" + "="*80)
    print("SUMMARY OF FINDINGS")
    print("="*80)

    if constant_alpha:
        print(f"\n✓ STRONG EVIDENCE: k[n] = floor({alpha_value} × 2^n)")
        print("\nNext steps:")
        print("1. Verify this formula against ALL 74 known keys")
        print("2. If verified, use it to derive ALL unsolved puzzles")
        print("3. Test if α relates to mathematical constants (π, e, φ)")
    else:
        print("\n✗ Simple α×2^n formula does NOT fit")
        print("The formula is more complex - continue investigating other hypotheses")

if __name__ == "__main__":
    main()
