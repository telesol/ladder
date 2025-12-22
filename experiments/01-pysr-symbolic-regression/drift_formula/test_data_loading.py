#!/usr/bin/env python3
"""
Quick test: Verify data loading works correctly

This script tests the data extraction logic without running PySR.
Use this to verify everything is set up correctly before launching the full training.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Constants
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

# Load drift data
DATA_FILE = project_root / "drift_data_CORRECT_BYTE_ORDER.json"
print(f"Loading data from: {DATA_FILE}")

with open(DATA_FILE) as f:
    data = json.load(f)

print(f"✓ Loaded {len(data['transitions'])} transitions")
print(f"✓ Total drift values: {data['total_drift_values']}")
print(f"✓ Byte order: {data['byte_order']}")

# Extract evolution values ONLY (k > lane×8)
print("\n=== Extracting Evolution Values ===")

features_list = []
targets_list = []

for trans in data['transitions']:
    k = trans['from_puzzle']

    for lane in range(16):
        activation_k = lane * 8 if lane > 0 else 1

        # EVOLUTION PHASE ONLY
        if k > activation_k:
            drift = trans['drifts'][lane]

            features_list.append({
                'k': k,
                'lane': lane,
                'steps_since_activation': k - activation_k,
                'exponent': EXPONENTS[lane]
            })
            targets_list.append(drift)

# Convert to DataFrame and numpy arrays
df = pd.DataFrame(features_list)
X = df.values  # Features: [k, lane, steps_since_activation, exponent]
y = np.array(targets_list)  # Targets: drift values

print(f"✓ Extracted {len(y)} evolution values")
print(f"✓ Features shape: {X.shape}")
print(f"✓ Target shape: {y.shape}")

# Analyze data
print("\n=== Data Statistics ===")
print(f"Drift range: [{y.min()}, {y.max()}]")
print(f"Drift mean: {y.mean():.2f}")
print(f"Drift std: {y.std():.2f}")
print(f"Multiples of 16: {(y % 16 == 0).sum()}/{len(y)} = {100*(y % 16 == 0).sum()/len(y):.1f}%")

# Per-lane statistics
print("\nPer-lane counts:")
for lane in range(16):
    mask = df['lane'] == lane
    count = mask.sum()
    if count > 0:
        lane_drift = y[mask]
        print(f"  Lane {lane}: {count:3d} values, "
              f"drift ∈ [{lane_drift.min():3d}, {lane_drift.max():3d}], "
              f"mean={lane_drift.mean():.1f}, "
              f"exp={EXPONENTS[lane]}")

# Split into train/validation
# Strategy: Use puzzles 1-55 for training, 56-69 for validation
TRAIN_CUTOFF = 55

train_mask = df['k'] <= TRAIN_CUTOFF
val_mask = df['k'] > TRAIN_CUTOFF

X_train, X_val = X[train_mask], X[val_mask]
y_train, y_val = y[train_mask], y[val_mask]

print(f"\n=== Train/Val Split ===")
print(f"Training: puzzles 1-{TRAIN_CUTOFF} → {len(y_train)} samples")
print(f"Validation: puzzles {TRAIN_CUTOFF+1}-69 → {len(y_val)} samples")

# Show sample data
print("\n=== Sample Training Data (first 10) ===")
print(df.head(10))
print(f"\nSample targets: {y[:10]}")

# Show sample validation data
val_df = df[val_mask]
print("\n=== Sample Validation Data (first 10) ===")
print(val_df.head(10))
print(f"\nSample targets: {y[val_mask][:10]}")

print("\n✅ Data loading test PASSED!")
print("\nReady to run full PySR training.")
print("Run: python3 train_drift_evolution.py")
