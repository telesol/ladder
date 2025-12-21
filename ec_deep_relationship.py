#!/usr/bin/env python3
"""
Deep EC Relationship Analysis

The fundamental question: What EC operation connects consecutive puzzles?

We know:
  P[n] = k[n] × G

In EC, the main operations are:
  - Point doubling: 2P
  - Point addition: P + Q
  - Scalar multiplication: k × P

The puzzle structure suggests:
  k[n] = 2*k[n-1] + adj[n]

In EC terms:
  P[n] = 2*P[n-1] + adj[n]*G
       = 2*P[n-1] + (2^n - m[n]*k[d[n]])*G
       = 2*P[n-1] + 2^n*G - m[n]*P[d[n]]

This means every puzzle point is:
  1. Double the previous point
  2. Add 2^n × G
  3. Subtract m[n] copies of an earlier puzzle point

The "subtract" is EC point addition with negation: P - Q = P + (-Q)

Let's verify this EC relationship holds and analyze the structure.
"""
import sqlite3
import json
from pathlib import Path
import math

# Load known k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 161):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

# Load m and d values
data_file = Path('data_for_csolver.json')
if data_file.exists():
    with open(data_file) as f:
        data = json.load(f)
        m_seq = data.get('m_seq', [])
        d_seq = data.get('d_seq', [])
else:
    m_seq = []
    d_seq = []

print("=" * 80)
print("DEEP EC RELATIONSHIP ANALYSIS")
print("=" * 80)
print()

# Verify the EC scalar relationship
print("### EC Scalar Identity: k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]] ###")
print()
print("This means:")
print("  P[n] = 2*P[n-1] + 2^n × G - m[n] × P[d[n]]")
print()
print("Verification for n=2 to n=20:")
print()
print("n  | 2*k[n-1] + 2^n | m[n]*k[d[n]] | Result = k[n]? |")
print("---|----------------|--------------|----------------|")

for i in range(18):  # n=2 to n=19
    n = i + 2
    if n in k_values and (n-1) in k_values and i < len(m_seq) and i < len(d_seq):
        k_n = k_values[n]
        k_prev = k_values[n-1]
        m = m_seq[i]
        d = d_seq[i]

        if d in k_values:
            k_d = k_values[d]
            computed = 2*k_prev + 2**n - m*k_d
            match = "✓" if computed == k_n else "✗"
            print(f"{n:2d} | {2*k_prev + 2**n:14d} | {m*k_d:12d} | {match}")

print()

# Analyze the "5-step ladder" in EC terms
print("### 5-Step Ladder in EC Terms ###")
print()
print("For n → n+5, we have:")
print("  P[n+5] = some_function(P[n], P[n+1], ..., G)")
print()
print("Let's compute k[n+5] in terms of k[n] and k values in between:")
print()

# k[n+5] = 2*k[n+4] + 2^(n+5) - m[n+5]*k[d[n+5]]
#        = 2*(2*k[n+3] + 2^(n+4) - m[n+4]*k[d[n+4]]) + 2^(n+5) - m[n+5]*k[d[n+5]]
#        = 4*k[n+3] + 2^(n+5) - 2*m[n+4]*k[d[n+4]] + 2^(n+5) - m[n+5]*k[d[n+5]]
#        = 4*k[n+3] + 2^(n+6) - 2*m[n+4]*k[d[n+4]] - m[n+5]*k[d[n+5]]
# Continue unrolling...

# For consecutive puzzles, expand k[n+5] in terms of k[n]
print("Expanding k[n+5] = 2^5*k[n] + offset_sum:")
print()
for n in range(5, 66):
    if n in k_values and (n+5) in k_values:
        k_n = k_values[n]
        k_n5 = k_values[n+5]
        offset = k_n5 - 32*k_n
        ratio = offset / k_n if k_n != 0 else 0
        print(f"k[{n+5}] = 32*k[{n}] + {offset:>20d} (= {ratio:+.4f}*k[{n}])")
        if n >= 30:  # Show fewer for brevity
            print("...")
            break

print()

# The offset is NOT constant - it oscillates
print("### Offset Pattern Analysis ###")
print()
print("The offset k[n+5] - 32*k[n] depends on:")
print("  sum of: 2^4*(2^(n+1) - m[n+1]*k[d[n+1]])")
print("        + 2^3*(2^(n+2) - m[n+2]*k[d[n+2]])")
print("        + 2^2*(2^(n+3) - m[n+3]*k[d[n+3]])")
print("        + 2^1*(2^(n+4) - m[n+4]*k[d[n+4]])")
print("        + 2^0*(2^(n+5) - m[n+5]*k[d[n+5]])")
print()

# Compute this sum for several n values
print("n  | Computed offset | Actual offset | Match?")
print("---|-----------------|---------------|-------")
for n in range(5, 21):
    if all((n+j) in k_values for j in range(6)):
        # Compute the offset using the formula
        offset_sum = 0
        for j in range(1, 6):
            idx = (n + j) - 2  # Index into m_seq, d_seq
            if idx < len(m_seq) and idx < len(d_seq):
                m = m_seq[idx]
                d = d_seq[idx]
                if d in k_values:
                    k_d = k_values[d]
                    offset_sum += 2**(5-j) * (2**(n+j) - m*k_d)

        actual_offset = k_values[n+5] - 32*k_values[n]
        match = "✓" if offset_sum == actual_offset else "✗"
        print(f"{n:2d} | {offset_sum:15d} | {actual_offset:13d} | {match}")

print()

# Key insight: The gap puzzles must follow the same structure
print("### Gap Puzzle EC Structure ###")
print()
print("For gap puzzle at n=75, we need to express:")
print("  P[75] = 2*P[74] + 2^75 × G - m[75] × P[d[75]]")
print()
print("But P[74] is unknown!")
print()
print("Alternative: Express P[75] directly in terms of known points:")
print("  P[75] = 32*P[70] + offset[70→75] × G")
print()
print("The offset[70→75] is what we need to compute, and it requires")
print("knowing m[71], m[72], m[73], m[74], m[75] and d[71], ..., d[75].")
print()

# What if we work backwards from the gap puzzles?
print("### Working Backwards from Gap Puzzles ###")
print()
print("Given k[75] and k[70], we can compute:")
offset_75 = k_values[75] - 32 * k_values[70]
print(f"  offset[70→75] = k[75] - 32*k[70] = {offset_75}")
print()
print("This offset is the sum of 5 terms involving m[71] through m[75].")
print("With 5 unknowns (m values) and 1 equation, we can't solve uniquely.")
print()

# But between gaps, we have:
print("Between consecutive gaps:")
for i in range(len([75, 80, 85, 90]) - 1):
    n1 = [75, 80, 85, 90][i]
    n2 = [75, 80, 85, 90][i+1]
    if n1 in k_values and n2 in k_values:
        offset = k_values[n2] - 32 * k_values[n1]
        print(f"  offset[{n1}→{n2}] = {offset}")
        print(f"  = {offset / k_values[n1]:.4f} × k[{n1}]")

print()
print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print()
print("The EC structure tells us:")
print("1. Each puzzle point is constructed from earlier points")
print("2. The 5-step jump k[n+5] = 32*k[n] + offset is NOT linear")
print("3. The offset depends on m[n+1], ..., m[n+5] values")
print("4. Gap puzzles hide the intermediate m values")
print()
print("To crack the gaps, we need:")
print("- A formula for m[n] that works for ANY n")
print("- Or: constraints from multiple equations (e.g., k[75], k[80], k[85], k[90])")
print()
