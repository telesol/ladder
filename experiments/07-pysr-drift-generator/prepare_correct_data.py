#!/usr/bin/env python3
"""
Prepare training data for PySR from drift_data_export.json

This creates train/val/test splits with CORRECT drift values from the export file.
"""

import json
import pandas as pd
import random

# Load drift data
with open('drift_data_export.json') as f:
    data = json.load(f)

print("Loading drift data...")
print(f"Total transitions: {len(data['transitions'])}")
print()

# Create dataset
records = []

for t in data['transitions']:
    k = t['from_puzzle']
    for lane in range(16):
        drift_prev = t['X_k'][lane]
        drift = t['drifts'][lane]
        A = data['A_coefficients'][lane]

        records.append({
            'k': k,
            'lane': lane,
            'drift': drift,
            'drift_prev': drift_prev,
            'A': A
        })

print(f"Total records: {len(records)}")
print()

# Convert to DataFrame
df = pd.DataFrame(records)

# Shuffle
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Split: 80% train, 10% val, 10% test
n = len(df)
n_train = int(0.8 * n)
n_val = int(0.1 * n)

train = df[:n_train]
val = df[n_train:n_train+n_val]
test = df[n_train+n_val:]

print(f"Train: {len(train)}")
print(f"Val:   {len(val)}")
print(f"Test:  {len(test)}")
print()

# Save
train.to_csv('experiments/07-pysr-drift-generator/train.csv', index=False)
val.to_csv('experiments/07-pysr-drift-generator/val.csv', index=False)
test.to_csv('experiments/07-pysr-drift-generator/test.csv', index=False)

print("✅ Data saved!")
print()

# Show Lane 7 stats
lane7_train = train[train['lane'] == 7]
lane7_val = val[val['lane'] == 7]
lane7_test = test[test['lane'] == 7]

print("Lane 7 statistics:")
print(f"  Train: {len(lane7_train)} samples, {lane7_train['drift'].nunique()} unique drifts")
print(f"  Val:   {len(lane7_val)} samples, {lane7_val['drift'].nunique()} unique drifts")
print(f"  Test:  {len(lane7_test)} samples, {lane7_test['drift'].nunique()} unique drifts")
print()
print(f"  Unique drift values: {sorted(train[train['lane'] == 7]['drift'].unique())}")
