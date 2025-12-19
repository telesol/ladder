#!/usr/bin/env python3
"""Analyze the adjustment sequence adj[n] = k[n] - 2*k[n-1]."""

import json
import sqlite3

# Load k values from database
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
k_seq = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

# Compute adj sequence
adj_seq = {}
for n in range(2, 71):
    if n in k_seq and n-1 in k_seq:
        adj_seq[n] = k_seq[n] - 2 * k_seq[n-1]

print("="*80)
print("ADJUSTMENT SEQUENCE: adj[n] = k[n] - 2*k[n-1]")
print("="*80)
print()

# Print adj values
for n in range(2, 31):
    adj = adj_seq.get(n)
    if adj is not None:
        sign = "+" if adj >= 0 else ""
        print(f"adj[{n:2d}] = {sign}{adj:>12}")

print()
print("="*80)
print("SIGN PATTERN IN ADJ SEQUENCE")
print("="*80)
print()

signs = ""
for n in range(2, 71):
    adj = adj_seq.get(n)
    if adj is not None:
        signs += "+" if adj >= 0 else "-"
print(f"Signs: {signs}")
print()

# Count consecutive same signs
runs = []
current_sign = None
current_count = 0
for s in signs:
    if s == current_sign:
        current_count += 1
    else:
        if current_sign is not None:
            runs.append((current_sign, current_count))
        current_sign = s
        current_count = 1
runs.append((current_sign, current_count))

print(f"Runs of same sign: {runs[:20]}")
print(f"Total runs: {len(runs)}")
print()

# Check if there's any periodicity
print("="*80)
print("CHECKING PERIODICITY IN SIGN PATTERN")
print("="*80)
print()

for period in range(2, 20):
    matches = 0
    total = 0
    for i in range(len(signs) - period):
        total += 1
        if signs[i] == signs[i + period]:
            matches += 1
    if total > 0:
        pct = 100 * matches / total
        if pct > 60 or pct < 40:  # Only show interesting patterns
            print(f"Period {period:2d}: {matches}/{total} matches ({pct:.1f}%)")

print()
print("="*80)
print("MAGNITUDE ANALYSIS OF ADJ")
print("="*80)
print()

# Check how adj relates to 2^n
print("Ratio |adj[n]| / 2^n:")
for n in range(2, 31):
    adj = adj_seq.get(n)
    if adj is not None:
        ratio = abs(adj) / (2**n)
        print(f"n={n:2d}: |adj|={abs(adj):>12}, 2^n={2**n:>12}, ratio={ratio:.6f}")

print()
print("="*80)
print("ADJ AS FUNCTION OF EARLIER VALUES")
print("="*80)
print()

# Check if adj[n] relates to earlier adj values
print("Checking adj[n] = f(adj[n-1]):")
for n in range(3, 20):
    adj_n = adj_seq.get(n)
    adj_prev = adj_seq.get(n-1)
    if adj_n is not None and adj_prev is not None and adj_prev != 0:
        ratio = adj_n / adj_prev
        print(f"adj[{n:2d}]/adj[{n-1:2d}] = {adj_n:>10} / {adj_prev:>10} = {ratio:>10.4f}")

print()
print("="*80)
print("FACTORIZATION OF ADJ VALUES")
print("="*80)
print()

import subprocess
def factor_gnu(n):
    if n == 0:
        return "0"
    if n < 0:
        sign = "-"
        n = abs(n)
    else:
        sign = ""
    result = subprocess.run(['factor', str(n)], capture_output=True, text=True)
    parts = result.stdout.strip().split(':')[1].strip()
    return sign + parts

for n in range(2, 25):
    adj = adj_seq.get(n)
    if adj is not None:
        factors = factor_gnu(adj)
        print(f"adj[{n:2d}] = {adj:>12} = {factors}")
