#!/usr/bin/env python3
"""
Task 1: Train PySR on Lane 8 with k<64 filter

Hypothesis: Lane 8 is STABLE for k<64 (drift always = 0)
Expected: 100% accuracy with formula `drift = 0` or `drift = drift_prev`
"""

import pandas as pd
import numpy as np
from pysr import PySRRegressor
import json
import os
from datetime import datetime

def main():
    print("=" * 80)
    print("TASK 1: PySR Lane 8 with k<64 Filter")
    print("=" * 80)
    print()

    # Load datasets
    print("Loading filtered datasets (k<64)...")
    train_df = pd.read_csv('train_k64_filtered.csv')
    val_df = pd.read_csv('val_k64_filtered.csv')
    test_df = pd.read_csv('test_k64_filtered.csv')

    print(f"  Train: {len(train_df)} samples")
    print(f"  Val:   {len(val_df)} samples")
    print(f"  Test:  {len(test_df)} samples")
    print()

    # Filter for lane 8 only
    print("Filtering for lane 8...")
    train_lane8 = train_df[train_df['lane'] == 8].copy()
    val_lane8 = val_df[val_df['lane'] == 8].copy()
    test_lane8 = test_df[test_df['lane'] == 8].copy()

    print(f"  Train: {len(train_lane8)} samples")
    print(f"  Val:   {len(val_lane8)} samples")
    print(f"  Test:  {len(test_lane8)} samples")
    print()

    # Verify all k < 64
    max_k_train = train_lane8['k'].max()
    max_k_val = val_lane8['k'].max()
    max_k_test = test_lane8['k'].max()

    print(f"Max k in train: {max_k_train}")
    print(f"Max k in val:   {max_k_val}")
    print(f"Max k in test:  {max_k_test}")
    assert max_k_train < 64 and max_k_val < 64 and max_k_test < 64, "ERROR: Some k >= 64!"
    print("✓ All k < 64 confirmed")
    print()

    # Analyze drift values
    print("Analyzing drift values for lane 8...")
    unique_drifts_train = train_lane8['drift'].unique()
    unique_drifts_val = val_lane8['drift'].unique()
    unique_drifts_test = test_lane8['drift'].unique()

    print(f"  Train unique drifts: {sorted(unique_drifts_train)}")
    print(f"  Val unique drifts:   {sorted(unique_drifts_val)}")
    print(f"  Test unique drifts:  {sorted(unique_drifts_test)}")
    print()

    # Count zeros
    train_zeros = (train_lane8['drift'] == 0).sum()
    val_zeros = (val_lane8['drift'] == 0).sum()
    test_zeros = (test_lane8['drift'] == 0).sum()

    print(f"  Train: {train_zeros}/{len(train_lane8)} = {100*train_zeros/len(train_lane8):.1f}% zeros")
    print(f"  Val:   {val_zeros}/{len(val_lane8)} = {100*val_zeros/len(val_lane8):.1f}% zeros")
    print(f"  Test:  {test_zeros}/{len(test_lane8)} = {100*test_zeros/len(test_lane8):.1f}% zeros")
    print()

    # Prepare features
    print("Preparing features...")
    feature_cols = ['k', 'lane', 'drift_prev', 'A']

    X_train = train_lane8[feature_cols].values
    y_train = train_lane8['drift'].values

    X_val = val_lane8[feature_cols].values
    y_val = val_lane8['drift'].values

    X_test = test_lane8[feature_cols].values
    y_test = test_lane8['drift'].values

    print(f"  X_train shape: {X_train.shape}")
    print(f"  X_val shape:   {X_val.shape}")
    print(f"  X_test shape:  {X_test.shape}")
    print()

    # Train PySR
    print("Training PySR (this should be quick for lane 8)...")
    print()

    model = PySRRegressor(
        niterations=50,
        binary_operators=["+", "*", "-"],
        unary_operators=[],
        maxsize=7,  # Minimum required by PySR
        populations=20,
        population_size=30,
        timeout_in_seconds=1800,  # 30 minutes max
        parsimony=0.001,
        model_selection="best",
        verbosity=1,
        progress=True,
        random_state=42
    )

    start_time = datetime.now()
    model.fit(X_train, y_train, variable_names=feature_cols)
    train_time = (datetime.now() - start_time).total_seconds()

    print()
    print("=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)
    print(f"Training time: {train_time:.1f} seconds ({train_time/60:.1f} minutes)")
    print()

    # Get best equation
    print("Best equation found:")
    print(model)
    print()

    # Predictions
    print("Making predictions...")
    y_train_pred = model.predict(X_train)
    y_val_pred = model.predict(X_val)
    y_test_pred = model.predict(X_test)

    # Round to nearest integer and mod 256
    y_train_pred_int = np.round(y_train_pred).astype(int) % 256
    y_val_pred_int = np.round(y_val_pred).astype(int) % 256
    y_test_pred_int = np.round(y_test_pred).astype(int) % 256

    # Calculate exact match accuracy
    train_exact = np.sum(y_train_pred_int == y_train)
    val_exact = np.sum(y_val_pred_int == y_val)
    test_exact = np.sum(y_test_pred_int == y_test)

    train_acc = 100 * train_exact / len(y_train)
    val_acc = 100 * val_exact / len(y_val)
    test_acc = 100 * test_exact / len(y_test)

    # Also calculate MSE
    train_mse = np.mean((y_train_pred - y_train) ** 2)
    val_mse = np.mean((y_val_pred - y_val) ** 2)
    test_mse = np.mean((y_test_pred - y_test) ** 2)

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    print("Exact Match Accuracy (mod 256):")
    print(f"  Train: {train_exact}/{len(y_train)} = {train_acc:.2f}%")
    print(f"  Val:   {val_exact}/{len(y_val)} = {val_acc:.2f}%")
    print(f"  Test:  {test_exact}/{len(y_test)} = {test_acc:.2f}%")
    print()

    print("Mean Squared Error:")
    print(f"  Train MSE: {train_mse:.4f}")
    print(f"  Val MSE:   {val_mse:.4f}")
    print(f"  Test MSE:  {test_mse:.4f}")
    print()

    # Check if hypothesis confirmed
    hypothesis_confirmed = test_acc >= 99.0

    print("=" * 80)
    print(f"Hypothesis (drift=0 for lane 8, k<64): {'✓ CONFIRMED' if hypothesis_confirmed else '✗ REJECTED'}")
    print("=" * 80)
    print()

    # Show some example predictions vs actual
    print("Sample predictions (first 10):")
    print("k   | drift_actual | drift_pred | match")
    print("-" * 50)
    for i in range(min(10, len(test_lane8))):
        k = test_lane8.iloc[i]['k']
        actual = y_test[i]
        pred = y_test_pred_int[i]
        match = "✓" if actual == pred else "✗"
        print(f"{k:3d} | {actual:12d} | {pred:10d} | {match}")
    print()

    # Save results
    results = {
        "task": "Task 1 - Lane 8 (k<64)",
        "timestamp": datetime.now().isoformat(),
        "train_time_seconds": float(train_time),
        "best_formula": str(model),
        "data_stats": {
            "train_samples": int(len(train_lane8)),
            "val_samples": int(len(val_lane8)),
            "test_samples": int(len(test_lane8)),
            "train_zeros_percent": float(100 * train_zeros / len(train_lane8)),
            "val_zeros_percent": float(100 * val_zeros / len(val_lane8)),
            "test_zeros_percent": float(100 * test_zeros / len(test_lane8))
        },
        "accuracy": {
            "train_exact_match_percent": float(train_acc),
            "val_exact_match_percent": float(val_acc),
            "test_exact_match_percent": float(test_acc),
            "train_mse": float(train_mse),
            "val_mse": float(val_mse),
            "test_mse": float(test_mse)
        },
        "hypothesis_confirmed": bool(hypothesis_confirmed)
    }

    os.makedirs('results', exist_ok=True)
    output_file = 'results/task1_lane8_k64_filtered.json'

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

    # Print final report
    print("=" * 80)
    print("TASK 1 FINAL REPORT")
    print("=" * 80)
    print()
    print(f"Formula: {model}")
    print(f"Train accuracy: {train_acc:.2f}%")
    print(f"Val accuracy: {val_acc:.2f}%")
    print(f"Test accuracy: {test_acc:.2f}%")
    print(f"Confirms hypothesis: {'YES ✓' if hypothesis_confirmed else 'NO ✗'}")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
