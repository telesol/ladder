#!/usr/bin/env python3
"""
AI Brain: Verify PySR Formula on FULL 32-Byte Keys

The AI needs to understand:
1. Bitcoin keys are 32 bytes (256 bits) FULL
2. They grow from RIGHT to LEFT (big-endian)
3. PySR should work on ALL 32 lanes, not just 16
4. Lanes may have dependencies (carries between bytes)

This script verifies if PySR's discovered exponents work on the COMPLETE key.
"""

import csv
import numpy as np
from pathlib import Path
from typing import Dict, List

# PySR discovered exponents (for FIRST 16 lanes)
# Question: Do we need exponents for ALL 32 lanes?
PYSR_EXPONENTS_16 = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]


def load_puzzles_full_32bytes(csv_path: str) -> Dict[int, bytes]:
    """
    Load FULL 32-byte keys from CSV.

    Returns dict: puzzle_num -> 32 bytes (full key)
    """
    puzzles = {}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                puzzle_num = int(row['puzzle'])
            except ValueError:
                continue

            key_hex_64 = row['key_hex_64'].strip()
            if len(key_hex_64) != 64:
                continue

            # Convert to FULL 32 bytes
            full_32_bytes = bytes.fromhex(key_hex_64)
            puzzles[puzzle_num] = full_32_bytes

    return puzzles


def apply_pysr_formula_32lanes(current_bytes: bytes, exponents: List[int]) -> bytes:
    """
    Apply PySR formula to ALL 32 lanes.

    Formula: X_{k+1}(ℓ) = X_k(ℓ)^n mod 256

    Args:
        current_bytes: 32 bytes (full key)
        exponents: 32 exponents (one per lane)

    Returns:
        32 bytes (calculated next key)
    """
    if len(current_bytes) != 32:
        raise ValueError(f"Expected 32 bytes, got {len(current_bytes)}")

    if len(exponents) != 32:
        raise ValueError(f"Expected 32 exponents, got {len(exponents)}")

    next_bytes = []
    for lane in range(32):
        x = current_bytes[lane]
        n = exponents[lane]
        next_val = pow(x, n, 256)  # x^n mod 256
        next_bytes.append(next_val)

    return bytes(next_bytes)


def verify_full_32byte_evolution(puzzles: Dict[int, bytes],
                                   exponents: List[int],
                                   start: int,
                                   end: int) -> dict:
    """
    Verify PySR formula on FULL 32-byte keys.

    Returns verification results with per-lane analysis.
    """
    print(f"\n{'='*80}")
    print(f"AI BRAIN: Verifying PySR on FULL 32-Byte Keys")
    print(f"{'='*80}")

    print(f"\n🔍 Testing puzzles {start} to {end}")
    print(f"   Exponents: {exponents}")
    print(f"   (Total: {len(exponents)} lanes)")

    results = []
    current_key = puzzles[start]

    print(f"\n🌱 Starting from puzzle {start}:")
    print(f"   Full key (32 bytes): {current_key.hex()}")
    print(f"   Rightmost 8 bytes:   ...{current_key[-8:].hex()}")

    print(f"\n{'='*80}")
    print(f"Testing Transitions...")
    print(f"{'='*80}\n")

    total_puzzles = 0
    perfect_matches = 0

    for puzzle_num in range(start + 1, end + 1):
        if puzzle_num not in puzzles:
            continue

        # Calculate next puzzle
        calculated = apply_pysr_formula_32lanes(current_key, exponents)
        actual = puzzles[puzzle_num]

        # Byte-by-byte comparison
        matches_per_lane = [calculated[i] == actual[i] for i in range(32)]
        num_correct_lanes = sum(matches_per_lane)
        byte_accuracy = (num_correct_lanes / 32) * 100
        perfect_match = (calculated == actual)

        total_puzzles += 1
        if perfect_match:
            perfect_matches += 1

        # Find which lanes differ
        diff_lanes = [i for i in range(32) if not matches_per_lane[i]]

        result = {
            'puzzle': puzzle_num,
            'predicted_hex': calculated.hex(),
            'actual_hex': actual.hex(),
            'perfect_match': perfect_match,
            'byte_accuracy': byte_accuracy,
            'correct_lanes': num_correct_lanes,
            'diff_lanes': diff_lanes,
            'matches_per_lane': matches_per_lane
        }
        results.append(result)

        # Print result
        if perfect_match:
            print(f"Puzzle {puzzle_num:3d}: ✅ PERFECT MATCH (32/32 bytes)")
        else:
            print(f"Puzzle {puzzle_num:3d}: ❌ MISMATCH ({num_correct_lanes}/32 bytes = {byte_accuracy:.1f}%)")
            print(f"           Calculated: {calculated.hex()}")
            print(f"           Actual:    {actual.hex()}")

            # Show rightmost 8 bytes (where action happens)
            print(f"           Right 8B calculated: ...{calculated[-8:].hex()}")
            print(f"           Right 8B actual:    ...{actual[-8:].hex()}")

            if len(diff_lanes) <= 10:
                print(f"           Diff lanes: {diff_lanes}")
            else:
                print(f"           Diff lanes: {len(diff_lanes)} lanes differ")

        # Use ACTUAL key for next iteration (to avoid error accumulation)
        current_key = actual

    # Summary
    overall_accuracy = (perfect_matches / total_puzzles * 100) if total_puzzles > 0 else 0

    print(f"\n{'='*80}")
    print(f"VERIFICATION SUMMARY")
    print(f"{'='*80}")

    print(f"\n📊 Results:")
    print(f"   Puzzles tested: {total_puzzles}")
    print(f"   Perfect matches: {perfect_matches}/{total_puzzles}")
    print(f"   Accuracy: {overall_accuracy:.2f}%")

    if overall_accuracy == 100.0:
        print(f"\n🎉 SUCCESS! PySR formula works on FULL 32-byte keys!")
        print(f"   ✅ All {total_puzzles} puzzles matched perfectly")
        print(f"   ✅ Formula is PROVEN on full keys")
    elif overall_accuracy >= 95.0:
        print(f"\n⚠️  Near perfect, but {total_puzzles - perfect_matches} mismatches")
        print(f"   Need to investigate remaining errors")
    else:
        print(f"\n❌ FORMULA DOES NOT WORK on full 32-byte keys")
        print(f"   Only {overall_accuracy:.1f}% accuracy")
        print(f"   {total_puzzles - perfect_matches} out of {total_puzzles} failed")

    # Per-lane accuracy analysis
    if results:
        print(f"\n📊 Per-Lane Accuracy Analysis:")
        lane_correct_counts = [0] * 32
        for r in results:
            for lane in range(32):
                if r['matches_per_lane'][lane]:
                    lane_correct_counts[lane] += 1

        print(f"\n   Lane | Correct | Accuracy")
        print(f"   -----|---------|----------")
        for lane in range(32):
            acc = (lane_correct_counts[lane] / total_puzzles * 100) if total_puzzles > 0 else 0
            status = "✅" if acc == 100.0 else "❌"
            print(f"   {lane:4d} | {lane_correct_counts[lane]:7d} | {acc:6.1f}% {status}")

    return {
        'total_puzzles': total_puzzles,
        'perfect_matches': perfect_matches,
        'accuracy': overall_accuracy,
        'results': results
    }


