#!/usr/bin/env python3
"""Analyze the very close linear combination matches to find exact pattern."""

import sqlite3

# Load k-sequence
conn = sqlite3.connect('/home/solo/LadderV3/kh-assist/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 95 ORDER BY puzzle_id")
rows = cur.fetchall()
conn.close()

k_seq = {row[0]: int(row[1], 16) for row in rows}

print("="*80)
print("ANALYZING CLOSE LINEAR MATCHES")
print("="*80)
print()

# k75 ≈ 17*k69 + 18*k70 (0.07% error)
if 75 in k_seq and 69 in k_seq and 70 in k_seq:
    k75_actual = k_seq[75]
    k69 = k_seq[69]
    k70 = k_seq[70]

    k75_pred = 17 * k69 + 18 * k70
    diff = k75_actual - k75_pred

    print("Match 1: k75 = 17*k69 + 18*k70")
    print(f"  k69 = {k69:#x}")
    print(f"  k70 = {k70:#x}")
    print(f"  Predicted: {k75_pred:#x}")
    print(f"  Actual:    {k75_actual:#x}")
    print(f"  Difference: {diff} ({diff:#x})")
    print(f"  Ratio: {diff / k75_actual if k75_actual != 0 else 0}")
    print()

    # Try small adjustments
    print("  Testing small adjustments:")
    for offset in range(-1000, 1001):
        if 17 * k69 + 18 * k70 + offset == k75_actual:
            print(f"    ✅ EXACT: k75 = 17*k69 + 18*k70 + {offset}")
            break
    else:
        # Try other nearby coefficients
        print("  Testing nearby coefficients:")
        for a in range(15, 20):
            for b in range(16, 21):
                for offset in range(-100, 101):
                    if a * k69 + b * k70 + offset == k75_actual:
                        print(f"    ✅ EXACT: k75 = {a}*k69 + {b}*k70 + {offset}")
                        break

    print()

# k85 ≈ 4*k75 + 19*k80 (0.02% error)
if 85 in k_seq and 75 in k_seq and 80 in k_seq:
    k85_actual = k_seq[85]
    k75 = k_seq[75]
    k80 = k_seq[80]

    k85_pred = 4 * k75 + 19 * k80
    diff = k85_actual - k85_pred

    print("Match 2: k85 = 4*k75 + 19*k80")
    print(f"  k75 = {k75:#x}")
    print(f"  k80 = {k80:#x}")
    print(f"  Predicted: {k85_pred:#x}")
    print(f"  Actual:    {k85_actual:#x}")
    print(f"  Difference: {diff} ({diff:#x})")
    print(f"  Ratio: {diff / k85_actual if k85_actual != 0 else 0}")
    print()

    # Try small adjustments
    print("  Testing small adjustments:")
    for offset in range(-1000, 1001):
        if 4 * k75 + 19 * k80 + offset == k85_actual:
            print(f"    ✅ EXACT: k85 = 4*k75 + 19*k80 + {offset}")
            break
    else:
        # Try other nearby coefficients
        print("  Testing nearby coefficients:")
        for a in range(2, 7):
            for b in range(17, 22):
                for offset in range(-100, 101):
                    if a * k75 + b * k80 + offset == k85_actual:
                        print(f"    ✅ EXACT: k85 = {a}*k75 + {b}*k80 + {offset}")
                        break

    print()

# Check if there's a pattern in the coefficients
print("="*80)
print("PATTERN ANALYSIS")
print("="*80)
print()

# The coefficients were: (17, 18) for k75 and (4, 19) for k85
# Let me check if these relate to puzzle numbers or other sequences

print("Coefficients found:")
print("  k75: (17, 18)")
print("  k85: (4, 19)")
print()

print("Checking for patterns:")
print("  17 + 18 = 35")
print("  4 + 19 = 23")
print("  75 - 70 = 5 (gap)")
print("  85 - 80 = 5 (gap)")
print()

# Load m-sequence to check for connections
try:
    import json
    with open('/home/solo/LadderV3/kh-assist/data_for_csolver.json') as f:
        data = json.load(f)

    m_list = data['m_seq']
    d_list = data['d_seq']

    print("Checking m-sequence for these values:")
    for i, m in enumerate(m_list[:20], start=2):
        if m == 17:
            print(f"  m[{i}] = 17")
        if m == 18:
            print(f"  m[{i}] = 18")
        if m == 19:
            print(f"  m[{i}] = 19")
        if m == 23:
            print(f"  m[{i}] = 23")
        if m == 35:
            print(f"  m[{i}] = 35")
except:
    pass

print()
print("="*80)
