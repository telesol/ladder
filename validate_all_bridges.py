#!/usr/bin/env python3
"""
Validate X_k formula on ALL available bridges

We have bridges at: 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130
Goal: Validate our X_k formula can correctly compute these bridges
"""

import json
import csv
from pathlib import Path

# Constants
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

def halfblock_to_bytes(hex_str):
    """Convert 64-hex half-block to 16 bytes (REVERSED byte order)"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    # Take first 32 hex chars, pad if needed
    hex_str = hex_str[:32].zfill(32)
    # Convert to bytes and REVERSE
    return bytes.fromhex(hex_str)[::-1]

def bytes_to_halfblock(data):
    """Convert 16 bytes to 64-hex half-block string (REVERSED)"""
    # Reverse bytes, convert to hex, pad to 32 hex chars, append 32 zeros
    return '0x' + data[::-1].hex().zfill(32) + '0' * 32

def calculate_next_X(X_k_bytes, drift_bytes):
    """Calculate X_{k+1} = (X_k^n + drift) mod 256 for all lanes"""
    result = bytearray(16)
    for lane in range(16):
        x = X_k_bytes[lane]
        d = drift_bytes[lane]
        n = EXPONENTS[lane]

        # Calculate x^n mod 256
        x_pow_n = pow(x, n, 256)

        # Add drift
        result[lane] = (x_pow_n + d) % 256

    return bytes(result)

def multi_step_calculate(X_start_bytes, transitions):
    """Calculate X through multiple transitions"""
    X_current = X_start_bytes

    for from_k, to_k, drift_bytes in transitions:
        X_current = calculate_next_X(X_current, drift_bytes)

    return X_current

def load_csv_data(csv_file):
    """Load puzzle data from CSV"""
    puzzles = {}
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            puzzle_id = int(row['puzzle'])
            puzzles[puzzle_id] = {
                'bits': int(row['bits']),
                'address': row['address'],
                'private_key': row['private_key']
            }
    return puzzles

def load_calibration(calib_file):
    """Load calibration drift data"""
    with open(calib_file) as f:
        calib = json.load(f)

    # Extract drift values (puzzles 1-70)
    drifts = {}
    for trans in calib.get('transitions', []):
        from_k = trans['from_puzzle']
        drift_values = trans['drifts']
        drifts[from_k] = drift_values

    return drifts

def main():
    print("="*70)
    print("BRIDGE VALIDATION: X_k Formula on Bridges 75-130")
    print("="*70)

    # Load data
    csv_file = Path('data/btc_puzzle_1_160_full.csv')
    calib_file = Path('drift_data_CORRECT_BYTE_ORDER.json')

    print(f"\nLoading CSV: {csv_file}")
    puzzles = load_csv_data(csv_file)
    print(f"✓ Loaded {len(puzzles)} puzzles")

    print(f"\nLoading calibration: {calib_file}")
    drifts = load_calibration(calib_file)
    print(f"✓ Loaded {len(drifts)} drift transitions (puzzles 1-69)")

    # Define bridges to validate
    bridges = [75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130]

    print(f"\n{'='*70}")
    print(f"VALIDATING {len(bridges)} BRIDGES")
    print(f"{'='*70}\n")

    results = []

    for bridge_k in bridges:
        if bridge_k not in puzzles:
            print(f"⚠️  Bridge {bridge_k}: Not in CSV")
            continue

        # Get actual key from CSV
        actual_key = puzzles[bridge_k]['private_key']
        actual_X = halfblock_to_bytes(actual_key)

        print(f"\n--- Bridge {bridge_k} ---")
        print(f"  Actual key: {actual_key[:34]}...")

        # Calculate from puzzle 70 using multi-step
        # We need drift values for transitions 70→71, 71→72, ..., up to bridge

        # For now, check if we can compute single-step from puzzle 70
        if bridge_k == 75:
            # Try 5-step calculation: 70→71→72→73→74→75
            X_70 = halfblock_to_bytes(puzzles[70]['private_key'])

            # We don't have drift for 70→71, 71→72, etc.
            # Can only validate if we extract drift from bridges themselves
            print(f"  ⚠️  Cannot calculate: Missing drift for 70→{bridge_k}")
            print(f"  Status: NEED DRIFT EXTRACTION")
        else:
            print(f"  ⚠️  Cannot calculate: Missing drift for 70→{bridge_k}")
            print(f"  Status: NEED DRIFT EXTRACTION")

        results.append({
            'bridge': bridge_k,
            'status': 'PENDING',
            'reason': 'Need drift extraction from bridges'
        })

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total bridges checked: {len(results)}")
    print(f"Status: NEED DRIFT EXTRACTION")
    print(f"\nNext step: Extract drift values FROM bridges themselves")
    print(f"  Method: drift = X_{{k+1}} - X_k^n (mod 256) for each lane")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
