#!/usr/bin/env python3
"""
Box 212: d_gap Linear Relationship Discovery
Target: Find formula for d[n] = n - d_gap (how far back to reference)
Expected: Nearly linear (correlation 0.9956), possibly piecewise
"""

import json
import numpy as np
import pandas as pd
import os
import sys
from datetime import datetime

os.environ['PATH'] = f"{os.path.expanduser('~/.juliaup/bin')}:{os.environ.get('PATH', '')}"

from pysr import PySRRegressor

print("=" * 80)
print("BOX 212: d_gap LINEAR RELATIONSHIP DISCOVERY")
print("=" * 80)
print(f"Start time: {datetime.now()}")

# Load data
print("\nLoading puzzle features...")
with open('data/clean/PHASE1_FEATURES_COMPLETE.json', 'r') as f:
    data = json.load(f)

complete = [d for d in data if d['d_gap'] is not None]
print(f"Loaded {len(complete)} puzzles with d_gap data")

# Extract features: n, m_log10 (if available)
X_list = []
y_list = []

for d in complete:
    X_list.append([
        d['n'],
        d.get('m_log10', 10.0),  # Default if missing
    ])
    y_list.append(d['d_gap'])

X = np.array(X_list)
y = np.array(y_list)

print(f"Feature matrix: {X.shape}")
print(f"Target vector: {y.shape}")
print(f"Target range: [{y.min():.1f}, {y.max():.1f}]")
print(f"Expected: d_gap ≈ 0.986*n - 1.824")

# PySR Configuration for linear/piecewise discovery
print("\nConfiguring PySR for linear patterns...")
print("Operators: MINIMAL + floor/ceil (for piecewise)")

model = PySRRegressor(
    niterations=100,
    binary_operators=["+", "-", "*", "/"],
    unary_operators=["abs", "floor", "ceil", "sign"],
    populations=6,
    population_size=40,
    tournament_selection_n=12,
    maxsize=15,
    parsimony=0.005,
    verbosity=1,
    progress=True,
    temp_equation_file=False,
    equation_file="outputs/box212_d_gap_equations.csv",
)

print("\n" + "=" * 80)
print("STARTING SYMBOLIC REGRESSION (100 iterations)")
print("=" * 80)

try:
    model.fit(X, y)
    print("\n✅ PySR completed successfully!")

    if hasattr(model, 'equations_'):
        equations_df = model.equations_
        equations_df.to_csv('outputs/box212_d_gap_hall_of_fame.csv', index=False)
        print(f"\n✅ Saved {len(equations_df)} equations")

        print("\n📊 TOP 5 EQUATIONS:")
        top5 = equations_df.nsmallest(5, 'loss')
        for idx, row in top5.iterrows():
            print(f"\n[{row['complexity']}] Loss: {row['loss']:.6e}")
            print(f"   {row['equation']}")

        best = equations_df.iloc[-1]
        print(f"\n🎯 BEST: {best['equation']}")
        print(f"   Complexity: {best['complexity']}, Loss: {best['loss']:.6e}")

        import pickle
        with open('outputs/box212_d_gap_model.pkl', 'wb') as f:
            pickle.dump(model, f)

except Exception as e:
    print(f"\n❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n{'=' * 80}")
print(f"BOX 212 COMPLETE - {datetime.now()}")
print(f"{'=' * 80}")
