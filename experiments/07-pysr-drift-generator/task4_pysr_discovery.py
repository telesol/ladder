#!/usr/bin/env python3
"""
Task 4: PySR Symbolic Regression for Index-Based Patterns

Use PySR to discover complex formulas for lanes 0-6
drift[k][lane] = f(k, lane)
"""

import json
import numpy as np
from pathlib import Path

def load_drift_data():
    """Load drift data from JSON file."""
    drift_file = Path("/home/solo/LadderV3/kh-assist/drift_data_export.json")
    with open(drift_file) as f:
        data = json.load(f)

    transitions = data["transitions"]
    k_values = np.array([t["from_puzzle"] for t in transitions])

    drift_by_lane = []
    for lane in range(16):
        lane_drifts = np.array([t["drifts"][lane] for t in transitions])
        drift_by_lane.append(lane_drifts)

    return k_values, drift_by_lane

def run_pysr_for_lane(lane, k_values, drift_values):
    """Run PySR for a single lane."""
    try:
        from pysr import PySRRegressor
    except ImportError:
        print("ERROR: PySR not installed. Install with: pip install pysr")
        return None

    print(f"\n--- Training PySR for Lane {lane} ---")

    # Split data
    split_idx = int(len(k_values) * 0.8)
    k_train = k_values[:split_idx].reshape(-1, 1)
    k_test = k_values[split_idx:].reshape(-1, 1)
    y_train = drift_values[:split_idx]
    y_test = drift_values[split_idx:]

    # Configure PySR
    model = PySRRegressor(
        niterations=50,  # Moderate iterations for quick results
        binary_operators=["+", "*", "-", "%"],
        unary_operators=["square", "cube", "abs"],
        model_selection="best",
        loss="L2DistLoss()",
        populations=8,
        population_size=30,
        maxsize=15,
        verbosity=0,
        progress=True,
        temp_equation_file=True,
        delete_tempfiles=True,
        parsimony=0.01,
        adaptive_parsimony_scaling=100.0,
        ncycles_per_iteration=300,
    )

    print(f"Training on {len(k_train)} samples...")
    model.fit(k_train, y_train)

    # Get best equation
    print(f"\nBest equation: {model.sympy()}")

    # Predict and evaluate
    pred_train_raw = model.predict(k_train)
    pred_test_raw = model.predict(k_test)

    # Apply mod 256
    pred_train = np.round(pred_train_raw) % 256
    pred_test = np.round(pred_test_raw) % 256

    train_acc = np.mean(pred_train == y_train)
    test_acc = np.mean(pred_test == y_test)

    print(f"Train accuracy: {train_acc*100:.1f}%")
    print(f"Test accuracy: {test_acc*100:.1f}%")

    # Get equation complexity
    complexity = model.get_best()[0] if hasattr(model, 'get_best') else 0

    result = {
        "lane": lane,
        "equation": str(model.sympy()),
        "train_accuracy": float(train_acc),
        "test_accuracy": float(test_acc),
        "complexity": int(complexity) if complexity else 0,
        "predictions_test": pred_test.tolist()
    }

    return result

def main():
    """Run PySR discovery for lanes 0-6."""
    print("Task 4 PySR: Symbolic Regression for Index-Based Patterns")
    print("=" * 60)

    # Load data
    k_values, drift_by_lane = load_drift_data()
    print(f"Loaded {len(k_values)} transitions")

    # Run PySR for each lane (focus on high-correlation lanes first)
    results = {}
    priority_lanes = [2, 3, 4, 5, 6, 0, 1]  # Sorted by correlation

    for lane in priority_lanes:
        if lane >= 7:
            break

        print(f"\n{'='*60}")
        print(f"Processing Lane {lane}")
        print(f"{'='*60}")

        result = run_pysr_for_lane(lane, k_values, drift_by_lane[lane])

        if result:
            results[f"lane_{lane}"] = result

            # Early stopping if we find 80%+ accuracy
            if result["test_accuracy"] >= 0.80:
                print(f"\n🎉 Found 80%+ formula for lane {lane}!")
                print(f"Formula: {result['equation']}")
                print(f"Accuracy: {result['test_accuracy']*100:.1f}%")

    # Summary
    print("\n" + "=" * 60)
    print("PySR RESULTS SUMMARY")
    print("=" * 60)

    for lane_key in sorted(results.keys()):
        r = results[lane_key]
        print(f"Lane {r['lane']}: {r['test_accuracy']*100:5.1f}% - {r['equation']}")

    # Save results
    output_file = Path("/home/solo/LadderV3/kh-assist/experiments/07-pysr-drift-generator/results/task4_pysr_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")

    # Best result
    if results:
        best = max(results.items(), key=lambda x: x[1]["test_accuracy"])
        print(f"\nBest: {best[0]} at {best[1]['test_accuracy']*100:.1f}%")
        print(f"Equation: {best[1]['equation']}")

        if best[1]["test_accuracy"] >= 0.80:
            print("\n✅ SUCCESS: Found ≥80% formula!")
        else:
            print(f"\n⚠ PARTIAL: Best {best[1]['test_accuracy']*100:.1f}% (target: ≥80%)")

    return results

if __name__ == "__main__":
    import sys
    try:
        results = main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
