#!/usr/bin/env python3
"""
Per-Lane PySR Training for Drift Evolution Discovery

Based on 14H orchestration results showing:
- Lane 8: 92.6% (affine: drift_next = drift)
- Lane 7: 82.4% (affine: drift_next = 23*drift)
- Lane 6: 70.6% (affine: drift_next = 5*drift)

Strategy: Train individual PySR model for each lane with recursive features
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import PySR
try:
    from pysr import PySRRegressor
except ImportError:
    print("ERROR: PySR not installed!")
    sys.exit(1)

# Constants
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

def extract_lane_data(data, lane_id):
    """Extract drift sequence for a specific lane"""
    features_list = []
    targets_list = []

    for trans in data['transitions']:
        k = trans['from_puzzle']
        activation_k = lane_id * 8 if lane_id > 0 else 1

        # Only evolution phase (k > activation)
        if k > activation_k:
            drift = trans['drifts'][lane_id]

            # Get previous drift values (for recursive patterns)
            prev_drift = None
            prev_prev_drift = None

            # Find previous transition
            for prev_trans in data['transitions']:
                if prev_trans['from_puzzle'] == k - 1:
                    prev_drift = prev_trans['drifts'][lane_id]
                    break

            # Find k-2 transition
            for prev_trans in data['transitions']:
                if prev_trans['from_puzzle'] == k - 2:
                    prev_prev_drift = prev_trans['drifts'][lane_id]
                    break

            features_list.append({
                'k': k,
                'steps_since_activation': k - activation_k,
                'exponent': EXPONENTS[lane_id],
                'prev_drift': prev_drift if prev_drift is not None else 0,
                'prev_prev_drift': prev_prev_drift if prev_prev_drift is not None else 0,
            })
            targets_list.append(drift)

    return pd.DataFrame(features_list), np.array(targets_list)

def train_lane(lane_id, data, output_dir, niterations=200):
    """Train PySR model for a specific lane"""

    print(f"\n{'='*60}")
    print(f"TRAINING LANE {lane_id}")
    print(f"{'='*60}\n")

    # Extract lane data
    df, y = extract_lane_data(data, lane_id)

    if len(y) == 0:
        print(f"⚠️  Lane {lane_id}: No evolution data (always 0)")
        return None

    print(f"✓ Extracted {len(y)} samples for Lane {lane_id}")
    print(f"  Drift range: [{y.min()}, {y.max()}]")
    print(f"  Drift mean: {y.mean():.1f}")
    print(f"  Unique values: {len(np.unique(y))}")

    # Train/val split
    TRAIN_CUTOFF = 55
    train_mask = df['k'] <= TRAIN_CUTOFF
    val_mask = df['k'] > TRAIN_CUTOFF

    X = df.values
    X_train, X_val = X[train_mask], X[val_mask]
    y_train, y_val = y[train_mask], y[val_mask]

    print(f"\n  Training: puzzles 1-{TRAIN_CUTOFF} → {len(y_train)} samples")
    print(f"  Validation: puzzles {TRAIN_CUTOFF+1}-69 → {len(y_val)} samples")

    # Configure PySR with recursive operators
    print(f"\n  Configuring PySR...")

    model = PySRRegressor(
        # Model selection
        model_selection="best",

        # Operators (include prev_drift for recursive patterns)
        binary_operators=["+", "-", "*", "/", "mod"],
        unary_operators=["square", "cube", "abs"],

        # Complexity
        maxsize=15,  # Smaller than unified (simpler per-lane patterns)
        maxdepth=6,

        # Search parameters
        niterations=niterations,
        populations=15,
        population_size=33,

        # Optimization
        ncyclesperiteration=500,
        fraction_replaced_hof=0.035,

        # Batching
        batching=True,
        batch_size=50,

        # Progress
        progress=True,
        verbosity=1,

        # Random seed
        random_state=42 + lane_id,  # Different seed per lane

        # Output
        temp_equation_file=True,
    )

    print(f"  Max size: {model.maxsize}")
    print(f"  Iterations: {model.niterations}")

    # Train
    print(f"\n  Training PySR for Lane {lane_id}...")
    print(f"  Estimated time: 1-2 hours")

    try:
        model.fit(X_train, y_train)
        print(f"\n✅ Training complete for Lane {lane_id}!")
    except KeyboardInterrupt:
        print(f"\n⚠️  Training interrupted for Lane {lane_id}")
    except Exception as e:
        print(f"\n❌ Training failed for Lane {lane_id}: {e}")
        return None

    # Evaluate
    print(f"\n  Evaluating on validation set...")
    y_val_pred = model.predict(X_val)

    # Metrics
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    mae = mean_absolute_error(y_val, y_val_pred)
    mse = mean_squared_error(y_val, y_val_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_val, y_val_pred)

    # Exact match accuracy
    exact_matches = (np.round(y_val_pred) == y_val).sum()
    accuracy = exact_matches / len(y_val)

    print(f"\n  {'='*60}")
    print(f"  LANE {lane_id} RESULTS")
    print(f"  {'='*60}")
    print(f"  MAE: {mae:.2f}")
    print(f"  RMSE: {rmse:.2f}")
    print(f"  R²: {r2:.4f}")
    print(f"  Exact matches: {exact_matches}/{len(y_val)} = {100*accuracy:.1f}%")
    print(f"  {'='*60}\n")

    # Save model
    lane_output_dir = output_dir / f"lane_{lane_id:02d}"
    lane_output_dir.mkdir(exist_ok=True)

    model_file = lane_output_dir / "model.pkl"
    equations_file = lane_output_dir / "equations.csv"
    results_file = lane_output_dir / "results.json"

    # Save model
    import pickle
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    print(f"  ✓ Model saved: {model_file}")

    # Save equations
    try:
        equations_df = model.equations_
        equations_df.to_csv(equations_file, index=False)
        print(f"  ✓ Equations saved: {equations_file}")
    except Exception as e:
        print(f"  ⚠️  Could not save equations: {e}")

    # Save results
    results = {
        'lane': lane_id,
        'samples': {
            'train': len(y_train),
            'val': len(y_val)
        },
        'metrics': {
            'accuracy': float(accuracy),
            'exact_matches': int(exact_matches),
            'total': len(y_val),
            'mae': float(mae),
            'rmse': float(rmse),
            'r2': float(r2)
        },
        'best_equation': str(model),
        'status': 'SUCCESS' if accuracy >= 0.99 else 'PARTIAL' if accuracy >= 0.80 else 'FAILED'
    }

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ Results saved: {results_file}\n")

    return results

def main():
    parser = argparse.ArgumentParser(description='Train per-lane PySR models')
    parser.add_argument('--lane', type=int, help='Train specific lane (0-15)')
    parser.add_argument('--lanes', type=str, help='Train multiple lanes (comma-separated, e.g., "8,7,6")')
    parser.add_argument('--iterations', type=int, default=200, help='PySR iterations (default: 200)')
    args = parser.parse_args()

    # Load data
    DATA_FILE = project_root / "drift_data_CORRECT_BYTE_ORDER.json"
    print(f"Loading data from: {DATA_FILE}")

    with open(DATA_FILE) as f:
        data = json.load(f)

    print(f"✓ Loaded {len(data['transitions'])} transitions")

    # Determine which lanes to train
    if args.lane is not None:
        lanes_to_train = [args.lane]
    elif args.lanes:
        lanes_to_train = [int(x.strip()) for x in args.lanes.split(',')]
    else:
        # Default priority order (based on H4 results)
        lanes_to_train = [8, 7, 6, 5, 4, 3, 2, 1, 0]

    print(f"\nTraining lanes: {lanes_to_train}")
    print(f"Iterations per lane: {args.iterations}")

    # Output directory
    output_dir = Path(__file__).parent / "results_per_lane"
    output_dir.mkdir(exist_ok=True)

    # Train each lane
    all_results = []

    for lane_id in lanes_to_train:
        result = train_lane(lane_id, data, output_dir, niterations=args.iterations)
        if result:
            all_results.append(result)

            # Check if we found 100% solution
            if result['metrics']['accuracy'] >= 0.999:
                print(f"\n🎉 100% SOLUTION FOUND FOR LANE {lane_id}!")
                print(f"   Equation: {result['best_equation']}")

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: Trained {len(all_results)} lanes")
    print(f"{'='*60}\n")

    for result in all_results:
        status_icon = "✅" if result['status'] == 'SUCCESS' else "⚠️" if result['status'] == 'PARTIAL' else "❌"
        print(f"{status_icon} Lane {result['lane']}: {result['metrics']['accuracy']*100:.1f}% "
              f"({result['metrics']['exact_matches']}/{result['metrics']['total']}) - {result['status']}")

    # Save summary
    summary_file = output_dir / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n✓ Summary saved: {summary_file}")

    print(f"\n✅ Per-lane training complete!")

if __name__ == "__main__":
    main()
