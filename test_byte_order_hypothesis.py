#!/usr/bin/env python3
"""
CRITICAL TEST: Byte Order Hypothesis
=====================================

Hypothesis: We've been reading bytes in WRONG ORDER!

Current extraction: [0,0,0,0,0,0,0,52,155,132,182,67,26,108,78,241]
  - Lanes 0-6: ZERO (we fail on these - 6-71% accuracy)
  - Lanes 7-15: ACTIVE (we succeed - 82-100% accuracy)

Reversed extraction: [241,78,108,26,67,182,132,155,52,0,0,0,0,0,0,0]
  - Lanes 0-8: ACTIVE
  - Lanes 9-15: ZERO

TEST: Does reversing byte order make lanes 0-6 solvable?
"""

import json
import csv
from pathlib import Path

def load_A_values():
    """Load A values"""
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        calib = json.load(f)
    return [calib['A'][str(i)] for i in range(16)]

def hex_to_bytes_normal(hex_str):
    """Normal byte extraction (current method)"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    if len(hex_str) > 32:
        hex_str = hex_str[32:64]
    hex_str = hex_str.zfill(32)
    return [int(hex_str[i:i+2], 16) for i in range(0, 32, 2)]

def hex_to_bytes_reversed(hex_str):
    """Reversed byte extraction (test method)"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    if len(hex_str) > 32:
        hex_str = hex_str[32:64]
    hex_str = hex_str.zfill(32)
    # Extract in reverse order
    return [int(hex_str[i:i+2], 16) for i in range(30, -1, -2)]

def bytes_to_hex(byte_list):
    """Convert bytes to hex"""
    return ''.join(f'{b:02x}' for b in byte_list)

def load_puzzle(n):
    """Load puzzle"""
    with open('data/btc_puzzle_1_160_full.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[0] == str(n) and row[3] and row[3] != '?':
                return row[3]
    return None

def test_byte_order():
    """Test if byte order reversal solves the 70% barrier"""

    print("=" * 80)
    print("TESTING BYTE ORDER HYPOTHESIS")
    print("=" * 80)
    print()

    A = load_A_values()

    # Load calibration drift
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        calib = json.load(f)
    drifts_data = calib.get('drifts', {})

    # Test on transition 1→2
    X_1_hex = load_puzzle(1)
    X_2_hex = load_puzzle(2)

    print(f"Testing transition 1→2:")
    print(f"X_1 (hex): {X_1_hex}")
    print(f"X_2 (hex): {X_2_hex}")
    print()

    # Extract drift 1→2
    drift_key = "1→2"
    if drift_key not in drifts_data:
        print("ERROR: Drift 1→2 not found")
        return

    drift = [drifts_data[drift_key][str(i)] for i in range(16)]
    print(f"Drift 1→2: {drift}")
    print()

    # Test NORMAL byte order
    print("=" * 80)
    print("TEST 1: NORMAL byte order (current method)")
    print("=" * 80)
    print()

    X_1_normal = hex_to_bytes_normal(X_1_hex)
    X_2_normal = hex_to_bytes_normal(X_2_hex)

    print(f"X_1 lanes: {X_1_normal}")
    print(f"X_2 lanes: {X_2_normal}")
    print()

    # Calculate X_2 from X_1 using formula
    X_2_calc_normal = []
    for lane in range(16):
        a4 = pow(A[lane], 4, 256)
        x_next = (a4 * X_1_normal[lane] + drift[lane]) % 256
        X_2_calc_normal.append(x_next)

    matches_normal = sum(1 for i in range(16) if X_2_calc_normal[i] == X_2_normal[i])
    print(f"Calculated X_2: {X_2_calc_normal}")
    print(f"Actual X_2:     {X_2_normal}")
    print(f"Matches: {matches_normal}/16 ({matches_normal/16*100:.1f}%)")
    print()

    # Test REVERSED byte order
    print("=" * 80)
    print("TEST 2: REVERSED byte order (hypothesis)")
    print("=" * 80)
    print()

    X_1_rev = hex_to_bytes_reversed(X_1_hex)
    X_2_rev = hex_to_bytes_reversed(X_2_hex)

    print(f"X_1 lanes (reversed): {X_1_rev}")
    print(f"X_2 lanes (reversed): {X_2_rev}")
    print()

    # Calculate X_2 from X_1 with reversed bytes
    X_2_calc_rev = []
    for lane in range(16):
        a4 = pow(A[lane], 4, 256)
        x_next = (a4 * X_1_rev[lane] + drift[lane]) % 256
        X_2_calc_rev.append(x_next)

    matches_rev = sum(1 for i in range(16) if X_2_calc_rev[i] == X_2_rev[i])
    print(f"Calculated X_2: {X_2_calc_rev}")
    print(f"Actual X_2:     {X_2_rev}")
    print(f"Matches: {matches_rev}/16 ({matches_rev/16*100:.1f}%)")
    print()

    # Compare
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print()
    print(f"Normal order:   {matches_normal}/16 ({matches_normal/16*100:.1f}%)")
    print(f"Reversed order: {matches_rev}/16 ({matches_rev/16*100:.1f}%)")
    print()

    if matches_rev > matches_normal:
        print("🎉 BREAKTHROUGH! Reversed byte order is BETTER!")
        print("We've been reading the bytes backwards!")
    elif matches_normal > matches_rev:
        print("✓ Normal byte order is correct (as expected)")
    else:
        print("⚠️  Both orders give same result - byte order doesn't matter here")

    print()

    # Additional test: Check which lanes are zero
    print("=" * 80)
    print("LANE DISTRIBUTION")
    print("=" * 80)
    print()

    print("Normal order - Zero lanes:")
    zero_normal = [i for i, v in enumerate(X_1_normal) if v == 0]
    print(f"  X_1 zero lanes: {zero_normal}")

    print()
    print("Reversed order - Zero lanes:")
    zero_rev = [i for i, v in enumerate(X_1_rev) if v == 0]
    print(f"  X_1 zero lanes: {zero_rev}")

    print()
    print("CRITICAL OBSERVATION:")
    print(f"  Normal: lanes {zero_normal} are zero (we FAIL on these)")
    print(f"  Reversed: lanes {zero_rev} are zero (would these be easier?)")
    print()

if __name__ == '__main__':
    test_byte_order()
