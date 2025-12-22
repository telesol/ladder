#!/usr/bin/env python3
"""
Analyze the TRUE Drift Structure

Based on user's insight: Bridges were FORWARD GENERATED using math formula.

This script verifies if C is CONSTANT within each block/occurrence.

Expected structure:
- C[block][lane][occ] should be SAME for all transitions in that block/occ
- Should get ~64 unique drift values (16 lanes × 2 blocks × 2 occurrences)
- NOT 1,296 per-puzzle drifts!
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

def determine_block_and_occ(puzzle_k):
    """Determine block and occurrence for a puzzle."""
    if puzzle_k < 29:
        return None, None

    block = (puzzle_k - 29) // 32
    within_block = (puzzle_k - 29) % 32
    occ = within_block // 16

    return block, occ

def load_calibration_and_keys():
    """Load calibration and extract key bytes."""
    calib_path = Path(__file__).parent.parent.parent / "out" / "ladder_calib_ultimate.json"
    csv_path = Path(__file__).parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"

    with open(calib_path) as f:
        calib = json.load(f)

    df = pd.read_csv(csv_path)

    # Extract A coefficients
    A = [calib['A'][str(i)] for i in range(16)]

    # Extract key bytes for all puzzles (little-endian)
    puzzles = {}
    for _, row in df.iterrows():
        puzzle_num = row['puzzle']
        key_hex = row['key_hex_64']
        # Last 32 hex chars (16 bytes), reversed for little-endian
        key_bytes = bytes(reversed(bytes.fromhex(key_hex[32:64])))
        puzzles[puzzle_num] = key_bytes

    return calib, A, puzzles

def analyze_drift_constancy():
    """
    Check if drift is CONSTANT within each block/occurrence.

    If TRUE: Each (block, occ, lane) should have ONLY ONE drift value
    If FALSE: Need to find more complex pattern
    """
    print("="*80)
    print("ANALYZING DRIFT STRUCTURE")
    print("="*80)
    print()

    calib, A, puzzles = load_calibration_and_keys()

    # Store computed drifts: drift[block][occ][lane] = [list of values]
    drift_by_structure = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Also store which puzzles contributed to each
    puzzle_tracking = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    print("📊 Computing drift values from actual transitions...")
    print()

    # Analyze transitions in puzzles 29-70 (complete Block 0, partial Block 1)
    transition_count = 0
    for puzzle_k in range(29, 70):
        if puzzle_k not in puzzles or puzzle_k + 1 not in puzzles:
            continue

        block, occ = determine_block_and_occ(puzzle_k)
        if block is None:
            continue

        X_k = puzzles[puzzle_k]
        X_k_plus_1 = puzzles[puzzle_k + 1]

        for lane in range(16):
            # Compute drift from actual transition
            # X_{k+1} = A * X_k + C (mod 256)
            # Therefore: C = X_{k+1} - A * X_k (mod 256)

            A_lane = A[lane]
            X_current = X_k[lane]
            X_next = X_k_plus_1[lane]

            C = (X_next - (A_lane * X_current)) & 0xFF

            drift_by_structure[block][occ][lane].append(C)
            puzzle_tracking[block][occ][lane].append(puzzle_k)

        transition_count += 1

    print(f"✅ Analyzed {transition_count} transitions")
    print()

    # Now analyze: Is C constant within each (block, occ, lane)?
    print("="*80)
    print("DRIFT CONSTANCY ANALYSIS")
    print("="*80)
    print()

    total_groups = 0
    constant_groups = 0
    variable_groups = 0

    results = []

    for block in sorted(drift_by_structure.keys()):
        for occ in sorted(drift_by_structure[block].keys()):
            for lane in sorted(drift_by_structure[block][occ].keys()):
                C_values = drift_by_structure[block][occ][lane]
                unique_C = set(C_values)
                puzzles_list = puzzle_tracking[block][occ][lane]

                total_groups += 1

                if len(unique_C) == 1:
                    constant_groups += 1
                    status = "✅ CONSTANT"
                    C_value = list(unique_C)[0]
                else:
                    variable_groups += 1
                    status = "❌ VARIABLE"
                    C_value = f"{len(unique_C)} different values: {sorted(unique_C)}"

                results.append({
                    'block': block,
                    'occ': occ,
                    'lane': lane,
                    'status': status,
                    'C_value': C_value,
                    'num_transitions': len(C_values),
                    'puzzles': f"{min(puzzles_list)}-{max(puzzles_list)}"
                })

    # Show summary
    print(f"📊 Summary:")
    print(f"   Total (block, occ, lane) groups: {total_groups}")
    print(f"   CONSTANT drift: {constant_groups} ({constant_groups/total_groups*100:.1f}%)")
    print(f"   VARIABLE drift: {variable_groups} ({variable_groups/total_groups*100:.1f}%)")
    print()

    # Show detailed results for first few lanes
    print("="*80)
    print("DETAILED RESULTS (First 4 Lanes)")
    print("="*80)
    print()

    df_results = pd.DataFrame(results)

    for lane in range(4):
        lane_data = df_results[df_results['lane'] == lane]
        print(f"Lane {lane}:")
        print("-" * 80)
        for _, row in lane_data.iterrows():
            print(f"  Block {row['block']}, occ {row['occ']}: {row['status']}")
            print(f"    C = {row['C_value']}")
            print(f"    Transitions: {row['num_transitions']} (puzzles {row['puzzles']})")
        print()

    # If all are variable, show the pattern
    if variable_groups == total_groups:
        print("="*80)
        print("⚠️  ALL DRIFTS ARE VARIABLE!")
        print("="*80)
        print()
        print("This confirms: Drift is NOT simply C[block][occ][lane]")
        print()
        print("Possible explanations:")
        print("1. Drift depends on X_k (current state)")
        print("2. Drift is cryptographically generated (hash-based)")
        print("3. Drift is PRNG-seeded (pseudo-random)")
        print("4. Drift is calibrated backwards (lookup table)")
        print()
        print("The 1,296 drift values in calibration file are REAL, not redundant!")
        print()

    # If some are constant, show which
    elif constant_groups > 0:
        print("="*80)
        print("✅ SOME DRIFTS ARE CONSTANT!")
        print("="*80)
        print()
        print("Constant drift groups:")
        constant_df = df_results[df_results['status'] == "✅ CONSTANT"]
        print(constant_df[['block', 'occ', 'lane', 'C_value', 'num_transitions']])
        print()

    # Save full results
    output_path = Path(__file__).parent / "drift_structure_analysis.csv"
    df_results.to_csv(output_path, index=False)
    print(f"💾 Full results saved to: {output_path}")
    print()

    return df_results

if __name__ == "__main__":
    results = analyze_drift_constancy()
