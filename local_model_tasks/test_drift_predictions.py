#!/usr/bin/env python3
"""
Test Drift Predictions
=======================

Test if predicted drift values can generate X_71 from X_70 using affine model.

Model: X_{k+1}[lane] = (A[lane]^4 * X_k[lane] + drift[lane]) mod 256
"""

import json
import csv
from pathlib import Path

def load_A_values():
    """Load A values from calibration"""
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        calib = json.load(f)
    return [calib['A'][str(i)] for i in range(16)]

def load_predictions():
    """Load predicted drift values"""
    with open('results/predicted_drift_70_71.json', 'r') as f:
        return json.load(f)

def hex_to_bytes(hex_str):
    """Convert hex string to byte list"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    if len(hex_str) > 32:
        hex_str = hex_str[32:64]
    hex_str = hex_str.zfill(32)
    return [int(hex_str[i:i+2], 16) for i in range(0, 32, 2)]

def bytes_to_hex(byte_list):
    """Convert byte list to hex string"""
    return ''.join(f'{b:02x}' for b in byte_list)

def load_puzzle(n):
    """Load puzzle from CSV"""
    with open('data/btc_puzzle_1_160_full.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[0] == str(n) and row[3] and row[3] != '?':
                return hex_to_bytes(row[3])
    return None

def calculate_with_drift(X_k, A, drift):
    """Calculate X_{k+1} using affine model with drift"""
    X_next = []
    for lane in range(16):
        a = A[lane]
        a4 = pow(a, 4, 256)
        x_k = X_k[lane]
        d = drift[lane]

        x_next = (a4 * x_k + d) % 256
        X_next.append(x_next)

    return X_next

def test_all_methods():
    """Test all 4 prediction methods"""

    print("=" * 80)
    print("TESTING DRIFT PREDICTIONS")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    A = load_A_values()
    predictions = load_predictions()
    X_70 = load_puzzle(70)
    X_71_actual = load_puzzle(71)

    print(f"A values: {A}")
    print(f"X_70: {bytes_to_hex(X_70)}")

    if X_71_actual:
        print(f"X_71 (actual): {bytes_to_hex(X_71_actual)}")
    else:
        print("X_71: UNKNOWN (not in CSV)")

    print()

    # Test each prediction method
    methods = ['last_value', 'mean', 'linear_extrap', 'moving_avg_5']

    results = {}

    for method in methods:
        print("=" * 80)
        print(f"METHOD: {method}")
        print("=" * 80)
        print()

        # Build drift vector from this method
        drift = []
        for lane in range(16):
            lane_predictions = predictions.get(str(lane), {})
            drift_value = lane_predictions.get(method, 0)
            drift.append(drift_value)

        print(f"Predicted drift: {drift}")
        print()

        # Calculate X_71 using this drift
        X_71_calculated = calculate_with_drift(X_70, A, drift)

        print(f"Calculated X_71: {bytes_to_hex(X_71_calculated)}")
        print()

        # Compare if X_71 is known
        if X_71_actual:
            matches = sum(1 for i in range(16) if X_71_calculated[i] == X_71_actual[i])
            accuracy = 100 * matches / 16

            print(f"Accuracy: {matches}/16 ({accuracy:.1f}%)")
            print()

            # Lane-by-lane comparison
            print("Lane | Calculated | Actual | Match?")
            print("-" * 50)
            for lane in range(16):
                calc = X_71_calculated[lane]
                actual = X_71_actual[lane]
                match = "✓" if calc == actual else "✗"
                print(f"{lane:4} | {calc:10} | {actual:6} | {match}")

            print()

            results[method] = {
                'drift': drift,
                'calculated': X_71_calculated,
                'accuracy': accuracy,
                'matches': matches
            }
        else:
            results[method] = {
                'drift': drift,
                'calculated': X_71_calculated,
                'accuracy': None,
                'matches': None
            }

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    if X_71_actual:
        for method, result in results.items():
            print(f"{method:20}: {result['accuracy']:.1f}% ({result['matches']}/16)")

        # Find best method
        best_method = max(results.items(), key=lambda x: x[1]['accuracy'] or 0)
        print()
        print(f"Best method: {best_method[0]} ({best_method[1]['accuracy']:.1f}%)")
        print()

        if best_method[1]['accuracy'] == 100.0:
            print("🎉 PERFECT! We can generate X_71 from X_70!")
        elif best_method[1]['accuracy'] >= 80.0:
            print("👍 Good accuracy! Refinement may achieve 100%")
        elif best_method[1]['accuracy'] >= 50.0:
            print("⚠️  Moderate accuracy. More sophisticated prediction needed.")
        else:
            print("❌ Low accuracy. Drift prediction approach may not work.")
    else:
        print("Cannot validate - X_71 is unknown")
        print("Showing calculated values for each method:")
        for method, result in results.items():
            print(f"{method}: {bytes_to_hex(result['calculated'])}")

    # Save results
    output = {
        'X_70': bytes_to_hex(X_70),
        'X_71_actual': bytes_to_hex(X_71_actual) if X_71_actual else None,
        'predictions_tested': {
            method: {
                'X_71_calculated': bytes_to_hex(res['calculated']),
                'drift_used': res['drift'],
                'accuracy': res['accuracy'],
                'matches': res['matches']
            }
            for method, res in results.items()
        }
    }

    with open('results/drift_prediction_test_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print("Results saved to: results/drift_prediction_test_results.json")

if __name__ == '__main__':
    test_all_methods()
