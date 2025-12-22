#!/usr/bin/env python3
"""
Phase 3.1: Train PySR on a single lane (Proof of Concept)

Discovers symbolic formula for one lane to verify the approach works.
"""

import argparse
import json
import numpy as np
from pathlib import Path

def modular_loss(y_true, y_pred):
    """Custom loss function for modular arithmetic (mod 256)."""
    diff = np.abs(y_true - y_pred)
    # Handle wraparound: min(diff, 256 - diff)
    return np.minimum(diff, 256 - diff)

def train_lane(lane_id, iterations=1000, verbose=True):
    """Train PySR symbolic regression on a single lane."""
    print(f"\n{'='*60}")
    print(f"Training Lane {lane_id} - Symbolic Regression")
    print(f"{'='*60}")

    # Load data
    data_dir = Path(__file__).parent.parent / "data" / "lanes"
    X = np.load(data_dir / f"lane_{lane_id:02d}_X.npy")
    y = np.load(data_dir / f"lane_{lane_id:02d}_y.npy")

    print(f"📊 Data loaded:")
    print(f"   X shape: {X.shape} (previous values)")
    print(f"   y shape: {y.shape} (next values)")
    print(f"   Sample X[0:3]: {X[0:3].flatten()}")
    print(f"   Sample y[0:3]: {y[0:3]}")

    # Import PySR
    try:
        from pysr import PySRRegressor
    except ImportError:
        print("\n❌ PySR not found!")
        print("   Install with: pip install pysr")
        print("   Then run: python3 -c 'import pysr; pysr.install()'")
        return None

    print(f"\n🔬 Configuring PySR...")

    # Configure PySR for modular arithmetic pattern discovery
    model = PySRRegressor(
        niterations=iterations,
        populations=15,
        population_size=33,
        binary_operators=["+", "*"],
        unary_operators=["square", "cube"],
        # Note: PySR doesn't directly support mod operator in search
        # We'll post-process results to apply mod 256
        maxsize=20,
        parsimony=0.001,
        model_selection="best",
        timeout_in_seconds=None,
        verbosity=1 if verbose else 0,
        random_state=42,
        # Constraints
        constraints={
            'square': 5,  # Max complexity for square
            'cube': 5,    # Max complexity for cube
        },
        denoise=True,
        select_k_features=1,  # Only use X (single feature)
    )

    print(f"   Iterations: {iterations}")
    print(f"   Populations: 15")
    print(f"   Operators: +, *, square, cube")
    print(f"   Target formula form: a*x^k + c (mod 256)")

    print(f"\n🚀 Starting symbolic regression...")
    print(f"   This may take 30-60 minutes for {iterations} iterations")
    print(f"   Progress will be shown below:\n")

    # Train
    model.fit(X, y)

    print(f"\n✅ Training complete!")

    # Get best equation
    print(f"\n📋 Discovered equations (top 5):")
    print(model)

    # Get the best equation
    best_eq = model.get_best()
    print(f"\n🏆 Best equation:")
    print(f"   Complexity: {best_eq['complexity']}")
    print(f"   Loss: {best_eq['loss']:.6f}")
    print(f"   Equation: {best_eq['equation']}")

    # Try to get sympy representation
    try:
        sympy_eq = model.sympy()
        print(f"   SymPy form: {sympy_eq}")
    except:
        sympy_eq = None

    # Evaluate on training data
    y_pred_raw = model.calculate(X)

    # Apply mod 256 to calculations
    y_pred = y_pred_raw.astype(int) % 256

    # Compute accuracy (exact matches)
    exact_matches = np.sum(y_pred == y)
    accuracy = exact_matches / len(y) * 100

    # Compute modular loss
    losses = modular_loss(y, y_pred)
    mean_loss = np.mean(losses)

    print(f"\n📊 Training Performance:")
    print(f"   Exact matches: {exact_matches}/{len(y)} ({accuracy:.2f}%)")
    print(f"   Mean modular loss: {mean_loss:.4f}")

    if accuracy < 95:
        print(f"\n⚠️  Accuracy below 95% - may need more iterations or different constraints")
    else:
        print(f"\n✅ Good accuracy! Formula likely captures the pattern.")

    # Try to extract A and C coefficients
    print(f"\n🔍 Attempting to extract coefficients...")

    # Save results
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Save formula
    formula_file = results_dir / f"lane_{lane_id:02d}_formula.txt"
    with open(formula_file, 'w') as f:
        f.write(f"Lane {lane_id} - Discovered Formula\n")
        f.write(f"=" * 40 + "\n\n")
        f.write(f"Best equation: {best_eq['equation']}\n")
        if sympy_eq:
            f.write(f"SymPy form: {sympy_eq}\n")
        f.write(f"\nComplexity: {best_eq['complexity']}\n")
        f.write(f"Loss: {best_eq['loss']:.6f}\n")
        f.write(f"Accuracy: {accuracy:.2f}%\n")
        f.write(f"Mean modular loss: {mean_loss:.4f}\n")

    print(f"💾 Saved formula to: {formula_file}")

    # Save detailed results
    results = {
        'lane': lane_id,
        'equation': str(best_eq['equation']),
        'sympy': str(sympy_eq) if sympy_eq else None,
        'complexity': int(best_eq['complexity']),
        'loss': float(best_eq['loss']),
        'accuracy': float(accuracy),
        'mean_modular_loss': float(mean_loss),
        'exact_matches': int(exact_matches),
        'total_samples': int(len(y)),
        'iterations': iterations,
    }

    results_file = results_dir / f"lane_{lane_id:02d}_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"💾 Saved results to: {results_file}")

    return model, results

def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train PySR on a single lane")
    parser.add_argument('--lane', type=int, default=0, help='Lane ID (0-15)')
    parser.add_argument('--iterations', type=int, default=1000, help='Number of iterations')
    parser.add_argument('--quiet', action='store_true', help='Reduce verbosity')

    args = parser.parse_args()

    if args.lane < 0 or args.lane > 15:
        print(f"❌ Lane must be between 0 and 15, got {args.lane}")
        return

    model, results = train_lane(args.lane, args.iterations, verbose=not args.quiet)

    if results:
        print(f"\n{'='*60}")
        print(f"✅ Lane {args.lane} Training Complete!")
        print(f"{'='*60}")
        print(f"\nNext steps:")
        print(f"1. Review results in: experiments/01-pysr-symbolic-regression/results/")
        print(f"2. If accuracy is good (>95%), run all lanes:")
        print(f"   python3 scripts/train_all_lanes.py")
        print(f"3. If accuracy is low, try:")
        print(f"   - More iterations: --iterations 2000")
        print(f"   - Different lane: --lane 1")
    else:
        print("\n❌ Training failed - check PySR installation")

if __name__ == "__main__":
    main()
