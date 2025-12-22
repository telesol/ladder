#!/usr/bin/env python3
"""
Hypothesis 4 (H4): Recursive Pattern (Drift Ladder)

Theory: Drift follows its own recurrence relation
    drift[k+1][lane] = g(drift[k][lane], k, lane)

Drift might have a ladder too!

Tests:
1. Analyze drift sequences per lane
2. Look for recurrence patterns
3. Test affine recurrence: drift_next = A_drift * drift_current + C_drift (mod 256)
4. Test polynomial recurrence
5. Check for fixed points and cycles
6. Test bridge spacing pattern: drift[k] = drift[k-5] + constant

Machine: ASUS B10 #2
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

def analyze_drift_sequences(data):
    """Analyze drift sequences per lane"""
    print("\n[2/6] Analyzing Drift Sequences (per lane)")

    transitions = data['transitions']

    # Organize by lane
    by_lane = defaultdict(list)

    for trans in sorted(transitions, key=lambda t: t['from_puzzle']):
        for lane in range(16):
            by_lane[lane].append(trans['drifts'][lane])

    results = {}

    for lane in range(16):
        sequence = by_lane[lane]

        # Check if constant
        unique_vals = len(set(sequence))

        # Check for cycles
        cycle_found = False
        cycle_length = 0

        for period in range(2, min(20, len(sequence) // 2)):
            is_cycle = True
            for i in range(period, len(sequence)):
                if sequence[i] != sequence[i % period]:
                    is_cycle = False
                    break
            if is_cycle:
                cycle_found = True
                cycle_length = period
                break

        # Check for arithmetic progression
        if len(sequence) > 1:
            diffs = [sequence[i+1] - sequence[i] for i in range(len(sequence)-1)]
            is_arithmetic = len(set(diffs)) == 1
            common_diff = diffs[0] if is_arithmetic else None
        else:
            is_arithmetic = False
            common_diff = None

        results[lane] = {
            'unique_values': unique_vals,
            'is_constant': unique_vals == 1,
            'has_cycle': cycle_found,
            'cycle_length': cycle_length if cycle_found else None,
            'is_arithmetic': is_arithmetic,
            'common_difference': common_diff
        }

        if results[lane]['is_constant']:
            print(f"  Lane {lane:2d}: CONSTANT")
        elif results[lane]['has_cycle']:
            print(f"  Lane {lane:2d}: CYCLE detected (period={cycle_length})")
        elif results[lane]['is_arithmetic']:
            print(f"  Lane {lane:2d}: ARITHMETIC PROGRESSION (diff={common_diff})")
        else:
            print(f"  Lane {lane:2d}: Complex pattern ({unique_vals} unique values)")

    return results

def test_affine_recurrence(data):
    """Test affine recurrence: drift[k+1] = A * drift[k] + C (mod 256)"""
    print("\n[3/6] Testing Affine Recurrence")

    transitions = data['transitions']

    # Organize by lane
    by_lane = defaultdict(list)

    for trans in sorted(transitions, key=lambda t: t['from_puzzle']):
        for lane in range(16):
            by_lane[lane].append(trans['drifts'][lane])

    results = {}

    for lane in range(16):
        sequence = by_lane[lane]

        if len(set(sequence)) == 1:
            # Constant sequence
            results[lane] = {'accuracy': 1.0, 'A': 1, 'C': 0, 'formula': 'constant'}
            continue

        # Try to find A and C
        best_accuracy = 0.0
        best_A = None
        best_C = None

        # Brute force search for A and C
        for A in range(256):
            for C in range(256):
                matches = 0

                for i in range(len(sequence) - 1):
                    predicted = (A * sequence[i] + C) % 256
                    if predicted == sequence[i + 1]:
                        matches += 1

                accuracy = matches / (len(sequence) - 1)

                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_A = A
                    best_C = C

                if accuracy == 1.0:
                    break
            if best_accuracy == 1.0:
                break

        results[lane] = {
            'accuracy': best_accuracy,
            'A': best_A,
            'C': best_C,
            'formula': f'drift_next = ({best_A} * drift + {best_C}) mod 256'
        }

        if best_accuracy == 1.0:
            print(f"  Lane {lane:2d}: 100% match! A={best_A}, C={best_C}")
        elif best_accuracy > 0.8:
            print(f"  Lane {lane:2d}: {best_accuracy*100:.1f}% match, A={best_A}, C={best_C}")

    # Overall accuracy
    overall_accuracy = sum(r['accuracy'] for r in results.values()) / 16
    print(f"\n  Overall affine recurrence accuracy: {overall_accuracy*100:.2f}%")

    return results, overall_accuracy

def test_polynomial_recurrence(data):
    """Test polynomial recurrence: drift[k+1] = f(drift[k])"""
    print("\n[4/6] Testing Polynomial Recurrence")

    transitions = data['transitions']

    # Organize by lane
    by_lane = defaultdict(list)

    for trans in sorted(transitions, key=lambda t: t['from_puzzle']):
        for lane in range(16):
            by_lane[lane].append(trans['drifts'][lane])

    results = {}

    for lane in range(16):
        sequence = by_lane[lane]

        if len(set(sequence)) == 1:
            results[lane] = {'accuracy': 1.0, 'degree': 0}
            continue

        # Try polynomial fits
        best_accuracy = 0.0
        best_degree = 0

        for degree in [2, 3, 4]:
            matches = 0

            for i in range(len(sequence) - 1):
                # Compute polynomial mod 256
                val = sequence[i]
                predicted = (val ** degree) % 256

                if predicted == sequence[i + 1]:
                    matches += 1

            accuracy = matches / (len(sequence) - 1)

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_degree = degree

        results[lane] = {
            'accuracy': best_accuracy,
            'degree': best_degree,
            'formula': f'drift_next = drift^{best_degree} mod 256'
        }

        if best_accuracy == 1.0:
            print(f"  Lane {lane:2d}: 100% match! drift^{best_degree} mod 256")
        elif best_accuracy > 0.8:
            print(f"  Lane {lane:2d}: {best_accuracy*100:.1f}% match, drift^{best_degree}")

    # Overall accuracy
    overall_accuracy = sum(r['accuracy'] for r in results.values()) / 16
    print(f"\n  Overall polynomial recurrence accuracy: {overall_accuracy*100:.2f}%")

    return results, overall_accuracy

def test_bridge_spacing_pattern(data):
    """Test if drift follows bridge spacing: drift[k] relates to drift[k-5]"""
    print("\n[5/6] Testing Bridge Spacing Pattern")

    transitions = data['transitions']

    # Organize by lane
    by_lane = defaultdict(list)

    for trans in sorted(transitions, key=lambda t: t['from_puzzle']):
        k = trans['from_puzzle']
        for lane in range(16):
            by_lane[lane].append((k, trans['drifts'][lane]))

    results = {}

    for lane in range(16):
        pairs = by_lane[lane]

        # Test: drift[k] = drift[k-5] + constant (mod 256)
        best_accuracy = 0.0
        best_spacing = 0
        best_offset = 0

        for spacing in [5, 10, 15, 20]:  # Test different spacings
            for offset in range(256):
                matches = 0
                total = 0

                # Build lookup dict
                drift_dict = {k: d for k, d in pairs}

                for k, drift in pairs:
                    if (k - spacing) in drift_dict:
                        predicted = (drift_dict[k - spacing] + offset) % 256
                        if predicted == drift:
                            matches += 1
                        total += 1

                if total > 0:
                    accuracy = matches / total

                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_spacing = spacing
                        best_offset = offset

        results[lane] = {
            'accuracy': best_accuracy,
            'spacing': best_spacing,
            'offset': best_offset
        }

        if best_accuracy == 1.0:
            print(f"  Lane {lane:2d}: 100% match! drift[k] = drift[k-{best_spacing}] + {best_offset}")
        elif best_accuracy > 0.8:
            print(f"  Lane {lane:2d}: {best_accuracy*100:.1f}% match, spacing={best_spacing}")

    # Overall accuracy
    overall_accuracy = sum(r['accuracy'] for r in results.values()) / 16
    print(f"\n  Overall bridge spacing accuracy: {overall_accuracy*100:.2f}%")

    return results, overall_accuracy

def test_multi_step_recurrence(data):
    """Test multi-step recurrence: drift[k+1] = f(drift[k], drift[k-1], ...)"""
    print("\n[6/6] Testing Multi-Step Recurrence")

    transitions = data['transitions']

    # Organize by lane
    by_lane = defaultdict(list)

    for trans in sorted(transitions, key=lambda t: t['from_puzzle']):
        for lane in range(16):
            by_lane[lane].append(trans['drifts'][lane])

    results = {}

    for lane in range(16):
        sequence = by_lane[lane]

        if len(set(sequence)) == 1:
            results[lane] = {'accuracy': 1.0, 'formula': 'constant'}
            continue

        # Test: drift[k+1] = (drift[k] + drift[k-1]) mod 256 (Fibonacci-like)
        if len(sequence) >= 3:
            matches = 0

            for i in range(1, len(sequence) - 1):
                predicted = (sequence[i] + sequence[i - 1]) % 256
                if predicted == sequence[i + 1]:
                    matches += 1

            fib_accuracy = matches / (len(sequence) - 2)
        else:
            fib_accuracy = 0.0

        # Test: drift[k+1] = (2*drift[k] - drift[k-1]) mod 256 (linear extrapolation)
        if len(sequence) >= 3:
            matches = 0

            for i in range(1, len(sequence) - 1):
                predicted = (2 * sequence[i] - sequence[i - 1]) % 256
                if predicted == sequence[i + 1]:
                    matches += 1

            linear_accuracy = matches / (len(sequence) - 2)
        else:
            linear_accuracy = 0.0

        best_accuracy = max(fib_accuracy, linear_accuracy)
        best_formula = 'fibonacci' if fib_accuracy > linear_accuracy else 'linear'

        results[lane] = {
            'accuracy': best_accuracy,
            'formula': best_formula,
            'fib_accuracy': fib_accuracy,
            'linear_accuracy': linear_accuracy
        }

        if best_accuracy == 1.0:
            print(f"  Lane {lane:2d}: 100% match! {best_formula}")
        elif best_accuracy > 0.8:
            print(f"  Lane {lane:2d}: {best_accuracy*100:.1f}% match, {best_formula}")

    # Overall accuracy
    overall_accuracy = sum(r['accuracy'] for r in results.values()) / 16
    print(f"\n  Overall multi-step accuracy: {overall_accuracy*100:.2f}%")

    return results, overall_accuracy

def generate_report(data, seq_analysis, affine_results, affine_acc, poly_results, poly_acc,
                   bridge_results, bridge_acc, multi_results, multi_acc):
    """Generate final report"""
    print("\n[7/7] Generating Report")

    # Find best approach
    approaches = [
        ('Affine Recurrence', affine_acc),
        ('Polynomial Recurrence', poly_acc),
        ('Bridge Spacing', bridge_acc),
        ('Multi-Step', multi_acc)
    ]

    best = max(approaches, key=lambda x: x[1])

    report = {
        'hypothesis': 'H4: Recursive Pattern (Drift Ladder)',
        'theory': 'drift[k+1][lane] = g(drift[k][lane], k, lane)',
        'results': {
            'sequence_analysis': seq_analysis,
            'affine_recurrence': {
                'overall_accuracy': affine_acc,
                'per_lane': affine_results
            },
            'polynomial_recurrence': {
                'overall_accuracy': poly_acc,
                'per_lane': poly_results
            },
            'bridge_spacing': {
                'overall_accuracy': bridge_acc,
                'per_lane': bridge_results
            },
            'multi_step': {
                'overall_accuracy': multi_acc,
                'per_lane': multi_results
            }
        },
        'best_approach': {
            'name': best[0],
            'accuracy': best[1]
        },
        'conclusion': 'SUCCESS' if best[1] == 1.0 else
                     'PROMISING' if best[1] > 0.9 else
                     'PARTIAL' if best[1] > 0.7 else 'FAILED'
    }

    # Save report
    output_path = Path("H4_results.json")
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"  ✓ Report saved to: {output_path}")

    # Print summary
    print("\n" + "="*60)
    print("H4 HYPOTHESIS SUMMARY")
    print("="*60)
    print(f"Best approach:  {best[0]}")
    print(f"Accuracy:       {best[1]*100:.2f}%")
    print(f"Conclusion:     {report['conclusion']}")
    print("="*60)

    if best[1] == 1.0:
        print("\n🎉 SUCCESS! Drift has its own ladder!")
    elif best[1] > 0.9:
        print("\n🔥 Very close! This hypothesis is promising.")
    elif best[1] > 0.7:
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
    seq_analysis = analyze_drift_sequences(data)
    affine_results, affine_acc = test_affine_recurrence(data)
    poly_results, poly_acc = test_polynomial_recurrence(data)
    bridge_results, bridge_acc = test_bridge_spacing_pattern(data)
    multi_results, multi_acc = test_multi_step_recurrence(data)

    # Generate report
    report = generate_report(data, seq_analysis, affine_results, affine_acc,
                           poly_results, poly_acc, bridge_results, bridge_acc,
                           multi_results, multi_acc)

    print("\n✅ H4 research complete!")

if __name__ == '__main__':
    main()
