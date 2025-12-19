#!/usr/bin/env python3
"""Analyze prime index offsets to find the pattern."""

import json
import subprocess
from sympy import isprime, prime, primepi

# Load m-sequence from source of truth
with open('/home/solo/LA/data_for_csolver.json') as f:
    data = json.load(f)

# Lists are 0-indexed starting at n=2
m_list = data['m_seq']
d_list = data['d_seq']
m_seq = {n: m_list[n-2] for n in range(2, 2 + len(m_list))}
d_seq = {n: d_list[n-2] for n in range(2, 2 + len(d_list))}

def get_prime_index(p):
    """Get the index of prime p (1-indexed: 2=p[1], 3=p[2], 5=p[3]...)"""
    if p < 2:
        return None
    if not isprime(p):
        return None
    if p > 10**9:  # Too large
        return f"pi({p})"
    return primepi(p)

def factor_with_gnu(n):
    """Use GNU factor for fast factorization."""
    if n <= 1:
        return {}
    result = subprocess.run(['factor', str(n)], capture_output=True, text=True)
    output = result.stdout.strip()
    if ':' not in output:
        return {}
    parts = output.split(':')[1].strip().split()
    factors = {}
    for p in parts:
        p_int = int(p)
        factors[p_int] = factors.get(p_int, 0) + 1
    return factors

print("="*80)
print("PRIME INDEX OFFSET ANALYSIS")
print("="*80)
print()

# Focus on cases where m[n] = p[7] × p[j] for some j
# p[7] = 17
P7 = 17

results = []

for n in range(2, 71):
    m = m_seq.get(n)
    d = d_seq.get(n)
    if m is None or d is None:
        continue

    factors = factor_with_gnu(m)

    # Check if p[7]=17 is a factor
    if P7 in factors and len(factors) == 2:  # Exactly 2 distinct primes
        primes = sorted(factors.keys())
        if primes[0] == P7:
            other_prime = primes[1]
            other_exp = factors[other_prime]
            if other_exp == 1:  # Simple case: 17 × p
                idx = get_prime_index(other_prime)
                if isinstance(idx, int):
                    offset = idx - n
                    results.append({
                        'n': n,
                        'm': m,
                        'd': d,
                        'factorization': f"17 × {other_prime}",
                        'prime_indices': f"p[7] × p[{idx}]",
                        'second_idx': idx,
                        'offset': offset
                    })

print("Cases where m[n] = p[7] × p[j]:")
print("-"*80)
print(f"{'n':>4} | {'m[n]':>10} | {'d[n]':>4} | {'Factorization':>16} | {'Indices':>16} | {'offset':>6}")
print("-"*80)

for r in results:
    print(f"{r['n']:>4} | {r['m']:>10} | {r['d']:>4} | {r['factorization']:>16} | {r['prime_indices']:>16} | {r['offset']:>6}")

print()
print("="*80)
print("OFFSET PATTERN ANALYSIS")
print("="*80)
print()

for r in results:
    n = r['n']
    offset = r['offset']
    d = r['d']

    print(f"n={n}: offset needed = {offset}")

    # Check which m[x] equals the offset
    matches = [x for x in range(2, n) if m_seq.get(x) == offset]
    if matches:
        print(f"  → offset {offset} = m[{matches}]")
        for match in matches:
            diff = n - match
            print(f"     m[{match}] where {match} = n - {diff}")
            # Check if diff relates to d or other known values
            if d_seq.get(n) == match:
                print(f"     NOTE: {match} = d[{n}]!")
            if d_seq.get(n) == diff:
                print(f"     NOTE: diff {diff} = d[{n}]!")
    else:
        print(f"  → No m[x] equals {offset}")
    print()

print("="*80)
print("LOOKING FOR d[n] RELATIONSHIP")
print("="*80)
print()

for r in results:
    n = r['n']
    offset = r['offset']
    d = r['d']

    # Try formula: offset = m[n - d[n]]
    lookup_n = n - d
    if lookup_n in m_seq:
        m_at_lookup = m_seq[lookup_n]
        print(f"n={n}: d={d}, m[n-d]=m[{lookup_n}]={m_at_lookup}, actual offset={offset}, match={m_at_lookup==offset}")

    # Try formula: offset = m[d[n]]
    if d in m_seq:
        m_at_d = m_seq[d]
        print(f"n={n}: d={d}, m[d]=m[{d}]={m_at_d}, actual offset={offset}, match={m_at_d==offset}")

print()
print("="*80)
print("ALL m VALUES FOR REFERENCE")
print("="*80)
for n in range(2, 25):
    print(f"m[{n}] = {m_seq.get(n)}, d[{n}] = {d_seq.get(n)}")
