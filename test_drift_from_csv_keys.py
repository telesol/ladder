#!/usr/bin/env python3
"""
Test if drift depends on X[k] using actual private keys from CSV
"""

import json
import csv

# Load drift data
with open('drift_data_CORRECT_BYTE_ORDER.json', 'r') as f:
    drift_data = json.load(f)

# Load private keys from CSV
private_keys = {}
with open('data/btc_puzzle_1_160_full.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 4:
            continue
        try:
            puzzle_num = int(row[0])
            priv_hex = row[3]  # Full private key
            if priv_hex.startswith('0x'):
                priv_hex = priv_hex[2:]
            # Pad to 64 hex chars
            priv_hex = priv_hex.zfill(64)
            private_keys[puzzle_num] = priv_hex
        except:
            continue

print(f"=== TESTING: drift[k][lane] = f(X_k[lane], k) ===\n")
print(f"Loaded {len(private_keys)} private keys from CSV\n")

# Show first few keys
print("Sample keys:")
for k in range(1, 6):
    if k in private_keys:
        key = private_keys[k]
        # Extract half-block (LAST 32 hex chars = 16 bytes)
        half = key[-32:]
        bytes_val = bytes.fromhex(half)
        print(f"  Puzzle {k}: {key}")
        print(f"    Half-block (last 32 chars): {half}")
        print(f"    Bytes: {list(bytes_val)}")

# Build (X_k[lane], drift) pairs
lane_data = {lane: [] for lane in range(16)}

for t in drift_data['transitions']:
    k_from = t['from_puzzle']
    k_to = t['to_puzzle']
    drifts = t['drifts']

    if k_from not in private_keys:
        continue

    key = private_keys[k_from]
    half_block = key[-32:]  # LAST 32 hex chars (where the actual data is!)
    X_k = bytes.fromhex(half_block)

    for lane in range(16):
        if k_from >= lane * 8:  # Lane is active
            x_val = X_k[lane]
            drift_val = drifts[lane]
            lane_data[lane].append((k_from, x_val, drift_val))

print("\n1. DATA DISTRIBUTION PER LANE:\n")
for lane in range(9):
    data = lane_data[lane]
    if not data:
        continue

    unique_x = len(set([x for k, x, d in data]))
    unique_d = len(set([d for k, x, d in data]))
    print(f"   Lane {lane}: {len(data)} points, {unique_x} unique X values, {unique_d} unique drift values")

# Test if drift = f(X) alone
print("\n2. TESTING: drift = f(X[k][lane]) alone\n")
for lane in range(9):
    data = lane_data[lane]
    if not data:
        continue

    # Group by X value
    x_to_drifts = {}
    for k, x, d in data:
        if x not in x_to_drifts:
            x_to_drifts[x] = []
        x_to_drifts[x].append(d)

    # Check if deterministic
    is_det = True
    for x, drifts in x_to_drifts.items():
        if len(set(drifts)) > 1:
            is_det = False
            break

    if is_det:
        print(f"   Lane {lane}: ✅ DETERMINISTIC (drift = f(X) alone)")
    else:
        multi = sum(1 for drifts in x_to_drifts.values() if len(set(drifts)) > 1)
        print(f"   Lane {lane}: ❌ NOT f(X) alone ({multi}/{len(x_to_drifts)} X values map to multiple drifts)")

# Test if drift = f(X, k)
print("\n3. TESTING: drift = (a*X + b*k + c) mod 256\n")
for lane in range(min(3, 9)):  # Test first 3 lanes
    data = lane_data[lane]
    if len(data) < 10:
        continue

    print(f"   Lane {lane}: testing all (a, b, c) combinations...")

    best_a, best_b, best_c, best_acc = 0, 0, 0, 0

    # Sample parameter space
    for a in range(0, 256, 4):
        for b in range(0, 256, 4):
            for c in range(0, 256, 4):
                correct = 0
                for k, x, d_actual in data:
                    d_pred = (a * x + b * k + c) % 256
                    if d_pred == d_actual:
                        correct += 1

                acc = 100 * correct / len(data)
                if acc > best_acc:
                    best_a, best_b, best_c, best_acc = a, b, c, acc

    status = "✅" if best_acc == 100 else "⚠️" if best_acc > 90 else ""
    print(f"      Best: a={best_a:3d}, b={best_b:3d}, c={best_c:3d}, accuracy={best_acc:.1f}% {status}")

print("\n" + "="*70)
