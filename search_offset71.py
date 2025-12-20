#!/usr/bin/env python3
"""
Search for offset[71] formula
=============================

offset[71] = a×k[i] + b×k[j] + c×k[m] + d×k[p] + e

We know:
- offset[71] ∈ [-7.98×10^20, +3.82×10^20]
- k[71] = 9 × k[68] + offset[71]
- k[71] must be in [2^70, 2^71-1]
"""

import sqlite3
from itertools import combinations

# Load known k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

print("=" * 80)
print("SEARCHING FOR offset[71] FORMULA")
print("=" * 80)

# Known values
k68 = k[68]
k69 = k[69]
k70 = k[70]
k75 = k[75]

base_71 = 9 * k68
min_k71 = 2**70
max_k71 = 2**71 - 1

print(f"\nk[68] = {k68}")
print(f"k[69] = {k69}")
print(f"k[70] = {k70}")
print(f"\n9×k[68] = {base_71}")
print(f"Valid k[71] range: [{min_k71}, {max_k71}]")

offset_min = min_k71 - base_71
offset_max = max_k71 - base_71
print(f"offset[71] range: [{offset_min}, {offset_max}]")

# Analyze offset pattern from n=60-70
print("\n### OFFSET PATTERN n=60-70 ###")
offsets = {}
for n in range(60, 71):
    offsets[n] = k[n] - 9 * k[n-3]
    print(f"offset[{n}] = {offsets[n]}")

# Look for ratio pattern
print("\n### OFFSET RATIO PATTERN ###")
for n in range(61, 71):
    ratio = offsets[n] / offsets[n-1] if offsets[n-1] != 0 else 0
    print(f"offset[{n}] / offset[{n-1}] = {ratio:.4f}")

# Extrapolate offset[71]
print("\n### EXTRAPOLATION ###")
# Average ratio
ratios = []
for n in range(63, 71):
    if offsets[n-1] != 0:
        ratios.append(offsets[n] / offsets[n-1])

avg_ratio = sum(ratios) / len(ratios)
print(f"Average ratio: {avg_ratio:.4f}")

predicted_offset71 = offsets[70] * avg_ratio
print(f"Predicted offset[71] ≈ offset[70] × {avg_ratio:.4f}")
print(f"                    ≈ {predicted_offset71:.0f}")

# Check if this is in valid range
predicted_k71 = base_71 + int(predicted_offset71)
print(f"\nPredicted k[71] = 9×k[68] + offset[71]")
print(f"               = {base_71} + {int(predicted_offset71)}")
print(f"               = {predicted_k71}")

if min_k71 <= predicted_k71 <= max_k71:
    print("✓ Predicted k[71] is in valid range!")
else:
    print("✗ Predicted k[71] is outside valid range")

# Now search for exact formula
print("\n### SEARCHING FOR EXACT FORMULA ###")
print("Testing offset[71] = a×k[67] + b×k[68] + c×k[69] + d×k[70] + e")

# Use the constraint from k[75]:
# k[75] = 81×k[69] + 9×offset[72] + offset[75]
# offset[72] = k[72] - 9×k[69]
# k[72] = 9×k[69] + offset[72]

# And k[75] = 9×k[72] + offset[75]
#           = 9×(9×k[69] + offset[72]) + offset[75]
#           = 81×k[69] + 9×offset[72] + offset[75]

# We know: 9×offset[72] + offset[75] = k[75] - 81×k[69]
constraint_72_75 = k75 - 81 * k69
print(f"\nConstraint: 9×offset[72] + offset[75] = {constraint_72_75}")

# If we assume offset[72] follows the same pattern as earlier offsets...
# offset[72] ≈ offset[71] × ratio
# Then: 9 × (offset[71] × ratio) + offset[75] = constraint

# Let's estimate offset[72] and offset[75]
estimated_offset71 = predicted_offset71
estimated_offset72 = estimated_offset71 * avg_ratio
estimated_offset75 = constraint_72_75 - 9 * estimated_offset72

print(f"\nEstimates based on average ratio {avg_ratio:.4f}:")
print(f"  offset[71] ≈ {estimated_offset71:.0f}")
print(f"  offset[72] ≈ {estimated_offset72:.0f}")
print(f"  offset[75] ≈ {estimated_offset75:.0f}")

# Verify chain
print("\n### VERIFICATION CHAIN ###")
est_k71 = base_71 + int(estimated_offset71)
est_k72 = 9 * est_k71 + int(estimated_offset72)
est_k75_from_chain = 81 * k69 + int(9 * estimated_offset72 + estimated_offset75)

print(f"Estimated k[71] = {est_k71}")
print(f"Estimated k[72] = {est_k72}")
print(f"Chain to k[75]  = {est_k75_from_chain}")
print(f"Actual k[75]    = {k75}")
print(f"Difference      = {est_k75_from_chain - k75}")

# Final summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"""
Based on offset ratio extrapolation:
- offset[71] ≈ {int(predicted_offset71)}
- k[71] ≈ {predicted_k71}

But this is an ESTIMATE. To find the exact value:
1. We need the exact formula for offset[71]
2. The formula should be: offset[71] = Σ aᵢ × k[iᵢ] + c
3. Previous patterns suggest coefficients are small integers

The search space is too large for brute force.
We need to find the PATTERN that generates the coefficients.
""")
