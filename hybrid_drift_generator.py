#!/usr/bin/env python3
"""
Hybrid Drift Generator
======================

Combines H4 recursive patterns (70.5% accuracy) with extrapolation for lanes 0-6.

Strategy:
- Lanes 7-15: Use H4 affine recurrence (82-100% accuracy)
- Lanes 0-6: Use linear extrapolation + validation against bridges

This approach leverages proven patterns where they work and supplements
with statistical methods for remaining lanes.
"""

import json
import csv
import numpy as np
from pathlib import Path

def load_calibration():
    """Load calibration file"""
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        return json.load(f)

def load_A_values():
    """Load A values from calibration"""
    calib = load_calibration()
    return [calib['A'][str(i)] for i in range(16)]

def extract_drift_sequences():
    """Extract drift sequences from calibration"""
    calib = load_calibration()
    drift_sequences = {lane: [] for lane in range(16)}
    drifts_data = calib.get('drifts', {})

    for k in range(1, 70):
        transition_key = f"{k}→{k+1}"
        if transition_key in drifts_data:
            drift_data = drifts_data[transition_key]
            for lane in range(16):
                drift_sequences[lane].append(drift_data[str(lane)])

    return drift_sequences

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

# H4 Affine Recurrence Parameters (from research)
H4_AFFINE_PARAMS = {
    7: {'A': 23, 'C': 0, 'accuracy': 0.824},
    8: {'A': 1, 'C': 0, 'accuracy': 0.926},
    9: {'A': 1, 'C': 0, 'accuracy': 1.0},
    10: {'A': 1, 'C': 0, 'accuracy': 1.0},
    11: {'A': 1, 'C': 0, 'accuracy': 1.0},
    12: {'A': 1, 'C': 0, 'accuracy': 1.0},
    13: {'A': 1, 'C': 0, 'accuracy': 1.0},
    14: {'A': 1, 'C': 0, 'accuracy': 1.0},
    15: {'A': 1, 'C': 0, 'accuracy': 1.0},
}

def predict_drift_h4_affine(lane, last_drift):
    """Predict drift using H4 affine recurrence"""
    if lane not in H4_AFFINE_PARAMS:
        return None

    params = H4_AFFINE_PARAMS[lane]
    A = params['A']
    C = params['C']

    if A == 1 and C == 0:
        # Constant
        return last_drift
    else:
        # Affine recurrence
        return (A * last_drift + C) % 256

def predict_drift_linear(drift_sequence):
    """Predict next drift using linear extrapolation"""
    if len(drift_sequence) < 2:
        return drift_sequence[-1] if drift_sequence else 0

    x = np.arange(len(drift_sequence))
    y = np.array(drift_sequence)
    coeffs = np.polyfit(x, y, 1)
    next_x = len(drift_sequence)
    return int(coeffs[0] * next_x + coeffs[1]) % 256

def generate_hybrid_drift(k, drift_sequences, last_drifts=None):
    """
    Generate drift for transition k→k+1 using hybrid approach

    Args:
        k: Current puzzle number
        drift_sequences: Historical drift sequences (1-70)
        last_drifts: Last computed drift values (for recurrence)

    Returns:
        List of 16 drift values
    """
    drift = []

    for lane in range(16):
        if lane in H4_AFFINE_PARAMS:
            # Use H4 affine recurrence (lanes 7-15)
            if last_drifts and lane < len(last_drifts):
                predicted = predict_drift_h4_affine(lane, last_drifts[lane])
            else:
                # No last drift - use last known value
                seq = drift_sequences[lane]
                predicted = seq[-1] if seq else 0

            drift.append(predicted)
        else:
            # Use linear extrapolation (lanes 0-6)
            seq = drift_sequences[lane]
            predicted = predict_drift_linear(seq)
            drift.append(predicted)

    return drift

