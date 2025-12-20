#!/usr/bin/env python3
"""
Factor m-values for n=36-70 with timeout handling for large numbers
"""

import json
import signal
from sympy import factorint, prime, primepi, isprime, primefactors

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

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError()

def factor_with_timeout(n, timeout_sec=10):
    """Factor n with a timeout"""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_sec)
    try:
        result = factorint(n)
        signal.alarm(0)
        return result
    except TimeoutError:
        return None
    finally:
        signal.alarm(0)

# Analyze n=36-70
print("=" * 80)
print("M-SEQUENCE FACTORIZATION (n=36-70)")
print("=" * 80)

results = []

for n in range(36, 71):
    m_val = m(n)
    bits = m_val.bit_length()

    print(f"\nm[{n}] = {m_val}")
    print(f"  Bits: {bits}")

    if bits > 60:  # Very large, try quick primality check first
        if isprime(m_val):
            prime_idx = primepi(m_val) if bits < 45 else "large"
            print(f"  *** PRIME (index ~{prime_idx}) ***")
            results.append({
                'n': n, 'm': m_val, 'factors': {m_val: 1},
                'is_prime': True, 'factored': True
            })
        else:
            # Try to find small factors quickly
            small_factors = {}
            temp = m_val
            for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
                while temp % p == 0:
                    small_factors[p] = small_factors.get(p, 0) + 1
                    temp //= p

            if temp == 1:
                print(f"  Factors: {small_factors}")
                results.append({
                    'n': n, 'm': m_val, 'factors': small_factors,
                    'is_prime': False, 'factored': True
                })
            elif temp != m_val:
                print(f"  Partial factors: {small_factors}, remaining: {temp} ({temp.bit_length()} bits)")
                results.append({
                    'n': n, 'm': m_val, 'factors': small_factors,
                    'remaining': temp, 'is_prime': False, 'factored': False
                })
            else:
                print(f"  Too large to factor quickly (no small factors)")
                results.append({
                    'n': n, 'm': m_val, 'factors': None,
                    'is_prime': False, 'factored': False
                })
    else:
        # Try with timeout
        factors = factor_with_timeout(m_val, timeout_sec=30)

        if factors:
            factor_str = " × ".join([f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items())])
            print(f"  Factors: {factor_str}")

            # Get prime indices
            for p in sorted(factors.keys()):
                idx = primepi(p)
                print(f"    p[{idx}] = {p}")

            results.append({
                'n': n, 'm': m_val, 'factors': factors,
                'is_prime': len(factors) == 1 and list(factors.values())[0] == 1,
                'factored': True
            })
        else:
            print(f"  Timeout during factorization")
            results.append({
                'n': n, 'm': m_val, 'factors': None,
                'is_prime': False, 'factored': False
            })

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

factored = [r for r in results if r['factored']]
primes = [r for r in results if r.get('is_prime', False)]

print(f"Successfully factored: {len(factored)}/{len(results)}")
print(f"Prime m-values: {len(primes)}")

if primes:
    print("\nPrime m-values:")
    for r in primes:
        print(f"  m[{r['n']}] is prime")

# Look for patterns in successfully factored values
print("\n" + "=" * 80)
print("PATTERN ANALYSIS")
print("=" * 80)

for r in factored:
    if r['factors'] is None:
        continue

    n = r['n']
    factors = r['factors']

    # Get factor indices
    factor_indices = {}
    for p in factors.keys():
        try:
            idx = primepi(p)
            factor_indices[p] = idx
        except:
            factor_indices[p] = "large"

    print(f"\nm[{n}] factor indices: {list(factor_indices.values())}")

    # Look for n-relationships
    for p, idx in factor_indices.items():
        if isinstance(idx, int):
            # Check various relationships
            if idx == n:
                print(f"  p[{idx}] = p[n]")
            if idx == n - m(5):  # m[5] = 9
                print(f"  p[{idx}] = p[n - m[5]] = p[n - 9]")
            if idx == n - m(6):  # m[6] = 19
                print(f"  p[{idx}] = p[n - m[6]] = p[n - 19]")
            if idx == n + m(5):
                print(f"  p[{idx}] = p[n + m[5]] = p[n + 9]")
            if idx == n + m(6):
                print(f"  p[{idx}] = p[n + m[6]] = p[n + 19]")
            if idx == n + m(7):  # m[7] = 50
                print(f"  p[{idx}] = p[n + m[7]] = p[n + 50]")
            if idx == n + m(8):  # m[8] = 23
                print(f"  p[{idx}] = p[n + m[8]] = p[n + 23]")
            if idx == 2*n:
                print(f"  p[{idx}] = p[2n]")
            if idx == 2*n + 1:
                print(f"  p[{idx}] = p[2n + 1]")

# Save results
with open('factorization_36_70.json', 'w') as f:
    # Convert for JSON serialization
    json_results = []
    for r in results:
        r_copy = {k: v for k, v in r.items()}
        if r_copy['factors']:
            r_copy['factors'] = {str(k): v for k, v in r['factors'].items()}
        if 'remaining' in r_copy:
            r_copy['remaining'] = str(r_copy['remaining'])
        r_copy['m'] = str(r_copy['m'])
        json_results.append(r_copy)
    json.dump(json_results, f, indent=2)

print("\n\nResults saved to factorization_36_70.json")
