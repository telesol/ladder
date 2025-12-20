#!/usr/bin/env python3
"""Deep analysis of early keys (n=1-16) where ++- pattern is perfect."""

import sqlite3
import json
from fractions import Fraction
from math import gcd, sqrt, log2

# Load k values
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 16 ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

# Load m and d sequences
with open('/home/solo/LA/data_for_csolver.json') as f:
    data = json.load(f)
m_list = data['m_seq']
d_list = data['d_seq']
m = {n: m_list[n-2] for n in range(2, 17)}
d = {n: d_list[n-2] for n in range(2, 17)}

# Compute adj
adj = {n: k[n] - 2*k[n-1] for n in range(2, 17)}

print("="*80)
print("EARLY KEYS DEEP ANALYSIS (n=1-16)")
print("The 'Rosetta Stone' region where ++- pattern is PERFECT")
print("="*80)
print()

# Display all values
print("Complete data for n=1-16:")
print(f"{'n':>3} | {'k[n]':>10} | {'adj':>8} | {'sign':>4} | {'m':>6} | {'d':>2}")
print("-"*50)
for n in range(1, 17):
    kn = k[n]
    if n >= 2:
        an = adj[n]
        sign = '+' if an >= 0 else '-'
        mn = m[n]
        dn = d[n]
        print(f"{n:>3} | {kn:>10} | {an:>8} | {sign:>4} | {mn:>6} | {dn:>2}")
    else:
        print(f"{n:>3} | {kn:>10} |      n/a |  n/a |    n/a | n/a")

print()
print("="*80)
print("LOOKING FOR RECURRENCE IN k-SEQUENCE")
print("="*80)
print()

# Check k[n] = a*k[n-1] + b*k[n-2] + c
print("Testing k[n] = a*k[n-1] + b*k[n-2] + c:")
for n in range(3, 17):
    # Solve for a, b, c using three consecutive values
    # k[n] = a*k[n-1] + b*k[n-2] + c
    # k[n-1] = a*k[n-2] + b*k[n-3] + c
    # k[n-2] = a*k[n-3] + b*k[n-4] + c (if n >= 5)

    # Try simple forms
    kn, kn1, kn2 = k[n], k[n-1], k[n-2]

    # k[n] = 2*k[n-1] + adj (we know this works)
    check1 = 2*kn1 + adj[n] == kn

    # Try other forms
    for a in range(-5, 10):
        for b in range(-5, 10):
            c = kn - a*kn1 - b*kn2
            if abs(c) < 100:  # Small constant
                # Check if this works for previous n too
                if n >= 4:
                    c_prev = k[n-1] - a*k[n-2] - b*k[n-3]
                    if c == c_prev:
                        print(f"n={n}: k[n] = {a}*k[n-1] + {b}*k[n-2] + {c}")

print()
print("="*80)
print("RATIO ANALYSIS: k[n]/k[n-1]")
print("="*80)
print()

print("Checking if ratios converge or follow pattern:")
ratios = []
for n in range(2, 17):
    ratio = k[n] / k[n-1]
    ratios.append(ratio)
    print(f"k[{n}]/k[{n-1}] = {ratio:.6f}")

print()
print(f"Mean ratio: {sum(ratios)/len(ratios):.4f}")
print(f"Golden ratio φ = {(1+sqrt(5))/2:.4f}")
print(f"2.0 (expected from k[n] ≈ 2*k[n-1]): 2.0000")

print()
print("="*80)
print("GCD RELATIONSHIPS")
print("="*80)
print()

# Check GCDs between keys
print("GCD(k[i], k[j]) for small i, j:")
for i in range(1, 10):
    for j in range(i+1, 10):
        g = gcd(k[i], k[j])
        if g > 1:
            print(f"GCD(k[{i}], k[{j}]) = {g}")

print()
print("="*80)
print("EXPRESSING k[n] IN TERMS OF k[1], k[2], k[3]")
print("="*80)
print()

# k[1]=1, k[2]=3, k[3]=7
# Try to express later k values as linear combinations

k1, k2, k3 = k[1], k[2], k[3]
print(f"Base values: k[1]={k1}, k[2]={k2}, k[3]={k3}")
print()

for n in range(4, 17):
    kn = k[n]
    # Try k[n] = a*k[1] + b*k[2] + c*k[3]
    found = []
    for a in range(-20, 50):
        for b in range(-20, 50):
            for c in range(-20, 50):
                if a*k1 + b*k2 + c*k3 == kn:
                    if abs(a) + abs(b) + abs(c) < 100:  # Keep it simple
                        found.append((a, b, c))

    if found:
        # Pick simplest one
        found.sort(key=lambda x: abs(x[0]) + abs(x[1]) + abs(x[2]))
        a, b, c = found[0]
        print(f"k[{n:2d}] = {kn:>10} = {a}*k[1] + {b}*k[2] + {c}*k[3] = {a}*1 + {b}*3 + {c}*7")

print()
print("="*80)
print("FIBONACCI EXTENSION ANALYSIS")
print("="*80)
print()

# k[1]=1=F1, k[2]=3=F4, k[4]=8=F6, k[5]=21=F8
# Are these connected?

fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
print("Fibonacci: ", fib)
print()
print("k values that are Fibonacci:")
fib_set = set(fib)
for n in range(1, 17):
    if k[n] in fib_set:
        idx = fib.index(k[n]) + 1
        print(f"  k[{n}] = {k[n]} = F_{idx}")

print()
print("Checking k[n] = F_i + F_j:")
for n in range(1, 17):
    kn = k[n]
    for i, fi in enumerate(fib):
        for j, fj in enumerate(fib):
            if fi + fj == kn and i <= j:
                print(f"  k[{n}] = {kn} = F_{i+1} + F_{j+1} = {fi} + {fj}")

print()
print("="*80)
print("MODULAR ARITHMETIC PATTERNS")
print("="*80)
print()

for mod in [3, 7, 8, 11]:
    print(f"k[n] mod {mod}:")
    vals = [k[n] % mod for n in range(1, 17)]
    print(f"  {vals}")

print()
print("="*80)
print("BINARY STRUCTURE")
print("="*80)
print()

print("Binary representation (leading bits):")
for n in range(1, 17):
    kn = k[n]
    bits = bin(kn)[2:]
    print(f"k[{n:2d}] = {kn:>10} = {bits:>16s} ({len(bits)} bits)")

print()
print("="*80)
print("adj[n] ANALYSIS")
print("="*80)
print()

print("Looking for pattern in adj sequence:")
for n in range(2, 17):
    an = adj[n]
    # adj = 2^n - m*k[d]
    mn, dn = m[n], d[n]
    kd = k[dn]
    computed = 2**n - mn * kd
    check = "✓" if computed == an else "✗"
    print(f"adj[{n:2d}] = {an:>8} = 2^{n} - {mn}*k[{dn}] = {2**n} - {mn*kd} {check}")
