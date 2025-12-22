#!/usr/bin/env python3
"""Analyze Task 2 predictions in detail."""

import pandas as pd
import numpy as np

# Load test data
test_df = pd.read_csv('test_k64_filtered.csv')
test_lane7 = test_df[test_df['lane'] == 7].copy()

print('=' * 80)
print('DETAILED PREDICTION ANALYSIS - Lane 7 (k<64)')
print('=' * 80)
print()
print('Formula: drift[k] = ((k/30) - 0.905)**32 * 0.596 mod 256')
print()

# Compute predictions using the formula
def pysr_predict(k):
    return int(((k * 0.033334613 - 0.90507096)**32 * 0.59550494)) % 256

# Get actual values
k_vals = test_lane7['k'].values
drift_prev_vals = test_lane7['drift_prev'].values
actual_vals = test_lane7['drift'].values

print('Test Set Predictions (all 12 samples):')
print('=' * 80)
print(' k | drift_prev | actual | predicted | error | match | notes')
print('-' * 80)

matches = 0
for i in range(len(k_vals)):
    k = int(k_vals[i])
    dp = int(drift_prev_vals[i])
    actual = int(actual_vals[i])
    pred = pysr_predict(k)
    error = abs(actual - pred)
    match = 'OK' if actual == pred else 'XX'

    # Add notes for special cases
    notes = ''
    if actual == 0:
        notes = '(zero drift)'
    elif error > 128:
        notes = f'(large error: {error})'

    if actual == pred:
        matches += 1

    print(f'{k:2d} | {dp:10d} | {actual:6d} | {pred:9d} | {error:5d} | {match:5s} | {notes}')

print('-' * 80)
print(f'Total: {matches}/{len(k_vals)} = {matches/len(k_vals)*100:.2f}% exact match')
print()

# Analyze errors
errors = []
for i in range(len(k_vals)):
    k = int(k_vals[i])
    actual = int(actual_vals[i])
    pred = pysr_predict(k)
    if actual != pred:
        errors.append((k, actual, pred, abs(actual - pred)))

if errors:
    print('ERROR ANALYSIS:')
    print('-' * 80)
    print(f'Number of mismatches: {len(errors)}')
    print(f'Mismatched k values: {[e[0] for e in errors]}')
    print()
    print('Mismatch details:')
    for k, actual, pred, error in errors:
        print(f'  k={k}: actual={actual}, pred={pred}, error={error}')
else:
    print('PERFECT: All predictions match!')

print('=' * 80)
