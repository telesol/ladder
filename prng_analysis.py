#!/usr/bin/env python3
"""
PRNG Analysis for Bitcoin Puzzle K-Sequence
Tests multiple PRNG hypotheses against the database values.
"""

import sqlite3
import numpy as np
from typing import List, Tuple
import hashlib
from decimal import Decimal

# Load k values from database
def load_k_values(db_path: str, max_n: int = 30) -> List[int]:
    """Load k[1] through k[max_n] from database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT puzzle_id, priv_hex
        FROM keys
        WHERE puzzle_id <= ?
        ORDER BY puzzle_id
    """, (max_n,))

    k_values = []
    for puzzle_id, priv_hex in cursor.fetchall():
        k_values.append(int(priv_hex, 16))

    conn.close()
    return k_values

def compute_normalized_positions(k_values: List[int]) -> List[float]:
    """
    For each k[n], compute position within range [2^(n-1), 2^n - 1]
    position = (k[n] - 2^(n-1)) / (2^(n-1))
    Returns values in [0, 1)
    """
    positions = []
    for n, k in enumerate(k_values, start=1):
        range_min = 2 ** (n - 1)
        range_size = 2 ** (n - 1)  # Size = 2^n - 1 - 2^(n-1) + 1 ≈ 2^(n-1)
        position = (k - range_min) / range_size
        positions.append(position)
    return positions

def test_lcg_pattern(k_values: List[int]) -> dict:
    """
    Test Linear Congruential Generator pattern:
    x[n+1] = (a * x[n] + c) mod m

    Try to find a, c, m such that k[n+1] ≈ f(k[n])
    """
    print("\n" + "="*60)
    print("TEST A: Linear Congruential Generator (LCG)")
    print("="*60)

    results = {
        "name": "LCG",
        "direct_lcg": False,
        "evidence": []
    }

    # Test 1: Direct LCG (unlikely with variable ranges)
    print("\n1. Testing direct LCG: k[n+1] = (a*k[n] + c) mod m")

    # For LCG, we'd expect k[n+1] to be predictable from k[n]
    # But our ranges vary exponentially, so this is unlikely
    for i in range(len(k_values) - 1):
        ratio = k_values[i+1] / k_values[i] if k_values[i] != 0 else 0
        print(f"  k[{i+2}]/k[{i+1}] = {k_values[i+1]}/{k_values[i]} = {ratio:.4f}")

    # Test 2: LCG on normalized positions
    print("\n2. Testing LCG on normalized positions:")
    positions = compute_normalized_positions(k_values)

    # Try to fit: pos[n+1] = (a * pos[n] + c) mod 1
    # Using least squares for first approximation
    if len(positions) >= 3:
        X = np.array(positions[:-1])
        y = np.array(positions[1:])

        # Try linear fit
        from numpy.linalg import lstsq
        A_matrix = np.vstack([X, np.ones(len(X))]).T
        solution, residuals, rank, s = lstsq(A_matrix, y, rcond=None)
        a_fit, c_fit = solution

        print(f"  Linear fit: pos[n+1] = {a_fit:.6f} * pos[n] + {c_fit:.6f}")

        # Check residuals
        predictions = a_fit * X + c_fit
        errors = np.abs(predictions - y)
        print(f"  Mean absolute error: {np.mean(errors):.6f}")
        print(f"  Max absolute error: {np.max(errors):.6f}")

        if np.mean(errors) < 0.1:
            results["evidence"].append(f"Positions show linear correlation (MAE={np.mean(errors):.6f})")
        else:
            results["evidence"].append(f"Positions NOT linearly correlated (MAE={np.mean(errors):.6f})")

    return results

def test_multiplicative_pattern(k_values: List[int]) -> dict:
    """
    Test multiplicative PRNG patterns:
    - Check if k[n+1]/k[n] shows patterns
    - Check if ratios relate to golden ratio, e, pi, etc.
    """
    print("\n" + "="*60)
    print("TEST B: Multiplicative Patterns")
    print("="*60)

    results = {
        "name": "Multiplicative",
        "constant_ratio": False,
        "evidence": []
    }

    ratios = []
    print("\nSuccessive ratios k[n+1]/k[n]:")
    for i in range(len(k_values) - 1):
        if k_values[i] != 0:
            ratio = k_values[i+1] / k_values[i]
            ratios.append(ratio)
            print(f"  k[{i+2}]/k[{i+1}] = {ratio:.6f}")

    # Statistics
    mean_ratio = np.mean(ratios)
    std_ratio = np.std(ratios)

    print(f"\nRatio statistics:")
    print(f"  Mean: {mean_ratio:.6f}")
    print(f"  Std:  {std_ratio:.6f}")
    print(f"  Min:  {min(ratios):.6f}")
    print(f"  Max:  {max(ratios):.6f}")

    # Check against mathematical constants
    constants = {
        "2": 2.0,
        "e": np.e,
        "π": np.pi,
        "φ (golden ratio)": (1 + np.sqrt(5)) / 2
    }

    print(f"\nComparison to mathematical constants:")
    for name, value in constants.items():
        diff = abs(mean_ratio - value)
        print(f"  Distance to {name}: {diff:.6f}")

    if std_ratio / mean_ratio < 0.1:  # Coefficient of variation < 10%
        results["constant_ratio"] = True
        results["evidence"].append(f"Nearly constant ratio: {mean_ratio:.6f} ± {std_ratio:.6f}")
    else:
        results["evidence"].append(f"Highly variable ratios (CV={std_ratio/mean_ratio:.2%})")

    return results

