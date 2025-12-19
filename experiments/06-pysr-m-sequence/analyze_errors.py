#!/usr/bin/env python3
"""
Analyze error patterns in PySR predictions to identify systematic biases.
"""

import json
import pandas as pd
import numpy as np

print("=" * 70)
print("PYSR ERROR PATTERN ANALYSIS")
print("=" * 70)

# Load training results
with open('training_results.json') as f:
    results = json.load(f)

predictions = results['validation']['predictions']

print("\n1. Validation Predictions:")
print(f"   {'n':<4} {'Predicted':<15} {'Actual':<15} {'Ratio':<8} {'Error':<15} {'d_n':<4}")
print("   " + "-" * 70)

from convergent_database import D_SEQUENCE

for pred in predictions:
    n = pred['n']
    predicted = pred['predicted']
    actual = pred['actual']
    ratio = predicted / actual if actual != 0 else 0
    error = predicted - actual
    d_n = D_SEQUENCE[n]

    print(f"   {n:<4} {predicted:<15,} {actual:<15,} {ratio:<8.2%} {error:<15,} {d_n:<4}")

# Calculate error statistics
ratios = [p['predicted'] / p['actual'] for p in predictions]
errors = [p['predicted'] - p['actual'] for p in predictions]
abs_errors = [abs(e) for e in errors]

print(f"\n2. Error Statistics:")
print(f"   Mean ratio (pred/actual): {np.mean(ratios):.4f}")
print(f"   Median ratio:             {np.median(ratios):.4f}")
print(f"   Std dev ratio:            {np.std(ratios):.4f}")
print(f"   Min ratio:                {np.min(ratios):.4f}")
print(f"   Max ratio:                {np.max(ratios):.4f}")

# Check if there's a consistent correction factor
correction_factor = 1 / np.mean(ratios)
print(f"\n3. Correction Factor Analysis:")
print(f"   Correction factor (to fix mean): {correction_factor:.4f}")

# Apply correction and check
print(f"\n4. Results with Correction Factor ({correction_factor:.4f}):")
print(f"   {'n':<4} {'Corrected':<15} {'Actual':<15} {'Ratio':<8} {'Match?':<6}")
print("   " + "-" * 60)

corrected_matches = 0
for pred in predictions:
    n = pred['n']
    predicted = pred['predicted']
    actual = pred['actual']

    corrected = int(predicted * correction_factor)
    ratio = corrected / actual if actual != 0 else 0
    match = (corrected == actual)

    if match:
        corrected_matches += 1

    print(f"   {n:<4} {corrected:<15,} {actual:<15,} {ratio:<8.2%} {'✅' if match else '❌':<6}")

accuracy_corrected = corrected_matches / len(predictions) * 100
print(f"\n   Accuracy with correction: {corrected_matches}/{len(predictions)} = {accuracy_corrected:.1f}%")

# Check d_n patterns
print(f"\n5. Error Patterns by d_n:")

errors_by_d = {}
for pred in predictions:
    n = pred['n']
    d_n = D_SEQUENCE[n]
    ratio = pred['predicted'] / pred['actual']

    if d_n not in errors_by_d:
        errors_by_d[d_n] = []
    errors_by_d[d_n].append((n, ratio))

for d_n in sorted(errors_by_d.keys()):
    samples = errors_by_d[d_n]
    ratios_d = [r for n, r in samples]
    print(f"   d={d_n}: {len(samples)} samples, mean ratio={np.mean(ratios_d):.4f}, samples={[(n,f'{r:.2%}') for n,r in samples]}")

# Suggest d-specific corrections
print(f"\n6. D-specific Correction Factors:")
for d_n in sorted(errors_by_d.keys()):
    samples = errors_by_d[d_n]
    ratios_d = [r for n, r in samples]
    correction_d = 1 / np.mean(ratios_d)
    print(f"   d={d_n}: correction={correction_d:.4f}")

# Apply d-specific corrections
print(f"\n7. Results with D-specific Corrections:")
print(f"   {'n':<4} {'Corrected':<15} {'Actual':<15} {'Ratio':<8} {'Match?':<6}")
print("   " + "-" * 60)

d_corrections = {d: 1/np.mean([r for n, r in errors_by_d[d]]) for d in errors_by_d}
d_corrected_matches = 0

for pred in predictions:
    n = pred['n']
    predicted = pred['predicted']
    actual = pred['actual']
    d_n = D_SEQUENCE[n]

    corrected = int(predicted * d_corrections[d_n])
    ratio = corrected / actual if actual != 0 else 0
    match = (corrected == actual)

    if match:
        d_corrected_matches += 1

    print(f"   {n:<4} {corrected:<15,} {actual:<15,} {ratio:<8.2%} {'✅' if match else '❌':<6}")

accuracy_d_corrected = d_corrected_matches / len(predictions) * 100
print(f"\n   Accuracy with d-specific correction: {d_corrected_matches}/{len(predictions)} = {accuracy_d_corrected:.1f}%")

# Save analysis
output = {
    'error_statistics': {
        'mean_ratio': float(np.mean(ratios)),
        'median_ratio': float(np.median(ratios)),
        'std_dev_ratio': float(np.std(ratios)),
        'min_ratio': float(np.min(ratios)),
        'max_ratio': float(np.max(ratios)),
    },
    'correction_factors': {
        'global': float(correction_factor),
        'by_d_n': {int(d): float(c) for d, c in d_corrections.items()}
    },
    'accuracy': {
        'baseline': results['validation']['accuracy_percent'],
        'with_global_correction': float(accuracy_corrected),
        'with_d_specific_correction': float(accuracy_d_corrected)
    }
}

with open('error_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n8. Summary:")
print(f"   Baseline accuracy:           {results['validation']['accuracy_percent']:.1f}%")
print(f"   With global correction:      {accuracy_corrected:.1f}%")
print(f"   With d-specific correction:  {accuracy_d_corrected:.1f}%")
print(f"\n   Saved analysis to: error_analysis.json")
