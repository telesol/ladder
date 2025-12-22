#!/usr/bin/env python3
"""
FINAL ANALYSIS: Find the exact recurrence relation for m-sequence
Based on discoveries:
1. m[n] = a*m[n-1] + b where a cycles through [2,3,1,2,3,1,3,3,1,2,2,2,2,...]
2. m[n] = a[n]*m[n-1] + m[n-2] + small_offset
"""

import numpy as np

# Known m-sequence
m_seq = {
    2: 3, 3: 7, 4: 22, 5: 27, 6: 57, 7: 150, 8: 184, 9: 493,
    10: 1444, 11: 1921, 12: 3723, 13: 8342, 14: 16272, 15: 26989,
    16: 67760, 17: 138269, 18: 255121, 19: 564091, 20: 900329
}

def analyze_convergent_pattern_precise():
    """Analyze m[n] = a[n]*m[n-1] + m[n-2] + offset pattern in detail"""
    print("=" * 80)
    print("CONVERGENT-STYLE RECURRENCE: m[n] = a[n]*m[n-1] + m[n-2] + offset")
    print("=" * 80)
    print()

    # Find the best integer a[n] and offset for each n
    a_sequence = []
    offset_sequence = []

    for n in range(4, 21):
        # Try all reasonable integer values of a[n]
        best_a = None
        best_offset = None
        min_abs_offset = float('inf')

        for a in range(-5, 10):
            offset = m_seq[n] - a * m_seq[n-1] - m_seq[n-2]
            if abs(offset) < min_abs_offset:
                min_abs_offset = abs(offset)
                best_a = a
                best_offset = offset

        a_sequence.append(best_a)
        offset_sequence.append(best_offset)

        print(f"  m[{n:2d}] = {best_a}*m[{n-1:2d}] + m[{n-2:2d}] + {best_offset:6d}")
        print(f"         = {best_a}*{m_seq[n-1]:7d} + {m_seq[n-2]:7d} + {best_offset:6d} = {m_seq[n]:7d}")

    # Analyze the a-sequence
    print("\n" + "=" * 80)
    print("ANALYSIS OF a-SEQUENCE")
    print("=" * 80)
    print(f"a-sequence: {a_sequence}")
    print()

    # Check for patterns in a-sequence
    print("Modulo patterns in a-sequence:")
    print(f"  a[n] mod 2: {[a % 2 for a in a_sequence]}")
    print(f"  a[n] mod 3: {[a % 3 for a in a_sequence]}")
    print()

    # Check if a-sequence follows a pattern based on n
    print("a-sequence by position modulo 3:")
    for mod in range(3):
        indices = [i for i in range(len(a_sequence)) if (i + 4) % 3 == mod]
        values = [a_sequence[i] for i in range(len(a_sequence)) if (i + 4) % 3 == mod]
        n_values = [i + 4 for i in range(len(a_sequence)) if (i + 4) % 3 == mod]
        print(f"  n ≡ {mod} (mod 3): n = {n_values}, a = {values}")

    print("\na-sequence by position modulo 4:")
    for mod in range(4):
        indices = [i for i in range(len(a_sequence)) if (i + 4) % 4 == mod]
        values = [a_sequence[i] for i in range(len(a_sequence)) if (i + 4) % 4 == mod]
        n_values = [i + 4 for i in range(len(a_sequence)) if (i + 4) % 4 == mod]
        print(f"  n ≡ {mod} (mod 4): n = {n_values}, a = {values}")

    # Analyze the offset sequence
    print("\n" + "=" * 80)
    print("ANALYSIS OF OFFSET-SEQUENCE")
    print("=" * 80)
    print(f"offset-sequence: {offset_sequence}")
    print()

    # Check if offsets relate to 2^n or m values
    print("Offset patterns:")
    for i, n in enumerate(range(4, 21)):
        offset = offset_sequence[i]
        power_of_2 = 2**n
        ratio_power = offset / power_of_2 if power_of_2 != 0 else 0

        # Check ratio to various m values
        ratios = []
        for k in range(2, n):
            if k in m_seq:
                ratio = offset / m_seq[k] if m_seq[k] != 0 else 0
                if abs(ratio) < 10 and abs(ratio) > 0.01:
                    ratios.append(f"m[{k}]:{ratio:.2f}")

        ratios_str = ", ".join(ratios[:3]) if ratios else "none"
        print(f"  n={n:2d}: offset={offset:6d}, 2^n ratio={ratio_power:7.4f}, m ratios: {ratios_str}")

