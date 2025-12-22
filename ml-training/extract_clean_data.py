#!/usr/bin/env python3
"""
Extract clean training data from BTC puzzle CSV.
Validates all 160 puzzles and prepares data for ML pattern discovery.
"""

import csv
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple

def hex_to_bytes(hex_str: str) -> bytes:
    """Convert hex string to bytes, handling 0x prefix."""
    hex_str = hex_str.lower().removeprefix("0x")
    if len(hex_str) % 2:
        hex_str = "0" + hex_str
    return bytes.fromhex(hex_str)

def extract_puzzle_data(csv_path: Path) -> List[Dict]:
    """Extract all puzzle data with validation."""
    puzzles = []

    with csv_path.open('r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            puzzle_num = int(row['puzzle'])
            key_hex_64 = row['key_hex_64']

            # Validate 64-hex format
            if len(key_hex_64) != 64:
                print(f"⚠️  Puzzle {puzzle_num}: Invalid length {len(key_hex_64)}")
                continue

            try:
                key_bytes = bytes.fromhex(key_hex_64)
                assert len(key_bytes) == 32, f"Expected 32 bytes, got {len(key_bytes)}"
            except Exception as e:
                print(f"⚠️  Puzzle {puzzle_num}: Validation failed - {e}")
                continue

            puzzles.append({
                'puzzle': puzzle_num,
                'bits': puzzle_num,  # Using puzzle number as bits
                'key_hex_64': key_hex_64,
                'key_bytes': list(key_bytes),
                'address': row['address'],
                'range_start': row['range_hex_start'],
                'range_end': row['range_hex_end']
            })

    return puzzles

def extract_half_blocks(puzzles: List[Dict]) -> Dict:
    """Extract half-blocks for training (first/second 16 bytes)."""
    half_blocks = {
        'first_half': [],   # First 16 bytes (32 hex chars)
        'second_half': [],  # Last 16 bytes (32 hex chars)
        'full_key': [],     # All 32 bytes
        'metadata': []
    }

    for puzzle in puzzles:
        key_hex = puzzle['key_hex_64']
        first_half = key_hex[:32]
        second_half = key_hex[32:]

        half_blocks['first_half'].append(first_half)
        half_blocks['second_half'].append(second_half)
        half_blocks['full_key'].append(key_hex)
        half_blocks['metadata'].append({
            'puzzle': puzzle['puzzle'],
            'bits': puzzle['bits'],
            'address': puzzle['address']
        })

    return half_blocks

def create_lane_matrix(puzzles: List[Dict]) -> np.ndarray:
    """
    Create matrix of lane values for pattern analysis.
    Each row = one puzzle, each column = one byte lane (0-31).
    """
    matrix = np.zeros((len(puzzles), 32), dtype=np.uint8)

    for i, puzzle in enumerate(puzzles):
        matrix[i] = np.array(puzzle['key_bytes'], dtype=np.uint8)

    return matrix

def analyze_sequences(matrix: np.ndarray) -> Dict:
    """Analyze sequential differences for pattern discovery."""
    analysis = {
        'byte_diffs': {},
        'lane_patterns': {},
        'statistics': {}
    }

    # Compute differences between consecutive puzzles
    diffs = np.diff(matrix, axis=0)

    # Analyze each lane (byte position)
    for lane in range(32):
        lane_diffs = diffs[:, lane]
        analysis['lane_patterns'][lane] = {
            'mean': float(np.mean(lane_diffs)),
            'std': float(np.std(lane_diffs)),
            'min': int(np.min(lane_diffs)),
            'max': int(np.max(lane_diffs)),
            'unique_values': len(np.unique(lane_diffs)),
            'most_common': int(np.bincount(lane_diffs.astype(np.uint8)).argmax())
        }

    return analysis

def main():
    """Main extraction and analysis pipeline."""
    print("🔍 Extracting clean puzzle data...")

    # Paths
    csv_path = Path("data/btc_puzzle_1_160_full.csv")
    output_dir = Path("ml-training/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract data
    puzzles = extract_puzzle_data(csv_path)
    print(f"✅ Extracted {len(puzzles)} valid puzzles")

    # Save full puzzle data
    with open(output_dir / "puzzles_full.json", 'w') as f:
        json.dump(puzzles, f, indent=2)
    print(f"💾 Saved: {output_dir / 'puzzles_full.json'}")

    # Extract half-blocks
    half_blocks = extract_half_blocks(puzzles)
    with open(output_dir / "half_blocks.json", 'w') as f:
        json.dump(half_blocks, f, indent=2)
    print(f"💾 Saved: {output_dir / 'half_blocks.json'}")

    # Create lane matrix for ML training
    matrix = create_lane_matrix(puzzles)
    np.save(output_dir / "lane_matrix.npy", matrix)
    print(f"💾 Saved: {output_dir / 'lane_matrix.npy'} (shape: {matrix.shape})")

    # Analyze patterns
    analysis = analyze_sequences(matrix)
    with open(output_dir / "pattern_analysis.json", 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"💾 Saved: {output_dir / 'pattern_analysis.json'}")

    # Summary statistics
    print("\n📊 Data Summary:")
    print(f"  Total puzzles: {len(puzzles)}")
    print(f"  Puzzle range: {puzzles[0]['puzzle']} - {puzzles[-1]['puzzle']}")
    print(f"  Lane matrix shape: {matrix.shape}")
    print(f"  Total bytes: {matrix.size}")

    # Lane analysis preview
    print("\n🔬 Lane Pattern Analysis (first 5 lanes):")
    for lane in range(min(5, 32)):
        stats = analysis['lane_patterns'][lane]
        print(f"  Lane {lane:2d}: mean_diff={stats['mean']:6.2f}, "
              f"std={stats['std']:6.2f}, unique={stats['unique_values']}")

    print("\n✅ Clean data extraction complete!")
    print(f"📁 Output directory: {output_dir.absolute()}")

if __name__ == "__main__":
    main()
