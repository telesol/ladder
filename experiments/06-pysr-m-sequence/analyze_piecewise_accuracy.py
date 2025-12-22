#!/usr/bin/env python3
"""Analyze piecewise model predictions vs actual values."""

import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

# Load data
with open('m_sequence_data.json') as f:
    data = json.load(f)

# Load simple features
df = pd.read_csv('feature_matrix_simple.csv')

# Load models
model_d1 = pickle.load(open('m_sequence_model_d1.pkl', 'rb'))
model_d2 = pickle.load(open('m_sequence_model_d2.pkl', 'rb'))
model_d4 = pickle.load(open('m_sequence_model_d4.pkl', 'rb'))

# Split into train/validation
train_df = df[df['n'] <= 25]
val_df = df[df['n'] > 25]

print("=" * 80)
print("PIECEWISE MODEL ANALYSIS")
print("=" * 80)

results = []

for d_val, model, name in [(1, model_d1, 'd=1'), (2, model_d2, 'd=2'), (4, model_d4, 'd=4')]:
    print(f"\n{name} Group Analysis")
    print("-" * 80)

    # Filter validation set for this d value
    val_subset = val_df[val_df['d_n'] == d_val].copy()

    if len(val_subset) == 0:
        print(f"  No validation samples for {name}")
        continue

    # Get features
    feature_cols = ['n', 'd_n', 'power_of_2', 'n_squared', 'n_cubed', 'd_n_squared', 'prev_m', 'prev_d']
    X_val = val_subset[feature_cols].values
    y_true = val_subset['target_m'].values

    # Predict
    y_pred_float = model.predict(X_val)
    y_pred = np.round(y_pred_float).astype(int)

    # Calculate metrics
    exact_matches = np.sum(y_pred == y_true)
    accuracy = 100 * exact_matches / len(y_true)

    # Error analysis
    errors = y_pred - y_true
    abs_errors = np.abs(errors)
    rel_errors = 100 * abs_errors / np.maximum(y_true, 1)

    print(f"  Validation samples: {len(val_subset)}")
    print(f"  Exact matches: {exact_matches}/{len(y_true)} ({accuracy:.1f}%)")
    print(f"  Mean absolute error: {np.mean(abs_errors):.1f}")
    print(f"  Max absolute error: {np.max(abs_errors)}")
    print(f"  Mean relative error: {np.mean(rel_errors):.1f}%")
    print()
    print("  Sample predictions:")
    print("  n    true_m           pred_m           error      rel_err")
    print("  " + "-" * 70)

    for i in range(len(val_subset)):
        n = val_subset.iloc[i]['n']
        true_m = y_true[i]
        pred_m = y_pred[i]
        err = errors[i]
        rel_err = rel_errors[i]

        print(f"  {n:2d}   {true_m:15d}  {pred_m:15d}  {err:10d}  {rel_err:6.1f}%")

        results.append({
            'd': int(d_val),
            'n': int(n),
            'true_m': int(true_m),
            'pred_m': int(pred_m),
            'error': int(err),
            'rel_error_pct': float(rel_err)
        })

# Overall summary
print("\n" + "=" * 80)
print("OVERALL SUMMARY")
print("=" * 80)

all_exact = sum(1 for r in results if r['error'] == 0)
all_total = len(results)
all_accuracy = 100 * all_exact / all_total if all_total > 0 else 0

print(f"Total validation samples: {all_total}")
print(f"Total exact matches: {all_exact}/{all_total} ({all_accuracy:.1f}%)")

# Within tolerance
for tol in [10, 100, 1000, 10000]:
    within = sum(1 for r in results if abs(r['error']) <= tol)
    pct = 100 * within / all_total if all_total > 0 else 0
    print(f"Within ±{tol:5d}: {within}/{all_total} ({pct:.1f}%)")

# Save results
with open('piecewise_validation_analysis.json', 'w') as f:
    json.dump({
        'summary': {
            'total_samples': all_total,
            'exact_matches': all_exact,
            'accuracy_percent': all_accuracy
        },
        'predictions': results
    }, f, indent=2)

print("\n✅ Results saved to: piecewise_validation_analysis.json")
