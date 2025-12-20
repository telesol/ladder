#!/usr/bin/env python3
"""
Find two-term k-value formulas for larger offsets
=================================================

For n > 22, simple a×k[i] + b doesn't work.
Try: offset[n] = a×k[i] + b×k[j] + c
"""

import sqlite3
from itertools import combinations

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
print("FINDING TWO-TERM FORMULAS: offset = a×k[i] + b×k[j] + c")
print("=" * 80)

def find_twoterm_formula(n, offset, max_coeff=50):
    """Find a×k[i] + b×k[j] + c formula."""
    candidates = []

    # Try all pairs of k values
    for i, j in combinations(range(1, n), 2):
        ki, kj = k[i], k[j]
        if ki == 0 or kj == 0:
            continue

        # For small a, b, find c
        for a in range(-max_coeff, max_coeff + 1):
            if a == 0:
                continue
            for b in range(-max_coeff, max_coeff + 1):
                if b == 0:
                    continue
                base = a * ki + b * kj
                c = offset - base
                if abs(c) < 500:  # Small remainder
                    complexity = abs(a) + abs(b) + abs(c) / 100
                    candidates.append((complexity, a, i, b, j, c))

    candidates.sort(key=lambda x: x[0])
    return candidates[:3] if candidates else []

# Find formulas for n=23-35
print("\n### TWO-TERM FORMULAS FOR n=23-35 ###\n")

for n in range(23, 36):
    off = offsets[n]
    best = find_twoterm_formula(n, off)

    if best:
        _, a, i, b, j, c = best[0]
        # Verify
        computed = a * k[i] + b * k[j] + c
        match = "✓" if computed == off else "✗"
        sign_c = '+' if c >= 0 else ''
        formula = f"{a}×k[{i}] + {b}×k[{j}] {sign_c}{c}"
        print(f"offset[{n}] = {formula} {match}")
        print(f"         = {a}×{k[i]} + {b}×{k[j]} + {c} = {computed}")
    else:
        print(f"offset[{n}] = {off} (no two-term formula found)")
    print()

# Also try: offset = a × k[i] × k[j] / k[m] or similar
print("\n" + "=" * 80)
print("TRYING PRODUCT FORMULAS: offset ≈ k[i] × k[j] × factor")
print("=" * 80 + "\n")

for n in range(23, 31):
    off = offsets[n]

    # Try offset = k[i] × k[j] × a / b + c
    for i in range(3, n-3):
        for j in range(i+1, n-2):
            prod = k[i] * k[j]
            if prod == 0:
                continue

            # Is offset close to a multiple of prod?
            if abs(off) > prod // 10:  # offset should be comparable to product
                ratio = off / prod
                # Check if ratio is close to a simple fraction
                for num in range(-20, 21):
                    for den in range(1, 10):
                        if num == 0:
                            continue
                        expected = prod * num // den
                        diff = off - expected
                        if abs(diff) < 1000 and abs(diff) < abs(off) / 100:
                            print(f"offset[{n}] ≈ k[{i}]×k[{j}]×{num}/{den} + {diff}")
                            print(f"         = {k[i]}×{k[j]}×{num}/{den} + {diff}")
                            print()

# Summary
print("\n" + "=" * 80)
print("ALTERNATIVE: CHECK IF OFFSETS RELATE TO m-SEQUENCE")
print("=" * 80 + "\n")

# Load m sequence
import json
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)
m = {i+2: data['m_seq'][i] for i in range(len(data['m_seq']))}

# Check if offset[n] = f(m[n]) × k[g(n)]
print("Testing offset[n] vs m[n] × k[i]:")
for n in range(10, 26):
    off = offsets[n]
    mn = m[n]

    # Is offset related to m[n]?
    if mn != 0:
        ratio = off / mn
        # Find if ratio is close to some k value
        for i in range(1, n):
            if abs(ratio - k[i]) < abs(k[i]) * 0.1:
                diff = off - mn * k[i]
                print(f"offset[{n}] ≈ m[{n}] × k[{i}] + {diff}")
                print(f"         = {mn} × {k[i]} + {diff} = {mn * k[i] + diff}")
                break
        else:
            # Try negative
            for i in range(1, n):
                if abs(ratio + k[i]) < abs(k[i]) * 0.1:
                    diff = off + mn * k[i]
                    print(f"offset[{n}] ≈ -m[{n}] × k[{i}] + {diff}")
                    break
