#!/usr/bin/env python3
"""Comprehensive analysis of m-sequence factorizations."""

import json
import subprocess
from collections import defaultdict

# Load data
with open('/home/solo/LA/data_for_csolver.json') as f:
    data = json.load(f)

m_list = data['m_seq']
d_list = data['d_seq']
m_seq = {n: m_list[n-2] for n in range(2, 2 + len(m_list))}
d_seq = {n: d_list[n-2] for n in range(2, 2 + len(d_list))}

def factor_gnu(n):
    """Fast factorization using GNU factor."""
    if n <= 1:
        return []
    result = subprocess.run(['factor', str(n)], capture_output=True, text=True)
    parts = result.stdout.strip().split(':')[1].strip().split()
    return [int(p) for p in parts]

print("="*80)
print("COMPREHENSIVE FACTORIZATION ANALYSIS")
print("="*80)
print()

# Analyze all m values
print("Small primes frequency analysis:")
small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
prime_counts = defaultdict(list)

for n in range(2, 71):
    m = m_seq[n]
    factors = factor_gnu(m)
    for p in small_primes:
        if p in factors:
            prime_counts[p].append(n)

for p in small_primes:
    if prime_counts[p]:
        print(f"  p={p:2d} appears at n={prime_counts[p]}")

print()
print("="*80)
print("DETAILED FACTORIZATIONS (first 30)")
print("="*80)
print()

for n in range(2, 32):
    m = m_seq[n]
    d = d_seq[n]
    factors = factor_gnu(m)

    # Count unique primes
    unique_primes = list(set(factors))

    # Represent factorization
    from collections import Counter
    factor_counts = Counter(factors)
    factor_str = ' × '.join([f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factor_counts.items())])

    print(f"n={n:2d}: m={m:>10} = {factor_str:30s}  d={d}")

print()
print("="*80)
print("PATTERN: m[6] = m[10] = 19")
print("="*80)
print()

# Find all duplicate m values
m_to_n = defaultdict(list)
for n, m in m_seq.items():
    m_to_n[m].append(n)

print("Duplicate m values:")
for m, ns in sorted(m_to_n.items()):
    if len(ns) > 1:
        print(f"  m={m} appears at n={ns}")

print()
print("="*80)
print("RELATIONSHIP BETWEEN n AND d[n]")
print("="*80)
print()

# Group by d value
d_groups = defaultdict(list)
for n, d in d_seq.items():
    d_groups[d].append(n)

for d, ns in sorted(d_groups.items()):
    print(f"d={d}: n values = {ns[:15]}{'...' if len(ns) > 15 else ''}")

print()
print("="*80)
print("TESTING: m[n] = some_function(n, d[n], m[earlier])")
print("="*80)
print()

# For each n, check if m[n] can be expressed using earlier values
print("Looking for m[n] expressed in terms of m[n-1], m[n-2], m[d[n]], etc:")
for n in range(4, 20):
    m = m_seq[n]
    d = d_seq[n]
    prev = m_seq.get(n-1, 0)
    prev2 = m_seq.get(n-2, 0)
    m_at_d = m_seq.get(d, 0)

    formulas = []

    # Check simple relationships
    if prev > 0 and m % prev == 0:
        formulas.append(f"m[{n-1}] × {m//prev}")
    if prev2 > 0 and m % prev2 == 0:
        formulas.append(f"m[{n-2}] × {m//prev2}")
    if m_at_d > 0 and m % m_at_d == 0:
        formulas.append(f"m[d] × {m//m_at_d}")

    # Check additive
    for k in range(2, n):
        mk = m_seq.get(k, 0)
        if mk > 0:
            if m > mk and (m - mk) in m_seq.values():
                for j, mj in m_seq.items():
                    if mj == m - mk and j < n:
                        formulas.append(f"m[{k}] + m[{j}]")

    # Check 2^something
    if m > 0:
        import math
        log2 = math.log2(m) if m > 0 else 0
        if abs(log2 - round(log2)) < 0.001:
            formulas.append(f"2^{int(round(log2))}")

    print(f"n={n:2d}: m={m:>8}, d={d}, possible: {formulas[:3] if formulas else 'None found'}")

print()
print("="*80)
print("SPECIAL ANALYSIS: n where d[n]=1 (referencing k[1]=1)")
print("="*80)
print()

d1_cases = [n for n in d_seq if d_seq[n] == 1]
print(f"Cases where d[n]=1: {d1_cases}")
print()
for n in d1_cases[:15]:
    m = m_seq[n]
    factors = factor_gnu(m)
    factor_counts = Counter(factors)
    factor_str = ' × '.join([f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factor_counts.items())])
    print(f"  n={n:2d}: m={m:>12} = {factor_str}")
