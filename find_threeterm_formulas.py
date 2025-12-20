#!/usr/bin/env python3
"""
Find three-term k-value formulas for even larger offsets
=========================================================

For n > 31, two-term formulas don't work.
Try: offset[n] = a×k[i] + b×k[j] + c×k[m] + d
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
print("FINDING THREE-TERM FORMULAS: offset = a×k[i] + b×k[j] + c×k[m] + d")
print("=" * 80)

def find_threeterm_formula(n, offset, max_coeff=30):
    """Find a×k[i] + b×k[j] + c×k[m] + d formula."""
    candidates = []

    # Use k values from recent range (n-10 to n-2)
    indices = list(range(max(1, n-12), n))

    for i, j, m in combinations(indices, 3):
        ki, kj, km = k[i], k[j], k[m]
        if ki == 0 or kj == 0 or km == 0:
            continue

        # For small a, b, c, find d
        for a in range(-max_coeff, max_coeff + 1):
            if a == 0:
                continue
            for b in range(-max_coeff, max_coeff + 1):
                if b == 0:
                    continue
                partial = a * ki + b * kj

                # Estimate c
                if km != 0:
                    c_est = (offset - partial) // km
                    for c in [c_est - 1, c_est, c_est + 1]:
                        if c == 0:
                            continue
                        if abs(c) > max_coeff:
                            continue
                        d = offset - (a * ki + b * kj + c * km)
                        if abs(d) < 2000:
                            complexity = abs(a) + abs(b) + abs(c) + abs(d) / 100
                            candidates.append((complexity, a, i, b, j, c, m, d))

    candidates.sort(key=lambda x: x[0])
    return candidates[:3] if candidates else []

# Find formulas for n=32-40
print("\n### THREE-TERM FORMULAS FOR n=32-40 ###\n")

for n in range(32, 41):
    off = offsets[n]
    best = find_threeterm_formula(n, off)

    if best:
        _, a, i, b, j, c, m, d = best[0]
        computed = a * k[i] + b * k[j] + c * k[m] + d
        match = "✓" if computed == off else "✗"
        sign_d = '+' if d >= 0 else ''
        formula = f"{a}×k[{i}] + {b}×k[{j}] + {c}×k[{m}] {sign_d}{d}"
        print(f"offset[{n}] = {formula} {match}")
    else:
        print(f"offset[{n}] = {off} (no three-term formula found)")

# Now the key question: can we derive k[71]?
print("\n\n" + "=" * 80)
print("THE PATH TO k[71]")
print("=" * 80)

print("""
We have established:
1. k[n] = 9 × k[n-3] + offset[n]  for n ≥ 10

2. offset[n] is a linear combination of earlier k-values:
   - n=10-22: offset = a×k[i] + c (one term)
   - n=23-31: offset = a×k[i] + b×k[j] + c (two terms)
   - n=32+:   offset = a×k[i] + b×k[j] + c×k[m] + d (three+ terms)

3. To compute k[71], we need:
   k[71] = 9 × k[68] + offset[71]

4. We know k[68], k[69], k[70] from the database.

5. The challenge: derive offset[71] from k[68-70] and earlier values.
""")

# Let's examine the pattern of which k-values are used in offsets
print("\n### PATTERN: WHICH k-VALUES ARE USED IN OFFSETS? ###\n")

# From our discoveries
formulas = {
    10: [(-1, 8)],
    11: [(-2, 9)],
    12: [(-3, 10)],
    13: [(1, 10)],
    14: [(1, 7)],
    15: [(1, 12)],
    23: [(-4, 17), (-5, 19)],
    24: [(-3, 17), (-8, 18)],
    25: [(2, 16), (2, 22)],
    30: [(9, 19), (4, 23)],
    31: [(-32, 15), (1, 26)],
}

print("For each n, the k-indices used relative to n:")
for n, terms in formulas.items():
    indices = [t[1] for t in terms]
    diffs = [n - i for i in indices]
    print(f"  n={n}: uses k[{indices}], diffs from n: {diffs}")

print("""
OBSERVATION:
- Single-term: uses k[n-2] to k[n-5] range
- Two-term: uses k[n-4] to k[n-8] range
- The referenced k-values are always BEFORE the mod-3 base (k[n-3])

HYPOTHESIS FOR k[71]:
offset[71] = a×k[67] + b×k[68] + c×k[69] + d×k[70] + e

where a, b, c, d are small integers and e < 2000
""")
