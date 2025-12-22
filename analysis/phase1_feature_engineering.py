#!/usr/bin/env python3
"""
Phase 1: Feature Engineering for PySR Training
Orchestrator: Claude (Sonnet 4.5)
Date: 2025-12-22

This script calculates advanced features for symbolic regression:
- Phase 1.1: Inter-key relationships (ratios, differences, growth)
- Phase 1.2: Oscillation patterns (derivatives, envelopes)
- Phase 1.3: d-minimization analysis
"""

import json
import csv
import math
import numpy as np
from collections import defaultdict

print("=" * 80)
print("PHASE 1: FEATURE ENGINEERING FOR PYSR")
print("=" * 80)

# Load clean features
with open('data/clean/FEATURES_ALL_82.json', 'r') as f:
    data = json.load(f)

# Separate complete and incomplete features
complete = [d for d in data if d['adj_n'] is not None]
all_data = data

print(f"\nLoaded {len(all_data)} puzzles ({len(complete)} with complete features)")

# ============================================================================
# PHASE 1.1: INTER-KEY RELATIONSHIPS
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 1.1: INTER-KEY RELATIONSHIPS")
print("=" * 80)

features_1_1 = []

for i, d in enumerate(all_data):
    n = d['n']
    k_n = d['k_n']
    c_n = d['c_n']

    feat = {
        'n': n,
        'k_n': k_n,
        'c_n': c_n,
        'log2_k': math.log2(k_n) if k_n > 0 else None,
        'bits_used': k_n.bit_length(),
        'bits_expected': n,
    }

    # Growth ratio: k[n] / k[n-1]
    if i > 0 and all_data[i-1]['n'] == n - 1:
        k_prev = all_data[i-1]['k_n']
        feat['growth_ratio'] = k_n / k_prev if k_prev > 0 else None
        feat['growth_log2'] = math.log2(k_n / k_prev) if k_prev > 0 else None
        feat['k_diff'] = k_n - k_prev
        feat['c_diff'] = c_n - all_data[i-1]['c_n']
    else:
        feat['growth_ratio'] = None
        feat['growth_log2'] = None
        feat['k_diff'] = None
        feat['c_diff'] = None

    # Position in range [2^(n-1), 2^n)
    range_min = 2 ** (n - 1)
    range_max = 2 ** n
    feat['position_in_range'] = (k_n - range_min) / (range_max - range_min)

    # Distance from boundaries
    feat['dist_from_min'] = k_n - range_min
    feat['dist_from_max'] = range_max - k_n
    feat['min_dist_log2'] = math.log2(feat['dist_from_min']) if feat['dist_from_min'] > 0 else None

    # Mathematical properties
    feat['is_prime'] = None  # Too expensive to check for large k
    feat['hamming_weight'] = bin(k_n).count('1')  # Number of 1-bits
    feat['trailing_zeros'] = (k_n & -k_n).bit_length() - 1  # Number of trailing zeros

    features_1_1.append(feat)

print(f"\n✅ Calculated {len(features_1_1)} feature vectors")
print(f"\nSample features (n=10):")
for feat in features_1_1[:11]:
    if feat['n'] == 10:
        print(f"  n={feat['n']}: growth_ratio={feat['growth_ratio']:.4f}, c_diff={feat['c_diff']:.6f}, hamming_weight={feat['hamming_weight']}")

# Statistics
growth_ratios = [f['growth_ratio'] for f in features_1_1 if f['growth_ratio'] is not None]
print(f"\nGrowth ratio statistics:")
print(f"  Min: {min(growth_ratios):.4f}")
print(f"  Max: {max(growth_ratios):.4f}")
print(f"  Mean: {np.mean(growth_ratios):.4f}")
print(f"  Median: {np.median(growth_ratios):.4f}")

# ============================================================================
# PHASE 1.2: OSCILLATION PATTERN ENCODING
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 1.2: OSCILLATION PATTERN ENCODING")
print("=" * 80)

features_1_2 = []

# Calculate c[n] derivatives (rate of change)
c_values = [d['c_n'] for d in all_data]
n_values = [d['n'] for d in all_data]

