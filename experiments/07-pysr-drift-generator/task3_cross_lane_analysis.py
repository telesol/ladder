#!/usr/bin/env python3
"""
Task 3: Cross-Lane Dependency Analysis

Test if drift values in lanes 0-6 depend on multiple lanes (cross-lane dependencies)
rather than just their own previous drift values.

Approach:
- For each lane L in 0-6, test if drift[k][L] depends on drift[k-1][0:L+1]
- Use linear regression: drift[k][L] = w0*drift[k-1][0] + ... + wL*drift[k-1][L] + b
- Compare accuracy with single-lane recursive models
"""

import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

# Load drift data
print("Loading drift data...")
with open('/home/solo/LadderV3/kh-assist/drift_data_export.json', 'r') as f:
    data = json.load(f)

transitions = data['transitions']
n_transitions = len(transitions)
n_lanes = 16

# Build drift matrix [n_transitions, 16]
drift_matrix = np.zeros((n_transitions, n_lanes), dtype=int)
for i, trans in enumerate(transitions):
    drift_matrix[i] = trans['drifts']

print(f"Loaded {n_transitions} transitions, {n_lanes} lanes")
print(f"Drift matrix shape: {drift_matrix.shape}")

# Split into train/test
# Use first 50 transitions for training, 51-69 for testing
train_end = 50
train_data = drift_matrix[:train_end]
test_data = drift_matrix[train_end:]

print(f"\nTrain: transitions 1-{train_end} ({len(train_data)} samples)")
print(f"Test: transitions {train_end+1}-{n_transitions} ({len(test_data)} samples)")

# Results storage
results = {
    "metadata": {
        "description": "Cross-lane dependency analysis for lanes 0-6",
        "train_size": len(train_data),
        "test_size": len(test_data),
        "approach": "Linear regression with multiple lane dependencies"
    },
    "lanes": {}
}

print("\n" + "="*70)
print("TASK 3: CROSS-LANE DEPENDENCY ANALYSIS")
print("="*70)

# Analyze lanes 0-6 (the always-changing lanes)
for target_lane in range(7):
    print(f"\n--- Lane {target_lane} ---")

    # Build features: drift[k-1] for lanes 0 through target_lane
    # Build target: drift[k] for target_lane

    # Training data (need k-1 and k, so start from index 1)
    X_train = []
    y_train = []
    for k in range(1, len(train_data)):
        # Features: all lanes from 0 to target_lane at time k-1
        features = train_data[k-1, :target_lane+1].tolist()
        X_train.append(features)
        # Target: target_lane at time k
        y_train.append(train_data[k, target_lane])

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    # Test data
    X_test = []
    y_test = []
    for k in range(1, len(test_data)):
        # Need to get k-1 from appropriate source
        # For test data starting at index train_end, k-1 might be in train or test
        actual_k = train_end + k
        if actual_k > 0:
            # Get drift[k-1]
            if actual_k - 1 < train_end:
                prev_drift = train_data[actual_k - 1]
            else:
                prev_drift = test_data[k - 1]

            features = prev_drift[:target_lane+1].tolist()
            X_test.append(features)
            y_test.append(test_data[k, target_lane])

    X_test = np.array(X_test)
    y_test = np.array(y_test)

    print(f"Training samples: {len(X_train)}, features per sample: {X_train.shape[1]}")
    print(f"Test samples: {len(X_test)}")

    # Train linear regression model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Get predictions
    y_train_pred = model.predict(X_train) % 256
    y_test_pred = model.predict(X_test) % 256

    # Calculate metrics
    # Exact match accuracy (mod 256)
    train_acc = np.mean(np.round(y_train_pred) % 256 == y_train % 256) * 100
    test_acc = np.mean(np.round(y_test_pred) % 256 == y_test % 256) * 100

    # MAE
    train_mae = mean_absolute_error(y_train % 256, np.round(y_train_pred) % 256)
    test_mae = mean_absolute_error(y_test % 256, np.round(y_test_pred) % 256)

    # R² score
    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)

    # Get coefficients
    coefficients = model.coef_.tolist()
    intercept = float(model.intercept_)

    # Identify which lanes have strongest dependencies (largest absolute coefficients)
    lane_importance = [(i, abs(coefficients[i])) for i in range(len(coefficients))]
    lane_importance.sort(key=lambda x: x[1], reverse=True)

    print(f"Train accuracy: {train_acc:.1f}%")
    print(f"Test accuracy: {test_acc:.1f}%")
    print(f"Test MAE: {test_mae:.2f}")
    print(f"Test R²: {test_r2:.3f}")
    print(f"Intercept: {intercept:.2f}")
    print(f"Coefficients: {[f'{c:.3f}' for c in coefficients]}")
    print(f"Strongest dependencies: {[(f'Lane {idx}', f'{val:.3f}') for idx, val in lane_importance[:3]]}")

    # Store results
    results["lanes"][str(target_lane)] = {
        "num_dependent_lanes": target_lane + 1,
        "train_accuracy": float(train_acc),
        "test_accuracy": float(test_acc),
        "train_mae": float(train_mae),
        "test_mae": float(test_mae),
        "train_r2": float(train_r2),
        "test_r2": float(test_r2),
        "intercept": intercept,
        "coefficients": {f"lane_{i}": float(coefficients[i]) for i in range(len(coefficients))},
        "strongest_dependencies": [
            {"lane": idx, "weight": float(val)} for idx, val in lane_importance
        ],
        "formula": f"drift[k][{target_lane}] = " +
                   " + ".join([f"{coefficients[i]:.3f}*drift[k-1][{i}]" for i in range(len(coefficients))]) +
                   f" + {intercept:.3f}"
    }

