#!/usr/bin/env python3
"""
Train PySR to Discover the BLOCK STRUCTURE

Based on chat history discoveries:
- 32-puzzle blocks
- 2 occurrences per block (first half, second half)
- Each lane has only 4 drift values (not 1,296!)
  - C[0][ℓ][0], C[0][ℓ][1], C[1][ℓ][0], C[1][ℓ][1]

The formula is:
    X_{k+1}[lane] = A[lane] * X_k[lane] + C[block][lane][occ] (mod 256)

Where:
    block = which 32-puzzle block (0, 1, 2, ...)
    occ = which half of block (0=first 16, 1=second 16)

This script trains PySR to discover:
    C[block][lane][occ] = f(block, lane, occ)

Target: 100% accuracy (no less acceptable!)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from pysr import PySRRegressor


def determine_block_and_occ(puzzle_k):
    """
    Determine which block and occurrence a puzzle belongs to.

    From chat history:
    - Block 0: puzzles 29-60 (32 puzzles)
      - occ 0: puzzles 29-44 (first 16)
      - occ 1: puzzles 45-60 (second 16)
    - Block 1: puzzles 61-92
      - occ 0: puzzles 61-76
      - occ 1: puzzles 77-92

    General formula:
        block = (puzzle_k - 29) // 32
        within_block = (puzzle_k - 29) % 32
        occ = within_block // 16
    """
    if puzzle_k < 29:
        return None, None  # Before first complete block

    block = (puzzle_k - 29) // 32
    within_block = (puzzle_k - 29) % 32
    occ = within_block // 16

    return block, occ


def load_drift_with_structure():
    """
    Load drift data with block/occurrence structure.

    Returns:
        X_train: [[block, lane, occ, X_k], ...] features
        y_train: [drift, ...] targets
    """
    # Load calibration
    calib_path = Path(__file__).parent.parent.parent / "out" / "ladder_calib_ultimate.json"
    csv_path = Path(__file__).parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"

    with open(calib_path) as f:
        calib = json.load(f)

    df = pd.read_csv(csv_path)

    print("📂 Loading drift data with block/occurrence structure...")

    drift_data = []

    # Extract drift values for puzzles 29-69 (Block 0 complete, Block 1 partial)
    for puzzle_k in range(29, 70):
        block, occ = determine_block_and_occ(puzzle_k)

        if block is None:
            continue

        drift_key = f"{puzzle_k}→{puzzle_k+1}"
        if drift_key not in calib['drifts']:
            continue

        # Get current key bytes (little-endian)
        key_k_hex = df[df['puzzle'] == puzzle_k].iloc[0]['key_hex_64']
        key_k_bytes = bytes(reversed(bytes.fromhex(key_k_hex[32:64])))

        # For each lane
        for lane in range(16):
            drift = calib['drifts'][drift_key][str(lane)]
            X_k = key_k_bytes[lane]

            drift_data.append({
                'block': block,
                'lane': lane,
                'occ': occ,
                'X_k': X_k,
                'drift': drift,
                'puzzle_k': puzzle_k  # For reference only
            })

    train_df = pd.DataFrame(drift_data)

    # Features: block, lane, occ, X_k
    X = train_df[['block', 'lane', 'occ', 'X_k']].values

    # Target: drift
    y = train_df['drift'].values

    print(f"✅ Loaded {len(X)} training examples")
    print(f"   Puzzles: 29-69")
    print(f"   Blocks: {train_df['block'].min()}-{train_df['block'].max()}")
    print(f"   Occurrences: 0-1 (first/second half)")
    print(f"   Lanes: 0-15")
    print(f"   Features: block, lane, occ, X_k")
    print(f"   Target: drift")

    # Show structure
    print(f"\n📊 Data distribution:")
    print(train_df.groupby(['block', 'occ']).size())

    return X, y, train_df


def train_block_structure_formula(X_train, y_train):
    """
    Train PySR to discover: C[block][lane][occ] = f(block, lane, occ)

    Note: X_k should NOT be needed if drift is truly block/lane/occ dependent!
    """
    print(f"\n{'='*80}")
    print(f"Training PySR to Discover Block Structure Formula")
    print(f"{'='*80}\n")

    print(f"📊 Training data:")
    print(f"   Samples: {len(X_train)}")
    print(f"   Features: block, lane, occ, X_k")
    print(f"   Target: drift (0-255)")

    print(f"\n🤖 Starting PySR training...")
    print(f"   HYPOTHESIS: drift = f(block, lane, occ)")
    print(f"   If X_k appears in formula, model is more complex than expected")

    model = PySRRegressor(
        niterations=50,  # Start with fewer iterations
        binary_operators=["+", "*", "-"],
        unary_operators=["square"],
        populations=20,
        population_size=50,
        ncycles_per_iteration=550,
        model_selection="best",
        loss="L2DistLoss()",
        maxsize=20,
        parsimony=0.01,  # Favor simpler formulas
        verbosity=1,
        random_state=42,
    )

    # Fit the model
    model.fit(X_train, y_train, variable_names=["block", "lane", "occ", "X_k"])

    print(f"\n✅ Training complete!")

    return model


def analyze_block_results(model, X_train, y_train, train_df):
    """
    Analyze discovered block structure formula.
    """
    print(f"\n{'='*80}")
    print(f"PySR Results: Block Structure Discovery")
    print(f"{'='*80}\n")

    # Show top equations
    print(f"🔬 Top Discovered Equations:\n")
    print(model)

    # Get calculations
    y_pred = model.calculate(X_train)

    # Calculate accuracy
    y_pred_mod = np.round(y_pred).astype(int) % 256
    y_true_mod = y_train.astype(int) % 256

    exact_matches = np.sum(y_pred_mod == y_true_mod)
    accuracy = (exact_matches / len(y_train)) * 100

    # Per-block accuracy
    train_df['predicted_drift'] = y_pred_mod
    train_df['match'] = (y_pred_mod == y_true_mod)

    per_block_acc = train_df.groupby(['block', 'occ'])['match'].mean() * 100

    print(f"\n📊 Overall Accuracy: {accuracy:.2f}%")
    print(f"   Exact matches: {exact_matches}/{len(y_train)}")

    print(f"\n📊 Per-Block Accuracy:")
    print(per_block_acc)

    # Check if only 4 unique drifts per lane
    print(f"\n🔍 Analyzing drift patterns per lane:")
    for lane in range(4):  # Show first 4 lanes
        lane_data = train_df[train_df['lane'] == lane]
        unique_drifts = lane_data.groupby(['block', 'occ'])['drift'].unique()
        print(f"\nLane {lane}:")
        for (block, occ), drifts in unique_drifts.items():
            print(f"  Block {block}, occ {occ}: {drifts} (count: {len(drifts)})")

    return accuracy


def main():
    """Train PySR to discover block structure."""
    print("="*80)
    print("AI LEARNS LADDER: Block Structure Discovery")
    print("="*80)
    print()
    print("Based on historical chat discoveries:")
    print("  - 32-puzzle blocks")
    print("  - 2 occurrences per block")
    print("  - Only 4 drift values per lane!")
    print("="*80)

    # Load data with block/occurrence structure
    X_train, y_train, train_df = load_drift_with_structure()

    # Train PySR
    model = train_block_structure_formula(X_train, y_train)

    # Analyze results
    accuracy = analyze_block_results(model, X_train, y_train, train_df)

    # Save model
    model_path = Path(__file__).parent / "models" / "block_structure.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)

    import pickle
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    print(f"\n💾 Model saved to: {model_path}")

    # Summary
    print(f"\n{'='*80}")
    print(f"TRAINING SUMMARY")
    print(f"{'='*80}\n")

    if accuracy >= 100:
        print(f"🎉 PERFECT! 100% accuracy achieved!")
        print(f"\n✅ The ladder structure is discovered!")
        print(f"✅ Can now generate ANY puzzle using this formula!")
    elif accuracy >= 95:
        print(f"✅ EXCELLENT! {accuracy:.1f}% accuracy")
        print(f"\n📝 Close to 100% - minor refinements needed")
    else:
        print(f"❌ Accuracy: {accuracy:.1f}% (below target)")
        print(f"\n📝 Model needs adjustment or hypothesis is incorrect")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
