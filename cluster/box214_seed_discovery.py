#!/usr/bin/env python3
"""
Box 214: Seed Pattern Discovery (Mathematical Constants)
Target: Find relationships in m[n] encoding π, e, φ convergents
Expected: Early values (n=4,8,9,10,16) embed mathematical structure
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
print("BOX 214: SEED PATTERN DISCOVERY (π, e, φ)")
print("=" * 80)
print(f"Start time: {datetime.now()}")

# Load data - focus on early values with known patterns
print("\nLoading puzzle features...")
with open('data/clean/PHASE1_FEATURES_COMPLETE.json', 'r') as f:
    data = json.load(f)

# Filter to n <= 30 (where mathematical constants appear)
complete = [d for d in data if d.get('m_n') is not None and d['n'] <= 30]
print(f"Loaded {len(complete)} early puzzles (n≤30)")

# Extract features: n, k_n, m_n relationships
X_list = []
y_list = []

for d in complete:
    X_list.append([
        d['n'],
        np.log10(d.get('k_n', 1)),
    ])
    y_list.append(np.log10(d['m_n']))  # Log scale for better fitting

X = np.array(X_list)
y = np.array(y_list)

print(f"Feature matrix: {X.shape}")
print(f"Target: log10(m[n])")
print(f"Known patterns:")
print(f"  m[4]=22 (22/7≈π), m[8]=23, m[9]=493, m[10]=19, m[16]=8470")

# PySR Configuration for constant discovery
print("\nConfiguring PySR for mathematical constants...")
print("Operators: STANDARD + special constants")

model = PySRRegressor(
    niterations=100,
    binary_operators=["+", "-", "*", "/", "mod"],
    unary_operators=["exp", "log", "sqrt", "square", "abs"],
    populations=6,
    population_size=40,
    tournament_selection_n=12,
    maxsize=18,
    parsimony=0.01,
    verbosity=1,
    progress=True,
    temp_equation_file=False,
    equation_file="outputs/box214_seed_equations.csv",
)

print("\n" + "=" * 80)
print("STARTING SYMBOLIC REGRESSION (100 iterations)")
print("=" * 80)

try:
    model.fit(X, y)
    print("\n✅ PySR completed successfully!")

    if hasattr(model, 'equations_'):
        equations_df = model.equations_
        equations_df.to_csv('outputs/box214_seed_hall_of_fame.csv', index=False)
        print(f"\n✅ Saved {len(equations_df)} equations")

        print("\n📊 TOP 5 EQUATIONS:")
        top5 = equations_df.nsmallest(5, 'loss')
        for idx, row in top5.iterrows():
            print(f"\n[{row['complexity']}] Loss: {row['loss']:.6e}")
            print(f"   {row['equation']}")

        best = equations_df.iloc[-1]
        print(f"\n🎯 BEST: {best['equation']}")

        import pickle
        with open('outputs/box214_seed_model.pkl', 'wb') as f:
            pickle.dump(model, f)

except Exception as e:
    print(f"\n❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n{'=' * 80}")
print(f"BOX 214 COMPLETE - {datetime.now()}")
print(f"{'=' * 80}")
