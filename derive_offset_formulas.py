#!/usr/bin/env python3
"""
Derive k-value formulas for all mod-3 recursion offsets
========================================================

offset[n] = k[n] - 9 × k[n-3]

We discovered offsets are linear combinations of earlier k-values.
This script finds the exact formulas.
"""

import sqlite3

# Load k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

# Compute offsets
offsets = {}
for n in range(10, 71):
    if n in k and n-3 in k:
        offsets[n] = k[n] - 9 * k[n-3]

print("=" * 80)
print("DERIVING K-VALUE FORMULAS FOR ALL OFFSETS")
print("=" * 80)

def find_best_formula(n, offset, max_coeff=200):
    """Find the simplest a×k[i] + b formula for offset."""
    candidates = []

    # Single k-value: offset = a×k[i] + b
    for i in range(1, n):
        if k[i] == 0:
            continue
        # Find best a
        a = offset // k[i]
        for aa in [a-2, a-1, a, a+1, a+2]:
            if aa == 0:
                continue
            if abs(aa) > max_coeff:
                continue
            b = offset - aa * k[i]
            if abs(b) < 1000:
                complexity = abs(aa) + abs(b) / 100
                candidates.append((complexity, aa, i, b, f"{aa}×k[{i}] + {b}"))

    # Sort by complexity
    candidates.sort(key=lambda x: x[0])
    return candidates[:3] if candidates else []

# Find formulas for all offsets
print("\n### BEST FORMULAS FOR EACH OFFSET ###\n")
print(f"{'n':>3} {'offset':>15} {'formula':>30} {'verification':>15}")
print("-" * 75)

formulas = {}
for n in sorted(offsets.keys()):
    off = offsets[n]
    best = find_best_formula(n, off)

    if best:
        _, a, i, b, formula = best[0]
        # Verify
        computed = a * k[i] + b
        match = "✓" if computed == off else "✗"
        print(f"{n:>3} {off:>15} {formula:>30} {match:>15}")
        formulas[n] = (a, i, b)
    else:
        print(f"{n:>3} {off:>15} {'(no simple formula)':>30}")

# Analyze patterns in the formulas
print("\n\n" + "=" * 80)
print("PATTERN ANALYSIS")
print("=" * 80)

# Group by which k[i] is used
print("\n### WHICH k[i] IS USED? ###")
i_usage = {}
for n, (a, i, b) in formulas.items():
    if i not in i_usage:
        i_usage[i] = []
    i_usage[i].append(n)

for i in sorted(i_usage.keys()):
    if len(i_usage[i]) >= 2:
        print(f"  k[{i}] used in n = {i_usage[i]}")

# Group by coefficient a
print("\n### COEFFICIENT 'a' DISTRIBUTION ###")
a_usage = {}
for n, (a, i, b) in formulas.items():
    if a not in a_usage:
        a_usage[a] = []
    a_usage[a].append(n)

for a in sorted(a_usage.keys(), key=lambda x: -len(a_usage[x])):
    if len(a_usage[a]) >= 2:
        print(f"  a={a}: n = {a_usage[a]}")

# Look for pattern in b values
print("\n### 'b' VALUES (small constants) ###")
b_values = [(n, formulas[n][2]) for n in sorted(formulas.keys()) if abs(formulas[n][2]) < 100]
for n, b in b_values[:20]:
    print(f"  n={n}: b = {b}")

# Look for n vs i relationship
print("\n### RELATIONSHIP: n vs i (which k-value is referenced) ###")
for n in range(10, 31):
    if n in formulas:
        a, i, b = formulas[n]
        diff = n - i
        print(f"  n={n}: uses k[{i}], diff = {diff}, a = {a}, b = {b}")

# Summary
print("\n\n" + "=" * 80)
print("COMPLETE FORMULA TABLE")
print("=" * 80)
print("\noffset[n] = k[n] - 9×k[n-3]\n")

print("n ≡ 0 (mod 3):")
for n in range(10, 71, 3):
    if n in formulas:
        a, i, b = formulas[n]
        sign = '+' if b >= 0 else ''
        print(f"  offset[{n:2}] = {a:>5}×k[{i:2}] {sign}{b:>8}")

print("\nn ≡ 1 (mod 3):")
for n in range(11, 71, 3):
    if n in formulas:
        a, i, b = formulas[n]
        sign = '+' if b >= 0 else ''
        print(f"  offset[{n:2}] = {a:>5}×k[{i:2}] {sign}{b:>8}")

print("\nn ≡ 2 (mod 3):")
for n in range(12, 71, 3):
    if n in formulas:
        a, i, b = formulas[n]
        sign = '+' if b >= 0 else ''
        print(f"  offset[{n:2}] = {a:>5}×k[{i:2}] {sign}{b:>8}")
