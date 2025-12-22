#!/usr/bin/env python3
"""
Task 2: PySR Lane 7 with k<64 Filter
Train PySR on Lane 7 using only k<64 data to find stable-regime formula.
Expected: >90% accuracy, likely finding affine pattern with A=23
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from pysr import PySRRegressor

print("=" * 80)
print("TASK 2: PySR Lane 7 (k<64 Filtered)")
print("=" * 80)

# Load filtered datasets
train_df = pd.read_csv('experiments/07-pysr-drift-generator/train_k64_filtered.csv')
val_df = pd.read_csv('experiments/07-pysr-drift-generator/val_k64_filtered.csv')
test_df = pd.read_csv('experiments/07-pysr-drift-generator/test_k64_filtered.csv')

print(f"\nDataset sizes:")
print(f"Train: {len(train_df)} rows")
print(f"Val: {len(val_df)} rows")
print(f"Test: {len(test_df)} rows")

# Filter for lane 7 only
lane = 7
train_lane = train_df[train_df['lane'] == lane].copy()
val_lane = val_df[val_df['lane'] == lane].copy()
test_lane = test_df[test_df['lane'] == lane].copy()

print(f"\nLane {lane} sizes:")
print(f"Train: {len(train_lane)} rows")
print(f"Val: {len(val_lane)} rows")
print(f"Test: {len(test_lane)} rows")

# Verify k < 64
print(f"\nk range in train: {train_lane['k'].min()} to {train_lane['k'].max()}")
print(f"k range in val: {val_lane['k'].min()} to {val_lane['k'].max()}")
print(f"k range in test: {test_lane['k'].min()} to {test_lane['k'].max()}")

# Prepare features and targets
X_train = train_lane[['k', 'drift_prev']].values
y_train = train_lane['drift'].values

X_val = val_lane[['k', 'drift_prev']].values
y_val = val_lane['drift'].values

X_test = test_lane[['k', 'drift_prev']].values
y_test = test_lane['drift'].values

print(f"\nTraining PySR on Lane {lane}...")
print("Expected: Affine pattern with A=23 (prime multiplier)")

# Train PySR
model = PySRRegressor(
    niterations=100,
    binary_operators=["+", "*", "-", "%"],
    unary_operators=["square"],
    maxsize=12,
    timeout_in_seconds=3600,  # 1 hour max
    populations=15,
    population_size=33,
    ncyclesperiteration=550,
    model_selection="accuracy",
    verbosity=1,
    random_state=42,
    precision=32
)

model.fit(X_train, y_train, variable_names=["k", "drift_prev"])

print("\n" + "=" * 80)
print("TRAINING COMPLETE - Best Equations:")
print("=" * 80)
print(model)

# Get predictions
y_train_pred = model.predict(X_train)
y_val_pred = model.predict(X_val)
y_test_pred = model.predict(X_test)

# Compute predictions mod 256
y_train_pred_mod = np.round(y_train_pred).astype(int) % 256
y_val_pred_mod = np.round(y_val_pred).astype(int) % 256
y_test_pred_mod = np.round(y_test_pred).astype(int) % 256

# Calculate exact match accuracy
train_exact = np.mean(y_train_pred_mod == y_train) * 100
val_exact = np.mean(y_val_pred_mod == y_val) * 100
test_exact = np.mean(y_test_pred_mod == y_test) * 100

print("\n" + "=" * 80)
print("EXACT MATCH ACCURACY (mod 256):")
print("=" * 80)
print(f"Train: {train_exact:.2f}% ({np.sum(y_train_pred_mod == y_train)}/{len(y_train)})")
print(f"Val:   {val_exact:.2f}% ({np.sum(y_val_pred_mod == y_val)}/{len(y_val)})")
print(f"Test:  {test_exact:.2f}% ({np.sum(y_test_pred_mod == y_test)}/{len(y_test)})")

# Get best equation
best_equation = str(model.get_best())
print(f"\nBest equation: {best_equation}")

# Check for multiplier 23
contains_23 = '23' in best_equation
print(f"Contains A=23 multiplier: {'YES' if contains_23 else 'NO'}")

# Check for drift_prev term
contains_drift_prev = 'drift_prev' in best_equation
print(f"Contains drift_prev term: {'YES' if contains_drift_prev else 'NO'}")

# Check for k-dependent terms
contains_k = 'k' in best_equation and 'drift_prev' not in best_equation.replace('k', '')
print(f"Contains k-dependent terms: {'YES' if contains_k else 'NO'}")

# Improvement over H4 (82.4%)
h4_baseline = 82.4
improvement = test_exact - h4_baseline
print(f"\nImprovement over H4 baseline (82.4%): {improvement:+.2f}%")

# Save results
results_dir = Path('experiments/07-pysr-drift-generator/results')
results_dir.mkdir(exist_ok=True)

results = {
    'task': 'task2_lane7_k64_filtered',
    'lane': lane,
    'filter': 'k < 64',
    'formula': best_equation,
    'train_accuracy': float(train_exact),
    'val_accuracy': float(val_exact),
    'test_accuracy': float(test_exact),
    'train_size': len(train_lane),
    'val_size': len(val_lane),
    'test_size': len(test_lane),
    'contains_A23': contains_23,
    'contains_drift_prev': contains_drift_prev,
    'contains_k': contains_k,
    'h4_baseline': h4_baseline,
    'improvement': float(improvement),
    'pysr_settings': {
        'niterations': 100,
        'binary_operators': ['+', '*', '-', '%'],
        'unary_operators': ['square'],
        'maxsize': 12,
        'timeout_seconds': 3600
    }
}

output_file = results_dir / 'task2_lane7_k64_filtered.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_file}")

# Print final report
print("\n" + "=" * 80)
print("TASK 2 RESULTS - LANE 7 (k<64):")
print("=" * 80)
print(f"Formula: {best_equation}")
print(f"Train accuracy: {train_exact:.2f}%")
print(f"Val accuracy: {val_exact:.2f}%")
print(f"Test accuracy: {test_exact:.2f}%")
print(f"Contains A=23 multiplier: {'YES' if contains_23 else 'NO'}")
print(f"Improvement over H4 (82.4%): {improvement:+.2f}%")
print("=" * 80)

# Show some example predictions
print("\nExample Predictions (first 10 test samples):")
print("k | drift_prev | actual | predicted | match")
print("-" * 50)
for i in range(min(10, len(test_lane))):
    k_val = int(X_test[i, 0])
    dp_val = int(X_test[i, 1])
    actual = int(y_test[i])
    pred = int(y_test_pred_mod[i])
    match = "✓" if actual == pred else "✗"
    print(f"{k_val:2d} | {dp_val:3d} | {actual:3d} | {pred:3d} | {match}")

print("\nTask 2 complete!")
