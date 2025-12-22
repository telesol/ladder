#!/usr/bin/env python3
"""
Task 5: Regime-Specific PySR - Proof of Concept

Train only Lane 0 with minimal iterations to demonstrate the approach.
"""

import pandas as pd
import numpy as np
from pysr import PySRRegressor
import json
import time

def train_regime_model(train_data, val_data, test_data, regime_name, regime_filter):
    """Train PySR model for specific regime."""
    print(f"\n{'='*60}")
    print(f"{regime_name} Regime")
    print(f"{'='*60}")

    # Filter by regime
    train_regime = train_data[regime_filter(train_data['k'])].copy()
    val_regime = val_data[regime_filter(val_data['k'])].copy()
    test_regime = test_data[regime_filter(test_data['k'])].copy()

    print(f"Training samples: {len(train_regime)}")
    print(f"Validation samples: {len(val_regime)}")
    print(f"Test samples: {len(test_regime)}")

    if len(train_regime) < 3:
        print(f"❌ Not enough training samples, skipping")
        return None

    # Prepare features
    X_train = train_regime[['k', 'drift_prev', 'A']].values
    y_train = train_regime['drift'].values

    # Train PySR (MINIMAL VERSION)
    print(f"\n🚀 Training PySR model (minimal)...")
    start_time = time.time()

    model = PySRRegressor(
        niterations=5,  # MINIMAL
        binary_operators=["+", "*"],
        unary_operators=[],
        populations=5,
        population_size=30,
        maxsize=8,
        timeout_in_seconds=60,  # 1 minute max
        verbosity=0,
        deterministic=True,
        parallelism='serial'
    )

    try:
        model.fit(X_train, y_train)
        elapsed = time.time() - start_time
        print(f"✅ Training complete in {elapsed:.1f} seconds")

        # Get best formula
        best = model.get_best()
        print(f"\n📊 Best Formula: {best['equation']}")

        # Evaluate
        y_train_pred = model.predict(X_train)
        y_train_pred_int = np.round(y_train_pred).astype(int) % 256
        train_acc = np.mean(y_train_pred_int == y_train)

        test_acc = 0.0
        if len(test_regime) > 0:
            X_test = test_regime[['k', 'drift_prev', 'A']].values
            y_test = test_regime['drift'].values
            y_test_pred = model.predict(X_test)
            y_test_pred_int = np.round(y_test_pred).astype(int) % 256
            test_acc = np.mean(y_test_pred_int == y_test)

        print(f"   Train: {train_acc*100:.1f}% | Test: {test_acc*100:.1f}%")

        return {
            'formula': str(best['equation']),
            'train_acc': float(train_acc),
            'test_acc': float(test_acc),
            'train_samples': int(len(train_regime)),
            'test_samples': int(len(test_regime)),
            'training_time_sec': float(elapsed)
        }

    except Exception as e:
        print(f"❌ Training failed: {e}")
        return None


def main():
    print("="*60)
    print("TASK 5: PROOF OF CONCEPT - LANE 0 ONLY")
    print("="*60)

    # Load data
    train = pd.read_csv('train.csv')
    val = pd.read_csv('val.csv')
    test = pd.read_csv('test.csv')

    # Filter for Lane 0 only
    lane = 0
    train_lane = train[train['lane'] == lane].copy()
    val_lane = val[val['lane'] == lane].copy()
    test_lane = test[test['lane'] == lane].copy()

    print(f"\n📊 Lane {lane} Dataset:")
    print(f"   Train: {len(train_lane)} samples")
    print(f"   Val: {len(val_lane)} samples")
    print(f"   Test: {len(test_lane)} samples")

    # Define regimes
    regimes = {
        'stable': lambda k: k < 32,
        'moderate': lambda k: (k >= 32) & (k < 64),
        'complex': lambda k: k >= 64
    }

    # Train each regime
    results = {}
    for regime_name, regime_filter in regimes.items():
        result = train_regime_model(train_lane, val_lane, test_lane, regime_name, regime_filter)
        if result:
            results[regime_name] = result

    # Calculate overall
    if results:
        total_samples = sum(r['test_samples'] for r in results.values())
        if total_samples > 0:
            weighted_acc = sum(
                r['test_acc'] * r['test_samples'] for r in results.values()
            ) / total_samples
            results['overall_accuracy'] = float(weighted_acc)

            print(f"\n{'='*60}")
            print(f"Lane {lane} Overall: {weighted_acc*100:.2f}%")
            print(f"{'='*60}")

    # Save
    output = {
        'task': 'task5_proof_of_concept',
        'lane': lane,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'results': results
    }

    with open('results/task5_poc.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Results saved to results/task5_poc.json")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY - Lane 0")
    print(f"{'='*60}")
    for regime in ['stable', 'moderate', 'complex']:
        if regime in results:
            print(f"{regime:>10}: {results[regime]['test_acc']*100:>5.1f}% | {results[regime]['formula']}")
    if 'overall_accuracy' in results:
        print(f"{'Overall':>10}: {results['overall_accuracy']*100:>5.1f}%")


if __name__ == '__main__':
    main()
