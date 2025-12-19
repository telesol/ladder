#!/usr/bin/env python3
"""
Deep pattern search for m-sequence and d-sequence.
Looking for the generation formula.
"""

import json
from sympy import prime, primepi, factorint, isprime
from collections import defaultdict

# Load the data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

def m(n):
    if n < 2 or n > 71:
        return None
    return m_seq[n - 2]

def d(n):
    if n < 2 or n > 71:
        return None
    return d_seq[n - 2]

print("=" * 70)
print("DEEP PATTERN SEARCH: Looking for m[n] = f(17, n, earlier_m)")
print("=" * 70)

# For all m values divisible by 17, find the pattern
print("\n### All m[n] divisible by 17:")
print("n    m[n]           17^k  cofactor       cofactor_pi  formula_check")
print("-" * 70)

for n in range(2, 71):
    mv = m(n)
    if mv is None:
        continue
    factors = factorint(mv)
    if 17 in factors:
        k = factors[17]
        cofactor = mv // (17 ** k)
        if isprime(cofactor):
            cf_pi = int(primepi(cofactor))
            # Check all possible formulas n + m[j] or n - m[j]
            formula = ""
            for j in range(2, n):
                mj = m(j)
                if mj is not None:
                    if n + mj == cf_pi:
                        formula = f"n + m[{j}] = {n} + {mj} = {cf_pi}"
                        break
                    if n - mj == cf_pi and cf_pi > 0:
                        formula = f"n - m[{j}] = {n} - {mj} = {cf_pi}"
                        break
                    if n * mj == cf_pi:
                        formula = f"n × m[{j}] = {n} × {mj} = {cf_pi}"
                        break
            print(f"{n:3}  {mv:<14} 17^{k}  {cofactor:<13}  {cf_pi:<11}  {formula}")
        else:
            print(f"{n:3}  {mv:<14} 17^{k}  {cofactor:<13}  (composite)")

print("\n" + "=" * 70)
print("LOOKING AT d-SEQUENCE RULES")
print("=" * 70)

# Check if d[n] relates to factorization of n or some other property
print("\n### d[n] vs various properties of n:")
print("n   d[n]  n%8  n%4  (n-2)%8  lowbit  hibit")
for n in range(2, 32):
    dv = d(n)
    lowbit = (n & -n).bit_length()  # Position of lowest set bit
    hibit = n.bit_length()  # Position of highest set bit
    print(f"{n:3} {dv:4}  {n%8:3}  {n%4:3}  {(n-2)%8:7}  {lowbit:6}  {hibit:5}")

# Look for patterns when d=1
print("\n### When d[n] = 1 (reference previous k):")
d1_positions = [n for n in range(2, 71) if d(n) == 1]
print(f"Positions: {d1_positions[:20]}...")
print(f"Differences: {[d1_positions[i+1] - d1_positions[i] for i in range(min(15, len(d1_positions)-1))]}")

# Look for patterns when d=2
print("\n### When d[n] = 2:")
d2_positions = [n for n in range(2, 71) if d(n) == 2]
print(f"Positions: {d2_positions[:20]}...")

# Look for patterns when d=4
print("\n### When d[n] = 4:")
d4_positions = [n for n in range(2, 71) if d(n) == 4]
print(f"Positions: {d4_positions}")

print("\n" + "=" * 70)
print("CHECKING m[n] / 2^n RATIO")
print("=" * 70)

print("\n### m[n] / 2^n (normalized m):")
print("n    m[n]                2^n                   m/2^n")
for n in range(2, 32):
    mv = m(n)
    pow2 = 2**n
    ratio = mv / pow2
    print(f"{n:3}  {mv:<18}  {pow2:<20}  {ratio:.10f}")

print("\n" + "=" * 70)
print("CHECKING SELF-REFERENCE: m[n] vs m[d[n]]")
print("=" * 70)

print("\n### m[n] / m[d[n]] ratio:")
print("n    d[n]  m[n]           m[d[n]]        m[n]/m[d[n]]")
for n in range(2, 32):
    dv = d(n)
    mv = m(n)
    md = m(dv) if dv >= 2 else 1
    ratio = mv / md if md > 0 else 0
    print(f"{n:3}  {dv:4}  {mv:<13}  {md:<13}  {ratio:.4f}")

print("\n" + "=" * 70)
print("LOOKING FOR RECURRENCE: m[n] = a*m[n-1] + b*m[n-2] + ...")
print("=" * 70)

# Check if m[n] = f(m[n-1], m[n-2], 2^n, d[n])
print("\n### Checking m[n] = 2^n / d[n] + offset:")
print("n    m[n]           2^n/d[n]       diff")
for n in range(2, 32):
    mv = m(n)
    dv = d(n)
    predicted = 2**n // dv
    diff = mv - predicted
    print(f"{n:3}  {mv:<13}  {predicted:<13}  {diff}")

print("\n### Checking m[n] ~ c * 2^n (find c):")
print("n    m[n]           m[n]/2^n       log2(m[n])")
import math
for n in range(2, 32):
    mv = m(n)
    c = mv / (2**n)
    log2m = math.log2(mv) if mv > 0 else 0
    print(f"{n:3}  {mv:<13}  {c:.8f}     {log2m:.4f}")
