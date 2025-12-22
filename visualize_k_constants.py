#!/usr/bin/env python3
"""
Create visual summary of k-value constant relationships
"""

import sqlite3
import math
from decimal import Decimal, getcontext

getcontext().prec = 50

# Constants
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
}

def load_all_k_values():
    """Load all available k-values"""
    db_path = '/home/solo/LA/db/kh.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    k_values = {}

    # Load k[1] through k[70]
    for n in range(1, 71):
        cursor.execute("SELECT priv_hex FROM keys WHERE puzzle_id = ?", (n,))
        row = cursor.fetchone()
        if row:
            k_values[n] = int(row[0], 16)

    # Load k[75], k[80], k[85], k[90]
    for n in [75, 80, 85, 90]:
        cursor.execute("SELECT priv_hex FROM keys WHERE puzzle_id = ?", (n,))
        row = cursor.fetchone()
        if row:
            k_values[n] = int(row[0], 16)

    conn.close()
    return k_values

def find_best_constant_for_each_n(k_values):
    """Find best matching constant for each n"""
    results = {}

    for n in sorted(k_values.keys()):
        k_n = k_values[n]
        alpha = Decimal(k_n) / Decimal(2 ** n)

        best_match = None
        best_error = float('inf')

        for const_name, const_value in CONSTANTS.items():
            rel_error = abs(alpha - const_value) / const_value if const_value != 0 else abs(alpha)

            if rel_error < best_error:
                best_error = rel_error
                best_match = const_name

        results[n] = {
            'constant': best_match,
            'error': float(best_error) * 100,
            'alpha': float(alpha)
        }

    return results

def print_constant_map(results):
    """Print a visual map of which constant dominates each n"""
    print("=" * 80)
    print("CONSTANT DOMINANCE MAP")
    print("=" * 80)
    print("\nShowing best-matching constant for each n (if error < 10%):\n")

    # Group by constant
    by_constant = {}
    for n, data in results.items():
        if data['error'] < 10:  # Only show good matches
            const = data['constant']
            if const not in by_constant:
                by_constant[const] = []
            by_constant[const].append((n, data['error']))

    # Print each constant's territory
    for const in sorted(by_constant.keys()):
        matches = by_constant[const]
        print(f"\n{const}:")
        print("  " + "-" * 70)

        # Group consecutive n values
        groups = []
        current_group = [matches[0]]

        for i in range(1, len(matches)):
            if matches[i][0] == current_group[-1][0] + 1:
                current_group.append(matches[i])
            else:
                groups.append(current_group)
                current_group = [matches[i]]
        groups.append(current_group)

        # Print groups
        for group in groups:
            if len(group) == 1:
                n, err = group[0]
                print(f"  n={n:2d}  (error: {err:.3f}%)")
            else:
                n_start = group[0][0]
                n_end = group[-1][0]
                avg_err = sum(e for _, e in group) / len(group)
                print(f"  n={n_start:2d}-{n_end:2d}  (avg error: {avg_err:.3f}%)")

def print_precision_timeline(results):
    """Show how precision changes with n"""
    print("\n\n" + "=" * 80)
    print("PRECISION TIMELINE (Top 20 best matches)")
    print("=" * 80)

    # Sort by error
    sorted_results = sorted(results.items(), key=lambda x: x[1]['error'])

    print(f"\n{'Rank':<6} {'n':<6} {'Constant':<8} {'Error':<12} {'Alpha':<15}")
    print("-" * 80)

    for i, (n, data) in enumerate(sorted_results[:20], 1):
        print(f"{i:<6} {n:<6} {data['constant']:<8} {data['error']:>8.4f}%  {data['alpha']:.10f}")

def print_fibonacci_correlation(results):
    """Check correlation with Fibonacci numbers"""
    print("\n\n" + "=" * 80)
    print("FIBONACCI INDEX CORRELATION")
    print("=" * 80)

    # Generate Fibonacci
    fib = [1, 1]
    while fib[-1] < 100:
        fib.append(fib[-1] + fib[-2])

    print(f"\nFibonacci numbers up to 100: {fib}")

    # Check matches at or near Fibonacci indices
    print("\n\nk-values at Fibonacci indices:")
    print("-" * 80)

    for f in fib:
        if f in results:
            data = results[f]
            print(f"n={f:2d} (F): {data['constant']:<8} error={data['error']:>7.3f}%")

        # Check neighbors
        for offset in [-1, 1]:
            n = f + offset
            if n in results and n not in fib:
                data = results[n]
                sign = '+' if offset > 0 else ''
                print(f"n={n:2d} (F{sign}{offset}): {data['constant']:<8} error={data['error']:>7.3f}%")

        if f in results or f-1 in results or f+1 in results:
            print()

def print_multi_encodings(k_values):
    """Find values that match multiple constants well"""
    print("\n\n" + "=" * 80)
    print("MULTI-CONSTANT ENCODINGS (Dual/Triple matches)")
    print("=" * 80)

    print("\nValues where multiple constants match within 5%:\n")

    for n in sorted(k_values.keys()):
        k_n = k_values[n]
        alpha = Decimal(k_n) / Decimal(2 ** n)

        matches = []
        for const_name, const_value in CONSTANTS.items():
            rel_error = abs(alpha - const_value) / const_value if const_value != 0 else abs(alpha)
            if rel_error < Decimal('0.05'):  # Within 5%
                matches.append((const_name, float(rel_error) * 100))

        if len(matches) >= 2:
            print(f"n={n}:")
            for const, err in matches:
                print(f"  {const:<8} error={err:>6.3f}%")
            print()

def main():
    print("VISUAL ANALYSIS OF K-VALUE CONSTANT RELATIONSHIPS")
    print("=" * 80)
    print("\nLoading k-values from database...")

    k_values = load_all_k_values()
    print(f"Loaded {len(k_values)} k-values\n")

    # Find best constant for each n
    results = find_best_constant_for_each_n(k_values)

    # Print analyses
    print_constant_map(results)
    print_precision_timeline(results)
    print_fibonacci_correlation(results)
    print_multi_encodings(k_values)

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    # Count by constant
    by_const = {}
    for n, data in results.items():
        if data['error'] < 10:
            const = data['constant']
            by_const[const] = by_const.get(const, 0) + 1

    print("\nDominant constant frequency (error < 10%):")
    for const, count in sorted(by_const.items(), key=lambda x: -x[1]):
        pct = count / len([r for r in results.values() if r['error'] < 10]) * 100
        print(f"  {const:<8}: {count:2d} matches ({pct:5.1f}%)")

    # Precision ranges
    errors = [data['error'] for data in results.values()]
    print(f"\nError statistics:")
    print(f"  Best (min):  {min(errors):.4f}%")
    print(f"  Worst (max): {max(errors):.4f}%")
    print(f"  Average:     {sum(errors)/len(errors):.4f}%")
    print(f"  Median:      {sorted(errors)[len(errors)//2]:.4f}%")

    # Count ultra-precise matches
    ultra = len([e for e in errors if e < 0.1])
    very = len([e for e in errors if e < 1.0])
    good = len([e for e in errors if e < 5.0])

    print(f"\nPrecision breakdown:")
    print(f"  Ultra-precise (<0.1%): {ultra} values")
    print(f"  Very precise  (<1.0%): {very} values")
    print(f"  Good match    (<5.0%): {good} values")
    print(f"  Total analyzed:        {len(results)} values")

if __name__ == '__main__':
    main()
