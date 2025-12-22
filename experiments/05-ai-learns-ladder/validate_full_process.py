#!/usr/bin/env python3
"""
Full Process Validation

This script validates the ENTIRE ladder process:
1. Load calibration file
2. Generate keys using formula: X_{k+1} = A^4 * X_k + drift (mod 256)
3. Derive Bitcoin addresses cryptographically (ECDSA + SHA256 + RIPEMD160)
4. Compare with known addresses from CSV
5. Report success/failure for each puzzle

This PROVES our process is correct end-to-end.
"""

import json
import pandas as pd
import sys
from pathlib import Path
from crypto_validator import private_key_to_address, validate_key_generates_address


def load_calibration(corrected=True):
    """Load calibration file."""
    if corrected:
        calib_path = Path(__file__).parent.parent.parent / "out" / "ladder_calib_CORRECTED.json"
    else:
        calib_path = Path(__file__).parent.parent.parent / "out" / "ladder_calib_ultimate.json"

    with open(calib_path) as f:
        return json.load(f)


def load_puzzle_data():
    """Load puzzle CSV."""
    csv_path = Path(__file__).parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"
    return pd.read_csv(csv_path)


def generate_next_key(current_key_hex: str, drift_vector: list, A_coeffs: list) -> str:
    """
    Generate next key using ladder formula.

    Formula: X_{k+1}[lane] = (A[lane]^4 * X_k[lane] + drift[lane]) mod 256

    Args:
        current_key_hex: 64-char hex string (32 bytes)
        drift_vector: List of 16 drift values (0-255)
        A_coeffs: List of 16 A coefficients

    Returns:
        Next key as 64-char hex string
    """
    # Extract last 16 bytes (little-endian half-block)
    current_bytes = bytes.fromhex(current_key_hex[32:64])
    current_halfblock = bytes(reversed(current_bytes))

    # Apply formula to each lane
    next_halfblock = []
    for lane in range(16):
        A = A_coeffs[lane]
        A4 = pow(A, 4, 256)

        X_k = current_halfblock[lane]
        drift = drift_vector[lane]

        X_k_plus_1 = (A4 * X_k + drift) & 0xFF
        next_halfblock.append(X_k_plus_1)

    # Convert back to big-endian and prepend zeros
    next_halfblock_reversed = bytes(reversed(next_halfblock))
    next_key_hex = '0' * 32 + next_halfblock_reversed.hex()

    return next_key_hex


def validate_transition(puzzle_k: int, calib: dict, df: pd.DataFrame, verbose: bool = True) -> dict:
    """
    Validate a single transition: puzzle_k → puzzle_k+1

    Returns dict with validation results.
    """
    # Get keys from CSV
    key_k = df[df['puzzle'] == puzzle_k].iloc[0]['key_hex_64']
    key_k_plus_1_expected = df[df['puzzle'] == puzzle_k + 1].iloc[0]['key_hex_64']
    address_k_plus_1_expected = df[df['puzzle'] == puzzle_k + 1].iloc[0]['address']

    # Get drift vector from calibration
    drift_key = f"{puzzle_k}→{puzzle_k+1}"
    if drift_key not in calib['drifts']:
        return {
            'puzzle': f"{puzzle_k}→{puzzle_k+1}",
            'success': False,
            'error': 'Drift not in calibration',
        }

    drift_vector = [calib['drifts'][drift_key][str(i)] for i in range(16)]
    A_coeffs = [calib['A'][str(i)] for i in range(16)]

    # Generate next key using formula
    key_k_plus_1_generated = generate_next_key(key_k, drift_vector, A_coeffs)

    # Check if generated key matches expected key
    key_match = (key_k_plus_1_generated == key_k_plus_1_expected)

    # Derive Bitcoin address from generated key (Bitcoin puzzle uses COMPRESSED format)
    address_generated = private_key_to_address(key_k_plus_1_generated, compressed=True)

    # Check if address matches
    address_match = (address_generated == address_k_plus_1_expected)

    result = {
        'puzzle': f"{puzzle_k}→{puzzle_k+1}",
        'key_match': key_match,
        'address_match': address_match,
        'success': key_match and address_match,
        'key_expected': key_k_plus_1_expected,
        'key_generated': key_k_plus_1_generated,
        'address_expected': address_k_plus_1_expected,
        'address_generated': address_generated,
    }

    if verbose:
        status = "✅" if result['success'] else "❌"
        print(f"{status} Puzzle {puzzle_k}→{puzzle_k+1}:")
        if result['success']:
            print(f"   Key: {key_k_plus_1_generated[:32]}...{key_k_plus_1_generated[32:]}")
            print(f"   Address: {address_generated}")
        else:
            if not key_match:
                print(f"   ❌ Key mismatch!")
                print(f"      Expected:  {key_k_plus_1_expected}")
                print(f"      Generated: {key_k_plus_1_generated}")
            if not address_match:
                print(f"   ❌ Address mismatch!")
                print(f"      Expected:  {address_k_plus_1_expected}")
                print(f"      Generated: {address_generated}")

    return result


