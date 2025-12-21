#!/usr/bin/env python3
"""
Compute m[75], m[80], m[85], m[90] from the gap puzzles.

Key insight from DIRECT_FORMULA_RESEARCH.md:
The creator generated k[75] WITHOUT k[71-74] - meaning k[n] = f(n) for some direct formula.

For gap puzzles, we can still compute:
  m[n] = (2^n - adj[n]) / k[d[n]]

But we need adj[n] = k[n] - 2*k[n-1], and we don't have k[74], k[79], k[84], k[89].

HOWEVER: We can compute bounds on m by assuming adj is within typical range.
"""
import sqlite3

# Load known k values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 91):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

print("=" * 70)
print("GAP PUZZLE M-VALUE ANALYSIS")
print("=" * 70)
print()

print("### Known Gap Puzzles ###")
for n in [75, 80, 85, 90]:
    print(f"k[{n}] = {k_values[n]}")
print()

# For normal puzzles, adj[n] = k[n] - 2*k[n-1]
# For gap puzzles, k[n-1] is unknown.

# BUT: We can estimate using the bridge relations!
# From k[n] = 9*k[n-3] + offset[n], we can compute offset for gaps

print("### Gap Puzzle Offsets (3-step recursion) ###")
print()

# k[75] relates to k[72]: k[75] = 9*k[72] + offset[75]
# But k[72] is unknown. 
# However: k[75] = 81*k[69] + 9*offset[72] + offset[75]
# So: offset_sum = k[75] - 81*k[69] = 9*offset[72] + offset[75]

# k[80] relates to k[71]: k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]
# k[71] is unknown.

# k[85] relates to k[70]: k[85] = 59049*k[70] + offset_sum
# We CAN compute this!

k70 = k_values[70]
k85 = k_values[85]
offset_sum_85 = k85 - (9**5) * k70
print(f"k[85] - 9^5*k[70] = {offset_sum_85}")
print(f"This = 6561*off[73] + 729*off[76] + 81*off[79] + 9*off[82] + off[85]")
print()

k69 = k_values[69]
k90 = k_values[90]
offset_sum_90 = k90 - (9**7) * k69
print(f"k[90] - 9^7*k[69] = {offset_sum_90}")
print(f"This = offset sum from 72 to 90")
print()

# Alternative: Compute m[n] directly using the formula
# m[n] = 2^n / k[d[n]] approximately (when adj << 2^n)

print("### Approximate m values (assuming adj << 2^n) ###")
print()

for n in [75, 80, 85, 90]:
    k_n = k_values[n]
    
    # Try each possible d value
    print(f"n = {n}:")
    for d in [1, 2, 3, 4, 5, 6, 7, 8]:
        if d in k_values:
            k_d = k_values[d]
            m_approx = 2**n // k_d
            # Check if this makes sense
            adj_implied = 2**n - m_approx * k_d
            k_implied = 2*k_values.get(n-1, 0) + adj_implied if (n-1) in k_values else None
            
            print(f"  d={d}: m ≈ {m_approx:.4e}, adj ≈ {adj_implied:.4e}")
    print()

# Key insight: For gap puzzles, the formula m[n] = 2^n / k[d[n]] should still hold
# We just need to figure out which d was used

print("### Testing which d gives integer m values ###")
print()

for n in [75, 80, 85, 90]:
    k_n = k_values[n]
    print(f"n = {n}, k[n] = {k_n}")
    
    for d in [1, 2, 3, 4, 5, 6, 7, 8]:
        if d in k_values:
            k_d = k_values[d]
            
            # For m to be integer: k_d must divide (2^n - adj[n])
            # We don't know adj[n], but we can check divisibility patterns
            
            # If adj[n] = k[n] - 2*k[n-1] and we approximate k[n-1] ≈ k[n]/2:
            # adj[n] ≈ k[n] - 2*(k[n]/2) = 0 (this is wrong!)
            
            # Better: Use the offset pattern
            # offset[n] = k[n] - 9*k[n-3]
            # adj[n] = offset[n] - 4*adj[n-2] - 2*adj[n-1]
            
            # For now, just check 2^n mod k_d
            remainder = (2**n) % k_d
            print(f"  d={d}: 2^{n} mod k[{d}] = {remainder}")
    print()

print("=" * 70)
print("KEY INSIGHT")
print("=" * 70)
print()
print("Since k[75], k[80], k[85], k[90] were generated WITHOUT intermediates,")
print("the formula k[n] = f(n) must exist and be computable for any n.")
print()
print("The m[n] = (2^n - adj[n]) / k[d[n]] formula suggests:")
print("1. Either adj[n] has a direct formula: adj[n] = g(n)")
print("2. Or m[n] has a direct formula: m[n] = h(n)")
print()
print("If we find h(n), we can derive k[n] = 2^n - h(n)*k[d[n]] + recursive terms")
