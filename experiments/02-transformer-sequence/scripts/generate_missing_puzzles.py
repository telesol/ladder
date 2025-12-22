#!/usr/bin/env python3
"""
Generate missing puzzles using trained neural network

Uses the trained model to calculate puzzles 71-160
Compares with PySR formula where we have known values
"""

import argparse
import json
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path

# Import model architecture
import sys
sys.path.insert(0, str(Path(__file__).parent))
from train_transformer import SimpleLanePredictor, PYSR_EXPONENTS

def pysr_predict(current_bytes, exponents):
    """PySR formula: X_{k+1}(ℓ) = X_k(ℓ)^n mod 256"""
    next_bytes = []
    for lane in range(len(exponents)):
        next_bytes.append(int(current_bytes[lane] ** exponents[lane]) % 256)
    return bytes(next_bytes)

def load_model(checkpoint_path):
    """Load trained model from checkpoint."""
    checkpoint = torch.load(checkpoint_path, map_location='cpu')

    config = checkpoint['config']
    model = SimpleLanePredictor(hidden_size=config['hidden_size'])
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    return model

def neural_predict(model, current_bytes):
    """Calculate next puzzle using neural network."""
    # Convert to tensor and normalize
    x = torch.FloatTensor(np.array(list(current_bytes))) / 255.0
    x = x.unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        logits = model(x)  # (1, 16, 256)
        calculations = torch.argmax(logits, dim=2).squeeze(0)  # (16,)

    return bytes(calculations.numpy().astype(np.uint8))

def generate_puzzles(model, start_puzzle_bytes, start_num, end_num, pysr_exponents):
    """Generate puzzles from start_num to end_num."""

    results = []
    current_bytes = start_puzzle_bytes

    print(f"\n🔮 Generating puzzles {start_num+1} to {end_num}...")
    print(f"   Starting from puzzle {start_num}: {current_bytes.hex()}")
    print("=" * 80)

    for puzzle_num in range(start_num + 1, end_num + 1):
        # Neural network calculation
        neural_next = neural_predict(model, current_bytes)

        # PySR calculation (for comparison)
        pysr_next = pysr_predict(current_bytes, pysr_exponents)

        # Check if they match
        match = (neural_next == pysr_next)

        result = {
            'puzzle': puzzle_num,
            'neural_hex': neural_next.hex(),
            'pysr_hex': pysr_next.hex(),
            'match': match,
            'per_lane_match': [neural_next[i] == pysr_next[i] for i in range(16)]
        }
        results.append(result)

        # Print result
        if match:
            print(f"Puzzle {puzzle_num:3d}: ✅ MATCH    {neural_next.hex()}")
        else:
            print(f"Puzzle {puzzle_num:3d}: ❌ MISMATCH")
            print(f"             Neural: {neural_next.hex()}")
            print(f"             PySR:   {pysr_next.hex()}")
            # Show which lanes differ
            diff_lanes = [i for i in range(16) if neural_next[i] != pysr_next[i]]
            print(f"             Diff lanes: {diff_lanes}")

        # Use neural calculation for next step (let it extrapolate)
        current_bytes = neural_next

    return results

def main():
    parser = argparse.ArgumentParser(description='Generate missing puzzles with trained model')
    parser.add_argument('--checkpoint', type=str, default='runs/run_004_baseline/checkpoints/best_model.pth',
                       help='Path to model checkpoint')
    parser.add_argument('--start', type=int, default=70, help='Start from puzzle number')
    parser.add_argument('--end', type=int, default=100, help='Generate up to puzzle number')
    args = parser.parse_args()

    print("=" * 80)
    print("Generate Missing Bitcoin Puzzles Using Neural Network")
    print("=" * 80)

    # Load model
    checkpoint_path = Path(__file__).parent.parent / args.checkpoint
    if not checkpoint_path.exists():
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        return

    print(f"\n📦 Loading model from: {checkpoint_path.name}")
    model = load_model(checkpoint_path)
    print(f"   ✅ Model loaded")

    # Load starting puzzle from CSV (get the REAL puzzle 70 value)
    import pandas as pd
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"

    if not csv_path.exists():
        print(f"❌ CSV not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    puzzle_row = df[df['puzzle'] == args.start].iloc[0]

    # Extract last 16 bytes (last 32 hex chars) from 64-char hex string
    key_hex_64 = str(puzzle_row['key_hex_64'])
    if len(key_hex_64) != 64:
        print(f"⚠️  Warning: Expected 64 hex chars, got {len(key_hex_64)} for puzzle {args.start}")
        print(f"   Value: {key_hex_64}")

    key_hex_32 = key_hex_64[32:64]  # Last 32 hex chars = last 16 bytes

    puzzle_70_bytes = bytes.fromhex(key_hex_32)

    print(f"\n🌱 Starting puzzle {args.start}:")
    print(f"   {puzzle_70_bytes.hex()}")

    # Generate puzzles
    results = generate_puzzles(model, puzzle_70_bytes, args.start, args.end, PYSR_EXPONENTS)

    # Summary
    total = len(results)
    matches = sum(1 for r in results if r['match'])
    accuracy = (matches / total * 100) if total > 0 else 0

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n📊 Generation Results:")
    print(f"   Puzzles generated: {total}")
    print(f"   Matches with PySR: {matches}/{total} ({accuracy:.2f}%)")

    if accuracy == 100.0:
        print(f"\n🎉 PERFECT! Neural network can extrapolate beyond training data!")
        print(f"   The network learned the underlying pattern (not just memorization)")
    elif accuracy >= 95.0:
        print(f"\n✅ Very good! Minor differences from PySR")
    else:
        print(f"\n⚠️  Neural network diverges from PySR formula")
        print(f"   This suggests it memorized training data but didn't learn the pattern")

    # Save results
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    output_file = results_dir / f"generated_puzzles_{args.start+1}_{args.end}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'start_puzzle': args.start,
            'end_puzzle': args.end,
            'total_generated': total,
            'matches': matches,
            'accuracy': accuracy,
            'results': results
        }, f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")

    # Show first mismatch details if any
    if accuracy < 100.0:
        print(f"\n🔍 First mismatch analysis:")
        for r in results:
            if not r['match']:
                print(f"   Puzzle {r['puzzle']}:")
                print(f"   Neural: {r['neural_hex']}")
                print(f"   PySR:   {r['pysr_hex']}")
                print(f"   Per-lane match: {r['per_lane_match']}")
                break

if __name__ == "__main__":
    main()
