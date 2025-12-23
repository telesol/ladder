#!/usr/bin/env python3
"""
Generate Lanes 9-15 for Puzzles 71-95

Based on research findings:
- Lanes 9-15 have drift = 0 (100% confirmed by H1 and H4)
- Formula: X_{k+1}[lane] = X_k[lane]^n mod 256 (NO DRIFT)

Process:
1. Load puzzle 70 from CSV (starting point)
2. Generate lanes 9-15 for puzzles 71-95
3. Verify against bridge endpoints (75, 80, 85, 90, 95)
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
    hex_str = hex_str[-32:].zfill(32)
    return bytes.fromhex(hex_str)[::-1]

def bytes_to_halfblock(data):
    """Convert 16 bytes to 64-hex half-block string (REVERSED)"""
    return '0x' + data[::-1].hex().zfill(32) + '0' * 32

def calculate_next_X_lanes_9_15(X_k_bytes):
    """
    Calculate X_{k+1} for lanes 9-15 ONLY

    Formula: X_{k+1}[lane] = X_k[lane]^n mod 256
    Drift = 0 for these lanes (100% confirmed)

    Returns: 16 bytes (lanes 0-8 unchanged, lanes 9-15 computed)
    """
    result = bytearray(X_k_bytes)  # Copy all lanes

    # Compute ONLY lanes 9-15 with drift=0
    for lane in range(9, 16):
        x = X_k_bytes[lane]
        n = EXPONENTS[lane]
        result[lane] = pow(x, n, 256)

    return bytes(result)

def load_csv_data(csv_file):
    """Load puzzle data from CSV"""
    puzzles = {}
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['key_hex'] != '?':
                puzzle_id = int(row['puzzle'])
                puzzles[puzzle_id] = row['key_hex_64']
    return puzzles

def main():
    print("="*70)
    print("GENERATE LANES 9-15 FOR PUZZLES 71-95")
    print("="*70)
    print("\nBased on H1/H4 research: drift = 0 for lanes 9-15 (100% confirmed)")
    print("Formula: X_{k+1}[lane] = X_k[lane]^n mod 256\n")

    # Load CSV data
    csv_file = Path('data/btc_puzzle_1_160_full.csv')
    print(f"Loading CSV: {csv_file}")
    puzzles = load_csv_data(csv_file)
    print(f"✓ Loaded {len(puzzles)} known puzzles\n")

    # Start from puzzle 70
    if 70 not in puzzles:
        print("❌ Error: Puzzle 70 not found in CSV!")
        return

    X_70 = halfblock_to_bytes(puzzles[70])
    print(f"Starting from puzzle 70:")
    print(f"  X_70 = {bytes_to_halfblock(X_70)[:34]}...")
    print(f"  Lanes 9-15 values: {list(X_70[9:16])}\n")

    # Generate puzzles 71-95
    print("="*70)
    print("GENERATING PUZZLES 71-95 (Lanes 9-15 only)")
    print("="*70)

    generated = {}
    X_current = X_70

    for k in range(70, 95):
        # Calculate next X (lanes 9-15 only)
        X_next = calculate_next_X_lanes_9_15(X_current)

        generated[k+1] = {
            'puzzle': k+1,
            'X_k_hex': bytes_to_halfblock(X_next),
            'lanes_9_15': list(X_next[9:16]),
            'generated': True
        }

        X_current = X_next

    print(f"✓ Generated {len(generated)} puzzles (71-95)\n")

    # Verify against bridges
    print("="*70)
    print("VERIFICATION AGAINST BRIDGES")
    print("="*70)

    bridges = [75, 80, 85, 90, 95]
    verification_results = {}

    for bridge_k in bridges:
        if bridge_k not in puzzles:
            print(f"\n⚠️  Bridge {bridge_k}: Not in CSV (skipping)")
            continue

        # Get actual bridge value from CSV
        X_bridge_actual = halfblock_to_bytes(puzzles[bridge_k])

        # Get our generated value
        X_bridge_generated = halfblock_to_bytes(generated[bridge_k]['X_k_hex'])

        # Compare ONLY lanes 9-15
        matches = 0
        mismatches = []

        for lane in range(9, 16):
            if X_bridge_generated[lane] == X_bridge_actual[lane]:
                matches += 1
            else:
                mismatches.append({
                    'lane': lane,
                    'generated': X_bridge_generated[lane],
                    'actual': X_bridge_actual[lane]
                })

        accuracy = matches / 7 * 100

        verification_results[bridge_k] = {
            'matches': matches,
            'accuracy': accuracy,
            'mismatches': mismatches
        }

        status = "✅" if accuracy == 100 else f"⚠️  {accuracy:.1f}%"
        print(f"\nBridge {bridge_k}: {status} ({matches}/7 lanes match)")

        if mismatches:
            print(f"  Mismatches:")
            for mm in mismatches:
                print(f"    Lane {mm['lane']}: gen={mm['generated']}, actual={mm['actual']}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    total_matches = sum(v['matches'] for v in verification_results.values())
    total_lanes = len(verification_results) * 7
    overall_accuracy = total_matches / total_lanes * 100 if total_lanes > 0 else 0

    print(f"\nGenerated puzzles: 71-95 (25 puzzles)")
    print(f"Lanes generated: 9-15 (7 lanes per puzzle)")
    print(f"Bridges verified: {len(verification_results)}")
    print(f"Overall accuracy: {overall_accuracy:.2f}% ({total_matches}/{total_lanes} lanes)")

    if overall_accuracy == 100:
        print(f"\n🎉 SUCCESS! All lanes 9-15 match perfectly!")
        print(f"   Formula validated: drift = 0 for lanes 9-15")
    elif overall_accuracy >= 90:
        print(f"\n🔥 Very close! {overall_accuracy:.1f}% accuracy")
        print(f"   Minor discrepancies to investigate")
    else:
        print(f"\n⚠️  Lower accuracy than expected: {overall_accuracy:.1f}%")
        print(f"   Hypothesis may need refinement")

    # Save results
    output = {
        'method': 'drift_zero_lanes_9_15',
        'formula': 'X_{k+1}[lane] = X_k[lane]^n mod 256 (drift=0)',
        'lanes_generated': list(range(9, 16)),
        'puzzles_range': '71-95',
        'total_puzzles': len(generated),
        'verification': {
            'bridges_checked': list(verification_results.keys()),
            'overall_accuracy': overall_accuracy,
            'total_matches': total_matches,
            'total_lanes': total_lanes,
            'per_bridge': verification_results
        },
        'generated_puzzles': generated
    }

    output_file = Path('generated_lanes_9_15_puzzles_71_95.json')
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Saved results: {output_file}")

    print(f"\n{'='*70}")
    print("CONCLUSION")
    print(f"{'='*70}")

    if overall_accuracy == 100:
        print("\n✅ Research confirmed!")
        print("   - Lanes 9-15 have drift = 0")
        print("   - Can generate these lanes for puzzles 71-95")
        print("   - Formula is mathematically correct")
        print("\n⚠️  Note: Lanes 0-8 still unknown (complex drift)")
        print("   - Generated puzzles are PARTIAL (7/16 lanes)")
        print("   - Cannot generate complete 256-bit keys")
    else:
        print(f"\n⚠️  Accuracy: {overall_accuracy:.1f}%")
        print("   Hypothesis needs refinement")

    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    main()
