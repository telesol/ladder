#!/usr/bin/env python3
"""
GAP PUZZLE PRNG/HASH ANALYSIS

Since α = k[n]/2^n varies, test if k[n] is generated via:
1. PRNG(seed, n) where output is in range [2^(n-1), 2^n - 1]
2. hash(seed || n) mod 2^(n-1) + 2^(n-1)
3. Linear Congruential Generator (LCG)
4. Mersenne Twister fingerprints
"""

import sqlite3
import hashlib
from decimal import Decimal, getcontext

getcontext().prec = 100

DB_PATH = "/home/solo/LA/db/kh.db"

def get_all_keys():
    """Load ALL 74 known keys from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id")
    rows = cursor.fetchall()

    keys = {}
    for pid, hex_val in rows:
        keys[pid] = int(hex_val, 16)

    conn.close()
    return keys

def test_lcg_pattern(keys):
    """Test if keys follow Linear Congruential Generator pattern"""
    print("="*80)
    print("LINEAR CONGRUENTIAL GENERATOR (LCG) TEST")
    print("="*80)
    print("\nLCG: X_{n+1} = (a*X_n + c) mod m")
    print("Testing if offsets follow LCG pattern...\n")

    # Get offsets from minimum
    offsets = {}
    for n, k in keys.items():
        min_val = 2**(n-1)
        offsets[n] = k - min_val

    # Test consecutive pairs to find a, c
    sorted_n = sorted(keys.keys())

    for i in range(min(5, len(sorted_n) - 1)):
        n1 = sorted_n[i]
        n2 = sorted_n[i+1]

        if n1 in offsets and n2 in offsets:
            x1 = offsets[n1]
            x2 = offsets[n2]

            print(f"n={n1} → n={n2}:")
            print(f"  offset[{n1}] = {x1}")
            print(f"  offset[{n2}] = {x2}")

            # For simple LCG, try to derive a and c
            # x2 = (a*x1 + c) mod m
            # We don't know m, but could try various moduli

def test_hash_based_generation(keys):
    """Test if keys are generated via hash(seed, n)"""
    print("\n" + "="*80)
    print("HASH-BASED GENERATION TEST")
    print("="*80)
    print("\nHypothesis: k[n] = hash(seed || n) constrained to [2^(n-1), 2^n - 1]")

    # Strategy: If hash-based, byte patterns should appear random
    # AND there should be no correlation between consecutive keys

    sorted_n = sorted(keys.keys())

    print("\nTesting for hash fingerprints:")
    print("1. Byte randomness (chi-square test)")
    print("2. Lack of correlation between consecutive keys\n")

    for n in sorted_n[:10]:  # Test first 10
        k = keys[n]

        # Convert to bytes
        num_bytes = (n + 7) // 8
        byte_array = k.to_bytes(num_bytes, byteorder='big')

        # Count byte values
        byte_counts = [0] * 256
        for byte in byte_array:
            byte_counts[byte] += 1

        # Simple uniformity check
        non_zero_bytes = sum(1 for c in byte_counts if c > 0)
        max_count = max(byte_counts)

        print(f"n={n}:")
        print(f"  Unique byte values: {non_zero_bytes}/256")
        print(f"  Max byte occurrence: {max_count}")

        # XOR with next key to check correlation
        if n + 1 in keys:
            k_next = keys[n+1]
            # Normalize to same bit length for comparison
            xor_val = k ^ (k_next >> (n+1-n))
            print(f"  XOR with k[{n+1}] (normalized): {bin(xor_val).count('1')}/{n} ones")

def test_position_pattern(keys):
    """Test if position in range follows a pattern"""
    print("\n" + "="*80)
    print("POSITION PATTERN ANALYSIS")
    print("="*80)
    print("\nIf positions are random: should be uniform 0-100%")
    print("If positions follow pattern: may correlate with n or f(n)\n")

    positions = []
    sorted_n = sorted(keys.keys())

    for n in sorted_n:
        k = keys[n]
        min_val = 2**(n-1)
        max_val = 2**n - 1
        range_size = max_val - min_val + 1
        offset = k - min_val
        position_pct = (offset / range_size) * 100
        positions.append((n, position_pct))

        print(f"n={n:3d}: position = {position_pct:6.2f}%")

    # Statistical analysis
    pos_values = [p for _, p in positions]
    avg_pos = sum(pos_values) / len(pos_values)
    variance = sum((p - avg_pos)**2 for p in pos_values) / len(pos_values)
    std_dev = variance ** 0.5

    print(f"\nStatistics:")
    print(f"  Mean position: {avg_pos:.2f}%")
    print(f"  Std deviation: {std_dev:.2f}%")
    print(f"  Expected (uniform): 50.00% ± 28.87%")

    if abs(avg_pos - 50) < 5:
        print("\n✓ Mean close to 50% - consistent with random/hash generation")
    else:
        print(f"\n✗ Mean {avg_pos:.2f}% deviates from 50% - may indicate bias")

def test_alpha_function(keys):
    """Test if α = k[n]/2^n follows a mathematical function of n"""
    print("\n" + "="*80)
    print("ALPHA FUNCTION ANALYSIS: α(n) = k[n]/2^n")
    print("="*80)

    alphas = []
    sorted_n = sorted(keys.keys())

    print("\nα values for all known keys:\n")

    for n in sorted_n:
        k = keys[n]
        alpha = Decimal(k) / Decimal(2**n)
        alphas.append((n, float(alpha)))

        # Only print GAP keys and early keys for clarity
        if n <= 20 or n in [70, 75, 80, 85, 90]:
            print(f"n={n:3d}: α = {alpha:.10f}")

    # Test if α follows polynomial, exponential, or trigonometric pattern
    print("\n\nTesting α(n) patterns:")

    # Linear regression: α = a*n + b
    from statistics import mean
    n_values = [n for n, _ in alphas]
    alpha_values = [a for _, a in alphas]

    n_mean = mean(n_values)
    alpha_mean = mean(alpha_values)

    # Calculate slope and intercept
    numerator = sum((n - n_mean) * (a - alpha_mean) for n, a in alphas)
    denominator = sum((n - n_mean)**2 for n in n_values)

    if denominator != 0:
        slope = numerator / denominator
        intercept = alpha_mean - slope * n_mean

        print(f"\nLinear fit: α(n) ≈ {slope:.10f}*n + {intercept:.10f}")

        # Calculate R² (coefficient of determination)
        ss_tot = sum((a - alpha_mean)**2 for a in alpha_values)
        ss_res = sum((a - (slope*n + intercept))**2 for n, a in alphas)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        print(f"R² = {r_squared:.6f}")

        if r_squared > 0.5:
            print("✓ Strong linear correlation - α may be function of n")
        else:
            print("✗ Weak linear correlation")

    # Test for periodic patterns
    print("\n\nTesting for periodic patterns:")

    for period in [5, 10, 15, 20]:
        # Check if α values repeat with given period
        matches = 0
        comparisons = 0

        for i in range(len(alphas)):
            for j in range(i+1, len(alphas)):
                n1, a1 = alphas[i]
                n2, a2 = alphas[j]

                if (n2 - n1) % period == 0:
                    comparisons += 1
                    if abs(a1 - a2) < 0.1:  # Tolerance
                        matches += 1

        if comparisons > 0:
            match_rate = matches / comparisons
            print(f"  Period {period}: {match_rate*100:.1f}% similarity")

def test_seed_reconstruction(keys):
    """Attempt to reconstruct a possible seed value"""
    print("\n" + "="*80)
    print("SEED RECONSTRUCTION ATTEMPT")
    print("="*80)

    print("\nIf k[n] = hash(seed || n), we can try to find patterns in the hash outputs")
    print("that might reveal information about the seed.\n")

    # Test common hash functions with various seeds
    test_seeds = [
        b"bitcoin",
        b"puzzle",
        b"satoshi",
        b"1",
        b"2015",  # Year puzzle created
        b"creator",
    ]

    sorted_n = sorted(keys.keys())[:5]  # Test first 5

    for seed in test_seeds:
        print(f"\nTesting seed: {seed.decode()}")

        matches = 0
        for n in sorted_n:
            k = keys[n]
            min_val = 2**(n-1)
            max_val = 2**n - 1

            # Test SHA256
            hash_input = seed + str(n).encode()
            hash_output = hashlib.sha256(hash_input).digest()
            hash_int = int.from_bytes(hash_output, byteorder='big')

            # Constrain to range
            range_size = max_val - min_val + 1
            k_predicted = min_val + (hash_int % range_size)

            if k_predicted == k:
                matches += 1
                print(f"  ✓ n={n}: MATCH!")

        if matches > 0:
            print(f"  Total matches: {matches}/{len(sorted_n)}")

def main():
    print("="*80)
    print("GAP PUZZLE PRNG/HASH ANALYSIS")
    print("="*80)

    keys = get_all_keys()
    print(f"\nLoaded {len(keys)} known keys from database\n")

    # Run all tests
    test_lcg_pattern(keys)
    test_hash_based_generation(keys)
    test_position_pattern(keys)
    test_alpha_function(keys)
    test_seed_reconstruction(keys)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
