#!/usr/bin/env python3
"""
Verify Discovered Formulas Against m-sequence
==============================================

This script verifies that the patterns found in FORMULAS_36_70_DISCOVERED.md
correctly match the actual m-sequence values.

Key patterns to verify:
- p[n - m[7]] (n-50) at n=51, 55, 58
- p[n - m[8]] (n-23) at n=43, 70
- p[n + m[5]] (n+9) at n=61
- p[m[7]] = p[50] at n=55
"""

import json
from math import sqrt
from functools import lru_cache

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
m = {n: m_seq[n-2] for n in range(2, 2 + len(m_seq))}
d = {n: d_seq[n-2] for n in range(2, 2 + len(d_seq))}

# Prime generation
@lru_cache(maxsize=500000)
def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(sqrt(n)) + 1, 2):
        if n % i == 0: return False
    return True

primes = []
candidate = 2
while len(primes) < 500000:
    if is_prime(candidate):
        primes.append(candidate)
    candidate += 1

prime_to_index = {p: i+1 for i, p in enumerate(primes)}

def p(i):
    """Return the i-th prime (1-indexed)."""
    if i < 1 or i > len(primes): return None
    return primes[i-1]

def pi(prime_val):
    """Return the index of a prime (1-indexed)."""
    return prime_to_index.get(prime_val)

print("=" * 80)
print("VERIFICATION OF DISCOVERED FORMULAS")
print("=" * 80)

# Building blocks
print("\n## Building Blocks (m-values used in formulas)")
print("-" * 40)
for k in range(2, 9):
    print(f"m[{k}] = {m[k]}")

print("\n## Key Primes from Building Blocks")
print("-" * 40)
print(f"p[m[5]] = p[{m[5]}] = {p(m[5])}")  # p[9] = 23
print(f"p[m[6]] = p[{m[6]}] = {p(m[6])}")  # p[19] = 67
print(f"p[m[7]] = p[{m[7]}] = {p(m[7])}")  # p[50] = 229
print(f"p[m[8]] = p[{m[8]}] = {p(m[8])}")  # p[23] = 83

# Verify specific discovered patterns
print("\n" + "=" * 80)
print("VERIFICATION: p[n - m[7]] Pattern (n-50)")
print("=" * 80)

for n in [51, 55, 58]:
    idx = n - m[7]  # n - 50
    prime_val = p(idx)
    target = m[n]
    if target % prime_val == 0:
        quotient = target // prime_val
        print(f"n={n}: m[{n}] = {target:,}")
        print(f"       p[n - m[7]] = p[{idx}] = {prime_val}")
        print(f"       m[{n}] / {prime_val} = {quotient:,}")
        print(f"       ✓ VERIFIED: {prime_val} divides m[{n}]")
    else:
        print(f"n={n}: ✗ FAILED - p[{idx}] = {prime_val} does NOT divide m[{n}]")
    print()

print("=" * 80)
print("VERIFICATION: p[n - m[8]] Pattern (n-23)")
print("=" * 80)

for n in [43, 70]:
    idx = n - m[8]  # n - 23
    prime_val = p(idx)
    target = m[n]
    if target % prime_val == 0:
        quotient = target // prime_val
        print(f"n={n}: m[{n}] = {target:,}")
        print(f"       p[n - m[8]] = p[{idx}] = {prime_val}")
        print(f"       m[{n}] / {prime_val} = {quotient:,}")
        print(f"       ✓ VERIFIED: {prime_val} divides m[{n}]")
    else:
        print(f"n={n}: ✗ FAILED - p[{idx}] = {prime_val} does NOT divide m[{n}]")
    print()

print("=" * 80)
print("VERIFICATION: p[n + m[5]] Pattern (n+9)")
print("=" * 80)

for n in [61]:
    idx = n + m[5]  # n + 9
    prime_val = p(idx)
    target = m[n]
    if target % prime_val == 0:
        quotient = target // prime_val
        print(f"n={n}: m[{n}] = {target:,}")
        print(f"       p[n + m[5]] = p[{idx}] = {prime_val}")
        print(f"       m[{n}] / {prime_val} = {quotient:,}")
        print(f"       ✓ VERIFIED: {prime_val} divides m[{n}]")
    else:
        print(f"n={n}: ✗ FAILED - p[{idx}] = {prime_val} does NOT divide m[{n}]")
    print()

print("=" * 80)
print("VERIFICATION: p[m[7]] = p[50] Direct Reference")
print("=" * 80)

