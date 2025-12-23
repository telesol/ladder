#!/usr/bin/env python3
"""
VERIFY: Is drift really zero across bridges, or is there a deeper structure?

Finding: 92.1% of bridge lanes can be explained by constant drift = 0
Question: What does this mean structurally?

Theory 1: Drift becomes 0 after puzzle 70 (phase change)
Theory 2: Bridges are chosen to have this property (selection)
Theory 3: Multi-step accumulation appears as drift=0 (mathematical structure)
"""

import json
import csv
from pathlib import Path

# Constants
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

def halfblock_to_bytes(hex_str):
    """Convert hex to 16 bytes (REVERSED)"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    hex_str = hex_str[:32].zfill(32)
    return bytes.fromhex(hex_str)[::-1]

def verify_pure_exponential(X_start, X_end, steps, lane):
    """
    Verify if X_end = X_start^(n^steps) mod 256

    If drift = 0 at each step:
    X_1 = X_0^n
    X_2 = X_1^n = X_0^(n²)
    X_3 = X_2^n = X_0^(n³)
    ...
    X_steps = X_0^(n^steps)
    """
    n = EXPONENTS[lane]

    if n == 0:
        # Lane 6: if n=0, X stays constant (unless drift != 0)
        return X_start == X_end, 'constant' if X_start == X_end else 'needs_drift'

    # Calculate n^steps mod φ(256) where φ(256) = 128 (Euler's totient)
    # For modular exponentiation, we need: a^(b^c) mod m

    # Actually, let's just simulate step by step with drift=0
    X_current = X_start
    for _ in range(steps):
        X_current = pow(X_current, n, 256)

    matches = (X_current == X_end)
    return matches, 'pure_exponential' if matches else 'needs_drift'

def extract_actual_multi_step_drift(X_start, X_end, steps, lane):
    """
    For lanes that DON'T work with drift=0, what drift values would work?

    This is UNDERDETERMINED - there are many solutions!
    But we can find ONE solution by trying different drift patterns.
    """
    n = EXPONENTS[lane]

    # Try constant drift
    for drift in range(256):
        X_current = X_start
        for _ in range(steps):
            X_current = (pow(X_current, n, 256) + drift) % 256
        if X_current == X_end:
            return drift, 'constant_drift'

    # No constant drift solution found
    # Try linear drift: drift = k * step_num (mod 256)
    # This is too complex for now - mark as complex
    return None, 'complex_drift'

def main():
    print("="*70)
    print("VERIFICATION: Drift = 0 Hypothesis")
    print("="*70)
    print("\nTesting if bridge transitions are pure exponential cascades\n")

    # Load data
    csv_file = Path('data/btc_puzzle_1_160_full.csv')
    print(f"Loading CSV: {csv_file}")
    puzzles = {}
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['key_hex'] != '?':
                puzzles[int(row['puzzle'])] = row['key_hex_64']
    print(f"✓ Loaded {len(puzzles)} known puzzles\n")

    # Bridges
    bridges = [(70, 75), (75, 80), (80, 85), (85, 90), (90, 95),
               (95, 100), (100, 105), (105, 110), (110, 115),
               (115, 120), (120, 125), (125, 130)]

    print(f"{'='*70}")
    print("LANE-BY-LANE VERIFICATION")
    print(f"{'='*70}\n")

    results = []

    for start_k, end_k in bridges:
        if start_k not in puzzles or end_k not in puzzles:
            continue

        X_start = halfblock_to_bytes(puzzles[start_k])
        X_end = halfblock_to_bytes(puzzles[end_k])
        steps = end_k - start_k

        print(f"\n--- Bridge {start_k}→{end_k} ({steps} steps) ---")

        bridge_result = {
            'start_k': start_k,
            'end_k': end_k,
            'steps': steps,
            'lanes': {}
        }

        pure_exponential_count = 0
        needs_drift_count = 0

        for lane in range(16):
            activation_k = lane * 8 if lane > 0 else 1

            if start_k < activation_k:
                # Dormant phase
                status = 'dormant'
                drift_value = None
            else:
                # Evolution/activation phase - test hypothesis
                matches, status = verify_pure_exponential(
                    X_start[lane], X_end[lane], steps, lane
                )

                if status == 'pure_exponential':
                    pure_exponential_count += 1
                    drift_value = 0
                elif status == 'constant':
                    pure_exponential_count += 1
                    drift_value = 0
                else:
                    # Needs drift - extract it
                    drift_value, drift_type = extract_actual_multi_step_drift(
                        X_start[lane], X_end[lane], steps, lane
                    )
                    needs_drift_count += 1
                    status = drift_type

            bridge_result['lanes'][lane] = {
                'x_start': X_start[lane],
                'x_end': X_end[lane],
                'exponent': EXPONENTS[lane],
                'status': status,
                'drift_value': drift_value,
                'activation_k': activation_k
            }

        print(f"  Pure exponential (drift=0): {pure_exponential_count}/16 lanes")
        print(f"  Needs drift: {needs_drift_count}/16 lanes")

        # Show lanes that need drift
        if needs_drift_count > 0:
            print(f"  Lanes requiring drift:")
            for lane in range(16):
                lane_result = bridge_result['lanes'][lane]
                if lane_result['status'] not in ['dormant', 'pure_exponential', 'constant']:
                    drift_val = lane_result['drift_value']
                    if drift_val is not None:
                        print(f"    Lane {lane}: drift={drift_val} ({lane_result['status']})")
                    else:
                        print(f"    Lane {lane}: COMPLEX drift pattern")

        results.append(bridge_result)

    # Summary statistics
    print(f"\n{'='*70}")
    print("SUMMARY STATISTICS")
    print(f"{'='*70}\n")

    total_lanes = 0
    pure_exponential_total = 0
    constant_drift_total = 0
    complex_drift_total = 0

    # Per-lane summary across all bridges
    lane_summary = {lane: {'pure': 0, 'constant_drift': 0, 'complex': 0, 'total': 0}
                    for lane in range(16)}

    for result in results:
        for lane in range(16):
            lane_result = result['lanes'][lane]
            status = lane_result['status']

            if status not in ['dormant']:
                total_lanes += 1
                lane_summary[lane]['total'] += 1

                if status in ['pure_exponential', 'constant']:
                    pure_exponential_total += 1
                    lane_summary[lane]['pure'] += 1
                elif status == 'constant_drift':
                    constant_drift_total += 1
                    lane_summary[lane]['constant_drift'] += 1
                else:
                    complex_drift_total += 1
                    lane_summary[lane]['complex'] += 1

    print(f"Total active lane transitions: {total_lanes}")
    print(f"Pure exponential (drift=0): {pure_exponential_total} ({100*pure_exponential_total/total_lanes:.1f}%)")
    print(f"Constant drift (≠0): {constant_drift_total} ({100*constant_drift_total/total_lanes:.1f}%)")
    print(f"Complex drift: {complex_drift_total} ({100*complex_drift_total/total_lanes:.1f}%)")

    print(f"\nPer-Lane Summary:")
    print(f"{'Lane':<6} {'Total':<7} {'Pure':<7} {'ConstDrift':<12} {'Complex':<10}")
    print("-" * 60)
    for lane in range(16):
        total = lane_summary[lane]['total']
        pure = lane_summary[lane]['pure']
        const_drift = lane_summary[lane]['constant_drift']
        complex_d = lane_summary[lane]['complex']

        if total > 0:
            print(f"Lane {lane:<2} {total:<7} {pure:<7} {const_drift:<12} {complex_d:<10}")

    # Save results
    output = {
        'hypothesis': 'drift_zero_after_puzzle_70',
        'bridges_analyzed': len(results),
        'total_lane_transitions': total_lanes,
        'pure_exponential_count': pure_exponential_total,
        'constant_drift_count': constant_drift_total,
        'complex_drift_count': complex_drift_total,
        'percentage_pure': 100 * pure_exponential_total / total_lanes if total_lanes > 0 else 0,
        'lane_summary': lane_summary,
        'detailed_results': results
    }

    output_file = Path('drift_zero_verification.json')
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Saved verification results: {output_file}")

    # Key findings
    print(f"\n{'='*70}")
    print("KEY STRUCTURAL FINDINGS")
    print(f"{'='*70}\n")

    if pure_exponential_total / total_lanes > 0.90:
        print("✓ FINDING 1: >90% of bridge transitions are PURE EXPONENTIAL")
        print("  → After puzzle 70, drift ≈ 0 for most lanes")
        print("  → System becomes nearly deterministic polynomial iterator")
        print()
        print("  Mathematical form: X_{k+5} = X_k^(n^5) mod 256")
        print("  → No drift needed for most lanes!")
        print()
        print("  Implication: MAJOR PHASE CHANGE at k=70")

    if complex_drift_total > 0:
        print(f"\n✓ FINDING 2: {complex_drift_total} lanes have COMPLEX drift patterns")
        print("  → These lanes don't follow simple exponential or constant drift")
        print("  → Analyze these specifically for hidden structure")

    if constant_drift_total > 0:
        print(f"\n✓ FINDING 3: {constant_drift_total} lanes use NON-ZERO constant drift")
        print("  → Not pure exponential, but still simple pattern")
        print("  → Document these drift values")

    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
