#!/usr/bin/env python3
"""
PROPER STRUCTURAL ANALYSIS: Explore drift patterns in bridges

NOT prediction - STRUCTURAL EXPLORATION!

What we're analyzing:
1. Extract "effective drift" from multi-step transitions (70→75, 75→80, etc.)
2. Compare 1-step drift (1-70) vs 5-step transitions (bridges)
3. Test if H1-H4 patterns hold across different step sizes
4. Understand drift evolution structure
"""

import json
import csv
from pathlib import Path
import numpy as np

# Constants
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

def halfblock_to_bytes(hex_str):
    """Convert hex to 16 bytes (REVERSED)"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    hex_str = hex_str[-32:].zfill(32)
    return bytes.fromhex(hex_str)[::-1]

def calculate_next_X(X_k_bytes, drift_bytes):
    """X_{k+1} = (X_k^n + drift) mod 256"""
    result = bytearray(16)
    for lane in range(16):
        x = X_k_bytes[lane]
        d = drift_bytes[lane]
        n = EXPONENTS[lane]
        x_pow_n = pow(x, n, 256)
        result[lane] = (x_pow_n + d) % 256
    return bytes(result)

def analyze_single_step_drift(calibration):
    """Analyze drift patterns from consecutive puzzles 1-70"""
    print("="*70)
    print("SINGLE-STEP DRIFT ANALYSIS (Puzzles 1-70)")
    print("="*70)

    transitions = calibration['transitions']

    # Organize by lane
    lane_drifts = {lane: [] for lane in range(16)}

    for trans in transitions:
        k = trans['from_puzzle']
        for lane in range(16):
            activation_k = lane * 8 if lane > 0 else 1
            if k >= activation_k:  # Evolution phase
                lane_drifts[lane].append({
                    'k': k,
                    'drift': trans['drifts'][lane]
                })

    # Statistics per lane
    print(f"\nLane-by-Lane Statistics (Evolution Phase Only):")
    print(f"{'Lane':<6} {'Samples':<8} {'Min':<6} {'Max':<6} {'Mean':<10} {'Std':<10}")
    print("-" * 60)

    lane_stats = {}
    for lane in range(16):
        if lane_drifts[lane]:
            values = [d['drift'] for d in lane_drifts[lane]]
            lane_stats[lane] = {
                'samples': len(values),
                'min': min(values),
                'max': max(values),
                'mean': np.mean(values),
                'std': np.std(values),
                'values': values
            }
            print(f"Lane {lane:<2} {len(values):<8} {min(values):<6} {max(values):<6} {np.mean(values):<10.2f} {np.std(values):<10.2f}")
        else:
            lane_stats[lane] = None
            print(f"Lane {lane:<2} {'N/A':<8} {'N/A':<6} {'N/A':<6} {'N/A':<10} {'N/A':<10}")

    return lane_stats

def explore_multi_step_structure(puzzles, start_k, end_k):
    """
    Explore the structure of multi-step transitions

    We have X_start and X_end, but NOT the intermediate steps.
    Question: What can we learn about the STRUCTURE?
    """
    X_start = halfblock_to_bytes(puzzles[start_k])
    X_end = halfblock_to_bytes(puzzles[end_k])
    steps = end_k - start_k

    results = {
        'start_k': start_k,
        'end_k': end_k,
        'steps': steps,
        'lanes': {}
    }

    # For each lane, analyze the transformation
    for lane in range(16):
        x_start = X_start[lane]
        x_end = X_end[lane]
        n = EXPONENTS[lane]
        activation_k = lane * 8 if lane > 0 else 1

        # Determine phase
        if start_k < activation_k:
            phase = 'dormant'
        elif start_k == activation_k:
            phase = 'activation'
        else:
            phase = 'evolution'

        results['lanes'][lane] = {
            'x_start': x_start,
            'x_end': x_end,
            'exponent': n,
            'phase': phase,
            'activation_k': activation_k
        }

        # If both in evolution phase, we can explore drift space
        if start_k >= activation_k and end_k >= activation_k:
            # Question: What constant drift would approximate this transition?
            # X_end ≈ (X_start^n + c_drift)^n + c_drift)^n ... (steps times)
            # This is NOT solvable, but we can test hypotheses

            # Simple approximation: average drift per step
            # This assumes drift is constant (which we know is wrong, but it's a baseline)

            if n == 0:
                # Lane 6: always stays 0
                approx_drift = 0
            else:
                # Try to find a constant drift
                # We'll test this by simulating
                approx_drift = None

                # Brute force search for constant drift (0-255)
                for test_drift in range(256):
                    X_current = x_start
                    for _ in range(steps):
                        X_current = (pow(X_current, n, 256) + test_drift) % 256
                    if X_current == x_end:
                        approx_drift = test_drift
                        break

                results['lanes'][lane]['constant_drift_solution'] = approx_drift

    return results

def main():
    print("="*70)
    print("STRUCTURAL EXPLORATION OF DRIFT ACROSS ALL 82 PUZZLES")
    print("="*70)
    print("\nApproach: ANALYZE structure, NOT predict unknowns")
    print("Goal: Understand drift evolution patterns\n")

    # Load data
    csv_file = Path('data/btc_puzzle_1_160_full.csv')
    calib_file = Path('drift_data_CORRECT_BYTE_ORDER.json')

    print(f"Loading CSV: {csv_file}")
    puzzles = {}
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['key_hex'] != '?':
                puzzles[int(row['puzzle'])] = row['key_hex_64']
    print(f"✓ Loaded {len(puzzles)} known puzzles\n")

    print(f"Loading calibration: {calib_file}")
    with open(calib_file) as f:
        calibration = json.load(f)
    print(f"✓ Loaded {len(calibration['transitions'])} transitions (1-70)\n")

    # STEP 1: Analyze single-step drift (baseline)
    lane_stats_1_70 = analyze_single_step_drift(calibration)

    # STEP 2: Explore multi-step structure
    print(f"\n{'='*70}")
    print("MULTI-STEP TRANSITION STRUCTURE (Bridges)")
    print(f"{'='*70}\n")

    bridges = [(70, 75), (75, 80), (80, 85), (85, 90), (90, 95),
               (95, 100), (100, 105), (105, 110), (110, 115),
               (115, 120), (120, 125), (125, 130)]

    bridge_results = []

    for start_k, end_k in bridges:
        if start_k not in puzzles or end_k not in puzzles:
            continue

        print(f"\n--- Bridge {start_k}→{end_k} ({end_k - start_k} steps) ---")

        result = explore_multi_step_structure(puzzles, start_k, end_k)
        bridge_results.append(result)

        # Show constant drift solutions (if they exist)
        print(f"  Constant drift solutions:")
        for lane in range(16):
            sol = result['lanes'][lane].get('constant_drift_solution')
            phase = result['lanes'][lane]['phase']
            if sol is not None:
                print(f"    Lane {lane}: drift={sol:3d} (phase: {phase})")
            elif phase == 'evolution':
                print(f"    Lane {lane}: NO constant solution (phase: {phase})")

    # STEP 3: Structural insights
    print(f"\n{'='*70}")
    print("STRUCTURAL INSIGHTS")
    print(f"{'='*70}\n")

    # Count how many lanes have constant drift solutions
    total_lanes_tested = 0
    lanes_with_constant_solution = 0

    for result in bridge_results:
        for lane in range(16):
            if result['lanes'][lane]['phase'] == 'evolution':
                total_lanes_tested += 1
                if result['lanes'][lane].get('constant_drift_solution') is not None:
                    lanes_with_constant_solution += 1

    print(f"Lanes in evolution phase across all bridges: {total_lanes_tested}")
    print(f"Lanes with constant drift solution: {lanes_with_constant_solution}")
    print(f"Percentage: {100 * lanes_with_constant_solution / total_lanes_tested if total_lanes_tested > 0 else 0:.1f}%")

    if lanes_with_constant_solution == 0:
        print("\n✓ FINDING: NO multi-step transitions can be explained by constant drift")
        print("  → Drift is NON-CONSTANT (changes at each step)")
        print("  → This is consistent with cryptographic design")
    else:
        print(f"\n✓ FINDING: {lanes_with_constant_solution} lanes have constant drift solutions")
        print("  → Analyze these lanes for patterns")

    # Save results
    output = {
        'single_step_stats': {
            lane: {k: (v.tolist() if isinstance(v, np.ndarray) else v)
                   for k, v in stats.items() if k != 'values'}
            for lane, stats in lane_stats_1_70.items() if stats is not None
        },
        'bridge_analysis': bridge_results
    }

    output_file = Path('bridge_structure_analysis.json')
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Saved structural analysis: {output_file}")

    print(f"\n{'='*70}")
    print("NEXT: Apply H1-H4 frameworks to bridge transitions")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
