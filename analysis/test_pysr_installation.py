#!/usr/bin/env python3
"""
Test PySR Installation
Phase 2.1: Verify PySR environment works
"""

import numpy as np
import os

# Set Julia path
os.environ['PATH'] = f"{os.path.expanduser('~/.juliaup/bin')}:{os.environ.get('PATH', '')}"

print("Testing PySR installation...")
print("=" * 60)

# Import PySR (will trigger Julia package installation on first run)
print("Importing PySR...")
try:
    from pysr import PySRRegressor
    print("✅ PySR imported successfully")
except Exception as e:
    print(f"❌ Failed to import PySR: {e}")
    exit(1)

# Create simple test data: y = 2*x + 3
print("\nCreating test data: y = 2*x + 3")
np.random.seed(42)
X = np.random.randn(100, 1)
y = 2 * X[:, 0] + 3 + 0.1 * np.random.randn(100)

# Simple PySR test
print("\nRunning PySR test (niterations=5, quick test)...")
model = PySRRegressor(
    niterations=5,
    binary_operators=["+", "*"],
    unary_operators=[],
    populations=2,
    population_size=20,
    tournament_selection_n=5,
    verbosity=0,
    progress=False,
    temp_equation_file=False,
)

try:
    model.fit(X, y)
    print("✅ PySR fit completed successfully")

    # Check if it found the equation
    if hasattr(model, 'equations_'):
        print(f"\n📊 Best equation found:")
        best = model.equations_.iloc[-1]
        print(f"   {best['equation']}")
        print(f"   Complexity: {best['complexity']}")
        print(f"   Loss: {best['loss']:.6f}")

    # Make a prediction
    y_pred = model.predict(X[:5])
    print(f"\n✅ Prediction test successful")
    print(f"   First 5 predictions: {y_pred}")

except Exception as e:
    print(f"❌ PySR test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ PySR INSTALLATION VERIFIED")
print("=" * 60)
print("\nEnvironment ready for:")
print("  - Phase 2.2: Define operator sets")
print("  - Phase 2.3: Test with puzzle data")
print("  - Phase 4.2: Full PySR symbolic regression")
