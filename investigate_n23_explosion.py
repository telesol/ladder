#!/usr/bin/env python3
"""
Investigate why the pattern explodes at n=23
=============================================

The mod-3 recursive pattern k[n] = 9×k[n-3] + a×k[5] + b
works for n=11,14,17,20 but explodes at n=23.

Questions:
1. What's special about n=23?
2. Does a different formula structure apply for n ≥ 23?
3. Is there a meta-pattern for the coefficient explosion?
"""

import sqlite3
import json

# Load data
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']
d_seq = data['d_seq']

m = {i+2: m_seq[i] for i in range(len(m_seq))}
d = {i+2: d_seq[i] for i in range(len(d_seq))}

# Primes
primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
p = {i+1: primes[i] for i in range(len(primes))}
prime_idx = {primes[i]: i+1 for i in range(len(primes))}

print("=" * 80)
print("INVESTIGATING n=23 PATTERN EXPLOSION")
print("=" * 80)

# Properties of n=23
print("\n### PROPERTIES OF n=23 ###")
print(f"23 = p[9] (9th prime)")
print(f"23 = 7 + 16 = k[3] + 2^4")
print(f"23 = 3 × 7 + 2 = k[5] + 2")
print(f"23 mod 3 = {23 % 3}")
print(f"k[23] = {k[23]}")

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

print(f"k[23] factors: {factorint(k[23])}")
print(f"d[23] = {d[23]}")
print(f"m[23] = {m[23]}")

# Analyze the coefficient patterns up to n=26
print("\n### COEFFICIENT ANALYSIS (n ≡ 2 mod 3) ###")
print("k[n] = 9×k[n-3] + a×k[5] + b\n")

for n in [11, 14, 17, 20, 23, 26, 29, 32, 35, 38]:
    if n-3 in k and n in k:
        base = 9 * k[n-3]
        remainder = k[n] - base
        a = remainder // 21
        b = remainder % 21

        # Handle negative remainders
        if remainder < 0:
            a = (remainder - 20) // 21
            b = remainder - a * 21

        print(f"n={n:2}: a={a:>10}, b={b:>3}  (k[n]={k[n]:>15}, 9×k[n-3]={base:>15})")

# Try alternative formulas for n=23
print("\n### ALTERNATIVE FORMULAS FOR n=23 ###")
k23 = k[23]

# Try k[n] = c × k[n-3] + d × k[n-6] + e
print("\nForm: k[n] = c×k[n-3] + d×k[n-6] + e")
for c in range(1, 20):
    for d_coef in range(-50, 51):
        val = c * k[20] + d_coef * k[17]
        if abs(k23 - val) < 1000:
            e = k23 - val
            print(f"  k[23] = {c}×k[20] + {d_coef}×k[17] + {e}")

# Try k[n] = c × k[n-3] + d × k[j] for various j
print("\nForm: k[n] = c×k[n-3] + d×k[j] + e (small e)")
for c in range(1, 15):
    for j in range(1, 20):
        if j != 20:
            for d_coef in range(-100, 101):
                val = c * k[20] + d_coef * k[j]
                if abs(k23 - val) < 50:
                    e = k23 - val
                    print(f"  k[23] = {c}×k[20] + {d_coef}×k[{j}] + {e}")

# Check if different recursive structure applies
print("\n### TRYING DIFFERENT RECURSION DEPTHS ###")

# k[n] = a×k[n-6] + b (skipping 6 instead of 3)
print("\nForm: k[n] = a×k[n-6] + offset")
for n in [17, 20, 23, 26, 29]:
    if n-6 >= 1 and n in k:
        for a in range(1, 100):
            if a * k[n-6] <= k[n]:
                offset = k[n] - a * k[n-6]
                if offset < 10000 and offset > -10000:
                    print(f"  k[{n}] = {a}×k[{n-6}] + {offset}")
                    break

# k[n] = a×k[n-9] + b (skipping 9 instead of 3)
print("\nForm: k[n] = a×k[n-9] + offset")
for n in [20, 23, 26, 29, 32]:
    if n-9 >= 1 and n in k:
        for a in range(1, 200):
            if a * k[n-9] <= k[n]:
                offset = k[n] - a * k[n-9]
                if offset < 10000 and offset > -10000:
                    print(f"  k[{n}] = {a}×k[{n-9}] + {offset}")
                    break

# Check the "phase" theory: different formula after n=17
print("\n### PHASE ANALYSIS (after n=17 transition) ###")

# For n > 17, try k[n] = 2×k[n-1] + adj[n] and analyze adj
print("\nAdj pattern after n=17:")
for n in range(18, 30):
    if n-1 in k and n in k:
        adj = k[n] - 2*k[n-1]
        ratio = k[n] / k[n-1]
        print(f"n={n}: k[n]/k[n-1] = {ratio:.6f}, adj = {adj:>10}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
FINDINGS:
1. n=23 = p[9] (9th prime) is special
2. The simple 9×k[n-3] + a×k[5] + b formula explodes here
3. Alternative recursion depths (6, 9) might work better

HYPOTHESIS:
The pattern changes at critical points:
- n=4: Transition from Mersenne to convergent-based
- n=17: Transition from ++- to irregular sign pattern (p[7])
- n=23: Transition to different recursion structure (p[9])

The puzzle creator may have used different formula "phases"
at prime milestones.
""")
