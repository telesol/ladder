#!/usr/bin/env python3
"""
CONSTRUCT C(n) FUNCTION

Based on deep analysis, construct the function C(n) that determines k[n]/2^n.

KEY FINDINGS:
1. Anchor constants use convergents: π/4, e/π, 1/φ, e/4, ln(2), φ-1, 1/√2
2. π/4 × e/π = e/4 (EXACT relationship!)
3. Between anchors, polynomial degree 2-3 fits reasonably well (MSE < 0.02)
4. n mod 16 shows some clustering (especially residues 8, 13, 15)
5. No simple linear interpolation

HYPOTHESIS: C(n) is constructed using:
- A base constant selected by n properties
- Perturbations based on n mod something
- Transitions between anchors using polynomial interpolation
"""

import math
import numpy as np
from puzzle_config import get_known_keys

# Mathematical constants
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LN2 = math.log(2)
SQRT2 = math.sqrt(2)

# Known anchors
ANCHORS = [
    (16, PI/4, "π/4"),
    (21, E/PI, "e/π"),
    (36, 1/PHI, "1/φ"),
    (48, E/4, "e/4"),
    (58, LN2, "ln(2)"),
    (61, PHI-1, "φ-1"),
    (90, 1/SQRT2, "1/√2"),
]

def construct_c_piecewise_poly(n):
    """
    Construct C(n) using piecewise polynomial interpolation.
    Between each pair of anchors, use cubic polynomial.
    """
    # Find which segment n falls into
    for i in range(len(ANCHORS) - 1):
        n_start, c_start, _ = ANCHORS[i]
        n_end, c_end, _ = ANCHORS[i+1]

        if n_start <= n <= n_end:
            # Use cubic Hermite spline (smooth interpolation)
            t = (n - n_start) / (n_end - n_start)

            # Hermite basis functions
            h00 = 2*t**3 - 3*t**2 + 1
            h10 = t**3 - 2*t**2 + t
            h01 = -2*t**3 + 3*t**2
            h11 = t**3 - t**2

            # Estimate derivatives (using finite differences from anchors)
            if i > 0:
                n_prev, c_prev, _ = ANCHORS[i-1]
                m_start = (c_start - c_prev) / (n_start - n_prev)
            else:
                m_start = 0

            if i < len(ANCHORS) - 2:
                n_next, c_next, _ = ANCHORS[i+2]
                m_end = (c_next - c_end) / (n_next - n_end)
            else:
                m_end = 0

            # Cubic Hermite interpolation
            c_value = h00 * c_start + h10 * (n_end - n_start) * m_start + \
                      h01 * c_end + h11 * (n_end - n_start) * m_end

            return c_value

    # Before first anchor or after last
    if n < ANCHORS[0][0]:
        # Extrapolate backward
        n0, c0, _ = ANCHORS[0]
        n1, c1, _ = ANCHORS[1]
        slope = (c1 - c0) / (n1 - n0)
        return c0 + slope * (n - n0)
    else:
        # Extrapolate forward
        n0, c0, _ = ANCHORS[-2]
        n1, c1, _ = ANCHORS[-1]
        slope = (c1 - c0) / (n1 - n0)
        return c1 + slope * (n - n1)

def construct_c_data_driven(n, keys):
    """
    Use actual data: fit polynomial in windows around n.
    """
    # Get a window of nearby n values
    window = []
    for n_key in keys:
        if abs(n_key - n) <= 10:
            k = keys[n_key]
            ratio = k / (2 ** n_key)
            window.append((n_key, ratio))

    if len(window) < 3:
        # Not enough data, use piecewise
        return construct_c_piecewise_poly(n)

    # Fit polynomial to window
    n_vals = np.array([w[0] for w in window])
    c_vals = np.array([w[1] for w in window])

    coeffs = np.polyfit(n_vals, c_vals, min(3, len(window)-1))
    c_value = np.polyval(coeffs, n)

    return c_value

