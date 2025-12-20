#!/usr/bin/env python3
"""
Task A: Offset Pattern Analysis
Find the formula for offsets in the mod-3 k-sequence recursion.
"""

import json
import sqlite3
from sympy import isprime, primefactors, factorint

# Load data
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

M_SEQ = data['m_seq']
D_SEQ = data['d_seq']

# Load k-sequence
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
rows = cursor.fetchall()
conn.close()

K = {pid: int(hx, 16) for pid, hx in rows}

def m(n):
    if n < 2 or n > 70: return None
    return M_SEQ[n - 2]

def d(n):
    if n < 2 or n > 70: return None
    return D_SEQ[n - 2]

print("="*80)
print("OFFSET PATTERN ANALYSIS")
print("="*80)
print()

# Compute offsets for mod-3 recursion: k[n] = c * k[n-3] + offset
print("Mod-3 Recursion Offsets:")
print("-"*80)

offsets = {}
for n in range(10, 31):
    if n not in K or (n-3) not in K:
        continue
    
    # Try different coefficients
    for c in [9, 10, 11, 8]:
        offset = K[n] - c * K[n-3]
        if abs(offset) < K[n]:  # Reasonable offset
            offsets[n] = {'c': c, 'offset': offset, 'k_n': K[n], 'k_n3': K[n-3]}
            break

for n in sorted(offsets.keys()):
    o = offsets[n]
    factors = factorint(abs(o['offset'])) if o['offset'] != 0 else {}
    factor_str = ' × '.join([f"{p}^{e}" if e > 1 else str(p) for p, e in factors.items()])
    
    # Check if offset relates to m or d values
    m_match = [i for i in range(2, 20) if m(i) and abs(o['offset']) % m(i) == 0]
    
    print(f"n={n:2}: k[{n}] = {o['c']} × k[{n-3}] + ({o['offset']:+})")
    print(f"       offset = {o['offset']} = {factor_str if factor_str else '0'}")
    if m_match:
        print(f"       divisible by m[{m_match}]")
    print()

# Look for patterns in offsets
print("="*80)
print("OFFSET SEQUENCE ANALYSIS")
print("="*80)

offset_vals = [offsets[n]['offset'] for n in sorted(offsets.keys())]
print(f"\nOffset sequence: {offset_vals}")

# Check if offsets are convergent values
print("\nChecking if offsets are convergent-related...")
# This would need the convergent database

# Check mod patterns
print("\nOffset mod patterns:")
for mod in [7, 9, 11, 13, 17, 19, 22]:
    mods = [o % mod for o in offset_vals if o != 0]
    print(f"  mod {mod}: {mods}")
