#!/usr/bin/env python3
"""
Validate Drift Predictions on Bridge Points
============================================

Test drift prediction methods on transitions where we have KNOWN ground truth:
- 75→76→77→78→79→80 (we know X_75 and X_80)

This validates which drift prediction strategy works best.
"""

import json
import csv
import numpy as np
from pathlib import Path

def load_A_values():
    """Load A values from calibration"""
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        calib = json.load(f)
    return [calib['A'][str(i)] for i in range(16)]

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

def extract_drift_sequence():
    """Extract drift sequences from calibration"""
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        calib = json.load(f)

    drift_sequences = {lane: [] for lane in range(16)}
    drifts_data = calib.get('drifts', {})

    for k in range(1, 70):
        transition_key = f"{k}→{k+1}"
        if transition_key in drifts_data:
            drift_data = drifts_data[transition_key]
            for lane in range(16):
                drift_sequences[lane].append(drift_data[str(lane)])

    return drift_sequences

def predict_drift(drift_sequences, method='mean'):
    """Predict next drift value using specified method"""
    predicted_drift = []

    for lane in range(16):
        sequence = drift_sequences[lane]

        if not sequence:
            predicted_drift.append(0)
            continue

        if method == 'last_value':
            predicted_drift.append(sequence[-1])
        elif method == 'mean':
            predicted_drift.append(int(np.mean(sequence)))
        elif method == 'linear_extrap':
            if len(sequence) > 1:
                x = np.arange(len(sequence))
                y = np.array(sequence)
                coeffs = np.polyfit(x, y, 1)
                next_x = len(sequence)
                predicted_drift.append(int(coeffs[0] * next_x + coeffs[1]))
            else:
                predicted_drift.append(sequence[-1])
        elif method == 'moving_avg_5':
            if len(sequence) >= 5:
                predicted_drift.append(int(np.mean(sequence[-5:])))
            else:
                predicted_drift.append(int(np.mean(sequence)))
        else:
            predicted_drift.append(0)

    return predicted_drift

def calculate_with_drift(X_k, A, drift):
    """Calculate X_{k+1} using affine model with drift"""
    X_next = []
    for lane in range(16):
        a4 = pow(A[lane], 4, 256)
        x_next = (a4 * X_k[lane] + drift[lane]) % 256
        X_next.append(x_next)
    return X_next

def multi_step_calculate(X_start, A, drift, steps=5):
    """Calculate multiple steps forward using same drift"""
    current = X_start
    for _ in range(steps):
        current = calculate_with_drift(current, A, drift)
    return current

def test_bridge_75_80():
    """Test drift predictions on 75→80 bridge"""

    print("=" * 80)
    print("VALIDATING DRIFT PREDICTIONS ON BRIDGES")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    A = load_A_values()
    drift_sequences = extract_drift_sequence()
    X_75 = load_puzzle(75)
    X_80 = load_puzzle(80)

    if not X_75 or not X_80:
        print("ERROR: Cannot load bridge puzzles 75 or 80")
        return

    print(f"A values: {A}")
    print(f"X_75: {bytes_to_hex(X_75)}")
    print(f"X_80 (target): {bytes_to_hex(X_80)}")
    print()

    # Test each prediction method
    methods = ['last_value', 'mean', 'linear_extrap', 'moving_avg_5']
    results = {}

    for method in methods:
        print("=" * 80)
        print(f"METHOD: {method}")
        print("=" * 80)
        print()

        # Predict drift for transitions 70→71
        drift = predict_drift(drift_sequences, method)
        print(f"Predicted drift: {drift}")
        print()

        # Calculate X_80 from X_75 (5 steps)
        X_80_calculated = multi_step_calculate(X_75, A, drift, steps=5)

        print(f"Calculated X_80: {bytes_to_hex(X_80_calculated)}")
        print(f"Actual X_80:     {bytes_to_hex(X_80)}")
        print()

        # Compare
        matches = sum(1 for i in range(16) if X_80_calculated[i] == X_80[i])
        accuracy = 100 * matches / 16

        print(f"Accuracy: {matches}/16 ({accuracy:.1f}%)")
        print()

        # Lane-by-lane comparison
        print("Lane | Calculated | Actual | Match?")
        print("-" * 50)
        for lane in range(16):
            calc = X_80_calculated[lane]
            actual = X_80[lane]
            match = "✓" if calc == actual else "✗"
            print(f"{lane:4} | {calc:10} | {actual:6} | {match}")

        print()

        results[method] = {
            'drift': drift,
            'calculated': X_80_calculated,
            'actual': X_80,
            'accuracy': accuracy,
            'matches': matches
        }

    # Summary
    print("=" * 80)
    print("SUMMARY - BRIDGE 75→80 VALIDATION")
    print("=" * 80)
    print()

    for method, result in results.items():
        print(f"{method:20}: {result['accuracy']:.1f}% ({result['matches']}/16)")

    print()

    # Find best method
    best_method = max(results.items(), key=lambda x: x[1]['accuracy'])
    print(f"Best method: {best_method[0]} ({best_method[1]['accuracy']:.1f}%)")
    print()

    if best_method[1]['accuracy'] == 100.0:
        print("🎉 PERFECT! This drift prediction method works!")
    elif best_method[1]['accuracy'] >= 80.0:
        print("👍 Good accuracy! Refinement may achieve 100%")
    elif best_method[1]['accuracy'] >= 50.0:
        print("⚠️  Moderate accuracy. More sophisticated prediction needed.")
    else:
        print("❌ Low accuracy. Need different drift prediction approach.")

    # Save results
    output = {
        'bridge': '75→80',
        'X_75': bytes_to_hex(X_75),
        'X_80_actual': bytes_to_hex(X_80),
        'drift_methods_tested': {
            method: {
                'X_80_calculated': bytes_to_hex(res['calculated']),
                'drift_used': res['drift'],
                'accuracy': res['accuracy'],
                'matches': res['matches']
            }
            for method, res in results.items()
        },
        'best_method': best_method[0],
        'best_accuracy': best_method[1]['accuracy']
    }

    with open('results/bridge_75_80_validation.json', 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print("Results saved to: results/bridge_75_80_validation.json")
    print()

if __name__ == '__main__':
    test_bridge_75_80()