def construct_c_hybrid(n, keys):
    """
    Hybrid approach: use data when available, piecewise when not.
    """
    if n in keys:
        # Exact value known
        return keys[n] / (2 ** n)

    # Check if we have nearby data
    nearby = [n_key for n_key in keys if abs(n_key - n) <= 5]

    if len(nearby) >= 3:
        return construct_c_data_driven(n, keys)
    else:
        return construct_c_piecewise_poly(n)

def test_c_construction():
    """Test different construction methods."""
    print("=" * 80)
    print("C(n) CONSTRUCTION TEST")
    print("=" * 80)

    keys = get_known_keys()

    methods = {
        "Piecewise Poly": construct_c_piecewise_poly,
        "Data-Driven": lambda n: construct_c_data_driven(n, keys),
        "Hybrid": lambda n: construct_c_hybrid(n, keys),
    }

    for method_name, method_func in methods.items():
        print(f"\n{method_name} Method:")
        print(f"{'n':>3} | {'Actual':>15} | {'Predicted':>15} | {'Error %':>8}")
        print("-" * 60)

        errors = []
        for n in sorted(keys.keys()):
            if n > 90:
                break

            actual = keys[n] / (2 ** n)
            predicted = method_func(n)

            error = abs(actual - predicted) / actual * 100
            errors.append(error)

            if n <= 20 or n in [36, 48, 58, 61, 90]:
                print(f"{n:3} | {actual:15.10f} | {predicted:15.10f} | {error:7.3f}%")

        print(f"\nAverage error: {np.mean(errors):.3f}%")
        print(f"Max error: {np.max(errors):.3f}%")
        print(f"Median error: {np.median(errors):.3f}%")

def predict_unsolved_k_values():
    """Use the best C(n) to predict unsolved puzzle keys."""
    print("\n" + "=" * 80)
    print("PREDICT UNSOLVED KEYS")
    print("=" * 80)

    keys = get_known_keys()

    # Use hybrid method (best performance)
    unsolved = [71, 72, 73, 74, 76, 77, 78, 79, 81, 82, 83, 84, 86, 87, 88, 89]

    print("\nPredictions for unsolved puzzles (71-89):")
    print(f"{'n':>3} | {'Predicted C(n)':>15} | {'Predicted k[n]':>25} | {'Range size':>15}")
    print("-" * 85)

    for n in unsolved:
        c_n = construct_c_hybrid(n, keys)
        k_n = int(c_n * (2 ** n))

        range_size = 2 ** (n - 1)

        print(f"{n:3} | {c_n:15.10f} | {k_n:25} | {range_size:15}")

def analyze_m_from_c():
    """Compute m[n] from C(n) formula."""
    print("\n" + "=" * 80)
    print("M[n] FROM C(n) FORMULA")
    print("=" * 80)

    keys = get_known_keys()

    print("\nUsing m[n] = 2^n (1 - C(n) + C(n-1)):")
    print(f"{'n':>3} | {'C(n)':>15} | {'C(n-1)':>15} | {'m[n] from C':>15} | {'Actual k[n]':>15}")
    print("-" * 85)

    # Start from n=2
    prev_c = construct_c_hybrid(1, keys)
    prev_k = keys.get(1, 0)

    for n in range(2, 21):
        c_n = construct_c_hybrid(n, keys)

        # m[n] = 2^n - k[n] + 2*k[n-1]
        # If k[n] = C(n) * 2^n, then:
        # m[n] = 2^n - C(n)*2^n + 2*C(n-1)*2^(n-1)
        #      = 2^n (1 - C(n) + C(n-1))

        factor = 1 - c_n + prev_c
        m_n = factor * (2 ** n)

        # From m[n], compute k[n]
        # k[n] = 2^n - m[n] + 2*k[n-1]
        k_n = (2 ** n) - m_n + 2 * prev_k

        actual_k = keys.get(n, 0)

        error = abs(k_n - actual_k) / actual_k * 100 if actual_k > 0 else 0

        print(f"{n:3} | {c_n:15.10f} | {prev_c:15.10f} | {m_n:15.0f} | {k_n:15.0f} ({error:.1f}%)")

        prev_c = c_n
        prev_k = actual_k  # Use actual to avoid error accumulation

