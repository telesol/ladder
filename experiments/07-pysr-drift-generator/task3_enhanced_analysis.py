#!/usr/bin/env python3
"""
Task 3 Enhanced: Cross-Lane Dependency Analysis with Multiple Approaches

Test multiple hypotheses:
1. Linear cross-lane dependencies
2. Nonlinear cross-lane dependencies (polynomial features)
3. XOR/bitwise dependencies
4. Index-based patterns with cross-lane modulation
"""

import json
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Load drift data
print("Loading drift data...")
with open('/home/solo/LadderV3/kh-assist/drift_data_export.json', 'r') as f:
    data = json.load(f)

transitions = data['transitions']
n_transitions = len(transitions)

# Build drift matrix and puzzle index mapping
drift_matrix = np.zeros((n_transitions, 16), dtype=int)
puzzle_indices = []
for i, trans in enumerate(transitions):
    drift_matrix[i] = trans['drifts']
    puzzle_indices.append(trans['from_puzzle'])

print(f"Loaded {n_transitions} transitions")

# Split train/test
train_end = 50
train_data = drift_matrix[:train_end]
test_data = drift_matrix[train_end:]
train_indices = puzzle_indices[:train_end]
test_indices = puzzle_indices[train_end:]

results = {
    "metadata": {
        "description": "Enhanced cross-lane dependency analysis with multiple approaches",
        "approaches": ["linear", "polynomial", "random_forest", "xor_bitwise", "index_modulated"]
    },
    "lanes": {}
}

print("\n" + "="*70)
print("TASK 3 ENHANCED: MULTIPLE DEPENDENCY TESTS")
print("="*70)

for target_lane in range(7):
    print(f"\n{'='*70}")
    print(f"Lane {target_lane}")
    print(f"{'='*70}")

    lane_results = {
        "approaches": {}
    }

    # Prepare sequential data (k-1 -> k)
    X_train_seq = []
    y_train_seq = []
    idx_train_seq = []

    for k in range(1, len(train_data)):
        X_train_seq.append(train_data[k-1, :target_lane+1])
        y_train_seq.append(train_data[k, target_lane])
        idx_train_seq.append(train_indices[k])

    X_train_seq = np.array(X_train_seq)
    y_train_seq = np.array(y_train_seq)
    idx_train_seq = np.array(idx_train_seq)

    X_test_seq = []
    y_test_seq = []
    idx_test_seq = []

    for k in range(1, len(test_data)):
        actual_k = train_end + k
        if actual_k > 0:
            if actual_k - 1 < train_end:
                prev_drift = train_data[actual_k - 1]
            else:
                prev_drift = test_data[k - 1]

            X_test_seq.append(prev_drift[:target_lane+1])
            y_test_seq.append(test_data[k, target_lane])
            idx_test_seq.append(test_indices[k] if k < len(test_indices) else 0)

    X_test_seq = np.array(X_test_seq)
    y_test_seq = np.array(y_test_seq)
    idx_test_seq = np.array(idx_test_seq)

    # Approach 1: Linear (baseline from previous run)
    print("\n1. Linear Regression:")
    model_linear = LinearRegression()
    model_linear.fit(X_train_seq, y_train_seq)
    pred_linear = np.round(model_linear.predict(X_test_seq)) % 256
    acc_linear = np.mean(pred_linear == y_test_seq) * 100
    mae_linear = mean_absolute_error(y_test_seq, pred_linear)
    print(f"   Accuracy: {acc_linear:.1f}%  MAE: {mae_linear:.2f}")

    lane_results["approaches"]["linear"] = {
        "accuracy": float(acc_linear),
        "mae": float(mae_linear)
    }

    # Approach 2: Polynomial features (degree 2)
    if target_lane <= 3:  # Only for small number of lanes (avoid feature explosion)
        print("\n2. Polynomial Features (degree 2):")
        poly = PolynomialFeatures(degree=2, include_bias=False)
        X_train_poly = poly.fit_transform(X_train_seq)
        X_test_poly = poly.transform(X_test_seq)

        model_poly = Ridge(alpha=1.0)  # Use Ridge to prevent overfitting
        model_poly.fit(X_train_poly, y_train_seq)
        pred_poly = np.round(model_poly.predict(X_test_poly)) % 256
        acc_poly = np.mean(pred_poly == y_test_seq) * 100
        mae_poly = mean_absolute_error(y_test_seq, pred_poly)
        print(f"   Accuracy: {acc_poly:.1f}%  MAE: {mae_poly:.2f}")

        lane_results["approaches"]["polynomial"] = {
            "accuracy": float(acc_poly),
            "mae": float(mae_poly)
        }
    else:
        print("\n2. Polynomial Features: Skipped (too many features)")
        lane_results["approaches"]["polynomial"] = {"accuracy": 0.0, "mae": 256.0}

    # Approach 3: Random Forest (captures nonlinear patterns)
    print("\n3. Random Forest:")
    model_rf = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
    model_rf.fit(X_train_seq, y_train_seq)
    pred_rf = np.round(model_rf.predict(X_test_seq)) % 256
    acc_rf = np.mean(pred_rf == y_test_seq) * 100
    mae_rf = mean_absolute_error(y_test_seq, pred_rf)
    print(f"   Accuracy: {acc_rf:.1f}%  MAE: {mae_rf:.2f}")

    lane_results["approaches"]["random_forest"] = {
        "accuracy": float(acc_rf),
        "mae": float(mae_rf)
    }

    # Approach 4: XOR/Bitwise patterns
    print("\n4. XOR/Bitwise Features:")
    # Add XOR features between pairs of lanes
    X_train_xor = X_train_seq.copy()
    X_test_xor = X_test_seq.copy()

    if target_lane > 0:
        # Add XOR of adjacent lanes
        xor_features_train = []
        xor_features_test = []

        for i in range(target_lane):
            xor_features_train.append((X_train_seq[:, i] ^ X_train_seq[:, i+1]).reshape(-1, 1))
            xor_features_test.append((X_test_seq[:, i] ^ X_test_seq[:, i+1]).reshape(-1, 1))

        if xor_features_train:
            X_train_xor = np.hstack([X_train_seq] + xor_features_train)
            X_test_xor = np.hstack([X_test_seq] + xor_features_test)

    model_xor = LinearRegression()
    model_xor.fit(X_train_xor, y_train_seq)
    pred_xor = np.round(model_xor.predict(X_test_xor)) % 256
    acc_xor = np.mean(pred_xor == y_test_seq) * 100
    mae_xor = mean_absolute_error(y_test_seq, pred_xor)
    print(f"   Accuracy: {acc_xor:.1f}%  MAE: {mae_xor:.2f}")

    lane_results["approaches"]["xor_bitwise"] = {
        "accuracy": float(acc_xor),
        "mae": float(mae_xor)
    }

    # Approach 5: Index-modulated (drift depends on puzzle index AND previous drift)
    print("\n5. Index-Modulated:")
    # Features: [previous drift lanes, puzzle_index, puzzle_index % 16, puzzle_index^2]
    X_train_idx = np.hstack([
        X_train_seq,
        idx_train_seq.reshape(-1, 1),
        (idx_train_seq % 16).reshape(-1, 1),
        (idx_train_seq ** 2).reshape(-1, 1)
    ])

    X_test_idx = np.hstack([
        X_test_seq,
        idx_test_seq.reshape(-1, 1),
        (idx_test_seq % 16).reshape(-1, 1),
        (idx_test_seq ** 2).reshape(-1, 1)
    ])

    model_idx = Ridge(alpha=1.0)
    model_idx.fit(X_train_idx, y_train_seq)
    pred_idx = np.round(model_idx.predict(X_test_idx)) % 256
    acc_idx = np.mean(pred_idx == y_test_seq) * 100
    mae_idx = mean_absolute_error(y_test_seq, pred_idx)
    print(f"   Accuracy: {acc_idx:.1f}%  MAE: {mae_idx:.2f}")

    lane_results["approaches"]["index_modulated"] = {
        "accuracy": float(acc_idx),
        "mae": float(mae_idx)
    }

    # Find best approach
    approaches = lane_results["approaches"]
    best_approach = max(approaches.items(), key=lambda x: x[1]["accuracy"])
    lane_results["best_approach"] = {
        "name": best_approach[0],
        "accuracy": best_approach[1]["accuracy"],
        "mae": best_approach[1]["mae"]
    }

    print(f"\n   → Best: {best_approach[0]} ({best_approach[1]['accuracy']:.1f}%)")

    results["lanes"][str(target_lane)] = lane_results

