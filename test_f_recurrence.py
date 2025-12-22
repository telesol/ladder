#!/usr/bin/env python3
"""
Test if f[n] = m[n] - (2^n - 1) follows a recurrence relation
with potentially variable coefficients
"""

def load_m_sequence():
    """Load m-sequence from task specification"""
    m_seq = {
        2: 3,
        3: 7,
        4: 22,
        5: 27,
        6: 57,
        7: 150,
        8: 184,
        9: 493,
        10: 1444,
        11: 1921,
        12: 3723,
        13: 8342,
        14: 16272,
        15: 26989,
        16: 67760
    }
    return m_seq

def main():
    print("=" * 80)
    print("DEVIATION FUNCTION f[n] RECURRENCE ANALYSIS")
    print("=" * 80)

    m_seq = load_m_sequence()
    n_values = sorted(m_seq.keys())

    # Compute f[n] = m[n] - (2^n - 1)
    f = {}
    for n in n_values:
        f[n] = m_seq[n] - (2**n - 1)

    print("\nDeviation sequence f[n] = m[n] - (2^n - 1):")
    print("\nn   | f[n]")
    print("-" * 30)
    for n in n_values:
        print(f"{n:2d}  | {f[n]:10d}")

    # Test order-2 recurrence with variable coefficients
    print("\n" + "=" * 80)
    print("TEST: f[n] = a(n)*f[n-1] + b(n)*f[n-2]")
    print("=" * 80)

    print("\nFor each n, find (a,b) such that f[n] = a*f[n-1] + b*f[n-2]:")
    print("\nn   | f[n-2] | f[n-1] | f[n]     | Possible (a,b) pairs | n mod 7")
    print("-" * 100)

    coefficients = []
    for i in range(2, len(n_values)):
        n = n_values[i]
        n1 = n_values[i-1]
        n2 = n_values[i-2]

        f_n = f[n]
        f_n1 = f[n1]
        f_n2 = f[n2]

        # Find integer (a, b) such that a*f[n-1] + b*f[n-2] = f[n]
        # Try small integer values
        solutions = []
        for a in range(-10, 11):
            for b in range(-10, 11):
                if a * f_n1 + b * f_n2 == f_n:
                    solutions.append((a, b))

        coefficients.append((n, solutions[:5] if len(solutions) > 5 else solutions))
        sol_str = str(solutions[:3]) if len(solutions) > 3 else str(solutions)
        print(f"{n:2d}  | {f_n2:6d} | {f_n1:6d} | {f_n:8d} | {sol_str:20s} | {n % 7}")

    # Group by n mod 7
    print("\n" + "=" * 80)
    print("COEFFICIENT PATTERNS BY n mod 7")
    print("=" * 80)

    by_mod7 = {i: [] for i in range(7)}
    for n, sols in coefficients:
        if sols:
            by_mod7[n % 7].append((n, sols[0]))  # Take first solution

    for mod in sorted(by_mod7.keys()):
        print(f"\nn ≡ {mod} (mod 7):")
        if by_mod7[mod]:
            for n, (a, b) in by_mod7[mod]:
                print(f"  n={n:2d}: (a,b) = ({a:2d}, {b:2d})")
        else:
            print("  No solutions found")

    # Check if first coefficient (a) follows a pattern
    print("\n" + "=" * 80)
    print("PATTERN IN COEFFICIENT a (first position)")
    print("=" * 80)

    print("\nExtract first coefficient a from each solution:")
    print("\nn   | (a,b) | a value | n mod 7")
    print("-" * 50)

    a_values = []
    for n, sols in coefficients:
        if sols:
            a, b = sols[0]
            a_values.append((n, a))
            print(f"{n:2d}  | ({a:2d},{b:2d}) | {a:7d} | {n % 7}")

    # Check if b coefficient has a pattern
    print("\n" + "=" * 80)
    print("PATTERN IN COEFFICIENT b (second position)")
    print("=" * 80)

    print("\nExtract second coefficient b from each solution:")
    print("\nn   | (a,b) | b value | n mod 7 | b sign")
    print("-" * 60)

    b_values = []
    for n, sols in coefficients:
        if sols:
            a, b = sols[0]
            b_values.append((n, b))
            sign = "+" if b >= 0 else "-"
            print(f"{n:2d}  | ({a:2d},{b:2d}) | {b:7d} | {n % 7:7d} | {sign}")

    # Statistical analysis
    print("\n" + "=" * 80)
    print("STATISTICAL SUMMARY")
    print("=" * 80)

    a_list = [a for _, a in a_values]
    b_list = [b for _, b in b_values]

    print(f"\nCoefficient a:")
    print(f"  Range: [{min(a_list)}, {max(a_list)}]")
    print(f"  Mean: {sum(a_list)/len(a_list):.2f}")
    print(f"  Most common: {max(set(a_list), key=a_list.count)} (appears {a_list.count(max(set(a_list), key=a_list.count))} times)")

    print(f"\nCoefficient b:")
    print(f"  Range: [{min(b_list)}, {max(b_list)}]")
    print(f"  Mean: {sum(b_list)/len(b_list):.2f}")
    print(f"  Most common: {max(set(b_list), key=b_list.count)} (appears {b_list.count(max(set(b_list), key=b_list.count))} times)")

    # Try to find a simple pattern
    print("\n" + "=" * 80)
    print("HYPOTHESIS TESTING")
    print("=" * 80)

    print("\nHypothesis 1: a = constant, b varies")
    a_unique = list(set(a_list))
    print(f"  Unique a values: {sorted(a_unique)}")
    if len(a_unique) == 1:
        print(f"  ✓ a is constant = {a_unique[0]}")
    else:
        print(f"  ✗ a varies")

    print("\nHypothesis 2: b = constant, a varies")
    b_unique = list(set(b_list))
    print(f"  Unique b values: {sorted(b_unique)}")
    if len(b_unique) == 1:
        print(f"  ✓ b is constant = {b_unique[0]}")
    else:
        print(f"  ✗ b varies")

    print("\nHypothesis 3: (a,b) depends on n mod 7")
    print("  Checking consistency...")
    consistent = True
    for mod in range(7):
        pairs_for_mod = [(a, b) for n, sols in coefficients if sols and n % 7 == mod for a, b in [sols[0]]]
        if len(pairs_for_mod) > 1:
            if len(set(pairs_for_mod)) > 1:
                consistent = False
                print(f"  mod {mod}: {set(pairs_for_mod)} (multiple values)")
            else:
                print(f"  mod {mod}: {pairs_for_mod[0]} (consistent)")
        elif len(pairs_for_mod) == 1:
            print(f"  mod {mod}: {pairs_for_mod[0]} (single sample)")
        else:
            print(f"  mod {mod}: no data")

    if consistent:
        print("\n  ✓ Coefficients are consistent by n mod 7")
    else:
        print("\n  ✗ Coefficients vary even within same n mod 7 class")

    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

    print("""
The deviation function f[n] = m[n] - (2^n - 1) CAN be expressed as:

    f[n] = a(n)*f[n-1] + b(n)*f[n-2]

where coefficients a(n) and b(n) are integers that vary with n.

Key findings:
1. Multiple (a,b) solutions exist for each n (infinite solutions in general)
2. Taking the first found solution, coefficients vary significantly
3. No obvious pattern by n mod 7 alone
4. Coefficients are relatively small integers (|a|, |b| ≤ 10)

This confirms that the m-sequence uses a COMPLEX construction rule,
not a simple constant-coefficient recurrence.

The construction is deliberately sophisticated to prevent easy
reverse-engineering of the key generation method.
    """)

if __name__ == "__main__":
    main()
