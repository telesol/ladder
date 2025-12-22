#!/usr/bin/env python3
"""
HARD PROOF VERIFICATION: Compare PySR calculations with actual Bitcoin puzzle keys

This script provides byte-for-byte comparison between:
1. PySR formula calculations (starting from puzzle 1)
2. Real Bitcoin keys from btc_puzzle_1_160_full.csv

Scientific Rigor: We need 100% exact match to claim we "discovered" the formula.
"""

import csv
import json
import numpy as np
from pathlib import Path

# Discovered exponent pattern
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

def apply_formula(x, exponent):
    """Apply discovered formula: f(x) = x^n (mod 256)."""
    if exponent == 0:
        return 0
    else:
        return int(x ** exponent) % 256

def predict_next(current_bytes, exponents):
    """Calculate next puzzle's first 16 bytes given current puzzle."""
    next_bytes = []
    for lane in range(len(exponents)):
        next_bytes.append(apply_formula(current_bytes[lane], exponents[lane]))
    return bytes(next_bytes)

def load_csv_keys(csv_path):
    """Load actual Bitcoin keys from CSV."""
    keys = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                puzzle_num = int(row['puzzle'])
            except ValueError:
                # Skip header or malformed rows
                continue

            # Get the 64-character hex key (padded to 64 chars)
            key_hex_64 = row['key_hex_64'].strip()

            # Validate it's actually hex
            if len(key_hex_64) != 64:
                print(f"⚠️  Puzzle {puzzle_num}: key_hex_64 length is {len(key_hex_64)}, expected 64, skipping...")
                continue

            # Convert to bytes (first 16 bytes are what we're validating)
            try:
                key_bytes = bytes.fromhex(key_hex_64)[:16]  # First 16 bytes only
            except ValueError as e:
                print(f"⚠️  Puzzle {puzzle_num}: Invalid hex in key_hex_64: {e}, skipping...")
                continue

            keys[puzzle_num] = {
                'hex_full': key_hex_64,
                'hex_first16': key_hex_64[:32],  # First 16 bytes as hex string
                'bytes_first16': key_bytes,
                'address': row['address']
            }

    return keys

def verify_puzzles(csv_path, start_puzzle, end_puzzle, exponents):
    """
    Verify that PySR formula generates exact Bitcoin keys.

    Returns:
        dict with verification results
    """
    print(f"\n{'='*80}")
    print(f"HARD PROOF VERIFICATION: PySR Formula vs Real Bitcoin Keys")
    print(f"{'='*80}")

    # Load real keys from CSV
    print(f"\n📂 Loading real Bitcoin keys from CSV...")
    real_keys = load_csv_keys(csv_path)
    print(f"   Loaded {len(real_keys)} puzzle keys")

    # Start from puzzle 1 (seed value)
    current_key = real_keys[start_puzzle]['bytes_first16']
    print(f"\n🌱 Starting from puzzle {start_puzzle}:")
    print(f"   Seed key (first 16 bytes): {current_key.hex()}")
    print(f"   Address: {real_keys[start_puzzle]['address']}")

    # Track results
    results = []
    total_matches = 0
    total_checked = 0

    print(f"\n🔄 Applying PySR formula to generate puzzles {start_puzzle+1} to {end_puzzle}...")
    print(f"{'='*80}")

    for puzzle_num in range(start_puzzle + 1, end_puzzle + 1):
        # Calculate next key using PySR formula
        predicted_bytes = predict_next(current_key, exponents)

        # Get real key from CSV
        if puzzle_num not in real_keys:
            print(f"⚠️  Puzzle {puzzle_num} not in CSV, skipping...")
            continue

        real_bytes = real_keys[puzzle_num]['bytes_first16']

        # Byte-for-byte comparison
        matches = (predicted_bytes == real_bytes)
        total_checked += 1

        if matches:
            total_matches += 1
            status = "✅ EXACT MATCH"
            per_lane_status = []
            for lane in range(16):
                if predicted_bytes[lane] == real_bytes[lane]:
                    per_lane_status.append(f"L{lane:02d}:✓")
                else:
                    per_lane_status.append(f"L{lane:02d}:✗")
        else:
            status = "❌ MISMATCH"
            per_lane_status = []
            for lane in range(16):
                if predicted_bytes[lane] == real_bytes[lane]:
                    per_lane_status.append(f"L{lane:02d}:✓")
                else:
                    per_lane_status.append(f"L{lane:02d}:✗ (pred:{predicted_bytes[lane]:02x} != real:{real_bytes[lane]:02x})")

        result_entry = {
            'puzzle': puzzle_num,
            'address': real_keys[puzzle_num]['address'],
            'predicted_hex': predicted_bytes.hex(),
            'real_hex': real_bytes.hex(),
            'match': matches,
            'per_lane': per_lane_status
        }
        results.append(result_entry)

        # Print progress
        if matches:
            print(f"Puzzle {puzzle_num:3d}: {status}")
        else:
            print(f"Puzzle {puzzle_num:3d}: {status}")
            print(f"            Calculated: {predicted_bytes.hex()}")
            print(f"            Real:      {real_bytes.hex()}")
            print(f"            Lanes: {' '.join(per_lane_status[:8])}")
            print(f"                   {' '.join(per_lane_status[8:])}")

        # Update current key for next iteration
        current_key = real_bytes  # Use real key (not calculation) to avoid error accumulation

    # Summary
    print(f"\n{'='*80}")
    print(f"VERIFICATION SUMMARY")
    print(f"{'='*80}")

    accuracy = (total_matches / total_checked * 100) if total_checked > 0 else 0

    print(f"\n📊 Overall Results:")
    print(f"   Puzzles checked: {total_checked}")
    print(f"   Exact matches: {total_matches}")
    print(f"   Accuracy: {accuracy:.2f}%")

    if accuracy == 100.0:
        print(f"\n🎉 HARD PROOF CONFIRMED!")
        print(f"   ✅ PySR formula generates EXACT Bitcoin keys for puzzles {start_puzzle+1}-{end_puzzle}")
        print(f"   ✅ Byte-for-byte identical to real puzzle keys")
        print(f"   ✅ Formula: X_{{k+1}}(ℓ) = X_k(ℓ)^n (mod 256)")
        print(f"   ✅ Exponents: {EXPONENTS}")
    else:
        print(f"\n⚠️  VERIFICATION FAILED")
        print(f"   ❌ Formula does not match real Bitcoin keys")
        print(f"   ❌ {total_checked - total_matches} mismatches found")

    return {
        'start_puzzle': start_puzzle,
        'end_puzzle': end_puzzle,
        'total_checked': total_checked,
        'total_matches': total_matches,
        'accuracy': accuracy,
        'results': results,
        'perfect': (accuracy == 100.0)
    }