def validate_range(start: int, end: int, calib: dict, df: pd.DataFrame) -> list:
    """
    Validate a range of transitions.

    Args:
        start: First puzzle number
        end: Last puzzle number (inclusive)
        calib: Calibration data
        df: Puzzle dataframe

    Returns:
        List of validation results
    """
    print("="*80)
    print(f"VALIDATING TRANSITIONS: Puzzles {start}→{end}")
    print("="*80)
    print()

    results = []
    for puzzle_k in range(start, end):
        # Only show verbose output for failures
        result = validate_transition(puzzle_k, calib, df, verbose=False)
        results.append(result)

        # Show progress dot
        if result['success']:
            print("✅", end="", flush=True)
        else:
            print("❌", end="", flush=True)

        # New line every 10 puzzles
        if (puzzle_k - start + 1) % 10 == 0:
            print(f"  ({puzzle_k})")

    print()
    print()

    # Show failures in detail
    failures = [r for r in results if not r['success']]
    if failures:
        print("Failed transitions in detail:")
        print()
        for r in failures:
            print(f"❌ {r['puzzle']}:")
            if not r['key_match']:
                print(f"   Key mismatch:")
                print(f"     Expected:  {r['key_expected']}")
                print(f"     Generated: {r['key_generated']}")
            if not r['address_match']:
                print(f"   Address mismatch:")
                print(f"     Expected:  {r['address_expected']}")
                print(f"     Generated: {r['address_generated']}")
            print()

    return results


def print_summary(results: list):
    """Print validation summary."""
    print("="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print()

    total = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total - successful

    success_rate = 100 * successful / total if total > 0 else 0

    print(f"Total transitions tested: {total}")
    print(f"✅ Successful: {successful} ({success_rate:.1f}%)")
    print(f"❌ Failed: {failed}")
    print()

    if failed > 0:
        print("Failed transitions:")
        for r in results:
            if not r['success']:
                print(f"  ❌ {r['puzzle']}")
                if not r['key_match']:
                    print(f"     Key mismatch")
                if not r.get('address_match', True):
                    print(f"     Address mismatch")
        print()

    if success_rate == 100.0:
        print("🎉 PERFECT! 100% validation success!")
        print("✅ Process is CORRECT:")
        print("   1. Calibration file is accurate")
        print("   2. Formula generates correct keys")
        print("   3. Cryptographic derivation is correct")
        print("   4. Bitcoin addresses match perfectly")
    elif success_rate >= 90:
        print("✅ Process is mostly correct!")
        print(f"   {success_rate:.1f}% accuracy - minor issues to fix")
    else:
        print("⚠️  Process has issues - needs debugging")

    print()
    print("="*80)


def main():
    """Validate full process on puzzles 1-10."""
    print("="*80)
    print("FULL PROCESS VALIDATION")
    print("="*80)
    print()
    print("This validates the ENTIRE pipeline:")
    print("1. Load calibration file")
    print("2. Generate keys using formula")
    print("3. Derive Bitcoin addresses cryptographically")
    print("4. Compare with known addresses from CSV")
    print()
    print("="*80)
    print()

    # Load data
    print("📂 Loading data...")
    calib = load_calibration()
    df = load_puzzle_data()
    print(f"✅ Loaded {len(calib['drifts'])} drift vectors")
    print(f"✅ Loaded {len(df)} puzzles from CSV")
    print()

    # Validate puzzles 1-70 (full calibration range)
    results = validate_range(1, 70, calib, df)

    # Print summary
    print_summary(results)

    # Return success status
    return all(r['success'] for r in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
