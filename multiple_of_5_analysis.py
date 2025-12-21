#!/usr/bin/env python3
"""
Why are gap puzzles at multiples of 5 (75, 80, 85, 90)?

This script analyzes patterns specific to n ≡ 0 (mod 5).
"""
import sqlite3
import json
from pathlib import Path
import math

# Load known k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 161):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

# Load m and d values
data_file = Path('data_for_csolver.json')
if data_file.exists():
    with open(data_file) as f:
        data = json.load(f)
        m_seq = data.get('m_seq', [])
        d_seq = data.get('d_seq', [])
else:
    m_seq = []
    d_seq = []

print("=" * 80)
print("MULTIPLE OF 5 ANALYSIS - Why gaps at 75, 80, 85, 90?")
print("=" * 80)
print()

# All multiples of 5 from 5 to 70
mult5 = [n for n in range(5, 71) if n % 5 == 0]
print(f"Multiples of 5 in [5, 70]: {mult5}")
print()

# Analyze d[n] for multiples of 5
print("### d[n] for n ≡ 0 (mod 5) ###")
print()
print("n    | d[n] | m[n]")
print("-----|------|----")
for n in mult5:
    i = n - 2  # Index into m_seq, d_seq
    if 0 <= i < len(d_seq):
        d = d_seq[i]
        m = m_seq[i]
        print(f"{n:4d} | {d:4d} | {m}")

print()

# Check if there's a pattern in d[n] for multiples of 5
d_at_mult5 = []
for n in mult5:
    i = n - 2
    if 0 <= i < len(d_seq):
        d_at_mult5.append((n, d_seq[i]))

print("d[n] values at multiples of 5:")
print([d for _, d in d_at_mult5])
print()

# Ratio patterns between consecutive multiples of 5
print("### Ratio k[n+5]/k[n] for multiples of 5 ###")
print()
print("n    | k[n+5]/k[n]      | Expected (2^5=32)")
print("-----|------------------|------------------")
for n in mult5:
    if n + 5 in k_values and n in k_values:
        ratio = k_values[n + 5] / k_values[n]
        diff = ratio - 32
        print(f"{n:4d} | {ratio:16.4f} | diff = {diff:+.4f}")

print()

# Special property: k[5n] / k[n] relationship?
print("### Is there k[5n] / k[n] pattern? ###")
print()
for n in [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14]:
    if n in k_values and 5*n in k_values:
        ratio = k_values[5*n] / k_values[n]
        log_ratio = math.log2(ratio)
        print(f"k[{5*n}] / k[{n}] = {ratio:.4f} (log2 = {log_ratio:.2f})")

print()

# Gap structure: 70 → 75 → 80 → 85 → 90
print("### Gap Structure Analysis ###")
print()
print("The consecutive k values stop at k[70], then jump to k[75].")
print("Then 5-step intervals: 75 → 80 → 85 → 90")
print()

# Compute offsets between gap puzzles
gaps = [70, 75, 80, 85, 90]
print("Offsets between gap puzzles (k[n] - 32*k[n-5]):")
print()
for i in range(1, len(gaps)):
    n = gaps[i]
    prev = gaps[i-1]
    if n in k_values and prev in k_values:
        offset = k_values[n] - 32 * k_values[prev]
        print(f"k[{n}] - 32*k[{prev}] = {offset}")
        print(f"  = {offset / k_values[prev]:.6f} × k[{prev}]")

print()

# Recursive 5-step formula test
# k[n] = α * k[n-5] + β * k[n-10] + ... ?
print("### Testing 5-step recursion ###")
print()
print("Hypothesis: k[n] = a*k[n-5] + b*k[n-10] + c")
print()

# For n=70, 65, 60, 55, 50, ...
for n in [70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20]:
    if n in k_values and (n-5) in k_values and (n-10) in k_values:
        # k[n] = a*k[n-5] + b*k[n-10]
        # This is underdetermined... let's try k[n] = 32*k[n-5] + offset
        offset = k_values[n] - 32 * k_values[n-5]
        k_n5 = k_values[n-5]
        k_n10 = k_values[n-10]

        # Try to express offset in terms of k[n-10]
        if k_n10 != 0:
            offset_ratio = offset / k_n10
            print(f"n={n:2d}: offset = {offset:20d} = {offset_ratio:.4f} × k[{n-10}]")

print()

# The key question: what determines the 5-step jump values?
print("### Key Question ###")
print()
print("The gap puzzles (75, 80, 85, 90) exist without intermediates.")
print("This means the formula k[n] = f(n) can be computed for ANY n,")
print("not just consecutive values.")
print()
print("The 5-step structure suggests:")
print("1. The formula is related to 2^5 = 32")
print("2. Or the formula is related to mod 5 properties")
print("3. Or the creator wanted to reveal the '5-step ladder' structure")
print()

# Check if 5 has special meaning in the sequence
print("### Divisibility by 5 ###")
print()
div_by_5 = [n for n, k in k_values.items() if k % 5 == 0]
print(f"k[n] divisible by 5: {sorted(div_by_5)[:20]}...")
print(f"Total: {len(div_by_5)} out of {len(k_values)}")
print()

# Check m values for multiples of 5
print("### m[n] for n ≡ 0 (mod 5) ###")
print()
for n in mult5:
    i = n - 2
    if 0 <= i < len(m_seq):
        m = m_seq[i]
        if m % 5 == 0:
            print(f"m[{n}] = {m} (divisible by 5!)")
        else:
            print(f"m[{n}] = {m}")
