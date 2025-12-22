#!/usr/bin/env python3
"""
AI Brain: Discover the TRUE Pattern

Since per-lane formulas don't work (carries between bytes),
let's test if this is simple INTEGER arithmetic.

Hypothesis tests:
1. Multiplication: puzzle[n+1] = puzzle[n] * k
2. Addition: puzzle[n+1] = puzzle[n] + k
3. Bit shift: puzzle[n+1] = puzzle[n] << k
4. Polynomial: puzzle[n+1] = puzzle[n]^k
"""

import csv
from pathlib import Path

def load_puzzles_as_integers(csv_path: str) -> dict:
    """Load puzzles as 256-bit integers."""
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

            # Convert to integer (256-bit number)
            key_int = int(key_hex_64, 16)
            puzzles[puzzle_num] = key_int

    return puzzles


def test_pattern(puzzles: dict, pattern_func, pattern_name: str, max_test: int = 10):
    """
    Test if a pattern holds across puzzles.

    Args:
        puzzles: dict of puzzle_num -> integer value
        pattern_func: function(current) -> next_predicted
        pattern_name: name of the pattern being tested
    """
    print(f"\n{'='*80}")
    print(f"Testing Pattern: {pattern_name}")
    print(f"{'='*80}\n")

    matches = 0
    total = 0

    for puzzle_num in range(1, max_test + 1):
        if puzzle_num not in puzzles or puzzle_num + 1 not in puzzles:
            continue

        current = puzzles[puzzle_num]
        actual_next = puzzles[puzzle_num + 1]
        predicted_next = pattern_func(current)

        match = (predicted_next == actual_next)
        total += 1
        if match:
            matches += 1

        status = "✅" if match else "❌"
        print(f"Puzzle {puzzle_num}→{puzzle_num+1}: {status}")
        if not match:
            print(f"  Current:   {current:#066x}")
            print(f"  Calculated: {predicted_next:#066x}")
            print(f"  Actual:    {actual_next:#066x}")

    accuracy = (matches / total * 100) if total > 0 else 0
    print(f"\nAccuracy: {matches}/{total} = {accuracy:.1f}%")

    return accuracy


def main():
    """AI discovers the true pattern."""
    print("="*80)
    print("AI BRAIN: Discovering the TRUE Pattern")
    print("="*80)

    # Load data as integers
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"
    puzzles = load_puzzles_as_integers(csv_path)

    print(f"\n📂 Loaded {len(puzzles)} puzzles as 256-bit integers")
    print(f"\n🔍 Sample values:")
    for i in [1, 2, 3, 10, 70]:
        if i in puzzles:
            print(f"   Puzzle {i:3d}: {puzzles[i]:#066x} = {puzzles[i]}")

    # Test various patterns
    print(f"\n{'='*80}")
    print(f"AI Testing Multiple Hypotheses...")
    print(f"{'='*80}")

    results = {}

    # Test 1: Simple multiplication by small constants
    for k in [2, 3, 4, 5, 7, 11]:
        pattern_name = f"Multiply by {k}"
        pattern_func = lambda x, mult=k: x * mult
        acc = test_pattern(puzzles, pattern_func, pattern_name, max_test=20)
        results[pattern_name] = acc

    # Test 2: Addition of constant
    for k in [1, 2, 3, 7]:
        pattern_name = f"Add {k}"
        pattern_func = lambda x, add=k: x + add
        acc = test_pattern(puzzles, pattern_func, pattern_name, max_test=20)
        results[pattern_name] = acc

    # Test 3: Bit shifts
    for k in [1, 2, 3]:
        pattern_name = f"Left shift by {k}"
        pattern_func = lambda x, shift=k: x << shift
        acc = test_pattern(puzzles, pattern_func, pattern_name, max_test=20)
        results[pattern_name] = acc

    # Test 4: Powers
    for k in [2, 3]:
        pattern_name = f"Power of {k}"
        pattern_func = lambda x, power=k: x ** power
        acc = test_pattern(puzzles, pattern_func, pattern_name, max_test=10)  # Careful with large numbers
        results[pattern_name] = acc

    # Test 5: Modular arithmetic (common in crypto)
    MODULUS = 2**256  # Since we're dealing with 256-bit numbers
    for k in [2, 3]:
        pattern_name = f"Multiply by {k} mod 2^256"
        pattern_func = lambda x, mult=k, mod=MODULUS: (x * mult) % mod
        acc = test_pattern(puzzles, pattern_func, pattern_name, max_test=20)
        results[pattern_name] = acc

    # AI's conclusion
    print(f"\n{'='*80}")
    print(f"AI CONCLUSION")
    print(f"{'='*80}\n")

    # Find best pattern
    best_pattern = max(results, key=results.get)
    best_accuracy = results[best_pattern]

    print(f"📊 Results Summary:")
    for pattern, acc in sorted(results.items(), key=lambda x: x[1], reverse=True):
        status = "🎯" if acc == 100.0 else "⚠️" if acc >= 50.0 else "❌"
        print(f"   {status} {pattern:30s}: {acc:6.1f}%")

    if best_accuracy == 100.0:
        print(f"\n🎉 SUCCESS! Pattern discovered:")
        print(f"   {best_pattern}")
        print(f"   Accuracy: {best_accuracy:.1f}%")
        print(f"\n✅ This is the TRUE pattern!")
    elif best_accuracy >= 95.0:
        print(f"\n🤔 Very close! Best pattern:")
        print(f"   {best_pattern}")
        print(f"   Accuracy: {best_accuracy:.1f}%")
        print(f"\n💡 May need minor adjustment")
    else:
        print(f"\n❌ No simple pattern found")
        print(f"   Best: {best_pattern} ({best_accuracy:.1f}%)")
        print(f"\n🧠 AI Recommendations:")
        print(f"   1. Pattern may be more complex (conditional logic)")
        print(f"   2. May involve puzzle number as input")
        print(f"   3. Could be a combination of operations")
        print(f"   4. Might need to analyze actual Bitcoin key generation")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
