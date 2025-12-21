#!/usr/bin/env python3
"""
Use bridge constraint from k[75] to constrain k[71].

3-step recursion: k[n] = 9*k[n-3] + offset[n]

Chain from k[68] to k[75]:
k[71] = 9*k[68] + offset[71]
k[72] = 9*k[69] + offset[72]
k[73] = 9*k[70] + offset[73]
k[74] = 9*k[71] + offset[74]
k[75] = 9*k[72] + offset[75]

If we assume offsets follow a pattern, we can constrain k[71].
"""
import sqlite3
import hashlib

# Get k values from database
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()

k_values = {}
for n in [1, 2, 5, 68, 69, 70, 75]:
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)

conn.close()

print("=" * 70)
print("SOLVING K[71] VIA BRIDGE CONSTRAINT TO K[75]")
print("=" * 70)
print()

k68 = k_values[68]
k69 = k_values[69]
k70 = k_values[70]
k75 = k_values[75]

print(f"k[68] = {k68}")
print(f"k[69] = {k69}")
print(f"k[70] = {k70}")
print(f"k[75] = {k75}")
print()

# From k[75] = 9*k[72] + offset[75]
# And k[72] = 9*k[69] + offset[72]
# We get: k[75] = 9*(9*k[69] + offset[72]) + offset[75]
#              = 81*k[69] + 9*offset[72] + offset[75]

# So: offset[75] + 9*offset[72] = k[75] - 81*k[69]
constraint_72_75 = k75 - 81*k69
print(f"Constraint: offset[75] + 9*offset[72] = {constraint_72_75}")
print()

# Similarly for k[74] = 9*k[71] + offset[74]
# And k[71] = 9*k[68] + offset[71]
# So: k[74] = 9*(9*k[68] + offset[71]) + offset[74] = 81*k[68] + 9*offset[71] + offset[74]

# And k[75] = 9*k[72] + offset[75]
# k[72] = 9*k[69] + offset[72]
# k[73] = 9*k[70] + offset[73]

# Let me work backwards from k[75]
# k[75] = 9*k[72] + offset[75]
# k[72] = (k[75] - offset[75]) / 9

print("### Backward propagation from k[75] ###")
print()

# If we knew offset[75], we could get k[72]
# Then if we knew offset[72], we could verify against k[69]

# Let's compute what offset values would work
# k[72] = 9*k[69] + offset[72]
# Also k[72] = (k[75] - offset[75]) / 9

# So: 9*k[69] + offset[72] = (k[75] - offset[75]) / 9
# 81*k[69] + 9*offset[72] = k[75] - offset[75]
# offset[75] + 9*offset[72] = k[75] - 81*k[69]

print(f"From k[75] - 81*k[69] = {constraint_72_75}")
print()

# Looking at offset patterns from verified data
import json
with open('data_for_csolver.json') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

# Compute adj values for recent n
adj_values = {}
for n in range(60, 71):
    cur_k = k_values.get(n)
    prev_k = k_values.get(n-1)
    if cur_k and prev_k:
        adj_values[n] = cur_k - 2*prev_k

# Get all k values first
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
for n in range(1, 71):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

# Compute offset values for n where we have data
print("### Offset values for recent n ###")
offsets = {}
for n in range(34, 71):
    if n in k_values and (n-3) in k_values:
        offset = k_values[n] - 9*k_values[n-3]
        offsets[n] = offset
        if n >= 65:
            print(f"offset[{n}] = {offset}")

print()

# Analyze offset pattern
print("### Offset pattern analysis ###")
off68 = offsets[68]
off69 = offsets[69]
off70 = offsets[70]

print(f"offset[68] = {off68}")
print(f"offset[69] = {off69}")
print(f"offset[70] = {off70}")
print()

print(f"offset[69] - offset[68] = {off69 - off68}")
print(f"offset[70] - offset[69] = {off70 - off69}")
print()

# Try to find pattern for offset[71]
# Using constraint: offset[75] + 9*offset[72] = k[75] - 81*k[69]

