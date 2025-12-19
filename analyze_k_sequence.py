#!/usr/bin/env python3
"""Analyze the k-sequence to find generation pattern."""

import json
import sqlite3
from collections import defaultdict
import subprocess

# Load k values from database
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
k_seq = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

print("="*80)
print("K-SEQUENCE ANALYSIS")
print("="*80)
print()

# Print k values
print("K values (n=1 to 20):")
for n in range(1, 21):
    k = k_seq.get(n, 'N/A')
    if isinstance(k, int):
        print(f"  k[{n:2d}] = {k:>15} = 0x{k:x}")

print()
print("="*80)
print("FIBONACCI RELATIONSHIP")
print("="*80)
print()

# Generate Fibonacci numbers
fib = [1, 1]
while fib[-1] < 10**30:
    fib.append(fib[-1] + fib[-2])

print("Fibonacci numbers:", fib[:20])
print()

# Check which k values are Fibonacci
print("K values that are Fibonacci:")
fib_set = set(fib)
for n, k in sorted(k_seq.items())[:30]:
    if k in fib_set:
        idx = fib.index(k) + 1  # 1-indexed
        print(f"  k[{n}] = {k} = F_{idx}")

print()
print("="*80)
print("PRIME FACTORIZATION OF K VALUES")
print("="*80)
print()

def factor_gnu(n):
    if n <= 1:
        return f"{n}"
    result = subprocess.run(['factor', str(n)], capture_output=True, text=True)
    parts = result.stdout.strip().split(':')[1].strip()
    return parts

for n in range(1, 25):
    k = k_seq.get(n)
    if k:
        factors = factor_gnu(k)
        print(f"k[{n:2d}] = {k:>15} = {factors}")

print()
print("="*80)
print("RATIOS k[n] / k[n-1]")
print("="*80)
print()

print("Ratio analysis (should be ~2 if k[n] = 2*k[n-1] + small adjustment):")
for n in range(2, 25):
    k_n = k_seq.get(n)
    k_prev = k_seq.get(n-1)
    if k_n and k_prev:
        ratio = k_n / k_prev
        adj = k_n - 2*k_prev
        print(f"k[{n:2d}]/k[{n-1:2d}] = {ratio:.6f}, adj = {adj:>10}")

print()
print("="*80)
print("BINARY REPRESENTATION")
print("="*80)
print()

print("Number of bits in k[n]:")
for n in range(1, 71):
    k = k_seq.get(n)
    if k:
        bits = k.bit_length()
        expected = n  # k[n] should be n bits
        match = "✓" if bits == n else f"✗ (expected {n})"
        if n <= 20 or bits != n:
            print(f"k[{n:2d}] has {bits:2d} bits {match}")

print()
print("="*80)
print("POSITION WITHIN RANGE")
print("="*80)
print()

print("Position of k[n] within [2^(n-1), 2^n - 1]:")
for n in range(2, 25):
    k = k_seq.get(n)
    if k:
        low = 2**(n-1)
        high = 2**n - 1
        range_size = high - low + 1
        position = k - low
        pct = 100 * position / range_size
        print(f"k[{n:2d}]: position {position:>10} / {range_size:>10} = {pct:6.2f}%")

print()
print("="*80)
print("CHECKING: k[n] % small_primes")
print("="*80)
print()

small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
for p in small_primes[:5]:
    divisible = [n for n in range(1, 71) if k_seq.get(n) and k_seq[n] % p == 0]
    print(f"k[n] divisible by {p}: n = {divisible[:15]}{'...' if len(divisible) > 15 else ''}")

print()
print("="*80)
print("DIGIT SUM ANALYSIS")
print("="*80)
print()

def digit_sum(n):
    return sum(int(d) for d in str(n))

for n in range(1, 25):
    k = k_seq.get(n)
    if k:
        ds = digit_sum(k)
        print(f"k[{n:2d}] = {k:>15}, digit_sum = {ds:>3}, digit_sum mod 9 = {ds % 9}")

print()
print("="*80)
print("CHECKING: k[n] mod n")
print("="*80)
print()

for n in range(1, 40):
    k = k_seq.get(n)
    if k and n > 0:
        mod_n = k % n
        if mod_n == 0:
            print(f"k[{n:2d}] ≡ 0 (mod {n})  -- k[n] is divisible by n!")
