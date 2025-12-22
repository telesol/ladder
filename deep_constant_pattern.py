#!/usr/bin/env python3
"""
DEEP PATTERN ANALYSIS

The linear interpolation FAILS badly (20-35% error).
This means there's a NON-LINEAR rule governing C(n).

Key observation from anchor sequence:
π/4 × e/π ≈ e/4

Let's explore:
1. Trigonometric patterns
2. Exponential decay/growth
3. Modular arithmetic on n
4. Composite functions
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

def analyze_oscillation_pattern():
    """Check if C(n) oscillates in a predictable way."""
    print("=" * 80)
    print("OSCILLATION PATTERN ANALYSIS")
    print("=" * 80)

    keys = get_known_keys()

    # Compute ratios for all n
    ratios = {}
    for n in sorted(keys.keys()):
        if n <= 90:
            k = keys[n]
            ratios[n] = k / (2 ** n)

    # Look at second differences to detect patterns
    n_vals = sorted(ratios.keys())
    first_diff = [ratios[n_vals[i+1]] - ratios[n_vals[i]] for i in range(len(n_vals)-1)]
    second_diff = [first_diff[i+1] - first_diff[i] for i in range(len(first_diff)-1)]

    print("\nFirst 20 second differences:")
    for i in range(min(20, len(second_diff))):
        print(f"  n={n_vals[i+2]:2}: Δ²C = {second_diff[i]:+.10f}")

    # Check for periodicity in sign changes
    print("\nSign pattern of C(n):")
    sign_pattern = []
    for n in n_vals[:30]:
        if ratios[n] > 0.7:
            sign_pattern.append('H')  # High
        elif ratios[n] < 0.6:
            sign_pattern.append('L')  # Low
        else:
            sign_pattern.append('M')  # Medium

    print("  " + "".join(sign_pattern))

    # Check if pattern repeats
    for period in [2, 3, 4, 5, 6, 7, 8, 9, 10, 12]:
        repeats = True
        for i in range(period, min(len(sign_pattern), 30)):
            if sign_pattern[i] != sign_pattern[i % period]:
                repeats = False
                break
        if repeats:
            print(f"\n  Pattern repeats with period {period}!")

def analyze_modular_formula():
    """Test if C(n) is determined by n mod something."""
    print("\n" + "=" * 80)
    print("MODULAR FORMULA TEST")
    print("=" * 80)

    keys = get_known_keys()

    # Group by n mod various values
    for modulus in [5, 7, 8, 10, 12, 13, 16]:
        print(f"\nn mod {modulus}:")

        buckets = {i: [] for i in range(modulus)}
        for n in sorted(keys.keys()):
            if n <= 90:
                k = keys[n]
                ratio = k / (2 ** n)
                buckets[n % modulus].append((n, ratio))

        # Check if ratios are similar within each bucket
        for remainder in range(modulus):
            if buckets[remainder]:
                vals = [r for _, r in buckets[remainder]]
                mean = np.mean(vals)
                std = np.std(vals)
                n_list = [n for n, _ in buckets[remainder][:5]]  # First 5
                print(f"  {remainder}: mean={mean:.4f}, std={std:.4f}, n={n_list}...")

                # Highlight if std is very low (suggests strong pattern)
                if std < 0.05 and len(vals) > 3:
                    print(f"      *** LOW VARIANCE - POSSIBLE PATTERN! ***")

def analyze_trigonometric_pattern():
    """Test if C(n) follows sin/cos patterns."""
    print("\n" + "=" * 80)
    print("TRIGONOMETRIC PATTERN TEST")
    print("=" * 80)

    keys = get_known_keys()

    # Test various trig formulas
    print("\nTesting C(n) = a + b*sin(c*n + d):")

    n_vals = []
    c_vals = []
    for n in sorted(keys.keys()):
        if 1 <= n <= 90:
            k = keys[n]
            ratio = k / (2 ** n)
            n_vals.append(n)
            c_vals.append(ratio)

    n_arr = np.array(n_vals)
    c_arr = np.array(c_vals)

    # Try different frequencies
    for freq in [PI/16, PI/12, PI/10, PI/8, PI/7, PI/6, PI/5]:
        # Fit: C(n) = a + b*sin(freq*n + phase)
        # Using least squares to find a, b, phase

        best_error = float('inf')
        best_params = None

        for phase in np.linspace(0, 2*PI, 20):
            sin_vals = np.sin(freq * n_arr + phase)

            # Solve for a, b using least squares
            A = np.column_stack([np.ones_like(sin_vals), sin_vals])
            params, _, _, _ = np.linalg.lstsq(A, c_arr, rcond=None)

            a, b = params
            predicted = a + b * np.sin(freq * n_arr + phase)
            error = np.mean((c_arr - predicted) ** 2)

            if error < best_error:
                best_error = error
                best_params = (a, b, phase)

        a, b, phase = best_params
        print(f"  freq={freq:.4f}: a={a:.4f}, b={b:.4f}, phase={phase:.4f}, MSE={best_error:.6f}")

def analyze_piecewise_functions():
    """Check if different formulas apply in different n ranges."""
    print("\n" + "=" * 80)
    print("PIECEWISE FUNCTION ANALYSIS")
    print("=" * 80)

    keys = get_known_keys()

    # Define ranges between anchors
    ranges = []
    for i in range(len(ANCHORS) - 1):
        n_start = ANCHORS[i][0]
        n_end = ANCHORS[i+1][0]
        ranges.append((n_start, n_end, ANCHORS[i][2], ANCHORS[i+1][2]))

    for n_start, n_end, name_start, name_end in ranges:
        print(f"\nRange [{n_start}, {n_end}] ({name_start} → {name_end}):")

        # Get all n in this range
        n_vals = []
        c_vals = []
        for n in sorted(keys.keys()):
            if n_start <= n <= n_end:
                k = keys[n]
                ratio = k / (2 ** n)
                n_vals.append(n)
                c_vals.append(ratio)

        if len(n_vals) < 3:
            print("  Too few points for analysis")
            continue

        n_arr = np.array(n_vals)
        c_arr = np.array(c_vals)

        # Test polynomial fit
        for degree in [2, 3]:
            coeffs = np.polyfit(n_arr, c_arr, degree)
            predicted = np.polyval(coeffs, n_arr)
            mse = np.mean((c_arr - predicted) ** 2)
            print(f"  Poly degree {degree}: MSE={mse:.6f}")

        # Test exponential fit: C(n) = a * exp(b*n) + c
        from scipy.optimize import curve_fit

        def exp_model(n, a, b, c):
            return a * np.exp(b * n) + c

        try:
            params, _ = curve_fit(exp_model, n_arr, c_arr, p0=[1, -0.01, 0.5], maxfev=5000)
            predicted = exp_model(n_arr, *params)
            mse = np.mean((c_arr - predicted) ** 2)
            print(f"  Exponential: a={params[0]:.4f}, b={params[1]:.6f}, c={params[2]:.4f}, MSE={mse:.6f}")
        except:
            print("  Exponential fit failed")

def analyze_number_theoretic_properties():
    """Check if anchors relate to number-theoretic properties of n."""
    print("\n" + "=" * 80)
    print("NUMBER THEORETIC PROPERTIES OF ANCHORS")
    print("=" * 80)

    anchor_positions = [16, 21, 36, 48, 58, 61, 90]

    # Check sum of divisors
    def sum_of_divisors(n):
        divisors = [i for i in range(1, n+1) if n % i == 0]
        return sum(divisors)

    # Check number of divisors
    def num_divisors(n):
        return len([i for i in range(1, n+1) if n % i == 0])

    # Check Euler's totient
    def euler_phi(n):
        count = 0
        for i in range(1, n+1):
            if math.gcd(i, n) == 1:
                count += 1
        return count

    print(f"\n{'n':>3} | {'σ(n)':>6} | {'τ(n)':>6} | {'φ(n)':>6} | {'n-φ(n)':>6} | {'σ(n)/n':>8}")
    print("-" * 60)

    for n in anchor_positions:
        sigma = sum_of_divisors(n)
        tau = num_divisors(n)
        phi = euler_phi(n)
        print(f"{n:3} | {sigma:6} | {tau:6} | {phi:6} | {n-phi:6} | {sigma/n:8.4f}")

    # Check if there's a pattern in σ(n)/n or φ(n)
    ratios = [sum_of_divisors(n)/n for n in anchor_positions]
    print(f"\nσ(n)/n ratios: {[f'{r:.4f}' for r in ratios]}")

    phis = [euler_phi(n) for n in anchor_positions]
    print(f"φ(n) values: {phis}")

def analyze_constant_relationships():
    """Deeply analyze how the constants relate to each other."""
    print("\n" + "=" * 80)
    print("CONSTANT RELATIONSHIP ANALYSIS")
    print("=" * 80)

    constants = {
        "π/4": PI/4,
        "e/π": E/PI,
        "1/φ": 1/PHI,
        "e/4": E/4,
        "ln(2)": LN2,
        "φ-1": PHI-1,
        "1/√2": 1/SQRT2,
    }

    # Check all pairwise products, sums, differences
    names = list(constants.keys())
    vals = list(constants.values())

    print("\nProducts that equal other constants (within 1%):")
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            prod = vals[i] * vals[j]
            for k, (name_k, val_k) in enumerate(constants.items()):
                if k != i and k != j:
                    error = abs(prod - val_k) / val_k
                    if error < 0.01:
                        print(f"  {names[i]:8} × {names[j]:8} = {prod:.6f} ≈ {name_k:8} ({error*100:.2f}% error)")

    print("\nRatios that equal other constants (within 1%):")
    for i in range(len(names)):
        for j in range(len(names)):
            if i != j:
                ratio = vals[i] / vals[j]
                for k, (name_k, val_k) in enumerate(constants.items()):
                    if k != i and k != j:
                        error = abs(ratio - val_k) / val_k
                        if error < 0.01:
                            print(f"  {names[i]:8} / {names[j]:8} = {ratio:.6f} ≈ {name_k:8} ({error*100:.2f}% error)")

    print("\nSums/differences that equal other constants (within 1%):")
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            total = vals[i] + vals[j]
            diff = abs(vals[i] - vals[j])

            for k, (name_k, val_k) in enumerate(constants.items()):
                if k != i and k != j:
                    error_sum = abs(total - val_k) / val_k
                    error_diff = abs(diff - val_k) / val_k

                    if error_sum < 0.01:
                        print(f"  {names[i]:8} + {names[j]:8} = {total:.6f} ≈ {name_k:8} ({error_sum*100:.2f}% error)")
                    if error_diff < 0.01:
                        print(f"  |{names[i]:8} - {names[j]:8}| = {diff:.6f} ≈ {name_k:8} ({error_diff*100:.2f}% error)")

def test_convergent_hypothesis():
    """Test if C(n) uses convergents of mathematical constants."""
    print("\n" + "=" * 80)
    print("CONVERGENT HYPOTHESIS TEST")
    print("=" * 80)

    print("\nConvergents are rational approximations p/q of constants.")
    print("Maybe C(n) cycles through convergents of π, e, φ, etc.")

    # Get convergents of π
    def get_convergents(value, max_q=1000):
        """Get continued fraction convergents."""
        convergents = []
        a = int(value)
        convergents.append((a, 1))

        p_prev, q_prev = a, 1
        p_pprev, q_pprev = 1, 0

        remainder = value - a
        for _ in range(20):  # Max 20 iterations
            if abs(remainder) < 1e-10:
                break

            remainder = 1 / remainder
            a = int(remainder)

            p = a * p_prev + p_pprev
            q = a * q_prev + q_pprev

            if q > max_q:
                break

            convergents.append((p, q))

            p_pprev, q_pprev = p_prev, q_prev
            p_prev, q_prev = p, q

            remainder = remainder - a

        return convergents

    print("\nConvergents of π:")
    pi_conv = get_convergents(PI, 1000)
    for p, q in pi_conv[:15]:
        print(f"  {p}/{q} = {p/q:.10f} (error: {abs(p/q - PI)/PI * 100:.4f}%)")

    print("\nConvergents of e:")
    e_conv = get_convergents(E, 1000)
    for p, q in e_conv[:15]:
        print(f"  {p}/{q} = {p/q:.10f} (error: {abs(p/q - E)/E * 100:.4f}%)")

    print("\nConvergents of φ:")
    phi_conv = get_convergents(PHI, 1000)
    for p, q in phi_conv[:15]:
        print(f"  {p}/{q} = {p/q:.10f} (error: {abs(p/q - PHI)/PHI * 100:.4f}%)")

    # Check if anchor constants match convergents
    print("\n\nChecking if anchor constants use convergents:")
    all_convergents = []
    for name, value in [("π", PI), ("e", E), ("φ", PHI), ("√2", SQRT2)]:
        convs = get_convergents(value, 1000)
        for p, q in convs:
            all_convergents.append((p, q, p/q, name))

    # Check each anchor constant
    for n, const_val, const_name in ANCHORS:
        print(f"\n{const_name} = {const_val:.10f}:")
        matches = []
        for p, q, ratio, base_const in all_convergents:
            # Check direct match
            if abs(ratio - const_val) / const_val < 0.001:
                matches.append(f"  {p}/{q} of {base_const}")
            # Check inverse match
            if abs(1/ratio - const_val) / const_val < 0.001:
                matches.append(f"  1/({p}/{q}) of {base_const}")
            # Check scaled match
            for scale in [2, 4, 8]:
                if abs(ratio/scale - const_val) / const_val < 0.001:
                    matches.append(f"  ({p}/{q})/{scale} of {base_const}")

        if matches:
            for m in matches[:5]:  # Show first 5 matches
                print(m)
        else:
            print("  No convergent matches found")

if __name__ == "__main__":
    analyze_oscillation_pattern()
    analyze_modular_formula()
    analyze_trigonometric_pattern()
    analyze_piecewise_functions()
    analyze_number_theoretic_properties()
    analyze_constant_relationships()
    test_convergent_hypothesis()

    print("\n" + "=" * 80)
    print("DEEP ANALYSIS COMPLETE")
    print("=" * 80)
