#!/usr/bin/env python3
"""
Validate m-sequence predictions by generating k-values and comparing to bridges.

Strategy:
1. Use our models to predict m-values for n=2..95
2. Generate k-values using master formula: k_n = 2×k_{n-1} + (2^n - m_n × k_{d_n})
3. Compare generated k75, k80, k85, k90, k95 with actual bridge values from CSV
"""

import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

# Load data
with open('convergent_database.py') as f:
    exec(f.read())

# Load CSV to get actual bridge k-values
df_csv = pd.read_csv('../../data/btc_puzzle_1_160_full.csv')

# Bridge indices (currently limited to n<=31 due to D_SEQUENCE availability)
# TODO: Extend D_SEQUENCE to enable bridge validation
# BRIDGES = [75, 80, 85, 90, 95]
BRIDGES = [26, 27, 28, 29, 30, 31]  # Use validation range instead

print("=" * 80)
print("VALIDATE M-SEQUENCE PREDICTIONS ON BITCOIN PUZZLE BRIDGES")
print("=" * 80)

# Load models
print("\n1. Loading models...")
model_global = pickle.load(open('m_sequence_model.pkl', 'rb'))
model_d1 = pickle.load(open('m_sequence_model_d1.pkl', 'rb'))
model_d2 = pickle.load(open('m_sequence_model_d2.pkl', 'rb'))
model_d4 = pickle.load(open('m_sequence_model_d4.pkl', 'rb'))
print("   ✓ Loaded: global, d=1, d=2, d=4 models")

# Helper function to predict m using piecewise model
def predict_m_piecewise(n, prev_m, prev_d, d_n):
    """Predict m_n using piecewise model."""
    features = np.array([[
        n,                    # n
        d_n,                  # d_n
        2**n,                 # power_of_2
        n**2,                 # n_squared
        n**3,                 # n_cubed
        d_n**2,               # d_n_squared
        prev_m,               # prev_m
        prev_d                # prev_d
    ]])

    # Select model based on d_n
    if d_n == 1:
        m_pred = model_d1.predict(features)[0]
    elif d_n == 2:
        m_pred = model_d2.predict(features)[0]
    elif d_n == 4:
        m_pred = model_d4.predict(features)[0]
    else:
        # Fallback to global model for other d values
        m_pred = model_global.predict(features)[0]

    return int(round(m_pred))

def predict_m_global(n, prev_m, prev_d, d_n):
    """Predict m_n using global model."""
    features = np.array([[
        n,                    # n
        d_n,                  # d_n
        2**n,                 # power_of_2
        n**2,                 # n_squared
        n**3,                 # n_cubed
        d_n**2,               # d_n_squared
        prev_m,               # prev_m
        prev_d                # prev_d
    ]])
    m_pred = model_global.predict(features)[0]
    return int(round(m_pred))

# Generate k-values using master formula
def generate_k_values(m_predictor, max_n=95):
    """Generate k-values from n=1 to max_n using predicted m-values."""
    k_values = {1: 1}  # Base case
    m_values = {1: 0}   # m_1 doesn't exist, use 0

    for n in range(2, max_n + 1):
        d_n = D_SEQUENCE[n]

        # Get previous values
        prev_m = m_values.get(n - 1, 0)
        prev_d = D_SEQUENCE.get(n - 1, 0)

        # Predict m_n
        if n <= 31 and n in M_SEQUENCE:
            # Use ground truth for training range
            m_n = M_SEQUENCE[n]
        else:
            # Use predictor for unknown values
            m_n = m_predictor(n, prev_m, prev_d, d_n)

        m_values[n] = m_n

        # Calculate k_n using master formula
        k_prev = k_values[n - 1]

        # Handle circular dependency: when d_n = n
        if d_n == n:
            # k_n = 2×k_{n-1} + (2^n - m_n × k_n)
            # k_n × (1 + m_n) = 2×k_{n-1} + 2^n
            # k_n = (2×k_{n-1} + 2^n) / (1 + m_n)
            k_n = (2 * k_prev + 2**n) // (1 + m_n)
        else:
            k_d = k_values[d_n]
            k_n = 2 * k_prev + (2**n - m_n * k_d)

        k_values[n] = k_n

    return k_values, m_values

print("\n2. Generating k-values using piecewise model...")
k_piecewise, m_piecewise = generate_k_values(predict_m_piecewise, max_n=31)
print("   ✓ Generated k1..k31")

print("\n3. Generating k-values using global model...")
k_global, m_global = generate_k_values(predict_m_global, max_n=31)
print("   ✓ Generated k1..k31")

# Validate on bridges
print("\n" + "=" * 80)
print("BRIDGE VALIDATION RESULTS")
print("=" * 80)

