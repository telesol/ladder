#!/usr/bin/env python3
"""
Train PySR to Discover the DRIFT Formula

The real ladder formula is:
    X_{k+1}[lane] = (A[lane]^4 * X_k[lane] + drift[k→k+1][lane]) mod 256

Where A coefficients are known, but drift values change per puzzle.

This script trains PySR to discover:
    drift = f(puzzle_k, lane, X_k, ...)

If successful, we can generate ANY future puzzle!
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from pysr import PySRRegressor


def load_drift_training_data():
    """
    Extract drift values from calibration file.

    Returns:
        X_train: [[puzzle_k, lane, X_k], ...] features
        y_train: [drift, ...] targets
    """
    # Load calibration with known drift values
    calib_path = Path(__file__).parent.parent.parent / "out" / "ladder_calib_ultimate.json"
    csv_path = Path(__file__).parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"

    with open(calib_path) as f:
        calib = json.load(f)

    df = pd.read_csv(csv_path)

    print("📂 Loading drift training data...")

    drift_data = []

    # Extract drift values for puzzles 1-69 (training set)
    for puzzle_k in range(1, 70):
        drift_key = f"{puzzle_k}→{puzzle_k+1}"
        if drift_key not in calib['drifts']:
            continue

        # Get current key bytes (little-endian)
        key_k_hex = df[df['puzzle'] == puzzle_k].iloc[0]['key_hex_64']
        key_k_bytes = bytes(reversed(bytes.fromhex(key_k_hex[32:64])))

        # For each lane, create training example
        for lane in range(16):
            drift = calib['drifts'][drift_key][str(lane)]
            X_k = key_k_bytes[lane]

            drift_data.append({
                'puzzle_k': puzzle_k,
                'lane': lane,
                'X_k': X_k,
                'drift': drift
            })

    train_df = pd.DataFrame(drift_data)

    # Features: puzzle_k, lane, X_k
    X = train_df[['puzzle_k', 'lane', 'X_k']].values

    # Target: drift
    y = train_df['drift'].values

    print(f"✅ Loaded {len(X)} training examples")
    print(f"   Puzzles: 1-69")
    print(f"   Lanes: 0-15")
    print(f"   Features: puzzle_k, lane, X_k")
    print(f"   Target: drift")

    return X, y


def train_drift_formula(X_train, y_train):
    """
    Train PySR to discover the drift formula.

    Goal: drift = f(puzzle_k, lane, X_k)
    """
    print(f"\n{'='*80}")
    print(f"Training PySR to Discover Drift Formula")
    print(f"{'='*80}\n")

    print(f"📊 Training data:")
    print(f"   Samples: {len(X_train)}")
    print(f"   Features: puzzle_k (1-69), lane (0-15), X_k (0-255)")
    print(f"   Target: drift (0-255)")
    print(f"   drift range: [{y_train.min()}, {y_train.max()}]")

    print(f"\n🤖 Starting PySR training...")
    print(f"   This may take 10-30 minutes for complex patterns...")

    model = PySRRegressor(
        niterations=100,  # More iterations for complex patterns
        binary_operators=["+", "*", "-", "/"],
        unary_operators=["square", "cube"],
        populations=30,
        population_size=100,
        ncycles_per_iteration=550,
        model_selection="best",
        loss="loss(calculation, target) = (calculation - target)^2",
        maxsize=30,  # Allow more complex formulas
        parsimony=0.001,  # Favor simpler formulas
        verbosity=1,
        random_state=42,
        # Timeout after 30 minutes
        timeout_in_seconds=1800,
    )

    # Fit the model
    model.fit(X_train, y_train, variable_names=["puzzle_k", "lane", "X_k"])

    print(f"\n✅ Training complete!")

    return model


def analyze_results(model, X_train, y_train):
    """
    Analyze discovered drift formula.
    """
    print(f"\n{'='*80}")
    print(f"PySR Results: Drift Formula Discovery")
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

    # Calculate mean absolute error
    mae = np.mean(np.abs(y_pred - y_train))

    print(f"\n📊 Accuracy on Training Data:")
    print(f"   Exact matches (mod 256): {exact_matches}/{len(y_train)}")
    print(f"   Accuracy: {accuracy:.2f}%")
    print(f"   Mean Absolute Error: {mae:.2f}")

    # Show sample calculations for lane 0
    print(f"\n📝 Sample Calculations (Lane 0 only):")
    print(f"{'puzzle_k':>9} | {'X_k':>5} | {'Calculated':>9} | {'Actual':>6} | {'Match':>5}")
    print(f"{'-'*9}-+-{'-'*5}-+-{'-'*9}-+-{'-'*6}-+-{'-'*5}")

    lane0_indices = np.where(X_train[:, 1] == 0)[0][:20]  # First 20 lane 0 examples

    for idx in lane0_indices:
        puzzle_k = int(X_train[idx, 0])
        x_k = int(X_train[idx, 2])
        pred = int(y_pred_mod[idx])
        actual = int(y_true_mod[idx])
        match = "✅" if pred == actual else "❌"
        print(f"{puzzle_k:9d} | {x_k:5d} | {pred:9d} | {actual:6d} | {match:>5}")

    return accuracy


def main():
    """Train PySR to discover drift formula."""
    print("="*80)
    print("AI LEARNS LADDER: Drift Formula Discovery")
    print("="*80)

    # Load drift training data
    print(f"\n📂 Loading drift training data...")
    X_train, y_train = load_drift_training_data()

    # Train PySR
    model = train_drift_formula(X_train, y_train)

    # Analyze results
    accuracy = analyze_results(model, X_train, y_train)

    # Save model
    model_path = Path(__file__).parent / "models" / "drift_formula.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)

    # PySR uses pickle protocol
    import pickle
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    print(f"\n💾 Model saved to: {model_path}")

    # Summary
    print(f"\n{'='*80}")
    print(f"TRAINING SUMMARY")
    print(f"{'='*80}\n")

    if accuracy >= 95:
        print(f"🎉 EXCELLENT! PySR discovered accurate drift formula ({accuracy:.1f}%)")
        print(f"\n📝 Next Steps:")
        print(f"   1. Validate formula on test set (puzzle 70)")
        print(f"   2. Generate puzzles 71-95 using discovered formula")
        print(f"   3. Derive Bitcoin addresses for validation")
        print(f"   4. Achieve 100% cryptographic proof")
    elif accuracy >= 70:
        print(f"⚠️  GOOD but not perfect ({accuracy:.1f}%)")
        print(f"\n📝 Next Steps:")
        print(f"   1. Try more iterations (200, 500)")
        print(f"   2. Add more operators (mod, abs)")
        print(f"   3. Analyze pattern in failed calculations")
    else:
        print(f"❌ LOW accuracy ({accuracy:.1f}%)")
        print(f"\n📝 Possible Issues:")
        print(f"   1. Drift may not have simple mathematical formula")
        print(f"   2. May require lookup table or neural network")
        print(f"   3. Pattern may be cryptographically random")
        print(f"\n💡 Alternative Approaches:")
        print(f"   - Train neural network (LSTM/Transformer)")
        print(f"   - Use calibration data directly (no discovery)")
        print(f"   - Analyze if pattern is truly learnable")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
