#!/usr/bin/env python3
"""
PySR Training with custom prime(i) operator.

This script trains PySR with a prime(i) function that returns the i-th prime.
Required for discovering m-sequence formulas which are prime products.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import sympy

try:
    from pysr import PySRRegressor
    PYSR_AVAILABLE = True
except ImportError:
    PYSR_AVAILABLE = False
    print("ERROR: PySR not installed!")

# Custom prime function for sympy mapping
def sympy_prime(x):
    """SymPy mapping for prime(i) function."""
    if hasattr(x, 'is_integer') and x.is_integer and x > 0:
        return sympy.prime(int(x))
    return sympy.Function('prime')(x)

def main():
    print("=" * 70)
    print("PYSR TRAINING WITH PRIME OPERATOR")
    print("=" * 70)

    if not PYSR_AVAILABLE:
        return

    # Load feature matrix
    print("\n1. Loading feature matrix...")
    df = pd.read_csv('feature_matrix.csv')
    print(f"   Loaded {len(df)} samples")

    # Train/validation split
    train_df = df[df['n'] <= 25]
    val_df = df[df['n'] > 25]

    X_train = train_df.drop(['target_m'], axis=1).values
    y_train = train_df['target_m'].values

    X_val = val_df.drop(['target_m'], axis=1).values
    y_val = val_df['target_m'].values

    feature_names = train_df.drop(['target_m'], axis=1).columns.tolist()

    print(f"   Training: {len(X_train)} samples (n=2..25)")
    print(f"   Validation: {len(X_val)} samples (n=26..31)")

    # Configure PySR with prime operator
    print("\n2. Configuring PySR with prime operator...")

    # Define prime function in Julia
    # Uses Primes.jl which should be available in PySR's Julia environment
    prime_julia = """
    function prime_op(x::T) where {T<:Real}
        # Round to nearest integer, clamp to valid range
        i = clamp(round(Int, x), 1, 10000)
        # Return the i-th prime as type T
        return T(Primes.prime(i))
    end
    """

    model = PySRRegressor(
        niterations=50,  # Fewer iterations to test
        binary_operators=["+", "*", "-", "/"],
        unary_operators=[
            "square",
            "cube",
            # Custom prime operator - returns i-th prime
            "prime_op(x::T) where {T} = T(Primes.prime(clamp(round(Int,x),1,10000)))",
        ],
        populations=40,
        population_size=50,
        ncycles_per_iteration=300,
        maxsize=20,  # Larger to accommodate prime combinations
        parsimony=0.0005,  # Less simplicity bias
        elementwise_loss="L2DistLoss()",
        verbosity=1,
        progress=True,
        temp_equation_file=True,
        # Parallelization
        parallelism='multiprocessing',
        procs=20,
        # SymPy mapping for prime function
        extra_sympy_mappings={
            "prime_op": sympy_prime,
        },
        # Complexity: prime is more "expensive" than basic ops
        complexity_of_operators={
            "prime_op": 3,
            "square": 1,
            "cube": 2,
        },
    )

    print("   Configuration:")
    print("     - Operators: +, *, -, /, square, cube, prime_op")
    print("     - Max size: 20")
    print("     - Parallelization: 20 cores")

    # Train
    print("\n3. Training PySR...")
    print(f"   Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    with open('STATUS_PRIME.txt', 'w') as f:
        f.write('STATUS: TRAINING_PRIME\n')
        f.write(f'Started: {datetime.now().isoformat()}\n')

    try:
        model.fit(X_train, y_train, variable_names=feature_names)

        print(f"   End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n   Training complete!")

        # Show results
        print("\n4. Best equations found:")
        print(model)

        # Validate
        print("\n5. Validating...")
        y_pred = model.predict(X_val)

        exact_matches = 0
        for i, (pred, actual) in enumerate(zip(y_pred, y_val)):
            pred_int = int(round(pred))
            match = (pred_int == actual)
            if match:
                exact_matches += 1
            n_val = val_df['n'].iloc[i]
            print(f"   n={n_val}: pred={pred_int:>10}, actual={actual:>10}, match={match}")

        accuracy = exact_matches / len(y_val) * 100
        print(f"\n   Accuracy: {exact_matches}/{len(y_val)} = {accuracy:.1f}%")

        # Save
        results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'has_prime_op': True,
            },
            'validation': {
                'exact_matches': int(exact_matches),
                'total': len(y_val),
                'accuracy_percent': float(accuracy),
            },
            'best_equation': str(model.sympy()),
        }

        with open('training_results_prime.json', 'w') as f:
            json.dump(results, f, indent=2)

        with open('STATUS_PRIME.txt', 'w') as f:
            f.write(f'STATUS: SUCCESS_{int(accuracy)}\n')
            f.write(f'Completed: {datetime.now().isoformat()}\n')

        print("\n" + "=" * 70)
        print("TRAINING COMPLETE")
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Best: {model.sympy()}")
        print("=" * 70)

    except Exception as e:
        print(f"\n   ERROR: {e}")
        with open('STATUS_PRIME.txt', 'w') as f:
            f.write(f'STATUS: ERROR\n{str(e)}\n')
        raise

if __name__ == "__main__":
    main()
