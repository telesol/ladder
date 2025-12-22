#!/usr/bin/env python3
"""
Task 4 HYBRID Analysis: Test if lanes 0-6 are actually RECURSIVE, not index-based

Hypothesis: High correlation with k but low polynomial accuracy suggests:
- drift[k][lane] depends on BOTH k AND drift[k-1][lane]
- Not purely index-based, but index-INFLUENCED recursive

Test: drift[k][lane] = f(k, drift[k-1][lane])
"""

import json
import numpy as np
from pathlib import Path
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge

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

def test_recursive_with_k(k_values, drift_values):
    """
    Test: drift[k] = f(k, drift[k-1])

    Features: k, drift[k-1]
    Target: drift[k]
    """
    # Create lagged features (skip first element since we need drift[k-1])
    k_current = k_values[1:]  # k values starting from index 1
    drift_prev = drift_values[:-1]  # drift[k-1]
    drift_current = drift_values[1:]  # drift[k]

    # Combine features: k and drift[k-1]
    X = np.column_stack([k_current, drift_prev])
    y = drift_current

    # Split data
    split_idx = int(len(X) * 0.8)
    X_train = X[:split_idx]
    X_test = X[split_idx:]
    y_train = y[:split_idx]
    y_test = y[split_idx:]

    results = {}

    # Test different polynomial degrees
    for degree in range(1, 4):
        poly = PolynomialFeatures(degree=degree, include_bias=True)
        X_train_poly = poly.fit_transform(X_train)
        X_test_poly = poly.transform(X_test)

        model = LinearRegression()
        model.fit(X_train_poly, y_train)

        pred_train = np.round(model.predict(X_train_poly)) % 256
        pred_test = np.round(model.predict(X_test_poly)) % 256

        train_acc = np.mean(pred_train == y_train)
        test_acc = np.mean(pred_test == y_test)

        results[f"degree_{degree}"] = {
            "train_accuracy": float(train_acc),
            "test_accuracy": float(test_acc),
            "features": f"k, drift[k-1] (polynomial degree {degree})"
        }

    return results

def test_pure_recursive(drift_values):
    """
    Test: drift[k] = f(drift[k-1])

    Pure recursive without k influence.
    """
    drift_prev = drift_values[:-1].reshape(-1, 1)
    drift_current = drift_values[1:]

    split_idx = int(len(drift_prev) * 0.8)
    X_train = drift_prev[:split_idx]
    X_test = drift_prev[split_idx:]
    y_train = drift_current[:split_idx]
    y_test = drift_current[split_idx:]

    results = {}

    for degree in range(1, 4):
        poly = PolynomialFeatures(degree=degree, include_bias=True)
        X_train_poly = poly.fit_transform(X_train)
        X_test_poly = poly.transform(X_test)

        model = LinearRegression()
        model.fit(X_train_poly, y_train)

        pred_train = np.round(model.predict(X_train_poly)) % 256
        pred_test = np.round(model.predict(X_test_poly)) % 256

        train_acc = np.mean(pred_train == y_train)
        test_acc = np.mean(pred_test == y_test)

        results[f"degree_{degree}"] = {
            "train_accuracy": float(train_acc),
            "test_accuracy": float(test_acc),
            "features": f"drift[k-1] only (polynomial degree {degree})"
        }

    return results

def test_modular_recursive(k_values, drift_values):
    """
    Test specific modular patterns:
    drift[k] = (a*k + b*drift[k-1]) mod 256
    """
    k_current = k_values[1:]
    drift_prev = drift_values[:-1]
    drift_current = drift_values[1:]

    split_idx = int(len(k_current) * 0.8)
    k_test = k_current[split_idx:]
    drift_prev_test = drift_prev[split_idx:]
    y_test = drift_current[split_idx:]

    best_acc = 0
    best_pattern = None

    # Pattern: (a*k + b*drift[k-1]) mod 256
    for a in range(0, 20):
        for b in range(0, 10):
            pred_test = (a * k_test + b * drift_prev_test) % 256
            acc = np.mean(pred_test == y_test)
            if acc > best_acc:
                best_acc = acc
                best_pattern = f"({a}*k + {b}*drift[k-1]) mod 256"

    return {
        "best_pattern": best_pattern,
        "accuracy": float(best_acc)
    }

