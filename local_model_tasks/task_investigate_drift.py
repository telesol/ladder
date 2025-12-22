#!/usr/bin/env python3
"""
LOCAL MODEL TASK: Investigate Drift Patterns
==============================================

This task can run on local models (Qwen, Phi4) or Python directly.

Goal: Analyze drift patterns from calibration data to see if they can be predicted.

This is COMPUTATION, not reasoning - perfect for local models!
"""

import json
import numpy as np
from pathlib import Path

def load_calibration():
    """Load the corrected calibration file"""
    # Try multiple locations
    possible_paths = [
        Path('out/ladder_calib_CORRECTED.json'),
        Path('experiments/05-ai-learns-ladder/out/ladder_calib_CORRECTED.json'),
        Path('out/ladder_calib_1_70_complete.json')
    ]

    for calib_path in possible_paths:
        if calib_path.exists():
            print(f"  Found calibration: {calib_path}")
            with open(calib_path, 'r') as f:
                return json.load(f)

    raise FileNotFoundError("Could not find calibration file in any expected location")

def extract_drift_sequence():
    """Extract the sequence of drift values for each transition"""
    calib = load_calibration()

    # Structure: calib['drifts'] has transitions like '1→2', '2→3', ..., '69→70'
    drift_sequences = {lane: [] for lane in range(16)}

    drifts_data = calib.get('drifts', {})

    # Extract drift for each transition
    for k in range(1, 70):
        # Try both arrow formats
        transition_key = f"{k}→{k+1}"
        if transition_key not in drifts_data:
            transition_key = f"{k}_to_{k+1}"

        if transition_key in drifts_data:
            drift_data = drifts_data[transition_key]
            for lane in range(16):
                lane_key = str(lane)
                if lane_key in drift_data:
                    drift_sequences[lane].append(drift_data[lane_key])

    return drift_sequences

def analyze_drift_patterns(drift_sequences):
    """Analyze patterns in drift sequences"""

    print("=" * 80)
    print("DRIFT PATTERN ANALYSIS")
    print("=" * 80)
    print()

    for lane in range(16):
        sequence = drift_sequences[lane]
        if not sequence:
            continue

        print(f"Lane {lane}:")
        print(f"  Length: {len(sequence)}")
        print(f"  First 10: {sequence[:10]}")
        print(f"  Last 10: {sequence[-10:]}")
        print(f"  Min: {min(sequence)}, Max: {max(sequence)}")
        print(f"  Mean: {np.mean(sequence):.2f}, Std: {np.std(sequence):.2f}")

        # Check for patterns
        # 1. Is it constant?
        if len(set(sequence)) == 1:
            print(f"  → CONSTANT: Always {sequence[0]}")

        # 2. Is it periodic?
        for period in [2, 3, 4, 5, 10]:
            is_periodic = all(sequence[i] == sequence[i % period] for i in range(len(sequence)))
            if is_periodic:
                print(f"  → PERIODIC with period {period}")
                break

        # 3. Linear trend?
        if len(sequence) > 1:
            x = np.arange(len(sequence))
            y = np.array(sequence)
            coeffs = np.polyfit(x, y, 1)
            trend = coeffs[0]
            if abs(trend) > 0.1:
                print(f"  → LINEAR TREND: {trend:.4f} per step")

        # 4. Autocorrelation
        if len(sequence) > 10:
            autocorr = np.corrcoef(sequence[:-1], sequence[1:])[0, 1]
            print(f"  → AUTOCORRELATION: {autocorr:.4f}")

        print()

def predict_next_drift_simple(drift_sequences, lane):
    """Simple prediction: last value, mean, or linear extrapolation"""
    sequence = drift_sequences[lane]

    if not sequence:
        return None

    predictions = {}

    # Method 1: Last value
    predictions['last_value'] = sequence[-1]

    # Method 2: Mean
    predictions['mean'] = int(np.mean(sequence))

    # Method 3: Linear extrapolation
    if len(sequence) > 1:
        x = np.arange(len(sequence))
        y = np.array(sequence)
        coeffs = np.polyfit(x, y, 1)
        next_x = len(sequence)
        predictions['linear_extrap'] = int(coeffs[0] * next_x + coeffs[1])

    # Method 4: Moving average
    if len(sequence) >= 5:
        predictions['moving_avg_5'] = int(np.mean(sequence[-5:]))

    return predictions

def main():
    print("Loading calibration data...")
    calib = load_calibration()

    print("Extracting drift sequences...")
    drift_sequences = extract_drift_sequence()

    print(f"Found drift data for {len([s for s in drift_sequences.values() if s])} lanes")
    print()

    # Analyze patterns
    analyze_drift_patterns(drift_sequences)

    # Predict drift[70→71] for each lane
    print("=" * 80)
    print("PREDICTING DRIFT[70→71]")
    print("=" * 80)
    print()

    predicted_drift_70_71 = {}

    for lane in range(16):
        predictions = predict_next_drift_simple(drift_sequences, lane)
        if predictions:
            print(f"Lane {lane}: {predictions}")
            predicted_drift_70_71[lane] = predictions

    print()

    # Save predictions
    output_file = 'results/predicted_drift_70_71.json'
    with open(output_file, 'w') as f:
        json.dump(predicted_drift_70_71, f, indent=2)

    print(f"Predictions saved to: {output_file}")
    print()

    # Next step: Test these predictions!
    print("=" * 80)
    print("NEXT STEP:")
    print("=" * 80)
    print()
    print("Run: python3 local_model_tasks/test_drift_predictions.py")
    print("This will test if predicted drift values can generate X_71 from X_70")
    print()

if __name__ == '__main__':
    main()
