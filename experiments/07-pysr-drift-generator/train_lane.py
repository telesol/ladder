#!/usr/bin/env python3
"""
Train PySR on specific lane to discover drift generator formula

Usage: python3 train_lane.py --lane 8 --niter 100
"""

import argparse
import pandas as pd
import numpy as np
import json
import sys

def train_pysr(lane, niterations=100, timeout=3600):
    """Train PySR on specific lane"""
    try:
        from pysr import PySRRegressor
    except ImportError:
        print("ERROR: PySR not installed!")
        print("Install with: pip install pysr")
        return None

    print(f"="*60)
    print(f"TRAINING PYSR ON LANE {lane}")
    print(f"="*60)
    print()

    # Load training data
    print("Loading data...")
    train = pd.read_csv('experiments/07-pysr-drift-generator/train.csv')
    val = pd.read_csv('experiments/07-pysr-drift-generator/val.csv')
    test = pd.read_csv('experiments/07-pysr-drift-generator/test.csv')

    # Filter for this lane
    train_lane = train[train['lane'] == lane].copy()
    val_lane = val[val['lane'] == lane].copy()
    test_lane = test[test['lane'] == lane].copy()

    print(f"  Train: {len(train_lane)} samples")
    print(f"  Val:   {len(val_lane)} samples")
    print(f"  Test:  {len(test_lane)} samples")
    print()

    # Features
    X_train = train_lane[['k', 'drift_prev']].values
    y_train = train_lane['drift'].values % 256

    X_val = val_lane[['k', 'drift_prev']].values
    y_val = val_lane['drift'].values % 256

    X_test = test_lane[['k', 'drift_prev']].values
    y_test = test_lane['drift'].values % 256

    print(f"Features: k (puzzle number), drift_prev (previous drift)")
    print(f"Target: drift (mod 256)")
    print()

    # Configure PySR
    print(f"Configuring PySR...")
    print(f"  Iterations: {niterations}")
    print(f"  Timeout: {timeout}s ({timeout/3600:.1f}h)")
    print()

    model = PySRRegressor(
        niterations=niterations,
        binary_operators=["+", "*", "-"],
        unary_operators=["square", "cube"],
        complexity_of_constants=2,
        populations=30,
        population_size=100,
        ncycles_per_iteration=550,
        maxsize=15,
        timeout_in_seconds=timeout,
        verbosity=1,
        progress=True,
    )

    # Train
    print("Training PySR...")
    print("(This may take a while - check progress above)")
    print()

    model.fit(X_train, y_train)

    # Evaluate
    print()
    print("="*60)
    print("RESULTS")
    print("="*60)
    print()

    train_score = model.score(X_train, y_train)
    val_score = model.score(X_val, y_val)
    test_score = model.score(X_test, y_test)

    print(f"R² Scores:")
    print(f"  Train: {train_score:.4f}")
    print(f"  Val:   {val_score:.4f}")
    print(f"  Test:  {test_score:.4f}")
    print()

    # Get best formulas
    print("Top 5 formulas:")
    print()
    try:
        equations = model.equations_
        for i, row in equations.head(5).iterrows():
            print(f"  {i+1}. Complexity {row['complexity']}: {row['equation']}")
            print(f"     Loss: {row['loss']:.6f}, Score: {row['score']:.6f}")
            print()
    except Exception as e:
        print(f"  (Could not display equations: {e})")
        print()

    # Best formula
    best_eq = model.get_best()
    print(f"Best formula: {best_eq}")
    print()

    # Test accuracy (exact matches mod 256)
    y_pred_train = model.predict(X_train).astype(int) % 256
    y_pred_val = model.predict(X_val).astype(int) % 256
    y_pred_test = model.predict(X_test).astype(int) % 256

    train_acc = (y_pred_train == y_train).mean()
    val_acc = (y_pred_val == y_val).mean()
    test_acc = (y_pred_test == y_test).mean()

    print(f"Exact match accuracy (mod 256):")
    print(f"  Train: {train_acc*100:.2f}%")
    print(f"  Val:   {val_acc*100:.2f}%")
    print(f"  Test:  {test_acc*100:.2f}%")
    print()

    # Save results
    results = {
        'lane': lane,
        'niterations': niterations,
        'best_formula': str(best_eq),
        'r2_train': float(train_score),
        'r2_val': float(val_score),
        'r2_test': float(test_score),
        'accuracy_train': float(train_acc),
        'accuracy_val': float(val_acc),
        'accuracy_test': float(test_acc),
    }

    output_file = f'experiments/07-pysr-drift-generator/results/lane_{lane}_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✅ Results saved to: {output_file}")
    print()

    # Save model (using pickle instead of deprecated save method)
    import pickle
    model_file = f'experiments/07-pysr-drift-generator/results/lane_{lane}_model.pkl'
    try:
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        print(f"✅ Model saved to: {model_file}")
    except Exception as e:
        print(f"⚠️  Model save failed: {e}")
    print()

    return results

def main():
    parser = argparse.ArgumentParser(description='Train PySR on specific lane')
    parser.add_argument('--lane', type=int, required=True, help='Lane number (0-15)')
    parser.add_argument('--niter', type=int, default=100, help='Number of iterations')
    parser.add_argument('--timeout', type=int, default=3600, help='Timeout in seconds')

    args = parser.parse_args()

    if args.lane < 0 or args.lane > 15:
        print(f"ERROR: Lane must be 0-15, got {args.lane}")
        return 1

    results = train_pysr(args.lane, args.niter, args.timeout)

    if results is None:
        return 1

    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Lane {args.lane}: {results['accuracy_val']*100:.2f}% validation accuracy")
    print(f"Formula: {results['best_formula']}")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
