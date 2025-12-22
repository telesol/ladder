#!/usr/bin/env python3
"""
Deep analysis of adj sequence to find the generation rule
adj[n] = k[n] - 2*k[n-1]
"""

import sqlite3
import json

# Get all known keys
conn = sqlite3.connect('db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
rows = cursor.fetchall()
conn.close()

k = {}
for puzzle_id, priv_hex in rows:
    k[puzzle_id] = int(priv_hex, 16)

# Compute adj[n] = k[n] - 2*k[n-1]
adj = {}
for n in range(2, 100):
    if n in k and (n-1) in k:
        adj[n] = k[n] - 2*k[n-1]

# Load m and d sequences
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']  # m_seq[i] = m[i+2]
d_seq = data['d_seq']  # d_seq[i] = d[i+2]

def get_m(n):
    if n >= 2 and n-2 < len(m_seq):
        return m_seq[n-2]
    return None

def get_d(n):
    if n >= 2 and n-2 < len(d_seq):
        return d_seq[n-2]
    return None

print("=" * 80)
print("ADJ vs M RELATIONSHIP")
print("=" * 80)

# We know: adj[n] = 2^n - m[n]*k[d[n]] (from unified formula)
print("\nVerifying: adj[n] = 2^n - m[n]*k[d[n]]")
print(f"{'n':>3} {'adj[n]':>20} {'computed':>20} {'match':>6}")
print("-" * 60)

for n in range(2, 71):
    if n in adj:
        m_n = get_m(n)
        d_n = get_d(n)
        if m_n is not None and d_n is not None and d_n in k:
            computed = (2**n) - m_n * k[d_n]
            match = "YES" if computed == adj[n] else "NO"
            if n <= 25 or computed != adj[n]:
                print(f"{n:>3} {adj[n]:>20} {computed:>20} {match:>6}")

print()
print("=" * 80)
print("SIGN PATTERN OF ADJ")
print("=" * 80)

signs = []
for n in range(2, 71):
    if n in adj:
        signs.append("+" if adj[n] >= 0 else "-")

print(f"adj signs (n=2 to n=70):")
for i in range(0, len(signs), 20):
    chunk = signs[i:i+20]
    start_n = i + 2
    end_n = start_n + len(chunk) - 1
    print(f"n={start_n:>2}-{end_n:>2}: {''.join(chunk)}")

print()
print("=" * 80)
print("KEY FINDING: adj[n] = 2^n - m[n]*k[d[n]]")
print("=" * 80)

# If this formula holds, then to predict adj[71], we need:
# - m[71] (unknown)
# - d[71] (predicted 60% = 1, 20% = 2, 20% = 5)
# - k[d[71]] (known if d[71] is 1, 2, or 5)

print("\nTo predict adj[71]:")
print("  We need m[71] and d[71]")
print("  If d[71] = 1: adj[71] = 2^71 - m[71]*k[1] = 2^71 - m[71]")
print("  If d[71] = 2: adj[71] = 2^71 - m[71]*k[2] = 2^71 - 3*m[71]")
print("  If d[71] = 5: adj[71] = 2^71 - m[71]*k[5] = 2^71 - 21*m[71]")

k70 = k[70]
min_k71 = 2**70  
max_k71 = 2**71 - 1  
k71_base = 2 * k70  

print(f"\nConstraints on adj[71]:")
print(f"  2*k[70] = {k71_base}")
print(f"  min k[71] = 2^70 = {min_k71}")
print(f"  max k[71] = 2^71-1 = {max_k71}")

adj71_min = min_k71 - k71_base
adj71_max = max_k71 - k71_base
print(f"  adj[71] range: [{adj71_min:,}, {adj71_max:,}]")

# For d[71]=1: adj[71] = 2^71 - m[71]
# So: m[71] = 2^71 - adj[71]
print(f"\nIf d[71]=1: m[71] = 2^71 - adj[71]")
print(f"  m[71] range: [{2**71 - adj71_max:,}, {2**71 - adj71_min:,}]")

# For d[71]=2: adj[71] = 2^71 - 3*m[71]
# So: m[71] = (2^71 - adj[71]) / 3
print(f"\nIf d[71]=2: m[71] = (2^71 - adj[71]) / 3")

# For d[71]=5: adj[71] = 2^71 - 21*m[71]
# So: m[71] = (2^71 - adj[71]) / 21
print(f"\nIf d[71]=5: m[71] = (2^71 - adj[71]) / 21")

print()
print("=" * 80)
print("M-SEQUENCE PATTERN ANALYSIS")
print("=" * 80)

print(f"\n{'n':>3} {'m[n]':>15} {'m[n]/2^n':>15} {'d[n]':>5}")
print("-" * 45)
for n in range(2, 71):
    m_n = get_m(n)
    d_n = get_d(n)
    if m_n is not None:
        ratio = m_n / (2**n)
        print(f"{n:>3} {m_n:>15} {ratio:>15.6f} {d_n:>5}")

print()
print("=" * 80)
print("LOOKING FOR M-SEQUENCE RECURRENCE")
print("=" * 80)

# Check various recurrence patterns
print("\nTrying: m[n+5] vs 32*m[n]")
for n in range(2, 66):
    m_n = get_m(n)
    m_n5 = get_m(n+5)
    if m_n is not None and m_n5 is not None and m_n != 0:
        ratio = m_n5 / (32 * m_n)
        print(f"m[{n+5:>2}] / (32*m[{n:>2}]) = {ratio:.4f}")
