#!/usr/bin/env python3
"""
Prepare Training Data for Local AI

This script prepares data for PySR to LEARN the ladder pattern.

For each lane (0-15), we create training examples:
    Input:  (X_k[lane], puzzle_k)
    Output: X_{k+1}[lane]

The AI will discover the relationship: f(X_k, k) → X_{k+1}
"""

import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List


def load_puzzles_from_csv(csv_path: str, max_puzzle: int = 70) -> Dict[int, bytes]:
    """
    Load puzzles from CSV (little-endian format for formula).

    Args:
        csv_path: Path to CSV file
        max_puzzle: Maximum puzzle number to load (default: 70 for training)

    Returns:
        Dict mapping puzzle_num -> 16 bytes (little-endian)
    """
    puzzles = {}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                puzzle_num = int(row['puzzle'])
            except ValueError:
                continue

            if puzzle_num > max_puzzle:
                continue

            key_hex_64 = row['key_hex_64'].strip()
            if len(key_hex_64) != 64:
                continue

            # Extract LAST 32 hex chars (last 16 bytes)
            last_32_hex = key_hex_64[32:64]
            big_endian_bytes = bytes.fromhex(last_32_hex)

            # Convert to little-endian (lane 0 = rightmost byte)
            little_endian_bytes = bytes(reversed(big_endian_bytes))

            puzzles[puzzle_num] = little_endian_bytes

    return puzzles


def create_per_lane_training_data(puzzles: Dict[int, bytes],
                                    output_dir: Path) -> Dict[int, pd.DataFrame]:
    """
    Create training data for each lane.

    For each lane L:
        - Input features: X_k[L], puzzle_k
        - Target: X_{k+1}[L]

    Args:
        puzzles: Dict of puzzle_num -> bytes
        output_dir: Directory to save per-lane CSV files

    Returns:
        Dict mapping lane_num -> DataFrame
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    lane_data = {lane: [] for lane in range(16)}

    # Create transitions (puzzle k → puzzle k+1)
    puzzle_nums = sorted(puzzles.keys())

    for i in range(len(puzzle_nums) - 1):
        k = puzzle_nums[i]
        k_plus_1 = puzzle_nums[i + 1]

        # Skip non-consecutive puzzles
        if k_plus_1 != k + 1:
            continue

        current = puzzles[k]
        next_puzzle = puzzles[k_plus_1]

        # For each lane, create training example
        for lane in range(16):
            X_k = current[lane]
            X_k_plus_1 = next_puzzle[lane]

            lane_data[lane].append({
                'puzzle_k': k,
                'X_k': X_k,
                'X_k+1': X_k_plus_1,
            })

    # Convert to DataFrames and save
    dfs = {}

    for lane in range(16):
        df = pd.DataFrame(lane_data[lane])
        dfs[lane] = df

        # Save to CSV
        output_path = output_dir / f"lane_{lane:02d}_train.csv"
        df.to_csv(output_path, index=False)

        print(f"Lane {lane:2d}: {len(df):3d} training examples → {output_path.name}")

    return dfs


def analyze_lane_data(lane_df: pd.DataFrame, lane_num: int):
    """
    Analyze training data for a specific lane.

    Shows patterns, ranges, etc.
    """
    print(f"\n{'='*80}")
    print(f"Lane {lane_num} Analysis")
    print(f"{'='*80}")

    print(f"\n📊 Statistics:")
    print(f"   Training examples: {len(lane_df)}")
    print(f"   X_k range: [{lane_df['X_k'].min()}, {lane_df['X_k'].max()}]")
    print(f"   X_k+1 range: [{lane_df['X_k+1'].min()}, {lane_df['X_k+1'].max()}]")

    # Check if lane is always zero
    if lane_df['X_k'].max() == 0 and lane_df['X_k+1'].max() == 0:
        print(f"   ⚠️  Lane {lane_num} is ALWAYS ZERO")
        return

    # Check when lane becomes active
    first_nonzero = lane_df[lane_df['X_k'] > 0].iloc[0]['puzzle_k'] if len(lane_df[lane_df['X_k'] > 0]) > 0 else None

    if first_nonzero:
        print(f"   🔥 First non-zero at puzzle {first_nonzero}")

    # Show first few examples
    print(f"\n📝 First 5 examples:")
    print(lane_df.head().to_string(index=False))

    # Show last few examples
    print(f"\n📝 Last 5 examples:")
    print(lane_df.tail().to_string(index=False))


def main():
    """Prepare training data for local AI."""
    print("="*80)
    print("AI LEARNS LADDER: Data Preparation")
    print("="*80)

    # Paths
    base_path = Path(__file__).parent.parent.parent
    csv_path = base_path / "data" / "btc_puzzle_1_160_full.csv"
    output_dir = Path(__file__).parent / "data"

    print(f"\n📂 Loading puzzles from CSV...")
    print(f"   Path: {csv_path}")

    # Load training data (puzzles 1-70)
    puzzles = load_puzzles_from_csv(csv_path, max_puzzle=70)
    print(f"   ✅ Loaded {len(puzzles)} puzzles")

    # Create per-lane training data
    print(f"\n📚 Creating per-lane training data...")
    print(f"   Output: {output_dir}/")
    print()

    lane_dfs = create_per_lane_training_data(puzzles, output_dir)

    # Analyze a few interesting lanes
    print(f"\n{'='*80}")
    print(f"Analyzing Interesting Lanes")
    print(f"{'='*80}")

    # Lane 0 (rightmost, always active)
    analyze_lane_data(lane_dfs[0], 0)

    # Lane 1 (becomes active around puzzle 8)
    analyze_lane_data(lane_dfs[1], 1)

    # Lane 6 (should be always zero based on old AI)
    analyze_lane_data(lane_dfs[6], 6)

    # Lane 15 (leftmost, mostly zeros)
    analyze_lane_data(lane_dfs[15], 15)

    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")

    print(f"\n✅ Created training data for 16 lanes")
    print(f"✅ Each lane has ~69 training examples (puzzle 1→70)")
    print(f"✅ Data saved to: {output_dir}/")

    print(f"\n📝 Next Steps:")
    print(f"   1. Train PySR on lane 0 (most active)")
    print(f"   2. Discover equation: f(X_k, puzzle_k) → X_k+1")
    print(f"   3. Validate with cryptographic proof")
    print(f"   4. Extend to all 16 lanes")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