def validate_with_bridge(X_start, drift_sequence, A, X_target, steps=5):
    """
    Validate drift sequence by calculating forward and comparing to target

    Args:
        X_start: Starting halfblock
        drift_sequence: List of drift vectors (one per step)
        A: A values
        X_target: Target halfblock to match
        steps: Number of steps

    Returns:
        (accuracy, matches, X_calculated)
    """
    current = X_start

    for i in range(steps):
        drift = drift_sequence[i] if i < len(drift_sequence) else drift_sequence[-1]
        next_block = []
        for lane in range(16):
            a4 = pow(A[lane], 4, 256)
            next_val = (a4 * current[lane] + drift[lane]) % 256
            next_block.append(next_val)
        current = next_block

    matches = sum(1 for i in range(16) if current[i] == X_target[i])
    accuracy = 100 * matches / 16

    return accuracy, matches, current

def test_hybrid_generator():
    """Test hybrid drift generator on bridges"""

    print("=" * 80)
    print("HYBRID DRIFT GENERATOR TEST")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    A = load_A_values()
    drift_sequences = extract_drift_sequences()

    print(f"A values: {A}")
    print(f"Loaded drift for 69 transitions")
    print()

    # Test on bridge 70→75
    print("=" * 80)
    print("TEST: Generate drift for 70→75 and validate")
    print("=" * 80)
    print()

    X_70 = load_puzzle(70)
    X_75 = load_puzzle(75)

    if not X_70 or not X_75:
        print("ERROR: Cannot load puzzles 70 or 75")
        return

    print(f"X_70: {bytes_to_hex(X_70)}")
    print(f"X_75 (target): {bytes_to_hex(X_75)}")
    print()

    # Generate drift for 70→71, 71→72, ..., 74→75
    generated_drifts = []
    last_drift = [drift_sequences[i][-1] for i in range(16)]  # Start with drift[69→70]

    for k in range(70, 75):
        drift = generate_hybrid_drift(k, drift_sequences, last_drift)
        generated_drifts.append(drift)
        last_drift = drift
        print(f"drift[{k}→{k+1}]: {drift}")

    print()

    # Validate
    accuracy, matches, X_75_calc = validate_with_bridge(X_70, generated_drifts, A, X_75, steps=5)

    print("Validation Results:")
    print(f"Calculated X_75: {bytes_to_hex(X_75_calc)}")
    print(f"Target X_75:     {bytes_to_hex(X_75)}")
    print(f"Accuracy: {matches}/16 ({accuracy:.1f}%)")
    print()

    # Lane-by-lane comparison
    print("Lane | Calculated | Target | Match? | Method")
    print("-" * 60)
    for lane in range(16):
        calc = X_75_calc[lane]
        target = X_75[lane]
        match = "✓" if calc == target else "✗"
        method = "H4 affine" if lane in H4_AFFINE_PARAMS else "Linear extrap"
        print(f"{lane:4} | {calc:10} | {target:6} | {match:6} | {method}")

    print()

    # Summary
    if accuracy == 100.0:
        print("🎉 PERFECT! Hybrid generator works!")
    elif accuracy >= 80.0:
        print(f"👍 Good! {accuracy:.1f}% accuracy - refinement may achieve 100%")
    elif accuracy >= 50.0:
        print(f"⚠️  Moderate {accuracy:.1f}% - needs more work")
    else:
        print(f"❌ Low {accuracy:.1f}% - different approach needed")

    # Save results
    results = {
        'method': 'hybrid',
        'h4_lanes': list(H4_AFFINE_PARAMS.keys()),
        'linear_lanes': [i for i in range(16) if i not in H4_AFFINE_PARAMS],
        'test_bridge': '70→75',
        'X_70': bytes_to_hex(X_70),
        'X_75_target': bytes_to_hex(X_75),
        'X_75_calculated': bytes_to_hex(X_75_calc),
        'generated_drifts': [
            {f'drift_{70+i}_{71+i}': drift}
            for i, drift in enumerate(generated_drifts)
        ],
        'accuracy': accuracy,
        'matches': matches,
        'per_lane_accuracy': {
            str(lane): {
                'calculated': X_75_calc[lane],
                'target': X_75[lane],
                'match': X_75_calc[lane] == X_75[lane],
                'method': 'H4_affine' if lane in H4_AFFINE_PARAMS else 'linear_extrap'
            }
            for lane in range(16)
        }
    }

    with open('results/hybrid_drift_generator_test.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print("Results saved to: results/hybrid_drift_generator_test.json")
    print()

if __name__ == '__main__':
    test_hybrid_generator()
