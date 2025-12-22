#!/usr/bin/env python3
"""Prepare filtered datasets for regime-aware training"""

import pandas as pd

# Load full datasets
train = pd.read_csv('experiments/07-pysr-drift-generator/train.csv')
val = pd.read_csv('experiments/07-pysr-drift-generator/val.csv')
test = pd.read_csv('experiments/07-pysr-drift-generator/test.csv')

# k<64 filter (stable regime)
train_k64 = train[train['k'] < 64]
val_k64 = val[val['k'] < 64]
test_k64 = test[test['k'] < 64]

train_k64.to_csv('experiments/07-pysr-drift-generator/train_k64_filtered.csv', index=False)
val_k64.to_csv('experiments/07-pysr-drift-generator/val_k64_filtered.csv', index=False)
test_k64.to_csv('experiments/07-pysr-drift-generator/test_k64_filtered.csv', index=False)

print(f"k<64 filtered:")
print(f"  Train: {len(train_k64)} samples")
print(f"  Val: {len(val_k64)} samples")
print(f"  Test: {len(test_k64)} samples")

# k<32 filter (most stable)
train_k32 = train[train['k'] < 32]
train_k32.to_csv('experiments/07-pysr-drift-generator/train_k32_stable.csv', index=False)
print(f"\nk<32 stable: {len(train_k32)} samples")

print("\n✅ Filtered datasets ready!")
