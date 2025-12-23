#!/usr/bin/env python3
"""
Generate puzzles 126-130 using special drift for Lane 0

Discovery: Lane 0 requires drift=171 for transitions 125→130
"""

import json
import csv
from pathlib import Path

# Constants
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

def halfblock_to_bytes(hex_str):
    """Convert hex to 16 bytes (REVERSED)"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    hex_str = hex_str[-32:].zfill(32)
    return bytes.fromhex(hex_str)[::-1]

def bytes_to_halfblock(data):
    """Convert 16 bytes to 64-hex half-block string (REVERSED)"""
    return '0x' + data[::-1].hex().zfill(32) + '0' * 32

def calculate_next_X_with_drift(X_k_bytes, drift_vector):
    """X_{k+1} = (X_k^n + drift) mod 256"""
    result = bytearray(16)
    for lane in range(16):
        x = X_k_bytes[lane]
        n = EXPONENTS[lane]
        d = drift_vector[lane]

        # Special case for lane 6 (n=0): if x=0 and drift=0, stay at 0
        if n == 0 and x == 0 and d == 0:
            result[lane] = 0
        else:
            result[lane] = (pow(x, n, 256) + d) % 256
    return bytes(result)

def main():
    print("="*70)
    print("GENERATE PUZZLES 126-130 (Special Drift)")
    print("="*70)
    print("\nLane 0: drift=171")
    print("All other lanes: drift=0\n")

    # Load CSV
    csv_file = Path('data/btc_puzzle_1_160_full.csv')
    puzzles = {}
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['key_hex'] != '?':
                puzzles[int(row['puzzle'])] = row['key_hex_64']

    # Start from puzzle 125
    X_125 = halfblock_to_bytes(puzzles[125])
    print(f"Starting from puzzle 125:")
    print(f"  X_125 = {bytes_to_halfblock(X_125)[:18]}...\n")

    # Drift vector: Lane 0 = 171, all others = 0
    drift_vector = [171] + [0] * 15

    generated_puzzles = {}
    X_current = X_125

    for k in range(125, 130):
        X_current = calculate_next_X_with_drift(X_current, drift_vector)
        puzzle_num = k + 1
        generated_puzzles[puzzle_num] = {
            'puzzle': puzzle_num,
            'X_k_hex': bytes_to_halfblock(X_current),
            'generated': True,
            'method': 'drift_lane_0_171'
        }
        print(f"  Puzzle {puzzle_num}: {bytes_to_halfblock(X_current)[:18]}...")

    # Verify against CSV
    print(f"\nVerification:")
    matches = 0
    total = 0
    for k in generated_puzzles:
        if k in puzzles:
            X_gen = halfblock_to_bytes(generated_puzzles[k]['X_k_hex'])
            X_csv = halfblock_to_bytes(puzzles[k])
            total += 1
            if X_gen == X_csv:
                matches += 1
                print(f"  Puzzle {k}: ✅ MATCH")
            else:
                print(f"  Puzzle {k}: ❌ MISMATCH")

    print(f"\n{'='*70}")
    if matches == total and total > 0:
        print(f"✅ ALL {total} puzzles VERIFIED!")

        # Update the main generated file
        main_file = Path('generated_intermediate_puzzles.json')
        if main_file.exists():
            with open(main_file) as f:
                data = json.load(f)

            # Add 126-129 (130 is already known)
            for k in [126, 127, 128, 129]:
                data['puzzles'][str(k)] = generated_puzzles[k]

            data['puzzles_generated'] = len(data['puzzles'])
            data['special_drift_126_130'] = {
                'lane_0_drift': 171,
                'other_lanes_drift': 0
            }

            with open(main_file, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"✓ Updated {main_file}")
            print(f"  Total intermediate puzzles: {len(data['puzzles'])}")
    else:
        print(f"❌ FAILED: {matches}/{total}")

    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
