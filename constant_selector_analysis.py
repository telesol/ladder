#!/usr/bin/env python3
"""
CONSTANT SELECTOR RULE DISCOVERY

Analyze how k[n]/2^n maps to mathematical constants.
Find the pattern that determines WHICH constant at WHICH n.
"""

import math
from typing import Dict, List, Tuple
from puzzle_config import get_known_keys

# Mathematical constants
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LN2 = math.log(2)
SQRT2 = math.sqrt(2)

# Known anchor points: (n, constant_value, constant_name)
ANCHORS = [
    (16, PI/4, "π/4"),
    (21, E/PI, "e/π"),
    (36, 1/PHI, "1/φ"),
    (48, E/4, "e/4"),
    (58, LN2, "ln(2)"),
    (61, PHI-1, "φ-1"),
    (90, 1/SQRT2, "1/√2"),
]

def analyze_anchor_spacing():
    """Analyze the pattern in anchor positions."""
    print("=" * 80)
    print("ANCHOR POSITION ANALYSIS")
    print("=" * 80)

    positions = [a[0] for a in ANCHORS]
    print(f"\nAnchor positions: {positions}")

    # Differences between consecutive anchors
    diffs = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
    print(f"Differences: {diffs}")

    # Check if they're prime
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    print(f"\nPrime check:")
    for p in positions:
        print(f"  {p}: {'PRIME' if is_prime(p) else 'composite'}")

    # Check Fibonacci relationship
    fib = [1, 1]
    while fib[-1] < max(positions):
        fib.append(fib[-1] + fib[-2])

    print(f"\nFibonacci numbers up to {max(positions)}: {[f for f in fib if f <= max(positions)]}")

    # Check if differences are Fibonacci
    print(f"\nDifferences vs Fibonacci:")
    for d in diffs:
        if d in fib:
            print(f"  {d}: IN Fibonacci sequence!")
        else:
            print(f"  {d}: not in Fibonacci")

    # Check modular patterns
    print(f"\nModular patterns:")
    for mod in [2, 3, 5, 7, 11, 13]:
        residues = [p % mod for p in positions]
        print(f"  mod {mod}: {residues}")

    # Check if positions follow a formula
    print(f"\nTrying polynomial fits:")
    import numpy as np
    x = np.arange(len(positions))
    y = np.array(positions)

    for degree in [1, 2, 3]:
        coeffs = np.polyfit(x, y, degree)
        fitted = np.polyval(coeffs, x)
        error = np.abs(y - fitted).max()
        print(f"  Degree {degree}: max error = {error:.2f}")
        if error < 1:
            print(f"    Coefficients: {coeffs}")

def compute_ratio_at_n(n: int, k: int) -> float:
    """Compute k[n] / 2^n"""
    return k / (2 ** n)

def find_closest_constant(ratio: float) -> Tuple[str, float, float]:
    """Find which constant is closest to the given ratio."""
    constants = {
        "π/4": PI/4,
        "π/8": PI/8,
        "e/π": E/PI,
        "e/4": E/4,
        "e/8": E/8,
        "1/e": 1/E,
        "1/π": 1/PI,
        "1/φ": 1/PHI,
        "φ-1": PHI-1,
        "1/(φ²)": 1/(PHI**2),
        "ln(2)": LN2,
        "ln(π)": math.log(PI),
        "ln(e)": 1.0,
        "1/√2": 1/SQRT2,
        "√2/2": SQRT2/2,
        "1/√3": 1/math.sqrt(3),
        "1/√5": 1/math.sqrt(5),
        "φ/π": PHI/PI,
        "e/φ": E/PHI,
        "π/e": PI/E,
    }

    best_name = None
    best_value = None
    best_error = float('inf')

    for name, value in constants.items():
        error = abs((ratio - value) / value) * 100  # % error
        if error < best_error:
            best_error = error
            best_name = name
            best_value = value

    return best_name, best_value, best_error

def analyze_all_ratios():
    """Analyze k[n]/2^n for all known keys."""
    print("\n" + "=" * 80)
    print("RATIO ANALYSIS FOR ALL KNOWN KEYS")
    print("=" * 80)

    keys = get_known_keys()
    anchor_dict = {n: (const, name) for n, const, name in ANCHORS}

    print(f"\n{'n':>3} | {'k[n]':>20} | {'k[n]/2^n':>15} | {'Closest Const':>12} | {'Error %':>8}")
    print("-" * 80)

    for n in sorted(keys.keys()):
        if n > 90:  # Focus on n <= 90 for now
            break

        k = keys[n]
        ratio = compute_ratio_at_n(n, k)

        if n in anchor_dict:
            const_val, const_name = anchor_dict[n]
            error = abs((ratio - const_val) / const_val) * 100
            print(f"{n:3} | {k:20} | {ratio:15.10f} | {const_name:>12} | {error:7.3f}% *")
        else:
            name, value, error = find_closest_constant(ratio)
            print(f"{n:3} | {k:20} | {ratio:15.10f} | {name:>12} | {error:7.3f}%")

