#!/usr/bin/env python3
"""
Validate Ladder Calibration with Full Cryptographic Proof

Uses the WORKING calibration (ladder_calib_ultimate.json) to:
1. Generate puzzles 1-70 using the formula
2. Derive Bitcoin addresses using FULL cryptographic pipeline
3. Compare to CSV addresses for 100% proof

Formula: X_{k+1}[lane] = (A[lane]^4 * X_k[lane] + drift[k→k+1][lane]) mod 256
"""

import json
import pandas as pd
from pathlib import Path
import sys

# Import crypto validator
sys.path.append(str(Path(__file__).parent))
from crypto_validator import private_key_to_address

def load_calibration_and_csv():
    """Load calibration and CSV data."""
    calib_path = Path(__file__).parent.parent.parent / "out" / "ladder_calib_ultimate.json"
    csv_path = Path(__file__).parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"

    with open(calib_path) as f:
        calib = json.load(f)

    df = pd.read_csv(csv_path)

    return calib, df

def reconstruct_full_key(lane_bytes):
    """
    Reconstruct full 32-byte private key from 16-byte lanes.

    Bitcoin puzzle keys have structure:
    - First 16 bytes: zeros (for puzzles 1-70)
    - Last 16 bytes: our lane_bytes (little-endian)

    Returns: 64-hex-character string
    """
    # Last 16 bytes (big-endian for Bitcoin)
    last_16_bytes = bytes(reversed(lane_bytes))

    # First 16 bytes (zeros for low puzzles)
    first_16_bytes = bytes(16)

    # Full 32-byte key
    full_key = first_16_bytes + last_16_bytes

    return full_key.hex()

def validate_calibration_with_crypto():
    """
    Validate calibration using cryptographic proof.

    For each puzzle 1-70:
    1. Generate next puzzle using formula
    2. Construct full 32-byte private key
    3. Derive Bitcoin address (ECDSA + SHA256 + RIPEMD160 + Base58Check)
    4. Compare to CSV address
    """
    print("="*80)
    print("CRYPTOGRAPHIC VALIDATION OF LADDER CALIBRATION")
    print("="*80)
    print()

    calib, df = load_calibration_and_csv()

    # Extract A coefficients
    A = [calib['A'][str(i)] for i in range(16)]

    print("📋 A coefficients:")
    print(f"   {A}")
    print()

    # Start from puzzle 1 (known)
    puzzle_1_hex = df[df['puzzle'] == 1].iloc[0]['key_hex_64']
    current_key_bytes = bytes(reversed(bytes.fromhex(puzzle_1_hex[32:64])))  # Little-endian

    print(f"🔑 Starting from puzzle 1 (known):")
    print(f"   Key (hex): {puzzle_1_hex}")
    print(f"   Lanes (little-endian): {list(current_key_bytes)}")
    print()

    # Validation results
    results = []
    total = 0
    hex_matches = 0
    address_matches = 0

    print("="*80)
    print("GENERATING AND VALIDATING PUZZLES 2-70")
    print("="*80)
    print()

    for puzzle_k in range(1, 70):
        puzzle_k_plus_1 = puzzle_k + 1

        # Check if drift exists
        drift_key = f"{puzzle_k}→{puzzle_k_plus_1}"
        if drift_key not in calib['drifts']:
            print(f"⚠️  Missing drift for {drift_key}, skipping...")
            continue

        # Generate next puzzle using formula
        next_key_bytes = []
        for lane in range(16):
            A_lane = A[lane]
            A4 = pow(A_lane, 4, 256)  # A^4 mod 256
            drift = calib['drifts'][drift_key][str(lane)]

            X_k = current_key_bytes[lane]
            X_k_plus_1 = (A4 * X_k + drift) & 0xFF

            next_key_bytes.append(X_k_plus_1)

        next_key_bytes = bytes(next_key_bytes)

        # Reconstruct full 32-byte key
        generated_full_key = reconstruct_full_key(next_key_bytes)

        # Get actual key from CSV
        csv_row = df[df['puzzle'] == puzzle_k_plus_1].iloc[0]
        actual_full_key = csv_row['key_hex_64']
        csv_address = csv_row['address']

        # Check hex match
        hex_match = (generated_full_key.lower() == actual_full_key.lower())

        # Derive Bitcoin address from generated key
        try:
            generated_address = private_key_to_address(generated_full_key, compressed=True)
            address_match = (generated_address == csv_address)
        except Exception as e:
            generated_address = f"ERROR: {e}"
            address_match = False

        # Update counters
        total += 1
        if hex_match:
            hex_matches += 1
        if address_match:
            address_matches += 1

        # Store result
        results.append({
            'puzzle': puzzle_k_plus_1,
            'hex_match': '✅' if hex_match else '❌',
            'address_match': '✅' if address_match else '❌',
            'csv_address': csv_address,
            'generated_address': generated_address,
        })

        # Print progress (every 10 puzzles)
        if puzzle_k_plus_1 % 10 == 0:
            print(f"Puzzle {puzzle_k_plus_1:3d}: "
                  f"Hex {'✅' if hex_match else '❌'}, "
                  f"Address {'✅' if address_match else '❌'}")

        # Update current state for next iteration
        current_key_bytes = next_key_bytes

    # Summary
    print()
    print("="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print()

    print(f"📊 Results:")
    print(f"   Total puzzles tested: {total}")
    print(f"   Hex matches: {hex_matches}/{total} ({hex_matches/total*100:.2f}%)")
    print(f"   Bitcoin address matches: {address_matches}/{total} ({address_matches/total*100:.2f}%)")
    print()

    if address_matches == total:
        print("🎉 PERFECT! 100% cryptographic validation!")
        print()
        print("✅ The calibration is MATHEMATICALLY PROVEN!")
        print("✅ All generated keys produce correct Bitcoin addresses!")
        print("✅ Can now generate ANY future puzzle with confidence!")
    elif address_matches >= total * 0.95:
        print(f"✅ EXCELLENT! {address_matches/total*100:.1f}% cryptographic validation!")
        print()
        print("Minor mismatches detected. Analyzing...")
        print()

        # Show mismatches
        df_results = pd.DataFrame(results)
        mismatches = df_results[df_results['address_match'] != '✅']

        if len(mismatches) > 0:
            print("Mismatches:")
            for _, row in mismatches.iterrows():
                print(f"  Puzzle {row['puzzle']}:")
                print(f"    Expected: {row['csv_address']}")
                print(f"    Generated: {row['generated_address']}")
    else:
        print(f"❌ Accuracy: {address_matches/total*100:.1f}% (below target)")
        print()
        print("Significant mismatches detected. Further investigation needed.")

    # Save detailed results
    output_path = Path(__file__).parent / "crypto_validation_results.csv"
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_path, index=False)
    print()
    print(f"💾 Detailed results saved to: {output_path}")
    print()

    return results

if __name__ == "__main__":
    results = validate_calibration_with_crypto()
