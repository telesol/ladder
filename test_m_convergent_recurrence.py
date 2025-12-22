#!/usr/bin/env python3
"""
Test if m-sequence is built from convergents or mathematical constant approximations
Based on discovery that m[4]/m[3] = 22/7 (π approximation)
"""

import numpy as np
from fractions import Fraction

# Known m-sequence
m_seq = {
    2: 3, 3: 7, 4: 22, 5: 27, 6: 57, 7: 150, 8: 184, 9: 493,
    10: 1444, 11: 1921, 12: 3723, 13: 8342, 14: 16272, 15: 26989,
    16: 67760, 17: 138269, 18: 255121, 19: 564091, 20: 900329
}

def get_continued_fraction(value, max_terms=20):
    """Get continued fraction representation of a value"""
    cf = []
    for _ in range(max_terms):
        integer_part = int(value)
        cf.append(integer_part)
        fractional_part = value - integer_part
        if abs(fractional_part) < 1e-10:
            break
        value = 1 / fractional_part
    return cf

def convergents_from_cf(cf):
    """Get convergent fractions from continued fraction"""
    convergents = []
    h_prev2, h_prev1 = 0, 1
    k_prev2, k_prev1 = 1, 0

    for a in cf:
        h = a * h_prev1 + h_prev2
        k = a * k_prev1 + k_prev2
        convergents.append((h, k))
        h_prev2, h_prev1 = h_prev1, h
        k_prev2, k_prev1 = k_prev1, k

    return convergents

def analyze_ratios():
    """Analyze m[n+1]/m[n] and m[n+2]/m[n] ratios"""
    print("=" * 80)
    print("RATIO ANALYSIS")
    print("=" * 80)

    print("\nConsecutive ratios m[n+1]/m[n]:")
    for n in range(2, 20):
        ratio = m_seq[n+1] / m_seq[n]
        frac = Fraction(m_seq[n+1], m_seq[n]).limit_denominator(1000)
        print(f"  m[{n+1:2d}]/m[{n:2d}] = {m_seq[n+1]:7d}/{m_seq[n]:7d} = {ratio:8.6f} ≈ {frac}")

    print("\nSkip-one ratios m[n+2]/m[n]:")
    for n in range(2, 19):
        ratio = m_seq[n+2] / m_seq[n]
        frac = Fraction(m_seq[n+2], m_seq[n]).limit_denominator(1000)
        print(f"  m[{n+2:2d}]/m[{n:2d}] = {m_seq[n+2]:7d}/{m_seq[n]:7d} = {ratio:8.6f} ≈ {frac}")

def analyze_fibonacci_like():
    """Test if m[n] = a*m[n-1] + b*m[n-2] with varying a,b"""
    print("\n" + "=" * 80)
    print("FIBONACCI-LIKE WITH VARYING COEFFICIENTS")
    print("=" * 80)

    print("\nCompute implied coefficients if m[n] = a*m[n-1] + b*m[n-2]:")

    for n in range(4, 21):
        # Solve: m[n] = a*m[n-1] + b*m[n-2]
        # We have one equation, two unknowns, so try b = 1
        # m[n] = a*m[n-1] + 1*m[n-2]
        # a = (m[n] - m[n-2]) / m[n-1]

        a = (m_seq[n] - m_seq[n-2]) / m_seq[n-1]
        b = 1

        # Also try b = -1
        a_neg = (m_seq[n] + m_seq[n-2]) / m_seq[n-1]
        b_neg = -1

        # Also try integer a with minimal b
        a_int = m_seq[n] // m_seq[n-1]
        b_from_int = m_seq[n] - a_int * m_seq[n-1]

        print(f"\n  n={n:2d}: m[{n}]={m_seq[n]:7d}")
        print(f"    If b=+1: a={a:8.6f}  →  m[{n}] = {a:.6f}*m[{n-1}] + 1*m[{n-2}]")
        print(f"    If b=-1: a={a_neg:8.6f}  →  m[{n}] = {a_neg:.6f}*m[{n-1}] - 1*m[{n-2}]")
        print(f"    If a={a_int}: b={b_from_int:7d}  →  m[{n}] = {a_int}*m[{n-1}] + {b_from_int}")

