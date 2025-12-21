#!/usr/bin/env python3
"""
Predict adj[71] using offset formula and bridge constraints.

From the verified formula:
  offset[n] = k[n] - 9*k[n-3] = -k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]

This means:
  adj[n] = offset[n] + k[n-3] - 4*adj[n-2] - 2*adj[n-1]

We know adj[68], adj[69], adj[70]. If we can estimate offset[71], we get adj[71].
"""
import sqlite3

# Load k values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 91):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

# Compute adj values
adj = {}
for n in range(2, 71):
    if n in k_values and (n-1) in k_values:
        adj[n] = k_values[n] - 2*k_values[n-1]

# Compute offset values
offset = {}
for n in range(4, 71):
    if n in k_values and (n-3) in k_values:
        offset[n] = k_values[n] - 9*k_values[n-3]

print("=" * 70)
print("ADJ[71] PREDICTION VIA OFFSET FORMULA")
print("=" * 70)
print()

print("### Recent adj and offset values ###")
for n in range(65, 71):
    print(f"adj[{n}] = {adj[n]:>30}")
for n in range(65, 71):
    print(f"offset[{n}] = {offset[n]:>28}")

print()
print("### Offset growth pattern ###")
for n in range(66, 71):
    ratio = offset[n] / offset[n-1]
    print(f"offset[{n}]/offset[{n-1}] = {ratio:.4f}")

# Predict offset[71] using different models
print()
print("### Offset[71] predictions ###")

# Model 1: Recent ratio
ratio_70 = offset[70] / offset[69]
off71_ratio = offset[70] * ratio_70
print(f"Model 1 (recent ratio {ratio_70:.4f}): offset[71] = {off71_ratio:.4e}")

# Model 2: Average of last 3 ratios
ratios = [offset[n]/offset[n-1] for n in range(68, 71)]
avg_ratio = sum(ratios) / len(ratios)
off71_avg = offset[70] * avg_ratio
print(f"Model 2 (avg ratio {avg_ratio:.4f}): offset[71] = {off71_avg:.4e}")

# Model 3: Second difference continuation
d1_69 = offset[69] - offset[68]
d1_70 = offset[70] - offset[69]
d2 = d1_70 - d1_69
d1_71 = d1_70 + d2
off71_d2 = offset[70] + d1_71
print(f"Model 3 (constant d2): offset[71] = {off71_d2:.4e}")

print()
print("### Computing adj[71] from offset[71] ###")
print()
print("Formula: adj[n] = offset[n] + k[n-3] - 4*adj[n-2] - 2*adj[n-1]")
print()

# adj[71] = offset[71] + k[68] - 4*adj[69] - 2*adj[70]
k68 = k_values[68]
adj69 = adj[69]
adj70 = adj[70]

print(f"k[68] = {k68}")
print(f"adj[69] = {adj69}")
print(f"adj[70] = {adj70}")
print()

for name, off71 in [("ratio", off71_ratio), ("avg", off71_avg), ("d2", off71_d2)]:
    adj71 = off71 + k68 - 4*adj69 - 2*adj70
    k71 = 2*k_values[70] + adj71
    print(f"{name:5}: adj[71] = {adj71:.4e}, k[71] = {k71:.4e}")
    
    # Check if in valid range
    min_k71 = 2**70
    max_k71 = 2**71 - 1
    in_range = min_k71 <= k71 <= max_k71
    print(f"        In range [{min_k71:.4e}, {max_k71:.4e}]: {in_range}")
    print()

# What offset[71] gives k[71] at the boundaries?
print("### Offset[71] bounds for valid k[71] ###")
print()

# k[71] = 2*k[70] + adj[71]
# adj[71] = offset[71] + k68 - 4*adj69 - 2*adj70
# k[71] = 2*k[70] + offset[71] + k68 - 4*adj69 - 2*adj70
# Let C = 2*k[70] + k68 - 4*adj69 - 2*adj70
# k[71] = offset[71] + C

k70 = k_values[70]
C = 2*k70 + k68 - 4*adj69 - 2*adj70
print(f"C = 2*k[70] + k[68] - 4*adj[69] - 2*adj[70] = {C:.4e}")
print()

off71_for_min = min_k71 - C
off71_for_max = max_k71 - C
print(f"For k[71] = min: offset[71] = {off71_for_min:.4e}")
print(f"For k[71] = max: offset[71] = {off71_for_max:.4e}")
print()

# Compare to predictions
print("### Comparison ###")
print(f"Predicted offset[71] (ratio): {off71_ratio:.4e}")
print(f"Valid range: [{off71_for_min:.4e}, {off71_for_max:.4e}]")
print(f"Predicted in range: {off71_for_min <= off71_ratio <= off71_for_max}")
print()
print("=" * 70)
