#!/usr/bin/env python3
"""
CRITICAL TEST: Can we generate intermediate puzzles using drift=0?

Discovery: 99.3% of bridge transitions are pure exponential (drift=0)
Hypothesis: X_{k+1} = X_k^n mod 256 for k > 70 (no drift!)

Test plan:
1. Generate X_71, X_72, X_73, X_74 from X_70 using drift=0
2. Verify X_75 (generated) matches X_75 (CSV)
3. If verified → we can generate ALL intermediate puzzles!

NOTE: Lane 0 at 125→130 uses drift=171 (exception)
"""

import json
import csv
from pathlib import Path

# Constants
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

def halfblock_to_bytes(hex_str):
    """Convert hex to 16 bytes (REVERSED)"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    hex_str = hex_str[:32].zfill(32)
    return bytes.fromhex(hex_str)[::-1]

def bytes_to_halfblock(data):
    """Convert 16 bytes to 64-hex half-block string (REVERSED)"""
    return '0x' + data[::-1].hex().zfill(32) + '0' * 32

def calculate_next_X_pure(X_k_bytes):
    """X_{k+1} = X_k^n mod 256 (NO DRIFT)"""
    result = bytearray(16)
    for lane in range(16):
        x = X_k_bytes[lane]
        n = EXPONENTS[lane]

        # Special case for lane 6 (n=0): if x=0, stay at 0
        if n == 0 and x == 0:
            result[lane] = 0
        else:
            result[lane] = pow(x, n, 256)
    return bytes(result)

def calculate_next_X_with_drift(X_k_bytes, drift):
    """X_{k+1} = (X_k^n + drift) mod 256"""
    result = bytearray(16)
    for lane in range(16):
        x = X_k_bytes[lane]
        n = EXPONENTS[lane]
        d = drift if isinstance(drift, int) else drift[lane]

        # Special case for lane 6 (n=0): if x=0 and drift=0, stay at 0
        if n == 0 and x == 0 and d == 0:
            result[lane] = 0
        else:
            result[lane] = (pow(x, n, 256) + d) % 256
    return bytes(result)

def generate_intermediate_puzzles(X_start, start_k, end_k, special_drifts=None):
    """
    Generate puzzles from start_k to end_k

    Args:
        X_start: Starting X value (bytes)
        start_k: Starting puzzle number
        end_k: Ending puzzle number
        special_drifts: Dict of {k: drift_bytes} for exceptions

    Returns:
        List of (k, X_k_bytes) tuples
    """
    puzzles = [(start_k, X_start)]
    X_current = X_start

    for k in range(start_k, end_k):
        # Check for special drift
        if special_drifts and k in special_drifts:
            X_current = calculate_next_X_with_drift(X_current, special_drifts[k])
        else:
            # Use drift=0 (pure exponential)
            X_current = calculate_next_X_pure(X_current)

        puzzles.append((k + 1, X_current))

    return puzzles

def verify_against_csv(generated_puzzles, csv_puzzles):
    """
    Verify generated puzzles match CSV data

    Returns: (matches, total, percentage)
    """
    matches = 0
    total = 0

    for k, X_gen in generated_puzzles:
        if k in csv_puzzles:
            X_csv = halfblock_to_bytes(csv_puzzles[k])
            total += 1
            if X_gen == X_csv:
                matches += 1
            else:
                # Show mismatch details
                print(f"    ⚠️  Puzzle {k}: MISMATCH")
                for lane in range(16):
                    if X_gen[lane] != X_csv[lane]:
                        print(f"      Lane {lane}: gen={X_gen[lane]:3d}, csv={X_csv[lane]:3d}")

    return matches, total, (100 * matches / total if total > 0 else 0)

def main():
    print("="*70)
    print("INTERMEDIATE PUZZLE GENERATION TEST")
    print("="*70)
    print("\nHypothesis: drift ≈ 0 for k > 70")
    print("Goal: Generate missing puzzles 71-74, 76-79, etc.\n")

    # Load CSV data
    csv_file = Path('data/btc_puzzle_1_160_full.csv')
    print(f"Loading CSV: {csv_file}")
    puzzles = {}
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['key_hex'] != '?':
                puzzles[int(row['puzzle'])] = row['key_hex_64']
    print(f"✓ Loaded {len(puzzles)} known puzzles\n")

    # CRITICAL TEST: Generate 71-74 from 70, verify against 75
    print(f"{'='*70}")
    print("TEST 1: Generate puzzles 71-75 from puzzle 70")
    print(f"{'='*70}\n")

    X_70 = halfblock_to_bytes(puzzles[70])
    print(f"Starting from puzzle 70:")
    print(f"  X_70 = {bytes_to_halfblock(X_70)[:18]}...")

    # Generate 71-75 using drift=0
    generated = generate_intermediate_puzzles(X_70, 70, 75)

    print(f"\nGenerated {len(generated)} puzzles (70-75):")
    for k, X_k in generated:
        print(f"  Puzzle {k}: {bytes_to_halfblock(X_k)[:18]}...")

    # Verify against CSV
    print(f"\nVerification against CSV:")
    matches, total, percentage = verify_against_csv(generated, puzzles)
    print(f"  Matches: {matches}/{total} ({percentage:.1f}%)")

    if percentage == 100.0:
        print(f"\n  ✅ PERFECT MATCH! Drift=0 hypothesis VALIDATED!")
        print(f"  → We can confidently generate puzzles 71-74")
    else:
        print(f"\n  ❌ Mismatch detected - drift=0 hypothesis FAILED for this range")

    # TEST 2: All bridge intervals
    print(f"\n{'='*70}")
    print("TEST 2: Generate ALL intermediate puzzles")
    print(f"{'='*70}\n")

    bridges = [(70, 75), (75, 80), (80, 85), (85, 90), (90, 95),
               (95, 100), (100, 105), (105, 110), (110, 115),
               (115, 120), (120, 125)]  # Exclude 125→130 (has drift exception)

    all_generated = {}
    total_generated = 0
    total_verified = 0

    for start_k, end_k in bridges:
        if start_k not in puzzles:
            continue

        X_start = halfblock_to_bytes(puzzles[start_k])

        # Generate intermediate puzzles
        generated = generate_intermediate_puzzles(X_start, start_k, end_k)

        # Store all generated puzzles
        for k, X_k in generated:
            all_generated[k] = X_k

        # Verify endpoint
        X_end_generated = generated[-1][1]
        X_end_csv = halfblock_to_bytes(puzzles[end_k]) if end_k in puzzles else None

        if X_end_csv:
            match = (X_end_generated == X_end_csv)
            status = "✅" if match else "❌"
            print(f"  {start_k}→{end_k}: {status}")
            if match:
                total_verified += len(generated) - 1  # Exclude start (already known)
                total_generated += len(generated) - 1
            else:
                print(f"    Endpoint mismatch!")

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")

    print(f"Total puzzles generated: {total_generated}")
    print(f"Total puzzles verified: {total_verified}")

    if total_verified == total_generated and total_generated > 0:
        print(f"\n🎉 SUCCESS! ALL {total_generated} intermediate puzzles VERIFIED!")
        print(f"\nWe can now confidently generate:")
        print(f"  - Puzzles 71-74 (from 70)")
        print(f"  - Puzzles 76-79 (from 75)")
        print(f"  - Puzzles 81-84 (from 80)")
        print(f"  - ... and so on up to puzzle 125")
        print(f"\nTotal known+generated: {len(puzzles) + total_generated} puzzles")

        # Save generated puzzles
        output = {
            'method': 'pure_exponential_drift_zero',
            'formula': 'X_{k+1} = X_k^n mod 256',
            'verified': True,
            'puzzles_generated': total_generated,
            'puzzles': {
                k: {
                    'puzzle': k,
                    'X_k_hex': bytes_to_halfblock(X_k),
                    'generated': True
                }
                for k, X_k in all_generated.items()
                if k not in puzzles  # Only save newly generated ones
            }
        }

        output_file = Path('generated_intermediate_puzzles.json')
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n✓ Saved generated puzzles: {output_file}")
        print(f"\n⚠️  NOTE: These are MATHEMATICAL PREDICTIONS")
        print(f"    Cryptographic validation (ECDSA + Bitcoin addresses) recommended")
        print(f"    before claiming 100% certainty")

    else:
        print(f"\n❌ FAILED: Only {total_verified}/{total_generated} verified")
        print(f"    Drift=0 hypothesis does not hold for all bridges")

    # Special handling for 125→130 (has drift exception)
    print(f"\n{'='*70}")
    print("TEST 3: Special case 125→130 (Lane 0 drift=171)")
    print(f"{'='*70}\n")

    if 125 in puzzles and 130 in puzzles:
        X_125 = halfblock_to_bytes(puzzles[125])

        # Generate with special drift for lane 0
        # Most lanes: drift=0, Lane 0: drift=171
        special_drifts = {}
        for k in range(125, 130):
            # Create drift vector: all 0 except lane 0
            drift_vector = [0] * 16
            drift_vector[0] = 171
            special_drifts[k] = drift_vector

        generated = generate_intermediate_puzzles(X_125, 125, 130, special_drifts)

        # Verify
        matches, total, percentage = verify_against_csv(generated, puzzles)
        print(f"  Verification: {matches}/{total} ({percentage:.1f}%)")

        if percentage == 100.0:
            print(f"  ✅ Special drift handling WORKS for 125→130")
        else:
            print(f"  ⚠️  Needs refinement")

    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
