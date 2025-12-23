#!/usr/bin/env python3
"""
Box 213: adj[n] Sign Pattern Discovery
Target: Find formula for adj[n] = k[n] - 2*k[n-1]
Expected: ++- pattern for n=2-16, breaks at n=17, irregular after
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
print("BOX 213: adj[n] SIGN PATTERN DISCOVERY")
print("=" * 80)
print(f"Start time: {datetime.now()}")

# Load data
print("\nLoading puzzle features...")
with open('data/clean/PHASE1_FEATURES_COMPLETE.json', 'r') as f:
    data = json.load(f)

complete = [d for d in data if d['adj_n'] is not None]
print(f"Loaded {len(complete)} puzzles with adj[n] data")

# Extract features: n, hamming_weight, c_n
X_list = []
y_list = []

for d in complete:
    X_list.append([
        d['n'],
        d.get('hamming_weight', 10),
        d.get('c_n', 0.75),
    ])
    y_list.append(d['adj_n'])

X = np.array(X_list)
y = np.array(y_list)

print(f"Feature matrix: {X.shape}")
print(f"Target vector: {y.shape}")
print(f"Target range: [{y.min():.2e}, {y.max():.2e}]")
print(f"Pattern: ++- repeats n=2-16, breaks at n=17")

# PySR Configuration for pattern discovery
print("\nConfiguring PySR for sign pattern...")
print("Operators: CUSTOM (need mod for periodic patterns)")

model = PySRRegressor(
    niterations=100,
    binary_operators=["+", "-", "*", "/", "mod"],
    unary_operators=["square", "abs", "exp", "log", "sqrt", "sign", "sin", "cos"],
    populations=7,
    population_size=45,
    tournament_selection_n=13,
    maxsize=20,
    parsimony=0.008,
    verbosity=1,
    progress=True,
    temp_equation_file=False,
    equation_file="outputs/box213_adj_equations.csv",
)

print("\n" + "=" * 80)
print("STARTING SYMBOLIC REGRESSION (100 iterations)")
print("=" * 80)

try:
    model.fit(X, y)
    print("\n✅ PySR completed successfully!")

    if hasattr(model, 'equations_'):
        equations_df = model.equations_
        equations_df.to_csv('outputs/box213_adj_hall_of_fame.csv', index=False)
        print(f"\n✅ Saved {len(equations_df)} equations")

        print("\n📊 TOP 5 EQUATIONS:")
        top5 = equations_df.nsmallest(5, 'loss')
        for idx, row in top5.iterrows():
            print(f"\n[{row['complexity']}] Loss: {row['loss']:.6e}")
            print(f"   {row['equation']}")

        best = equations_df.iloc[-1]
        print(f"\n🎯 BEST: {best['equation']}")

        import pickle
        with open('outputs/box213_adj_model.pkl', 'wb') as f:
            pickle.dump(model, f)

except Exception as e:
    print(f"\n❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n{'=' * 80}")
print(f"BOX 213 COMPLETE - {datetime.now()}")
print(f"{'=' * 80}")
