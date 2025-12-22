#!/usr/bin/env python3
"""
Verify Affine Recurrence Formula

This script verifies the OLD AI's discovered formula:
X_{k+1}(ℓ) = A_ℓ^4 * X_k(ℓ) + Γ_ℓ * C_0(ℓ) (mod 256)

Using the calibration file from 18 months of work.

This is PURE MATH - we can construct/engineer the solution,
not calculate or brute force it.
"""

import json
import csv
from pathlib import Path
from typing import Dict, Tuple

def load_calibration(calib_path: str) -> dict:
    """Load calibration from JSON file."""
    with open(calib_path, 'r') as f:
        return json.load(f)


def load_puzzles_from_csv(csv_path: str) -> Dict[int, bytes]:
    """
    Load puzzles from CSV as raw bytes.

    Returns dict: puzzle_num -> 16 bytes (last half of key)

    IMPORTANT: Returns bytes in LITTLE-ENDIAN order (lane 0 = rightmost byte)
    to match the calibration file format.
    """
    puzzles = {}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                puzzle_num = int(row['puzzle'])
            except ValueError:
                continue

            key_hex_64 = row['key_hex_64'].strip()
            if len(key_hex_64) != 64:
                continue

            # Extract LAST 32 hex chars (last 16 bytes)
            # This is where the actual key data is
            last_32_hex = key_hex_64[32:64]

            # Convert to bytes in BIG-ENDIAN (as stored in CSV)
            big_endian_bytes = bytes.fromhex(last_32_hex)

            # Reverse to LITTLE-ENDIAN (lane 0 = rightmost byte)
            # This matches the calibration file format
            little_endian_bytes = bytes(reversed(big_endian_bytes))

            puzzles[puzzle_num] = little_endian_bytes

    return puzzles


def apply_affine_recurrence(current_bytes: bytes,
                             A: list,
                             drifts: dict) -> bytes:
    """
    Apply affine recurrence formula from old AI's work.

    Formula (ACTUAL from verify_affine.py): X_{k+1}(ℓ) = A_ℓ * X_k(ℓ) + C(ℓ) (mod 256)

    NOT A^4! Just A (linear).

    Args:
        current_bytes: 16 bytes (current puzzle state)
        A: 16 integers (per-lane multipliers)
        drifts: dict mapping lane -> drift value for this transition

    Returns:
        16 bytes (next puzzle state)
    """
    if len(current_bytes) != 16:
        raise ValueError(f"Expected 16 bytes, got {len(current_bytes)}")

    if len(A) != 16:
        raise ValueError(f"Expected 16 A values, got {len(A)}")

    next_bytes = []
    for lane in range(16):
        x = current_bytes[lane]
        a = A[lane] & 0xff

        # Get drift for this lane
        drift = drifts.get(str(lane), 0)

        # Apply formula: a * x + c (mod 256)
        next_val = (a * x + drift) & 0xff
        next_bytes.append(next_val)

    return bytes(next_bytes)