def find_constant_selector_pattern():
    """
    Try to find the RULE for which constant at which n.
    """
    print("\n" + "=" * 80)
    print("CONSTANT SELECTOR PATTERN")
    print("=" * 80)

    anchor_positions = [16, 21, 36, 48, 58, 61, 90]

    print("\nAnalyzing anchor position differences:")
    diffs = [anchor_positions[i+1] - anchor_positions[i] for i in range(len(anchor_positions)-1)]
    print(f"Differences: {diffs}")

    # Try to find pattern in differences
    print("\nSecond differences:")
    second_diffs = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]
    print(f"{second_diffs}")

    # Check if differences follow a formula
    print("\nTrying to fit anchor positions:")

    # Test: n_i = f(i) for various functions
    indices = list(range(len(anchor_positions)))

    for formula_name, formula in [
        ("Linear: a*i + b", lambda i, a, b: a*i + b),
        ("Quadratic: a*i² + b*i + c", lambda i, a, b, c: a*i**2 + b*i + c),
        ("Exponential: a * exp(b*i) + c", lambda i, a, b, c: a * np.exp(b*i) + c),
    ]:
        print(f"\n{formula_name}:")

        if formula_name.startswith("Linear"):
            from scipy.optimize import curve_fit
            try:
                params, _ = curve_fit(formula, indices, anchor_positions)
                predicted = [formula(i, *params) for i in indices]
                errors = [abs(p - a) for p, a in zip(predicted, anchor_positions)]
                print(f"  Params: {params}")
                print(f"  Max error: {max(errors):.2f}")
                print(f"  Predicted: {[int(p) for p in predicted]}")
                print(f"  Actual: {anchor_positions}")
            except:
                print("  Fit failed")

        elif formula_name.startswith("Quadratic"):
            coeffs = np.polyfit(indices, anchor_positions, 2)
            predicted = np.polyval(coeffs, indices)
            errors = [abs(p - a) for p, a in zip(predicted, anchor_positions)]
            print(f"  Coefficients: {coeffs}")
            print(f"  Max error: {max(errors):.2f}")
            print(f"  Predicted: {[int(p) for p in predicted]}")
            print(f"  Actual: {anchor_positions}")

        else:
            from scipy.optimize import curve_fit
            try:
                params, _ = curve_fit(formula, indices, anchor_positions, p0=[1, 0.5, 10], maxfev=10000)
                predicted = [formula(i, *params) for i in indices]
                errors = [abs(p - a) for p, a in zip(predicted, anchor_positions)]
                print(f"  Params: {params}")
                print(f"  Max error: {max(errors):.2f}")
                print(f"  Predicted: {[int(p) for p in predicted]}")
                print(f"  Actual: {anchor_positions}")
            except:
                print("  Fit failed")

    # Manual pattern check
    print("\n\nManual pattern analysis:")
    print("Could the anchors be: powers of 2 ± small adjustments?")
    for pos in anchor_positions:
        # Find nearest power of 2
        log2 = math.log2(pos)
        nearest_pow = 2 ** round(log2)
        diff = pos - nearest_pow

        # Also check nearest 2^k ± 2^j
        candidates = []
        for k in range(1, 8):
            for j in range(k):
                candidates.append(2**k + 2**j)
                candidates.append(2**k - 2**j)

        matches = [c for c in candidates if c == pos]

        print(f"  n={pos:2}: 2^{log2:.2f} = {nearest_pow}, diff={diff:+3}, matches={matches}")

if __name__ == "__main__":
    test_c_construction()
    predict_unsolved_k_values()
    analyze_m_from_c()
    find_constant_selector_pattern()

    print("\n" + "=" * 80)
    print("CONSTRUCTION COMPLETE")
    print("=" * 80)
