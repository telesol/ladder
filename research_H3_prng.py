#!/usr/bin/env python3
"""
Hypothesis 3 (H3): PRNG (Pseudo-Random Number Generator)

Theory: drift comes from seeded random number generator
    rng = PRNG(seed=?)
    for puzzle in range(1, 161):
        for lane in range(16):
            drift[puzzle][lane] = rng.next() mod 256

Tests:
1. Python random.Random() with various seeds
2. NumPy random with various seeds
3. Mersenne Twister (MT19937)
4. Linear Congruential Generator (LCG)
5. Crypto PRNGs (if available)
6. Brute-force seed search (0-100000)

Machine: ASUS B10 #1
Expected time: 3-4 hours
"""

import json
import random
import sys
from pathlib import Path

def load_data(json_path="drift_data_export.json"):
    """Load drift data from export file"""
    print(f"[1/6] Loading data from {json_path}")
    with open(json_path) as f:
        data = json.load(f)

    transitions = data['transitions']
    print(f"  ✓ Loaded {len(transitions)} transitions ({len(transitions)*16} drift values)")

    # Extract expected sequence of drifts (in order)
    expected_sequence = []
    for trans in sorted(transitions, key=lambda t: t['from_puzzle']):
        for lane in range(16):
            expected_sequence.append(trans['drifts'][lane])

    print(f"  ✓ Built expected sequence: {len(expected_sequence)} values")
    return data, expected_sequence

def test_python_random_seed(expected_sequence, seed):
    """Test Python's random.Random() with given seed"""
    rng = random.Random(seed)

    matches = 0
    for expected in expected_sequence:
        generated = rng.randint(0, 255)
        if generated == expected:
            matches += 1

    return matches / len(expected_sequence)

def test_python_random_seeds(expected_sequence):
    """Test Python random.Random() with various seeds"""
    print("\n[2/6] Testing Python random.Random()")

    # Test common seeds
    common_seeds = [0, 1, 42, 123, 255, 1337, 12345, 0x1234, 0xDEADBEEF]

    best_seed = None
    best_accuracy = 0.0

    print("  Testing common seeds...")
    for seed in common_seeds:
        accuracy = test_python_random_seed(expected_sequence, seed)
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_seed = seed

        if accuracy == 1.0:
            print(f"    ✅ 100% match with seed={seed}!")
            return {'best_seed': seed, 'accuracy': 1.0, 'method': 'python_random'}
        elif accuracy > 0.8:
            print(f"    🔥 {accuracy*100:.1f}% with seed={seed}")

    print(f"  Best common seed: {best_seed} ({best_accuracy*100:.1f}%)")
    return {'best_seed': best_seed, 'accuracy': best_accuracy, 'method': 'python_random'}

def test_numpy_random_seeds(expected_sequence):
    """Test NumPy random with various seeds"""
    print("\n[3/6] Testing NumPy random")

    try:
        import numpy as np

        common_seeds = [0, 1, 42, 123, 255, 1337, 12345]

        best_seed = None
        best_accuracy = 0.0

        for seed in common_seeds:
            rng = np.random.RandomState(seed)
            matches = 0

            for expected in expected_sequence:
                generated = rng.randint(0, 256)
                if generated == expected:
                    matches += 1

            accuracy = matches / len(expected_sequence)

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_seed = seed

            if accuracy == 1.0:
                print(f"  ✅ 100% match with seed={seed}!")
                return {'best_seed': seed, 'accuracy': 1.0, 'method': 'numpy_random'}
            elif accuracy > 0.8:
                print(f"  🔥 {accuracy*100:.1f}% with seed={seed}")

        print(f"  Best seed: {best_seed} ({best_accuracy*100:.1f}%)")
        return {'best_seed': best_seed, 'accuracy': best_accuracy, 'method': 'numpy_random'}

    except ImportError:
        print("  ⚠ NumPy not available")
        return {'available': False}

def test_lcg_seeds(expected_sequence):
    """Test Linear Congruential Generator (LCG)"""
    print("\n[4/6] Testing LCG (Linear Congruential Generator)")

    # Standard LCG parameters (from various implementations)
    lcg_params = [
        ('MINSTD', 48271, 0, 2**31 - 1),  # Minimum standard
        ('GLIBC', 1103515245, 12345, 2**31),  # GNU C Library
        ('BORLAND', 22695477, 1, 2**32),  # Borland C/C++
        ('NUMERICAL_RECIPES', 1664525, 1013904223, 2**32)  # Numerical Recipes
    ]

    best_result = {'accuracy': 0.0}

    for name, a, c, m in lcg_params:
        print(f"  Testing {name} LCG...")

        # Try different seeds
        for seed in [0, 1, 42, 123, 1337, 12345]:
            state = seed
            matches = 0

            for expected in expected_sequence:
                state = (a * state + c) % m
                generated = state % 256

                if generated == expected:
                    matches += 1

            accuracy = matches / len(expected_sequence)

            if accuracy > best_result['accuracy']:
                best_result = {
                    'name': name,
                    'seed': seed,
                    'accuracy': accuracy,
                    'params': {'a': a, 'c': c, 'm': m}
                }

            if accuracy == 1.0:
                print(f"    ✅ 100% match with {name} seed={seed}!")
                return best_result
            elif accuracy > 0.8:
                print(f"    🔥 {accuracy*100:.1f}% with seed={seed}")

    if best_result['accuracy'] > 0:
        print(f"  Best: {best_result['name']} seed={best_result['seed']} "
              f"({best_result['accuracy']*100:.1f}%)")

    return best_result