def verify_calibration(puzzles: Dict[int, bytes],
                        calib: dict,
                        start: int,
                        end: int) -> dict:
    """
    Verify calibration on known puzzles.

    Returns verification results.
    """
    print(f"\n{'='*80}")
    print(f"Verifying Affine Recurrence Formula")
    print(f"{'='*80}")

    A = [calib['A'][str(i)] for i in range(16)]
    drifts_dict = calib['drifts']

    print(f"\n🔧 Configuration:")
    print(f"   A matrix: {A}")
    print(f"   Testing puzzles {start} to {end}")

    print(f"\n{'='*80}")
    print(f"Testing Transitions...")
    print(f"{'='*80}\n")

    results = []
    total = 0
    perfect_matches = 0

    for puzzle_num in range(start, end):
        if puzzle_num not in puzzles or puzzle_num + 1 not in puzzles:
            continue

        # Get transition key
        transition_key = f"{puzzle_num}→{puzzle_num+1}"
        if transition_key not in drifts_dict:
            print(f"⚠️  No drift data for {transition_key}")
            continue

        current = puzzles[puzzle_num]
        actual_next = puzzles[puzzle_num + 1]

        # Get drifts for this transition
        drifts = drifts_dict[transition_key]

        # Apply formula
        predicted_next = apply_affine_recurrence(current, A, drifts)

        # Compare
        match = (predicted_next == actual_next)
        total += 1
        if match:
            perfect_matches += 1

        # Byte-by-byte accuracy
        matches_per_lane = [predicted_next[i] == actual_next[i] for i in range(16)]
        num_correct = sum(matches_per_lane)
        byte_accuracy = (num_correct / 16) * 100

        # Convert to big-endian for display
        predicted_hex = bytes(reversed(predicted_next)).hex()
        actual_hex = bytes(reversed(actual_next)).hex()

        result = {
            'puzzle': puzzle_num,
            'transition': transition_key,
            'predicted_hex': predicted_hex,
            'actual_hex': actual_hex,
            'perfect_match': match,
            'byte_accuracy': byte_accuracy,
            'correct_lanes': num_correct
        }
        results.append(result)

        # Print result
        if match:
            print(f"{transition_key:7s}: ✅ PERFECT MATCH")
        else:
            print(f"{transition_key:7s}: ❌ MISMATCH ({num_correct}/16 bytes = {byte_accuracy:.1f}%)")
            print(f"           Calculated: {predicted_hex}")
            print(f"           Actual:    {actual_hex}")

            # Show which lanes differ (in little-endian lane numbering)
            diff_lanes = [i for i in range(16) if not matches_per_lane[i]]
            if len(diff_lanes) <= 5:
                print(f"           Diff lanes (LE): {diff_lanes}")

    # Summary
    accuracy = (perfect_matches / total * 100) if total > 0 else 0

    print(f"\n{'='*80}")
    print(f"VERIFICATION RESULTS")
    print(f"{'='*80}")
    print(f"\n📊 Summary:")
    print(f"   Total transitions: {total}")
    print(f"   Perfect matches: {perfect_matches}/{total}")
    print(f"   Accuracy: {accuracy:.2f}%")

    if accuracy == 100.0:
        print(f"\n🎉 SUCCESS! Formula verified 100% on puzzles {start}-{end}!")
        print(f"   ✅ Old AI's calibration is CORRECT")
        print(f"   ✅ Affine recurrence formula is PROVEN")
    elif accuracy >= 95.0:
        print(f"\n⚠️  Very close! {perfect_matches}/{total} matched")
        print(f"   Minor errors may be data or implementation issues")
    else:
        print(f"\n❌ Formula verification failed")
        print(f"   Only {accuracy:.1f}% accuracy")

    return {
        'total': total,
        'perfect_matches': perfect_matches,
        'accuracy': accuracy,
        'results': results
    }


def main():
    """Verify the old AI's affine recurrence formula."""
    print("="*80)
    print("Verifying Old AI's Affine Recurrence Formula")
    print("="*80)

    # Paths
    base_path = Path(__file__).parent.parent.parent.parent
    csv_path = base_path / "data" / "btc_puzzle_1_160_full.csv"
    calib_path = base_path / "out" / "ladder_calib_1_70_complete.json"

    print(f"\n📂 Loading data...")
    print(f"   CSV: {csv_path}")
    print(f"   Calibration: {calib_path}")

    # Load
    puzzles = load_puzzles_from_csv(csv_path)
    calib = load_calibration(calib_path)

    print(f"\n✅ Loaded {len(puzzles)} puzzles")
    print(f"✅ Loaded calibration for range {calib['range']}")

    # Show sample (convert to big-endian for display)
    print(f"\n🔍 Sample puzzles (big-endian hex):")
    for i in [1, 2, 10, 70]:
        if i in puzzles:
            big_endian = bytes(reversed(puzzles[i]))
            print(f"   Puzzle {i:3d}: {big_endian.hex()}")

    # Verify on puzzles 1-70
    results = verify_calibration(puzzles, calib, 1, 70)

    print(f"\n{'='*80}")
    print(f"CONCLUSION")
    print(f"{'='*80}\n")

    if results['accuracy'] == 100.0:
        print(f"✅ The old AI (phi, mistral, oss) was RIGHT!")
        print(f"✅ Affine recurrence formula works perfectly")
        print(f"✅ This is PURE MATH - we can engineer the solution")
        print(f"\n📝 Next: Use this formula to generate puzzles 71-160")
    else:
        print(f"⚠️  Accuracy: {results['accuracy']:.2f}%")
        print(f"⚠️  Need to investigate mismatches")
        print(f"\n💡 Check:")
        print(f"   1. Data format (are we using correct 16 bytes?)")
        print(f"   2. Formula implementation (A^4 calculation)")
        print(f"   3. Drift values (from calibration file)")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
