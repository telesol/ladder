#!/usr/bin/env python3
"""
PySR Training: Discover m-sequence generation formula using symbolic regression.

This script trains PySR on the convergent-based feature matrix to discover
the mathematical formula for generating m-values.
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
    print("WARNING: PySR not installed. Install with: pip install pysr")

def main():
    print("=" * 70)
    print("PYSR TRAINING: m-sequence Formula Discovery")
    print("=" * 70)

    if not PYSR_AVAILABLE:
        print("\nERROR: PySR is not installed!")
        print("Install with: pip install pysr")
        print("Or: conda install -c conda-forge pysr")
        return

    # Step 1: Load feature matrix
    print("\n1. Loading feature matrix...")
    df = pd.read_csv('feature_matrix.csv')
    print(f"   Loaded {len(df)} samples with {len(df.columns)-1} features")

    # Step 2: Prepare train/validation split
    print("\n2. Preparing train/validation split...")

    # Train on n=2..25 (24 samples)
    # Validate on n=26..31 (6 samples)
    train_df = df[df['n'] <= 25]
    val_df = df[df['n'] > 25]

    X_train = train_df.drop(['target_m'], axis=1).values
    y_train = train_df['target_m'].values

    X_val = val_df.drop(['target_m'], axis=1).values
    y_val = val_df['target_m'].values

    feature_names = train_df.drop(['target_m'], axis=1).columns.tolist()

    print(f"   Training set: {len(X_train)} samples (n=2..25)")
    print(f"   Validation set: {len(X_val)} samples (n=26..31)")
    print(f"   Features: {len(feature_names)}")

    # Step 3: Configure PySR
    print("\n3. Configuring PySR...")

    model = PySRRegressor(
        niterations=100,  # Number of iterations
        binary_operators=["+", "*", "-", "/"],
        unary_operators=["square", "cube"],
        populations=30,
        population_size=50,
        ncycles_per_iteration=500,
        maxsize=15,  # Max formula complexity
        parsimony=0.001,  # Simplicity bias
        elementwise_loss="L2DistLoss()",
        verbosity=1,  # Print progress
        progress=True,
        temp_equation_file=True,
    )

    print("   Configuration:")
    print(f"     - Iterations: 100")
    print(f"     - Binary operators: +, *, -, /")
    print(f"     - Unary operators: square, cube")
    print(f"     - Max formula size: 15")
    print(f"     - Populations: 30 × 50")

    # Step 4: Train PySR
    print("\n4. Training PySR (this will take 2-4 hours)...")
    print(f"   Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    with open('STATUS.txt', 'w') as f:
        f.write('STATUS: TRAINING\n')
        f.write(f'Started: {datetime.now().isoformat()}\n')

    try:
        model.fit(X_train, y_train, variable_names=feature_names)

        print(f"   End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n   Training complete!")

        # Step 5: Show best equations
        print("\n5. Best equations found:")
        print(model)

        # Step 6: Validate on holdout set
        print("\n6. Validating on holdout set (n=26..31)...")

        y_pred = model.predict(X_val)

        # Check exact matches (integer accuracy)
        exact_matches = 0
        for i, (pred, actual) in enumerate(zip(y_pred, y_val)):
            pred_int = int(round(pred))
            match = (pred_int == actual)
            if match:
                exact_matches += 1

            n_val = val_df['n'].iloc[i]
            print(f"   n={n_val}: predicted={pred_int:>10}, actual={actual:>10}, match={match}")

        accuracy = exact_matches / len(y_val) * 100
        print(f"\n   Exact match accuracy: {exact_matches}/{len(y_val)} = {accuracy:.1f}%")

        # Step 7: Save results
        print("\n7. Saving results...")

        results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'features': len(feature_names),
            },
            'validation': {
                'exact_matches': int(exact_matches),
                'total': len(y_val),
                'accuracy_percent': float(accuracy),
                'predictions': [
                    {
                        'n': int(val_df['n'].iloc[i]),
                        'predicted': int(round(y_pred[i])),
                        'actual': int(y_val[i]),
                        'match': bool(int(round(y_pred[i])) == y_val[i])
                    }
                    for i in range(len(y_val))
                ]
            },
            'best_equation': str(model.sympy()),
            'best_score': float(model.score(X_val, y_val)),
        }

        with open('training_results.json', 'w') as f:
            json.dump(results, f, indent=2)

        # Save the model
        model.save('m_sequence_model.pkl')

        # Update status
        with open('STATUS.txt', 'w') as f:
            f.write(f'STATUS: SUCCESS_{int(accuracy)}\n')
            f.write(f'Completed: {datetime.now().isoformat()}\n')
            f.write(f'Accuracy: {accuracy:.1f}%\n')

        print(f"   Saved results to: training_results.json")
        print(f"   Saved model to: m_sequence_model.pkl")

        # Step 8: Show summary
        print("\n" + "=" * 70)
        print("TRAINING COMPLETE")
        print("=" * 70)
        print(f"\nValidation Accuracy: {accuracy:.1f}%")
        print(f"\nBest Formula: {model.sympy()}")

        if accuracy == 100.0:
            print("\n🎉 PERFECT ACCURACY! Formula discovered!")
            print("Next step: Run generate_full_sequence.py")
        elif accuracy >= 90:
            print("\n🔥 Very strong formula! Close to solution.")
            print("Next step: Refine or use hybrid approach")
        elif accuracy >= 80:
            print("\n👍 Good progress! Formula captures major patterns.")
            print("Next step: Analyze mismatches and refine")
        else:
            print("\n🤔 Partial success. Formula provides insights.")
            print("Next step: Try phase-based training or different features")

    except Exception as e:
        print(f"\n   ERROR during training: {e}")
        with open('STATUS.txt', 'w') as f:
            f.write('STATUS: ERROR\n')
            f.write(f'Error: {str(e)}\n')
        raise

if __name__ == "__main__":
    main()