for i, d in enumerate(all_data):
    n = d['n']
    c_n = d['c_n']

    feat = {
        'n': n,
        'c_n': c_n,
    }

    # First derivative (slope)
    if i > 0 and n_values[i-1] == n - 1:
        feat['c_derivative'] = c_values[i] - c_values[i-1]
    else:
        feat['c_derivative'] = None

    # Second derivative (acceleration)
    if i > 1 and n_values[i-1] == n - 1 and n_values[i-2] == n - 2:
        deriv1 = c_values[i] - c_values[i-1]
        deriv0 = c_values[i-1] - c_values[i-2]
        feat['c_acceleration'] = deriv1 - deriv0
    else:
        feat['c_acceleration'] = None

    # Oscillation phase (approximate)
    # Simple heuristic: if c is increasing, phase = 0-90, if decreasing, phase = 90-180
    if feat['c_derivative'] is not None:
        if feat['c_derivative'] > 0:
            feat['oscillation_phase'] = 'UP'
        elif feat['c_derivative'] < 0:
            feat['oscillation_phase'] = 'DOWN'
        else:
            feat['oscillation_phase'] = 'FLAT'
    else:
        feat['oscillation_phase'] = None

    # Distance from mean c
    mean_c = np.mean(c_values)
    feat['c_deviation_from_mean'] = c_n - mean_c

    # Local envelope (max/min in window)
    window = 5
    start_idx = max(0, i - window)
    end_idx = min(len(c_values), i + window + 1)
    local_c = c_values[start_idx:end_idx]
    feat['local_c_max'] = max(local_c)
    feat['local_c_min'] = min(local_c)
    feat['c_in_local_range'] = (c_n - feat['local_c_min']) / (feat['local_c_max'] - feat['local_c_min']) if feat['local_c_max'] > feat['local_c_min'] else 0.5

    features_1_2.append(feat)

print(f"\n✅ Calculated {len(features_1_2)} oscillation features")

# Phase pattern for gap puzzles
print(f"\nGap puzzle oscillation phases:")
for n in [70, 75, 80, 85, 90]:
    feat = next((f for f in features_1_2 if f['n'] == n), None)
    if feat:
        c_deriv_str = f"{feat['c_derivative']:.6f}" if feat['c_derivative'] is not None else 'N/A'
        print(f"  n={n}: phase={feat['oscillation_phase']}, c_derivative={c_deriv_str}")

# Count UP vs DOWN phases
up_count = sum(1 for f in features_1_2 if f['oscillation_phase'] == 'UP')
down_count = sum(1 for f in features_1_2 if f['oscillation_phase'] == 'DOWN')
print(f"\nOverall phase distribution:")
print(f"  UP: {up_count} ({100*up_count/(up_count+down_count):.1f}%)")
print(f"  DOWN: {down_count} ({100*down_count/(up_count+down_count):.1f}%)")

# ============================================================================
# PHASE 1.3: D-MINIMIZATION ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 1.3: D-MINIMIZATION ANALYSIS")
print("=" * 80)

features_1_3 = []

for d in complete:
    n = d['n']
    d_n = d['d_n']
    m_n = d['m_n']
    adj_n = d['adj_n']
    k_n = d['k_n']

    feat = {
        'n': n,
        'd_n': d_n,
        'm_n': m_n,
        'adj_n': adj_n,
    }

    # d properties
    feat['d_gap'] = n - d_n  # How far back does d reference?
    feat['d_ratio'] = d_n / n  # Relative position

    # m properties
    feat['m_log10'] = math.log10(m_n) if m_n > 0 else None
    feat['m_bits'] = m_n.bit_length()

    # adj properties
    feat['adj_sign'] = '+' if adj_n > 0 else '-' if adj_n < 0 else '0'
    feat['adj_magnitude_log10'] = math.log10(abs(adj_n)) if adj_n != 0 else None

    # Divisibility: How many previous k values can divide (2^n - adj[n])?
    numerator = (2 ** n) - adj_n
    divisor_count = 0
    for other in complete:
        if other['n'] < n:
            if numerator % other['k_n'] == 0:
                divisor_count += 1

    feat['num_valid_divisors'] = divisor_count

    # k[d[n]] magnitude relative to k[n]
    k_d = next((x['k_n'] for x in all_data if x['n'] == d_n), None)
    if k_d:
        feat['k_d_ratio'] = k_d / k_n
        feat['k_d_log_ratio'] = math.log10(k_d / k_n) if k_d > 0 and k_n > 0 else None
    else:
        feat['k_d_ratio'] = None
        feat['k_d_log_ratio'] = None

    features_1_3.append(feat)

print(f"\n✅ Calculated {len(features_1_3)} d-minimization features")

