#!/usr/bin/env python3
"""
CRITICAL OBSERVATION: m[2] = 3 = 2^2 - 1, m[3] = 7 = 2^3 - 1
Check if this pattern extends or if m[n] has special relationship to 2^n - 1
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
    print("CRITICAL PATTERN: m[n] vs 2^n - 1")
    print("=" * 80)

    m_seq = load_m_sequence()
    n_values = sorted(m_seq.keys())

    print("\nOBSERVATION:")
    print(f"  m[2] = {m_seq[2]} = 2^2 - 1 = {2**2 - 1} ✓")
    print(f"  m[3] = {m_seq[3]} = 2^3 - 1 = {2**3 - 1} ✓")

    print("\nFull comparison:")
    print("\nn   | m[n]     | 2^n - 1     | m[n] / (2^n - 1) | Difference")
    print("-" * 90)

    for n in n_values:
        m = m_seq[n]
        pow2_minus_1 = 2**n - 1
        ratio = m / pow2_minus_1
        diff = m - pow2_minus_1

        marker = "✓" if m == pow2_minus_1 else ""
        print(f"{n:2d}  | {m:8d} | {pow2_minus_1:11d} | {ratio:16.9f} | {diff:10d} {marker}")

    print("\n" + "=" * 80)
    print("HYPOTHESIS: m[n] may be CONSTRUCTED from 2^n - 1")
    print("=" * 80)

    print("\nFor n ≥ 4, m[n] ≠ 2^n - 1, but check if m[n] = a*(2^n - 1) + b:")

    print("\nn   | m[n]     | 2^n - 1  | m[n] mod (2^n - 1)")
    print("-" * 60)

    for n in n_values:
        m = m_seq[n]
        pow2_minus_1 = 2**n - 1
        mod = m % pow2_minus_1

        print(f"{n:2d}  | {m:8d} | {pow2_minus_1:8d} | {mod:19d}")

    # Check if m[n] = (2^n - 1) + f(n) for some function f
    print("\n" + "=" * 80)
    print("ADDITIVE DECOMPOSITION: m[n] = (2^n - 1) + f(n)")
    print("=" * 80)

    print("\nn   | f(n) = m[n] - (2^n - 1) | f(n) / (2^n - 1)")
    print("-" * 60)

    f_values = []
    for n in n_values:
        m = m_seq[n]
        pow2_minus_1 = 2**n - 1
        f = m - pow2_minus_1
        f_ratio = f / pow2_minus_1 if pow2_minus_1 > 0 else 0

        f_values.append(f)
        print(f"{n:2d}  | {f:24d} | {f_ratio:16.9f}")

    print(f"\nf-sequence: {f_values}")

    # Check if f[n] follows a pattern
    print("\n" + "=" * 80)
    print("PATTERN IN f[n]:")
    print("=" * 80)

    print("\nCheck if f[n] = a*f[n-1] + b*f[n-2]:")
    for i in range(2, min(len(f_values), 10)):
        f_n = f_values[i]
        f_n1 = f_values[i-1]
        f_n2 = f_values[i-2]

        # Try to find a, b
        # f_n = a*f_n1 + b*f_n2
        # We have one equation, infinite solutions
        # Try simple integer values
        found = False
        for a in range(-5, 6):
            for b in range(-5, 6):
                if a * f_n1 + b * f_n2 == f_n:
                    n = n_values[i]
                    print(f"n={n}: f[{n}] = {a}*f[{n-1}] + {b}*f[{n-2}] = {a}*{f_n1} + {b}*{f_n2} = {f_n}")
                    found = True
                    break
            if found:
                break

    # Check multiplicative pattern
    print("\n" + "=" * 80)
    print("MULTIPLICATIVE DECOMPOSITION: m[n] = a*(2^n - 1)")
    print("=" * 80)

    print("\nn   | m[n] / (2^n - 1) | Continued fraction approximation")
    print("-" * 80)

    for n in n_values:
        m = m_seq[n]
        pow2_minus_1 = 2**n - 1
        ratio = m / pow2_minus_1

        # Compute simple fraction approximation
        from fractions import Fraction
        frac = Fraction(m, pow2_minus_1).limit_denominator(1000)

        print(f"{n:2d}  | {ratio:16.9f} | {frac}")

    # Check if m[n] * (2^k - 1) has special properties
    print("\n" + "=" * 80)
    print("PRODUCT ANALYSIS: m[n] * (2^k - 1) for various k")
    print("=" * 80)

    print("\nCheck if m[n] * (2^n - 1) mod (2^(n+1) - 1) has a pattern:")
    print("\nn   | m[n] * (2^n - 1) | mod (2^(n+1) - 1)")
    print("-" * 70)

    for n in n_values[:10]:
        m = m_seq[n]
        pow2n_minus_1 = 2**n - 1
        pow2n1_minus_1 = 2**(n+1) - 1

        product = m * pow2n_minus_1
        mod = product % pow2n1_minus_1

        print(f"{n:2d}  | {product:16d} | {mod:20d}")

    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

    print("""
The m-sequence starts with:
  - m[2] = 2^2 - 1 = 3 (Mersenne number)
  - m[3] = 2^3 - 1 = 7 (Mersenne prime)

For n ≥ 4, m[n] diverges from 2^n - 1, but the ratio m[n]/(2^n - 1)
varies between 0.72 and 1.47, suggesting m[n] is constructed as a
PERTURBATION or SCALING of the Mersenne numbers.

This connection to Mersenne numbers (2^n - 1) is significant because:
1. The puzzle uses 2^n ranges
2. Mersenne primes have special properties in cryptography
3. m[4]/m[3] = 22/7 relates to π, another fundamental constant

Recommendation: Investigate if m[n] is built using:
  - Mersenne number bases: 2^n - 1
  - Convergent corrections: adding/subtracting terms to hit target ratios
  - Modular arithmetic on Mersenne numbers
    """)

if __name__ == "__main__":
    main()
