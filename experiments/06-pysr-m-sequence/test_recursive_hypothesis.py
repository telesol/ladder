#!/usr/bin/env python3
"""
Test Recursive Hypothesis
Check if m[n] can be expressed as combinations of previous m-values
"""

from convergent_database import M_SEQUENCE, D_SEQUENCE

def test_linear_combinations(target_n, max_lookback=10):
    """
    Test if m[n] = a*m[i] + b*m[j] + c
    where i, j < n
    """
    target = M_SEQUENCE[target_n]
    matches = []

    for i in range(2, target_n):
        for j in range(2, target_n):
            mi = M_SEQUENCE[i]
            mj = M_SEQUENCE[j]

            # Test simple combinations
            tests = [
                (mi + mj, f'm[{i}] + m[{j}]', (1, 1, 0)),
                (mi - mj, f'm[{i}] - m[{j}]', (1, -1, 0)),
                (mi * mj, f'm[{i}] × m[{j}]', None),
                (mi + mj + 1, f'm[{i}] + m[{j}] + 1', (1, 1, 1)),
                (mi + mj - 1, f'm[{i}] + m[{j}] - 1', (1, 1, -1)),
                (mi * 2 + mj, f'2×m[{i}] + m[{j}]', (2, 1, 0)),
                (mi * 3 + mj, f'3×m[{i}] + m[{j}]', (3, 1, 0)),
                (mi + mj * 2, f'm[{i}] + 2×m[{j}]', (1, 2, 0)),
                (mi + mj * 3, f'm[{i}] + 3×m[{j}]', (1, 3, 0)),
            ]

            for value, formula, coeffs in tests:
                if value == target:
                    matches.append({
                        'formula': formula,
                        'value': value,
                        'coeffs': coeffs
                    })

    return matches

def test_with_d_sequence(target_n):
    """Test if d[n] is involved in the formula."""
    target = M_SEQUENCE[target_n]
    d = D_SEQUENCE[target_n]
    matches = []

    for i in range(2, target_n):
        mi = M_SEQUENCE[i]

        # Test d-based formulas
        tests = [
            (mi * d, f'd[{target_n}] × m[{i}] = {d} × m[{i}]'),
            (mi + d, f'm[{i}] + d[{target_n}] = m[{i}] + {d}'),
            (mi - d, f'm[{i}] - d[{target_n}] = m[{i}] - {d}'),
        ]

        for value, formula in tests:
            if value == target:
                matches.append(formula)

    # Two-term with d
    for i in range(2, target_n):
        for j in range(2, target_n):
            mi = M_SEQUENCE[i]
            mj = M_SEQUENCE[j]

            tests = [
                (mi * d + mj, f'd[{target_n}]×m[{i}] + m[{j}] = {d}×m[{i}] + m[{j}]'),
                (mi + mj * d, f'm[{i}] + d[{target_n}]×m[{j}] = m[{i}] + {d}×m[{j}]'),
            ]

            for value, formula in tests:
                if value == target:
                    matches.append(formula)

    return matches

def test_fibonacci_style(target_n):
    """Test if m[n] = a*m[n-1] + b*m[n-2] + c"""
    if target_n < 4:
        return []

    target = M_SEQUENCE[target_n]
    matches = []

    # Simple Fibonacci-like
    if target_n >= 3:
        m_prev1 = M_SEQUENCE[target_n - 1]
        m_prev2 = M_SEQUENCE[target_n - 2]

        tests = [
            (m_prev1 + m_prev2, f'm[{target_n-1}] + m[{target_n-2}]'),
            (m_prev1 - m_prev2, f'm[{target_n-1}] - m[{target_n-2}]'),
            (m_prev1 * 2 - m_prev2, f'2×m[{target_n-1}] - m[{target_n-2}]'),
            (m_prev1 * 2 + m_prev2, f'2×m[{target_n-1}] + m[{target_n-2}]'),
        ]

        for value, formula in tests:
            if value == target:
                matches.append(formula)

    return matches

def main():
    print("="*80)
    print("RECURSIVE HYPOTHESIS TESTING")
    print("="*80)

    print("\nTesting if m[n] can be expressed using previous m-values...\n")

    for n in range(4, 16):
        print(f"\n{'='*80}")
        print(f"n={n}, m[{n}]={M_SEQUENCE[n]}, d[{n}]={D_SEQUENCE[n]}")
        print(f"{'='*80}")

        # Test linear combinations
        linear_matches = test_linear_combinations(n)
        if linear_matches:
            print(f"\nLINEAR COMBINATIONS ({len(linear_matches)} found):")
            for match in linear_matches[:10]:  # Limit to 10
                print(f"  {match['formula']} = {match['value']}")

        # Test Fibonacci-style
        fib_matches = test_fibonacci_style(n)
        if fib_matches:
            print(f"\nFIBONACCI-STYLE RECURSION:")
            for match in fib_matches:
                print(f"  {match}")

        # Test with d-sequence
        d_matches = test_with_d_sequence(n)
        if d_matches:
            print(f"\nWITH D-SEQUENCE ({len(d_matches)} found):")
            for match in d_matches[:10]:  # Limit to 10
                print(f"  {match}")

        if not linear_matches and not fib_matches and not d_matches:
            print("\nNO RECURSIVE MATCHES FOUND")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY OF RECURSIVE PATTERNS")
    print("="*80)

    summary = {}
    for n in range(4, 16):
        linear_matches = test_linear_combinations(n)
        fib_matches = test_fibonacci_style(n)
        d_matches = test_with_d_sequence(n)

        total = len(linear_matches) + len(fib_matches) + len(d_matches)
        summary[n] = {
            'linear': len(linear_matches),
            'fib': len(fib_matches),
            'd_seq': len(d_matches),
            'total': total
        }

    for n in range(4, 16):
        s = summary[n]
        print(f"m[{n:2}] = {M_SEQUENCE[n]:>8}: "
              f"Linear={s['linear']:2}, Fib={s['fib']:2}, D-seq={s['d_seq']:2}, "
              f"Total={s['total']:2}")

    # Specific interesting cases
    print("\n" + "="*80)
    print("NOTABLE RECURSIVE FORMULAS")
    print("="*80)

    notable = {
        8: test_linear_combinations(8),
        10: test_linear_combinations(10),
        11: test_linear_combinations(11),
    }

    for n, matches in notable.items():
        if matches:
            print(f"\nm[{n}] = {M_SEQUENCE[n]}:")
            for match in matches[:5]:
                print(f"  {match['formula']}")

if __name__ == "__main__":
    main()