def brute_force_seeds(expected_sequence, max_seed=100000, sample_size=20):
    """Brute force search for seed (testing first N values only for speed)"""
    print(f"\n[5/6] Brute Force Seed Search (0-{max_seed})")
    print(f"  Testing first {sample_size} drift values for speed...")

    sample_expected = expected_sequence[:sample_size]

    best_seed = None
    best_accuracy = 0.0
    best_full_accuracy = 0.0

    print("  Searching seeds...")

    for seed in range(max_seed + 1):
        if seed % 10000 == 0:
            print(f"    Progress: {seed}/{max_seed} (best so far: {best_accuracy*100:.1f}%)")

        # Test with sample
        rng = random.Random(seed)
        matches = sum(1 for exp in sample_expected if rng.randint(0, 255) == exp)
        accuracy = matches / len(sample_expected)

        if accuracy > 0.9:  # Promising seed, test full sequence
            rng = random.Random(seed)
            full_matches = sum(1 for exp in expected_sequence if rng.randint(0, 255) == exp)
            full_accuracy = full_matches / len(expected_sequence)

            if full_accuracy > best_full_accuracy:
                best_full_accuracy = full_accuracy
                best_seed = seed
                best_accuracy = accuracy

            if full_accuracy == 1.0:
                print(f"\n  ✅ 100% MATCH FOUND! seed={seed}")
                return {'seed': seed, 'accuracy': 1.0, 'method': 'brute_force'}

        elif accuracy > best_accuracy:
            best_accuracy = accuracy
            best_seed = seed

    if best_seed is not None:
        print(f"\n  Best seed found: {best_seed}")
        print(f"    Sample accuracy: {best_accuracy*100:.1f}%")
        if best_full_accuracy > 0:
            print(f"    Full accuracy: {best_full_accuracy*100:.1f}%")

        return {'seed': best_seed, 'sample_accuracy': best_accuracy,
                'full_accuracy': best_full_accuracy, 'method': 'brute_force'}

    print(f"  ❌ No promising seeds found")
    return {'accuracy': 0.0, 'method': 'brute_force'}

def test_custom_prng(expected_sequence):
    """Test custom PRNG patterns"""
    print("\n[6/6] Testing Custom PRNG Patterns")

    # Test: Simple counter mod 256
    print("  Testing simple counter...")
    matches = sum(1 for i, exp in enumerate(expected_sequence) if i % 256 == exp)
    counter_accuracy = matches / len(expected_sequence)

    if counter_accuracy == 1.0:
        print(f"  ✅ 100% match with counter mod 256!")
        return {'counter': 1.0}
    elif counter_accuracy > 0.8:
        print(f"  🔥 Counter: {counter_accuracy*100:.1f}%")

    # Test: Fibonacci-like sequence
    print("  Testing Fibonacci-like PRNG...")
    a, b = 0, 1
    matches = 0
    for expected in expected_sequence:
        if (a % 256) == expected:
            matches += 1
        a, b = b, (a + b) % 256

    fib_accuracy = matches / len(expected_sequence)

    if fib_accuracy == 1.0:
        print(f"  ✅ 100% match with Fibonacci PRNG!")
    elif fib_accuracy > 0.8:
        print(f"  🔥 Fibonacci: {fib_accuracy*100:.1f}%")

    return {'counter': counter_accuracy, 'fibonacci': fib_accuracy}

def generate_report(data, python_result, numpy_result, lcg_result, brute_result, custom_result):
    """Generate final report"""
    print("\n[7/7] Generating Report")

    # Find best result
    all_results = [
        ('Python random', python_result.get('accuracy', 0.0)),
        ('NumPy random', numpy_result.get('accuracy', 0.0)),
        ('LCG', lcg_result.get('accuracy', 0.0)),
        ('Brute force', brute_result.get('full_accuracy', brute_result.get('accuracy', 0.0))),
        ('Counter', custom_result.get('counter', 0.0)),
        ('Fibonacci', custom_result.get('fibonacci', 0.0))
    ]

    best = max(all_results, key=lambda x: x[1])

    report = {
        'hypothesis': 'H3: PRNG (Pseudo-Random Generator)',
        'theory': 'drift = PRNG(seed).next() mod 256',
        'results': {
            'python_random': python_result,
            'numpy_random': numpy_result,
            'lcg': lcg_result,
            'brute_force': brute_result,
            'custom_patterns': custom_result
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
    output_path = Path("H3_results.json")
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"  ✓ Report saved to: {output_path}")

    # Print summary
    print("\n" + "="*60)
    print("H3 HYPOTHESIS SUMMARY")
    print("="*60)
    print(f"Best approach:  {best[0]}")
    print(f"Accuracy:       {best[1]*100:.2f}%")
    print(f"Conclusion:     {report['conclusion']}")
    print("="*60)

    if best[1] == 1.0:
        print("\n🎉 SUCCESS! Generator found: drift = PRNG(seed)")
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
    data, expected_sequence = load_data(data_file)

    # Run tests
    python_result = test_python_random_seeds(expected_sequence)
    numpy_result = test_numpy_random_seeds(expected_sequence)
    lcg_result = test_lcg_seeds(expected_sequence)
    brute_result = brute_force_seeds(expected_sequence, max_seed=100000, sample_size=20)
    custom_result = test_custom_prng(expected_sequence)

    # Generate report
    report = generate_report(data, python_result, numpy_result, lcg_result, brute_result, custom_result)

    print("\n✅ H3 research complete!")

if __name__ == '__main__':
    main()