# From verified offset formula:
# offset[n] = -k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]

# For n=71:
# offset[71] = -k[68] + 4*adj[69] + 2*adj[70] + adj[71]

# We know k[68], adj[69], adj[70]
# adj[71] = k[71] - 2*k[70]
# k[71] = 9*k[68] + offset[71]

# Substituting:
# offset[71] = -k[68] + 4*adj[69] + 2*adj[70] + (9*k[68] + offset[71] - 2*k[70])
# 0 = -k[68] + 4*adj[69] + 2*adj[70] + 9*k[68] - 2*k[70]
# 0 = 8*k[68] + 4*adj[69] + 2*adj[70] - 2*k[70]

adj69 = k_values[69] - 2*k_values[68]
adj70 = k_values[70] - 2*k_values[69]

check = 8*k68 + 4*adj69 + 2*adj70 - 2*k70
print(f"### Verification of offset formula consistency ###")
print(f"8*k[68] + 4*adj[69] + 2*adj[70] - 2*k[70] = {check}")
print(f"(Should be 0 if formula is consistent)")
print()

# Since the formula is consistent, we can't determine k[71] from it alone
# We need additional constraints

# Let's use the k[75] constraint
# k[75] = 9^3 * k[66] + (something involving offsets 67-75)

# Actually, let's iterate: if k[71] = X, then:
# k[72] = 9*k[69] + offset[72]
# offset[72] = -k[69] + 4*adj[70] + 2*adj[71] + adj[72]
# adj[71] = k[71] - 2*k[70] = X - 2*k[70]
# adj[72] = k[72] - 2*k[71] = k[72] - 2*X

# This is getting complex. Let me try a different approach:
# Search for k[71] that satisfies the k[75] bridge constraint

print("### Searching k[71] via k[75] bridge ###")
print()

# We have verified offset formula:
# offset[n] = -k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]
# where adj[n] = k[n] - 2*k[n-1]

min_k71 = 2**70
max_k71 = 2**71 - 1

# Sample a few k[71] values and propagate to k[75]
samples = [
    min_k71,
    min_k71 + (max_k71 - min_k71) // 4,
    min_k71 + (max_k71 - min_k71) // 2,
    min_k71 + 3*(max_k71 - min_k71) // 4,
    max_k71,
]

print("Sample k[71] propagation:")
for k71 in samples:
    # Compute adj[71]
    adj71 = k71 - 2*k70
    
    # Compute offset[71]
    offset71 = -k68 + 4*adj69 + 2*adj70 + adj71
    
    # Compute k[72] using 3-step
    k72 = 9*k69 + (-k69 + 4*adj70 + 2*adj71 + (k72_temp := 0))  # Need adj[72]
    
    # This is circular - need different approach
    
# Actually, let me just search for k[71] that, when propagated through
# the recurrence, matches k[75]

print("Brute search approach needed - range too large for direct search")
print()

# Alternative: use the constraint k[75] = 9^2 * k[69] + ...
# From k[75] = 9*k[72] + offset[75] and k[72] = 9*k[69] + offset[72]
# k[75] = 81*k[69] + 9*offset[72] + offset[75]

k75_from_k69 = 81*k69
remainder_75 = k75 - k75_from_k69
print(f"k[75] - 81*k[69] = {remainder_75}")
print(f"This must equal 9*offset[72] + offset[75]")
print()

# Now for the k[71] chain:
# k[74] = 9*k[71] + offset[74]
# offset[74] = -k[71] + 4*adj[72] + 2*adj[73] + adj[74]

# This involves too many unknowns. Let me try numerical search.

print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print("The k[75] bridge provides a constraint, but the search space")
print("is still O(2^70) which is too large for brute force.")
print()
print("Next steps:")
print("1. Find additional patterns in offset sequence")
print("2. Use mod constraints to reduce search space")
print("3. Apply m[71] formula constraints")
print("=" * 70)
