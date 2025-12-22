#!/usr/bin/env python3
"""
Phase 5: Validate Discovered Formulas

Tests discovered formulas on:
1. Validation set (puzzles 61-70)
2. Test set (bridge rows 75, 80, 85, 90, 95)
3. Full forward calculation
"""

import json
import numpy as np
from pathlib import Path

# Exponent pattern discovered by PySR
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

def apply_formula(x, exponent):
    """Apply discovered formula: f(x) = x^n (mod 256)."""
    if exponent == 0:
        return 0
    else:
        return int(x ** exponent) % 256

def predict_next(current_puzzle, exponents):
    """Calculate next puzzle given current puzzle."""
    next_puzzle = np.zeros(len(current_puzzle), dtype=int)

    # We only have exponents for first 16 lanes (first half-block)
    # Second half (lanes 16-31) we'll keep as zeros for now
    num_lanes = min(len(exponents), len(current_puzzle))

    for lane in range(num_lanes):
        next_puzzle[lane] = apply_formula(current_puzzle[lane], exponents[lane])

    # Lanes 16-31: keep as zero (second half not trained yet)
    # This is expected since we trained on half-blocks

    return next_puzzle

def validate_on_set(matrix, set_name, exponents):
    """Validate formulas on a dataset."""
    print(f"\n{'='*70}")
    print(f"Validating on {set_name}")
    print(f"{'='*70}")

    total_transitions = len(matrix) - 1
    num_lanes = len(exponents)  # Only validate first 16 lanes we trained
    total_bytes = total_transitions * num_lanes
    correct_bytes = 0
    correct_transitions = 0

    per_lane_correct = np.zeros(num_lanes, dtype=int)
    per_lane_total = np.zeros(num_lanes, dtype=int)

    for i in range(total_transitions):
        current = matrix[i]
        actual_next = matrix[i + 1]

        predicted_next = predict_next(current, exponents)

        # Count correct bytes (only first 16 lanes)
        matches = (predicted_next[:num_lanes] == actual_next[:num_lanes])
        correct_bytes += np.sum(matches)

        # Count correct transitions (all trained lanes match)
        if np.all(matches):
            correct_transitions += 1

        # Per-lane accuracy
        per_lane_correct += matches.astype(int)
        per_lane_total += 1

    # Overall accuracy
    byte_accuracy = (correct_bytes / total_bytes) * 100
    transition_accuracy = (correct_transitions / total_transitions) * 100

    print(f"\n📊 Results:")
    print(f"   Byte-level accuracy: {correct_bytes}/{total_bytes} ({byte_accuracy:.2f}%)")
    print(f"   Transition accuracy: {correct_transitions}/{total_transitions} ({transition_accuracy:.2f}%)")

    # Per-lane breakdown
    print(f"\n📋 Per-Lane Accuracy (first {num_lanes} lanes only):")
    all_perfect = True
    for lane in range(num_lanes):
        lane_acc = (per_lane_correct[lane] / per_lane_total[lane]) * 100
        status = "✅" if lane_acc == 100.0 else "❌"
        print(f"   Lane {lane:2d} (x^{exponents[lane]}): {per_lane_correct[lane]}/{per_lane_total[lane]} ({lane_acc:6.2f}%) {status}")

        if lane_acc < 100.0:
            all_perfect = False

    if all_perfect:
        print(f"\n✅ PERFECT! All lanes 100% accurate on {set_name}")
    else:
        print(f"\n⚠️  Some lanes failed on {set_name}")

    return {
        'set_name': set_name,
        'byte_accuracy': float(byte_accuracy),
        'transition_accuracy': float(transition_accuracy),
        'correct_bytes': int(correct_bytes),
        'total_bytes': int(total_bytes),
        'correct_transitions': int(correct_transitions),
        'total_transitions': int(total_transitions),
        'per_lane_accuracy': [float((per_lane_correct[i] / per_lane_total[i]) * 100) for i in range(num_lanes)],
        'all_perfect': all_perfect
    }

