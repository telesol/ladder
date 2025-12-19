#!/usr/bin/env python3
"""
Test the self-reference formula on ALL 70 m-values.
Pattern: Does m[n] divide m[n + m[n]]?
"""

import json
from math import gcd

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

def m(n):
    if n < 2 or n > 70:
        return None
    return m_seq[n - 2]

def d(n):
    if n < 2 or n > 70:
        return None
    return d_seq[n - 2]

print("=" * 80)
print("SELF-REFERENCE TEST: Does m[n] divide m[n + m[n]]?")
print("=" * 80)

# Test all values
successes = []
failures = []
out_of_bounds = []

for n in range(2, 71):
    mn = m(n)
    if mn is None:
        continue

    target_n = n + mn
    target_m = m(target_n)

    if target_m is None:
        out_of_bounds.append((n, mn, target_n))
        continue

    if mn == 0:
        continue

    if target_m % mn == 0:
        quotient = target_m // mn
        successes.append((n, mn, target_n, target_m, quotient))
    else:
        remainder = target_m % mn
        failures.append((n, mn, target_n, target_m, remainder))

print(f"\n### Results:")
print(f"  Successes: {len(successes)}")
print(f"  Failures: {len(failures)}")
print(f"  Out of bounds: {len(out_of_bounds)}")

print("\n### Successful self-references:")
print("n    m[n]           n+m[n]  m[n+m[n]]           quotient")
print("-" * 80)
for n, mn, tn, tm, q in successes:
    print(f"{n:3}  {mn:<14} {tn:6}  {tm:<18} {q}")

print("\n### Failed self-references (first 20):")
print("n    m[n]           n+m[n]  m[n+m[n]]           remainder")
print("-" * 80)
for n, mn, tn, tm, r in failures[:20]:
    print(f"{n:3}  {mn:<14} {tn:6}  {tm:<18} {r}")

# Analyze the quotients
print("\n" + "=" * 80)
print("QUOTIENT ANALYSIS")
print("=" * 80)

print("\n### Quotients when m[n] divides m[n + m[n]]:")
for n, mn, tn, tm, q in successes:
    # Factor the quotient
    from sympy import factorint
    factors = factorint(q)
    factor_str = ' × '.join([f'{p}^{e}' if e > 1 else str(p) for p, e in sorted(factors.items())]) if q > 1 else "1"
    print(f"  m[{tn}] / m[{n}] = {q} = {factor_str}")

# Check for GCD patterns in failures
print("\n" + "=" * 80)
print("GCD ANALYSIS FOR FAILURES")
print("=" * 80)

print("\nFor failed cases, what is gcd(m[n], m[n+m[n]])?")
print("n    m[n]           m[n+m[n]]           gcd         gcd/m[n]")
print("-" * 80)
for n, mn, tn, tm, r in failures[:30]:
    g = gcd(mn, tm)
    ratio = g / mn if mn > 0 else 0
    print(f"{n:3}  {mn:<14} {tm:<18} {g:<10} {ratio:.4f}")

# Check: what fraction of m[n] divides m[n+m[n]]?
print("\n" + "=" * 80)
print("PARTIAL DIVISIBILITY ANALYSIS")
print("=" * 80)

print("\nFor each n, what is gcd(m[n], m[n+m[n]]) / m[n]?")
all_ratios = []
for n, mn, tn, tm, r in failures:
    g = gcd(mn, tm)
    ratio = g / mn if mn > 0 else 0
    all_ratios.append((n, ratio))

# Categorize by ratio
ratio_categories = {}
for n, ratio in all_ratios:
    bucket = round(ratio, 1)
    if bucket not in ratio_categories:
        ratio_categories[bucket] = []
    ratio_categories[bucket].append(n)

print("\nRatio distribution:")
for ratio, ns in sorted(ratio_categories.items()):
    print(f"  gcd/m[n] ≈ {ratio}: n = {ns[:10]}{'...' if len(ns) > 10 else ''}")

# Alternative pattern: Does m[n] divide m[k] for any k > n?
print("\n" + "=" * 80)
print("ALTERNATIVE: For which k > n does m[n] divide m[k]?")
print("=" * 80)

for n in [4, 5, 6, 9, 11, 12]:  # Key m-values
    mn = m(n)
    divisors = []
    for k in range(n + 1, 71):
        mk = m(k)
        if mk is not None and mk % mn == 0:
            divisors.append((k, mk // mn))

    print(f"\nm[{n}] = {mn} divides:")
    for k, q in divisors[:10]:
        print(f"  m[{k}] = {m(k)} = m[{n}] × {q}")

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)
