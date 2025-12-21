#!/usr/bin/env python3
"""
Find patterns in offset sequence that can help predict offset[71].
"""
import sqlite3

# Get all k values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 71):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

# Compute offsets for n >= 34
offsets = {}
for n in range(34, 71):
    if n in k_values and (n-3) in k_values:
        offsets[n] = k_values[n] - 9*k_values[n-3]

print("=" * 70)
print("OFFSET PATTERN ANALYSIS")
print("=" * 70)
print()

# First differences
print("### Offset values and first differences ###")
d1 = {}
for n in range(35, 71):
    if n in offsets and (n-1) in offsets:
        d1[n] = offsets[n] - offsets[n-1]

# Second differences
print("### Second differences ###")
d2 = {}
for n in range(36, 71):
    if n in d1 and (n-1) in d1:
        d2[n] = d1[n] - d1[n-1]

# Show recent data
print("n\t| offset[n]\t\t\t| d1[n]\t\t\t| d2[n]")
print("-" * 100)
for n in range(60, 71):
    off = offsets.get(n, "?")
    delta = d1.get(n, "?")
    delta2 = d2.get(n, "?")
    print(f"{n}\t| {off}\t| {delta}\t| {delta2}")

print()

# Look for ratio patterns
print("### Ratio patterns ###")
for n in range(65, 71):
    if n in offsets and (n-1) in offsets and offsets[n-1] != 0:
        ratio = offsets[n] / offsets[n-1]
        print(f"offset[{n}]/offset[{n-1}] = {ratio:.4f}")

print()

# Look for mod patterns
print("### Mod patterns ###")
for mod in [3, 7, 9, 11, 13, 17]:
    print(f"offset[n] mod {mod}:")
    for n in range(65, 71):
        if n in offsets:
            print(f"  offset[{n}] mod {mod} = {offsets[n] % mod}")
    print()

# Predict offset[71] using second difference pattern
print("### Offset[71] prediction using patterns ###")
d1_70 = d1.get(70)
d2_70 = d2.get(70)
if d1_70 and d2_70:
    # Assume d2 continues with similar pattern
    d2_71_est = d2_70  # Or could try d2_70 * (d2_70/d2[69])
    d1_71_est = d1_70 + d2_71_est
    offset_71_est = offsets[70] + d1_71_est
    print(f"Using constant d2: offset[71] = {offset_71_est}")
    
    # Check if in valid range
    min_k71 = 2**70
    max_k71 = 2**71 - 1
    k70 = k_values[70]
    
    # offset[71] = k[71] - 9*k[68]
    # k[71] = 9*k[68] + offset[71]
    k68 = k_values[68]
    k71_from_offset = 9*k68 + offset_71_est
    
    print(f"This gives k[71] = {k71_from_offset}")
    print(f"Valid range: [{min_k71}, {max_k71}]")
    print(f"In range: {min_k71 <= k71_from_offset <= max_k71}")

print()

# Try exponential fit
import math
print("### Exponential fit for |offset| ###")
log_offsets = []
for n in range(60, 71):
    if n in offsets and offsets[n] != 0:
        log_offsets.append((n, math.log(abs(offsets[n]))))

if len(log_offsets) >= 2:
    # Linear regression on log values
    n1, log1 = log_offsets[0]
    n2, log2 = log_offsets[-1]
    slope = (log2 - log1) / (n2 - n1)
    intercept = log1 - slope * n1
    
    log_offset_71 = slope * 71 + intercept
    offset_71_exp = math.exp(log_offset_71)
    
    # Determine sign based on pattern
    # Recent offsets are negative
    if offsets[70] < 0:
        offset_71_exp = -offset_71_exp
    
    print(f"Exponential fit: offset[71] ≈ {offset_71_exp:.2e}")
    
    k71_exp = 9*k_values[68] + int(offset_71_exp)
    print(f"This gives k[71] ≈ {k71_exp:.2e}")
    print(f"In valid range: {min_k71 <= k71_exp <= max_k71}")

print()
print("=" * 70)