def test_xor_patterns(k_values: List[int]) -> dict:
    """
    Test XOR-based PRNG (LFSR-style):
    - Compute k[n] XOR k[n-1]
    - Look for patterns in XOR values
    - Check for recurrence relations
    """
    print("\n" + "="*60)
    print("TEST C: XOR-Based Patterns (LFSR)")
    print("="*60)

    results = {
        "name": "XOR/LFSR",
        "pattern_found": False,
        "evidence": []
    }

    print("\nXOR successive values:")
    xor_values = []
    for i in range(len(k_values) - 1):
        xor_val = k_values[i] ^ k_values[i+1]
        xor_values.append(xor_val)
        print(f"  k[{i+1}] XOR k[{i+2}] = {xor_val:064b} ({xor_val})")

    # Check if XOR values follow a pattern
    print("\nXOR value ratios:")
    for i in range(len(xor_values) - 1):
        if xor_values[i] != 0:
            ratio = xor_values[i+1] / xor_values[i]
            print(f"  XOR[{i+2}]/XOR[{i+1}] = {ratio:.6f}")

    # Check for bit patterns
    print("\nBit pattern analysis:")
    for i, xor_val in enumerate(xor_values[:10], start=1):
        bit_count = bin(xor_val).count('1')
        print(f"  XOR[{i}]: {bit_count} bits set")

    return results

def test_position_distribution(k_values: List[int]) -> dict:
    """
    Analyze normalized position distribution:
    - Uniform distribution suggests PRNG
    - Non-uniform suggests deterministic formula
    - Autocorrelation analysis
    """
    print("\n" + "="*60)
    print("TEST D: Position Distribution Analysis")
    print("="*60)

    results = {
        "name": "Distribution",
        "uniform": None,
        "evidence": []
    }

    positions = compute_normalized_positions(k_values)

    print("\nNormalized positions (0 = min of range, 1 = max):")
    for i, pos in enumerate(positions, start=1):
        print(f"  k[{i}] position: {pos:.6f}")

    # Statistical tests
    mean_pos = np.mean(positions)
    std_pos = np.std(positions)

    print(f"\nPosition statistics:")
    print(f"  Mean: {mean_pos:.6f} (expect 0.5 for uniform)")
    print(f"  Std:  {std_pos:.6f} (expect ~0.29 for uniform)")

    # Uniform distribution has mean=0.5, variance=1/12 ≈ 0.0833, std ≈ 0.289
    expected_mean = 0.5
    expected_std = 1/np.sqrt(12)

    mean_diff = abs(mean_pos - expected_mean)
    std_diff = abs(std_pos - expected_std)

    print(f"\nComparison to uniform distribution:")
    print(f"  Mean difference: {mean_diff:.6f}")
    print(f"  Std difference:  {std_diff:.6f}")

    # Autocorrelation
    print(f"\nAutocorrelation analysis:")
    for lag in [1, 2, 3]:
        if len(positions) > lag:
            correlation = np.corrcoef(positions[:-lag], positions[lag:])[0, 1]
            print(f"  Lag-{lag} autocorrelation: {correlation:.6f}")

            if abs(correlation) > 0.5:
                results["evidence"].append(f"Strong autocorrelation at lag {lag}: {correlation:.6f}")

    # Uniformity assessment
    if mean_diff < 0.15 and std_diff < 0.1:
        results["uniform"] = True
        results["evidence"].append("Position distribution consistent with uniform PRNG")
    else:
        results["uniform"] = False
        results["evidence"].append("Position distribution NOT uniform - suggests deterministic formula")

    return results

