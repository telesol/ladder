#!/usr/bin/env python3
"""
Verify Byte Order on ALL Transitions
=====================================

Test reversed byte order on ALL 69 transitions (1→70)
"""

import json
import csv

def load_A_values():
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        calib = json.load(f)
    return [calib['A'][str(i)] for i in range(16)]

def hex_to_bytes_reversed(hex_str):
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    if len(hex_str) > 32:
        hex_str = hex_str[32:64]
    hex_str = hex_str.zfill(32)
    return [int(hex_str[i:i+2], 16) for i in range(30, -1, -2)]

def load_puzzle(n):
    with open('data/btc_puzzle_1_160_full.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[0] == str(n) and row[3] and row[3] != '?':
                return row[3]
    return None

def verify_all():
    A = load_A_values()

    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        calib = json.load(f)
    drifts_data = calib.get('drifts', {})

    print("Testing reversed byte order on ALL 69 transitions...")
    print()

    total_matches = 0
    total_lanes = 0
    failures = []

    for k in range(1, 70):
        X_k_hex = load_puzzle(k)
        X_k1_hex = load_puzzle(k+1)

        if not X_k_hex or not X_k1_hex:
            continue

        drift_key = f"{k}→{k+1}"
        if drift_key not in drifts_data:
            continue

        drift = [drifts_data[drift_key][str(i)] for i in range(16)]

        # Use REVERSED byte order
        X_k = hex_to_bytes_reversed(X_k_hex)
        X_k1_actual = hex_to_bytes_reversed(X_k1_hex)

        # Calculate
        X_k1_calc = []
        for lane in range(16):
            a4 = pow(A[lane], 4, 256)
            x_next = (a4 * X_k[lane] + drift[lane]) % 256
            X_k1_calc.append(x_next)

        # Count matches
        matches = sum(1 for i in range(16) if X_k1_calc[i] == X_k1_actual[i])
        total_matches += matches
        total_lanes += 16

        if matches == 16:
            print(f"  {k}→{k+1}: ✓ 100% (16/16)")
        else:
            print(f"  {k}→{k+1}: ✗ {matches}/16 ({matches/16*100:.1f}%)")
            failures.append((k, matches))

    print()
    print("=" * 80)
    print(f"OVERALL: {total_matches}/{total_lanes} ({total_matches/total_lanes*100:.2f}%)")
    print("=" * 80)
    print()

    if total_matches == total_lanes:
        print("🎉🎉🎉 PERFECT 100%! Reversed byte order is CORRECT!")
    else:
        print(f"Failures: {len(failures)}")
        for k, matches in failures[:10]:
            print(f"  {k}→{k+1}: {matches}/16")

if __name__ == '__main__':
    verify_all()