def main():
    """Main verification."""
    print("="*80)
    print("AI BRAIN: Full 32-Byte PySR Verification")
    print("="*80)

    # Load data
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"

    print(f"\n📂 Loading puzzles from CSV...")
    puzzles = load_puzzles_full_32bytes(csv_path)
    print(f"   Loaded {len(puzzles)} puzzles")

    # AI reports what it sees
    print(f"\n🧠 AI Understanding:")
    print(f"   Each puzzle is 32 bytes (256 bits)")
    print(f"   Keys grow from RIGHT to LEFT")
    print(f"   Example puzzle 1: {puzzles[1].hex()}")
    print(f"   Example puzzle 70: {puzzles[70].hex()}")

    # Test 1: Do we have exponents for all 32 lanes?
    print(f"\n⚠️  PROBLEM DETECTED:")
    print(f"   PySR only discovered {len(PYSR_EXPONENTS_16)} exponents")
    print(f"   But we need 32 exponents (one per lane)!")
    print(f"\n   Current exponents: {PYSR_EXPONENTS_16}")

    # Assume last 16 lanes might have same pattern (hypothesis)
    print(f"\n💡 AI Hypothesis:")
    print(f"   Maybe the pattern repeats? Or mirrors?")
    print(f"   Let's test a few scenarios...")

    # Scenario 1: First 16 lanes use discovered exponents, last 16 are zeros
    print(f"\n{'='*80}")
    print(f"SCENARIO 1: First 16 lanes active, last 16 are passive (zero)")
    print(f"{'='*80}")
    exponents_scenario1 = [0] * 16 + PYSR_EXPONENTS_16
    results1 = verify_full_32byte_evolution(puzzles, exponents_scenario1, 1, 10)

    # Scenario 2: Pattern repeats (16 + 16)
    print(f"\n{'='*80}")
    print(f"SCENARIO 2: Pattern repeats (first 16 + first 16 again)")
    print(f"{'='*80}")
    exponents_scenario2 = PYSR_EXPONENTS_16 + PYSR_EXPONENTS_16
    results2 = verify_full_32byte_evolution(puzzles, exponents_scenario2, 1, 10)

    # Scenario 3: Mirrored pattern
    print(f"\n{'='*80}")
    print(f"SCENARIO 3: Pattern mirrors (first 16 + reversed)")
    print(f"{'='*80}")
    exponents_scenario3 = PYSR_EXPONENTS_16 + list(reversed(PYSR_EXPONENTS_16))
    results3 = verify_full_32byte_evolution(puzzles, exponents_scenario3, 1, 10)

    # Final AI conclusion
    print(f"\n{'='*80}")
    print(f"AI CONCLUSION")
    print(f"{'='*80}")

    best_accuracy = max(results1['accuracy'], results2['accuracy'], results3['accuracy'])

    if best_accuracy == 100.0:
        if results1['accuracy'] == 100.0:
            print(f"\n✅ SCENARIO 1 WORKS! (First 16 passive, last 16 active)")
        elif results2['accuracy'] == 100.0:
            print(f"\n✅ SCENARIO 2 WORKS! (Pattern repeats)")
        elif results3['accuracy'] == 100.0:
            print(f"\n✅ SCENARIO 3 WORKS! (Pattern mirrors)")
        print(f"\n🎉 We found the correct exponent pattern for all 32 lanes!")
    else:
        print(f"\n❌ NONE OF THE SCENARIOS WORK")
        print(f"   Best accuracy: {best_accuracy:.1f}%")
        print(f"\n🧠 AI Recommendation:")
        print(f"   1. Check if PySR was trained on correct data (all 32 lanes)")
        print(f"   2. Verify if lanes have dependencies (carries)")
        print(f"   3. May need to retrain PySR on FULL 32-byte sequences")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