for n in [55]:
    idx = m[7]  # 50
    prime_val = p(idx)
    target = m[n]
    if target % prime_val == 0:
        quotient = target // prime_val
        print(f"n={n}: m[{n}] = {target:,}")
        print(f"       p[m[7]] = p[{idx}] = {prime_val}")
        print(f"       m[{n}] / {prime_val} = {quotient:,}")
        print(f"       ✓ VERIFIED: {prime_val} divides m[{n}]")
    else:
        print(f"n={n}: ✗ FAILED - p[{idx}] = {prime_val} does NOT divide m[{n}]")
    print()

# Now verify the complete formula for n=55 (double pattern)
print("=" * 80)
print("COMPLETE FORMULA VERIFICATION: n=55")
print("=" * 80)

n = 55
target = m[n]
print(f"m[{n}] = {target:,}")

# Pattern found: m[55] = p[1] × p[n - m[7]] × p[m[7]] × p[1523] × p[large]
# = 2 × 11 × 229 × 12763 × large
factors_found = []

# p[1] = 2
if target % 2 == 0:
    factors_found.append((2, 'p[1]'))
    target //= 2

# p[n - m[7]] = p[5] = 11
prime_val = p(n - m[7])
if target % prime_val == 0:
    factors_found.append((prime_val, f'p[n - m[7]] = p[{n - m[7]}]'))
    target //= prime_val

# p[m[7]] = p[50] = 229
prime_val = p(m[7])
if target % prime_val == 0:
    factors_found.append((prime_val, f'p[m[7]] = p[{m[7]}]'))
    target //= prime_val

print("\nFactors extracted:")
for prime_val, pattern in factors_found:
    print(f"  {prime_val} = {pattern}")

print(f"\nRemaining after extraction: {target:,}")

# Check if remaining is prime
if is_prime(target):
    idx = pi(target)
    print(f"Remaining is prime: p[{idx}] = {target}")
else:
    print("Remaining is composite, factoring...")
    # Simple trial division
    remaining = target
    while remaining > 1:
        for prime in primes:
            if remaining % prime == 0:
                idx = pi(prime)
                exp = 0
                while remaining % prime == 0:
                    remaining //= prime
                    exp += 1
                exp_str = f"^{exp}" if exp > 1 else ""
                print(f"  {prime}{exp_str} = p[{idx}]")
                break
        if remaining > 1 and prime > sqrt(remaining):
            if is_prime(remaining):
                idx = pi(remaining)
                print(f"  {remaining} = p[{idx}]")
            else:
                print(f"  {remaining} (large composite)")
            break

# Search for more n - m[k] patterns
print("\n" + "=" * 80)
print("SCANNING ALL n=36-70 FOR p[n - m[k]] PATTERNS")
print("=" * 80)

pattern_hits = {}

for n in range(36, 71):
    target = m[n]
    patterns = []

    # Check n - m[k] for k = 2..8
    for k in range(2, 9):
        idx = n - m[k]
        if idx >= 1:
            prime_val = p(idx)
            if prime_val and target % prime_val == 0:
                patterns.append(f"p[n-m[{k}]] = p[{idx}] = {prime_val}")

    # Check n + m[k] for k = 2..8
    for k in range(2, 9):
        idx = n + m[k]
        prime_val = p(idx)
        if prime_val and target % prime_val == 0:
            patterns.append(f"p[n+m[{k}]] = p[{idx}] = {prime_val}")

    # Check p[m[k]] direct
    for k in range(2, 9):
        idx = m[k]
        prime_val = p(idx)
        if prime_val and target % prime_val == 0:
            patterns.append(f"p[m[{k}]] = p[{idx}] = {prime_val}")

    if patterns:
        print(f"\nn={n}: m[{n}] = {target:,}")
        for patt in patterns:
            print(f"    {patt}")
        pattern_hits[n] = patterns

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total positions with p[n ± m[k]] or p[m[k]] patterns: {len(pattern_hits)}")
print(f"Positions: {sorted(pattern_hits.keys())}")

# Count pattern types
pattern_type_counts = {}
for n, patterns in pattern_hits.items():
    for patt in patterns:
        ptype = patt.split('=')[0].strip()
        pattern_type_counts[ptype] = pattern_type_counts.get(ptype, 0) + 1

print("\nPattern type frequency:")
for ptype, count in sorted(pattern_type_counts.items(), key=lambda x: -x[1]):
    print(f"  {ptype}: {count}")

# Save results
results = {
    'verified_patterns': {
        'p[n-m[7]]': [51, 55, 58],
        'p[n-m[8]]': [43, 70],
        'p[n+m[5]]': [61],
        'p[m[7]]': [55],
    },
    'all_pattern_hits': {str(k): v for k, v in pattern_hits.items()},
    'pattern_type_counts': pattern_type_counts
}

with open('FORMULA_VERIFICATION_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to FORMULA_VERIFICATION_RESULTS.json")
