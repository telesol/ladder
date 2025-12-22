#!/usr/bin/env python3
"""
Prepare data for transformer training

Uses the same train/val/test splits as PySR experiment (01)
Creates symlinks to avoid data duplication
"""

import json
import numpy as np
from pathlib import Path
import os

def create_symlinks():
    """Create symlinks to PySR data."""
    pysr_data_dir = Path(__file__).parent.parent.parent / "01-pysr-symbolic-regression" / "data"
    transformer_data_dir = Path(__file__).parent.parent / "data"

    print("=" * 70)
    print("Preparing Transformer Data (Linking to PySR Data)")
    print("=" * 70)

    # Files to link
    files_to_link = [
        "puzzles_full.json",
        "train_matrix.npy",
        "val_matrix.npy",
        "test_matrix.npy"
    ]

    for filename in files_to_link:
        source = pysr_data_dir / filename
        target = transformer_data_dir / filename

        if target.exists() or target.is_symlink():
            print(f"✓ {filename} already exists")
            continue

        if not source.exists():
            print(f"⚠️  Source file not found: {source}")
            continue

        # Create symlink
        os.symlink(source, target)
        print(f"✓ Linked {filename}")

    print(f"\n✅ Data preparation complete")
    print(f"   Source: {pysr_data_dir}")
    print(f"   Target: {transformer_data_dir}")

def load_and_verify_data():
    """Load data and verify format."""
    data_dir = Path(__file__).parent.parent / "data"

    print(f"\n📂 Loading data...")

    # Load matrices
    train_matrix = np.load(data_dir / "train_matrix.npy")
    val_matrix = np.load(data_dir / "val_matrix.npy")
    test_matrix = np.load(data_dir / "test_matrix.npy")

    # Load puzzles metadata
    with open(data_dir / "puzzles_full.json", 'r') as f:
        puzzles = json.load(f)

    print(f"   Training puzzles: {train_matrix.shape} (puzzles 1-60)")
    print(f"   Validation puzzles: {val_matrix.shape} (puzzles 61-70)")
    print(f"   Test puzzles: {test_matrix.shape} (bridge rows)")
    print(f"   Total puzzles: {len(puzzles)}")

    # Verify first 16 bytes (what we're training on)
    print(f"\n🔍 Data format:")
    print(f"   Each row: {train_matrix.shape[1]} bytes")
    print(f"   First 16 bytes: puzzle key (training target)")
    print(f"   Last 16 bytes: zeros (not used)")

    # Create training pairs
    print(f"\n🔄 Creating input/output pairs:")

    # Training: puzzle_k -> puzzle_{k+1}
    train_X = train_matrix[:-1, :16]  # First 16 bytes of puzzles 1-59
    train_y = train_matrix[1:, :16]   # First 16 bytes of puzzles 2-60

    print(f"   Train X: {train_X.shape} (inputs)")
    print(f"   Train y: {train_y.shape} (outputs)")
    print(f"   Pairs: {len(train_X)}")

    # Validation: puzzle_k -> puzzle_{k+1}
    val_X = val_matrix[:-1, :16]
    val_y = val_matrix[1:, :16]

    print(f"   Val X: {val_X.shape}")
    print(f"   Val y: {val_y.shape}")
    print(f"   Pairs: {len(val_X)}")

    # Save processed data
    output_dir = data_dir

    np.save(output_dir / "train_X.npy", train_X)
    np.save(output_dir / "train_y.npy", train_y)
    np.save(output_dir / "val_X.npy", val_X)
    np.save(output_dir / "val_y.npy", val_y)

    print(f"\n💾 Saved processed data:")
    print(f"   {output_dir}/train_X.npy")
    print(f"   {output_dir}/train_y.npy")
    print(f"   {output_dir}/val_X.npy")
    print(f"   {output_dir}/val_y.npy")

    # Save metadata
    metadata = {
        'train_puzzles': '1-60',
        'val_puzzles': '61-70',
        'test_puzzles': 'bridge rows (75, 80, 85, 90, 95)',
        'train_pairs': int(len(train_X)),
        'val_pairs': int(len(val_X)),
        'input_dim': 16,
        'output_dim': 16,
        'byte_range': [0, 255],
        'data_format': 'uint8'
    }

    with open(output_dir / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"   {output_dir}/metadata.json")

    return {
        'train_X': train_X,
        'train_y': train_y,
        'val_X': val_X,
        'val_y': val_y,
        'metadata': metadata
    }

def main():
    """Main data preparation pipeline."""
    # Create symlinks to PySR data
    create_symlinks()

    # Load and verify
    data = load_and_verify_data()

    print(f"\n" + "=" * 70)
    print(f"✅ Data preparation complete!")
    print(f"=" * 70)
    print(f"\nNext step: Train transformer model")
    print(f"   python scripts/train_transformer.py")

if __name__ == "__main__":
    main()
