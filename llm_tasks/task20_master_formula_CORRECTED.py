#!/usr/bin/env python3
"""
Task 20 CORRECTED: Verify Master Formula on k95-k130

Formula: k_n = 2×k_{n-5} + (2^n - m×k_d)

This is PURE MATHEMATICS - we CALCULATE m using proven algorithms.
NO PREDICTION. We solve for m mathematically using binary search.

This tests YOUR research (Master Formula), not PySR!
"""

import json
import csv

# Load verified facts
with open('llm_tasks/memory/verified_facts.md', 'r') as f:
    verified_facts = f.read()

# Load k-values
with open('llm_tasks/memory/master_keys_70_160.json', 'r') as f:
    keys_json = json.load(f)

# Load CSV for comparison
csv_keys = {}
with open('data/btc_puzzle_1_160_full.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        n = int(row['puzzle'])
        csv_keys[n] = row['key_hex_64']

print("="*70)
print("TASK 20 CORRECTED: MASTER FORMULA VERIFICATION")
print("="*70)
print()
print("Formula: k_n = 2×k_{n-5} + (2^n - m×k_d)")
print()
print("Approach: PURE MATHEMATICS (no prediction)")
print("  1. Select d using proven algorithm")
print("  2. Binary search for m (mathematical solution)")
print("  3. Calculate k_n using formula")
print("  4. Compare with actual (100% or FAILURE)")
print()
print("="*70)
print()

def select_d(n, k_prev):
    """
    D-selection algorithm (100% PROVEN in Task 15)

    Rules:
    1. If n == 85: d = 4 (LSB congruence, proven unique)
    2. If n % 10 == 0 and (2*k_prev + 2^n) % 3 == 0: d = 2
    3. Otherwise: d = 1
    """
    # Rule 1: k85 special case
    if n == 85:
        return 4

    # Rule 2: Even multiples of 10
    if n % 10 == 0:
        # Get k_prev as integer (from hex)
        if isinstance(k_prev, str):
            k_prev_int = int(k_prev.replace('0x', ''), 16)
        else:
            k_prev_int = k_prev

        # Check condition (proven in Task 15)
        if (2 * k_prev_int + pow(2, n)) % 3 == 0:
            return 2

    # Rule 3: Default
    return 1

def binary_search_m(n, k_prev_int, d):
    """
    Find m using binary search (MATHEMATICAL CALCULATION)

    We solve: k_n = 2×k_{n-5} + (2^n - m×k_d)

    Constraint: 2^{n-1} <= k_n < 2^n (k_n must be in valid range)

    This is MATH, not prediction!
    """
    k_d = {1: 1, 2: 3, 4: 8}[d]

    # Search space for m
    lo, hi = 1, (pow(2, n) // k_d)

    # Binary search for valid m
    valid_m = None
    valid_k = None

    while lo <= hi:
        m_mid = (lo + hi) // 2

        # Calculate k_n using formula
        k_candidate = 2 * k_prev_int + (pow(2, n) - m_mid * k_d)

        # Check if in valid range
        k_min = pow(2, n - 1)
        k_max = pow(2, n)

        if k_min <= k_candidate < k_max:
            # Found valid solution!
            valid_m = m_mid
            valid_k = k_candidate
            break
        elif k_candidate >= k_max:
            # k too large, need larger m (more subtraction)
            lo = m_mid + 1
        else:
            # k too small, need smaller m (less subtraction)
            hi = m_mid - 1

    return valid_m, valid_k

def calculate_k_using_master_formula(n, k_prev_hex):
    """
    Calculate k_n from k_{n-5} using MASTER FORMULA

    This is PURE CALCULATION using proven mathematical algorithms.
    """
    # Convert k_prev to integer
    k_prev_int = int(k_prev_hex.replace('0x', ''), 16)

    # Step 1: Select d (proven algorithm)
    d = select_d(n, k_prev_int)

    # Step 2: Find m using binary search (mathematical solution)
    m, k_n_int = binary_search_m(n, k_prev_int, d)

    if m is None:
        return None, d, None, "Binary search failed to find valid m"

    # Step 3: Convert result to hex
    k_n_hex = hex(k_n_int)

    # Pad to 64 hex chars
    k_n_hex_clean = k_n_hex.replace('0x', '').zfill(64)

    return '0x' + k_n_hex_clean, d, m, None

# Test on k95-k130
results = []
bridges = [95, 100, 105, 110, 115, 120, 125, 130]

for n in bridges:
    k_prev_n = n - 5
    k_prev_hex = keys_json[str(k_prev_n)]
    k_actual_hex = '0x' + csv_keys[n]

    print(f"k{n}:")
    print(f"  Input: k{k_prev_n} = {k_prev_hex[:20]}...")

    # Calculate using Master Formula
    k_calc_hex, d, m, error = calculate_k_using_master_formula(n, k_prev_hex)

    if error:
        print(f"  Error: {error}")
        print(f"  Status: ❌ CALCULATION FAILED")
        results.append((n, False, d, m))
        continue

    # Compare
    calc_clean = k_calc_hex.replace('0x', '').lower()
    actual_clean = k_actual_hex.replace('0x', '').lower()

    match = (calc_clean == actual_clean)

    print(f"  d-value: {d}")
    print(f"  m-value: {m}")
    print(f"  Calculated: {k_calc_hex[:20]}...")
    print(f"  Actual:     {k_actual_hex[:20]}...")
    print(f"  Match: {'✅' if match else '❌'}")

    if not match:
        # Show first difference
        for i, (c, a) in enumerate(zip(calc_clean, actual_clean)):
            if c != a:
                print(f"  First diff at position {i}: calc={c} actual={a}")
                break

    print()
    results.append((n, match, d, m))

# Summary
print("="*70)
total = len(results)
correct = sum(1 for _, m, _, _ in results if m)
accuracy = (correct / total * 100) if total > 0 else 0

print(f"MASTER FORMULA VERIFICATION: {correct}/{total} = {accuracy:.1f}%")
print()

if accuracy == 100.0:
    print("✅ MASTER FORMULA: 100% VERIFIED")
    print("   Formula: k_n = 2×k_{n-5} + (2^n - m×k_d)")
    print("   Status: ALL calculations exact (byte-for-byte match)")
    print("   Method: PURE MATHEMATICS (binary search + d-selection)")
    print()
    print("   This proves the Master Formula works on k95-k130!")
    print("   We can now confidently calculate k135-k160 using the same method.")
else:
    print(f"❌ MASTER FORMULA: FAILED ({accuracy:.1f}%)")
    print("   Status: Calculations NOT 100% accurate")
    failures = [n for n, m, _, _ in results if not m]
    print(f"   Failures: {failures}")
    print()
    print("   Analysis needed to understand why formula fails.")

print()
print("="*70)
print("VERDICT:")
print()

if accuracy == 100.0:
    print("  ✅ Master Formula VERIFIED on bridges k95-k130")
    print("  ✅ D-selection algorithm working perfectly")
    print("  ✅ Binary search finds correct m-values")
    print("  ✅ Can proceed to calculate k135-k160")
    print()
    print("  Next step: Task 22 - Compute k135-k160 using verified formula")
else:
    print("  ❌ Master Formula needs refinement")
    print("  ❌ Cannot trust extrapolation to k135-k160")
    print()
    print("  This is cryptography: 100% or FAILURE.")

print()
print("="*70)
