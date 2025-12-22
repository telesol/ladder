#!/usr/bin/env python3
"""
Piecewise PySR Training: Train separate models for each d_n group.

Based on error analysis showing d_n-specific patterns:
- d=1: 15 samples, correction ×1.5665
- d=2: 8 samples, correction ×1.2782 (100% exact on validation!)
- d=4: 5 samples, correction ×1.5899 (100% exact on validation!)

Hypothesis: Each d_n group has its OWN formula!
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

try:
    from pysr import PySRRegressor
    PYSR_AVAILABLE = True
except ImportError:
    PYSR_AVAILABLE = False
    print("ERROR: PySR not installed!")
    exit(1)

from convergent_database import D_SEQUENCE

print("=" * 70)
print("PIECEWISE PYSR TRAINING: Separate Models per d_n Group")
print("=" * 70)

# Load simple feature matrix
print("\n1. Loading simple feature matrix...")
df = pd.read_csv('feature_matrix_simple.csv')
print(f"   Loaded {len(df)} samples with {len(df.columns)-1} features")

# Group by d_n
print("\n2. Grouping by d_n...")
groups = {}
for _, row in df.iterrows():
    d = int(row['d_n'])
    if d not in groups:
        groups[d] = []
    groups[d].append(row)

for d, samples in sorted(groups.items()):
    print(f"   d={d}: {len(samples)} samples")

# Train models for d=1, d=2, d=4 (skip d=3, d=7 - only 1 sample each)
train_groups = [1, 2, 4]

all_results = {}

for d_val in train_groups:
    print(f"\n{'=' * 70}")
    print(f"TRAINING MODEL FOR d={d_val}")
    print(f"{'=' * 70}")

    # Get samples for this d_n group
    group_df = pd.DataFrame([s for d, samples in groups.items() if d == d_val for s in samples])

    print(f"\n   Samples: {len(group_df)}")
    print(f"   n-values: {sorted(group_df['n'].tolist())}")

    # Split train/validation (80/20)
    train_size = int(len(group_df) * 0.8)
    if train_size < 3:
        print(f"   ⚠️  Too few samples ({len(group_df)}) - training on all, no validation")
        train_df = group_df
        val_df = pd.DataFrame()
    else:
        train_df = group_df.iloc[:train_size]
        val_df = group_df.iloc[train_size:]

    X_train = train_df.drop(['target_m'], axis=1).values
    y_train = train_df['target_m'].values
    feature_names = train_df.drop(['target_m'], axis=1).columns.tolist()

    print(f"   Training: {len(X_train)} samples")
    if len(val_df) > 0:
        print(f"   Validation: {len(val_df)} samples")
        X_val = val_df.drop(['target_m'], axis=1).values
        y_val = val_df['target_m'].values

    # Configure PySR
    print(f"\n   Configuring PySR...")
    model = PySRRegressor(
        procs=4,
        multithreading=True,
        niterations=50,  # Less iterations per group (faster)
        binary_operators=["+", "*", "-", "/"],
        unary_operators=["square", "cube"],
        populations=20,
        population_size=50,
        ncycles_per_iteration=500,
        maxsize=12,  # Smaller max size for simpler formulas
        parsimony=0.001,
        verbosity=1,
        progress=True,
        temp_equation_file=True,
    )

    # Train
    print(f"\n   Training PySR (d={d_val})...")
    start_time = datetime.now()

    try:
        model.fit(X_train, y_train, variable_names=feature_names)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n   ✅ Training complete! ({duration:.1f}s)")
        print(f"\n   Best formula: {model.sympy()}")

        # Validate
        if len(val_df) > 0:
            print(f"\n   Validating on holdout set...")
            y_pred = model.predict(X_val)

            exact_matches = 0
            for i, (pred, actual) in enumerate(zip(y_pred, y_val)):
                pred_int = int(round(pred))
                match = (pred_int == actual)
                if match:
                    exact_matches += 1

                n_val = val_df['n'].iloc[i]
                print(f"      n={n_val}: pred={pred_int:>15,}, actual={actual:>15,}, match={match}")

            accuracy = exact_matches / len(y_val) * 100
            print(f"\n   Accuracy: {exact_matches}/{len(y_val)} = {accuracy:.1f}%")
        else:
            # Validate on training set (not ideal, but better than nothing)
            print(f"\n   Validating on training set (no holdout)...")
            y_pred = model.predict(X_train)

            exact_matches = 0
            for i, (pred, actual) in enumerate(zip(y_pred, y_train)):
                pred_int = int(round(pred))
                match = (pred_int == actual)
                if match:
                    exact_matches += 1

            accuracy = exact_matches / len(y_train) * 100
            print(f"\n   Training accuracy: {exact_matches}/{len(y_train)} = {accuracy:.1f}%")

        # Save model
        import pickle
        model_file = f'm_sequence_model_d{d_val}.pkl'
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        print(f"\n   Saved model to: {model_file}")

        # Store results
        all_results[f'd_{d_val}'] = {
            'formula': str(model.sympy()),
            'training_samples': len(X_train),
            'validation_samples': len(val_df) if len(val_df) > 0 else 0,
            'accuracy_percent': float(accuracy),
            'duration_seconds': duration,
            'n_values': sorted(group_df['n'].tolist())
        }

    except Exception as e:
        print(f"\n   ❌ ERROR: {e}")
        all_results[f'd_{d_val}'] = {
            'error': str(e)
        }

# Save combined results
print(f"\n{'=' * 70}")
print("SAVING COMBINED RESULTS")
print(f"{'=' * 70}")

output = {
    'metadata': {
        'timestamp': datetime.now().isoformat(),
        'approach': 'piecewise_by_d',
        'groups_trained': train_groups
    },
    'results': all_results
}

with open('piecewise_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nSaved results to: piecewise_results.json")

# Summary
print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")

for d_val in train_groups:
    key = f'd_{d_val}'
    if key in all_results and 'error' not in all_results[key]:
        result = all_results[key]
        print(f"\nd={d_val}:")
        print(f"  Formula: {result['formula']}")
        print(f"  Accuracy: {result['accuracy_percent']:.1f}%")
        print(f"  Samples: {result['training_samples']} train, {result['validation_samples']} val")
        print(f"  Duration: {result['duration_seconds']:.1f}s")

print(f"\n✅ Piecewise training complete!")