def test_parity_based_recurrence():
    """Test if there's a different recurrence for odd vs even n"""
    print("\n" + "=" * 80)
    print("PARITY-BASED RECURRENCE")
    print("=" * 80)
    print()

    # Test for even n
    print("EVEN n: Test m[n] = a*m[n-1] + b*m[n-2]")
    even_equations = []
    even_results = []

    for n in [4, 6, 8, 10, 12, 14, 16, 18, 20]:
        if n-1 in m_seq and n-2 in m_seq:
            even_equations.append([m_seq[n-1], m_seq[n-2]])
            even_results.append(m_seq[n])

    A = np.array(even_equations, dtype=float)
    b = np.array(even_results, dtype=float)
    coeffs, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    a_even, b_even = coeffs

    print(f"  Best fit: m[n] = {a_even:.6f}*m[n-1] + {b_even:.6f}*m[n-2]")
    print("  Verification:")
    for n in [4, 6, 8, 10, 12, 14, 16, 18, 20]:
        predicted = a_even * m_seq[n-1] + b_even * m_seq[n-2]
        actual = m_seq[n]
        error = predicted - actual
        print(f"    n={n:2d}: predicted={predicted:10.1f}, actual={actual:7d}, error={error:8.1f}")

    # Test for odd n
    print("\nODD n: Test m[n] = a*m[n-1] + b*m[n-2]")
    odd_equations = []
    odd_results = []

    for n in [3, 5, 7, 9, 11, 13, 15, 17, 19]:
        if n-1 in m_seq and n-2 in m_seq:
            odd_equations.append([m_seq[n-1], m_seq[n-2]])
            odd_results.append(m_seq[n])

    A = np.array(odd_equations, dtype=float)
    b = np.array(odd_results, dtype=float)
    coeffs, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    a_odd, b_odd = coeffs

    print(f"  Best fit: m[n] = {a_odd:.6f}*m[n-1] + {b_odd:.6f}*m[n-2]")
    print("  Verification:")
    for n in [3, 5, 7, 9, 11, 13, 15, 17, 19]:
        if n-1 in m_seq and n-2 in m_seq:
            predicted = a_odd * m_seq[n-1] + b_odd * m_seq[n-2]
            actual = m_seq[n]
            error = predicted - actual
            print(f"    n={n:2d}: predicted={predicted:10.1f}, actual={actual:7d}, error={error:8.1f}")

def propose_generator_function():
    """Propose a generator function based on the analysis"""
    print("\n" + "=" * 80)
    print("PROPOSED GENERATOR FUNCTION")
    print("=" * 80)
    print()

    # Based on the integer multiplier analysis
    a_lookup = {
        3: 2, 4: 3, 5: 1, 6: 2, 7: 3, 8: 1, 9: 3, 10: 3, 11: 1,
        12: 2, 13: 2, 14: 2, 15: 2, 16: 3, 17: 2, 18: 2, 19: 2, 20: 2
    }

    print("Generator using integer multipliers a[n]:")
    print("Formula: m[n] = a[n]*m[n-1] + b[n]")
    print()

    # Compute b[n] for each
    for n in range(3, 21):
        if n in a_lookup and n-1 in m_seq:
            a = a_lookup[n]
            b = m_seq[n] - a * m_seq[n-1]
            print(f"  m[{n:2d}] = {a}*m[{n-1:2d}] + {b:7d}  (a[{n}]={a})")

    # Try to find pattern in a[n]
    print("\n" + "=" * 80)
    print("PATTERN IN a[n]")
    print("=" * 80)

    a_seq = [a_lookup[n] for n in range(3, 21)]
    print(f"a-sequence: {a_seq}")

    # Look for repeating patterns
    for period in range(2, 10):
        matches = True
        for i in range(len(a_seq) - period):
            if a_seq[i] != a_seq[i + period]:
                matches = False
                break
        if matches:
            print(f"  Period {period} detected: {a_seq[:period]}")

    # Check if related to n modulo something
    print("\nRelationship to n:")
    for n in range(3, 21):
        a = a_lookup[n]
        print(f"  n={n:2d}: n%3={n%3}, n%4={n%4}, n%5={n%5}, n%6={n%6}, a[n]={a}")

def main():
    print("FINAL RECURRENCE RELATION ANALYSIS FOR m-SEQUENCE")
    print()

    analyze_convergent_pattern_precise()
    test_parity_based_recurrence()
    propose_generator_function()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
