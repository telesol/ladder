#!/usr/bin/env python3
"""
CRITICAL TEST: Generate 71-75 with CORRECT Byte Order
======================================================

Now that we know the correct byte order (REVERSED), let's test:
1. Can we generate drift for 70→71 using H4 affine recurrence?
2. Does it match bridge 75 when calculated forward?

This tests if the "pattern shift at 70" was real or our mistake.
"""

import json
import csv

def load_A_values():
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        calib = json.load(f)
    return [calib['A'][str(i)] for i in range(16)]

def hex_to_bytes_reversed(hex_str):
    """CORRECT byte extraction method"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    if len(hex_str) > 32:
        hex_str = hex_str[32:64]
    hex_str = hex_str.zfill(32)
    return [int(hex_str[i:i+2], 16) for i in range(30, -1, -2)]

def bytes_to_hex_reversed(byte_list):
    """Convert reversed bytes back to hex"""
    # Reverse the bytes back
    return ''.join(f'{byte_list[15-i]:02x}' for i in range(16))

def load_puzzle(n):
    with open('data/btc_puzzle_1_160_full.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[0] == str(n) and row[3] and row[3] != '?':
                return row[3]
    return None

def extract_drift_sequences_reversed():
    """Extract drift sequences with CORRECT byte order"""
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        calib = json.load(f)

    drift_sequences = {lane: [] for lane in range(16)}
    drifts_data = calib.get('drifts', {})

    for k in range(1, 70):
        drift_key = f"{k}→{k+1}"
        if drift_key in drifts_data:
            for lane in range(16):
                drift_sequences[lane].append(drifts_data[drift_key][str(lane)])

    return drift_sequences

# H4 Affine Parameters (from research - but these were with WRONG byte order!)
# Need to re-analyze with correct order, but let's try first
H4_AFFINE = {
    0: {'A': 10, 'C': 163},
    1: {'A': 120, 'C': 0},
    2: {'A': 2, 'C': 0},
    3: {'A': 7, 'C': 0},
    4: {'A': 31, 'C': 0},
    5: {'A': 178, 'C': 0},
    6: {'A': 5, 'C': 0},
    7: {'A': 23, 'C': 0},
    8: {'A': 1, 'C': 0},
    9: {'A': 1, 'C': 0},
    10: {'A': 1, 'C': 0},
    11: {'A': 1, 'C': 0},
    12: {'A': 1, 'C': 0},
    13: {'A': 1, 'C': 0},
    14: {'A': 1, 'C': 0},
    15: {'A': 1, 'C': 0},
}

def generate_drift_h4(last_drift, lane):
    """Generate next drift using H4 affine recurrence"""
    params = H4_AFFINE[lane]
    A = params['A']
    C = params['C']
    return (A * last_drift + C) % 256

def calculate_next(X_k, A, drift):
    """Calculate X_{k+1} from X_k"""
    X_next = []
    for lane in range(16):
        a4 = pow(A[lane], 4, 256)
        x_next = (a4 * X_k[lane] + drift[lane]) % 256
        X_next.append(x_next)
    return X_next

def test_generation_70_to_75():
    print("=" * 80)
    print("TESTING GENERATION 70→75 WITH CORRECT BYTE ORDER")
    print("=" * 80)
    print()

    A = load_A_values()
    drift_sequences = extract_drift_sequences_reversed()

    # Load X_70 and X_75
    X_70_hex = load_puzzle(70)
    X_75_hex = load_puzzle(75)

    X_70 = hex_to_bytes_reversed(X_70_hex)
    X_75_target = hex_to_bytes_reversed(X_75_hex)

    print(f"X_70 (correct order): {X_70}")
    print(f"X_75 target (correct order): {X_75_target}")
    print()

    # Generate drift for 70→71, 71→72, ..., 74→75 using H4
    print("Generating drift using H4 affine recurrence...")
    print()

    current_X = X_70
    last_drift = [drift_sequences[lane][-1] for lane in range(16)]  # drift[69→70]

    for step in range(5):
        k = 70 + step

        # Generate drift for k→k+1
        drift = []
        for lane in range(16):
            d = generate_drift_h4(last_drift[lane], lane)
            drift.append(d)

        print(f"drift[{k}→{k+1}]: {drift}")

        # Calculate X_{k+1}
        current_X = calculate_next(current_X, A, drift)
        last_drift = drift

    X_75_calc = current_X

    print()
    print("=" * 80)
    print("RESULT")
    print("=" * 80)
    print()

    print(f"Calculated X_75: {X_75_calc}")
    print(f"Target X_75:     {X_75_target}")
    print()

    matches = sum(1 for i in range(16) if X_75_calc[i] == X_75_target[i])
    accuracy = matches / 16 * 100

    print(f"Matches: {matches}/16 ({accuracy:.1f}%)")
    print()

    # Lane-by-lane
    print("Lane | Calculated | Target | Match?")
    print("-" * 50)
    for lane in range(16):
        calc = X_75_calc[lane]
        target = X_75_target[lane]
        match = "✓" if calc == target else "✗"
        print(f"{lane:4} | {calc:10} | {target:6} | {match}")

    print()

    if accuracy == 100.0:
        print("🎉🎉🎉 PERFECT! Can generate 71-75!")
        print("The 'pattern shift at 70' was our byte order mistake!")
    elif accuracy >= 80.0:
        print(f"👍 {accuracy:.1f}% - very close! H4 parameters may need adjustment")
    else:
        print(f"⚠️  {accuracy:.1f}% - H4 parameters from wrong byte order don't work")
        print("Need to re-run H4 research with correct byte order!")

if __name__ == '__main__':
    test_generation_70_to_75()
