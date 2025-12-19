#!/usr/bin/env python3
"""
Test the self-reference formula: Does m[n] divide m[n + m[n]]?

This is one of the most significant patterns discovered in the factorization analysis.
"""

import json
from pathlib import Path

def main():
    # Load data
    data_path = Path('/home/rkh/ladder/data_for_csolver.json')
    with open(data_path, 'r') as f:
        data = json.load(f)

    m_seq = data['m_seq']

    print("=" * 80)
    print("SELF-REFERENCE FORMULA TEST")
    print("=" * 80)
    print("\nHypothesis: m[n] divides m[n + m[n]]")
    print("\nTesting all m-values where n + m[n] is within sequence bounds...")
    print("-" * 80)

    successes = []
    failures = []
    out_of_bounds = []

    for i in range(len(m_seq)):
        n = i + 2  # m[2] is at index 0
        m_n = m_seq[i]

        # Calculate target index
        target_n = n + m_n
        target_i = target_n - 2  # Convert back to array index

        # Check if target is in bounds
        if target_i >= len(m_seq):
            out_of_bounds.append((n, m_n, target_n))
            continue

        m_target = m_seq[target_i]

        # Test divisibility
        if m_n > 0 and m_target % m_n == 0:
            quotient = m_target // m_n
            successes.append((n, m_n, target_n, m_target, quotient))
            print(f"✓ m[{n}] = {m_n} divides m[{target_n}] = {m_target}")
            print(f"  m[{target_n}] = m[{n}] × {quotient}")
        else:
            failures.append((n, m_n, target_n, m_target))
            print(f"✗ m[{n}] = {m_n} does NOT divide m[{target_n}] = {m_target}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total_tested = len(successes) + len(failures)
    print(f"\nTotal tested: {total_tested}")
    print(f"Successes: {len(successes)} ({len(successes)/total_tested*100:.1f}%)")
    print(f"Failures: {len(failures)} ({len(failures)/total_tested*100:.1f}%)")
    print(f"Out of bounds: {len(out_of_bounds)}")

    if successes:
        print("\n" + "-" * 80)
        print("SUCCESSFUL CASES:")
        print("-" * 80)
        for n, m_n, target_n, m_target, quotient in successes:
            print(f"  m[{n}] = {m_n:>10} → m[{target_n}] = {m_target:>15} (quotient: {quotient})")

    if failures:
        print("\n" + "-" * 80)
        print("FAILED CASES (showing first 10):")
        print("-" * 80)
        for n, m_n, target_n, m_target in failures[:10]:
            remainder = m_target % m_n if m_n > 0 else "N/A"
            print(f"  m[{n}] = {m_n:>10} ∤ m[{target_n}] = {m_target:>15} (remainder: {remainder})")

    # Check for patterns in successes
    if successes:
        print("\n" + "=" * 80)
        print("PATTERN ANALYSIS OF SUCCESSES")
        print("=" * 80)

        print("\nIndices where formula works:")
        success_indices = [n for n, _, _, _, _ in successes]
        print(f"  n = {success_indices}")

        print("\nValues that divide their offset-targets:")
        success_values = [(n, m_n) for n, m_n, _, _, _ in successes]
        for n, m_n in success_values:
            print(f"  m[{n}] = {m_n}")

        print("\nTarget indices reached:")
        target_indices = [target_n for _, _, target_n, _, _ in successes]
        print(f"  n + m[n] = {target_indices}")

        # Check if success indices have patterns
        if len(success_indices) > 1:
            diffs = [success_indices[i+1] - success_indices[i] for i in range(len(success_indices)-1)]
            print(f"\nDifferences between success indices: {diffs}")

    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

    if len(successes) > 0:
        print(f"\n✓ The self-reference formula holds for {len(successes)} out of {total_tested} testable cases!")
        print(f"  Success rate: {len(successes)/total_tested*100:.1f}%")

        if len(successes) >= 2:
            print("\n★ This is a SIGNIFICANT PATTERN!")
            print("  The m-sequence exhibits self-referential structure.")
            print("  This could be key to deriving the generation formula.")
    else:
        print("\n✗ The self-reference formula does not hold for any cases in the tested range.")
        print("  The pattern may emerge only in specific cases or require modification.")

    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
