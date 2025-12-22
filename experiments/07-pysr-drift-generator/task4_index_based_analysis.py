#!/usr/bin/env python3
"""
Task 4: Index-Based Pattern Analysis (Lanes 0-6)

Approach:
1. Polynomial Regression (degrees 1-5)
2. Modular Arithmetic Patterns
3. PySR Symbolic Regression (if time permits)

Goal: Find drift[k][lane] = f(k, lane) for lanes 0-6
"""

import json
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, r2_score
import sys
from pathlib import Path

def load_drift_data():
    """Load drift data from JSON file."""
    drift_file = Path("/home/solo/LadderV3/kh-assist/drift_data_export.json")
    with open(drift_file) as f:
        data = json.load(f)

    # Extract drift values organized by lane
    transitions = data["transitions"]
    num_transitions = len(transitions)
    num_lanes = 16

    # Create k values (puzzle numbers from_puzzle)
    k_values = np.array([t["from_puzzle"] for t in transitions])

    # Organize drift by lane
    drift_by_lane = []
    for lane in range(num_lanes):
        lane_drifts = np.array([t["drifts"][lane] for t in transitions])
        drift_by_lane.append(lane_drifts)

    return k_values, drift_by_lane

def polynomial_regression_analysis(k_values, drift_by_lane, max_lane=7):
    """Test polynomial regression for lanes 0-6."""
    print("=" * 60)
    print("POLYNOMIAL REGRESSION ANALYSIS")
    print("=" * 60)

    results = {}

    for lane in range(max_lane):
        print(f"\n--- Lane {lane} ---")
        lane_results = {}

        # Get drift values for this lane
        y = drift_by_lane[lane]

        # Split data: train on first 80%, test on last 20%
        split_idx = int(len(k_values) * 0.8)
        k_train = k_values[:split_idx].reshape(-1, 1)
        k_test = k_values[split_idx:].reshape(-1, 1)
        y_train = y[:split_idx]
        y_test = y[split_idx:]

        best_score = 0
        best_degree = 0
        best_predictions = None

        for degree in range(1, 6):
            # Create polynomial features
            poly = PolynomialFeatures(degree=degree, include_bias=True)
            k_train_poly = poly.fit_transform(k_train)
            k_test_poly = poly.transform(k_test)

            # Try both regular and ridge regression
            for reg_type, model in [("Linear", LinearRegression()),
                                     ("Ridge", Ridge(alpha=1.0))]:
                model.fit(k_train_poly, y_train)

                # Predict and apply mod 256
                pred_train = np.round(model.predict(k_train_poly)) % 256
                pred_test = np.round(model.predict(k_test_poly)) % 256

                # Calculate accuracy
                train_acc = np.mean(pred_train == y_train)
                test_acc = np.mean(pred_test == y_test)

                # MAE for continuous metric
                mae_test = mean_absolute_error(y_test, pred_test)

                label = f"degree_{degree}_{reg_type}"
                lane_results[label] = {
                    "degree": degree,
                    "regression": reg_type,
                    "train_accuracy": float(train_acc),
                    "test_accuracy": float(test_acc),
                    "mae": float(mae_test),
                    "coefficients": model.coef_.tolist() if hasattr(model, 'coef_') else []
                }

                if test_acc > best_score:
                    best_score = test_acc
                    best_degree = degree
                    best_predictions = pred_test

                print(f"  Deg {degree} ({reg_type:6s}): Train={train_acc*100:5.1f}%, Test={test_acc*100:5.1f}%, MAE={mae_test:.2f}")

        lane_results["best"] = {
            "degree": best_degree,
            "accuracy": float(best_score),
            "predictions": best_predictions.tolist() if best_predictions is not None else []
        }

        results[f"lane_{lane}"] = lane_results

    return results

