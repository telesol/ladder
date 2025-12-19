#!/usr/bin/env python3
"""
PySR Training with enhanced prime-related features.

This approach pre-computes prime features instead of using a custom operator.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

try:
    from pysr import PySRRegressor
    PYSR_AVAILABLE = True
except ImportError:
    PYSR_AVAILABLE = False
    print("ERROR: PySR not installed!")

def main():
    print("=" * 70)
    print("PYSR TRAINING WITH ENHANCED PRIME FEATURES")
    print("=" * 70)

    if not PYSR_AVAILABLE:
        return

    # Load enhanced feature matrix
    print("\n1. Loading enhanced feature matrix...")
    df = pd.read_csv('feature_matrix_enhanced.csv')
    print(f"   Loaded {len(df)} samples with {len(df.columns)-1} features")
    print(f"   Features: {list(df.columns[:-1])}")

    # Train/validation split
    print("\n2. Preparing train/validation split...")
    train_df = df[df['n'] <= 25]
    val_df = df[df['n'] > 25]

    # Select most relevant features
    feature_cols = ['n', 'prime_n', 'p7', 'p8', 'p10', 'p7_times_p10',
                    'prev_m', 'prev2_m', 'd_n', 'm_at_d',
                    'p_n_plus_19', 'p_n_plus_9', 'pow2_n', 'p7_times_pn']

    X_train = train_df[feature_cols].values
    y_train = train_df['target_m'].values

    X_val = val_df[feature_cols].values
    y_val = val_df['target_m'].values

    print(f"   Training: {len(X_train)} samples (n=2..25)")
    print(f"   Validation: {len(X_val)} samples (n=26..31)")

    # Configure PySR
    print("\n3. Configuring PySR...")

    model = PySRRegressor(
        niterations=100,
        binary_operators=["+", "*", "-", "/"],
        unary_operators=["square", "cube"],
        populations=40,
        population_size=50,
        ncycles_per_iteration=400,
        maxsize=25,  # Larger to accommodate complex formulas
        parsimony=0.0003,  # Lower simplicity bias
        elementwise_loss="L2DistLoss()",
        verbosity=1,
        progress=True,
        temp_equation_file=True,
        # Full parallelization
        parallelism='multiprocessing',
        procs=20,
    )

    print("   Configuration:")
    print("     - Iterations: 100")
    print("     - Operators: +, *, -, /, square, cube")
    print("     - Max size: 25")
    print("     - Parallelization: 20 cores")

    # Train
    print("\n4. Training PySR...")
    print(f"   Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    with open('STATUS_ENHANCED.txt', 'w') as f:
        f.write('STATUS: TRAINING_ENHANCED\n')
        f.write(f'Started: {datetime.now().isoformat()}\n')

    try:
        model.fit(X_train, y_train, variable_names=feature_cols)

        print(f"   End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Show results
        print("\n5. Best equations found:")
        print(model)

        # Validate
        print("\n6. Validating on holdout set...")
        y_pred = model.predict(X_val)

        exact_matches = 0
        close_matches = 0
        for i, (pred, actual) in enumerate(zip(y_pred, y_val)):
            pred_int = int(round(pred))
            exact = (pred_int == actual)
            close = abs(pred_int - actual) / actual < 0.01  # Within 1%

            if exact:
                exact_matches += 1
            if close:
                close_matches += 1

            n_val = val_df['n'].iloc[i]
            error_pct = abs(pred_int - actual) / actual * 100
            print(f"   n={n_val}: pred={pred_int:>12}, actual={actual:>12}, error={error_pct:>6.2f}%")

        exact_acc = exact_matches / len(y_val) * 100
        close_acc = close_matches / len(y_val) * 100

        print(f"\n   Exact matches: {exact_matches}/{len(y_val)} = {exact_acc:.1f}%")
        print(f"   Within 1%: {close_matches}/{len(y_val)} = {close_acc:.1f}%")

        # Save results
        results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'features': feature_cols,
                'enhanced': True,
            },
            'validation': {
                'exact_matches': int(exact_matches),
                'close_matches': int(close_matches),
                'total': len(y_val),
                'exact_accuracy': float(exact_acc),
                'close_accuracy': float(close_acc),
            },
            'best_equation': str(model.sympy()),
        }

        with open('training_results_enhanced.json', 'w') as f:
            json.dump(results, f, indent=2)

        # Save model
        import pickle
        with open('model_enhanced.pkl', 'wb') as f:
            pickle.dump(model, f)

        with open('STATUS_ENHANCED.txt', 'w') as f:
            f.write(f'STATUS: SUCCESS_EXACT{int(exact_acc)}_CLOSE{int(close_acc)}\n')
            f.write(f'Completed: {datetime.now().isoformat()}\n')

        print("\n" + "=" * 70)
        print("TRAINING COMPLETE")
        print(f"Exact accuracy: {exact_acc:.1f}%")
        print(f"Best equation: {model.sympy()}")
        print("=" * 70)

    except Exception as e:
        print(f"\n   ERROR: {e}")
        with open('STATUS_ENHANCED.txt', 'w') as f:
            f.write(f'STATUS: ERROR\n{str(e)}\n')
        raise

if __name__ == "__main__":
    main()
