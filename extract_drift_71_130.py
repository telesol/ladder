#!/usr/bin/env python3
"""
Extract drift values for transitions 70→71 through 129→130

This gives us 60 NEW drift samples to add to our existing 69!
Total: 129 transitions (1→70 + 70→130)
"""

import json
import csv
from pathlib import Path

# Constants
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

def halfblock_to_bytes(hex_str):
    """Convert hex to 16 bytes (REVERSED byte order)"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    hex_str = hex_str[-32:].zfill(32)
    return bytes.fromhex(hex_str)[::-1]

def extract_drift(X_k_bytes, X_k_plus_1_bytes):
    """Extract drift: drift = X_{k+1} - X_k^n (mod 256)"""
    drift = []
    for lane in range(16):
        x_k = X_k_bytes[lane]
        x_k_plus_1 = X_k_plus_1_bytes[lane]
        n = EXPONENTS[lane]

        # Calculate x^n mod 256
        x_pow_n = pow(x_k, n, 256)

        # drift = X_{k+1} - X_k^n (mod 256)
        d = (x_k_plus_1 - x_pow_n) % 256
        drift.append(d)

    return drift

def main():
    print("="*70)
    print("DRIFT EXTRACTION: Puzzles 71-130")
    print("="*70)

    # Load CSV
    csv_file = Path('data/btc_puzzle_1_160_full.csv')
    print(f"\nLoading CSV: {csv_file}")

    puzzles = {}
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            puzzle_id = int(row['puzzle'])
            puzzles[puzzle_id] = {
                'address': row['address'],
                'key_hex_64': row['key_hex_64']
            }

    print(f"✓ Loaded {len(puzzles)} puzzles")

    # Extract drift for transitions 70→71 through 129→130
    print(f"\nExtracting drift transitions 70→130...")

    transitions = []
    for k in range(70, 130):
        if k not in puzzles or k+1 not in puzzles:
            print(f"  ⚠️  Missing puzzle {k} or {k+1}")
            continue

        X_k = halfblock_to_bytes(puzzles[k]['key_hex_64'])
        X_k_plus_1 = halfblock_to_bytes(puzzles[k+1]['key_hex_64'])

        drift = extract_drift(X_k, X_k_plus_1)

        transitions.append({
            'from_puzzle': k,
            'to_puzzle': k + 1,
            'drifts': drift
        })

        # Show first few
        if k <= 72 or k == 129:
            print(f"  ✓ Transition {k}→{k+1}: drift = {drift[:4]}... ({sum(1 for d in drift if d > 0)} active lanes)")

    print(f"\n✓ Extracted {len(transitions)} transitions")

    # Load existing calibration (1-70)
    existing_calib_file = Path('drift_data_CORRECT_BYTE_ORDER.json')
    if existing_calib_file.exists():
        print(f"\nLoading existing calibration: {existing_calib_file}")
        with open(existing_calib_file) as f:
            existing_data = json.load(f)
        existing_transitions = existing_data.get('transitions', [])
        print(f"  ✓ Existing: {len(existing_transitions)} transitions (puzzles 1-70)")
    else:
        existing_transitions = []
        print(f"  ⚠️  No existing calibration found")

    # Combine
    all_transitions = existing_transitions + transitions
    print(f"\n✓ Total transitions: {len(all_transitions)} (1→130)")

    # Save extended calibration
    output_file = Path('drift_data_1_to_130.json')
    output_data = {
        'byte_order': 'REVERSED',
        'source': 'btc_puzzle_1_160_full.csv',
        'transitions': all_transitions,
        'total_drift_values': len(all_transitions) * 16,
        'range': '1→130',
        'extracted_date': '2025-12-23'
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✓ Saved extended calibration: {output_file}")

    # Statistics
    print(f"\n{'='*70}")
    print("STATISTICS")
    print(f"{'='*70}")

    # Count active drifts per lane
    lane_stats = {lane: {'total': 0, 'nonzero': 0, 'values': []} for lane in range(16)}

    for trans in all_transitions:
        k = trans['from_puzzle']
        for lane in range(16):
            drift_val = trans['drifts'][lane]
            activation_k = lane * 8 if lane > 0 else 1

            if k >= activation_k:  # Evolution phase
                lane_stats[lane]['total'] += 1
                if drift_val != 0:
                    lane_stats[lane]['nonzero'] += 1
                lane_stats[lane]['values'].append(drift_val)

    print(f"\nPer-Lane Evolution Statistics (k > lane×8):")
    print(f"{'Lane':<6} {'Samples':<8} {'NonZero':<10} {'Range':<15} {'Mean':<10}")
    print("-" * 60)

    for lane in range(16):
        total = lane_stats[lane]['total']
        nonzero = lane_stats[lane]['nonzero']
        values = lane_stats[lane]['values']

        if total > 0:
            min_val = min(values)
            max_val = max(values)
            mean_val = sum(values) / len(values)
            print(f"Lane {lane:<2} {total:<8} {nonzero:<10} [{min_val:3d}, {max_val:3d}]  {mean_val:8.1f}")
        else:
            print(f"Lane {lane:<2} {total:<8} {'N/A':<10} {'N/A':<15} {'N/A':<10}")

    # Compare old vs new
    print(f"\n{'='*70}")
    print("COMPARISON: Old (1-70) vs Extended (1-130)")
    print(f"{'='*70}")

    old_count = len(existing_transitions)
    new_count = len(transitions)
    total_count = len(all_transitions)

    print(f"Previous dataset: {old_count} transitions (puzzles 1-70)")
    print(f"New additions:    {new_count} transitions (puzzles 70-130)")
    print(f"Total dataset:    {total_count} transitions (puzzles 1-130)")
    print(f"Increase:         +{(new_count/old_count)*100:.1f}%")

    # Evolution samples
    old_evolution = sum(1 for t in existing_transitions for lane in range(16)
                       if t['drifts'][lane] > 0 or t['from_puzzle'] > lane * 8)
    new_evolution = sum(1 for t in transitions for lane in range(16)
                       if t['drifts'][lane] > 0 or t['from_puzzle'] > lane * 8)

    print(f"\nEvolution samples:")
    print(f"  Previous: ~332 (estimated)")
    print(f"  New:      ~{new_evolution} (calculated)")
    print(f"  Total:    ~{old_evolution + new_evolution}")

    print(f"\n{'='*70}")
    print("READY FOR NEW TRAINING!")
    print(f"{'='*70}")
    print(f"\nNext steps:")
    print(f"1. Re-run unified PySR with 129 transitions (was 69)")
    print(f"2. Re-run per-lane PySR with ~2x more data")
    print(f"3. Higher chance of discovering formula!")
    print(f"\n✅ Drift extraction complete!")

if __name__ == "__main__":
    main()