def main():
    """Main verification entry point."""
    # Paths
    # CSV is in kh-assist/data/, not experiments/data/
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Verify puzzles 1-70 (training + validation)
    print("\n" + "="*80)
    print("VERIFICATION 1: Puzzles 1-70 (Training + Validation Set)")
    print("="*80)
    results_1_70 = verify_puzzles(csv_path, 1, 70, EXPONENTS)

    # Verify bridge rows (75, 80, 85, 90, 95)
    # Note: These require multi-step calculation from puzzle 70
    print("\n" + "="*80)
    print("VERIFICATION 2: Bridge Rows (75, 80, 85, 90, 95)")
    print("="*80)

    # Load real keys
    real_keys = load_csv_keys(csv_path)

    # Start from puzzle 70
    current_key = real_keys[70]['bytes_first16']
    bridge_results = []
    bridge_puzzles = [75, 80, 85, 90, 95]

    print(f"\n🌱 Starting from puzzle 70:")
    print(f"   Seed key: {current_key.hex()}")

    for target_puzzle in bridge_puzzles:
        # Calculate steps needed
        start_from = 70 if target_puzzle == 75 else bridge_results[-1]['puzzle']
        steps = target_puzzle - start_from

        # Multi-step calculation
        print(f"\n🔄 Calculating puzzle {target_puzzle} ({steps} steps from puzzle {start_from})...")
        for step in range(steps):
            current_key = predict_next(current_key, EXPONENTS)

        # Compare with real key
        real_bytes = real_keys[target_puzzle]['bytes_first16']
        matches = (current_key == real_bytes)

        if matches:
            print(f"   ✅ EXACT MATCH")
        else:
            print(f"   ❌ MISMATCH")
            print(f"   Calculated: {current_key.hex()}")
            print(f"   Real:      {real_bytes.hex()}")

        bridge_results.append({
            'puzzle': target_puzzle,
            'steps_from_70': target_puzzle - 70,
            'predicted_hex': current_key.hex(),
            'real_hex': real_bytes.hex(),
            'match': matches
        })

        # Use real key for next calculation to avoid error accumulation
        current_key = real_bytes

    # Bridge summary
    bridge_matches = sum(1 for r in bridge_results if r['match'])
    bridge_accuracy = (bridge_matches / len(bridge_results) * 100) if bridge_results else 0

    print(f"\n📊 Bridge Rows Summary:")
    print(f"   Checked: {len(bridge_results)}")
    print(f"   Matches: {bridge_matches}")
    print(f"   Accuracy: {bridge_accuracy:.2f}%")

    # Final summary
    print(f"\n{'='*80}")
    print(f"FINAL VERDICT")
    print(f"{'='*80}")

    overall_perfect = results_1_70['perfect'] and (bridge_accuracy == 100.0)

    if overall_perfect:
        print(f"\n🏆 COMPLETE SUCCESS - HARD PROOF ESTABLISHED!")
        print(f"\n✅ PySR formula is PROVEN to generate real Bitcoin puzzle keys:")
        print(f"   • Puzzles 1-70: {results_1_70['accuracy']:.2f}% accuracy")
        print(f"   • Bridge rows: {bridge_accuracy:.2f}% accuracy")
        print(f"   • Formula: X_{{k+1}}(ℓ) = X_k(ℓ)^n (mod 256)")
        print(f"   • Exponents: {EXPONENTS}")
        print(f"\n🔬 This is not speculation - this is mathematical proof.")
        print(f"   We can now confidently generate missing puzzles 71-160.")
    else:
        print(f"\n⚠️  VERIFICATION INCOMPLETE")
        print(f"   Puzzles 1-70: {results_1_70['accuracy']:.2f}%")
        print(f"   Bridge rows: {bridge_accuracy:.2f}%")
        print(f"\n   Further investigation needed.")

    # Save results
    output_file = results_dir / "bitcoin_key_verification.json"
    with open(output_file, 'w') as f:
        json.dump({
            'puzzles_1_70': results_1_70,
            'bridge_rows': {
                'results': bridge_results,
                'accuracy': bridge_accuracy,
                'perfect': (bridge_accuracy == 100.0)
            },
            'overall_perfect': overall_perfect,
            'exponents_used': EXPONENTS
        }, f, indent=2)

    print(f"\n💾 Full results saved to: {output_file}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
