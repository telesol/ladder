#!/usr/bin/env python3
"""
PROOF: Test Hybrid Drift Generator on KNOWN Data (Puzzles 1-70)

This proves our discovered formulas work by testing on data we can verify.
"""

import json

def load_calibration():
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        return json.load(f)

def load_h4_params():
    with open('results/H4_results.json', 'r') as f:
        return json.load(f)

def predict_drift_hybrid(k, lane, drift_prev, h4_params):
    """
    Hybrid predictor using discovered formulas
    """
    # TRIVIAL LANES (9-15): Always 0
    if lane >= 9:
        return 0

    # LANE 8 (k<64): Always 0
    if lane == 8 and k < 64:
        return 0

    # LANE 7 (k<64): K-based formula
    if lane == 7 and k < 64:
        value = ((k / 30.0) - 0.905) ** 32 * 0.596
        return int(value) % 256

    # LANES 0-8: H4 Affine Recurrence
    if h4_params and str(lane) in h4_params['results']['affine_recurrence']['per_lane']:
        lane_params = h4_params['results']['affine_recurrence']['per_lane'][str(lane)]
        A = lane_params['A']
        C = lane_params['C']
        return (A * drift_prev + C) % 256

    return 0

def main():
    print("="*80)
    print("PROOF: Hybrid Drift Generator on Known Data (1-70)")
    print("="*80)
    print()

    calib = load_calibration()
    h4_params = load_h4_params()

    # Track per-lane accuracy
    lane_correct = [0] * 16
    lane_total = [0] * 16

    # Track drift_prev for recursive lanes
    drift_prev = [0] * 16

    # Test all 69 transitions
    for k in range(1, 70):
        trans_key = f'{k}→{k+1}'

        if trans_key not in calib['drifts']:
            continue

        for lane in range(16):
            # Get actual drift
            actual = calib['drifts'][trans_key][str(lane)]

            # Predict
            predicted = predict_drift_hybrid(k, lane, drift_prev[lane], h4_params)

            # Check
            if predicted == actual:
                lane_correct[lane] += 1

            lane_total[lane] += 1

            # Update drift_prev with ACTUAL (for next iteration)
            drift_prev[lane] = actual

    # Display results
    print("Lane | Method                    | Correct/Total | Accuracy | Expected")
    print("-----|---------------------------|---------------|----------|----------")

    for lane in range(16):
        acc = (lane_correct[lane] / lane_total[lane] * 100) if lane_total[lane] > 0 else 0

        if lane >= 9:
            method = "Trivial (drift=0)"
            expected = "100%"
        elif lane == 8:
            method = "k<64: 0, else H4"
            expected = "~94%"
        elif lane == 7:
            method = "k<64: formula, else H4"
            expected = "~88%"
        else:
            method = "H4 affine"
            h4_acc = h4_params['results']['affine_recurrence']['per_lane'][str(lane)]['accuracy']
            expected = f"{h4_acc*100:.1f}%"

        print(f"  {lane:2d} | {method:25s} | {lane_correct[lane]:4d}/{lane_total[lane]:4d} | {acc:7.2f}% | {expected}")

    # Overall
    total_correct = sum(lane_correct)
    total = sum(lane_total)
    overall_acc = (total_correct / total * 100) if total > 0 else 0

    print("-----|---------------------------|---------------|----------|----------")
    print(f"TOTAL| Hybrid                    | {total_correct:4d}/{total:4d} | {overall_acc:7.2f}% |")
    print()

    # Category breakdown
    print("="*80)
    print("BY CATEGORY")
    print("="*80)
    print()

    trivial = sum(lane_correct[9:16])
    trivial_total = sum(lane_total[9:16])
    trivial_acc = (trivial / trivial_total * 100) if trivial_total > 0 else 0

    learnable = sum(lane_correct[7:9])
    learnable_total = sum(lane_total[7:9])
    learnable_acc = (learnable / learnable_total * 100) if learnable_total > 0 else 0

    complex_lanes = sum(lane_correct[0:7])
    complex_total = sum(lane_total[0:7])
    complex_acc = (complex_lanes / complex_total * 100) if complex_total > 0 else 0

    print(f"Trivial (9-15):   {trivial_acc:6.2f}% ({trivial}/{trivial_total})")
    print(f"Learnable (7-8):  {learnable_acc:6.2f}% ({learnable}/{learnable_total})")
    print(f"Complex (0-6):    {complex_acc:6.2f}% ({complex_lanes}/{complex_total})")
    print()

    # Comparison
    print("="*80)
    print("COMPARISON")
    print("="*80)
    print()
    h4_overall = h4_params['results']['affine_recurrence']['overall_accuracy']
    print(f"H4 baseline:      {h4_overall*100:.2f}%")
    print(f"Hybrid generator: {overall_acc:.2f}%")
    print(f"Improvement:      {overall_acc - h4_overall*100:+.2f}%")
    print()

    # Conclusion
    if overall_acc >= 85:
        print("✅ PROOF SUCCESS: Hybrid achieves >85% accuracy!")
    elif overall_acc > h4_overall * 100:
        print(f"⚠️  PROOF PARTIAL: Hybrid improves by {overall_acc - h4_overall*100:+.2f}%")
    else:
        print("❌ PROOF FAILED: No improvement over H4")

    return overall_acc

if __name__ == '__main__':
    acc = main()
