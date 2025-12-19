#!/usr/bin/env python3
"""Search for formulas expressing m[n] in terms of earlier m values."""

import json
from itertools import combinations

# Load data
with open('/home/solo/LA/data_for_csolver.json') as f:
    data = json.load(f)

m_list = data['m_seq']
d_list = data['d_seq']
m_seq = {n: m_list[n-2] for n in range(2, 2 + len(m_list))}
d_seq = {n: d_list[n-2] for n in range(2, 2 + len(d_list))}

print("="*80)
print("SEARCHING FOR m[n] FORMULAS")
print("="*80)
print()

formulas_found = {}

for n in range(4, 40):
    m = m_seq[n]
    d = d_seq[n]
    found = []

    # Additive: m[n] = m[i] + m[j]
    for i, j in combinations(range(2, n), 2):
        if m_seq[i] + m_seq[j] == m:
            found.append(f"m[{i}] + m[{j}] = {m_seq[i]} + {m_seq[j]}")

    # Subtractive: m[n] = m[i] - m[j]
    for i in range(2, n):
        for j in range(2, n):
            if i != j and m_seq[i] - m_seq[j] == m:
                found.append(f"m[{i}] - m[{j}] = {m_seq[i]} - {m_seq[j]}")

    # Multiplicative: m[n] = m[i] * m[j]
    for i, j in combinations(range(2, n), 2):
        if m_seq[i] * m_seq[j] == m:
            found.append(f"m[{i}] × m[{j}] = {m_seq[i]} × {m_seq[j]}")

    # Multiplicative with constant: m[n] = c * m[i]
    for i in range(2, n):
        if m_seq[i] > 0 and m % m_seq[i] == 0:
            c = m // m_seq[i]
            if 2 <= c <= 100:
                found.append(f"{c} × m[{i}] = {c} × {m_seq[i]}")

    # Linear combination: m[n] = a*m[i] + b*m[j] for small a, b
    for i in range(2, n):
        for j in range(2, n):
            if i != j:
                for a in range(1, 10):
                    for b in range(-5, 10):
                        if a * m_seq[i] + b * m_seq[j] == m:
                            found.append(f"{a}×m[{i}] + {b}×m[{j}] = {a}×{m_seq[i]} + {b}×{m_seq[j]}")

    # Power of 2 relationship: m[n] = 2^k ± m[i]
    import math
    for k in range(1, 30):
        pow2 = 2**k
        if abs(pow2 - m) <= max(m_seq.values()) and abs(pow2 - m) in m_seq.values():
            for i, mi in m_seq.items():
                if i < n:
                    if pow2 - mi == m:
                        found.append(f"2^{k} - m[{i}] = {pow2} - {mi}")
                    if pow2 + mi == m:
                        found.append(f"2^{k} + m[{i}] = {pow2} + {mi}")

    # Involving d[n]: m[n] = f(m[d[n]], n)
    m_at_d = m_seq.get(d)
    if m_at_d:
        if m % m_at_d == 0:
            c = m // m_at_d
            found.append(f"(m[d={d}]={m_at_d}) × {c}")
        # m[n] = m[d] + something
        diff = m - m_at_d
        for i in range(2, n):
            if m_seq[i] == diff:
                found.append(f"m[d={d}] + m[{i}] = {m_at_d} + {diff}")

    if found:
        formulas_found[n] = found
        print(f"n={n:2d}: m={m:>10}, d={d}")
        for f in found[:5]:  # Limit output
            print(f"      → {f}")
        print()

print("="*80)
print("SUMMARY OF FORMULAS FOUND")
print("="*80)
print()
print(f"Found formulas for {len(formulas_found)} out of 36 values checked")
print()

# Check for consistent patterns
print("Pattern: m[n] = c × m[d[n]] appears in:")
for n, forms in formulas_found.items():
    for f in forms:
        if f.startswith("(m[d="):
            print(f"  n={n}: {f}")