# Summary
print("\n" + "="*70)
print("SUMMARY - Best Approach per Lane")
print("="*70)

for lane in range(7):
    lane_data = results["lanes"][str(lane)]
    best = lane_data["best_approach"]
    print(f"Lane {lane}: {best['name']:20s} - {best['accuracy']:5.1f}% accuracy (MAE: {best['mae']:.2f})")

# Overall best
all_best = [(lane, results["lanes"][str(lane)]["best_approach"])
            for lane in range(7)]
overall_best = max(all_best, key=lambda x: x[1]["accuracy"])
print(f"\nOverall best: Lane {overall_best[0]} with {overall_best[1]['name']} ({overall_best[1]['accuracy']:.1f}%)")

# Check if any approach achieved >80%
high_acc = [f"Lane {lane} ({results['lanes'][str(lane)]['best_approach']['name']})"
            for lane in range(7)
            if results["lanes"][str(lane)]["best_approach"]["accuracy"] >= 80.0]

if high_acc:
    print(f"\n✓ Approaches with ≥80% accuracy: {', '.join(high_acc)}")
    conclusion = "DEPENDENCIES EXIST - Strong predictive models found"
else:
    avg_best = np.mean([results["lanes"][str(lane)]["best_approach"]["accuracy"]
                        for lane in range(7)])
    print(f"\n✗ No approach achieved ≥80% accuracy")
    print(f"Average best accuracy: {avg_best:.1f}%")

    if avg_best >= 20.0:
        conclusion = "WEAK PATTERNS - Some correlation detected but not predictive"
    else:
        conclusion = "INDEPENDENT - Drift appears random/unpredictable from previous values"

results["summary"] = {
    "overall_best_lane": overall_best[0],
    "overall_best_approach": overall_best[1]["name"],
    "overall_best_accuracy": overall_best[1]["accuracy"],
    "high_accuracy_lanes": high_acc,
    "conclusion": conclusion
}

print(f"\nConclusion: {conclusion}")

# Save
output_file = '/home/solo/LadderV3/kh-assist/experiments/07-pysr-drift-generator/results/task3_enhanced_analysis.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Results saved to: {output_file}")
print("="*70)
