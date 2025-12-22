#!/usr/bin/env python3
"""
Search for mathematical constants in k-values
"""

import sqlite3
import math
from fractions import Fraction
from decimal import Decimal, getcontext

# Set high precision for calculations
getcontext().prec = 50

# Mathematical constants
PI = Decimal(str(math.pi))
E = Decimal(str(math.e))
PHI = Decimal((1 + Decimal(5).sqrt()) / 2)  # Golden ratio
LN2 = Decimal(str(math.log(2)))
SQRT2 = Decimal(2).sqrt()
SQRT3 = Decimal(3).sqrt()

CONSTANTS = {
    'π': PI,
    'π/2': PI / 2,
    'π/4': PI / 4,
    'π/8': PI / 8,
    'e': E,
    'e/2': E / 2,
    'e/4': E / 4,
    'φ (phi)': PHI,
    '1/φ': 1 / PHI,
    'φ²': PHI * PHI,
    'ln(2)': LN2,
    '1/ln(2)': 1 / LN2,
    '1/√2': 1 / SQRT2,
    '√2': SQRT2,
    '√3': SQRT3,
    '1/√3': 1 / SQRT3,
    '√5': Decimal(5).sqrt(),
    'e/π': E / PI,
    'π/e': PI / E,
}

def load_k_values():
    """Load k[1] through k[70] from database"""
    db_path = '/home/solo/LA/db/kh.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    k_values = {}
    for n in range(1, 71):
        cursor.execute("SELECT priv_hex FROM keys WHERE puzzle_id = ?", (n,))
        row = cursor.fetchone()
        if row:
            k_values[n] = int(row[0], 16)

    conn.close()
    return k_values

def analyze_alpha_values(k_values):
    """Analyze k[n] / 2^n (alpha values)"""
    print("=" * 80)
    print("ANALYSIS 1: Alpha values (k[n] / 2^n)")
    print("=" * 80)

    results = []
    for n in sorted(k_values.keys()):
        k_n = k_values[n]
        alpha = Decimal(k_n) / Decimal(2 ** n)

        # Check proximity to each constant
        matches = []
        for const_name, const_value in CONSTANTS.items():
            diff = abs(alpha - const_value)
            relative_error = diff / const_value if const_value != 0 else diff

            if relative_error < Decimal('0.05'):  # Within 5%
                matches.append((const_name, const_value, relative_error))

        if matches:
            matches.sort(key=lambda x: x[2])  # Sort by relative error
            best_match = matches[0]
            results.append({
                'n': n,
                'k_n': k_n,
                'alpha': alpha,
                'constant': best_match[0],
                'const_value': best_match[1],
                'rel_error': best_match[2]
            })

    # Print results
    if results:
        print(f"\nFound {len(results)} alpha values close to mathematical constants:\n")
        for r in results:
            print(f"n={r['n']:2d}: k[{r['n']}]/{2**r['n']} = {float(r['alpha']):.6f}")
            print(f"      ≈ {r['constant']} = {float(r['const_value']):.6f}")
            print(f"      Relative error: {float(r['rel_error']) * 100:.3f}%\n")
    else:
        print("\nNo alpha values found close to mathematical constants.")

    return results

def analyze_floor_constant(k_values):
    """Check if k[n] = floor(C × 2^n) + correction"""
    print("\n" + "=" * 80)
    print("ANALYSIS 2: k[n] = floor(C × 2^n) + correction")
    print("=" * 80)

    results = []
    for const_name, const_value in CONSTANTS.items():
        matches = []
        for n in sorted(k_values.keys()):
            k_n = k_values[n]
            predicted = int(const_value * Decimal(2 ** n))
            correction = k_n - predicted

            # Check if correction is small or has a pattern
            if abs(correction) <= 1000 or abs(correction) < k_n * 0.01:  # Small correction
                matches.append({
                    'n': n,
                    'k_n': k_n,
                    'predicted': predicted,
                    'correction': correction,
                    'ratio': abs(correction) / k_n if k_n != 0 else 0
                })

        if len(matches) >= 5:  # At least 5 matches
            results.append({
                'constant': const_name,
                'const_value': const_value,
                'matches': matches
            })

    # Print results
    if results:
        for r in results:
            print(f"\nConstant: {r['constant']} = {float(r['const_value']):.10f}")
            print(f"Matches: {len(r['matches'])}/70\n")
            for m in r['matches'][:10]:  # Show first 10
                print(f"  n={m['n']:2d}: k[{m['n']}] = {m['k_n']}")
                print(f"       floor({r['constant']} × 2^{m['n']}) = {m['predicted']}")
                print(f"       correction = {m['correction']:+d} ({m['ratio']*100:.2f}%)\n")
            if len(r['matches']) > 10:
                print(f"  ... and {len(r['matches']) - 10} more matches")
    else:
        print("\nNo floor(C × 2^n) patterns found.")

    return results

