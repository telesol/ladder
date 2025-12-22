#!/usr/bin/env python3
"""
Deep analysis of offset patterns to find the formula
"""

import sqlite3

# Get all known keys
conn = sqlite3.connect('db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
rows = cursor.fetchall()
conn.close()

k = {}
for puzzle_id, priv_hex in rows:
    k[puzzle_id] = int(priv_hex, 16)

# Compute adj[n] = k[n] - 2*k[n-1] (the 1-step adjustment)
adj = {}
for n in range(2, 100):
    if n in k and (n-1) in k:
        adj[n] = k[n] - 2*k[n-1]

# Compute 5-step offset
offset5 = {}
for n in range(1, 130):
    if n in k and (n+5) in k:
        offset5[n] = k[n+5] - 32 * k[n]

print("=" * 80)
print("OFFSET AS FUNCTION OF ADJ SEQUENCE")
print("=" * 80)

print("\noffset5[n] expressed in terms of adj:")
print("Formula: k[n+5] = 32*k[n] + 16*adj[n+1] + 8*adj[n+2] + 4*adj[n+3] + 2*adj[n+4] + adj[n+5]")
print()

for n in range(1, 70):
    if n in offset5 and all((n+i) in adj for i in range(1, 6)):
        # From recurrence: k[n+5] = 32*k[n] + 16*adj[n+1] + 8*adj[n+2] + 4*adj[n+3] + 2*adj[n+4] + adj[n+5]
        computed = 16*adj[n+1] + 8*adj[n+2] + 4*adj[n+3] + 2*adj[n+4] + adj[n+5]
        actual = offset5[n]
        match = "✓" if computed == actual else "✗"
        if n <= 20 or computed != actual:  # Show first 20 or mismatches
            print(f"n={n:>2}: computed = {computed:>20}, actual = {actual:>20} {match}")

print()
print("=" * 80)
print("OFFSET EXPRESSED VIA adj WEIGHTED SUM")
print("=" * 80)

# offset5[n] = sum_{i=1}^{5} 2^(5-i) * adj[n+i]
# = 16*adj[n+1] + 8*adj[n+2] + 4*adj[n+3] + 2*adj[n+4] + 1*adj[n+5]

all_match = True
for n in range(1, 70):
    if n in offset5 and all((n+i) in adj for i in range(1, 6)):
        computed = sum(2**(5-i) * adj[n+i] for i in range(1, 6))
        actual = offset5[n]
        if computed != actual:
            print(f"MISMATCH at n={n}: {computed} vs {actual}")
            all_match = False

if all_match:
    print("VERIFIED: offset5[n] = 16*adj[n+1] + 8*adj[n+2] + 4*adj[n+3] + 2*adj[n+4] + adj[n+5]")
    print("         = sum_{i=1}^{5} 2^(5-i) * adj[n+i]")

print()
print("=" * 80)
print("ADJ SEQUENCE ANALYSIS (n=2 to n=70)")
print("=" * 80)

print(f"\n{'n':>3} {'adj[n]':>25} {'sign':>5} {'adj/2^(n-1)':>15}")
print("-" * 60)

for n in sorted(adj.keys()):
    sign = "+" if adj[n] >= 0 else "-"
    norm = adj[n] / (2**(n-1))
    print(f"{n:>3} {adj[n]:>25} {sign:>5} {norm:>15.6f}")

print()
print("=" * 80)
print("ADJ PATTERN BY n mod 5")
print("=" * 80)

for mod_val in range(5):
    vals = [(n, adj[n]) for n in sorted(adj.keys()) if n % 5 == mod_val]
    signs = ["+" if a >= 0 else "-" for _, a in vals]
    print(f"\nn mod 5 = {mod_val}:")
    print(f"  Signs: {''.join(signs)}")
    print(f"  Values: {[a for _, a in vals[:10]]}...")

print()
print("=" * 80)
print("ADJ RATIOS (adj[n+5] / adj[n])")
print("=" * 80)

for n in range(2, 66):
    if n in adj and (n+5) in adj and adj[n] != 0:
        ratio = adj[n+5] / adj[n]
        print(f"adj[{n+5:>2}]/adj[{n:>2}] = {ratio:>15.4f}")

print()
print("=" * 80)
print("LOOKING FOR ADJ RECURRENCE")
print("=" * 80)

# Try adj[n] = c1*adj[n-1] + c2*adj[n-2] + ...
print("\nTrying adj[n] = a*adj[n-1] + b*adj[n-2]:")
for n in range(4, 25):
    if all(i in adj for i in [n, n-1, n-2]) and adj[n-2] != 0:
        # adj[n] = a*adj[n-1] + b*adj[n-2]
        # Two unknowns, need to solve system
        pass

print("\nTrying adj[n+5] as function of adj[n]:")
for n in range(2, 20):
    if n in adj and (n+5) in adj:
        diff = adj[n+5] - adj[n]
        ratio = adj[n+5] / adj[n] if adj[n] != 0 else float('inf')
        print(f"n={n:>2}: adj[{n+5}] = {adj[n+5]:>15}, adj[{n}] = {adj[n]:>10}, diff = {diff:>15}, ratio = {ratio:>10.2f}")

print()
print("=" * 80)
print("CHECKING IF ADJ IS DETERMINISTIC FROM EARLIER ADJ VALUES")
print("=" * 80)

# Key insight: If adj[n] can be computed from adj[2..n-1], we can predict!
# Try various recurrences

print("\nTrying: adj[n] = 2*adj[n-1] + some_pattern")
for n in range(3, 30):
    if n in adj and (n-1) in adj:
        diff = adj[n] - 2*adj[n-1]
        print(f"n={n:>2}: adj[{n}] - 2*adj[{n-1}] = {diff}")