def check_pattern_in_differences():
    """Check if differences follow a pattern related to 2^n or other constants"""
    print("\n" + "=" * 80)
    print("DIFFERENCE PATTERNS")
    print("=" * 80)

    # Corrections from m[n] = 2*m[n-1] + correction[n]
    print("\nCorrection from doubling: correction[n] = m[n] - 2*m[n-1]")
    corrections = {}
    for n in range(3, 21):
        corrections[n] = m_seq[n] - 2 * m_seq[n-1]

        # Check if correction relates to 2^n
        power_ratio = corrections[n] / (2**n)

        # Check if correction relates to m[n-2]
        if n > 3:
            m_ratio = corrections[n] / m_seq[n-2] if m_seq[n-2] != 0 else 0
        else:
            m_ratio = 0

        print(f"  corr[{n:2d}] = {corrections[n]:7d}  |  corr/2^n = {power_ratio:8.6f}  |  corr/m[{n-2}] = {m_ratio:8.6f}")

    # Check pattern: m[n] = 2*m[n-1] + m[n-2]
    print("\nTest: m[n] = 2*m[n-1] + m[n-2]")
    for n in range(4, 21):
        predicted = 2 * m_seq[n-1] + m_seq[n-2]
        actual = m_seq[n]
        error = predicted - actual
        print(f"  n={n:2d}: 2*{m_seq[n-1]:7d} + {m_seq[n-2]:7d} = {predicted:7d}  |  actual={actual:7d}  |  error={error:7d}")

    # Check pattern: m[n] = 2*m[n-1] - m[n-2]
    print("\nTest: m[n] = 2*m[n-1] - m[n-2]")
    for n in range(4, 21):
        predicted = 2 * m_seq[n-1] - m_seq[n-2]
        actual = m_seq[n]
        error = predicted - actual
        print(f"  n={n:2d}: 2*{m_seq[n-1]:7d} - {m_seq[n-2]:7d} = {predicted:7d}  |  actual={actual:7d}  |  error={error:7d}")

    # Check pattern: m[n] = 3*m[n-1] - m[n-2]
    print("\nTest: m[n] = 3*m[n-1] - m[n-2]")
    for n in range(4, 21):
        predicted = 3 * m_seq[n-1] - m_seq[n-2]
        actual = m_seq[n]
        error = predicted - actual
        print(f"  n={n:2d}: 3*{m_seq[n-1]:7d} - {m_seq[n-2]:7d} = {predicted:7d}  |  actual={actual:7d}  |  error={error:7d}")

def check_modular_patterns():
    """Check if there's a pattern when n is odd vs even"""
    print("\n" + "=" * 80)
    print("ODD/EVEN INDEX PATTERNS")
    print("=" * 80)

    odd_indices = [n for n in range(3, 21, 2)]
    even_indices = [n for n in range(2, 21, 2)]

    print("\nOdd indices (n=3,5,7,...):")
    for n in odd_indices:
        print(f"  m[{n:2d}] = {m_seq[n]:7d}")

    print("\nEven indices (n=2,4,6,...):")
    for n in even_indices:
        print(f"  m[{n:2d}] = {m_seq[n]:7d}")

    # Check if odd subsequence follows a recurrence
    print("\nOdd subsequence recurrence test: m[n] = a*m[n-2] + b*m[n-4]")
    for i in range(2, len(odd_indices)-1):
        n = odd_indices[i]
        n_prev = odd_indices[i-1]
        n_prev2 = odd_indices[i-2]

        if n_prev2 in m_seq:
            # Solve for a,b
            # m[n] = a*m[n-2] + b*m[n-4]
            A = np.array([[m_seq[n_prev], m_seq[n_prev2]]])
            b_vec = np.array([m_seq[n]])

            # Not enough equations for 2 unknowns, try a=2
            a = 2
            b_implied = (m_seq[n] - a * m_seq[n_prev]) / m_seq[n_prev2] if m_seq[n_prev2] != 0 else 0
            print(f"  m[{n:2d}] = 2*m[{n_prev:2d}] + {b_implied:.2f}*m[{n_prev2:2d}]")

def check_sum_patterns():
    """Check various sum/combination patterns"""
    print("\n" + "=" * 80)
    print("SUM/COMBINATION PATTERNS")
    print("=" * 80)

    # Check m[n] = m[n-1] + m[n-2] + offset
    print("\nTest: m[n] = m[n-1] + m[n-2] + offset")
    for n in range(4, 21):
        predicted = m_seq[n-1] + m_seq[n-2]
        actual = m_seq[n]
        offset = actual - predicted
        print(f"  m[{n:2d}] = m[{n-1:2d}] + m[{n-2:2d}] + {offset:7d}  =  {m_seq[n-1]:7d} + {m_seq[n-2]:7d} + {offset:7d}")

def main():
    print("RECURRENCE RELATION ANALYSIS FOR m-SEQUENCE")
    print("Focus: Mathematical constant convergents and construction patterns")
    print()

    analyze_ratios()
    analyze_fibonacci_like()
    check_pattern_in_differences()
    check_modular_patterns()
    check_sum_patterns()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