def test_multi_step_prediction(matrix, steps, exponents):
    """Test multi-step forward calculation (for bridge rows)."""
    print(f"\n{'='*70}")
    print(f"Multi-Step Calculation Test ({steps} steps)")
    print(f"{'='*70}")

    # Start from first puzzle
    current = matrix[0].copy()
    calculations = [current]

    print(f"\n🚀 Calculating {steps} steps forward...")
    for step in range(steps):
        current = predict_next(current, exponents)
        calculations.append(current)
        print(f"   Step {step+1}/{steps} complete")

    # Compare final calculation with actual
    if steps < len(matrix):
        actual_final = matrix[steps]
        predicted_final = calculations[-1]

        matches = (predicted_final[:16] == actual_final[:16])  # Only check first 16 lanes
        accuracy = (np.sum(matches) / 16) * 100

        print(f"\n📊 {steps}-Step Calculation Accuracy: {np.sum(matches)}/16 ({accuracy:.2f}%)")

        if accuracy == 100.0:
            print(f"✅ Perfect multi-step calculation!")
        else:
            print(f"❌ Multi-step calculation has errors")
            print(f"\n   Lane mismatches:")
            for lane in range(16):
                if not matches[lane]:
                    print(f"      Lane {lane:2d}: calculated={predicted_final[lane]}, actual={actual_final[lane]}")

        return accuracy == 100.0
    else:
        print(f"⚠️  Cannot validate {steps}-step calculation (not enough data)")
        return None

def main():
    """Main validation pipeline."""
    print("=" * 70)
    print("Phase 5: Formula Validation")
    print("=" * 70)

    data_dir = Path(__file__).parent.parent / "data"

    # Load datasets
    print(f"\n📂 Loading datasets...")
    train_matrix = np.load(data_dir / "train_matrix.npy")
    val_matrix = np.load(data_dir / "val_matrix.npy")
    test_matrix = np.load(data_dir / "test_matrix.npy")

    print(f"   Training: {train_matrix.shape}")
    print(f"   Validation: {val_matrix.shape}")
    print(f"   Test: {test_matrix.shape}")

    print(f"\n🔢 Using discovered exponent pattern:")
    print(f"   {EXPONENTS}")

    # Validate on training set (should be 100%)
    train_results = validate_on_set(train_matrix, "Training Set (Puzzles 1-60)", EXPONENTS)

    # Validate on validation set
    val_results = validate_on_set(val_matrix, "Validation Set (Puzzles 61-70)", EXPONENTS)

    # Validate on test set (bridge rows)
    test_results = validate_on_set(test_matrix, "Test Set (Bridge Rows 75-95)", EXPONENTS)

    # Multi-step calculation test
    # Bridge rows are 5 steps apart, so test 5-step calculation
    multi_step_5_perfect = test_multi_step_prediction(train_matrix, 5, EXPONENTS)

    # Summary
    print(f"\n" + "=" * 70)
    print(f"Validation Summary")
    print(f"=" * 70)

    all_results = [train_results, val_results, test_results]

    print(f"\n📊 Overall Accuracy:")
    for result in all_results:
        status = "✅" if result['all_perfect'] else "❌"
        print(f"   {result['set_name']:<40} {result['transition_accuracy']:>6.2f}% {status}")

    # Save results
    results_dir = Path(__file__).parent.parent / "results"
    validation_file = results_dir / "validation_results.json"

    validation_summary = {
        'training': train_results,
        'validation': val_results,
        'test': test_results,
        'multi_step_5': bool(multi_step_5_perfect) if multi_step_5_perfect is not None else None,
        'exponents_used': EXPONENTS,
        'overall_success': bool(all([r['all_perfect'] for r in all_results]))
    }

    with open(validation_file, 'w') as f:
        json.dump(validation_summary, f, indent=2)

    print(f"\n💾 Results saved to: {validation_file}")

    # Final verdict
    print(f"\n" + "=" * 70)
    if validation_summary['overall_success']:
        print(f"🎉 SUCCESS! 100% accuracy on ALL datasets!")
        print(f"=" * 70)
        print(f"\n✅ Discovered formula is CONFIRMED:")
        print(f"   X_{{k+1}}(ℓ) = X_k(ℓ)^n (mod 256)")
        print(f"   Where n = {EXPONENTS}")
        print(f"\n📋 Next steps:")
        print(f"   1. Generate missing puzzles (71-74, 76-79, etc.)")
        print(f"   2. Reconstruct full ladder (1-160)")
        print(f"   3. Export to database format")
    else:
        print(f"⚠️  VALIDATION INCOMPLETE")
        print(f"=" * 70)
        print(f"\nSome datasets showed errors. Review results above.")
        print(f"Possible issues:")
        print(f"   - Formula doesn't generalize beyond training data")
        print(f"   - Multi-step calculation accumulates errors")
        print(f"   - Different pattern for higher puzzles")

if __name__ == "__main__":
    main()