# d-gap distribution
d_gaps = [f['d_gap'] for f in features_1_3]
print(f"\nd-gap statistics (how far back d[n] references):")
print(f"  Min: {min(d_gaps)}")
print(f"  Max: {max(d_gaps)}")
print(f"  Mean: {np.mean(d_gaps):.2f}")
print(f"  Median: {np.median(d_gaps):.1f}")

# Correlation: d_gap vs n
print(f"\nd_gap correlation with n:")
correlation = np.corrcoef([f['n'] for f in features_1_3], d_gaps)[0, 1]
print(f"  Pearson correlation: {correlation:.4f}")
if abs(correlation) > 0.5:
    print(f"  → STRONG correlation: d_gap {'increases' if correlation > 0 else 'decreases'} with n")
elif abs(correlation) > 0.3:
    print(f"  → MODERATE correlation")
else:
    print(f"  → WEAK correlation (d_gap relatively independent of n)")

# ============================================================================
# SAVE COMBINED FEATURES
# ============================================================================
print("\n" + "=" * 80)
print("SAVING COMBINED FEATURES")
print("=" * 80)

# Merge all features by n
combined = []
for d in all_data:
    n = d['n']

    entry = {
        'n': n,
        'k_n': d['k_n'],
        'c_n': d['c_n'],
        'adj_n': d['adj_n'],
        'd_n': d['d_n'],
        'm_n': d['m_n'],
    }

    # Add Phase 1.1 features
    feat_1_1 = next((f for f in features_1_1 if f['n'] == n), None)
    if feat_1_1:
        entry.update({k: v for k, v in feat_1_1.items() if k not in ['n', 'k_n', 'c_n']})

    # Add Phase 1.2 features
    feat_1_2 = next((f for f in features_1_2 if f['n'] == n), None)
    if feat_1_2:
        entry.update({k: v for k, v in feat_1_2.items() if k not in ['n', 'c_n']})

    # Add Phase 1.3 features
    feat_1_3 = next((f for f in features_1_3 if f['n'] == n), None)
    if feat_1_3:
        entry.update({k: v for k, v in feat_1_3.items() if k not in ['n', 'd_n', 'm_n', 'adj_n']})

    combined.append(entry)

# Save to JSON
with open('data/clean/PHASE1_FEATURES_COMPLETE.json', 'w') as f:
    json.dump(combined, f, indent=2)

# Save to CSV (for easier inspection)
# Collect all unique fieldnames
all_fields = set()
for entry in combined:
    all_fields.update(entry.keys())
all_fields = sorted(all_fields)  # Sort for consistent ordering

with open('data/clean/PHASE1_FEATURES_COMPLETE.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=all_fields)
    writer.writeheader()
    writer.writerows(combined)

print(f"\n✅ Saved combined features:")
print(f"   - data/clean/PHASE1_FEATURES_COMPLETE.json")
print(f"   - data/clean/PHASE1_FEATURES_COMPLETE.csv")
print(f"   Total features: {len(combined[0])} columns")
print(f"   Total puzzles: {len(combined)}")

# ============================================================================
# FEATURE IMPORTANCE HINTS
# ============================================================================
print("\n" + "=" * 80)
print("FEATURE IMPORTANCE HINTS FOR PYSR")
print("=" * 80)

print("""
Based on Phase 1 analysis, these features are likely important for PySR:

HIGH PRIORITY:
- c_n: Normalized position (verified oscillation pattern)
- adj_n: Adjustment from doubling (++- pattern for n=2-16)
- d_gap: How far back d[n] references (varies with n)
- growth_ratio: k[n]/k[n-1] (growth pattern)
- c_derivative: Rate of c[n] change (oscillation direction)

MEDIUM PRIORITY:
- hamming_weight: Number of 1-bits in k[n]
- position_in_range: Where k[n] sits in [2^(n-1), 2^n)
- m_log10: Magnitude of m[n]
- oscillation_phase: UP/DOWN/FLAT indicator

LOW PRIORITY:
- trailing_zeros: Artifact of representation
- local_c_max/min: Noisy local statistics

OPERATOR SUGGESTIONS FOR PYSR:
- Basic: +, -, *, /, mod
- Trigonometric: sin, cos (for oscillation)
- Exponential: exp, log, log2
- Hyperbolic: cosh, sinh (from Wave 3 closed-form)
- Custom: floor, ceiling (for integer constraints)
""")

print("\n" + "=" * 80)
print("PHASE 1 FEATURE ENGINEERING COMPLETE")
print("=" * 80)
