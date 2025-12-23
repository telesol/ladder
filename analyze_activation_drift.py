#!/usr/bin/env python3
"""
Analyze Actual Drift Values for Lanes 9-15 During Activation Phase

Key Discovery: Lanes 9-15 were dormant (value=0) in puzzles 1-70,
but activate with NON-ZERO values in puzzles 71-95.

This script extracts the ACTUAL drift values from bridge data to
understand the activation phase pattern.
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

def calculate_drift(X_k, X_next, lane):
    """
    Calculate drift for a specific lane

    Formula: drift = (X_{k+1}[lane] - X_k[lane]^n) mod 256
    """
    n = EXPONENTS[lane]
    expected = pow(X_k[lane], n, 256)
    drift = (X_next[lane] - expected) % 256
    return drift

def main():
    print("="*70)
    print("ACTIVATION PHASE DRIFT ANALYSIS")
    print("="*70)
    print("\nAnalyzing ACTUAL drift values for lanes 9-15 from bridges\n")

    # Load CSV data
    csv_file = Path('data/btc_puzzle_1_160_full.csv')
    print(f"Loading CSV: {csv_file}")
    puzzles = load_csv_data(csv_file)
    print(f"✓ Loaded {len(puzzles)} known puzzles\n")

    # Bridge pairs to analyze
    bridges = [(70, 75), (75, 80), (80, 85), (85, 90), (90, 95)]

    print("="*70)
    print("EXTRACTING DRIFT VALUES FROM BRIDGES")
    print("="*70)

    all_drift_data = []

    for k_start, k_end in bridges:
        steps = k_end - k_start

        if k_start not in puzzles or k_end not in puzzles:
            print(f"\n⚠️  Missing data: {k_start}→{k_end}")
            continue

        X_start = halfblock_to_bytes(puzzles[k_start])
        X_end = halfblock_to_bytes(puzzles[k_end])

        print(f"\nBridge {k_start}→{k_end} ({steps} steps):")
        print(f"  X_{k_start} lanes 9-15: {list(X_start[9:16])}")
        print(f"  X_{k_end} lanes 9-15: {list(X_end[9:16])}")

        # For multi-step transition, we need to calculate cumulative drift
        # But first, let's see what the single-step drift would be
        print(f"\n  Single-step drift (as if {k_start}→{k_end} was one step):")

        drift_values = []
        for lane in range(9, 16):
            drift = calculate_drift(X_start, X_end, lane)
            drift_values.append(drift)

            activation_k = lane * 8
            status = ""
            if k_end <= activation_k:
                status = "dormant"
            elif k_start < activation_k <= k_end:
                status = f"ACTIVATES at k={activation_k}"
            else:
                status = "active"

            print(f"    Lane {lane}: drift={drift:3d} (0x{drift:02x}) - {status}")

        all_drift_data.append({
            'bridge': f"{k_start}→{k_end}",
            'k_start': k_start,
            'k_end': k_end,
            'steps': steps,
            'X_start_lanes_9_15': list(X_start[9:16]),
            'X_end_lanes_9_15': list(X_end[9:16]),
            'drift_values': drift_values
        })

    # Analyze patterns
    print(f"\n{'='*70}")
    print("PATTERN ANALYSIS")
    print(f"{'='*70}")

    print("\nLane Activation Schedule:")
    for lane in range(9, 16):
        activation_k = lane * 8
        print(f"  Lane {lane}: Activates at k={activation_k} (puzzle {activation_k})")

    print("\nDrift Pattern Analysis:")
    for lane in range(9, 16):
        print(f"\n  Lane {lane}:")
        drift_sequence = []
        for bridge_data in all_drift_data:
            k_start = bridge_data['k_start']
            k_end = bridge_data['k_end']
            drift = bridge_data['drift_values'][lane - 9]

            activation_k = lane * 8
            if k_end <= activation_k:
                phase = "dormant"
            elif k_start < activation_k <= k_end:
                phase = "ACTIVATION"
            else:
                phase = "active"

            drift_sequence.append(drift)
            print(f"    Bridge {k_start:2d}→{k_end:2d}: drift={drift:3d} ({phase})")

        # Check if drift is constant
        unique_drifts = set(drift_sequence)
        if len(unique_drifts) == 1:
            print(f"    → CONSTANT drift = {drift_sequence[0]}")
        else:
            print(f"    → VARYING drift: {unique_drifts}")

    # Save results
    output = {
        'analysis': 'activation_phase_drift',
        'bridges_analyzed': [f"{k}→{k+5}" for k, _ in bridges],
        'lane_activation_schedule': {
            f"lane_{lane}": lane * 8 for lane in range(9, 16)
        },
        'drift_data': all_drift_data
    }

    output_file = Path('activation_drift_analysis.json')
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Saved results: {output_file}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    print("\nKey Findings:")
    print("1. Bridge transitions are 5-step intervals (70→75, 75→80, etc.)")
    print("2. Lane activations occur at k = lane*8:")
    print("   - Lane 9 activates at k=72 (between bridges 70 and 75)")
    print("   - Lane 10 activates at k=80 (exactly at bridge 80)")
    print("   - Lane 11 activates at k=88 (between bridges 85 and 90)")
    print("   - Etc.")
    print("\n3. Multi-step drift calculation needed:")
    print("   - Cannot use single-step drift formula for 5-step transitions")
    print("   - Need to compute step-by-step through k=71, 72, 73, 74, 75")
    print("   - Activation happens MID-BRIDGE")

    print("\n4. The 'drift=0' finding from H1/H4 research:")
    print("   ✓ TRUE for dormant phase (puzzles 1-70, lanes inactive)")
    print("   ? UNKNOWN for active phase (puzzles 71+, lanes activated)")
    print("   - Need single-step drift data to verify")

    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    main()
