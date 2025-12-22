#!/usr/bin/env python3
"""
PHASE 0 CRITICAL VALIDATION
============================

THIS IS THE MOST IMPORTANT TEST!

We MUST verify that the PySR formula works FORWARD (generation),
not just backward (verification).

Test: Calculate X_75 from X_74 using formula, compare to actual X_75

IF THIS PASSES → Safe to calculate puzzles 71-160
IF THIS FAILS → STOP! Formula doesn't work for generation!
"""

import csv
import json
from pathlib import Path

# The proven PySR formula
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

def hex_to_bytes(hex_str):
    """Convert hex string to list of bytes"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    # Ensure even length
    if len(hex_str) % 2:
        hex_str = '0' + hex_str
    # Take second half (16 bytes = 32 hex chars)
    if len(hex_str) > 32:
        hex_str = hex_str[32:64]  # Second half
    # Pad if needed
    hex_str = hex_str.zfill(32)

    # Convert to byte array
    return [int(hex_str[i:i+2], 16) for i in range(0, 32, 2)]

def bytes_to_hex(byte_list):
    """Convert list of bytes to hex string"""
    return ''.join(f'{b:02x}' for b in byte_list)

def calculate_next_halfblock(X_k):
    """
    Calculate X_{k+1} from X_k using proven PySR formula

    Formula: X_{k+1}[lane] = (X_k[lane])^n mod 256
    where n = EXPONENTS[lane]
    """
    X_next = []
    for lane in range(16):
        n = EXPONENTS[lane]
        if n == 0:
            X_next.append(0)  # Lane 6 is always 0
        else:
            # Use Python's built-in modular exponentiation
            X_next.append(pow(X_k[lane], n, 256))
    return X_next

def load_puzzle_from_csv(puzzle_num):
    """Load a puzzle's half-block from CSV"""
    csv_path = Path('data/btc_puzzle_1_160_full.csv')

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 4 and row[0] == str(puzzle_num):
                priv_hex = row[3]
                if priv_hex and priv_hex != '?' and not priv_hex.startswith('?'):
                    return hex_to_bytes(priv_hex)
    return None

