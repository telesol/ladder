#!/usr/bin/env python3
"""
Generate Puzzles 71-95 Using Proven Affine Recurrence

This script uses the VERIFIED formula:
X_{k+1}(ℓ) = A_ℓ * X_k(ℓ) + C(ℓ) (mod 256)

We have 100% accuracy on puzzles 1-70.

Challenge: We need drift values for transitions 70→71, 71→72, ..., 94→95
But the calibration file only has drifts up to 69→70.

Strategy:
1. Check if there's a pattern in the drifts
2. Analyze how drifts evolve as puzzles grow
3. Calculate drifts for transitions 70→71 and beyond
"""

import json
import csv
from pathlib import Path
from typing import Dict

def load_calibration(calib_path: str) -> dict:
    """Load calibration from JSON file."""
    with open(calib_path, 'r') as f:
        return json.load(f)


def analyze_drift_pattern(calib: dict):
    """
    Analyze how drifts evolve across transitions.

    Looking for patterns like:
    - Do drifts increase/decrease systematically?
    - Are there repeating patterns?
    - Can we model drift as a function of puzzle number?
    """
    print(f"\n{'='*80}")
    print(f"Analyzing Drift Patterns")
    print(f"{'='*80}\n")

    drifts_dict = calib['drifts']

    # Extract drift values for each lane across all transitions
    lane_drifts = {lane: [] for lane in range(16)}

    # Parse transitions in order
    for puzzle_num in range(1, 70):
        transition_key = f"{puzzle_num}→{puzzle_num+1}"
        if transition_key in drifts_dict:
            drifts = drifts_dict[transition_key]
            for lane in range(16):
                lane_drifts[lane].append(drifts[str(lane)])

    # Analyze each lane
    print(f"📊 Per-Lane Drift Analysis:\n")
    for lane in range(16):
        values = lane_drifts[lane]
        if not values:
            continue

        # Find when this lane becomes non-zero
        first_nonzero = next((i for i, v in enumerate(values) if v != 0), None)

        if first_nonzero is None:
            print(f"Lane {lane:2d}: Always zero")
        else:
            nonzero_count = sum(1 for v in values if v != 0)
            print(f"Lane {lane:2d}: First non-zero at puzzle {first_nonzero+1}, {nonzero_count}/{len(values)} non-zero")

            # Show last few values
            last_5 = values[-5:]
            print(f"         Last 5 drifts: {last_5}")

            # Check if drift is increasing
            if len(values) >= 2:
                increasing = all(values[i] <= values[i+1] or values[i+1] == 0
                                  for i in range(len(values)-1) if values[i] != 0)
                if increasing:
                    print(f"         Pattern: Appears to be increasing")

    # Special analysis for lane 0 (most active)
    print(f"\n{'='*80}")
    print(f"Lane 0 Detailed Analysis (Rightmost Byte)")
    print(f"{'='*80}\n")

    lane0_drifts = lane_drifts[0]
    print(f"First 10 drifts: {lane0_drifts[:10]}")
    print(f"Last 10 drifts:  {lane0_drifts[-10:]}")

    # Check for patterns
    print(f"\nPattern Analysis:")
    print(f"   Min drift: {min(lane0_drifts)}")
    print(f"   Max drift: {max(lane0_drifts)}")
    print(f"   Non-zero count: {sum(1 for v in lane0_drifts if v != 0)}/{len(lane0_drifts)}")

    # Check differences
    diffs = [lane0_drifts[i+1] - lane0_drifts[i] for i in range(len(lane0_drifts)-1)]
    print(f"\n   Drift differences (Δ):")
    print(f"   First 10: {diffs[:10]}")
    print(f"   Last 10:  {diffs[-10:]}")

    print(f"\n{'='*80}\n")

    return lane_drifts


def predict_next_drift(lane_drifts: Dict[int, list], last_puzzle_num: int) -> dict:
    """
    Calculate drift for the NEXT transition.

    This is the HARD PART - we need to understand the pattern.

    For now, let's try simple heuristics:
    1. If lane has been zero, keep it zero
    2. If lane has pattern, extrapolate it
    3. Use last value as baseline
    """
    predicted_drift = {}

    for lane in range(16):
        values = lane_drifts[lane]
        if not values:
            predicted_drift[lane] = 0
            continue

        # Simple heuristic: use last value
        # (This is naive - real pattern is likely more complex)
        last_value = values[-1]
        predicted_drift[lane] = last_value

        # TODO: Implement better calculation
        # - Analyze growth rate
        # - Check for cyclic patterns
        # - Use multi-precision arithmetic rules

    return predicted_drift


def main():
    """Analyze drift patterns to prepare for generation."""
    print("="*80)
    print("Generate Puzzles 71-95: Drift Analysis")
    print("="*80)

    # Load calibration
    base_path = Path(__file__).parent.parent.parent.parent
    calib_path = base_path / "out" / "ladder_calib_1_70_complete.json"

    print(f"\n📂 Loading calibration...")
    print(f"   Path: {calib_path}")

    calib = load_calibration(calib_path)
    print(f"✅ Loaded calibration for range {calib['range']}")

    # Analyze drift patterns
    lane_drifts = analyze_drift_pattern(calib)

    # Calculate next drift (for 70→71)
    print(f"\n{'='*80}")
    print(f"Calculation Attempt: Drift for 70→71")
    print(f"{'='*80}\n")

    calculated = predict_next_drift(lane_drifts, 70)
    print(f"Calculated drift (naive - using last values):")
    for lane in range(16):
        print(f"   Lane {lane:2d}: {calculated[lane]:3d}")

    print(f"\n{'='*80}")
    print(f"CRITICAL QUESTION")
    print(f"{'='*80}\n")
    print(f"❓ How do we determine drifts for puzzles 71-95?")
    print(f"\n   Options:")
    print(f"   1. Analyze drift growth pattern (mathematical model)")
    print(f"   2. Check if puzzle 75, 80, 85, 90, 95 are known (bridge rows)")
    print(f"   3. Use multi-precision arithmetic to compute carries")
    print(f"   4. Reverse-engineer from known solutions (if available)")
    print(f"\n   🧠 The old AI mentions 'bridge rows' at bits 75, 80, 85, 90, 95")
    print(f"   🧠 These might be KNOWN values we can use to compute drifts!")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