def analyze_interpolation():
    """Check if values between anchors follow interpolation."""
    print("\n" + "=" * 80)
    print("INTERPOLATION ANALYSIS BETWEEN ANCHORS")
    print("=" * 80)

    keys = get_known_keys()

    for i in range(len(ANCHORS) - 1):
        n1, c1, name1 = ANCHORS[i]
        n2, c2, name2 = ANCHORS[i+1]

        print(f"\nBetween n={n1} ({name1}={c1:.6f}) and n={n2} ({name2}={c2:.6f}):")

        # Get all n values in between
        between = [n for n in sorted(keys.keys()) if n1 < n < n2]

        if not between:
            print("  No intermediate values in database")
            continue

        print(f"  Intermediate n values: {between}")

        # Test linear interpolation in ratio space
        print(f"\n  {'n':>3} | {'Actual ratio':>15} | {'Linear interp':>15} | {'Error %':>8}")
        print("  " + "-" * 60)

        for n in between:
            k = keys[n]
            actual_ratio = compute_ratio_at_n(n, k)

            # Linear interpolation in ratio space
            t = (n - n1) / (n2 - n1)  # Parameter from 0 to 1
            interp_ratio = c1 + t * (c2 - c1)

            error = abs((actual_ratio - interp_ratio) / actual_ratio) * 100
            print(f"  {n:3} | {actual_ratio:15.10f} | {interp_ratio:15.10f} | {error:7.3f}%")

def analyze_sequence_properties():
    """Analyze the sequence of constants used."""
    print("\n" + "=" * 80)
    print("CONSTANT SEQUENCE PROPERTIES")
    print("=" * 80)

    print("\nConstants in order:")
    for n, c, name in ANCHORS:
        print(f"  n={n:2}: {name:8} = {c:.10f}")

    # Check ratios between consecutive constants
    print("\nRatios between consecutive constants:")
    for i in range(len(ANCHORS) - 1):
        n1, c1, name1 = ANCHORS[i]
        n2, c2, name2 = ANCHORS[i+1]
        ratio = c2 / c1
        print(f"  {name2}/{name1} = {ratio:.6f}")

    # Check if constants relate to each other
    print("\nRelationships between constants:")
    consts = [c for _, c, _ in ANCHORS]

    # Check products
    for i in range(len(consts)):
        for j in range(i+1, len(consts)):
            prod = consts[i] * consts[j]
            # Check if product is close to another constant
            for k, (_, c, name) in enumerate(ANCHORS):
                if k != i and k != j:
                    if abs(prod - c) / c < 0.01:  # Within 1%
                        print(f"  {ANCHORS[i][2]} × {ANCHORS[j][2]} ≈ {name}")

def analyze_m_sequence():
    """Analyze m[n] = 2^n - k[n] + 2*k[n-1] using constant ratios."""
    print("\n" + "=" * 80)
    print("M-SEQUENCE RECONSTRUCTION FROM CONSTANT RULE")
    print("=" * 80)

    keys = get_known_keys()

    print("\nIf k[n] = C(n) * 2^n, then:")
    print("m[n] = 2^n - k[n] + 2*k[n-1]")
    print("     = 2^n - C(n)*2^n + 2*C(n-1)*2^(n-1)")
    print("     = 2^n(1 - C(n) + C(n-1))")
    print("     = 2^n(1 - C(n) + C(n-1))")

    print(f"\n{'n':>3} | {'C(n)':>15} | {'C(n-1)':>15} | {'1-C(n)+C(n-1)':>18} | {'m[n] computed':>15}")
    print("-" * 85)

    prev_k = 0
    for n in sorted(keys.keys()):
        if n > 20:  # Just show first 20
            break

        k = keys[n]
        c_n = k / (2 ** n)

        if n > 1:
            c_n_minus_1 = prev_k / (2 ** (n-1))
            factor = 1 - c_n + c_n_minus_1
            m_n = factor * (2 ** n)
            print(f"{n:3} | {c_n:15.10f} | {c_n_minus_1:15.10f} | {factor:18.10f} | {m_n:15.0f}")
        else:
            print(f"{n:3} | {c_n:15.10f} | {'---':>15} | {'---':>18} | {'---':>15}")

        prev_k = k

def test_construction_hypothesis():
    """Test if we can construct the sequence using a simple rule."""
    print("\n" + "=" * 80)
    print("CONSTRUCTION HYPOTHESIS TEST")
    print("=" * 80)

    print("\nHypothesis: C(n) is selected based on n properties")
    print("Testing various selection rules...")

    positions = [16, 21, 36, 48, 58, 61, 90]

    # Test: Is it based on digital root?
    print("\nDigital root analysis:")
    for p in positions:
        dr = p
        while dr >= 10:
            dr = sum(int(d) for d in str(dr))
        print(f"  n={p}: digital root = {dr}")

    # Test: Is it based on sum of prime factors?
    print("\nPrime factorization:")
    for p in positions:
        n = p
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        print(f"  n={p}: {factors}, sum={sum(factors)}")

    # Test: Is it based on n mod some number?
    print("\nChecking if anchor positions have special mod properties:")
    for mod in [7, 8, 9, 10, 12, 13, 16]:
        residues = [p % mod for p in positions]
        unique_residues = len(set(residues))
        print(f"  mod {mod}: {residues} ({unique_residues} unique)")

if __name__ == "__main__":
    # Run all analyses
    analyze_anchor_spacing()
    analyze_all_ratios()
    analyze_interpolation()
    analyze_sequence_properties()
    analyze_m_sequence()
    test_construction_hypothesis()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
