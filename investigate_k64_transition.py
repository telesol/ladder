#!/usr/bin/env python3
"""
Investigate k=64 Regime Change Across All Lanes

Based on Lane 8 discovery: drift changes dramatically at k=64
Check if this is universal or lane-specific
"""

import json
import sys
from math import log2

def load_calibration():
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        return json.load(f)

def investigate_k64():
    print("="*80)
    print("INVESTIGATING k=64 REGIME CHANGE")
    print("="*80)
    print()
    print("Discovery: Lane 8 shows dramatic change at k=64 (2^6 = 64)")
    print("Question: Is this universal or lane-specific?")
    print()

    calib = load_calibration()

    # Check k=63, 64, 65 for all lanes
    print("="*80)
    print("DRIFT VALUES AT k=63, 64, 65 (ALL LANES)")
    print("="*80)
    print()
    print("Lane | k=63→64 | k=64→65 | k=65→66 | Δ(63→64) | Δ(64→65) | Change?")
    print("-----|---------|---------|---------|----------|----------|--------")

    transitions_at_64 = 0
    transitions_at_65 = 0

    for lane in range(16):
        d_63 = calib['drifts']['63→64'][str(lane)]
        d_64 = calib['drifts']['64→65'][str(lane)]
        d_65 = calib['drifts']['65→66'][str(lane)]

        delta_63_64 = d_64 - d_63
        delta_64_65 = d_65 - d_64

        changed_at_64 = (d_63 != d_64)
        changed_at_65 = (d_64 != d_65)

        if changed_at_64:
            transitions_at_64 += 1
        if changed_at_65:
            transitions_at_65 += 1

        marker = ""
        if changed_at_64 or changed_at_65:
            marker = "⚠️ YES"
        else:
            marker = "   -"

        print(f"  {lane:2d} | {d_63:7d} | {d_64:7d} | {d_65:7d} | {delta_63_64:8d} | {delta_64_65:8d} | {marker}")

    print()
    print(f"Transitions at k=64: {transitions_at_64}/16 lanes")
    print(f"Transitions at k=65: {transitions_at_65}/16 lanes")
    print()

    if transitions_at_64 > 8:
        print("✅ UNIVERSAL REGIME CHANGE at k=64 (majority of lanes)")
    elif transitions_at_64 > 0:
        print("⚠️  PARTIAL regime change at k=64 (some lanes)")
    else:
        print("❌ No regime change at k=64")

    print()

    # Check stability before k=64
    print("="*80)
    print("STABILITY CHECK: k=50-63 vs k=64-69")
    print("="*80)
    print()
    print("Lane | Changes k=50-63 | Changes k=64-69 | Ratio (64-69/50-63)")
    print("-----|------------------|------------------|---------------------")

    for lane in range(16):
        # Count changes k=50-63 (13 transitions)
        changes_before = 0
        for k in range(50, 63):
            d_k = calib['drifts'][f'{k}→{k+1}'][str(lane)]
            d_k1 = calib['drifts'][f'{k+1}→{k+2}'][str(lane)]
            if d_k != d_k1:
                changes_before += 1

        # Count changes k=64-69 (5 transitions)
        changes_after = 0
        for k in range(64, 69):
            d_k = calib['drifts'][f'{k}→{k+1}'][str(lane)]
            d_k1 = calib['drifts'][f'{k+1}→{k+2}'][str(lane)]
            if d_k != d_k1:
                changes_after += 1

        # Normalize by number of transitions
        rate_before = changes_before / 13 * 100
        rate_after = changes_after / 5 * 100

        if rate_before > 0:
            ratio = rate_after / rate_before
        else:
            ratio = float('inf') if rate_after > 0 else 0

        marker = ""
        if ratio > 2:
            marker = "🔥 MUCH MORE"
        elif ratio > 1.2:
            marker = "⚠️  MORE"
        elif ratio < 0.5:
            marker = "   LESS"

        print(f"  {lane:2d} | {changes_before:2d}/13 ({rate_before:5.1f}%) | {changes_after:2d}/5 ({rate_after:5.1f}%) | {ratio:6.2f}x {marker}")

    print()

def check_power_of_2_boundaries():
    """Check if other power-of-2 boundaries show transitions"""
    print("="*80)
    print("POWER-OF-2 BOUNDARY ANALYSIS")
    print("="*80)
    print()

    calib = load_calibration()
    boundaries = [2, 4, 8, 16, 32, 64]

    print("Boundary | 2^n | Transitions (all lanes) | Avg Δ | Notes")
    print("---------|-----|--------------------------|-------|-------")

    for k in boundaries:
        n = int(log2(k))

        transitions = 0
        total_delta = 0

        for lane in range(16):
            try:
                d_before = calib['drifts'][f'{k-1}→{k}'][str(lane)]
                d_at = calib['drifts'][f'{k}→{k+1}'][str(lane)]

                if d_before != d_at:
                    transitions += 1
                    total_delta += abs(d_at - d_before)
            except KeyError:
                pass  # Boundary before our data

        avg_delta = total_delta / max(transitions, 1)

        marker = ""
        if transitions >= 8:
            marker = "🔥 HIGH"
        elif transitions >= 4:
            marker = "⚠️  MEDIUM"

        print(f"  k={k:3d}  | 2^{n} | {transitions:2d}/16 lanes         | {avg_delta:5.1f} | {marker}")

    print()

def check_high_transition_zones():
    """Find zones with high transition rates"""
    print("="*80)
    print("HIGH TRANSITION ZONES (5-step windows)")
    print("="*80)
    print()

    calib = load_calibration()

    print("Window    | Total Transitions | Rate | Notes")
    print("----------|-------------------|------|-------")

    for k_start in range(1, 66, 5):
        k_end = min(k_start + 4, 69)

        transitions = 0
        for k in range(k_start, k_end):
            for lane in range(16):
                try:
                    d_k = calib['drifts'][f'{k}→{k+1}'][str(lane)]
                    d_k1 = calib['drifts'][f'{k+1}→{k+2}'][str(lane)]
                    if d_k != d_k1:
                        transitions += 1
                except KeyError:
                    pass

        window_size = (k_end - k_start) * 16
        rate = transitions / window_size * 100 if window_size > 0 else 0

        marker = ""
        if rate > 50:
            marker = "🔥 VERY HIGH"
        elif rate > 30:
            marker = "⚠️  HIGH"

        print(f"k={k_start:2d}-{k_end:2d}  | {transitions:3d}/{window_size:3d} | {rate:5.1f}% | {marker}")

    print()

def main():
    # Main investigation
    investigate_k64()

    # Check other boundaries
    check_power_of_2_boundaries()

    # Find high transition zones
    check_high_transition_zones()

    print("="*80)
    print("CONCLUSION")
    print("="*80)
    print()
    print("✅ k=64 analysis complete")
    print()
    print("Next steps:")
    print("  1. Review findings above")
    print("  2. If k=64 is universal → Create regime-specific models")
    print("  3. If k=64 is lane-specific → Investigate why")
    print("  4. Check other boundaries for additional regime changes")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
