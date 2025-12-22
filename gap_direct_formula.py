#!/usr/bin/env python3
"""
DIRECT FORMULA ANALYSIS

CRITICAL INSIGHT: The GAP puzzles PROVE a direct formula exists.
Since k[75] exists without k[71-74], the formula CANNOT be recursive.

Let's analyze the mathematical structure more deeply.
"""

import sqlite3
from decimal import Decimal, getcontext
from fractions import Fraction
import math

getcontext().prec = 150

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

def analyze_normalized_values(keys):
    """
    Analyze k[n] / 2^(n-1) - this removes the exponential growth
    and reveals the underlying pattern
    """
    print("="*80)
    print("NORMALIZED VALUE ANALYSIS: k[n] / 2^(n-1)")
    print("="*80)
    print("\nIf k[n] = f(n) × 2^(n-1), then k[n]/2^(n-1) = f(n)")
    print("This f(n) should be in range [1, 2) for valid keys\n")

    f_values = {}
    for n in sorted(keys.keys()):
        k = keys[n]
        min_val = 2**(n-1)
        f_n = Decimal(k) / Decimal(min_val)
        f_values[n] = f_n

        print(f"n={n:3d}: f({n}) = {f_n}")

    return f_values

def test_f_as_continued_fraction(f_values):
    """
    Test if f(n) can be expressed as continued fractions
    Known: m[4]/m[3] = 22/7 ≈ π, suggesting convergent patterns
    """
    print("\n" + "="*80)
    print("CONTINUED FRACTION ANALYSIS")
    print("="*80)

    for n, f_n in sorted(f_values.items())[:20]:  # First 20
        # Convert to rational approximation
        frac = Fraction(float(f_n)).limit_denominator(10000)

        print(f"\nn={n}: f({n}) ≈ {frac.numerator}/{frac.denominator}")

        # Check if numerator or denominator has special meaning
        num = frac.numerator
        den = frac.denominator

        # Known convergent denominators
        pi_convergents = [1, 7, 106, 113, 33102, 33215, 355, 103993]
        e_convergents = [1, 2, 3, 4, 7, 11, 18, 39, 71]
        phi_convergents = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]  # Fibonacci

        if den in pi_convergents:
            print(f"  !! Denominator {den} is a π convergent!")
        if den in e_convergents:
            print(f"  !! Denominator {den} is an e convergent!")
        if den in phi_convergents:
            print(f"  !! Denominator {den} is a φ convergent (Fibonacci)!")

def analyze_offset_ratios(keys):
    """
    Analyze ratios between offsets for different n values
    offset[n] = k[n] - 2^(n-1)
    """
    print("\n" + "="*80)
    print("OFFSET RATIO ANALYSIS")
    print("="*80)

    offsets = {}
    for n, k in keys.items():
        offsets[n] = k - 2**(n-1)

    # Check specific ratio patterns
    test_pairs = [
        (70, 14),  # 5x multiplier
        (75, 15),  # 5x multiplier
        (80, 16),  # 5x multiplier
        (85, 17),  # 5x multiplier
        (90, 18),  # 5x multiplier
    ]

    print("\nTesting 5x multiplier pattern (n vs 5n):")
    for n1, n2 in test_pairs:
        if n1 in offsets and n2 in offsets:
            ratio = Decimal(offsets[n1]) / Decimal(offsets[n2])
            print(f"\noffset[{n1}] / offset[{n2}] = {ratio}")

            # Expected if formula is offset[n] = g(n) × 2^(n-1)
            expected_power = Decimal(2**(n1 - n2))
            print(f"  2^({n1}-{n2}) = {expected_power}")
            print(f"  Ratio / 2^({n1}-{n2}) = {ratio / expected_power}")

def test_modular_arithmetic(keys):
    """
    Test if keys follow modular arithmetic patterns
    e.g., k[n] ≡ f(n) (mod m) for some modulus m
    """
    print("\n" + "="*80)
    print("MODULAR ARITHMETIC ANALYSIS")
    print("="*80)

    # Test small moduli
    test_moduli = [7, 22, 113, 355, 2015, 65537]

    for mod in test_moduli:
        print(f"\nTesting modulus {mod}:")

        residues = {}
        for n in sorted(keys.keys())[:20]:  # First 20 keys
            k = keys[n]
            residues[n] = k % mod

        # Check if residues follow a pattern
        residue_values = list(residues.values())

        # Count unique residues
        unique = len(set(residue_values))
        print(f"  Unique residues: {unique}/{len(residues)}")

        # Show first few
        for n in sorted(list(residues.keys())[:10]):
            print(f"    k[{n}] mod {mod} = {residues[n]}")

