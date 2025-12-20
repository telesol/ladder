#!/usr/bin/env python3
"""
Refine k[71] search using constraint chain
==========================================

We found the estimate is off by only 29,637 in the chain to k[75].
Let's use this to narrow down the exact k[71].
"""

import sqlite3

# Load known k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

print("=" * 80)
print("REFINING k[71] USING CONSTRAINT CHAIN")
print("=" * 80)

k68 = k[68]
k69 = k[69]
k70 = k[70]
k75 = k[75]

# The constraint
# k[75] = 81×k[69] + 9×offset[72] + offset[75]
# k[72] = 9×k[69] + offset[72]
# k[71] = 9×k[68] + offset[71]

# Also: k[72] = 9×k[71] + offset[72] (from mod-3 recursion with step 1... wait, that's wrong)
# Actually: k[72] = 9×k[69] + offset[72] (mod-3 recursion)

# And: k[75] = 9×k[72] + offset[75]
#            = 9×(9×k[69] + offset[72]) + offset[75]
#            = 81×k[69] + 9×offset[72] + offset[75]

constraint = k75 - 81 * k69
print(f"Constraint: 9×offset[72] + offset[75] = {constraint}")

# From our estimate:
# offset[71] ≈ -303,043,283,711,645,253,632
# This gives chain error of +29,637

# The chain is:
# k[71] = 9×k[68] + offset[71]
# k[72] = 9×k[69] + offset[72]
# k[75] = 9×k[72] + offset[75] = 81×k[69] + 9×offset[72] + offset[75]

# The error comes from offset[72] and offset[75] estimates, not offset[71]!
# Because k[71] doesn't appear in the k[75] constraint directly.

# Let me reconsider...
# k[72] = 9 × k[69] + offset[72]   (using mod-3 recursion)
# k[73] = 9 × k[70] + offset[73]
# k[74] = 9 × k[71] + offset[74]   (uses k[71]!)
# k[75] = 9 × k[72] + offset[75]

# So k[75] is independent of k[71]!
# And k[74] depends on k[71].

# Let me use k[80] constraint instead:
# k[80] = 9^4 × k[68] + ... (involves k[71])

# Actually, let's trace the chain properly:
# k[71] = 9×k[68] + offset[71]
# k[74] = 9×k[71] + offset[74]
# k[77] = 9×k[74] + offset[77]
# k[80] = 9×k[77] + offset[80]

# So: k[80] = 9^4×k[68] + 9^3×offset[71] + 9^2×offset[74] + 9×offset[77] + offset[80]

k80 = k[80]
constraint80 = k80 - (9**4) * k68
print(f"\nConstraint from k[80]:")
print(f"729×offset[71] + 81×offset[74] + 9×offset[77] + offset[80] = {constraint80}")

# If we assume offsets grow with ratio r, then:
# offset[74] ≈ r^3 × offset[71]
# offset[77] ≈ r^6 × offset[71]
# offset[80] ≈ r^9 × offset[71]

# From our data, average ratio ≈ 1.356 per step
r = 1.356

print(f"\nAssuming ratio r = {r} per step:")
print(f"offset[74] ≈ r^3 × offset[71] = {r**3:.4f} × offset[71]")
print(f"offset[77] ≈ r^6 × offset[71] = {r**6:.4f} × offset[71]")
print(f"offset[80] ≈ r^9 × offset[71] = {r**9:.4f} × offset[71]")

# Substituting:
# 729×off71 + 81×(r^3×off71) + 9×(r^6×off71) + (r^9×off71) = constraint80
# off71 × (729 + 81×r^3 + 9×r^6 + r^9) = constraint80

coeff = 729 + 81 * (r**3) + 9 * (r**6) + (r**9)
print(f"\nCoefficient = 729 + 81×{r**3:.4f} + 9×{r**6:.4f} + {r**9:.4f} = {coeff:.4f}")

estimated_offset71 = constraint80 / coeff
print(f"Estimated offset[71] = {constraint80} / {coeff:.4f} = {estimated_offset71:.0f}")

# Compute estimated k[71]
base71 = 9 * k68
est_k71 = base71 + int(estimated_offset71)
print(f"\nEstimated k[71] = 9×k[68] + offset[71]")
print(f"               = {base71} + {int(estimated_offset71)}")
print(f"               = {est_k71}")

# Check if in valid range
if 2**70 <= est_k71 <= 2**71 - 1:
    print("✓ In valid 71-bit range!")
else:
    print("✗ Outside valid range!")

# Verify by chaining to k[80]
print("\n### VERIFICATION ###")
est_off74 = estimated_offset71 * (r**3)
est_off77 = estimated_offset71 * (r**6)
est_off80 = estimated_offset71 * (r**9)

est_k74 = 9 * est_k71 + int(est_off74)
est_k77 = 9 * est_k74 + int(est_off77)
est_k80 = 9 * est_k77 + int(est_off80)

print(f"Chain computation:")
print(f"  k[71] = {est_k71}")
print(f"  k[74] = 9×k[71] + offset[74] = {est_k74}")
print(f"  k[77] = 9×k[74] + offset[77] = {est_k77}")
print(f"  k[80] = 9×k[77] + offset[80] = {est_k80}")
print(f"\nActual k[80] = {k80}")
print(f"Difference   = {est_k80 - k80}")

# Now let's try to find exact value by searching near the estimate
print("\n### FINE-TUNING SEARCH ###")
print(f"Searching around offset[71] ≈ {int(estimated_offset71)}")

# The constraint must be satisfied exactly
# Let offset[71] = est + delta, where delta is small

# Search for delta that makes chain work
best_delta = 0
best_diff = abs(est_k80 - k80)

for delta in range(-1000000, 1000001):
    test_off71 = int(estimated_offset71) + delta
    test_k71 = base71 + test_off71

    if not (2**70 <= test_k71 <= 2**71 - 1):
        continue

    # Chain forward using fixed ratios
    test_k74 = 9 * test_k71 + int(test_off71 * (r**3))
    test_k77 = 9 * test_k74 + int(test_off71 * (r**6))
    test_k80 = 9 * test_k77 + int(test_off71 * (r**9))

    diff = abs(test_k80 - k80)
    if diff < best_diff:
        best_diff = diff
        best_delta = delta

print(f"Best delta: {best_delta}")
print(f"Best difference to k[80]: {best_diff}")

if best_diff == 0:
    final_off71 = int(estimated_offset71) + best_delta
    final_k71 = base71 + final_off71
    print(f"\n*** EXACT k[71] FOUND! ***")
    print(f"k[71] = {final_k71}")
    print(f"offset[71] = {final_off71}")
else:
    print("\nExact value not found - ratio assumption may be wrong")
    print("Need to search different offset patterns")