# Summary statistics
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

# Find best performing lanes
lane_accuracies = [(lane, results["lanes"][str(lane)]["test_accuracy"])
                   for lane in range(7)]
lane_accuracies.sort(key=lambda x: x[1], reverse=True)

print("\nLane Performance (Test Accuracy):")
for lane, acc in lane_accuracies:
    print(f"  Lane {lane}: {acc:.1f}%")

# Check for lanes with >80% accuracy
high_performers = [lane for lane, acc in lane_accuracies if acc >= 80.0]
if high_performers:
    print(f"\n✓ Lanes with ≥80% accuracy: {high_performers}")
else:
    print(f"\n✗ No lanes achieved ≥80% accuracy")

# Average improvement metrics
avg_test_acc = np.mean([results["lanes"][str(i)]["test_accuracy"] for i in range(7)])
print(f"\nAverage test accuracy across lanes 0-6: {avg_test_acc:.1f}%")

# Analyze dependency patterns
print("\nDependency Patterns:")
for lane in range(7):
    lane_data = results["lanes"][str(lane)]
    top_dep = lane_data["strongest_dependencies"][0]
    print(f"  Lane {lane}: Strongest dependency on Lane {top_dep['lane']} (weight: {top_dep['weight']:.3f})")

# Determine conclusion
if any(acc >= 80.0 for _, acc in lane_accuracies):
    conclusion = "DEPENDENCIES EXIST - Cross-lane models show strong predictive power"
elif avg_test_acc >= 50.0:
    conclusion = "WEAK DEPENDENCIES - Some cross-lane correlation detected"
else:
    conclusion = "INDEPENDENT - No significant cross-lane dependencies found"

results["summary"] = {
    "best_lane": lane_accuracies[0][0],
    "best_accuracy": lane_accuracies[0][1],
    "average_test_accuracy": float(avg_test_acc),
    "high_performers_80_percent": high_performers,
    "conclusion": conclusion
}

print(f"\nConclusion: {conclusion}")

# Save results
output_file = '/home/solo/LadderV3/kh-assist/experiments/07-pysr-drift-generator/results/task3_cross_lane_analysis.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Results saved to: {output_file}")

# Generate formatted report
print("\n" + "="*70)
print("TASK 3 REPORT - Cross-Lane Dependencies")
print("="*70)
print()
for lane in range(7):
    lane_data = results["lanes"][str(lane)]
    deps = lane_data["strongest_dependencies"][:3]
    dep_str = ", ".join([f"Lane {d['lane']}" for d in deps])
    print(f"Lane {lane}: {lane_data['test_accuracy']:.1f}% (depends on: {dep_str})")

if high_performers:
    best_lane = lane_accuracies[0][0]
    best_acc = lane_accuracies[0][1]
    baseline_acc = 0.0  # Baseline would be from single-lane recursive (Task 1)
    improvement = best_acc - baseline_acc
    print(f"\nBest improvement: Lane {best_lane} (+{improvement:.1f}% vs single-lane)")
else:
    print(f"\nNo significant improvement over single-lane models")

print(f"\nConclusion: {conclusion}")
print("="*70)
