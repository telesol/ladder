#!/usr/bin/env python3
"""
Deep analysis of m-sequence to find prediction patterns
========================================================

Goal: Find patterns that can predict m[71] and beyond
"""

import sqlite3
import json
from math import log2

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']
d_seq = data['d_seq']

m = {i+2: m_seq[i] for i in range(len(m_seq))}
d = {i+2: d_seq[i] for i in range(len(d_seq))}

# Load k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

def factorint(n):
    factors = {}
    d_val = 2
    while d_val * d_val <= n:
        while n % d_val == 0:
            factors[d_val] = factors.get(d_val, 0) + 1
            n //= d_val
        d_val += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

print("=" * 80)
print("M-SEQUENCE DEEP ANALYSIS")
print("=" * 80)

# Basic statistics
print("\n### BASIC STATISTICS ###")
print(f"Range: m[2] to m[70]")
print(f"Min m: {min(m.values())} at n={[n for n,v in m.items() if v==min(m.values())]}")
print(f"Max m: {max(m.values())} at n={[n for n,v in m.items() if v==max(m.values())]}")

# Growth rate
print("\n### GROWTH RATE ###")
print("log2(m[n]) / n:")
for n in [10, 20, 30, 40, 50, 60, 70]:
    if n in m and m[n] > 0:
        ratio = log2(m[n]) / n
        print(f"  n={n}: log2(m[{n}])/n = {ratio:.4f}")

# m[n] / 2^n ratio
print("\n### m[n] / 2^n RATIO ###")
for n in [10, 20, 30, 40, 50, 60, 70]:
    if n in m:
        ratio = m[n] / (2**n)
        print(f"  n={n}: m[{n}]/2^n = {ratio:.6e}")

# Factorization patterns
print("\n### FACTORIZATION PATTERNS ###")
print("Common prime factors:")

prime_counts = {}
for n in range(2, 71):
    factors = factorint(m[n])
    for p in factors:
        if p not in prime_counts:
            prime_counts[p] = []
        prime_counts[p].append(n)

# Show primes that appear in many m-values
for p in sorted(prime_counts.keys())[:20]:
    if len(prime_counts[p]) >= 3:
        print(f"  p={p}: appears in m[{','.join(map(str, prime_counts[p][:10]))}...]")

# m-value differences
print("\n### CONSECUTIVE DIFFERENCES ###")
print("m[n] - m[n-1] for n=3..15:")
for n in range(3, 16):
    diff = m[n] - m[n-1]
    print(f"  m[{n}] - m[{n-1}] = {m[n]} - {m[n-1]} = {diff}")

# Ratio to k values
print("\n### m[n] / k[d[n]] RATIO ###")
print("This gives the 'multiplier' in adj = 2^n - m×k[d]")
for n in range(2, 21):
    ratio = m[n] / k[d[n]] if d[n] in k else "N/A"
    print(f"  n={n}: m[{n}]/k[{d[n]}] = {m[n]}/{k[d[n]]} = {ratio:.2f}")

# Try to find m[n] = f(m[earlier]) pattern
print("\n### SELF-REFERENTIAL PATTERNS ###")
print("Testing m[n] = a×m[i] + b for small a,b")

for n in range(10, 21):
    found = []
    for i in range(2, n):
        if m[i] > 0:
            # m[n] = a×m[i] + b
            a = m[n] // m[i]
            for aa in [a-1, a, a+1]:
                if aa > 0:
                    b = m[n] - aa * m[i]
                    if abs(b) < m[i] and abs(b) < 100:
                        found.append((aa, i, b))
    if found:
        print(f"  m[{n}] = {m[n]}")
        for a, i, b in found[:3]:
            print(f"    = {a}×m[{i}] + {b} = {a}×{m[i]} + {b}")

# Look for m[n] relationship with n and k values
print("\n### RELATIONSHIP WITH n ###")
for n in range(2, 21):
    # m[n] mod n
    mod_n = m[n] % n
    # m[n] mod k[i] for small i
    mod_k1 = m[n] % k[1] if k[1] else "N/A"
    mod_k2 = m[n] % k[2]
    mod_k3 = m[n] % k[3]

    print(f"  m[{n:2}] = {m[n]:>6}  mod n={mod_n}, mod k[2]={mod_k2}, mod k[3]={mod_k3}")

# Check if m[n] relates to 2^n
print("\n### RELATIONSHIP WITH 2^n ###")
for n in range(2, 21):
    # What is 2^n mod m[n]?
    if m[n] > 0:
        remainder = (2**n) % m[n]
        quot = (2**n) // m[n]
        print(f"  2^{n} = {quot}×m[{n}] + {remainder}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY AND PREDICTION APPROACH")
print("=" * 80)
print("""
KEY OBSERVATIONS:
1. m[n] grows approximately as 2^(0.8n) to 2^(0.9n)
2. Common prime factors: 2, 3, 17 appear frequently
3. Self-referential patterns exist for some n

PREDICTION APPROACH FOR m[71]:
1. Estimate magnitude: m[71] ≈ 2^(0.85×71) ≈ 2^60 ≈ 10^18
2. Look for factor 17 pattern (might be present if 71 ≈ 2×36-1)
3. Check if m[71] = a×m[earlier] + b for small coefficients
4. Use constraint: (2^71 - adj[71]) must be divisible by k[d[71]]

NEXT STEPS:
1. Build prediction model based on growth rate
2. Constrain using factorization patterns
3. Verify against k-sequence formulas
""")