def analyze_ladder_differences(k_values):
    """Check if k[n+1] - 2×k[n] relates to constants"""
    print("\n" + "=" * 80)
    print("ANALYSIS 3: Ladder differences k[n+1] - 2×k[n]")
    print("=" * 80)

    diffs = {}
    for n in range(1, 70):
        if n in k_values and n+1 in k_values:
            diff = k_values[n+1] - 2 * k_values[n]
            diffs[n] = diff

    print(f"\nComputed {len(diffs)} ladder differences:\n")

    # Show first 20
    for n in sorted(diffs.keys())[:20]:
        print(f"d[{n}] = k[{n+1}] - 2×k[{n}] = {diffs[n]}")

    if len(diffs) > 20:
        print(f"\n... and {len(diffs) - 20} more")

    # Check if differences relate to constants
    print("\n\nChecking if differences relate to mathematical constants:")
    print("-" * 60)

    results = []
    for const_name, const_value in CONSTANTS.items():
        matches = []
        for n, diff in diffs.items():
            # Check if diff / 2^n ≈ constant
            ratio = Decimal(diff) / Decimal(2 ** n)
            rel_error = abs(ratio - const_value) / abs(const_value) if const_value != 0 else abs(ratio)

            if rel_error < Decimal('0.1'):  # Within 10%
                matches.append({
                    'n': n,
                    'diff': diff,
                    'ratio': ratio,
                    'rel_error': rel_error
                })

        if len(matches) >= 3:
            results.append({
                'constant': const_name,
                'const_value': const_value,
                'matches': matches
            })

    if results:
        for r in results:
            print(f"\nConstant: {r['constant']} = {float(r['const_value']):.10f}")
            print(f"Pattern: d[n] / 2^n ≈ {r['constant']}")
            print(f"Matches: {len(r['matches'])}\n")
            for m in r['matches'][:5]:
                print(f"  n={m['n']:2d}: d[{m['n']}] / 2^{m['n']} = {float(m['ratio']):.10f}")
                print(f"       Relative error: {float(m['rel_error']) * 100:.2f}%")
    else:
        print("\nNo constant patterns found in ladder differences.")

    return results

def analyze_k_ratios(k_values):
    """Look for continued fraction patterns in k[n]/k[m] ratios"""
    print("\n" + "=" * 80)
    print("ANALYSIS 4: k[n]/k[m] ratios and continued fractions")
    print("=" * 80)

    # Check ratios against constants
    results = []

    for n in sorted(k_values.keys()):
        for m in sorted(k_values.keys()):
            if m >= n:
                continue

            ratio = Decimal(k_values[n]) / Decimal(k_values[m])

            # Check against constants
            for const_name, const_value in CONSTANTS.items():
                rel_error = abs(ratio - const_value) / const_value if const_value != 0 else abs(ratio)

                if rel_error < Decimal('0.001'):  # Within 0.1%
                    results.append({
                        'n': n,
                        'm': m,
                        'k_n': k_values[n],
                        'k_m': k_values[m],
                        'ratio': ratio,
                        'constant': const_name,
                        'const_value': const_value,
                        'rel_error': rel_error
                    })

    # Sort by relative error
    results.sort(key=lambda x: x['rel_error'])

    if results:
        print(f"\nFound {len(results)} ratios close to mathematical constants:\n")
        for r in results[:20]:  # Show top 20
            print(f"k[{r['n']}] / k[{r['m']}] = {r['k_n']} / {r['k_m']}")
            print(f"  = {float(r['ratio']):.10f}")
            print(f"  ≈ {r['constant']} = {float(r['const_value']):.10f}")
            print(f"  Relative error: {float(r['rel_error']) * 100:.4f}%\n")

        if len(results) > 20:
            print(f"... and {len(results) - 20} more matches")
    else:
        print("\nNo k[n]/k[m] ratios found close to mathematical constants.")

    return results