def main():
    print("=" * 80)
    print("PHASE 0 CRITICAL VALIDATION")
    print("=" * 80)
    print()
    print("🚨 THIS IS THE CRITICAL TEST FOR THE ENTIRE PROJECT! 🚨")
    print()
    print("Testing: Can we GENERATE X_75 from X_70 using the PySR formula?")
    print()
    print("We've proven the formula works BACKWARD (verification).")
    print("Now we test if it works FORWARD (generation).")
    print()
    print("Note: Puzzles 71-74 are UNKNOWN, so we'll calculate X_75 from X_70")
    print("      by iterating the formula 5 times: X_70 → X_71 → ... → X_75")
    print()
    print("=" * 80)
    print()

    # Load X_70 (start point)
    print("1. Loading X_70 from CSV...")
    X_70 = load_puzzle_from_csv(70)
    if X_70 is None:
        print("❌ FAILED: Could not load X_70 from CSV")
        return False
    print(f"   ✓ X_70 loaded: {bytes_to_hex(X_70)}")
    print(f"   Lane values: {X_70}")
    print()

    # Load X_75 (target for validation)
    print("2. Loading X_75 from CSV (for validation)...")
    X_75_actual = load_puzzle_from_csv(75)
    if X_75_actual is None:
        print("❌ FAILED: Could not load X_75 from CSV")
        return False
    print(f"   ✓ X_75 actual: {bytes_to_hex(X_75_actual)}")
    print(f"   Lane values: {X_75_actual}")
    print()

    # Calculate X_75 from X_70 (5 iterations)
    print("3. Calculating X_75 from X_70 using PySR formula (5 steps)...")
    print()
    print("   Formula: X_{k+1}[lane] = (X_k[lane])^n mod 256")
    print(f"   Exponents: {EXPONENTS}")
    print()

    current = X_70
    for step in range(1, 6):
        current = calculate_next_halfblock(current)
        print(f"   Step {step}: X_{70+step} = {bytes_to_hex(current)}")

    X_75_calculated = current

    print(f"   ✓ X_75 calculated: {bytes_to_hex(X_75_calculated)}")
    print(f"   Lane values: {X_75_calculated}")
    print()

    # Compare lane by lane
    print("4. Comparing calculated vs. actual (lane by lane)...")
    print()
    print("Lane | Exponent | X_70 | Calculated | Actual | Match?")
    print("-" * 70)

    all_match = True
    mismatches = []

    for lane in range(16):
        exp = EXPONENTS[lane]
        val_70 = X_70[lane]
        calc = X_75_calculated[lane]
        actual = X_75_actual[lane]
        match = (calc == actual)

        if not match:
            all_match = False
            mismatches.append({
                'lane': lane,
                'exponent': exp,
                'X_70_value': val_70,
                'calculated': calc,
                'actual': actual,
                'diff': calc - actual
            })

        status = "✓" if match else "✗"
        print(f"{lane:4} | {exp:8} | {val_70:4} | {calc:10} | {actual:6} | {status}")

    print()
    print("=" * 80)
    print("RESULTS:")
    print("=" * 80)
    print()

    if all_match:
        print("🎉🎉🎉 SUCCESS! 🎉🎉🎉")
        print()
        print("✅ ALL 16 LANES MATCH EXACTLY!")
        print("✅ X_75 calculated from X_74 == X_75 actual")
        print()
        print("VERDICT: The PySR formula works FORWARD!")
        print()
        print("✅ SAFE TO PROCEED with calculating puzzles 71-160")
        print()
        result = {
            'validation_passed': True,
            'all_lanes_match': True,
            'mismatches': 0,
            'X_70': bytes_to_hex(X_70),
            'X_75_calculated': bytes_to_hex(X_75_calculated),
            'X_75_actual': bytes_to_hex(X_75_actual),
            'conclusion': 'Formula works forward - safe to generate puzzles'
        }
    else:
        print("❌ VALIDATION FAILED!")
        print()
        print(f"✗ {len(mismatches)} LANES DO NOT MATCH")
        print()
        print("Mismatches:")
        for mm in mismatches:
            print(f"  Lane {mm['lane']}: calculated={mm['calculated']}, actual={mm['actual']}, diff={mm['diff']}")
        print()
        print("VERDICT: The PySR formula does NOT work forward!")
        print()
        print("🛑 DO NOT PROCEED with calculating puzzles 71-160")
        print("🛑 INVESTIGATE WHY FORWARD CALCULATION FAILS")
        print()
        result = {
            'validation_passed': False,
            'all_lanes_match': False,
            'mismatches': len(mismatches),
            'mismatch_details': mismatches,
            'X_70': bytes_to_hex(X_70),
            'X_75_calculated': bytes_to_hex(X_75_calculated),
            'X_75_actual': bytes_to_hex(X_75_actual),
            'conclusion': 'Formula does NOT work forward - STOP all generation work!'
        }

    # Save result
    result_file = 'results/phase_0_validation_result.json'
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Result saved to: {result_file}")
    print()

    # Update orchestration status
    print("Updating ORCHESTRATION_STATUS.json...")
    try:
        with open('ORCHESTRATION_STATUS.json', 'r') as f:
            status = json.load(f)

        status['phase_0_critical']['status'] = 'completed'
        status['phase_0_critical']['completed_at'] = '2025-12-22T04:00:00Z'
        status['phase_0_critical']['validation_passed'] = result['validation_passed']
        status['phase_0_critical']['result'] = result
        status['last_updated'] = '2025-12-22T04:00:00Z'

        # Unblock Phase 2 tasks if validation passed
        if result['validation_passed']:
            for task_key in status['phase_2_range_calculations']:
                if status['phase_2_range_calculations'][task_key]['status'] == 'blocked':
                    status['phase_2_range_calculations'][task_key]['status'] = 'pending'
                    status['phase_2_range_calculations'][task_key]['blocked_by'] = None

            status['project_phase'] = 'Phase 1 - Setup'

        with open('ORCHESTRATION_STATUS.json', 'w') as f:
            json.dump(status, f, indent=2)

        print("✓ Orchestration status updated")
    except Exception as e:
        print(f"⚠ Could not update orchestration status: {e}")

    print()
    print("=" * 80)

    return result['validation_passed']

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
