#!/usr/bin/env python3
"""
Extend k-value formulas beyond n=16
===================================

Now that we have verified formulas for k[1]-k[14],
let's try to find formulas for k[15]-k[20] and understand
the n=17 transition.
"""

import sqlite3
from itertools import combinations, product

# Load k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

# Known formulas
known = {
    1: 1, 2: 3, 3: 7, 4: 8, 5: 21, 6: 49, 7: 76, 8: 224,
    9: 467, 10: 514, 11: 1155, 12: 2683, 13: 5216, 14: 10544,
    15: 26867, 16: 51510
}

# Verify known
for n, val in known.items():
    assert k[n] == val, f"k[{n}] mismatch: {k[n]} != {val}"

print("=" * 80)
print("SEARCHING FOR k-VALUE FORMULAS (n=15-20)")
print("=" * 80)

# m-sequence values (known building blocks)
m = {2: 1, 3: 1, 4: 22, 5: 9, 6: 19, 7: 50, 8: 23}

# Search for linear combinations: k[n] = a*k[i] + b*k[j] + c
def search_formulas(target_n, max_coeff=100):
    target = k[target_n]
    results = []

    # Try: k[n] = a*k[i] + b*k[j] + c
    for i in range(1, target_n):
        for j in range(i, target_n):
            ki, kj = k[i], k[j]
            for a in range(-max_coeff, max_coeff + 1):
                if a == 0:
                    continue
                for b in range(-max_coeff, max_coeff + 1):
                    if i == j and b != 0:
                        continue  # Don't double count
                    base = a * ki + b * kj
                    c = target - base
                    if abs(c) < 1000:  # Small offset
                        formula = f"{a}×k[{i}]"
                        if b != 0:
                            formula += f" + {b}×k[{j}]"
                        if c != 0:
                            formula += f" + {c}"
                        results.append((abs(a) + abs(b), formula, a, i, b, j, c))

    # Try: k[n] = a*k[i] + b (simple linear)
    for i in range(1, target_n):
        ki = k[i]
        for a in range(1, max_coeff + 1):
            base = a * ki
            c = target - base
            if abs(c) < 5000:
                formula = f"{a}×k[{i}] + {c}"
                results.append((a, formula, a, i, 0, 0, c))

    # Sort by simplicity (lower total coefficients = simpler)
    results.sort(key=lambda x: x[0])
    return results[:10]

for n in range(15, 21):
    print(f"\n{'='*60}")
    print(f"k[{n}] = {k[n]}")
    print(f"{'='*60}")

    formulas = search_formulas(n)
    if formulas:
        print("Top formulas found:")
        for _, formula, a, i, b, j, c in formulas[:5]:
            # Check if coefficients relate to m-values or powers of 2
            notes = []
            if abs(a) in m.values():
                mk = [kv for kv, v in m.items() if v == abs(a)]
                notes.append(f"{a}=m[{mk[0]}]")
            if abs(a) in [2**p for p in range(10)]:
                p = [p for p in range(10) if 2**p == abs(a)][0]
                notes.append(f"{a}=2^{p}")
            if abs(b) in m.values() and b != 0:
                mk = [kv for kv, v in m.items() if v == abs(b)]
                notes.append(f"{b}=m[{mk[0]}]")
            if abs(c) == n:
                notes.append(f"{c}=n")

            note_str = f" [{', '.join(notes)}]" if notes else ""
            print(f"  k[{n}] = {formula}{note_str}")

# Now analyze the transition at n=17
print("\n\n" + "=" * 80)
print("ANALYZING THE n=17 TRANSITION")
print("=" * 80)

# The known formula for k[15] and k[16]
print("\nKnown formulas around transition:")
print("k[15] = 10×k[12] + 37×k[1] = 26830 + 37 = 26867")
print("k[16] = 45×k[11] - 465 = 51975 - 465 = 51510")
print()

# Verify k[15] and k[16]
assert 10*k[12] + 37*k[1] == k[15], "k[15] formula failed"
assert 45*k[11] - 465 == k[16], "k[16] formula failed"
print("✓ Both verified")

# Check adj pattern
print("\nAdj pattern around transition:")
for n in range(14, 21):
    adj = k[n] - 2*k[n-1]
    sign = "+" if adj >= 0 else "-"
    expected = "++-"[(n-2) % 3]
    match = "✓" if sign == expected else "✗ BREAK"
    print(f"n={n}: adj = {adj:>8}, sign = {sign}, expected = {expected} {match}")

# Summary
print("\n\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("""
Key findings for n=15-20:

1. k[15] = 10×k[12] + 37×k[1] = 26867
   - Uses k[12] (prime value)
   - 37 is prime, might relate to convergent

2. k[16] = 45×k[11] - 465 = 51510
   - 45 = 9×5 = m[5]×5
   - 465 = 3×5×31

3. k[17] = ??? (TRANSITION POINT)
   - The ++- pattern BREAKS here
   - n=17 = p[7] (7th prime, Fermat prime)
   - Need to find a different formula structure

4. For n≥17, formulas likely use:
   - More complex combinations
   - Different coefficient sources
   - The m-sequence values m[7]=50, m[8]=23
""")