def analyze_fibonacci_lucas(k_values):
    """Check relationships to Fibonacci and Lucas numbers"""
    print("\n" + "=" * 80)
    print("ANALYSIS 5: Fibonacci and Lucas number relationships")
    print("=" * 80)

    # Generate Fibonacci numbers
    fib = [1, 1]
    while fib[-1] < 10**15:
        fib.append(fib[-1] + fib[-2])

    # Generate Lucas numbers
    lucas = [2, 1]
    while lucas[-1] < 10**15:
        lucas.append(lucas[-1] + lucas[-2])

    print("\nChecking if k-values are Fibonacci numbers:")
    fib_matches = []
    for n, k_n in sorted(k_values.items()):
        if k_n in fib:
            idx = fib.index(k_n)
            fib_matches.append((n, k_n, idx))
            print(f"  k[{n}] = {k_n} = F[{idx}] (Fibonacci #{idx})")

    if not fib_matches:
        print("  No exact Fibonacci matches.")

    print("\nChecking if k-values are Lucas numbers:")
    lucas_matches = []
    for n, k_n in sorted(k_values.items()):
        if k_n in lucas:
            idx = lucas.index(k_n)
            lucas_matches.append((n, k_n, idx))
            print(f"  k[{n}] = {k_n} = L[{idx}] (Lucas #{idx})")

    if not lucas_matches:
        print("  No exact Lucas matches.")

    return {'fibonacci': fib_matches, 'lucas': lucas_matches}

def analyze_power_of_2_proximity(k_values):
    """Check how close k[n] is to 2^n (position in range)"""
    print("\n" + "=" * 80)
    print("ANALYSIS 6: Position in range [2^(n-1), 2^n)")
    print("=" * 80)

    results = []
    for n in sorted(k_values.keys()):
        k_n = k_values[n]
        min_val = 2 ** (n - 1)
        max_val = 2 ** n - 1
        range_size = max_val - min_val + 1

        # Position as percentage
        position = (k_n - min_val) / range_size

        results.append({
            'n': n,
            'k_n': k_n,
            'position': position,
            'distance_from_min': k_n - min_val,
            'distance_from_max': max_val - k_n
        })

    # Find extreme positions
    print("\nKeys near minimum (position < 5%):")
    near_min = [r for r in results if r['position'] < 0.05]
    for r in near_min:
        print(f"  k[{r['n']}] = {r['k_n']} (position: {r['position']*100:.2f}%)")

    print("\nKeys near maximum (position > 95%):")
    near_max = [r for r in results if r['position'] > 0.95]
    for r in near_max:
        print(f"  k[{r['n']}] = {r['k_n']} (position: {r['position']*100:.2f}%)")

    # Check if position relates to constants
    print("\nChecking if positions relate to constants:")
    const_matches = []
    for r in results:
        pos = Decimal(str(r['position']))
        for const_name, const_value in CONSTANTS.items():
            # Normalize constant to [0, 1]
            norm_const = const_value
            while norm_const > 1:
                norm_const = norm_const - int(norm_const)

            rel_error = abs(pos - norm_const) / norm_const if norm_const != 0 else abs(pos)

            if rel_error < Decimal('0.05'):  # Within 5%
                const_matches.append({
                    'n': r['n'],
                    'position': pos,
                    'constant': const_name,
                    'const_value': norm_const,
                    'rel_error': rel_error
                })

    if const_matches:
        const_matches.sort(key=lambda x: x['rel_error'])
        print(f"\nFound {len(const_matches)} positions matching constants:\n")
        for m in const_matches[:10]:
            print(f"  k[{m['n']}] position = {float(m['position']):.6f}")
            print(f"    ≈ {m['constant']} (fractional part) = {float(m['const_value']):.6f}")
            print(f"    Relative error: {float(m['rel_error']) * 100:.2f}%\n")
    else:
        print("\nNo position-constant relationships found.")

    return results

def main():
    print("Loading k-values from database...")
    k_values = load_k_values()
    print(f"Loaded {len(k_values)} k-values (k[1] through k[70])\n")

    # Run all analyses
    alpha_results = analyze_alpha_values(k_values)
    floor_results = analyze_floor_constant(k_values)
    ladder_results = analyze_ladder_differences(k_values)
    ratio_results = analyze_k_ratios(k_values)
    fib_lucas_results = analyze_fibonacci_lucas(k_values)
    position_results = analyze_power_of_2_proximity(k_values)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Alpha value matches: {len(alpha_results)}")
    print(f"Floor constant patterns: {len(floor_results)}")
    print(f"Ladder difference patterns: {len(ladder_results)}")
    print(f"k[n]/k[m] ratio matches: {len(ratio_results)}")
    print(f"Fibonacci matches: {len(fib_lucas_results['fibonacci'])}")
    print(f"Lucas matches: {len(fib_lucas_results['lucas'])}")
    print(f"Position-constant matches: {len([r for r in position_results if r['position'] < 0.05 or r['position'] > 0.95])}")

if __name__ == '__main__':
    main()
