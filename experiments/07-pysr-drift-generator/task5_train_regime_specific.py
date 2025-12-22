#!/usr/bin/env python3
"""
Task 5: Regime-Specific PySR for Lanes 0-6

Train separate PySR models for different k regimes:
- Stable (k<32): 6-25% transition rate
- Moderate (k=32-63): 25-48% transition rate
- Complex (k>=64): 52%+ transition rate

Hypothesis: Mixing regimes dilutes signal. Separating them should improve accuracy.
"""

import pandas as pd
import numpy as np
from pysr import PySRRegressor
import json
import time

def train_regime_model(train_data, val_data, test_data, lane, regime_name, regime_filter):
    """Train PySR model for specific lane and regime."""
    print(f"\n{'='*60}")
    print(f"Lane {lane} - {regime_name} Regime")
    print(f"{'='*60}")

    # Filter by regime
    train_regime = train_data[regime_filter(train_data['k'])].copy()
    val_regime = val_data[regime_filter(val_data['k'])].copy()
    test_regime = test_data[regime_filter(test_data['k'])].copy()

    print(f"Training samples: {len(train_regime)}")
    print(f"Validation samples: {len(val_regime)}")
    print(f"Test samples: {len(test_regime)}")

    if len(train_regime) < 5:
        print(f"❌ Not enough training samples ({len(train_regime)}), skipping")
        return None

    # Prepare features
    X_train = train_regime[['k', 'drift_prev', 'A']].values
    y_train = train_regime['drift'].values

    # Train PySR
    print(f"\n🚀 Training PySR model...")
    start_time = time.time()

    model = PySRRegressor(
        niterations=100,
        binary_operators=["+", "*", "-"],
        unary_operators=["square", "cube"],
        constraints={'square': 5, 'cube': 5},
        complexity_of_constants=2,
        populations=30,
        population_size=100,
        ncycles_per_iteration=550,
        maxsize=15,
        timeout_in_seconds=1800,  # 30 minutes per regime
        random_state=42,
        verbosity=0
    )

    try:
        model.fit(X_train, y_train)
        elapsed = time.time() - start_time
        print(f"✅ Training complete in {elapsed/60:.1f} minutes")

        # Get best formula
        best = model.get_best()
        print(f"\n📊 Best Formula:")
        print(f"   Equation: {best['equation']}")
        print(f"   Complexity: {best['complexity']}")
        print(f"   Loss: {best['loss']:.6f}")

        # Evaluate on train
        y_train_pred = model.predict(X_train)
        y_train_pred_int = np.round(y_train_pred).astype(int) % 256
        train_acc = np.mean(y_train_pred_int == y_train)
        print(f"\n   Train Accuracy: {train_acc*100:.2f}%")

        # Evaluate on val
        if len(val_regime) > 0:
            X_val = val_regime[['k', 'drift_prev', 'A']].values
            y_val = val_regime['drift'].values
            y_val_pred = model.predict(X_val)
            y_val_pred_int = np.round(y_val_pred).astype(int) % 256
            val_acc = np.mean(y_val_pred_int == y_val)
            print(f"   Val Accuracy: {val_acc*100:.2f}%")
        else:
            val_acc = 0.0

        # Evaluate on test
        if len(test_regime) > 0:
            X_test = test_regime[['k', 'drift_prev', 'A']].values
            y_test = test_regime['drift'].values
            y_test_pred = model.predict(X_test)
            y_test_pred_int = np.round(y_test_pred).astype(int) % 256
            test_acc = np.mean(y_test_pred_int == y_test)
            print(f"   Test Accuracy: {test_acc*100:.2f}%")
        else:
            test_acc = 0.0

        return {
            'formula': str(best['equation']),
            'complexity': int(best['complexity']),
            'loss': float(best['loss']),
            'train_acc': float(train_acc),
            'val_acc': float(val_acc),
            'test_acc': float(test_acc),
            'train_samples': int(len(train_regime)),
            'val_samples': int(len(val_regime)),
            'test_samples': int(len(test_regime)),
            'training_time_sec': float(elapsed)
        }

    except Exception as e:
        print(f"❌ Training failed: {e}")
        return None


def main():
    print("="*60)
    print("TASK 5: REGIME-SPECIFIC PYSR FOR LANES 0-6")
    print("="*60)

    # Load data
    train = pd.read_csv('train.csv')
    val = pd.read_csv('val.csv')
    test = pd.read_csv('test.csv')

    print(f"\n📊 Dataset sizes:")
    print(f"   Train: {len(train)} samples (k={train['k'].min()}-{train['k'].max()})")
    print(f"   Val: {len(val)} samples (k={val['k'].min()}-{val['k'].max()})")
    print(f"   Test: {len(test)} samples (k={test['k'].min()}-{test['k'].max()})")

    # Define regimes
    regimes = {
        'stable': lambda k: k < 32,
        'moderate': lambda k: (k >= 32) & (k < 64),
        'complex': lambda k: k >= 64
    }

    # Train models for lanes 0-6
    results = {}

    for lane in range(7):  # Lanes 0-6
        print(f"\n\n{'#'*60}")
        print(f"# LANE {lane}")
        print(f"{'#'*60}")

        # Filter data for this lane
        train_lane = train[train['lane'] == lane].copy()
        val_lane = val[val['lane'] == lane].copy()
        test_lane = test[test['lane'] == lane].copy()

        lane_results = {}

        # Train model for each regime
        for regime_name, regime_filter in regimes.items():
            result = train_regime_model(
                train_lane, val_lane, test_lane,
                lane, regime_name, regime_filter
            )

            if result:
                lane_results[regime_name] = result

        # Calculate weighted overall accuracy
        if lane_results:
            total_samples = sum(r['test_samples'] for r in lane_results.values())
            if total_samples > 0:
                weighted_acc = sum(
                    r['test_acc'] * r['test_samples']
                    for r in lane_results.values()
                ) / total_samples

                print(f"\n{'='*60}")
                print(f"Lane {lane} Overall Weighted Accuracy: {weighted_acc*100:.2f}%")
                print(f"{'='*60}")

                lane_results['overall_accuracy'] = float(weighted_acc)

            results[f'lane_{lane}'] = lane_results

    # Save results
    output = {
        'task': 'task5_regime_specific',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'regimes': {
            'stable': 'k < 32',
            'moderate': '32 <= k < 64',
            'complex': 'k >= 64'
        },
        'results': results
    }

    with open('results/task5_regime_specific.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for lane in range(7):
        key = f'lane_{lane}'
        if key in results:
            overall = results[key].get('overall_accuracy', 0)
            print(f"Lane {lane}: {overall*100:.2f}% overall accuracy")
            for regime in ['stable', 'moderate', 'complex']:
                if regime in results[key]:
                    acc = results[key][regime]['test_acc']
                    print(f"  - {regime}: {acc*100:.2f}%")
        else:
            print(f"Lane {lane}: No results")

    print(f"\n✅ Results saved to results/task5_regime_specific.json")


if __name__ == '__main__':
    main()