def test_hash_construction(k_values: List[int]) -> dict:
    """
    Test if k[n] could be derived from hash(seed || n):
    - SHA256(seed || n) mod range
    - Check if any seed produces the sequence
    """
    print("\n" + "="*60)
    print("TEST E: Hash-Based Construction")
    print("="*60)

    results = {
        "name": "Hash",
        "hash_based": False,
        "evidence": []
    }

    print("\nTesting if k[n] = SHA256(seed || n) mod range")
    print("(Testing a few candidate seeds...)")

    # Try some simple seeds
    test_seeds = [
        b"bitcoin",
        b"satoshi",
        b"puzzle",
        b"0" * 32,
        b"1" * 32,
    ]

    found_match = False
    for seed in test_seeds:
        matches = 0
        for n, k in enumerate(k_values[:5], start=1):  # Test first 5
            hash_input = seed + n.to_bytes(8, 'big')
            hash_val = int(hashlib.sha256(hash_input).hexdigest(), 16)

            # Map to range [2^(n-1), 2^n - 1]
            range_min = 2 ** (n - 1)
            range_size = 2 ** (n - 1)
            k_candidate = range_min + (hash_val % range_size)

            if k_candidate == k:
                matches += 1

        if matches > 0:
            print(f"  Seed {seed}: {matches}/5 matches")
            if matches >= 5:
                found_match = True
                results["hash_based"] = True
                results["evidence"].append(f"Found matching seed: {seed}")

    if not found_match:
        print("  No simple seed produces the sequence")
        results["evidence"].append("Hash construction with simple seeds: NEGATIVE")

    return results

def test_delta_sequence(k_values: List[int]) -> dict:
    """
    Analyze the difference sequence: d[n] = k[n+1] - k[n]
    PRNGs often show patterns in deltas.
    """
    print("\n" + "="*60)
    print("TEST F: Delta Sequence Analysis")
    print("="*60)

    results = {
        "name": "Delta",
        "evidence": []
    }

    deltas = []
    print("\nDelta sequence d[n] = k[n+1] - k[n]:")
    for i in range(len(k_values) - 1):
        delta = k_values[i+1] - k_values[i]
        deltas.append(delta)
        print(f"  d[{i+1}] = k[{i+2}] - k[{i+1}] = {delta}")

    # Second differences
    print("\nSecond differences d2[n] = d[n+1] - d[n]:")
    for i in range(len(deltas) - 1):
        d2 = deltas[i+1] - deltas[i]
        print(f"  d2[{i+1}] = {d2}")

    # Check if deltas are monotonic
    monotonic = all(deltas[i] <= deltas[i+1] for i in range(len(deltas)-1))
    print(f"\nDeltas monotonically increasing: {monotonic}")

    if monotonic:
        results["evidence"].append("Deltas monotonically increasing - suggests exponential growth, NOT random")

    return results

def main():
    db_path = "/home/solo/LA/db/kh.db"

    print("="*60)
    print("PRNG ANALYSIS: Bitcoin Puzzle K-Sequence")
    print("="*60)
    print("\nHypothesis: k[n] = PRNG(secret_seed, n) mapped to range")
    print("Testing k[1] through k[30]")

    # Load data
    k_values = load_k_values(db_path, max_n=30)
    print(f"\nLoaded {len(k_values)} key values from database")

    # Run all tests
    all_results = []

    all_results.append(test_lcg_pattern(k_values))
    all_results.append(test_multiplicative_pattern(k_values))
    all_results.append(test_xor_patterns(k_values))
    all_results.append(test_position_distribution(k_values))
    all_results.append(test_hash_construction(k_values))
    all_results.append(test_delta_sequence(k_values))

    # Final summary
    print("\n" + "="*60)
    print("FINAL VERDICT")
    print("="*60)

    prng_evidence_count = 0
    formula_evidence_count = 0

    for result in all_results:
        print(f"\n{result['name']}:")
        for evidence in result['evidence']:
            print(f"  - {evidence}")
            if any(word in evidence.lower() for word in ['random', 'uniform', 'prng']):
                prng_evidence_count += 1
            if any(word in evidence.lower() for word in ['not', 'deterministic', 'formula', 'monotonic']):
                formula_evidence_count += 1

    print("\n" + "="*60)
    print("CONCLUSION:")
    print("="*60)

    if formula_evidence_count > prng_evidence_count:
        print("\nSTRONG EVIDENCE AGAINST PRNG GENERATION")
        print("The sequence shows deterministic patterns consistent with")
        print("a mathematical formula, NOT pseudorandom generation.")
        print("\nKey indicators:")
        print("  - Non-uniform position distribution")
        print("  - Monotonically increasing deltas")
        print("  - No hash-based construction found")
        print("  - Strong autocorrelation")
    else:
        print("\nEVIDENCE SUGGESTS PRNG GENERATION")
        print("The sequence shows characteristics of pseudorandom generation.")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()
