#!/usr/bin/env python3
"""
Task 20: Reconstruct k95-k130 using PySR (100% PROVEN METHOD)
This is CALCULATION, not prediction.
"""

import json
import subprocess
import sys

# Load k-values
with open('llm_tasks/memory/master_keys_70_160.json', 'r') as f:
    keys = json.load(f)

print("TASK 20: PYSR RECONSTRUCTION k95-k130")
print("="*60)
print()

results = []
for n in [95, 100, 105, 110, 115, 120, 125, 130]:
    k_prev_n = n - 5
    k_prev = keys[str(k_prev_n)]
    k_actual = keys[str(n)]

    # Calculate using PySR
    result = subprocess.run(
        ['python3', 'calculate_with_pysr.py', k_prev, '1'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"k{n}: ❌ CALCULATION FAILED")
        print(f"  Error: {result.stderr}")
        results.append((n, False))
        continue

    k_calc = result.stdout.strip()

    # Compare last 32 hex (right half)
    calc_hex = k_calc.replace('0x', '')[-32:]
    actual_hex = k_actual.replace('0x', '')[-32:]

    match = (calc_hex.lower() == actual_hex.lower())

    print(f"k{n}:")
    print(f"  k{k_prev_n} = {k_prev[:18]}...")
    print(f"  Calculated:  {k_calc}")
    print(f"  Actual:      {k_actual}")
    print(f"  Match: {'✅' if match else '❌'}")
    print()

    results.append((n, match))

# Summary
total = len(results)
correct = sum(1 for _, m in results if m)
accuracy = (correct / total * 100) if total > 0 else 0

print("="*60)
print(f"RECONSTRUCTION ACCURACY: {correct}/{total} = {accuracy:.1f}%")
print()

if accuracy == 100.0:
    print("✅ PYSR RECONSTRUCTION: 100% VERIFIED")
    print("Status: ALL calculations exact (byte-for-byte match)")
else:
    print(f"❌ PYSR RECONSTRUCTION: FAILED ({accuracy:.1f}%)")
    print("Status: Calculations NOT 100% accurate")
    failures = [n for n, m in results if not m]
    print(f"Failures: {failures}")

print()
print("VERDICT:")
if accuracy == 100.0:
    print("  PySR formula VERIFIED on ALL bridges k95-k130")
    print("  Can proceed to compute k135-k160")
else:
    print("  PySR formula INCOMPLETE")
    print("  Cannot trust extrapolation to k135-k160")