def test_polynomial_fit(f_values):
    """
    Test if f(n) can be approximated by a polynomial
    """
    print("\n" + "="*80)
    print("POLYNOMIAL FIT ANALYSIS")
    print("="*80)

    import numpy as np
    from numpy.polynomial import polynomial as P

    # Convert to numpy arrays
    n_vals = np.array([n for n in sorted(f_values.keys())])
    f_vals = np.array([float(f_values[n]) for n in sorted(f_values.keys())])

    # Try polynomial fits of various degrees
    for degree in [1, 2, 3, 4, 5]:
        # Fit polynomial
        coeffs = P.polyfit(n_vals, f_vals, degree)

        # Calculate R²
        f_pred = P.polyval(n_vals, coeffs)
        ss_tot = np.sum((f_vals - np.mean(f_vals))**2)
        ss_res = np.sum((f_vals - f_pred)**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        print(f"\nDegree {degree} polynomial:")
        print(f"  R² = {r_squared:.6f}")

        if r_squared > 0.5:
            print(f"  Coefficients: {coeffs}")

def test_trigonometric_patterns(f_values):
    """
    Test if f(n) follows trigonometric patterns
    sin, cos, or combinations
    """
    print("\n" + "="*80)
    print("TRIGONOMETRIC PATTERN ANALYSIS")
    print("="*80)

    n_vals = [n for n in sorted(f_values.keys())]
    f_vals = [float(f_values[n]) for n in sorted(f_values.keys())]

    # Try to find period and amplitude
    # f(n) ≈ A + B*sin(C*n + D) or similar

    print("\nTesting sine wave fit: f(n) = A + B*sin(C*n + D)")

    # Simple correlation test for different periods
    for period in [5, 10, 20, 30, 45, 90]:
        omega = 2 * math.pi / period

        # Compute correlation with sin(omega * n)
        sin_vals = [math.sin(omega * n) for n in n_vals]

        # Normalize both
        f_mean = sum(f_vals) / len(f_vals)
        sin_mean = sum(sin_vals) / len(sin_vals)

        f_centered = [f - f_mean for f in f_vals]
        sin_centered = [s - sin_mean for s in sin_vals]

        # Correlation
        numerator = sum(f * s for f, s in zip(f_centered, sin_centered))
        f_var = sum(f**2 for f in f_centered)
        sin_var = sum(s**2 for s in sin_centered)

        if f_var > 0 and sin_var > 0:
            correlation = numerator / (math.sqrt(f_var * sin_var))
            print(f"  Period {period:3d}: correlation = {correlation:7.4f}")

def analyze_gap_specific_pattern(keys):
    """
    Focus specifically on the GAP puzzles (70, 75, 80, 85, 90)
    and see if there's a formula just for multiples of 5
    """
    print("\n" + "="*80)
    print("GAP-SPECIFIC PATTERN (multiples of 5)")
    print("="*80)

    # Get all multiples of 5 that we know
    mult5_keys = {n: k for n, k in keys.items() if n % 5 == 0}

    print(f"\nFound {len(mult5_keys)} keys with n divisible by 5:")

    for n in sorted(mult5_keys.keys()):
        k = mult5_keys[n]
        m = n // 5  # m = 1, 2, 3, 4, 5, ... for n = 5, 10, 15, 20, 25, ...

        # Normalize
        f_n = Decimal(k) / Decimal(2**(n-1))

        print(f"\nn={n} (m={m}): k[{n}] = {k}")
        print(f"  f({n}) = {f_n}")

        # Test if f(5m) follows pattern based on m
        if m > 1:
            # Check relationship to f(5(m-1))
            prev_n = n - 5
            if prev_n in mult5_keys:
                prev_k = mult5_keys[prev_n]
                prev_f = Decimal(prev_k) / Decimal(2**(prev_n-1))

                ratio = f_n / prev_f
                print(f"  f({n}) / f({prev_n}) = {ratio}")

                # Expected: 2^5 = 32 if purely exponential
                print(f"  Normalized ratio: {ratio / Decimal(32)}")

def main():
    print("="*80)
    print("DIRECT FORMULA DEEP ANALYSIS")
    print("="*80)

    # Load ALL known keys
    all_puzzle_ids = list(range(1, 71)) + [75, 80, 85, 90]
    keys = get_keys(all_puzzle_ids)

    print(f"\nLoaded {len(keys)} keys\n")

    # Run all analyses
    f_values = analyze_normalized_values(keys)
    test_f_as_continued_fraction(f_values)
    analyze_offset_ratios(keys)
    test_modular_arithmetic(keys)
    test_polynomial_fit(f_values)
    test_trigonometric_patterns(f_values)
    analyze_gap_specific_pattern(keys)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
