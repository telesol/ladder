#!/usr/bin/env python3
"""
Test recurrence relations for m-sequence
Goal: Find how to construct m[n] from previous values
"""

import numpy as np
from typing import List, Tuple, Optional

# Known m-sequence
m_seq = {
    2: 3, 3: 7, 4: 22, 5: 27, 6: 57, 7: 150, 8: 184, 9: 493,
    10: 1444, 11: 1921, 12: 3723, 13: 8342, 14: 16272, 15: 26989,
    16: 67760, 17: 138269, 18: 255121, 19: 564091, 20: 900329
}

def test_linear_constant_recurrence():
    """Test: m[n] = a*m[n-1] + b*m[n-2] + c*2^n + d"""
    print("=" * 80)
    print("TEST 1: Linear constant recurrence m[n] = a*m[n-1] + b*m[n-2] + c*2^n + d")
    print("=" * 80)

    # Build system of equations for n=4..10
    equations = []
    results = []

    for n in range(4, 11):
        # m[n] = a*m[n-1] + b*m[n-2] + c*2^n + d
        # Coefficients: [a, b, c, d]
        eq = [m_seq[n-1], m_seq[n-2], 2**n, 1]
        equations.append(eq)
        results.append(m_seq[n])

    A = np.array(equations, dtype=float)
    b = np.array(results, dtype=float)

    # Solve least squares
    coeffs, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    a, b_coef, c, d = coeffs

    print(f"Fitted coefficients:")
    print(f"  a = {a:.10f}")
    print(f"  b = {b_coef:.10f}")
    print(f"  c = {c:.10f}")
    print(f"  d = {d:.10f}")
    print(f"Residuals: {residuals}")
    print()

    # Verify against all known values
    print("Verification:")
    max_error = 0
    for n in range(4, 21):
        predicted = a * m_seq[n-1] + b_coef * m_seq[n-2] + c * (2**n) + d
        actual = m_seq[n]
        error = abs(predicted - actual)
        max_error = max(max_error, error)
        status = "✓" if error < 0.5 else "✗"
        print(f"  n={n:2d}: predicted={predicted:10.2f}, actual={actual:7d}, error={error:8.2f} {status}")

    print(f"\nMax error: {max_error:.2f}")
    return max_error < 0.5

def test_ratio_pattern():
    """Test: Compute m[n+1]/m[n] ratios"""
    print("\n" + "=" * 80)
    print("TEST 2: Ratio analysis m[n+1]/m[n]")
    print("=" * 80)

    ratios = []
    for n in range(2, 20):
        ratio = m_seq[n+1] / m_seq[n]
        ratios.append(ratio)
        print(f"  m[{n+1}]/m[{n}] = {ratio:.6f}")

    print(f"\nMean ratio: {np.mean(ratios):.6f}")
    print(f"Std ratio: {np.std(ratios):.6f}")

    # Check if ratios themselves follow a pattern
    print("\nRatio differences:")
    for i in range(1, len(ratios)):
        diff = ratios[i] - ratios[i-1]
        print(f"  Δ(n={i+2}): {diff:+.6f}")

def test_normalized_sequence():
    """Test: m[n]/2^n recurrence"""
    print("\n" + "=" * 80)
    print("TEST 3: Normalized sequence u[n] = m[n]/2^n")
    print("=" * 80)

    u_seq = {}
    for n in range(2, 21):
        u_seq[n] = m_seq[n] / (2**n)
        print(f"  u[{n}] = m[{n}]/2^{n} = {u_seq[n]:.10f}")

    # Test if u[n] follows simple recurrence
    print("\nTest: u[n] = a*u[n-1] + b")
    equations = []
    results = []

    for n in range(3, 11):
        eq = [u_seq[n-1], 1]
        equations.append(eq)
        results.append(u_seq[n])

    A = np.array(equations)
    b = np.array(results)

    coeffs, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    a, b_coef = coeffs

    print(f"Fitted: u[n] = {a:.10f}*u[n-1] + {b_coef:.10f}")
    print(f"Residuals: {residuals}")

    # Verify
    print("\nVerification of u[n]:")
    for n in range(3, 21):
        predicted = a * u_seq[n-1] + b_coef
        actual = u_seq[n]
        error = abs(predicted - actual)
        status = "✓" if error < 1e-6 else "✗"
        print(f"  n={n:2d}: predicted={predicted:.10f}, actual={actual:.10f}, error={error:.2e} {status}")