results = []

for n in BRIDGES:
    # Get actual k from CSV
    k_actual_hex = df_csv[df_csv['puzzle'] == n]['key_hex_64'].values[0]
    k_actual = int(k_actual_hex, 16)

    # Get predicted k from both models
    k_pred_piecewise = k_piecewise[n]
    k_pred_global = k_global[n]

    # Compare
    match_piecewise = (k_pred_piecewise == k_actual)
    match_global = (k_pred_global == k_actual)

    # Calculate relative errors
    err_piecewise = abs(k_pred_piecewise - k_actual)
    err_global = abs(k_pred_global - k_actual)
    rel_err_piecewise = 100 * err_piecewise / k_actual if k_actual > 0 else 0
    rel_err_global = 100 * err_global / k_actual if k_actual > 0 else 0

    print(f"\nBridge n={n} (d_n={D_SEQUENCE[n]}):")
    print(f"  Actual k:    {k_actual_hex}")
    print(f"  Piecewise k: {k_pred_piecewise:064x}")
    print(f"  Global k:    {k_pred_global:064x}")
    print(f"  Piecewise:   {'✓ EXACT MATCH!' if match_piecewise else f'✗ Error: {rel_err_piecewise:.2f}%'}")
    print(f"  Global:      {'✓ EXACT MATCH!' if match_global else f'✗ Error: {rel_err_global:.2f}%'}")
    print(f"  Predicted m: {m_piecewise[n]} (piecewise), {m_global[n]} (global)")

    results.append({
        'n': n,
        'd_n': D_SEQUENCE[n],
        'k_actual': k_actual_hex,
        'k_pred_piecewise': f'{k_pred_piecewise:064x}',
        'k_pred_global': f'{k_pred_global:064x}',
        'match_piecewise': bool(match_piecewise),
        'match_global': bool(match_global),
        'rel_err_piecewise_pct': float(rel_err_piecewise),
        'rel_err_global_pct': float(rel_err_global),
        'm_pred_piecewise': int(m_piecewise[n]),
        'm_pred_global': int(m_global[n])
    })

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

exact_piecewise = sum(1 for r in results if r['match_piecewise'])
exact_global = sum(1 for r in results if r['match_global'])
total = len(results)

print(f"\nPiecewise model: {exact_piecewise}/{total} exact matches ({100*exact_piecewise/total:.1f}%)")
print(f"Global model:    {exact_global}/{total} exact matches ({100*exact_global/total:.1f}%)")

avg_err_piecewise = np.mean([r['rel_err_piecewise_pct'] for r in results])
avg_err_global = np.mean([r['rel_err_global_pct'] for r in results])

print(f"\nPiecewise model: {avg_err_piecewise:.2f}% average relative error")
print(f"Global model:    {avg_err_global:.2f}% average relative error")

# Save results
with open('bridge_validation_results.json', 'w') as f:
    json.dump({
        'summary': {
            'piecewise_exact_matches': exact_piecewise,
            'global_exact_matches': exact_global,
            'total_bridges': total,
            'piecewise_accuracy_pct': 100 * exact_piecewise / total,
            'global_accuracy_pct': 100 * exact_global / total,
            'piecewise_avg_rel_error_pct': float(avg_err_piecewise),
            'global_avg_rel_error_pct': float(avg_err_global)
        },
        'bridges': results
    }, f, indent=2)

print("\n✅ Results saved to: bridge_validation_results.json")

# Final verdict
print("\n" + "=" * 80)
print("VERDICT")
print("=" * 80)

if exact_piecewise == total:
    print("\n🎉 PERFECT! Piecewise model generates exact Bitcoin keys!")
    print("   → Can proceed to generate puzzles 32-160")
elif exact_global == total:
    print("\n🎉 PERFECT! Global model generates exact Bitcoin keys!")
    print("   → Can proceed to generate puzzles 32-160")
elif exact_piecewise > 0 or exact_global > 0:
    print(f"\n⚠️  PARTIAL SUCCESS: Some bridges match, but not all")
    print("   → Models capture pattern but need refinement")
elif avg_err_piecewise < 1 or avg_err_global < 1:
    print(f"\n👍 CLOSE: <1% average error on bridges")
    print("   → Models are very close, need small corrections")
elif avg_err_piecewise < 10 or avg_err_global < 10:
    print(f"\n🤔 APPROXIMATE: {min(avg_err_piecewise, avg_err_global):.1f}% average error")
    print("   → Models capture trend but need different approach")
else:
    print(f"\n❌ POOR: >{min(avg_err_piecewise, avg_err_global):.1f}% average error")
    print("   → Need to revisit assumptions about m-sequence generation")
