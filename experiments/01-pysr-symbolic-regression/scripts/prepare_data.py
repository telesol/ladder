#!/usr/bin/env python3
"""
Phase 2: Data Preparation for PySR Experiment

Creates train/validation/test splits from the clean puzzle data.
"""

import json
import numpy as np
from pathlib import Path

def load_data():
    """Load the lane matrix from extracted data."""
    data_dir = Path(__file__).parent.parent / "data"

    print("📂 Loading data...")
    lane_matrix = np.load(data_dir / "lane_matrix.npy")

    with open(data_dir / "puzzles_full.json") as f:
        puzzles = json.load(f)

    print(f"✅ Loaded {len(puzzles)} puzzles")
    print(f"   Lane matrix shape: {lane_matrix.shape}")

    return lane_matrix, puzzles

def create_splits(lane_matrix, puzzles):
    """
    Split data into train/validation/test sets.

    Strategy:
    - Training: Puzzles 1-60 (indices 0-59) - 60 samples
    - Validation: Puzzles 61-70 (indices 60-69) - 10 samples
    - Test: Bridge rows 75, 80, 85, 90, 95 - 5 samples
    """
    # Continuous puzzles 1-70 are first 70 entries
    train_matrix = lane_matrix[:60]  # Puzzles 1-60
    val_matrix = lane_matrix[60:70]   # Puzzles 61-70

    # Bridge rows start at index 70
    # They are at bits: 75, 80, 85, 90, 95, 100, ...
    # Indices: 70, 71, 72, 73, 74, ...
    test_matrix = lane_matrix[70:75]  # First 5 bridge rows (75, 80, 85, 90, 95)

    print(f"\n📊 Data splits created:")
    print(f"   Training:   {train_matrix.shape} - Puzzles 1-60")
    print(f"   Validation: {val_matrix.shape} - Puzzles 61-70")
    print(f"   Test:       {test_matrix.shape} - Bridge rows 75-95")

    return train_matrix, val_matrix, test_matrix

def save_splits(train_matrix, val_matrix, test_matrix):
    """Save the splits to disk."""
    data_dir = Path(__file__).parent.parent / "data"

    np.save(data_dir / "train_matrix.npy", train_matrix)
    np.save(data_dir / "val_matrix.npy", val_matrix)
    np.save(data_dir / "test_matrix.npy", test_matrix)

    print(f"\n💾 Saved splits to {data_dir}/")
    print(f"   - train_matrix.npy")
    print(f"   - val_matrix.npy")
    print(f"   - test_matrix.npy")

def create_lane_datasets(train_matrix):
    """
    Create per-lane training datasets for symbolic regression.

    For each lane ℓ:
    - X: values at step k (X_k)
    - y: values at step k+1 (X_{k+1})
    """
    data_dir = Path(__file__).parent.parent / "data"
    lane_dir = data_dir / "lanes"
    lane_dir.mkdir(exist_ok=True)

    print(f"\n🔬 Creating per-lane datasets...")

    for lane in range(16):  # First 16 bytes (half-block)
        X = train_matrix[:-1, lane].reshape(-1, 1)  # X_k (shape: 59, 1)
        y = train_matrix[1:, lane]                   # X_{k+1} (shape: 59,)

        np.save(lane_dir / f"lane_{lane:02d}_X.npy", X)
        np.save(lane_dir / f"lane_{lane:02d}_y.npy", y)

    print(f"✅ Created 16 lane datasets in {lane_dir}/")
    print(f"   Each lane: X shape (59, 1), y shape (59,)")

def print_sample_data(train_matrix):
    """Print sample data for verification."""
    print(f"\n📋 Sample data (first 3 puzzles, first 4 lanes):")
    print(f"   Puzzle | Lane 0 | Lane 1 | Lane 2 | Lane 3")
    print(f"   -------|--------|--------|--------|--------")
    for i in range(3):
        print(f"   {i+1:6d} | {train_matrix[i,0]:6d} | {train_matrix[i,1]:6d} | {train_matrix[i,2]:6d} | {train_matrix[i,3]:6d}")

    print(f"\n📋 Sequential differences (Puzzle 2 - Puzzle 1):")
    diff = train_matrix[1] - train_matrix[0]
    print(f"   Lane 0-3: {diff[:4]}")

def main():
    """Main data preparation pipeline."""
    print("=" * 60)
    print("Phase 2: Data Preparation for PySR")
    print("=" * 60)

    # Load data
    lane_matrix, puzzles = load_data()

    # Create splits
    train_matrix, val_matrix, test_matrix = create_splits(lane_matrix, puzzles)

    # Save splits
    save_splits(train_matrix, val_matrix, test_matrix)

    # Create per-lane datasets
    create_lane_datasets(train_matrix)

    # Print sample
    print_sample_data(train_matrix)

    print("\n" + "=" * 60)
    print("✅ Phase 2 Complete!")
    print("=" * 60)
    print("\nNext step: Run train_single_lane.py for proof of concept")
    print("   python3 scripts/train_single_lane.py --lane 0")

if __name__ == "__main__":
    main()