def test_correction_pattern():
    """Test: m[n] = 2*m[n-1] + correction[n]"""
    print("\n" + "=" * 80)
    print("TEST 4: Correction pattern m[n] = 2*m[n-1] + correction[n]")
    print("=" * 80)

    corrections = {}
    for n in range(3, 21):
        correction = m_seq[n] - 2 * m_seq[n-1]
        corrections[n] = correction
        print(f"  correction[{n}] = m[{n}] - 2*m[{n-1}] = {correction:7d}")

    # Check if corrections follow a pattern
    print("\nCorrection differences:")
    for n in range(4, 21):
        diff = corrections[n] - corrections[n-1]
        print(f"  Δcorr[{n}] = {diff:7d}")

    # Test if correction follows recurrence
    print("\nTest: correction[n] = a*correction[n-1] + b*correction[n-2]")
    equations = []
    results = []

    for n in range(5, 11):
        eq = [corrections[n-1], corrections[n-2]]
        equations.append(eq)
        results.append(corrections[n])

    A = np.array(equations, dtype=float)
    b = np.array(results, dtype=float)

    coeffs, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    a, b_coef = coeffs

    print(f"Fitted: correction[n] = {a:.10f}*correction[n-1] + {b_coef:.10f}*correction[n-2]")
    print(f"Residuals: {residuals}")

    # Verify
    print("\nVerification of correction pattern:")
    for n in range(5, 21):
        predicted = a * corrections[n-1] + b_coef * corrections[n-2]
        actual = corrections[n]
        error = abs(predicted - actual)
        status = "✓" if error < 0.5 else "✗"
        print(f"  n={n:2d}: predicted={predicted:10.2f}, actual={actual:7d}, error={error:8.2f} {status}")

def test_second_order_recurrence():
    """Test: m[n] = a*m[n-1] + b*m[n-2]"""
    print("\n" + "=" * 80)
    print("TEST 5: Pure second-order recurrence m[n] = a*m[n-1] + b*m[n-2]")
    print("=" * 80)

    equations = []
    results = []

    for n in range(4, 11):
        eq = [m_seq[n-1], m_seq[n-2]]
        equations.append(eq)
        results.append(m_seq[n])

    A = np.array(equations, dtype=float)
    b = np.array(results, dtype=float)

    coeffs, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    a, b_coef = coeffs

    print(f"Fitted: m[n] = {a:.10f}*m[n-1] + {b_coef:.10f}*m[n-2]")
    print(f"Residuals: {residuals}")

    # Verify
    print("\nVerification:")
    max_error = 0
    for n in range(4, 21):
        predicted = a * m_seq[n-1] + b_coef * m_seq[n-2]
        actual = m_seq[n]
        error = abs(predicted - actual)
        max_error = max(max_error, error)
        status = "✓" if error < 0.5 else "✗"
        print(f"  n={n:2d}: predicted={predicted:10.2f}, actual={actual:7d}, error={error:8.2f} {status}")

    print(f"\nMax error: {max_error:.2f}")
    return max_error < 0.5

