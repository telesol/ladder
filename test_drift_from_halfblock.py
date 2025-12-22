#!/usr/bin/env python3
"""
NEW HYPOTHESIS: Active drift depends on the half-block X[k] itself.
Test if drift[k][lane] = f(X_k[lane]) for active lanes.
"""

import json
import sqlite3

# Load drift data
with open('drift_data_CORRECT_BYTE_ORDER.json', 'r') as f:
    drift_data = json.load(f)

# Load half-blocks from database
conn = sqlite3.connect('db/kh.db')
cursor = conn.cursor()

print("=== TESTING: drift[k][lane] = f(X_k[lane]) ===\n")

# Get half-blocks from database
cursor.execute("""
    SELECT bits, actual_hex
    FROM lcg_residuals
    WHERE bits BETWEEN 1 AND 70
    ORDER BY bits
""")
rows = cursor.fetchall()

halfblocks = {}
for bits, hex_str in rows:
    # Remove '0x' prefix, get last 32 hex chars (second half)
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    # Extract second half (last 32 hex chars = 16 bytes)
    second_half = hex_str[-32:]
    halfblocks[bits] = bytes.fromhex(second_half)

print(f"Loaded {len(halfblocks)} half-blocks from database\n")

# Build (X_k[lane], drift[k→k+1][lane]) pairs for active lanes
lane_mappings = {lane: {} for lane in range(16)}  # Maps X value to set of drift values

for t in drift_data['transitions']:
    k_from = t['from_puzzle']
    k_to = t['to_puzzle']
    drifts = t['drifts']

    if k_from not in halfblocks:
        continue

    X_k = halfblocks[k_from]

    for lane in range(16):
        if k_from >= lane * 8:  # Lane is active
            x_val = X_k[lane]
            drift_val = drifts[lane]

            if x_val not in lane_mappings[lane]:
                lane_mappings[lane][x_val] = []
            lane_mappings[lane][x_val].append(drift_val)

# Analyze if drift is deterministic function of X
print("1. IS DRIFT A FUNCTION OF X[k][lane]?\n")
print("   Testing if same X value always gives same drift\n")

for lane in range(9):  # Lanes 0-8
    mapping = lane_mappings[lane]
    if not mapping:
        continue

    # Check if mapping is deterministic (each X maps to exactly one drift)
    deterministic = True
    total_x_values = len(mapping)
    multi_valued = 0

    for x_val, drift_vals in mapping.items():
        unique_drifts = set(drift_vals)
        if len(unique_drifts) > 1:
            deterministic = False
            multi_valued += 1

    # Calculate coverage: how many unique X values seen vs theoretical max (256)
    coverage = 100 * total_x_values / 256

    if deterministic:
        print(f"   Lane {lane}: ✅ DETERMINISTIC! {total_x_values} X values seen ({coverage:.1f}% coverage)")
    else:
        print(f"   Lane {lane}: ❌ NOT deterministic ({multi_valued}/{total_x_values} X values map to multiple drifts)")

# For lanes that are deterministic, show the mapping
print("\n2. DETERMINISTIC MAPPINGS (if any):\n")

for lane in range(9):
    mapping = lane_mappings[lane]
    if not mapping:
        continue

    # Check if deterministic
    is_det = True
    for x_val, drift_vals in mapping.items():
        if len(set(drift_vals)) > 1:
            is_det = False
            break

    if is_det:
        # Create clean mapping
        clean_map = {x: drift_vals[0] for x, drift_vals in mapping.items()}

        print(f"   Lane {lane} mapping: X[k][{lane}] → drift[k][{lane}]")
        # Show first 20 entries
        items = sorted(clean_map.items())[:20]
        for x, d in items:
            print(f"      X={x:3d} → drift={d:3d}")
        if len(clean_map) > 20:
            print(f"      ... ({len(clean_map)-20} more entries)")

        # Test if it's a simple function (linear mod 256)
        # drift = (a * X + b) mod 256
        best_a, best_b, best_matches = 0, 0, 0
        for a in range(256):
            for b in range(256):
                matches = 0
                for x, d in clean_map.items():
                    if (a * x + b) % 256 == d:
                        matches += 1
                if matches > best_matches:
                    best_a, best_b, best_matches = a, b, matches

        acc = 100 * best_matches / len(clean_map)
        if acc > 50:
            print(f"      Best linear fit: drift = ({best_a}*X + {best_b}) mod 256, accuracy={acc:.1f}%")
        print()

print("="*70)

conn.close()
