#!/usr/bin/env python3
"""
Debug validation issues.
"""

import json
import pandas as pd
from pathlib import Path


def load_data():
    """Load calibration and CSV data."""
    calib_path = Path(__file__).parent.parent.parent / "out" / "ladder_calib_ultimate.json"
    csv_path = Path(__file__).parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"

    with open(calib_path) as f:
        calib = json.load(f)

    df = pd.read_csv(csv_path)

    return calib, df


def debug_puzzle_1_to_2():
    """Debug puzzle 1→2 transition in detail."""
    calib, df = load_data()

    print("="*80)
    print("DEBUGGING PUZZLE 1→2")
    print("="*80)
    print()

    # Get keys from CSV
    puzzle_1 = df[df['puzzle'] == 1].iloc[0]
    puzzle_2 = df[df['puzzle'] == 2].iloc[0]

    key_1 = puzzle_1['key_hex_64']
    key_2 = puzzle_2['key_hex_64']
    address_2 = puzzle_2['address']

    print(f"Puzzle 1:")
    print(f"  Key: {key_1}")
    print(f"  Address: {puzzle_1['address']}")
    print()

    print(f"Puzzle 2:")
    print(f"  Key: {key_2}")
    print(f"  Address: {address_2}")
    print()

    # Get A coefficients
    A = [calib['A'][str(i)] for i in range(16)]
    print(f"A coefficients: {A}")
    print()

    # Get drift vector
    drift_key = "1→2"
    if drift_key in calib['drifts']:
        drift = [calib['drifts'][drift_key][str(i)] for i in range(16)]
        print(f"Drift (1→2): {drift}")
    else:
        print(f"❌ Drift not found for {drift_key}")
        return

    print()

    # Extract half-blocks
    print("Half-block analysis:")
    print()

    # Key 1 - last 16 bytes
    key_1_second_half = key_1[32:64]
    key_1_bytes = bytes.fromhex(key_1_second_half)
    key_1_halfblock = bytes(reversed(key_1_bytes))  # Little-endian

    print(f"Key 1 (second half):     {key_1_second_half}")
    print(f"Key 1 (little-endian):   {key_1_halfblock.hex()}")
    print(f"Key 1 (as bytes):        {[f'{b:02x}' for b in key_1_halfblock]}")
    print()

    # Key 2 - last 16 bytes
    key_2_second_half = key_2[32:64]
    key_2_bytes = bytes.fromhex(key_2_second_half)
    key_2_halfblock = bytes(reversed(key_2_bytes))  # Little-endian

    print(f"Key 2 (second half):     {key_2_second_half}")
    print(f"Key 2 (little-endian):   {key_2_halfblock.hex()}")
    print(f"Key 2 (as bytes):        {[f'{b:02x}' for b in key_2_halfblock]}")
    print()

    # Apply formula: X_{k+1} = A^4 * X_k + drift (mod 256)
    print("Applying formula: X_{k+1} = A^4 * X_k + drift (mod 256)")
    print()

    generated_halfblock = []
    for lane in range(16):
        A_val = A[lane]
        A4 = pow(A_val, 4, 256)

        X_k = key_1_halfblock[lane]
        drift_val = drift[lane]

        X_k_plus_1_expected = key_2_halfblock[lane]
        X_k_plus_1_generated = (A4 * X_k + drift_val) & 0xFF

        match = "✅" if X_k_plus_1_generated == X_k_plus_1_expected else "❌"

        print(f"  Lane {lane:2d}: A={A_val:3d}, A^4={A4:3d}, "
              f"X_k={X_k:3d} (0x{X_k:02x}), drift={drift_val:3d}, "
              f"expected={X_k_plus_1_expected:3d} (0x{X_k_plus_1_expected:02x}), "
              f"generated={X_k_plus_1_generated:3d} (0x{X_k_plus_1_generated:02x}) {match}")

        generated_halfblock.append(X_k_plus_1_generated)

    print()

    # Convert back to big-endian
    generated_halfblock_reversed = bytes(reversed(generated_halfblock))
    generated_key_2 = '0' * 32 + generated_halfblock_reversed.hex()

    print(f"Generated key 2: {generated_key_2}")
    print(f"Expected key 2:  {key_2}")
    print(f"Match: {'✅' if generated_key_2 == key_2 else '❌'}")
    print()

    # Check if the keys are byte-identical in the second half
    if generated_key_2[32:64] == key_2[32:64]:
        print("✅ Second half matches perfectly!")
    else:
        print("❌ Second half mismatch")
        print(f"   Generated: {generated_key_2[32:64]}")
        print(f"   Expected:  {key_2[32:64]}")

    print()
    print("="*80)


if __name__ == "__main__":
    debug_puzzle_1_to_2()
