#!/usr/bin/env python3
"""
Extract Actual Drift from Bridges
==================================

Extract real drift values from known bridge transitions:
- 70→75 (5 steps, but we can compute per-step drift from endpoints)
- 75→80 (5 steps)
- 80→85 (5 steps)
- 85→90 (5 steps)
- 90→95 (5 steps)

This shows us ACTUAL drift patterns vs our predictions.
"""

import json
import csv
from pathlib import Path

def load_A_values():
    """Load A values from calibration"""
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        calib = json.load(f)
    return [calib['A'][str(i)] for i in range(16)]

def hex_to_bytes(hex_str):
    """Convert hex string to byte list"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    if len(hex_str) > 32:
        hex_str = hex_str[32:64]
    hex_str = hex_str.zfill(32)
    return [int(hex_str[i:i+2], 16) for i in range(0, 32, 2)]

def bytes_to_hex(byte_list):
    """Convert byte list to hex string"""
    return ''.join(f'{b:02x}' for b in byte_list)

def load_puzzle(n):
    """Load puzzle from CSV"""
    with open('data/btc_puzzle_1_160_full.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[0] == str(n) and row[3] and row[3] != '?':
                return hex_to_bytes(row[3])
    return None

def compute_single_step_drift(X_k, X_k1, A):
    """
    Compute drift for a single transition k→k+1
    Given: X_{k+1} = A^4 * X_k + drift (mod 256)
    Solve: drift = X_{k+1} - A^4 * X_k (mod 256)
    """
    drift = []
    for lane in range(16):
        a4 = pow(A[lane], 4, 256)
        d = (X_k1[lane] - a4 * X_k[lane]) % 256
        drift.append(d)
    return drift

def analyze_bridge_drift():
    """Extract and analyze drift from bridge points"""

    print("=" * 80)
    print("EXTRACTING ACTUAL DRIFT FROM BRIDGES")
    print("=" * 80)
    print()

    A = load_A_values()
    print(f"A values: {A}")
    print()

    # Load all bridge points
    bridges = [70, 75, 80, 85, 90, 95]
    X_values = {}

    print("Loading bridge puzzles...")
    for n in bridges:
        X = load_puzzle(n)
        if X:
            X_values[n] = X
            print(f"  X_{n}: {bytes_to_hex(X)}")
        else:
            print(f"  X_{n}: NOT FOUND")
    print()

    # For each bridge pair, we know endpoints but not intermediate steps
    # We can compute AVERAGE drift per step, but not individual drifts

    print("=" * 80)
    print("SINGLE-STEP DRIFT EXTRACTION")
    print("=" * 80)
    print()
    print("Note: For bridges (5-step gaps), we can only compute AVERAGE drift")
    print("      To get actual per-step drift, we need intermediate values.")
    print()

    bridge_pairs = [(70, 75), (75, 80), (80, 85), (85, 90), (90, 95)]

    results = {
        'bridge_drift_analysis': {},
        'observations': []
    }

    for start, end in bridge_pairs:
        if start not in X_values or end not in X_values:
            print(f"Bridge {start}→{end}: CANNOT COMPUTE (missing data)")
            continue

        print("=" * 80)
        print(f"BRIDGE {start}→{end}")
        print("=" * 80)
        print()

        X_start = X_values[start]
        X_end = X_values[end]

        print(f"X_{start}: {bytes_to_hex(X_start)}")
        print(f"X_{end}:  {bytes_to_hex(X_end)}")
        print()

        # Try to work backwards from end to find what single-step drift would give
        # But this only works if drift is constant across all 5 steps

        # Let's check: what if we had constant drift d?
        # After 5 steps: X_{k+5} = A^20 * X_k + d * (A^16 + A^12 + A^8 + A^4 + 1)
        # Solving for d requires modular inverse...

        # Instead, let's just see lane-by-lane what happened
        print("Lane | X_start | X_end | Delta | Notes")
        print("-" * 70)

        for lane in range(16):
            x_s = X_start[lane]
            x_e = X_end[lane]
            delta = (x_e - x_s) % 256

            # Check if pure polynomial (no drift) would explain it
            a4 = pow(A[lane], 4, 256)
            a20 = pow(A[lane], 20, 256)

            # Expected without drift: X_end = A^20 * X_start
            expected_no_drift = (a20 * x_s) % 256

            if x_e == expected_no_drift:
                notes = "✓ No drift needed"
            else:
                diff = (x_e - expected_no_drift) % 256
                notes = f"Needs drift (Δ={diff})"

            print(f"{lane:4} | {x_s:7} | {x_e:5} | {delta:5} | {notes}")

        print()

        results['bridge_drift_analysis'][f'{start}→{end}'] = {
            'X_start': bytes_to_hex(X_start),
            'X_end': bytes_to_hex(X_end),
            'steps': 5
        }

    # Key observation: Check if pattern changed
    print("=" * 80)
    print("KEY OBSERVATIONS")
    print("=" * 80)
    print()

    # Compare lanes 9-15 across bridges
    print("Lanes 9-15 (zero-drift in puzzles 1-70):")
    print()
    for n in bridges:
        if n in X_values:
            X = X_values[n]
            lane_vals = [X[i] for i in range(9, 16)]
            all_zero = all(v == 0 for v in lane_vals)
            print(f"  X_{n} lanes 9-15: {lane_vals} {'(all zero)' if all_zero else '(NON-ZERO!)'}")

    results['observations'].append({
        'finding': 'Lanes 9-15 transition from zero to non-zero at higher puzzles',
        'impact': 'Drift pattern changes - cannot extrapolate from puzzles 1-70'
    })

    print()
    print("CONCLUSION:")
    print("  - Lanes 9-15 are ZERO in puzzles ≤70")
    print("  - Lanes 9-15 are NON-ZERO in puzzles ≥75")
    print("  - This means drift pattern CHANGES around puzzle 70-75")
    print("  - Cannot use drift from 1-70 to predict 71+")
    print()

    # Save results
    with open('results/bridge_drift_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Results saved to: results/bridge_drift_analysis.json")
    print()

    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("To get actual per-step drift for bridges, we need:")
    print("  1. Find intermediate values (puzzles 71-74, 76-79, etc.) OR")
    print("  2. Discover the drift generator function OR")
    print("  3. Use ML to predict drift based on puzzle index and patterns")
    print()

if __name__ == '__main__':
    analyze_bridge_drift()
