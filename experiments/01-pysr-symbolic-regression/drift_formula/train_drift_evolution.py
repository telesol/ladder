#!/usr/bin/env python3
"""
PySR Training Script for Drift Evolution Formula Discovery

Goal: Discover the formula for drift[k][lane] when k > lane×8 (evolution phase)

Context:
- We have 332 evolution drift values from transitions 1→69
- We need to discover a formula to GENERATE drift for transitions 70+
- Formula: X_{k+1}[lane] = ((X_k[lane])^n + drift[k][lane]) mod 256

Key Findings from Data Analysis:
- Evolution drift is NOT quantized (6.3% multiples of 16, not 95%!)
- Lanes are independent (from GPT-OSS analysis)
- Drift appears complex with no obvious modular pattern
- Values range 0-255, relatively uniform distribution

Training Strategy:
1. Start with unified model (all lanes together)
2. Features: k, lane, steps_since_activation, exponent
3. If unified fails, try per-lane models
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import PySR
try:
    from pysr import PySRRegressor
except ImportError:
    print("ERROR: PySR not installed!")
    print("Install with: pip install pysr")
    print("Or use the venv: source experiments/01-pysr-symbolic-regression/.venv/bin/activate")
    sys.exit(1)

# Constants
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

# Load drift data
DATA_FILE = project_root / "drift_data_CORRECT_BYTE_ORDER.json"
print(f"Loading data from: {DATA_FILE}")

with open(DATA_FILE) as f:
    data = json.load(f)

print(f"✓ Loaded {len(data['transitions'])} transitions")
print(f"✓ Total drift values: {data['total_drift_values']}")
print(f"✓ Byte order: {data['byte_order']}")

# Extract evolution values ONLY (k > lane×8)
print("\n=== Extracting Evolution Values ===")

features_list = []
targets_list = []

for trans in data['transitions']:
    k = trans['from_puzzle']

    for lane in range(16):
        activation_k = lane * 8 if lane > 0 else 1

        # EVOLUTION PHASE ONLY
        if k > activation_k:
            drift = trans['drifts'][lane]

            features_list.append({
                'k': k,
                'lane': lane,
                'steps_since_activation': k - activation_k,
                'exponent': EXPONENTS[lane]
            })
            targets_list.append(drift)

# Convert to DataFrame and numpy arrays
df = pd.DataFrame(features_list)
X = df.values  # Features: [k, lane, steps_since_activation, exponent]
y = np.array(targets_list)  # Targets: drift values

print(f"✓ Extracted {len(y)} evolution values")
print(f"✓ Features shape: {X.shape}")
print(f"✓ Target shape: {y.shape}")

# Analyze data
print("\n=== Data Statistics ===")
print(f"Drift range: [{y.min()}, {y.max()}]")
print(f"Drift mean: {y.mean():.2f}")
print(f"Drift std: {y.std():.2f}")
print(f"Multiples of 16: {(y % 16 == 0).sum()}/{len(y)} = {100*(y % 16 == 0).sum()/len(y):.1f}%")

# Per-lane statistics
print("\nPer-lane counts:")
for lane in range(16):
    mask = df['lane'] == lane
    count = mask.sum()
    if count > 0:
        lane_drift = y[mask]
        print(f"  Lane {lane}: {count:3d} values, "
              f"drift ∈ [{lane_drift.min():3d}, {lane_drift.max():3d}], "
              f"mean={lane_drift.mean():.1f}, "
              f"exp={EXPONENTS[lane]}")

# Split into train/validation
# Strategy: Use puzzles 1-55 for training, 56-69 for validation
TRAIN_CUTOFF = 55

train_mask = df['k'] <= TRAIN_CUTOFF
val_mask = df['k'] > TRAIN_CUTOFF

X_train, X_val = X[train_mask], X[val_mask]
y_train, y_val = y[train_mask], y[val_mask]

print(f"\n=== Train/Val Split ===")
print(f"Training: puzzles 1-{TRAIN_CUTOFF} → {len(y_train)} samples")
print(f"Validation: puzzles {TRAIN_CUTOFF+1}-69 → {len(y_val)} samples")

# Configure PySR
print("\n=== Configuring PySR ===")

model = PySRRegressor(
    # Model selection
    model_selection="best",  # Use best model (not accuracy)

    # Operators
    binary_operators=["+", "-", "*", "/", "mod"],
    unary_operators=["square", "cube", "abs"],

    # Complexity
    maxsize=20,  # Maximum expression size
    maxdepth=8,  # Maximum tree depth

    # Search parameters
    niterations=100,  # Number of iterations (increase for longer search)
    populations=15,  # Number of populations
    population_size=33,  # Size of each population

    # Optimization
    ncyclesperiteration=500,  # Cycles per iteration
    fraction_replaced_hof=0.035,  # Fraction of population replaced

    # Constraints
    constraints={
        'mod': 5,  # Penalize mod (expensive operation)
        '/': 5,    # Penalize division (can cause NaN)
    },

    # Batching
    batching=True,
    batch_size=50,

    # Progress
    progress=True,
    verbosity=1,

    # Random seed
    random_state=42,

    # Feature names
    feature_names_in=['k', 'lane', 'steps_since_activation', 'exponent'],

    # Output
    temp_equation_file=True,
)

print("✓ PySR configured")
print(f"  Max size: {model.maxsize}")
print(f"  Max depth: {model.maxdepth}")
print(f"  Iterations: {model.niterations}")
print(f"  Populations: {model.populations}")

# Train model
print("\n=== Training PySR ===")
print("This may take 2-8 hours depending on your CPU...")
print("Press Ctrl+C to stop early (model will be saved)")

try:
    model.fit(X_train, y_train)
    print("\n✅ Training complete!")
except KeyboardInterrupt:
    print("\n⚠️  Training interrupted by user")
except Exception as e:
    print(f"\n❌ Training failed: {e}")
    sys.exit(1)

# Evaluate on validation set
print("\n=== Validation Results ===")

# Predict on validation
y_val_pred = model.predict(X_val)

# Calculate metrics
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

mae = mean_absolute_error(y_val, y_val_pred)
mse = mean_squared_error(y_val, y_val_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_val, y_val_pred)

# Exact match accuracy (for discrete values 0-255)
exact_matches = (np.round(y_val_pred) == y_val).sum()
accuracy = exact_matches / len(y_val)

print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R²: {r2:.4f}")
print(f"Exact matches: {exact_matches}/{len(y_val)} = {100*accuracy:.1f}%")

# Show best equations
print("\n=== Top 5 Equations (by complexity) ===")
print(model)

# Save model
output_dir = Path(__file__).parent / "results"
output_dir.mkdir(exist_ok=True)

model_file = output_dir / "drift_model_unified.pkl"
equations_file = output_dir / "drift_equations_unified.csv"

print(f"\n=== Saving Results ===")
print(f"Model: {model_file}")
print(f"Equations: {equations_file}")

# Save model (pickle)
import pickle
with open(model_file, 'wb') as f:
    pickle.dump(model, f)
print("✓ Model saved")

# Save equations (CSV)
try:
    equations_df = model.equations_
    equations_df.to_csv(equations_file, index=False)
    print("✓ Equations saved")
except Exception as e:
    print(f"⚠️  Could not save equations: {e}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Training samples: {len(y_train)}")
print(f"Validation samples: {len(y_val)}")
print(f"Validation accuracy: {100*accuracy:.1f}%")
print(f"Validation MAE: {mae:.2f}")
print(f"Validation R²: {r2:.4f}")
print("="*60)

# Next steps
print("\nNEXT STEPS:")
print("1. Review equations in:", equations_file)
print("2. Test best equation on full dataset")
print("3. If accuracy < 90%, try per-lane models")
print("4. If accuracy ≥ 90%, proceed to TASK 6 (validation on X_75)")

print("\n✅ Script complete!")
