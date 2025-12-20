#!/usr/bin/env python3
"""Verify the k-sequence formulas discovered by other Claude instances."""

import sqlite3

# Load k-sequence
conn = sqlite3.connect('/home/solo/LadderV3/kh-assist/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 95 ORDER BY puzzle_id")
rows = cur.fetchall()
conn.close()

k = {row[0]: int(row[1], 16) for row in rows}

print("="*80)
print("VERIFYING OTHER CLAUDES' K-SEQUENCE FORMULAS")
print("="*80)
print()

# Formulas from SYNTHESIS_WITH_OTHER_CLAUDES.md
formulas = [
    (5, "k2 × k3", lambda: k[2] * k[3]),
    (6, "k3²", lambda: k[3] ** 2),
    (7, "9×k2 + k6", lambda: 9 * k[2] + k[6]),
    (8, "13×k5 - k6", lambda: 13 * k[5] - k[6]),
    (11, "19×k6 + k8", lambda: 19 * k[6] + k[8]),
    (12, "12×k8 - 5", lambda: 12 * k[8] - 5),
    (13, "10×k10 + k7", lambda: 10 * k[10] + k[7]),
]

verified = 0
failed = 0

for n, formula_str, formula_fn in formulas:
    if n not in k:
        print(f"⚠️  k{n} not in database - skipping")
        continue

    try:
        k_predicted = formula_fn()
        k_actual = k[n]

        if k_predicted == k_actual:
            print(f"✅ k{n} = {formula_str}")
            print(f"   Predicted: {k_predicted:#x}")
            print(f"   Actual:    {k_actual:#x}")
            print(f"   EXACT MATCH!")
            verified += 1
        else:
            diff = k_actual - k_predicted
            error_pct = abs(diff) / k_actual * 100 if k_actual != 0 else 0
            print(f"❌ k{n} = {formula_str}")
            print(f"   Predicted: {k_predicted:#x}")
            print(f"   Actual:    {k_actual:#x}")
            print(f"   Difference: {diff} ({error_pct:.2f}% error)")
            failed += 1
    except Exception as e:
        print(f"⚠️  Error testing k{n}: {e}")
        failed += 1

    print()

print("="*80)
print(f"RESULTS: {verified} verified, {failed} failed")
print("="*80)
print()

if verified > 0:
    print("✅ Some formulas work! This confirms other Claudes' approach.")
    print("   Strategy: Find more patterns to fill gaps k71-k74, k76-k79, etc.")
else:
    print("❌ No formulas matched exactly.")
    print("   Need to re-examine the k-sequence generation approach.")

print()

# Try to discover similar patterns for other k-values
print("="*80)
print("SEARCHING FOR ADDITIONAL PATTERNS (n=2-30)")
print("="*80)
print()

for n in range(5, 31):
    if n not in k:
        continue

    k_actual = k[n]
    found = False

    # Try multiplication of two previous k-values
    for i in range(1, n):
        for j in range(1, n):
            if i not in k or j not in k:
                continue
            if k[i] * k[j] == k_actual:
                print(f"✅ k{n} = k{i} × k{j}")
                found = True
                break
        if found:
            break

    # Try squaring
    if not found:
        for i in range(1, n):
            if i not in k:
                continue
            if k[i] ** 2 == k_actual:
                print(f"✅ k{n} = k{i}²")
                found = True
                break

    # Try linear combinations with small coefficients
    if not found:
        for i in range(1, n):
            for j in range(1, n):
                if i not in k or j not in k or i == j:
                    continue
                for a in range(-20, 21):
                    for b in range(-20, 21):
                        if a == 0 and b == 0:
                            continue
                        if a * k[i] + b * k[j] == k_actual:
                            print(f"✅ k{n} = {a}×k{i} + {b}×k{j}")
                            found = True
                            break
                    if found:
                        break
                if found:
                    break
            if found:
                break

    # Try with constant offset
    if not found:
        for i in range(1, n):
            if i not in k:
                continue
            for mult in range(2, 21):
                for offset in range(-100, 101):
                    if mult * k[i] + offset == k_actual:
                        if offset == 0:
                            print(f"✅ k{n} = {mult}×k{i}")
                        else:
                            print(f"✅ k{n} = {mult}×k{i} + {offset}")
                        found = True
                        break
                if found:
                    break
            if found:
                break

print()
