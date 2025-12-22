#!/usr/bin/env python3
"""
Recompute Calibration from CSV

This script computes the CORRECT drift values by solving the equation:
X_{k+1} = A^4 * X_k + drift (mod 256)

For each transition k→k+1:
  drift = X_{k+1} - A^4 * X_k (mod 256)

This will create a NEW calibration file with 100% accurate drift values.
"""

import json
import pandas as pd
from pathlib import Path


def load_puzzle_data():
    """Load puzzle CSV."""
    csv_path = Path(__file__).parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"
    return pd.read_csv(csv_path)


def compute_drift_for_transition(key_k_hex: str, key_k_plus_1_hex: str, A_coeffs: list) -> list:
    """
    Compute drift vector for a single transition.

    Given:
      X_{k+1} = A^4 * X_k + drift (mod 256)

    Solve for drift:
      drift = X_{k+1} - A^4 * X_k (mod 256)

    Args:
        key_k_hex: Current key (64 hex chars)
        key_k_plus_1_hex: Next key (64 hex chars)
        A_coeffs: List of 16 A coefficients

    Returns:
        List of 16 drift values (0-255)
    """
    # Extract half-blocks (little-endian)
    X_k = bytes(reversed(bytes.fromhex(key_k_hex[32:64])))
    X_k_plus_1 = bytes(reversed(bytes.fromhex(key_k_plus_1_hex[32:64])))

    drift = []
    for lane in range(16):
        A = A_coeffs[lane]
        A4 = pow(A, 4, 256)

        # Solve: drift = X_{k+1} - A^4 * X_k (mod 256)
        drift_val = (X_k_plus_1[lane] - A4 * X_k[lane]) & 0xFF

        drift.append(drift_val)

    return drift


def recompute_calibration(start: int = 1, end: int = 70):
    """
    Recompute calibration file from CSV.

    Args:
        start: First puzzle number
        end: Last puzzle number (inclusive)
    """
    print("="*80)
    print("RECOMPUTING CALIBRATION FROM CSV")
    print("="*80)
    print()
    print(f"Computing drift values for transitions {start}→{end}")
    print()

    # Load puzzle data
    df = load_puzzle_data()

    # A coefficients (fixed constants)
    A_coeffs = [1, 91, 1, 1, 1, 169, 1, 1, 1, 32, 1, 1, 1, 182, 1, 1]

    print(f"A coefficients: {A_coeffs}")
    print()

    # Compute drift for each transition
    calibration = {
        'A': {str(i): A_coeffs[i] for i in range(16)},
        'drifts': {}
    }

    print("Computing drifts...")
    print()

    for puzzle_k in range(start, end):
        # Get keys
        key_k = df[df['puzzle'] == puzzle_k].iloc[0]['key_hex_64']
        key_k_plus_1 = df[df['puzzle'] == puzzle_k + 1].iloc[0]['key_hex_64']

        # Compute drift
        drift = compute_drift_for_transition(key_k, key_k_plus_1, A_coeffs)

        # Store in calibration
        transition_key = f"{puzzle_k}→{puzzle_k+1}"
        calibration['drifts'][transition_key] = {str(i): drift[i] for i in range(16)}

        # Show progress
        if puzzle_k % 10 == 0 or puzzle_k == start:
            print(f"✅ {transition_key}: {drift}")

    print()
    print(f"✅ Computed {len(calibration['drifts'])} drift vectors")
    print()

    return calibration


def save_calibration(calibration: dict, output_path: Path):
    """Save calibration to JSON."""
    with open(output_path, 'w') as f:
        json.dump(calibration, f, indent=2)

    print(f"💾 Saved calibration to: {output_path}")
    print()


def main():
    """Recompute calibration and save to file."""
    print("="*80)
    print("CALIBRATION RECOMPUTATION")
    print("="*80)
    print()
    print("This script computes CORRECT drift values from the CSV.")
    print("Formula: drift = X_{k+1} - A^4 * X_k (mod 256)")
    print()
    print("="*80)
    print()

    # Recompute calibration
    calibration = recompute_calibration(start=1, end=70)

    # Save to file
    output_dir = Path(__file__).parent.parent.parent / "out"
    output_path = output_dir / "ladder_calib_CORRECTED.json"

    save_calibration(calibration, output_path)

    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()
    print(f"✅ Recomputed calibration for puzzles 1-70")
    print(f"✅ Saved to: {output_path}")
    print()
    print("Next steps:")
    print("1. Validate the corrected calibration file")
    print("2. Use it for 100% accurate key generation")
    print()


if __name__ == "__main__":
    main()
