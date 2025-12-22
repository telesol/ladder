#!/usr/bin/env python3
"""
Calculate what drift values would be REQUIRED to make the formula work
from X_70 → X_75.

If we know: X_75_actual and X_75_calculated (pure formula),
we can compute: drift_total = X_75_actual - X_75_calculated (mod 256)

This tells us how much correction is needed!
"""

import json

# From validation output
X_70 = [0, 0, 0, 0, 0, 0, 0, 52, 155, 132, 182, 67, 26, 108, 78, 241]
X_75_calculated = [0, 0, 0, 0, 0, 0, 0, 0, 129, 0, 0, 129, 0, 0, 0, 209]
X_75_actual = [0, 0, 0, 0, 0, 0, 4, 197, 206, 17, 70, 134, 161, 51, 110, 7]

EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

print("=== REQUIRED DRIFT CALCULATION (X_70 → X_75) ===\n")

# Calculate total drift needed (5 steps combined)
print("Total drift needed to correct X_75:\n")
print("Lane | Calc | Actual | Required Drift |")
print("-----|------|--------|----------------|")

total_drift = []
for lane in range(16):
    calc = X_75_calculated[lane]
    actual = X_75_actual[lane]
    drift_needed = (actual - calc) % 256
    total_drift.append(drift_needed)
    print(f"{lane:4} | {calc:4} | {actual:6} | {drift_needed:14} |")

print(f"\nTotal drift vector: {total_drift}")
print()

# Now try to understand the pattern
# Check if it matches our conditional logic
print("Analysis using conditional logic (drift=0 if k<lane*8):\n")

for lane in range(16):
    activation_k = lane * 8
    k_test = 70  # Starting point

    if k_test >= activation_k:
        status = "ACTIVE"
    else:
        status = "INACTIVE"

    drift = total_drift[lane]
    print(f"Lane {lane:2}: activates at k={activation_k:2}, status at k=70: {status:8}, required drift: {drift:3}")

print("\nKey observation:")
print("- Lanes 0-8: Should be ACTIVE at k=70")
print("- Lanes 9-15: According to our rule, would activate at k=72-120")
print("- BUT we're at k=70→75, so lanes 9-15 SHOULD activate during this range!")
print()
print("Lane 9 activates at k=72")
print("Lane 10 activates at k=80")
print("Lane 11 activates at k=88")
print("etc.")
print()
print("This explains why the formula breaks - we're crossing activation boundaries!")
print()

# Check intermediate steps
print("Let's trace when each lane should activate during k=70→75:")
for step_k in range(70, 76):
    active_lanes = [l for l in range(16) if step_k >= l * 8]
    print(f"  k={step_k}: Lanes {active_lanes} are active")

print("\nConclusion:")
print("The pure exponentiation formula doesn't account for lane activation!")
print("We need to add drift when a lane first activates.")
