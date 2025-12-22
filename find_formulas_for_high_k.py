#!/usr/bin/env python3
"""Find formulas for high k-values (k60-k70) to understand pattern near bridges."""

import sqlite3
from itertools import combinations

# Load k-sequence
conn = sqlite3.connect('/home/solo/LadderV3/kh-assist/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 95 ORDER BY puzzle_id")
rows = cur.fetchall()
conn.close()

k = {row[0]: int(row[1], 16) for row in rows}

print("="*80)
print("SEARCHING FOR FORMULAS: k60-k70")
print("="*80)
print()

for n in range(60, 71):
    if n not in k:
        continue

    k_actual = k[n]
    found = False
    formula_found = None

    print(f"Searching for formula for k{n}...")

    # Try multiplication of two k-values
    for i in range(1, n):
        if found:
            break
        for j in range(i, n):
            if i not in k or j not in k:
                continue
            if k[i] * k[j] == k_actual:
                formula_found = f"k{n} = k{i} × k{j}"
                found = True
                break

    # Try squaring
    if not found:
        for i in range(1, n):
            if i not in k:
                continue
            if k[i] ** 2 == k_actual:
                formula_found = f"k{n} = k{i}²"
                found = True
                break

    # Try linear combinations with small coefficients (focus on recent k-values)
    if not found:
        search_range = list(range(max(1, n-20), n))  # Last 20 k-values
        for i in search_range:
            if found:
                break
            for j in search_range:
                if found:
                    break
                if i not in k or j not in k or i == j:
                    continue

                # Small coefficient range for efficiency
                for a in range(-5, 6):
                    if found:
                        break
                    for b in range(-5, 6):
                        if a == 0 and b == 0:
                            continue
                        if a * k[i] + b * k[j] == k_actual:
                            formula_found = f"k{n} = {a}×k{i} + {b}×k{j}"
                            found = True
                            break

    # Try with constant offset (single k-value + offset)
    if not found:
        for i in range(max(1, n-20), n):
            if found:
                break
            if i not in k:
                continue
            for mult in [2, 3, 5, 7, 11, 13, 17, 19]:
                if found:
                    break
                for offset in range(-1000, 1001, 10):  # Step by 10 for efficiency
                    if mult * k[i] + offset == k_actual:
                        formula_found = f"k{n} = {mult}×k{i} + {offset}"
                        found = True
                        break

    if formula_found:
        print(f"  ✅ {formula_found}")
    else:
        print(f"  ❌ No simple formula found")

    print()

print("="*80)
print("ATTEMPTING TO PREDICT k75 FROM k60-k70")
print("="*80)
print()

# If we found patterns for k60-k70, try to extrapolate to k75
# Strategy: Look for meta-patterns in the formulas themselves

if 75 in k:
    k75_actual = k[75]
    print(f"Actual k75 = {k75_actual:#x}")
    print()

    # Try formulas similar to what worked for k60-k70
    print("Testing formula types that worked for k60-k70:")
    print()

    # Linear combination of recent k-values
    candidates = []
    for i in range(60, 71):
        if i not in k:
            continue
        for j in range(60, 71):
            if j not in k or j == i:
                continue
            for a in range(-5, 6):
                for b in range(-5, 6):
                    if a == 0 and b == 0:
                        continue
                    k_pred = a * k[i] + b * k[j]
                    error = abs(k_pred - k75_actual)
                    if error == 0:
                        print(f"  ✅ EXACT: k75 = {a}×k{i} + {b}×k{j}")
                        candidates.append((0, f"k75 = {a}×k{i} + {b}×k{j}"))
                    elif error < k75_actual * 0.001:  # < 0.1% error
                        candidates.append((error, f"k75 = {a}×k{i} + {b}×k{j} (error: {error})"))

    if candidates:
        candidates.sort(key=lambda x: x[0])
        print("Top candidates:")
        for error, formula in candidates[:5]:
            print(f"  {formula}")
    else:
        print("  No close matches found with simple linear combinations")

print()
