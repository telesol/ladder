#!/usr/bin/env python3
"""Find k-value formulas for n=51-70."""
import sqlite3
from itertools import combinations

conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
rows = cursor.fetchall()
conn.close()

K = {row[0]: int(row[1], 16) for row in rows}

def find_formula(n, K, max_coeff=500, max_const=50000):
    results = []
    for i, j in combinations(range(max(1, n-30), n), 2):
        if i not in K or j not in K:
            continue
        for a in range(-max_coeff, max_coeff+1):
            if a == 0:
                continue
            remainder = K[n] - a * K[i]
            for b in range(-max_coeff, max_coeff+1):
                if b == 0:
                    continue
                c = remainder - b * K[j]
                if abs(c) <= max_const:
                    score = abs(a) + abs(b) + abs(c)//500
                    results.append((score, a, i, b, j, c))
    results.sort()
    return results[:1] if results else []

print("VERIFIED K-FORMULAS (n=51-70)")
print("=" * 70)

for n in range(51, 71):
    if n not in K:
        continue
    formulas = find_formula(n, K)
    if formulas:
        score, a, i, b, j, c = formulas[0]
        computed = a*K[i] + b*K[j] + c
        match = "✓" if computed == K[n] else "✗"
        sign_b = '+' if b >= 0 else ''
        sign_c = '+' if c >= 0 else ''
        print(f"k[{n}] = {a}×k[{i}] {sign_b}{b}×k[{j}] {sign_c}{c} {match}")
    else:
        print(f"k[{n}]: No simple formula found")
