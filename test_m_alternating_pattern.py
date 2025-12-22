#!/usr/bin/env python3
"""
Test alternating coefficient patterns in m-sequence
Observation: When m[n] = a*m[n-1] + b, the coefficient 'a' seems to alternate
"""

import numpy as np
from typing import List, Tuple

# Known m-sequence
m_seq = {
    2: 3, 3: 7, 4: 22, 5: 27, 6: 57, 7: 150, 8: 184, 9: 493,
    10: 1444, 11: 1921, 12: 3723, 13: 8342, 14: 16272, 15: 26989,
    16: 67760, 17: 138269, 18: 255121, 19: 564091, 20: 900329
}

def analyze_integer_multipliers():
    """Determine if m[n] can be expressed as integer multiple + offset"""
    print("=" * 80)
    print("INTEGER MULTIPLIER ANALYSIS: m[n] = a*m[n-1] + b")
    print("=" * 80)
    print()

    # For each n, find best integer a
    pattern_a = []
    pattern_b = []

    for n in range(3, 21):
        # Try integer multipliers 1, 2, 3, 4
        best_a = None
        best_b = None
        min_abs_b = float('inf')

        for a in [1, 2, 3, 4]:
            b = m_seq[n] - a * m_seq[n-1]
            if abs(b) < min_abs_b:
                min_abs_b = abs(b)
                best_a = a
                best_b = b

        pattern_a.append(best_a)
        pattern_b.append(best_b)

        print(f"  m[{n:2d}] = {best_a}*m[{n-1:2d}] + {best_b:7d}  =  {best_a}*{m_seq[n-1]:7d} + {best_b:7d}  =  {m_seq[n]:7d}")

    # Analyze the pattern of 'a' values
    print("\n" + "=" * 80)
    print("PATTERN OF MULTIPLIERS:")
    print("=" * 80)
    print(f"a-sequence: {pattern_a}")

    # Group by consecutive same values
    print("\nGrouped by value:")
    i = 0
    n_start = 3
    while i < len(pattern_a):
        current_a = pattern_a[i]
        count = 1
        while i + count < len(pattern_a) and pattern_a[i + count] == current_a:
            count += 1

        n_end = n_start + count - 1
        print(f"  a={current_a}: n={n_start}..{n_end} (length {count})")

        n_start = n_end + 1
        i += count

    # Check for alternating pattern
    print("\nAlternation analysis:")
    for i in range(len(pattern_a) - 1):
        n = i + 3
        print(f"  n={n:2d}→{n+1:2d}: a changes from {pattern_a[i]} to {pattern_a[i+1]}")

def analyze_fibonacci_offset():
    """Test m[n] = m[n-1] + m[n-2] + offset, analyze the offset pattern"""
    print("\n" + "=" * 80)
    print("FIBONACCI WITH OFFSET: m[n] = m[n-1] + m[n-2] + offset[n]")
    print("=" * 80)
    print()

    offsets = {}
    for n in range(4, 21):
        offset = m_seq[n] - m_seq[n-1] - m_seq[n-2]
        offsets[n] = offset

    # Show offsets
    for n in range(4, 21):
        print(f"  offset[{n:2d}] = {offsets[n]:7d}")

    # Check if offset relates to 2^n
    print("\n" + "=" * 80)
    print("OFFSET RELATIONSHIP TO POWERS OF 2:")
    print("=" * 80)
    print()

    for n in range(4, 21):
        power = 2**n
        ratio = offsets[n] / power
        print(f"  offset[{n:2d}] = {offsets[n]:7d}  |  2^{n:2d} = {power:7d}  |  ratio = {ratio:10.6f}")

    # Check if offset follows a recurrence
    print("\n" + "=" * 80)
    print("OFFSET RECURRENCE TEST: offset[n] = a*offset[n-1] + b")
    print("=" * 80)
    print()

    for n in range(5, 21):
        # Try different integer a values
        for a in [-2, -1, 0, 1, 2, 3]:
            b = offsets[n] - a * offsets[n-1]
            # Check if b is small
            if abs(b) < 100:
                print(f"  offset[{n:2d}] = {a:2d}*offset[{n-1:2d}] + {b:4d}  =  {a:2d}*{offsets[n-1]:7d} + {b:4d}")
                break

def test_modulo_patterns():
    """Check if there's a pattern in m[n] modulo small numbers"""
    print("\n" + "=" * 80)
    print("MODULO PATTERNS")
    print("=" * 80)
    print()

    for mod in [2, 3, 4, 5, 7, 8, 11]:
        print(f"m[n] mod {mod}:")
        residues = [m_seq[n] % mod for n in range(2, 21)]
        print(f"  {residues}")
        print()

def test_piecewise_pattern():
    """Check if pattern changes at specific boundaries"""
    print("\n" + "=" * 80)
    print("PIECEWISE PATTERN DETECTION")
    print("=" * 80)
    print()

    # Split into ranges and check for different patterns
    ranges = [
        (3, 6, "Early: n=3..6"),
        (7, 10, "Middle-early: n=7..10"),
        (11, 14, "Middle: n=11..14"),
        (15, 20, "Later: n=15..20")
    ]

    for start, end, label in ranges:
        print(f"\n{label}:")

        # Test linear recurrence for this range
        if end - start >= 3:
            equations = []
            results = []

            for n in range(start+2, min(end+1, 21)):
                if n-1 in m_seq and n-2 in m_seq:
                    eq = [m_seq[n-1], m_seq[n-2]]
                    equations.append(eq)
                    results.append(m_seq[n])

            if len(equations) >= 2:
                A = np.array(equations, dtype=float)
                b = np.array(results, dtype=float)

                coeffs, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
                a, b_coef = coeffs

                print(f"  Best fit: m[n] = {a:.6f}*m[n-1] + {b_coef:.6f}*m[n-2]")
                if len(residuals) > 0:
                    print(f"  Residuals: {residuals[0]:.2f}")

def check_convergent_construction():
    """Check if m[n] uses convergent-like construction"""
    print("\n" + "=" * 80)
    print("CONVERGENT-LIKE CONSTRUCTION")
    print("=" * 80)
    print()

    # In convergents: h[n] = a[n]*h[n-1] + h[n-2]
    # Check if there's a sequence a[n] that works

    print("Finding a[n] such that m[n] = a[n]*m[n-1] + m[n-2]:")
    print()

    a_values = []
    for n in range(4, 21):
        # m[n] = a[n]*m[n-1] + m[n-2]
        # a[n] = (m[n] - m[n-2]) / m[n-1]
        a_n = (m_seq[n] - m_seq[n-2]) / m_seq[n-1]
        a_values.append(a_n)

        # Also compute the closest integer
        a_int = round(a_n)
        error = abs(a_n - a_int)

        print(f"  a[{n:2d}] = {a_n:10.6f}  (closest int: {a_int}, error: {error:.6f})")

        # Check if using the integer works
        predicted = a_int * m_seq[n-1] + m_seq[n-2]
        actual = m_seq[n]
        diff = actual - predicted

        if abs(diff) < 1000:
            print(f"       → m[{n:2d}] = {a_int}*m[{n-1:2d}] + m[{n-2:2d}] + {diff:5d}")

    print(f"\na-sequence: {[round(a, 2) for a in a_values]}")

def main():
    print("ALTERNATING PATTERN ANALYSIS FOR m-SEQUENCE")
    print("Goal: Find if m[n] follows a pattern with varying coefficients")
    print()

    analyze_integer_multipliers()
    analyze_fibonacci_offset()
    test_modulo_patterns()
    test_piecewise_pattern()
    check_convergent_construction()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
