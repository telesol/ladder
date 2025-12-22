#!/usr/bin/env python3
"""
Analyze drift patterns to understand what we're missing.
"""

import json

# Load drift data
with open('drift_data_CORRECT_BYTE_ORDER.json', 'r') as f:
    data = json.load(f)

transitions = data['transitions']

print("=== DRIFT PATTERN ANALYSIS ===\n")

# 1. When does each lane "activate" (first non-zero drift)?
print("1. LANE ACTIVATION PATTERN:")
lane_activation = {i: None for i in range(16)}
for t in transitions:
    k = t['from_puzzle']
    drifts = t['drifts']
    for lane in range(16):
        if drifts[lane] != 0 and lane_activation[lane] is None:
            lane_activation[lane] = k

for lane, k in lane_activation.items():
    if k is not None:
        print(f"   Lane {lane:2d}: First non-zero at k={k:2d}")
    else:
        print(f"   Lane {lane:2d}: ALWAYS ZERO")

# 2. Pattern hypothesis: Does lane L activate at k = L * 8?
print("\n2. TESTING HYPOTHESIS: lane L activates at k = L * 8")
predicted = {i: i * 8 if i < 8 else None for i in range(16)}
for lane in range(16):
    actual = lane_activation[lane]
    pred = predicted[lane]
    match = "✅" if actual == pred else "❌"
    print(f"   Lane {lane:2d}: predicted k={pred}, actual k={actual} {match}")

# 3. Conditional logic hypothesis
print("\n3. TESTING: Is drift conditional on k and lane?")
print("   Hypothesis: drift[k][lane] = 0 if k < lane * 8")
errors = 0
total = 0
for t in transitions:
    k = t['from_puzzle']
    drifts = t['drifts']
    for lane in range(16):
        total += 1
        # Hypothesis: drift should be 0 if k < lane * 8
        if k < lane * 8:
            if drifts[lane] != 0:
                errors += 1
                if errors <= 10:  # Show first 10 errors
                    print(f"   ERROR: k={k}, lane={lane}, drift={drifts[lane]} (should be 0)")

accuracy = 100 * (1 - errors/total)
print(f"\n   Conditional zero accuracy: {accuracy:.2f}% ({total-errors}/{total})")

# 4. For active lanes (k >= lane*8), what patterns exist?
print("\n4. DRIFT VALUES FOR ACTIVE LANES:")
active_drifts = {i: [] for i in range(16)}
for t in transitions:
    k = t['from_puzzle']
    drifts = t['drifts']
    for lane in range(16):
        if k >= lane * 8:  # Lane is active
            active_drifts[lane].append((k, drifts[lane]))

for lane in range(8):  # Only lanes 0-7 have non-trivial drift
    values = active_drifts[lane]
    if values:
        unique = set([v for k, v in values])
        print(f"\n   Lane {lane}: {len(values)} active transitions, {len(unique)} unique drift values")
        # Show first 15 values
        print(f"      First 15: {[v for k, v in values[:15]]}")
        # Check if it's a simple sequence
        if len(values) >= 3:
            diffs = [values[i+1][1] - values[i][1] for i in range(min(10, len(values)-1))]
            print(f"      First 10 differences: {diffs}")

print("\n" + "="*60)
