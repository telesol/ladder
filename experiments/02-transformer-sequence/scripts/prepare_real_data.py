#!/usr/bin/env python3
"""
Prepare REAL Bitcoin puzzle data for training

Extracts actual puzzle keys from CSV (not preprocessed matrices)
"""

import csv
import json
import numpy as np
from pathlib import Path

def load_real_puzzles(csv_path):
    """Load real Bitcoin puzzle keys from CSV."""
    puzzles = {}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                puzzle_num = int(row['puzzle'])
            except ValueError:
                continue  # Skip header or invalid rows

            key_hex_64 = row['key_hex_64'].strip()  # 64-char hex string

            # Skip if not valid hex or wrong length
            if len(key_hex_64) != 64:
                continue

            # Extract LAST 16 bytes (last 32 hex chars) - this is where the actual key is!
            # For small puzzles, the first half is zeros, key is in second half
            key_hex_32 = key_hex_64[32:64]

            try:
                key_bytes = bytes.fromhex(key_hex_32)
            except ValueError:
                continue  # Skip invalid hex

            puzzles[puzzle_num] = {
                'puzzle': puzzle_num,
                'key_hex': key_hex_32,
                'key_bytes': key_bytes,
                'address': row['address']
            }

    return puzzles

def create_training_data(puzzles, train_range, val_range):
    """Create training pairs from real puzzles."""

    # Training data
    train_X = []
    train_y = []

    for i in range(train_range[0], train_range[1]):
        if i in puzzles and (i+1) in puzzles:
            train_X.append(list(puzzles[i]['key_bytes']))
            train_y.append(list(puzzles[i+1]['key_bytes']))

    # Validation data
    val_X = []
    val_y = []

    for i in range(val_range[0], val_range[1]):
        if i in puzzles and (i+1) in puzzles:
            val_X.append(list(puzzles[i]['key_bytes']))
            val_y.append(list(puzzles[i+1]['key_bytes']))

    return {
        'train_X': np.array(train_X, dtype=np.uint8),
        'train_y': np.array(train_y, dtype=np.uint8),
        'val_X': np.array(val_X, dtype=np.uint8),
        'val_y': np.array(val_y, dtype=np.uint8)
    }

def main():
    """Main data preparation pipeline."""
    print("=" * 70)
    print("Preparing REAL Bitcoin Puzzle Data")
    print("=" * 70)

    # Paths
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)

    print(f"\n📂 Loading real puzzle keys from CSV...")
    print(f"   {csv_path}")

    # Load puzzles
    puzzles = load_real_puzzles(csv_path)
    print(f"   Loaded {len(puzzles)} puzzles")

    # Show sample
    print(f"\n🔍 Sample puzzles:")
    for i in [1, 2, 3, 70]:
        if i in puzzles:
            print(f"   Puzzle {i:3d}: {puzzles[i]['key_hex']}")

    # Create training/validation splits
    print(f"\n🔄 Creating training pairs...")

    # Training: puzzles 1-60 (59 transitions)
    # Validation: puzzles 61-70 (9 transitions)
    data = create_training_data(
        puzzles,
        train_range=(1, 60),
        val_range=(61, 70)
    )

    print(f"   Train pairs: {len(data['train_X'])} (puzzle_k → puzzle_k+1)")
    print(f"   Val pairs: {len(data['val_X'])}")

    # Verify data is NOT all zeros
    print(f"\n✅ Data verification:")
    print(f"   Train data non-zero: {np.any(data['train_X'] != 0)}")
    print(f"   Val data non-zero: {np.any(data['val_X'] != 0)}")

    # Show first training example
    print(f"\n📋 First training example:")
    print(f"   Input (puzzle 1):  {bytes(data['train_X'][0]).hex()}")
    print(f"   Output (puzzle 2): {bytes(data['train_y'][0]).hex()}")

    # Save to disk
    print(f"\n💾 Saving data...")
    np.save(output_dir / "train_X_real.npy", data['train_X'])
    np.save(output_dir / "train_y_real.npy", data['train_y'])
    np.save(output_dir / "val_X_real.npy", data['val_X'])
    np.save(output_dir / "val_y_real.npy", data['val_y'])

    # Save metadata
    metadata = {
        'source': 'Real Bitcoin puzzle keys from CSV',
        'train_range': '1-60',
        'val_range': '61-70',
        'train_pairs': int(len(data['train_X'])),
        'val_pairs': int(len(data['val_X'])),
        'data_format': 'uint8 (0-255)',
        'bytes_per_puzzle': 16,
        'note': 'First 16 bytes of each 64-char hex key'
    }

    with open(output_dir / "metadata_real.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    # Save puzzle 70 for generation starting point
    puzzle_70_data = {
        'puzzle': 70,
        'key_hex': puzzles[70]['key_hex'],
        'key_bytes': list(puzzles[70]['key_bytes']),
        'address': puzzles[70]['address']
    }

    with open(output_dir / "puzzle_70.json", 'w') as f:
        json.dump(puzzle_70_data, f, indent=2)

    print(f"   {output_dir}/train_X_real.npy")
    print(f"   {output_dir}/train_y_real.npy")
    print(f"   {output_dir}/val_X_real.npy")
    print(f"   {output_dir}/val_y_real.npy")
    print(f"   {output_dir}/metadata_real.json")
    print(f"   {output_dir}/puzzle_70.json")

    print(f"\n✅ Real data preparation complete!")
    print(f"\nNext step: Retrain model with real data")
    print(f"   python scripts/train_transformer.py --real-data --run-dir run_005_real_data")

if __name__ == "__main__":
    main()
