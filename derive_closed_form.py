#!/usr/bin/env python3
"""
Derive Closed-Form Generation Formula
======================================

**THE BIG ONE!**

Attempt to derive a closed-form formula for k_n using eigenvalue decomposition:

    k_n = c_0×λ_0^n + c_1×λ_1^n + c_2×λ_2^n + c_3×λ_3^n + c_4×λ_4^n

where:
- λ_j = 2^(1/5) × e^(2πij/5) are the eigenvalues
- c_j are coefficients determined from initial conditions k_1 to k_5

If this works → WE FOUND THE SOURCE MATH!
"""

import numpy as np
import csv
import json
from pathlib import Path

def hex_to_int(hex_str):
    """Convert hex string to integer"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    return int(hex_str, 16)

def load_k_values_from_csv():
    """Load k-values from the CSV file"""
    csv_path = Path('data/btc_puzzle_1_160_full.csv')
    k_values = {}

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 4:
                puzzle_num = int(row[0])
                priv_hex = row[3]  # Private key in hex
                # Skip unsolved puzzles (marked with '?')
                if priv_hex and priv_hex != '?' and not priv_hex.startswith('?'):
                    try:
                        k_values[puzzle_num] = hex_to_int(priv_hex)
                    except ValueError:
                        # Skip invalid entries
                        pass

    return k_values

def compute_eigenvalues():
    """Compute the eigenvalues: 2^(1/5) × ω^j"""
    eigenvalues = []
    base = 2**(1/5)

    for j in range(5):
        omega = np.exp(2j * np.pi * 1j / 5)
        lambda_j = base * omega
        eigenvalues.append(lambda_j)

    return np.array(eigenvalues)

def solve_for_coefficients(k_values, eigenvalues):
    """
    Solve for coefficients c_j using initial conditions k_1 to k_5.

    System of equations:
    k_n = c_0×λ_0^n + c_1×λ_1^n + c_2×λ_2^n + c_3×λ_3^n + c_4×λ_4^n

    For n = 1, 2, 3, 4, 5:
    [λ_0^1  λ_1^1  λ_2^1  λ_3^1  λ_4^1] [c_0]   [k_1]
    [λ_0^2  λ_1^2  λ_2^2  λ_3^2  λ_4^2] [c_1] = [k_2]
    [λ_0^3  λ_1^3  λ_2^3  λ_3^3  λ_4^3] [c_2]   [k_3]
    [λ_0^4  λ_1^4  λ_2^4  λ_3^4  λ_4^4] [c_3]   [k_4]
    [λ_0^5  λ_1^5  λ_2^5  λ_3^5  λ_4^5] [c_4]   [k_5]
    """
    # Build the Vandermonde-like matrix
    A = np.zeros((5, 5), dtype=complex)
    b = np.zeros(5, dtype=complex)

    for n in range(1, 6):
        for j in range(5):
            A[n-1, j] = eigenvalues[j]**n
        b[n-1] = k_values[n]

    # Solve the system
    c = np.linalg.solve(A, b)

    return c

def predict_k_n(n, coefficients, eigenvalues):
    """Predict k_n using the closed-form formula"""
    result = sum(c * (lam**n) for c, lam in zip(coefficients, eigenvalues))
    return result

def main():
    print("=" * 70)
    print("CLOSED-FORM FORMULA DERIVATION")
    print("=" * 70)
    print()
    print("**THE BIG TEST!**")
    print()
    print("Can we express k_n as:")
    print("  k_n = c_0×λ_0^n + c_1×λ_1^n + c_2×λ_2^n + c_3×λ_3^n + c_4×λ_4^n")
    print()
    print("If YES → WE FOUND THE SOURCE MATH!")
    print()

    # Load k-values
    print("Loading k-values from CSV...")
    k_values = load_k_values_from_csv()
    print(f"Loaded {len(k_values)} k-values")
    print()

    # Compute eigenvalues
    print("Computing eigenvalues...")
    eigenvalues = compute_eigenvalues()
    print("Eigenvalues (λ_j = 2^(1/5) × e^(2πij/5)):")
    for j, lam in enumerate(eigenvalues):
        print(f"  λ_{j} = {lam.real:+.6f}{lam.imag:+.6f}i    |λ_{j}| = {abs(lam):.6f}")
    print()

    # Solve for coefficients
    print("Solving for coefficients using k_1 to k_5...")
    print()
    print("Initial conditions:")
    for n in range(1, 6):
        print(f"  k_{n} = {k_values[n]}")
    print()

    coefficients = solve_for_coefficients(k_values, eigenvalues)

    print("Computed coefficients:")
    for j, c in enumerate(coefficients):
        print(f"  c_{j} = {c.real:+.6f}{c.imag:+.6f}i    |c_{j}| = {abs(c):.6f}")
    print()

    # Validate on training data (k_1 to k_5)
    print("=" * 70)
    print("VALIDATION ON TRAINING DATA (k_1 to k_5):")
    print("=" * 70)
    print()
    print("n    k_n (actual)              k_n (predicted)           Error")
    print("-" * 75)

    training_errors = []
    for n in range(1, 6):
        actual = k_values[n]
        predicted = predict_k_n(n, coefficients, eigenvalues)

        # The prediction should be real (imaginary part should cancel)
        predicted_real = predicted.real
        error = abs(predicted_real - actual)
        rel_error = error / actual if actual != 0 else 0

        training_errors.append(error)

        print(f"{n}    {actual:<25} {predicted_real:<25.2f} {error:.2e}")

    print()
    print(f"Max training error: {max(training_errors):.2e}")
    print()

    # Test on validation data (k_6 to k_70)
    print("=" * 70)
    print("PREDICTION ON VALIDATION DATA (k_6 to k_70):")
    print("=" * 70)
    print()

    validation_errors = []
    accurate_predictions = 0
    total_predictions = 0

    print("n    k_n (actual)              k_n (predicted)           Abs Error         Rel Error")
    print("-" * 100)

    for n in range(6, 71):
        if n not in k_values:
            continue

        actual = k_values[n]
        predicted = predict_k_n(n, coefficients, eigenvalues)
        predicted_real = predicted.real

        error = abs(predicted_real - actual)
        rel_error = error / actual if actual != 0 else 0

        validation_errors.append(error)
        total_predictions += 1

        # Consider accurate if relative error < 1%
        if rel_error < 0.01:
            accurate_predictions += 1
            status = "✓"
        else:
            status = "✗"

        # Print first 20 and any large errors
        if n <= 25 or rel_error > 0.01:
            print(f"{n}    {actual:<25} {predicted_real:<25.2f} {error:< 15.2e}   {rel_error:.2%}  {status}")

    if total_predictions > 25:
        print(f"... ({total_predictions - 25} more predictions)")

    print()

    # Summary statistics
    print("=" * 70)
    print("PREDICTION STATISTICS:")
    print("=" * 70)
    print()
    print(f"Total predictions: {total_predictions}")
    print(f"Accurate predictions (rel error < 1%): {accurate_predictions}")
    print(f"Accuracy rate: {100 * accurate_predictions / total_predictions:.2f}%")
    print()
    print(f"Max absolute error: {max(validation_errors):.2e}")
    print(f"Mean absolute error: {np.mean(validation_errors):.2e}")
    print(f"Median absolute error: {np.median(validation_errors):.2e}")
    print()

    # Check if formula works
    print("=" * 70)
    print("FINAL VERDICT:")
    print("=" * 70)
    print()

    accuracy_rate = accurate_predictions / total_predictions

    if accuracy_rate >= 0.99:
        print("🎉🎉🎉 BREAKTHROUGH! 🎉🎉🎉")
        print()
        print("✅ The closed-form eigenvalue formula works with >99% accuracy!")
        print("✅ WE FOUND THE SOURCE MATH!")
        print()
        print("The ladder CAN be generated using pure eigenvalue decomposition:")
        print("  k_n = c_0×λ_0^n + c_1×λ_1^n + c_2×λ_2^n + c_3×λ_3^n + c_4×λ_4^n")
        print()
        print("This is the fundamental mathematical structure!")
    elif accuracy_rate >= 0.80:
        print("👍 VERY PROMISING!")
        print()
        print("✓ The eigenvalue formula shows high correlation (>80%)")
        print("✓ The Period-5 structure is real!")
        print()
        print("However, there are systematic deviations. Possible reasons:")
        print("  • Inhomogeneous terms (2^n - m×k_d - r) need separate treatment")
        print("  • Need to use particular solution + homogeneous solution")
        print("  • Integer rounding effects")
    else:
        print("❌ Pure eigenvalue formula does NOT work.")
        print()
        print("The recurrence has inhomogeneous terms that prevent")
        print("simple eigenvalue decomposition.")
        print()
        print("Next steps:")
        print("  • Account for forcing terms (2^n - m×k_d - r)")
        print("  • Use full solution: homogeneous + particular")
        print("  • Investigate m-value structure")

    print()

    # Save results
    results = {
        'eigenvalues': [{'real': lam.real, 'imag': lam.imag} for lam in eigenvalues],
        'coefficients': [{'real': c.real, 'imag': c.imag} for c in coefficients],
        'accuracy_rate': float(accuracy_rate),
        'max_error': float(max(validation_errors)),
        'mean_error': float(np.mean(validation_errors)),
        'total_predictions': total_predictions,
        'accurate_predictions': accurate_predictions
    }

    with open('closed_form_derivation_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Results saved to: closed_form_derivation_results.json")

if __name__ == '__main__':
    main()
