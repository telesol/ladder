#!/usr/bin/env python3
"""
Box 211: c[n] Oscillation Pattern Discovery
Target: Find formula for normalized key position (oscillates 0.5-1.0)
Expected: Periodic function with ~6-step cycle
"""

import json
import numpy as np
import pandas as pd
import os
import sys
from datetime import datetime

# Set Julia path
os.environ['PATH'] = f"{os.path.expanduser('~/.juliaup/bin')}:{os.environ.get('PATH', '')}"

from pysr import PySRRegressor

print("=" * 80)
print("BOX 211: c[n] OSCILLATION PATTERN DISCOVERY")
print("=" * 80)
print(f"Start time: {datetime.now()}")

# Load data
print("\nLoading puzzle features...")
with open('data/clean/PHASE1_FEATURES_COMPLETE.json', 'r') as f:
    data = json.load(f)

complete = [d for d in data if d['c_n'] is not None and d['growth_ratio'] is not None]
print(f"Loaded {len(complete)} puzzles with c[n] data")

# Extract features: n, growth_ratio, c_derivative
X_list = []
y_list = []

for d in complete:
    if d.get('c_derivative') is not None:
        X_list.append([
            d['n'],
            d.get('growth_ratio', 2.0),
            d.get('c_derivative', 0.0)
        ])
        y_list.append(d['c_n'])

X = np.array(X_list)
y = np.array(y_list)

print(f"Feature matrix: {X.shape}")
print(f"Target vector: {y.shape}")
print(f"Target range: [{y.min():.4f}, {y.max():.4f}]")

# PySR Configuration for oscillation discovery
print("\nConfiguring PySR for oscillation pattern...")
print("Operators: FULL set (need trig for periodic patterns)")

model = PySRRegressor(
    niterations=100,
    binary_operators=["+", "-", "*", "/", "mod", "pow"],
    unary_operators=["square", "abs", "exp", "log", "sqrt", "sin", "cos", "cosh", "sinh"],
    populations=8,
    population_size=50,
    tournament_selection_n=15,
    maxsize=25,
    parsimony=0.01,
    verbosity=1,
    progress=True,
    temp_equation_file=False,
    equation_file="outputs/box211_c_n_equations.csv",
)

print("\n" + "=" * 80)
print("STARTING SYMBOLIC REGRESSION (100 iterations, ~30-60 min)")
print("=" * 80)

try:
    model.fit(X, y)
    print("\n✅ PySR completed successfully!")

    # Save results
    if hasattr(model, 'equations_'):
        equations_df = model.equations_
        equations_df.to_csv('outputs/box211_c_n_hall_of_fame.csv', index=False)
        print(f"\n✅ Saved {len(equations_df)} equations to outputs/box211_c_n_hall_of_fame.csv")

        # Show top 5
        print("\n📊 TOP 5 EQUATIONS (by loss):")
        top5 = equations_df.nsmallest(5, 'loss')
        for idx, row in top5.iterrows():
            print(f"\n[Complexity {row['complexity']}] Loss: {row['loss']:.6e}")
            print(f"   {row['equation']}")

        # Best equation
        best = equations_df.iloc[-1]
        print(f"\n🎯 BEST EQUATION (Pareto front):")
        print(f"   {best['equation']}")
        print(f"   Complexity: {best['complexity']}, Loss: {best['loss']:.6e}")

        # Save model
        import pickle
        with open('outputs/box211_c_n_model.pkl', 'wb') as f:
            pickle.dump(model, f)
        print("\n✅ Model saved to outputs/box211_c_n_model.pkl")

except Exception as e:
    print(f"\n❌ PySR failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n{'=' * 80}")
print(f"BOX 211 COMPLETE - {datetime.now()}")
print(f"{'=' * 80}")
