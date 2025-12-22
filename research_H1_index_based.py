#!/usr/bin/env python3
"""
Hypothesis 1 (H1): Pure Index-Based Generator

Theory: drift[k→k+1][lane] = f(k, lane)

Tests:
1. Statistical correlation between drift and (k, lane)
2. Polynomial fits per lane
3. Modular arithmetic patterns
4. PySR symbolic regression (if available)

Machine: Spark 1
Expected time: 2-3 hours
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
import sys

def load_data(json_path="drift_data_export.json"):
    """Load drift data from export file"""
    print(f"[1/6] Loading data from {json_path}")
    with open(json_path) as f:
        data = json.load(f)

    transitions = data['transitions']
    print(f"  ✓ Loaded {len(transitions)} transitions ({len(transitions)*16} drift values)")
    return data

def statistical_analysis(data):
    """Analyze correlation between drift and (k, lane)"""
    print("\n[2/6] Statistical Analysis: Correlation with (k, lane)")

    transitions = data['transitions']

    # Organize data by lane
    by_lane = defaultdict(list)

    for trans in transitions:
        k = trans['from_puzzle']
        for lane in range(16):
            drift = trans['drifts'][lane]
            by_lane[lane].append((k, drift))

    # Analyze each lane
    results = {}
    for lane in range(16):
        pairs = by_lane[lane]
        k_values = np.array([p[0] for p in pairs])
        drift_values = np.array([p[1] for p in pairs])

        # Check if drift is constant
        unique_drifts = np.unique(drift_values)
        is_constant = len(unique_drifts) == 1

        # Check if drift is monotonic with k
        is_monotonic = np.all(np.diff(drift_values) >= 0) or np.all(np.diff(drift_values) <= 0)

        # Calculate correlation (if not constant)
        if len(unique_drifts) > 1:
            correlation = np.corrcoef(k_values, drift_values)[0, 1]
        else:
            correlation = 0.0

        results[lane] = {
            'is_constant': is_constant,
            'constant_value': drift_values[0] if is_constant else None,
            'is_monotonic': is_monotonic,
            'correlation': correlation,
            'unique_values': len(unique_drifts),
            'drift_range': (int(np.min(drift_values)), int(np.max(drift_values)))
        }

        if is_constant:
            print(f"  Lane {lane:2d}: CONSTANT = {drift_values[0]}")
        else:
            print(f"  Lane {lane:2d}: varying ({unique_drifts.size} values), "
                  f"range={results[lane]['drift_range']}, corr={correlation:.3f}")

    return results

def polynomial_fits(data):
    """Test polynomial fits: drift = a*k^2 + b*k + c (per lane)"""
    print("\n[3/6] Polynomial Fits (per lane)")

    transitions = data['transitions']
    by_lane = defaultdict(list)

    for trans in transitions:
        k = trans['from_puzzle']
        for lane in range(16):
            drift = trans['drifts'][lane]
            by_lane[lane].append((k, drift))

    results = {}

    for lane in range(16):
        pairs = by_lane[lane]
        k_values = np.array([p[0] for p in pairs])
        drift_values = np.array([p[1] for p in pairs])

        # Skip constant lanes
        if len(np.unique(drift_values)) == 1:
            results[lane] = {'accuracy': 1.0, 'formula': f'constant({drift_values[0]})'}
            continue

        # Try different polynomial degrees
        best_accuracy = 0.0
        best_degree = 0
        best_coeffs = None

        for degree in [1, 2, 3, 4]:
            # Fit polynomial
            coeffs = np.polyfit(k_values, drift_values, degree)
            poly = np.poly1d(coeffs)

            # Predict and evaluate (mod 256)
            predictions = poly(k_values) % 256
            matches = np.sum(predictions.astype(int) == drift_values)
            accuracy = matches / len(drift_values)

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_degree = degree
                best_coeffs = coeffs

        results[lane] = {
            'accuracy': best_accuracy,
            'degree': best_degree,
            'coefficients': best_coeffs.tolist() if best_coeffs is not None else None,
            'formula': f'poly_deg{best_degree}' if best_degree > 0 else 'constant'
        }

        print(f"  Lane {lane:2d}: degree={best_degree}, accuracy={best_accuracy*100:.1f}%")

    # Overall accuracy
    total_correct = sum(r['accuracy'] * 69 for r in results.values())
    overall_accuracy = total_correct / (69 * 16)
    print(f"\n  Overall polynomial accuracy: {overall_accuracy*100:.2f}%")

    return results, overall_accuracy

def modular_patterns(data):
    """Test modular arithmetic patterns"""
    print("\n[4/6] Modular Arithmetic Patterns")

    transitions = data['transitions']

    # Test: drift[k][lane] = (k * multiplier + offset) mod 256
    by_lane = defaultdict(list)

    for trans in transitions:
        k = trans['from_puzzle']
        for lane in range(16):
            drift = trans['drifts'][lane]
            by_lane[lane].append((k, drift))

    results = {}

    for lane in range(16):
        pairs = by_lane[lane]

        best_accuracy = 0.0
        best_params = None

        # Try different multipliers and offsets
        for mult in range(256):
            for offset in range(256):
                predictions = [(mult * k + offset) % 256 for k, _ in pairs]
                actuals = [d for _, d in pairs]
                matches = sum(1 for p, a in zip(predictions, actuals) if p == a)
                accuracy = matches / len(pairs)

                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_params = (mult, offset)

        results[lane] = {
            'accuracy': best_accuracy,
            'multiplier': best_params[0] if best_params else None,
            'offset': best_params[1] if best_params else None
        }

        if best_accuracy == 1.0:
            print(f"  Lane {lane:2d}: 100% match! drift = ({best_params[0]}*k + {best_params[1]}) mod 256")
        elif best_accuracy > 0.8:
            print(f"  Lane {lane:2d}: {best_accuracy*100:.1f}% match, mult={best_params[0]}, offset={best_params[1]}")

    # Overall accuracy
    overall_accuracy = sum(r['accuracy'] for r in results.values()) / 16
    print(f"\n  Overall modular accuracy: {overall_accuracy*100:.2f}%")

    return results, overall_accuracy

def pysr_symbolic_regression(data):
    """Use PySR for symbolic regression (if available)"""
    print("\n[5/6] PySR Symbolic Regression (Optional)")

    try:
        from pysr import PySRRegressor
        print("  ✓ PySR available, starting symbolic regression...")

        transitions = data['transitions']

        # Prepare data: features = (k, lane), target = drift
        X = []
        y = []

        for trans in transitions:
            k = trans['from_puzzle']
            for lane in range(16):
                X.append([k, lane])
                y.append(trans['drifts'][lane])

        X = np.array(X)
        y = np.array(y)

        print(f"  Training on {len(X)} samples...")

        # Configure PySR
        model = PySRRegressor(
            niterations=40,
            binary_operators=["+", "*", "-", "/", "%"],
            unary_operators=["square", "cube"],
            populations=8,
            population_size=33,
            maxsize=20,
            ncyclesperiteration=550,
            verbosity=0,
            progress=True
        )

        # Train
        model.fit(X, y)

        # Evaluate
        predictions = model.predict(X) % 256
        accuracy = np.mean(predictions.astype(int) == y)

        print(f"\n  PySR accuracy: {accuracy*100:.2f}%")
        print(f"  Best equation: {model.latex()}")

        return {
            'available': True,
            'accuracy': accuracy,
            'equation': str(model.latex())
        }

    except ImportError:
        print("  ⚠ PySR not installed (pip install pysr)")
        return {'available': False}
    except Exception as e:
        print(f"  ⚠ PySR error: {e}")
        return {'available': False, 'error': str(e)}

def generate_report(data, stats, poly_results, poly_acc, mod_results, mod_acc, pysr_result):
    """Generate final report"""
    print("\n[6/6] Generating Report")

    # Find best approach
    approaches = [
        ('Polynomial', poly_acc),
        ('Modular', mod_acc)
    ]

    if pysr_result.get('available'):
        approaches.append(('PySR', pysr_result['accuracy']))

    best_approach = max(approaches, key=lambda x: x[1])

    report = {
        'hypothesis': 'H1: Pure Index-Based Generator',
        'theory': 'drift[k][lane] = f(k, lane)',
        'results': {
            'statistical_analysis': stats,
            'polynomial_fits': {
                'overall_accuracy': poly_acc,
                'per_lane': poly_results
            },
            'modular_arithmetic': {
                'overall_accuracy': mod_acc,
                'per_lane': mod_results
            },
            'pysr': pysr_result
        },
        'best_approach': {
            'name': best_approach[0],
            'accuracy': best_approach[1]
        },
        'conclusion': 'SUCCESS' if best_approach[1] == 1.0 else
                     'PROMISING' if best_approach[1] > 0.9 else
                     'PARTIAL' if best_approach[1] > 0.7 else 'FAILED'
    }

    # Save report
    output_path = Path("H1_results.json")
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"  ✓ Report saved to: {output_path}")

    # Print summary
    print("\n" + "="*60)
    print("H1 HYPOTHESIS SUMMARY")
    print("="*60)
    print(f"Best approach:  {best_approach[0]}")
    print(f"Accuracy:       {best_approach[1]*100:.2f}%")
    print(f"Conclusion:     {report['conclusion']}")
    print("="*60)

    if best_approach[1] == 1.0:
        print("\n🎉 SUCCESS! Generator found: drift = f(k, lane)")
    elif best_approach[1] > 0.9:
        print("\n🔥 Very close! This hypothesis is promising.")
    elif best_approach[1] > 0.7:
        print("\n👍 Partial success. May need hybrid approach.")
    else:
        print("\n🤔 Hypothesis unlikely. Try other approaches.")

    return report

def main():
    # Check if data file exists
    data_file = Path("drift_data_export.json")
    if not data_file.exists():
        print(f"❌ Error: {data_file} not found!")
        print("Please run export_drift_data.py first.")
        sys.exit(1)

    # Load data
    data = load_data(data_file)

    # Run analyses
    stats = statistical_analysis(data)
    poly_results, poly_acc = polynomial_fits(data)
    mod_results, mod_acc = modular_patterns(data)
    pysr_result = pysr_symbolic_regression(data)

    # Generate report
    report = generate_report(data, stats, poly_results, poly_acc, mod_results, mod_acc, pysr_result)

    print("\n✅ H1 research complete!")

if __name__ == '__main__':
    main()
