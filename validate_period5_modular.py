#!/usr/bin/env python3
"""
Validate Period-5 Modular Theorem
==================================

Test the fundamental theorem: k_{n+5} ≡ k_n (mod 5)

This script tests whether the k-values from the Bitcoin puzzle
exhibit exact period-5 behavior when reduced modulo 5.

Theory: From the recurrence k_n = 2×k_{n-5} + (2^n - m×k_d - r)
        and Fermat's Little Theorem (2^5 ≡ 2 mod 5),
        we should have k_{n+5} ≡ k_n (mod 5) for all n.
"""

import json
import csv
from pathlib import Path

def hex_to_int(hex_str):
    """Convert hex string to integer"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    return int(hex_str, 16)

def load_k_values_from_csv():
    """Load k-values from the CSV file"""
    csv_path = Path('data/btc_puzzle_1_160_full.csv')
    k_values = {}

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 4:
                puzzle_num = int(row[0])
                priv_hex = row[3]  # Private key in hex
                # Skip unsolved puzzles (marked with '?')
                if priv_hex and priv_hex != '?' and not priv_hex.startswith('?'):
                    try:
                        k_values[puzzle_num] = hex_to_int(priv_hex)
                    except ValueError:
                        # Skip invalid entries
                        pass

    return k_values

def test_period5_modular(k_values, max_n=70):
    """Test k_{n+5} ≡ k_n (mod 5) for all available n"""
    print("=" * 70)
    print("PERIOD-5 MODULAR THEOREM VALIDATION")
    print("=" * 70)
    print()
    print("Theory: k_{n+5} ≡ k_n (mod 5)")
    print()

    results = []
    matches = 0
    total = 0

    print("Testing k-values from puzzles 1 to {}:".format(max_n))
    print()
    print("n    k_n mod 5    k_{n+5} mod 5    Match?")
    print("-" * 50)

    for n in range(1, max_n - 4):
        if n in k_values and (n+5) in k_values:
            k_n = k_values[n]
            k_n_plus_5 = k_values[n+5]

            mod_n = k_n % 5
            mod_n_plus_5 = k_n_plus_5 % 5

            match = (mod_n == mod_n_plus_5)
            matches += 1 if match else 0
            total += 1

            status = "✓" if match else "✗"

            # Print first 20 and any mismatches
            if n <= 20 or not match:
                print(f"{n:<4} {mod_n:<12} {mod_n_plus_5:<16} {status}")

            results.append({
                'n': n,
                'k_n_mod5': mod_n,
                'k_n_plus_5_mod5': mod_n_plus_5,
                'match': match
            })

    if total > 20:
        print("... ({} more tests)".format(total - 20))

    print()
    print("=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(f"Total tests: {total}")
    print(f"Matches: {matches}")
    print(f"Mismatches: {total - matches}")
    print(f"Accuracy: {100 * matches / total:.2f}%")
    print()

    if matches == total:
        print("✅ THEOREM CONFIRMED! Period-5 modular property holds for ALL tested values!")
    elif matches / total >= 0.9:
        print("⚠️  High accuracy but not perfect. Need to investigate mismatches.")
    else:
        print("❌ THEOREM NOT CONFIRMED. Significant deviations observed.")

    print()

    # Analyze the residue pattern
    print("=" * 70)
    print("RESIDUE PATTERN ANALYSIS")
    print("=" * 70)
    print()
    print("Observing the k_n mod 5 pattern:")
    print()
    pattern = [k_values[n] % 5 for n in range(1, min(26, max_n + 1)) if n in k_values]
    print("n:      ", " ".join(f"{n:2}" for n in range(1, len(pattern) + 1)))
    print("k_n%5:  ", " ".join(f"{r:2}" for r in pattern))
    print()

    # Check if pattern repeats with period 5
    if len(pattern) >= 10:
        period5 = True
        for i in range(5, min(len(pattern), 25)):
            if pattern[i] != pattern[i-5]:
                period5 = False
                break

        if period5:
            print("✓ Pattern confirms period-5 repetition!")
            print("  Base cycle: [{}]".format(", ".join(str(pattern[i]) for i in range(5))))
        else:
            print("✗ Pattern does NOT show perfect period-5 repetition")

    return results

def main():
    print("Loading k-values from CSV...")
    k_values = load_k_values_from_csv()
    print(f"Loaded {len(k_values)} k-values (puzzles 1-{max(k_values.keys())})")
    print()

    results = test_period5_modular(k_values)

    # Save results
    output_file = 'period5_modular_validation_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'total_tests': len(results),
            'matches': sum(1 for r in results if r['match']),
            'accuracy': sum(1 for r in results if r['match']) / len(results) if results else 0,
            'results': results
        }, f, indent=2)

    print(f"Results saved to: {output_file}")

if __name__ == '__main__':
    main()