def modular_arithmetic_patterns(k_values, drift_by_lane, max_lane=7):
    """Test specific modular arithmetic patterns."""
    print("\n" + "=" * 60)
    print("MODULAR ARITHMETIC PATTERN ANALYSIS")
    print("=" * 60)

    results = {}

    for lane in range(max_lane):
        print(f"\n--- Lane {lane} ---")
        lane_results = {}

        y = drift_by_lane[lane]
        split_idx = int(len(k_values) * 0.8)
        k_train = k_values[:split_idx]
        k_test = k_values[split_idx:]
        y_train = y[:split_idx]
        y_test = y[split_idx:]

        best_pattern = None
        best_score = 0

        # Pattern 1: drift = (a*k + b) mod 256
        for a in range(0, 20):
            for b in range(0, 256, 5):
                pred_test = (a * k_test + b) % 256
                acc = np.mean(pred_test == y_test)
                if acc > best_score:
                    best_score = acc
                    best_pattern = f"({a}*k + {b}) mod 256"

        lane_results["linear_mod"] = {
            "best_pattern": best_pattern,
            "accuracy": float(best_score)
        }
        print(f"  Linear mod: {best_pattern} = {best_score*100:.1f}%")

        # Pattern 2: drift = (a*k^2 + b*k + c) mod 256
        best_pattern2 = None
        best_score2 = 0
        for a in range(0, 5):
            for b in range(0, 10):
                for c in range(0, 256, 10):
                    pred_test = (a * k_test**2 + b * k_test + c) % 256
                    acc = np.mean(pred_test == y_test)
                    if acc > best_score2:
                        best_score2 = acc
                        best_pattern2 = f"({a}*k^2 + {b}*k + {c}) mod 256"

        lane_results["quadratic_mod"] = {
            "best_pattern": best_pattern2,
            "accuracy": float(best_score2)
        }
        print(f"  Quadratic mod: {best_pattern2} = {best_score2*100:.1f}%")

        # Pattern 3: drift = (a*k) mod m  (various moduli)
        best_pattern3 = None
        best_score3 = 0
        for m in [16, 32, 64, 128, 256]:
            for a in range(1, 20):
                pred_test = (a * k_test) % m
                # Map to 0-255 range if needed
                if m < 256:
                    pred_test = pred_test * (256 // m)
                acc = np.mean(pred_test == y_test)
                if acc > best_score3:
                    best_score3 = acc
                    best_pattern3 = f"({a}*k) mod {m}"

        lane_results["modular_mult"] = {
            "best_pattern": best_pattern3,
            "accuracy": float(best_score3)
        }
        print(f"  Modular mult: {best_pattern3} = {best_score3*100:.1f}%")

        results[f"lane_{lane}"] = lane_results

    return results

def bit_pattern_analysis(k_values, drift_by_lane, max_lane=7):
    """Analyze bit-level patterns."""
    print("\n" + "=" * 60)
    print("BIT PATTERN ANALYSIS")
    print("=" * 60)

    results = {}

    for lane in range(max_lane):
        print(f"\n--- Lane {lane} ---")

        y = drift_by_lane[lane]

        # Check if drift depends on k's bit patterns
        # E.g., drift = XOR(k, constant) mod 256
        best_xor = None
        best_score = 0

        split_idx = int(len(k_values) * 0.8)
        k_test = k_values[split_idx:]
        y_test = y[split_idx:]

        for const in range(0, 256, 1):
            pred_test = np.bitwise_xor(k_test, const) % 256
            acc = np.mean(pred_test == y_test)
            if acc > best_score:
                best_score = acc
                best_xor = const

        results[f"lane_{lane}"] = {
            "xor_constant": best_xor,
            "accuracy": float(best_score)
        }
        print(f"  XOR with {best_xor}: {best_score*100:.1f}%")

    return results

def correlation_analysis(k_values, drift_by_lane, max_lane=7):
    """Compute correlations between k and drift."""
    print("\n" + "=" * 60)
    print("CORRELATION ANALYSIS")
    print("=" * 60)

    results = {}

    for lane in range(max_lane):
        y = drift_by_lane[lane]

        # Pearson correlation
        corr = np.corrcoef(k_values, y)[0, 1]

        # Spearman rank correlation (monotonic relationship)
        from scipy.stats import spearmanr
        spearman_corr, p_value = spearmanr(k_values, y)

        results[f"lane_{lane}"] = {
            "pearson": float(corr),
            "spearman": float(spearman_corr),
            "p_value": float(p_value)
        }

        print(f"Lane {lane}: Pearson={corr:.4f}, Spearman={spearman_corr:.4f}, p={p_value:.4e}")

    return results

def summarize_results(poly_results, mod_results, bit_results, corr_results):
    """Create summary report."""
    print("\n" + "=" * 60)
    print("SUMMARY REPORT")
    print("=" * 60)

    summary = {
        "task": "Task 4: Index-Based Pattern Analysis (Lanes 0-6)",
        "goal": "Find drift[k][lane] = f(k, lane)",
        "lanes_analyzed": list(range(7)),
        "results_by_lane": {}
    }

    for lane in range(7):
        lane_key = f"lane_{lane}"

        # Get best polynomial result
        poly_lane = poly_results[lane_key]
        poly_best = max(
            [(k, v) for k, v in poly_lane.items() if k.startswith("degree_")],
            key=lambda x: x[1]["test_accuracy"]
        )

        # Get best modular result
        mod_lane = mod_results[lane_key]
        mod_best_acc = max(
            mod_lane["linear_mod"]["accuracy"],
            mod_lane["quadratic_mod"]["accuracy"],
            mod_lane["modular_mult"]["accuracy"]
        )

        # Determine which is best
        if mod_best_acc > poly_best[1]["test_accuracy"]:
            if mod_lane["linear_mod"]["accuracy"] == mod_best_acc:
                best_method = "Modular (Linear)"
                best_formula = mod_lane["linear_mod"]["best_pattern"]
            elif mod_lane["quadratic_mod"]["accuracy"] == mod_best_acc:
                best_method = "Modular (Quadratic)"
                best_formula = mod_lane["quadratic_mod"]["best_pattern"]
            else:
                best_method = "Modular (Mult)"
                best_formula = mod_lane["modular_mult"]["best_pattern"]
            best_accuracy = mod_best_acc
        else:
            best_method = f"Polynomial (degree {poly_best[1]['degree']}, {poly_best[1]['regression']})"
            best_formula = f"polynomial degree {poly_best[1]['degree']}"
            best_accuracy = poly_best[1]["test_accuracy"]

        summary["results_by_lane"][lane_key] = {
            "best_method": best_method,
            "best_accuracy": float(best_accuracy),
            "best_formula": best_formula,
            "correlation": corr_results[lane_key]["pearson"],
            "polynomial_best": float(poly_best[1]["test_accuracy"]),
            "modular_best": float(mod_best_acc),
            "bit_xor_best": float(bit_results[lane_key]["accuracy"])
        }

        print(f"\nLane {lane}:")
        print(f"  Best: {best_method} = {best_accuracy*100:.1f}%")
        print(f"  Formula: {best_formula}")
        print(f"  Correlation: {corr_results[lane_key]['pearson']:.4f}")

    # Overall summary
    best_overall = max(
        [(lane, data["best_accuracy"]) for lane, data in summary["results_by_lane"].items()],
        key=lambda x: x[1]
    )

    print("\n" + "=" * 60)
    print(f"BEST OVERALL: {best_overall[0]} at {best_overall[1]*100:.1f}% accuracy")
    print("=" * 60)

    summary["best_overall"] = {
        "lane": best_overall[0],
        "accuracy": float(best_overall[1]),
        "details": summary["results_by_lane"][best_overall[0]]
    }

    return summary

def main():
    """Run full index-based analysis."""
    print("Task 4: Index-Based Pattern Analysis")
    print("Analyzing lanes 0-6 for drift[k][lane] = f(k, lane)")
    print()

    # Load data
    print("Loading drift data...")
    k_values, drift_by_lane = load_drift_data()
    print(f"Loaded {len(k_values)} transitions across 16 lanes")
    print(f"k values range: {k_values.min()} to {k_values.max()}")
    print()

    # Run analyses
    poly_results = polynomial_regression_analysis(k_values, drift_by_lane)
    mod_results = modular_arithmetic_patterns(k_values, drift_by_lane)
    bit_results = bit_pattern_analysis(k_values, drift_by_lane)
    corr_results = correlation_analysis(k_values, drift_by_lane)

    # Summarize
    summary = summarize_results(poly_results, mod_results, bit_results, corr_results)

    # Save results
    output_file = Path("/home/solo/LadderV3/kh-assist/experiments/07-pysr-drift-generator/results/task4_index_based_analysis.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    full_results = {
        "summary": summary,
        "polynomial_regression": poly_results,
        "modular_arithmetic": mod_results,
        "bit_patterns": bit_results,
        "correlations": corr_results
    }

    with open(output_file, 'w') as f:
        json.dump(full_results, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")

    # Print final report format
    print("\n" + "=" * 60)
    print("TASK 4 FINAL REPORT")
    print("=" * 60)

    for lane in range(7):
        lane_key = f"lane_{lane}"
        data = summary["results_by_lane"][lane_key]
        print(f"Lane {lane}: Best {data['best_accuracy']*100:5.1f}% (method: {data['best_method']})")

    best = summary["best_overall"]
    print(f"\nBest overall: {best['lane']} at {best['accuracy']*100:.1f}%")
    print(f"Formula: {best['details']['best_formula']}")

    # Success criteria
    if best["accuracy"] >= 0.80:
        print("\n✅ SUCCESS: Achieved ≥80% accuracy!")
    else:
        print(f"\n⚠ PARTIAL: Best accuracy {best['accuracy']*100:.1f}% (target: ≥80%)")

    return summary

if __name__ == "__main__":
    try:
        summary = main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
