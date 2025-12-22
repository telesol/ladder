#!/usr/bin/env python3
"""
Re-test H1 (index-based) on ACTIVE drift values only.
Test if active_drift[k][lane] = f(k) where k is adjusted for activation time.
"""

import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# Load drift data
with open('drift_data_CORRECT_BYTE_ORDER.json', 'r') as f:
    data = json.load(f)

transitions = data['transitions']

print("=== H1 INDEX-BASED PATTERN (ACTIVE VALUES ONLY) ===\n")

# For each lane, build (k_adjusted, drift) pairs
# where k_adjusted = k - lane*8 (steps since activation)
active_data = {lane: [] for lane in range(16)}
for t in transitions:
    k = t['from_puzzle']
    drifts = t['drifts']
    for lane in range(16):
        if k >= lane * 8:  # Lane is active
            k_adj = k - lane * 8  # Steps since activation
            active_data[lane].append((k_adj, drifts[lane]))

# Test polynomial regression on k_adjusted
def test_polynomial_fit(data_points, degree=3):
    """Test polynomial fit: drift = sum(a_i * k^i) mod 256"""
    if len(data_points) < degree + 1:
        return None, 0

    k_vals = np.array([k for k, d in data_points]).reshape(-1, 1)
    drift_vals = np.array([d for k, d in data_points])

    # Try polynomial regression
    poly = PolynomialFeatures(degree=degree)
    k_poly = poly.fit_transform(k_vals)

    model = LinearRegression()
    model.fit(k_poly, drift_vals)

    predictions = model.predict(k_poly)
    predictions_mod = np.round(predictions) % 256

    correct = np.sum(predictions_mod == drift_vals)
    accuracy = 100 * correct / len(drift_vals)

    return model, accuracy

# Test modular arithmetic: drift = (a*k + b) mod 256
def test_modular_linear(data_points):
    """Test all combinations of (a*k + b) mod 256"""
    if len(data_points) < 2:
        return None, None, 0

    best_a, best_b, best_acc = 0, 0, 0

    for a in range(256):
        for b in range(256):
            correct = 0
            for k, drift_actual in data_points:
                drift_pred = (a * k + b) % 256
                if drift_pred == drift_actual:
                    correct += 1

            accuracy = 100 * correct / len(data_points)
            if accuracy > best_acc:
                best_a, best_b, best_acc = a, b, accuracy

    return best_a, best_b, best_acc

# Test modular polynomial: drift = (a*k^2 + b*k + c) mod 256
def test_modular_quadratic(data_points):
    """Test all combinations of (a*k^2 + b*k + c) mod 256 (sampled)"""
    if len(data_points) < 3:
        return None, None, None, 0

    best_a, best_b, best_c, best_acc = 0, 0, 0, 0

    # Sample parameter space
    for a in range(0, 256, 8):
        for b in range(0, 256, 8):
            for c in range(0, 256, 8):
                correct = 0
                for k, drift_actual in data_points:
                    drift_pred = (a * k * k + b * k + c) % 256
                    if drift_pred == drift_actual:
                        correct += 1

                accuracy = 100 * correct / len(data_points)
                if accuracy > best_acc:
                    best_a, best_b, best_c, best_acc = a, b, c, accuracy

    return best_a, best_b, best_c, best_acc

print("1. MODULAR LINEAR: drift = (a*k_adj + b) mod 256")
print("   (k_adj = k - lane*8, steps since lane activation)\n")
for lane in range(9):
    points = active_data[lane]
    if len(points) < 2:
        continue

    a, b, acc = test_modular_linear(points)
    status = "✅" if acc == 100 else "⚠️" if acc > 90 else ""
    print(f"   Lane {lane}: a={a:3d}, b={b:3d}, accuracy={acc:6.2f}% ({int(acc*len(points)/100)}/{len(points)}) {status}")

print("\n2. MODULAR QUADRATIC (sampled): drift = (a*k^2 + b*k + c) mod 256\n")
for lane in range(9):
    points = active_data[lane]
    if len(points) < 3:
        continue

    a, b, c, acc = test_modular_quadratic(points)
    status = "✅" if acc == 100 else "⚠️" if acc > 90 else ""
    print(f"   Lane {lane}: a={a:3d}, b={b:3d}, c={c:3d}, accuracy={acc:6.2f}% {status}")

print("\n3. POLYNOMIAL REGRESSION (degree 3): drift ≈ sum(a_i * k^i)\n")
for lane in range(9):
    points = active_data[lane]
    if len(points) < 4:
        continue

    model, acc = test_polynomial_fit(points, degree=3)
    status = "✅" if acc == 100 else "⚠️" if acc > 90 else ""
    print(f"   Lane {lane}: accuracy={acc:6.2f}% {status}")

print("\n" + "="*70)
print("NOTE: Testing on k_adjusted = k - lane*8 (steps since activation)")
print("      Quadratic test uses sampled parameter space (step=8)")
print("="*70)