def test_third_order_recurrence():
    """Test: m[n] = a*m[n-1] + b*m[n-2] + c*m[n-3]"""
    print("\n" + "=" * 80)
    print("TEST 6: Third-order recurrence m[n] = a*m[n-1] + b*m[n-2] + c*m[n-3]")
    print("=" * 80)

    equations = []
    results = []

    for n in range(5, 11):
        eq = [m_seq[n-1], m_seq[n-2], m_seq[n-3]]
        equations.append(eq)
        results.append(m_seq[n])

    A = np.array(equations, dtype=float)
    b = np.array(results, dtype=float)

    coeffs, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    a, b_coef, c = coeffs

    print(f"Fitted coefficients:")
    print(f"  a = {a:.10f}")
    print(f"  b = {b_coef:.10f}")
    print(f"  c = {c:.10f}")
    print(f"Residuals: {residuals}")
    print()

    # Verify
    print("Verification:")
    max_error = 0
    for n in range(5, 21):
        predicted = a * m_seq[n-1] + b_coef * m_seq[n-2] + c * m_seq[n-3]
        actual = m_seq[n]
        error = abs(predicted - actual)
        max_error = max(max_error, error)
        status = "✓" if error < 0.5 else "✗"
        print(f"  n={n:2d}: predicted={predicted:10.2f}, actual={actual:7d}, error={error:8.2f} {status}")

    print(f"\nMax error: {max_error:.2f}")
    return max_error < 0.5

def test_fibonacci_like_with_offset():
    """Test: m[n] = a*m[n-1] + b*m[n-2] + f(n)"""
    print("\n" + "=" * 80)
    print("TEST 7: Fibonacci-like with offset m[n] = a*m[n-1] + b*m[n-2] + c*n + d")
    print("=" * 80)

    equations = []
    results = []

    for n in range(4, 11):
        eq = [m_seq[n-1], m_seq[n-2], n, 1]
        equations.append(eq)
        results.append(m_seq[n])

    A = np.array(equations, dtype=float)
    b = np.array(results, dtype=float)

    coeffs, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    a, b_coef, c, d = coeffs

    print(f"Fitted coefficients:")
    print(f"  a = {a:.10f}")
    print(f"  b = {b_coef:.10f}")
    print(f"  c = {c:.10f}")
    print(f"  d = {d:.10f}")
    print(f"Residuals: {residuals}")
    print()

    # Verify
    print("Verification:")
    max_error = 0
    for n in range(4, 21):
        predicted = a * m_seq[n-1] + b_coef * m_seq[n-2] + c * n + d
        actual = m_seq[n]
        error = abs(predicted - actual)
        max_error = max(max_error, error)
        status = "✓" if error < 0.5 else "✗"
        print(f"  n={n:2d}: predicted={predicted:10.2f}, actual={actual:7d}, error={error:8.2f} {status}")

    print(f"\nMax error: {max_error:.2f}")
    return max_error < 0.5

def test_differences():
    """Analyze differences and second differences"""
    print("\n" + "=" * 80)
    print("TEST 8: Difference analysis")
    print("=" * 80)

    # First differences
    print("First differences d1[n] = m[n] - m[n-1]:")
    d1 = {}
    for n in range(3, 21):
        d1[n] = m_seq[n] - m_seq[n-1]
        print(f"  d1[{n}] = {d1[n]:7d}")

    # Second differences
    print("\nSecond differences d2[n] = d1[n] - d1[n-1]:")
    d2 = {}
    for n in range(4, 21):
        d2[n] = d1[n] - d1[n-1]
        print(f"  d2[{n}] = {d2[n]:7d}")

    # Third differences
    print("\nThird differences d3[n] = d2[n] - d2[n-1]:")
    d3 = {}
    for n in range(5, 21):
        d3[n] = d2[n] - d2[n-1]
        print(f"  d3[{n}] = {d3[n]:7d}")

def main():
    print("RECURRENCE RELATION ANALYSIS FOR m-SEQUENCE")
    print("=" * 80)
    print("m-sequence: m[2]=3, m[3]=7, m[4]=22, m[5]=27, m[6]=57, ...")
    print("Goal: Find recurrence relation to construct m[n] from previous values")
    print()

    # Run all tests
    test_linear_constant_recurrence()
    test_ratio_pattern()
    test_normalized_sequence()
    test_correction_pattern()
    test_second_order_recurrence()
    test_third_order_recurrence()
    test_fibonacci_like_with_offset()
    test_differences()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
