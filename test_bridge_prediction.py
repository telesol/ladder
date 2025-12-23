#!/usr/bin/env python3
"""
Test Bridge Prediction: Can we predict drift to reach bridges?

Challenge: We have X_70, X_75, X_80, etc., but NOT X_71-74, X_76-79, etc.
Goal: Test if drift patterns from 1-70 can predict bridges 75-130

Methods to test:
1. Average drift per lane
2. H4 affine recurrence (70% accurate)
3. Pattern extrapolation
4. Neural network (if available)
"""

import json
import csv
import hashlib
from pathlib import Path

# Constants
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

def halfblock_to_bytes(hex_str):
    """Convert hex to 16 bytes (REVERSED)"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    hex_str = hex_str[:32].zfill(32)
    return bytes.fromhex(hex_str)[::-1]

def bytes_to_hex(data):
    """Convert 16 bytes to hex string"""
    return '0x' + data[::-1].hex().zfill(32)

def calculate_next_X(X_k_bytes, drift_bytes):
    """X_{k+1} = (X_k^n + drift) mod 256"""
    result = bytearray(16)
    for lane in range(16):
        x = X_k_bytes[lane]
        d = drift_bytes[lane]
        n = EXPONENTS[lane]
        x_pow_n = pow(x, n, 256)
        result[lane] = (x_pow_n + d) % 256
    return bytes(result)

def multi_step(X_start, drift_list):
    """Apply multiple drift transitions"""
    X_current = X_start
    for drift in drift_list:
        X_current = calculate_next_X(X_current, drift)
    return X_current

def compute_average_drift(calibration):
    """Method 1: Use average drift per lane"""
    lane_drifts = {lane: [] for lane in range(16)}

    for trans in calibration['transitions']:
        k = trans['from_puzzle']
        for lane in range(16):
            activation_k = lane * 8 if lane > 0 else 1
            if k >= activation_k:  # Evolution phase
                lane_drifts[lane].append(trans['drifts'][lane])

    # Compute average
    avg_drift = []
    for lane in range(16):
        if lane_drifts[lane]:
            avg = int(round(sum(lane_drifts[lane]) / len(lane_drifts[lane])))
        else:
            avg = 0
        avg_drift.append(avg)

    return avg_drift

def test_bridge(X_start, X_target, steps, drift_per_step, method_name):
    """Test if drift pattern can reach target in N steps"""
    # Apply drift for each step
    drifts = [drift_per_step for _ in range(steps)]
    X_predicted = multi_step(X_start, drifts)

    # Compare
    matches = sum(1 for i in range(16) if X_predicted[i] == X_target[i])
    accuracy = matches / 16

    return {
        'method': method_name,
        'matches': matches,
        'accuracy': accuracy,
        'predicted': X_predicted,
        'expected': X_target
    }

def main():
    print("="*70)
    print("BRIDGE PREDICTION TEST")
    print("="*70)

    # Load data
    csv_file = Path('data/btc_puzzle_1_160_full.csv')
    calib_file = Path('drift_data_CORRECT_BYTE_ORDER.json')

    print(f"\nLoading CSV: {csv_file}")
    puzzles = {}
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['key_hex'] != '?':
                puzzles[int(row['puzzle'])] = row['key_hex_64']
    print(f"✓ Loaded {len(puzzles)} known puzzles")

    print(f"\nLoading calibration: {calib_file}")
    with open(calib_file) as f:
        calibration = json.load(f)
    print(f"✓ Loaded {len(calibration['transitions'])} transitions")

    # Bridges to test
    bridges = [(70, 75), (75, 80), (80, 85), (85, 90), (90, 95),
               (95, 100), (100, 105), (105, 110), (110, 115),
               (115, 120), (120, 125), (125, 130)]

    print(f"\n{'='*70}")
    print(f"Testing {len(bridges)} bridge predictions")
    print(f"{'='*70}\n")

    # Method 1: Average drift
    avg_drift_bytes = bytes(compute_average_drift(calibration))
    print(f"Method 1: Average Drift")
    print(f"  Avg drift per lane: {list(avg_drift_bytes[:8])}...")

    results = []

    for start_k, end_k in bridges:
        if start_k not in puzzles or end_k not in puzzles:
            print(f"\n⚠️  Bridge {start_k}→{end_k}: Missing data")
            continue

        X_start = halfblock_to_bytes(puzzles[start_k])
        X_target = halfblock_to_bytes(puzzles[end_k])
        steps = end_k - start_k

        print(f"\n--- Bridge {start_k}→{end_k} ({steps} steps) ---")

        # Test method 1: Average drift
        result = test_bridge(X_start, X_target, steps, avg_drift_bytes, "Average Drift")
        results.append(result)

        print(f"  Average Drift: {result['matches']}/16 lanes = {result['accuracy']*100:.1f}%")

        # Show lane-by-lane for first bridge
        if start_k == 70:
            print(f"\n  Lane-by-lane comparison:")
            for lane in range(8):  # First 8 lanes
                pred = result['predicted'][lane]
                exp = result['expected'][lane]
                match = "✓" if pred == exp else "✗"
                print(f"    Lane {lane}: pred={pred:3d}, exp={exp:3d} {match}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    total = len(results)
    avg_accuracy = sum(r['accuracy'] for r in results) / total if total > 0 else 0

    print(f"Bridges tested: {total}")
    print(f"Average accuracy: {avg_accuracy*100:.1f}%")
    print(f"\nPer-bridge results:")
    for i, (start_k, end_k) in enumerate(bridges[:len(results)]):
        r = results[i]
        print(f"  {start_k}→{end_k}: {r['matches']}/16 = {r['accuracy']*100:.1f}%")

    if avg_accuracy >= 0.99:
        print(f"\n🎉 SUCCESS! Average drift predicts bridges with {avg_accuracy*100:.1f}% accuracy!")
        print(f"   This validates our X_k formula!")
    elif avg_accuracy >= 0.70:
        print(f"\n👍 PARTIAL SUCCESS! {avg_accuracy*100:.1f}% accuracy")
        print(f"   Formula is correct, but drift prediction needs refinement")
    else:
        print(f"\n❌ FAILED: Only {avg_accuracy*100:.1f}% accuracy")
        print(f"   Average drift does not work for bridge prediction")
        print(f"   Need better drift model or more data")

    print(f"\n{'='*70}")
    print("Next steps:")
    print("1. Try H4 affine recurrence for drift prediction")
    print("2. Try pattern extrapolation based on lane statistics")
    print("3. If all fail: Accept that bridges cannot be predicted")
    print("   (which is fine - it means drift is cryptographically secure)")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
