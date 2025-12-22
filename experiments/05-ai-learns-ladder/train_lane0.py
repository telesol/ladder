#!/usr/bin/env python3
"""
Train Local AI on Lane 0

Let PySR DISCOVER the equation for lane 0 (rightmost byte).

This is where the AI LEARNS the pattern, not just applies a formula.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from pysr import PySRRegressor


def load_lane_data(lane_num: int, data_dir: Path) -> tuple:
    """
    Load training data for a specific lane.

    Returns:
        (X_train, y_train) where:
        - X_train: [[X_k, puzzle_k], ...] features
        - y_train: [X_k+1, ...] targets
    """
    csv_path = data_dir / f"lane_{lane_num:02d}_train.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"Training data not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Features: X_k and puzzle_k
    X = df[['X_k', 'puzzle_k']].values

    # Target: X_k+1
    y = df['X_k+1'].values

    return X, y


def train_pysr_lane(X_train, y_train, lane_num: int):
    """
    Train PySR to discover equation for a lane.

    Let the AI discover: f(X_k, puzzle_k) → X_k+1
    """
    print(f"\n{'='*80}")
    print(f"Training PySR on Lane {lane_num}")
    print(f"{'='*80}\n")

    print(f"📊 Training data:")
    print(f"   Samples: {len(X_train)}")
    print(f"   Features: X_k, puzzle_k")
    print(f"   Target: X_k+1")
    print(f"   X_k range: [{X_train[:, 0].min()}, {X_train[:, 0].max()}]")
    print(f"   puzzle_k range: [{X_train[:, 1].min()}, {X_train[:, 1].max()}]")
    print(f"   y range: [{y_train.min()}, {y_train.max()}]")

    print(f"\n🤖 Starting PySR training...")
    print(f"   This will take a few minutes...")

    model = PySRRegressor(
        niterations=50,  # Start with fewer iterations for testing
        binary_operators=["+", "*", "-"],
        unary_operators=["square"],
        populations=20,
        population_size=50,
        ncycles_per_iteration=550,
        model_selection="best",
        loss="loss(calculation, target) = (calculation - target)^2",
        maxsize=20,
        parsimony=0.0032,
        verbosity=1,
        random_state=0,
    )

    # Fit the model
    model.fit(X_train, y_train, variable_names=["X_k", "puzzle_k"])

    print(f"\n✅ Training complete!")

    return model


def analyze_results(model, X_train, y_train, lane_num: int):
    """
    Analyze discovered equations and accuracy.
    """
    print(f"\n{'='*80}")
    print(f"PySR Results for Lane {lane_num}")
    print(f"{'='*80}\n")

    # Show top equations
    print(f"🔬 Top Discovered Equations:\n")
    print(model)

    # Get calculations
    y_pred = model.calculate(X_train)

    # Calculate accuracy (exact matches mod 256)
    y_pred_mod = np.round(y_pred).astype(int) % 256
    y_true_mod = y_train.astype(int) % 256

    exact_matches = np.sum(y_pred_mod == y_true_mod)
    accuracy = (exact_matches / len(y_train)) * 100

    print(f"\n📊 Accuracy on Training Data:")
    print(f"   Exact matches (mod 256): {exact_matches}/{len(y_train)}")
    print(f"   Accuracy: {accuracy:.2f}%")

    # Show some examples
    print(f"\n📝 Sample Calculations vs Actual:")
    print(f"{'puzzle_k':>9} | {'X_k':>5} | {'Calculated':>9} | {'Actual':>6} | {'Match':>5}")
    print(f"{'-'*9}-+-{'-'*5}-+-{'-'*9}-+-{'-'*6}-+-{'-'*5}")

    for i in [0, 10, 20, 30, 40, 50, 60, 68]:
        if i < len(X_train):
            puzzle_k = int(X_train[i, 1])
            x_k = int(X_train[i, 0])
            pred = int(y_pred_mod[i])
            actual = int(y_true_mod[i])
            match = "✅" if pred == actual else "❌"
            print(f"{puzzle_k:9d} | {x_k:5d} | {pred:9d} | {actual:6d} | {match:>5}")

    return accuracy


def main():
    """Train PySR on lane 0."""
    print("="*80)
    print("AI LEARNS LADDER: Training Lane 0")
    print("="*80)

    data_dir = Path(__file__).parent / "data"

    # Load training data
    print(f"\n📂 Loading training data...")
    X_train, y_train = load_lane_data(0, data_dir)
    print(f"   ✅ Loaded {len(X_train)} training examples")

    # Train PySR
    model = train_pysr_lane(X_train, y_train, lane_num=0)

    # Analyze results
    accuracy = analyze_results(model, X_train, y_train, lane_num=0)

    # Save model
    model_path = Path(__file__).parent / "models" / "lane_00.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(model_path))

    print(f"\n💾 Model saved to: {model_path}")

    # Summary
    print(f"\n{'='*80}")
    print(f"TRAINING SUMMARY")
    print(f"{'='*80}\n")

    if accuracy >= 95:
        print(f"🎉 EXCELLENT! PySR discovered accurate equation ({accuracy:.1f}%)")
        print(f"\n📝 Next Steps:")
        print(f"   1. Extract discovered equation")
        print(f"   2. Validate with cryptographic proof")
        print(f"   3. Train remaining 15 lanes")
    elif accuracy >= 70:
        print(f"⚠️  GOOD but not perfect ({accuracy:.1f}%)")
        print(f"\n📝 Next Steps:")
        print(f"   1. Try more iterations")
        print(f"   2. Adjust PySR parameters")
        print(f"   3. Analyze failed cases")
    else:
        print(f"❌ LOW accuracy ({accuracy:.1f}%)")
        print(f"\n📝 Next Steps:")
        print(f"   1. Review training data")
        print(f"   2. Try different operators")
        print(f"   3. Increase iterations")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
