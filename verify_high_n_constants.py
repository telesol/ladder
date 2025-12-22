#!/usr/bin/env python3
"""
Verify constant patterns for k[75], k[80], k[85], k[90]
"""

import sqlite3
import math
from decimal import Decimal, getcontext

getcontext().prec = 50

# Mathematical constants
PI = Decimal(str(math.pi))
E = Decimal(str(math.e))
PHI = Decimal((1 + Decimal(5).sqrt()) / 2)
LN2 = Decimal(str(math.log(2)))
SQRT2 = Decimal(2).sqrt()
SQRT3 = Decimal(3).sqrt()

CONSTANTS = {
    'π/4': PI / 4,
    'e/π': E / PI,
    '1/φ': 1 / PHI,
    'ln(2)': LN2,
    'e/4': E / 4,
    '1/√2': 1 / SQRT2,
    '1/√3': 1 / SQRT3,
    'φ': PHI,
    'π/8': PI / 8,
    'e/2': E / 2,
}

def load_high_n_keys():
    """Load k[75], k[80], k[85], k[90] from database"""
    db_path = '/home/solo/LA/db/kh.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    k_values = {}
    for n in [75, 80, 85, 90]:
        cursor.execute("SELECT priv_hex FROM keys WHERE puzzle_id = ?", (n,))
        row = cursor.fetchone()
        if row:
            k_values[n] = int(row[0], 16)
            print(f"k[{n}] = {k_values[n]}")

    conn.close()
    return k_values

def analyze_high_n_constants(k_values):
    """Analyze which constants the high-n keys match"""
    print("\n" + "=" * 80)
    print("CONSTANT MATCHING ANALYSIS FOR HIGH-N KEYS")
    print("=" * 80)

    for n in sorted(k_values.keys()):
        k_n = k_values[n]
        alpha = Decimal(k_n) / Decimal(2 ** n)

        print(f"\n{'='*80}")
        print(f"n = {n}")
        print(f"k[{n}] = {k_n}")
        print(f"k[{n}] / 2^{n} = {float(alpha):.15f}")
        print(f"{'='*80}")

        # Find best matches
        matches = []
        for const_name, const_value in CONSTANTS.items():
            diff = abs(alpha - const_value)
            rel_error = diff / const_value if const_value != 0 else diff
            matches.append({
                'constant': const_name,
                'value': const_value,
                'rel_error': rel_error
            })

        # Sort by relative error
        matches.sort(key=lambda x: x['rel_error'])

        # Show top 5 matches
        print("\nTop 5 constant matches:")
        print("-" * 80)
        for i, m in enumerate(matches[:5], 1):
            print(f"{i}. {m['constant']:8s} = {float(m['value']):.15f}")
            print(f"   Relative error: {float(m['rel_error']) * 100:8.4f}%")
            if i < 5:
                print()

        # Check floor function matches
        print("\n\nFloor function check:")
        print("-" * 80)
        for const_name, const_value in CONSTANTS.items():
            predicted = int(const_value * Decimal(2 ** n))
            correction = k_n - predicted
            ratio = abs(correction) / k_n if k_n != 0 else 0

            if ratio < 0.05:  # Within 5%
                print(f"{const_name:8s}: k[{n}] ≈ floor({const_name} × 2^{n}) + {correction:+d}")
                print(f"           Correction: {ratio*100:.3f}% of k[{n}]")

def check_fibonacci_proximity(k_values):
    """Check if high-n indices relate to Fibonacci numbers"""
    print("\n\n" + "=" * 80)
    print("FIBONACCI/LUCAS INDEX ANALYSIS")
    print("=" * 80)

    # Generate Fibonacci
    fib = [1, 1]
    while fib[-1] < 100:
        fib.append(fib[-1] + fib[-2])

    print(f"\nFibonacci numbers up to 100: {fib}")

    print("\nHigh-n puzzle indices: 75, 80, 85, 90")
    print("\nProximity to Fibonacci numbers:")
    for n in [75, 80, 85, 90]:
        closest_fib = min(fib, key=lambda f: abs(f - n))
        diff = n - closest_fib
        print(f"  n={n}: closest Fibonacci is {closest_fib}, diff = {diff:+d}")

    # Check if they're multiples of Fibonacci
    print("\nChecking if n is divisible by Fibonacci numbers:")
    for n in [75, 80, 85, 90]:
        divisors = [f for f in fib if f > 1 and n % f == 0]
        if divisors:
            print(f"  n={n}: divisible by Fibonacci {divisors}")
        else:
            print(f"  n={n}: not divisible by any Fibonacci > 1")

    # Factorization
    print("\nFactorization:")
    print(f"  75 = 3 × 5² = 3 × 25")
    print(f"  80 = 2^4 × 5 = 16 × 5")
    print(f"  85 = 5 × 17")
    print(f"  90 = 2 × 3² × 5 = 2 × 45")
    print("\n  Note: 3, 5 are Fibonacci numbers!")
    print("        55, 89 are also Fibonacci (close to 75, 85, 90)")

def check_position_in_range(k_values):
    """Check position in range [2^(n-1), 2^n)"""
    print("\n\n" + "=" * 80)
    print("POSITION IN RANGE ANALYSIS")
    print("=" * 80)

    for n in sorted(k_values.keys()):
        k_n = k_values[n]
        min_val = 2 ** (n - 1)
        max_val = 2 ** n - 1
        range_size = max_val - min_val + 1

        position = (k_n - min_val) / range_size

        print(f"\nk[{n}]:")
        print(f"  Position in range: {position * 100:.4f}%")

        # Check if position matches a constant
        for const_name, const_value in CONSTANTS.items():
            # Normalize to [0, 1]
            norm_const = float(const_value)
            while norm_const > 1:
                norm_const -= int(norm_const)

            if abs(position - norm_const) / norm_const < 0.01:  # Within 1%
                print(f"  ≈ {const_name} (fractional part) = {norm_const:.6f}")
                print(f"    Error: {abs(position - norm_const) / norm_const * 100:.3f}%")

def main():
    print("VERIFICATION OF CONSTANT PATTERNS FOR HIGH-N KEYS")
    print("=" * 80)
    print("\nLoading k[75], k[80], k[85], k[90] from database...\n")

    k_values = load_high_n_keys()

    if not k_values:
        print("\nERROR: No high-n keys found in database!")
        return

    print(f"\nLoaded {len(k_values)} high-n keys")

    # Run analyses
    analyze_high_n_constants(k_values)
    check_fibonacci_proximity(k_values)
    check_position_in_range(k_values)

    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY: HIGH-N PATTERN CONTINUATION")
    print("=" * 80)
    print("""
The analysis of k[75], k[80], k[85], k[90] will reveal if the pattern
of mathematical constants continues beyond n=70.

Key questions:
1. Do these high-n values still match π/4, 1/φ, ln(2), e/π?
2. Is precision still increasing with n?
3. Are Fibonacci indices (55, 89) special?
4. Do multiples of 5 have a pattern? (75, 80, 85, 90)
    """)

if __name__ == '__main__':
    main()
