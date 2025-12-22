#!/usr/bin/env python3
"""
Task 5: Regime-Specific Analysis

Analyze whether regime separation helps with drift prediction.
Compare single-model vs regime-specific approaches empirically.
"""

import pandas as pd
import numpy as np
import json

def analyze_regime_statistics(df, lane, regime_name, regime_filter):
    """Calculate statistics for a specific regime."""
    regime_data = df[regime_filter(df['k'])]

    if len(regime_data) == 0:
        return None

    drift_values = regime_data['drift'].values

    # Calculate statistics
    stats = {
        'count': int(len(drift_values)),
        'unique_count': int(len(np.unique(drift_values))),
        'mean': float(np.mean(drift_values)),
        'std': float(np.std(drift_values)),
        'min': int(np.min(drift_values)),
        'max': int(np.max(drift_values)),
        'median': float(np.median(drift_values)),
        'zero_ratio': float(np.mean(drift_values == 0)),
        'transition_rate': float(np.mean(drift_values != regime_data['drift_prev'].values))
    }

    return stats


def simple_baseline(train_data, test_data):
    """
    Simple baseline: predict most common drift value from training data.
    """
    most_common = train_data['drift'].mode()[0] if len(train_data) > 0 else 0

    predictions = np.full(len(test_data), most_common)
    actual = test_data['drift'].values

    accuracy = np.mean(predictions == actual)
    return accuracy, most_common


def regime_aware_baseline(train_data, test_data, regimes):
    """
    Regime-aware baseline: predict most common value per regime.
    """
    # Learn most common value per regime
    regime_values = {}
    for regime_name, regime_filter in regimes.items():
        train_regime = train_data[regime_filter(train_data['k'])]
        if len(train_regime) > 0:
            regime_values[regime_name] = train_regime['drift'].mode()[0]
        else:
            regime_values[regime_name] = 0

    # Predict on test data
    predictions = []
    for _, row in test_data.iterrows():
        k = row['k']
        for regime_name, regime_filter in regimes.items():
            if regime_filter(k):
                predictions.append(regime_values[regime_name])
                break

    predictions = np.array(predictions)
    actual = test_data['drift'].values

    accuracy = np.mean(predictions == actual)
    return accuracy, regime_values


def main():
    print("="*60)
    print("TASK 5: REGIME-SPECIFIC ANALYSIS")
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

    # Analyze each lane
    results = {}

    for lane in range(7):  # Lanes 0-6
        print(f"\n\n{'#'*60}")
        print(f"# LANE {lane}")
        print(f"{'#'*60}")

        # Filter data for this lane
        train_lane = train.loc[train['lane'] == lane].copy()
        val_lane = val.loc[val['lane'] == lane].copy()
        test_lane = test.loc[test['lane'] == lane].copy()

        # Overall statistics
        print(f"\n📊 Overall Statistics:")
        print(f"   Train samples: {len(train_lane)}")
        print(f"   Test samples: {len(test_lane)}")
        print(f"   Unique drift values: {len(np.unique(train_lane['drift']))}")
        print(f"   Zero ratio: {np.mean(train_lane['drift'] == 0)*100:.1f}%")

        # Regime-specific statistics
        lane_stats = {}
        print(f"\n📊 Regime Statistics:")
        print(f"{'Regime':>10} | {'Train':<6} | {'Test':<5} | {'Unique':<6} | {'Mean':<6} | {'Std':<6} | {'Trans%':<7}")
        print("-" * 70)

        for regime_name, regime_filter in regimes.items():
            train_stats = analyze_regime_statistics(train_lane, lane, regime_name, regime_filter)
            test_stats = analyze_regime_statistics(test_lane, lane, regime_name, regime_filter)

            if train_stats:
                print(f"{regime_name:>10} | {train_stats['count']:<6} | {test_stats['count'] if test_stats else 0:<5} | "
                      f"{train_stats['unique_count']:<6} | {train_stats['mean']:<6.1f} | {train_stats['std']:<6.1f} | "
                      f"{train_stats['transition_rate']*100:<7.1f}")

                lane_stats[regime_name] = {
                    'train': train_stats,
                    'test': test_stats
                }

        # Baseline comparisons
        print(f"\n🔍 Baseline Comparisons:")

        # Simple baseline (global most common)
        simple_acc, simple_val = simple_baseline(train_lane, test_lane)
        print(f"   Simple (most common): {simple_acc*100:.2f}% (predicts {simple_val})")

        # Regime-aware baseline
        regime_acc, regime_vals = regime_aware_baseline(train_lane, test_lane, regimes)
        print(f"   Regime-aware: {regime_acc*100:.2f}%")
        for regime_name, regime_val in regime_vals.items():
            print(f"      - {regime_name}: {regime_val}")

        # Improvement
        improvement = regime_acc - simple_acc
        print(f"   Improvement: {improvement*100:+.2f}%")

        results[f'lane_{lane}'] = {
            'regime_stats': lane_stats,
            'simple_baseline': float(simple_acc),
            'regime_baseline': float(regime_acc),
            'improvement': float(improvement),
            'regime_values': {k: int(v) for k, v in regime_vals.items()}
        }

    # Save results
    output = {
        'task': 'task5_regime_analysis',
        'timestamp': pd.Timestamp.now().isoformat(),
        'regimes': {
            'stable': 'k < 32',
            'moderate': '32 <= k < 64',
            'complex': 'k >= 64'
        },
        'results': results
    }

    with open('results/task5_regime_specific.json', 'w') as f:
        json.dump(output, f, indent=2)

    # Final summary
    print(f"\n\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"\n{'Lane':<6} | {'Simple':<8} | {'Regime':<8} | {'Improvement':<12} | {'Verdict'}")
    print("-" * 60)

    helps_count = 0
    for lane in range(7):
        r = results[f'lane_{lane}']
        simple = r['simple_baseline'] * 100
        regime = r['regime_baseline'] * 100
        improvement = r['improvement'] * 100

        verdict = "✅ HELPS" if improvement > 0 else "❌ NO HELP"
        if improvement > 0:
            helps_count += 1

        print(f"{lane:<6} | {simple:>6.2f}% | {regime:>6.2f}% | {improvement:>+10.2f}% | {verdict}")

    print(f"\n{'='*60}")
    print(f"Regime-specific approach helps: {helps_count}/7 lanes")
    print(f"Conclusion: {'REGIME-SPECIFIC HELPS' if helps_count >= 4 else 'NO SIGNIFICANT IMPROVEMENT'}")
    print(f"{'='*60}")

    print(f"\n✅ Results saved to results/task5_regime_specific.json")


if __name__ == '__main__':
    main()
