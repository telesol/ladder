#!/usr/bin/env python3
"""
Verify Calibration Against Database Directly

The calibration file may have errors. Let's verify against the ACTUAL database puzzles.

This compares:
- CSV puzzles (ground truth)
- Calibration calculations using formula
- Direct validation (no compounding errors)
"""

import json
import pandas as pd
import sqlite3
from pathlib import Path

def load_all_data():
    """Load calibration, CSV, and database."""
    calib_path = Path(__file__).parent.parent.parent / "out" / "ladder_calib_ultimate.json"
    csv_path = Path(__file__).parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"
    db_path = Path(__file__).parent.parent.parent / "db" / "kh.db"

    with open(calib_path) as f:
        calib = json.load(f)

    df = pd.read_csv(csv_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    return calib, df, conn, cursor

def verify_single_transition(puzzle_k, calib, df):
    """
    Verify a single transition k → k+1 using calibration.

    Returns: (hex_match, byte_mismatches)
    """
    A = [calib['A'][str(i)] for i in range(16)]

    # Get keys from CSV
    key_k_hex = df[df['puzzle'] == puzzle_k].iloc[0]['key_hex_64']
    key_k_plus_1_hex = df[df['puzzle'] == puzzle_k + 1].iloc[0]['key_hex_64']

    # Extract last 16 bytes (little-endian)
    X_k = bytes(reversed(bytes.fromhex(key_k_hex[32:64])))
    X_k_plus_1_actual = bytes(reversed(bytes.fromhex(key_k_plus_1_hex[32:64])))

    # Check if drift exists
    drift_key = f"{puzzle_k}→{puzzle_k+1}"
    if drift_key not in calib['drifts']:
        return None, None

    # Calculate using formula
    X_k_plus_1_predicted = []
    for lane in range(16):
        A_lane = A[lane]
        A4 = pow(A_lane, 4, 256)
        drift = calib['drifts'][drift_key][str(lane)]

        X_k_byte = X_k[lane]
        X_k_plus_1_byte = (A4 * X_k_byte + drift) & 0xFF

        X_k_plus_1_predicted.append(X_k_plus_1_byte)

    X_k_plus_1_predicted = bytes(X_k_plus_1_predicted)

    # Count mismatches
    mismatches = []
    for lane in range(16):
        if X_k_plus_1_predicted[lane] != X_k_plus_1_actual[lane]:
            mismatches.append({
                'lane': lane,
                'calculated': X_k_plus_1_predicted[lane],
                'actual': X_k_plus_1_actual[lane],
                'X_k': X_k[lane],
                'A': A[lane],
                'drift': calib['drifts'][drift_key][str(lane)],
            })

    hex_match = (X_k_plus_1_predicted == X_k_plus_1_actual)

    return hex_match, mismatches

def main():
    """Verify all transitions."""
    print("="*80)
    print("VERIFYING CALIBRATION AGAINST CSV DATA")
    print("="*80)
    print()

    calib, df, conn, cursor = load_all_data()

    print("📋 Testing calibration on ALL transitions (no compounding errors)")
    print()

    results = []
    total_transitions = 0
    perfect_transitions = 0
    total_byte_errors = 0

    for puzzle_k in range(1, 70):
        hex_match, mismatches = verify_single_transition(puzzle_k, calib, df)

        if hex_match is None:
            continue

        total_transitions += 1

        if hex_match:
            perfect_transitions += 1
            status = "✅"
        else:
            status = "❌"
            total_byte_errors += len(mismatches)

        results.append({
            'puzzle_k': puzzle_k,
            'transition': f"{puzzle_k}→{puzzle_k+1}",
            'match': status,
            'num_mismatches': len(mismatches),
            'mismatches': mismatches if mismatches else None,
        })

        # Show problematic transitions
        if not hex_match:
            print(f"Puzzle {puzzle_k}→{puzzle_k+1}: {status} ({len(mismatches)} lane mismatches)")
            for mismatch in mismatches[:3]:  # Show first 3
                print(f"  Lane {mismatch['lane']}: "
                      f"calculated={mismatch['calculated']}, "
                      f"actual={mismatch['actual']}, "
                      f"X_k={mismatch['X_k']}, "
                      f"A={mismatch['A']}, "
                      f"drift={mismatch['drift']}")

    # Summary
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()

    print(f"📊 Transition-by-transition accuracy (no compounding):")
    print(f"   Total transitions: {total_transitions}")
    print(f"   Perfect matches: {perfect_transitions}/{total_transitions} ({perfect_transitions/total_transitions*100:.2f}%)")
    print(f"   Total byte errors: {total_byte_errors}/{total_transitions*16} ({total_byte_errors/(total_transitions*16)*100:.2f}%)")
    print()

    byte_accuracy = (total_transitions * 16 - total_byte_errors) / (total_transitions * 16) * 100
    print(f"✅ Byte-level accuracy: {byte_accuracy:.2f}%")
    print()

    if byte_accuracy >= 100:
        print("🎉 PERFECT! 100% accuracy!")
    elif byte_accuracy >= 98:
        print(f"✅ EXCELLENT! {byte_accuracy:.1f}% accuracy (close to perfect)")
    else:
        print(f"📝 Accuracy: {byte_accuracy:.1f}% (needs improvement)")

    conn.close()

if __name__ == "__main__":
    main()
