#!/usr/bin/env python3
"""
Factor m-values for n=36-70 and look for prime patterns
"""

import json
from sympy import factorint, prime, primepi, isprime

# Load data
with open('data_for_csolver.json') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

# m[n] = m_seq[n-2] (0-indexed)
def m(n):
    return m_seq[n - 2]

def d(n):
    return d_seq[n - 2]

# Analyze n=36-70
print("=" * 80)
print("M-SEQUENCE FACTORIZATION (n=36-70)")
print("=" * 80)

results = []

for n in range(36, 71):
    m_val = m(n)
    factors = factorint(m_val)

    # Format factors nicely
    factor_str = " × ".join([f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items())])

    # Count prime factors (with multiplicity)
    omega = sum(factors.values())  # with multiplicity
    distinct = len(factors)  # distinct primes

    # Check if m_val itself is prime
    is_m_prime = isprime(m_val)

    # Find which prime index m_val corresponds to if it's prime
    prime_idx = None
    if is_m_prime:
        prime_idx = primepi(m_val)

    # Get prime indices of factors
    factor_indices = []
    for p in sorted(factors.keys()):
        idx = primepi(p)
        factor_indices.append(f"p[{idx}]={p}")

    print(f"\nm[{n}] = {m_val}")
    print(f"  Factors: {factor_str}")
    print(f"  Prime indices: {', '.join(factor_indices)}")
    print(f"  Distinct primes: {distinct}, Omega: {omega}")
    if is_m_prime:
        print(f"  *** m[{n}] is the {prime_idx}-th prime! ***")

    results.append({
        'n': n,
        'm': m_val,
        'factors': factors,
        'factor_indices': [primepi(p) for p in sorted(factors.keys())],
        'is_prime': is_m_prime,
        'prime_index': prime_idx
    })

# Summary of prime m-values
print("\n" + "=" * 80)
print("PRIME M-VALUES (n=36-70)")
print("=" * 80)
prime_ms = [r for r in results if r['is_prime']]
if prime_ms:
    for r in prime_ms:
        print(f"m[{r['n']}] = prime({r['prime_index']})")
else:
    print("No prime m-values in this range")

# Look for patterns in factor indices
print("\n" + "=" * 80)
print("FACTOR INDEX PATTERNS")
print("=" * 80)

for r in results:
    n = r['n']
    indices = r['factor_indices']
    factors = r['factors']

    # Check if any factor index relates to n or earlier m-values
    relations = []

    for idx in indices:
        # Check relation to n
        if idx == n:
            relations.append(f"p[{idx}] = p[n]")
        elif idx == n - 1:
            relations.append(f"p[{idx}] = p[n-1]")
        elif idx == n + 1:
            relations.append(f"p[{idx}] = p[n+1]")
        elif idx == 2*n:
            relations.append(f"p[{idx}] = p[2n]")
        elif idx == 3*n:
            relations.append(f"p[{idx}] = p[3n]")

        # Check relation to m-values
        for k in range(2, min(n, 20)):  # Check m[2] through m[19]
            mk = m(k)
            if idx == mk:
                relations.append(f"p[{idx}] = p[m[{k}]]")
            elif idx == n + mk:
                relations.append(f"p[{idx}] = p[n+m[{k}]]")
            elif idx == n - mk:
                relations.append(f"p[{idx}] = p[n-m[{k}]]")
            elif idx == n * mk:
                relations.append(f"p[{idx}] = p[n×m[{k}]]")

    if relations:
        print(f"m[{n}]: {', '.join(relations)}")

# Save detailed results
with open('factorization_36_70.json', 'w') as f:
    # Convert dict keys to strings for JSON
    json_results = []
    for r in results:
        r_copy = r.copy()
        r_copy['factors'] = {str(k): v for k, v in r['factors'].items()}
        json_results.append(r_copy)
    json.dump(json_results, f, indent=2)

print("\n\nDetailed results saved to factorization_36_70.json")
