#!/usr/bin/env python3
"""
Export drift data for drift generator discovery research.

This script extracts:
- All drift values (74 transitions × 16 lanes = 1,184 values)
- A coefficients
- X_k and X_k+1 states for each transition
- Metadata for analysis

Output: drift_data_export.json
"""

import json
import csv
from pathlib import Path

def extract_half_block(hex_key: str) -> list:
    """
    Extract the second half-block (right 32 hex chars = 16 bytes).
    Returns list of 16 integers.
    """
    # Take the right 32 characters (second half)
    if len(hex_key) == 64:
        half_block_hex = hex_key[32:64]
    else:
        # If shorter, pad with zeros on the left
        hex_key_padded = hex_key.zfill(64)
        half_block_hex = hex_key_padded[32:64]

    # Convert to 16 bytes
    return [int(half_block_hex[i:i+2], 16) for i in range(0, 32, 2)]

def main():
    # Paths
    calib_path = Path("out/ladder_calib_CORRECTED.json")
    csv_path = Path("data/btc_puzzle_1_160_full.csv")
    output_path = Path("drift_data_export.json")

    print(f"[1/4] Loading calibration file: {calib_path}")
    with open(calib_path) as f:
        calib = json.load(f)

    # Extract A coefficients
    A = [calib['A'][str(i)] for i in range(16)]
    print(f"  ✓ A coefficients: {A[:4]}... (16 values)")

    # Extract drifts
    drifts_dict = calib['drifts']
    print(f"  ✓ Drift transitions: {len(drifts_dict)}")

    print(f"\n[2/4] Loading CSV file: {csv_path}")
    puzzles = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            puzzle_num = int(row['puzzle'])
            if puzzle_num <= 95:  # Include bridge puzzles
                puzzles[puzzle_num] = {
                    'puzzle': puzzle_num,
                    'key_hex': row['key_hex_64'],
                    'address': row['address']
                }

    print(f"  ✓ Loaded {len(puzzles)} puzzles (1-70 + bridges 75,80,85,90,95)")

    print(f"\n[3/4] Building transition data")
    transitions = []

    # Parse drift keys like "1→2"
    for drift_key, drift_values in sorted(drifts_dict.items()):
        # Parse "k→k+1" format
        parts = drift_key.split('→')
        if len(parts) == 2:
            from_puzzle = int(parts[0])
            to_puzzle = int(parts[1])
        else:
            print(f"  ⚠ Skipping malformed drift key: {drift_key}")
            continue

        # Get X_k and X_k+1 states
        if from_puzzle in puzzles and to_puzzle in puzzles:
            X_k = extract_half_block(puzzles[from_puzzle]['key_hex'])
            X_k_plus_1 = extract_half_block(puzzles[to_puzzle]['key_hex'])

            # Get drift values (convert from dict to list)
            drifts = [drift_values[str(i)] for i in range(16)]

            transitions.append({
                'from_puzzle': from_puzzle,
                'to_puzzle': to_puzzle,
                'drifts': drifts,
                'X_k': X_k,
                'X_k_plus_1': X_k_plus_1
            })

    print(f"  ✓ Created {len(transitions)} transitions")

    # Separate regular transitions (1-70) and bridges
    regular_transitions = [t for t in transitions if t['to_puzzle'] <= 70]
    bridge_transitions = [t for t in transitions if t['to_puzzle'] > 70]

    print(f"    • Regular transitions (1→2 through 69→70): {len(regular_transitions)}")
    print(f"    • Bridge transitions (70→75, 75→80, etc.): {len(bridge_transitions)}")

    print(f"\n[4/4] Exporting data")
    output_data = {
        'metadata': {
            'description': 'Drift data for generator discovery research',
            'total_transitions': len(transitions),
            'regular_transitions': len(regular_transitions),
            'bridge_transitions': len(bridge_transitions),
            'total_drift_values': len(transitions) * 16,
            'lanes_per_transition': 16
        },
        'A_coefficients': A,
        'transitions': transitions,
        'formula': 'X_{k+1}[lane] = (A[lane]^4 * X_k[lane] + drift[k→k+1][lane]) mod 256'
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"  ✓ Exported to: {output_path}")
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Transitions:     {len(transitions)}")
    print(f"Drift values:    {len(transitions) * 16}")
    print(f"A coefficients:  16")
    print(f"File size:       {output_path.stat().st_size / 1024:.1f} KB")
    print(f"{'='*60}")
    print(f"\n✅ Data export complete! Ready for distributed research.")

    # Show sample transition
    if transitions:
        sample = transitions[0]
        print(f"\nSample transition (puzzle {sample['from_puzzle']}→{sample['to_puzzle']}):")
        print(f"  Drifts:  {sample['drifts'][:4]}... (16 values)")
        print(f"  X_k:     {sample['X_k'][:4]}... (16 bytes)")
        print(f"  X_k+1:   {sample['X_k_plus_1'][:4]}... (16 bytes)")

if __name__ == '__main__':
    main()