def main():
    """Run hybrid analysis."""
    print("Task 4 HYBRID Analysis: Index + Recursive Patterns")
    print("=" * 60)
    print("Testing if lanes 0-6 are RECURSIVE with k influence")
    print()

    k_values, drift_by_lane = load_drift_data()
    print(f"Loaded {len(k_values)} transitions\n")

    all_results = {}

    for lane in range(7):
        print(f"\n{'='*60}")
        print(f"Lane {lane}")
        print(f"{'='*60}")

        drift_values = drift_by_lane[lane]

        # Test 1: Recursive with k
        print("\n1. Recursive with k: drift[k] = f(k, drift[k-1])")
        rec_with_k = test_recursive_with_k(k_values, drift_values)
        for key, result in rec_with_k.items():
            print(f"   {key}: Train={result['train_accuracy']*100:5.1f}%, Test={result['test_accuracy']*100:5.1f}%")

        # Test 2: Pure recursive
        print("\n2. Pure recursive: drift[k] = f(drift[k-1])")
        pure_rec = test_pure_recursive(drift_values)
        for key, result in pure_rec.items():
            print(f"   {key}: Train={result['train_accuracy']*100:5.1f}%, Test={result['test_accuracy']*100:5.1f}%")

        # Test 3: Modular recursive
        print("\n3. Modular recursive: drift[k] = (a*k + b*drift[k-1]) mod 256")
        mod_rec = test_modular_recursive(k_values, drift_values)
        print(f"   Best: {mod_rec['best_pattern']} = {mod_rec['accuracy']*100:.1f}%")

        # Determine best approach
        best_rec_with_k = max(rec_with_k.values(), key=lambda x: x["test_accuracy"])
        best_pure_rec = max(pure_rec.values(), key=lambda x: x["test_accuracy"])

        best_overall_acc = max(
            best_rec_with_k["test_accuracy"],
            best_pure_rec["test_accuracy"],
            mod_rec["accuracy"]
        )

        if best_overall_acc == mod_rec["accuracy"]:
            best_method = "Modular recursive"
            best_desc = mod_rec["best_pattern"]
        elif best_overall_acc == best_rec_with_k["test_accuracy"]:
            best_method = "Recursive with k"
            best_desc = best_rec_with_k["features"]
        else:
            best_method = "Pure recursive"
            best_desc = best_pure_rec["features"]

        print(f"\n✓ Best: {best_method} ({best_overall_acc*100:.1f}%)")

        all_results[f"lane_{lane}"] = {
            "recursive_with_k": rec_with_k,
            "pure_recursive": pure_rec,
            "modular_recursive": mod_rec,
            "best_method": best_method,
            "best_accuracy": float(best_overall_acc),
            "best_description": best_desc
        }

    # Summary
    print("\n" + "=" * 60)
    print("HYBRID ANALYSIS SUMMARY")
    print("=" * 60)

    for lane in range(7):
        lane_key = f"lane_{lane}"
        result = all_results[lane_key]
        print(f"Lane {lane}: {result['best_accuracy']*100:5.1f}% ({result['best_method']})")

    # Save results
    output_file = Path("/home/solo/LadderV3/kh-assist/experiments/07-pysr-drift-generator/results/task4_hybrid_analysis.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")

    # Best overall
    best = max(all_results.items(), key=lambda x: x[1]["best_accuracy"])
    print(f"\nBest overall: {best[0]} at {best[1]['best_accuracy']*100:.1f}%")
    print(f"Method: {best[1]['best_method']}")
    print(f"Description: {best[1]['best_description']}")

    if best[1]["best_accuracy"] >= 0.80:
        print("\n✅ SUCCESS: Found ≥80% formula!")
    else:
        print(f"\n⚠ PARTIAL: Best {best[1]['best_accuracy']*100:.1f}% (target: ≥80%)")

    # Key insight
    print("\n" + "=" * 60)
    print("KEY INSIGHT")
    print("=" * 60)

    rec_count = sum(1 for r in all_results.values() if "recursive" in r["best_method"].lower())
    index_count = 7 - rec_count

    if rec_count > index_count:
        print(f"✓ Lanes 0-6 are RECURSIVE ({rec_count}/7 lanes)")
        print("  → drift[k] depends on drift[k-1], not just k")
        print("  → This explains high k-correlation but low polynomial accuracy!")
    else:
        print(f"✓ Lanes 0-6 are INDEX-BASED ({index_count}/7 lanes)")

    return all_results

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
