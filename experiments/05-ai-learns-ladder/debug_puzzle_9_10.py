#!/usr/bin/env python3
"""
Debug puzzle 9→10 transition in detail.
"""

import json
import pandas as pd
from pathlib import Path


def debug_puzzle_9_to_10():
    """Debug puzzle 9→10 transition."""
    # Load data
    calib_path = Path(__file__).parent.parent.parent / "out" / "ladder_calib_ultimate.json"
    csv_path = Path(__file__).parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"

    with open(calib_path) as f:
        calib = json.load(f)

    df = pd.read_csv(csv_path)

    print("="*80)
    print("DEBUGGING PUZZLE 9→10")
    print("="*80)
    print()

    # Get keys
    key_9 = df[df['puzzle'] == 9].iloc[0]['key_hex_64']
    key_10 = df[df['puzzle'] == 10].iloc[0]['key_hex_64']

    print(f"Puzzle 9 key:  {key_9}")
    print(f"Puzzle 10 key: {key_10}")
    print()

    # Get A and drift
    A = [calib['A'][str(i)] for i in range(16)]
    drift = [calib['drifts']['9→10'][str(i)] for i in range(16)]

    print(f"A coefficients: {A}")
    print(f"Drift (9→10):   {drift}")
    print()

    # Extract half-blocks (little-endian)
    key_9_halfblock = bytes(reversed(bytes.fromhex(key_9[32:64])))
    key_10_halfblock = bytes(reversed(bytes.fromhex(key_10[32:64])))

    print("Key 9 halfblock (little-endian):")
    print(f"  Hex: {key_9_halfblock.hex()}")
    print(f"  Bytes: {list(key_9_halfblock)}")
    print()

    print("Key 10 halfblock (little-endian):")
    print(f"  Hex: {key_10_halfblock.hex()}")
    print(f"  Bytes: {list(key_10_halfblock)}")
    print()

    # Apply formula
    print("Applying formula: X_{k+1} = A^4 * X_k + drift (mod 256)")
    print()

    generated = []
    for lane in range(16):
        A_val = A[lane]
        A4 = pow(A_val, 4, 256)

        X_k = key_9_halfblock[lane]
        drift_val = drift[lane]

        X_k_plus_1_expected = key_10_halfblock[lane]
        X_k_plus_1_generated = (A4 * X_k + drift_val) & 0xFF

        match = "✅" if X_k_plus_1_generated == X_k_plus_1_expected else "❌"

        print(f"  Lane {lane:2d}: A={A_val:3d}, A^4={A4:3d}, "
              f"X_k={X_k:3d} (0x{X_k:02x}), drift={drift_val:3d}, "
              f"expected={X_k_plus_1_expected:3d} (0x{X_k_plus_1_expected:02x}), "
              f"generated={X_k_plus_1_generated:3d} (0x{X_k_plus_1_generated:02x}) {match}")

        generated.append(X_k_plus_1_generated)

    print()

    # Convert back
    generated_halfblock_reversed = bytes(reversed(generated))
    generated_key_10 = '0' * 32 + generated_halfblock_reversed.hex()

    print(f"Generated key 10: {generated_key_10}")
    print(f"Expected key 10:  {key_10}")
    print(f"Match: {'✅' if generated_key_10 == key_10 else '❌'}")
    print()

    # Manual check for lane 0
    print("="*80)
    print("MANUAL VERIFICATION FOR LANE 0:")
    print("="*80)
    print()

    X_k_lane0 = key_9_halfblock[0]
    print(f"X_k (puzzle 9, lane 0) = {X_k_lane0} = 0x{X_k_lane0:02x} = 0b{X_k_lane0:08b}")

    A_lane0 = A[0]
    A4_lane0 = pow(A_lane0, 4, 256)
    print(f"A = {A_lane0}, A^4 mod 256 = {A4_lane0}")

    drift_lane0 = drift[0]
    print(f"drift = {drift_lane0}")
    print()

    product = A4_lane0 * X_k_lane0
    print(f"A^4 * X_k = {A4_lane0} * {X_k_lane0} = {product}")

    result_before_mod = product + drift_lane0
    print(f"A^4 * X_k + drift = {product} + {drift_lane0} = {result_before_mod}")

    result_after_mod = result_before_mod & 0xFF
    print(f"(A^4 * X_k + drift) mod 256 = {result_after_mod} = 0x{result_after_mod:02x}")
    print()

    X_k_plus_1_expected_lane0 = key_10_halfblock[0]
    print(f"Expected X_{10} (lane 0) = {X_k_plus_1_expected_lane0} = 0x{X_k_plus_1_expected_lane0:02x}")
    print()

    if result_after_mod == X_k_plus_1_expected_lane0:
        print("✅ MATCH! Formula is correct for lane 0")
    else:
        print(f"❌ MISMATCH! Got {result_after_mod}, expected {X_k_plus_1_expected_lane0}")
        print()
        print("Possible issues:")
        print("1. Drift value is wrong in calibration")
        print("2. Endianness issue")
        print("3. A coefficient is wrong")

    print()
    print("="*80)


if __name__ == "__main__":
    debug_puzzle_9_to_10()
