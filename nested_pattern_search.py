#!/usr/bin/env python3
"""
Nested Pattern Search for Remaining Factors
============================================

After extracting simple p[n ± m[k]] patterns, search for nested patterns
in the remaining factors.

Hypothesis: Remaining factors are p[f(n, m[a], m[b], ...)] where f is a
combination of m-values.
"""

import json
from math import sqrt, gcd
from functools import lru_cache
from itertools import combinations, permutations

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
m = {n: m_seq[n-2] for n in range(2, 2 + len(m_seq))}
d = {n: d_seq[n-2] for n in range(2, 2 + len(d_seq))}

# Prime generation (larger set for nested patterns)
@lru_cache(maxsize=1000000)
def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(sqrt(n)) + 1, 2):
        if n % i == 0: return False
    return True

print("Generating primes...")
primes = []
candidate = 2
while len(primes) < 1000000:
    if is_prime(candidate):
        primes.append(candidate)
    candidate += 1
print(f"Generated {len(primes):,} primes up to {primes[-1]:,}")

prime_to_index = {p: i+1 for i, p in enumerate(primes)}

def p(i):
    """Return the i-th prime (1-indexed)."""
    if i < 1 or i > len(primes): return None
    return primes[i-1]

def pi(prime_val):
    """Return the index of a prime (1-indexed)."""
    return prime_to_index.get(prime_val)

def factorize(n, limit=10000):
    """Factorize n using trial division up to limit primes."""
    factors = []
    for prime in primes[:limit]:
        if prime * prime > n:
            break
        exp = 0
        while n % prime == 0:
            n //= prime
            exp += 1
        if exp > 0:
            factors.append((prime, exp))
    if n > 1:
        factors.append((n, 1))  # Remaining factor (may be prime or too large)
    return factors

# ============================================================================
# Generate candidate index expressions
# ============================================================================

def generate_index_expressions(n, max_depth=2):
    """
    Generate candidate index expressions of the form:
    - n ± c (constant offset)
    - n ± m[k]
    - n ± m[a] ± m[b]
    - a*n + b (linear)
    - m[a] * c
    - m[a] ± m[b]
    """
    expressions = []

    # n ± constant (larger range)
    for c in range(-200, 201):
        if n + c >= 1:
            expressions.append((n + c, f"n{'+' if c >= 0 else ''}{c}"))

    # n ± m[k]
    for k in range(2, 9):
        mk = m[k]
        if n + mk >= 1:
            expressions.append((n + mk, f"n+m[{k}]"))
        if n - mk >= 1:
            expressions.append((n - mk, f"n-m[{k}]"))

    # n ± m[a] ± m[b]
    for a in range(2, 9):
        for b in range(a, 9):
            ma, mb = m[a], m[b]
            exprs = [
                (n + ma + mb, f"n+m[{a}]+m[{b}]"),
                (n + ma - mb, f"n+m[{a}]-m[{b}]"),
                (n - ma + mb, f"n-m[{a}]+m[{b}]"),
                (n - ma - mb, f"n-m[{a}]-m[{b}]"),
            ]
            for val, desc in exprs:
                if val >= 1:
                    expressions.append((val, desc))

    # a*n + b (linear)
    for a in [2, 3, 4, 5]:
        for b in range(-50, 51):
            if a * n + b >= 1:
                expressions.append((a * n + b, f"{a}n{'+' if b >= 0 else ''}{b}"))

    # m[k] direct
    for k in range(2, 9):
        expressions.append((m[k], f"m[{k}]"))

    # c * m[k]
    for k in range(2, 9):
        mk = m[k]
        for c in range(2, 20):
            expressions.append((c * mk, f"{c}*m[{k}]"))

    # m[a] ± m[b]
    for a in range(2, 9):
        for b in range(a, 9):
            if a != b:
                ma, mb = m[a], m[b]
                expressions.append((ma + mb, f"m[{a}]+m[{b}]"))
                if ma - mb >= 1:
                    expressions.append((ma - mb, f"m[{a}]-m[{b}]"))
                if mb - ma >= 1:
                    expressions.append((mb - ma, f"m[{b}]-m[{a}]"))

    # n * m[k] / m[j] (if exact division)
    for k in range(2, 9):
        for j in range(2, 9):
            if k != j and m[j] != 0:
                product = n * m[k]
                if product % m[j] == 0:
                    result = product // m[j]
                    expressions.append((result, f"n*m[{k}]/m[{j}]"))

    return expressions

# ============================================================================
# Analyze each n in range 36-70
# ============================================================================

print("\n" + "=" * 80)
print("NESTED PATTERN SEARCH FOR n=36-70")
print("=" * 80)

discoveries = {}

for n in range(36, 71):
    target = m[n]
    factors = factorize(target, limit=50000)

    print(f"\n{'='*80}")
    print(f"n={n}: m[{n}] = {target:,}")
    print(f"{'='*80}")

    # Get all factor prime indices
    factor_info = []
    for (prime_val, exp) in factors:
        idx = pi(prime_val)
        if idx is not None:
            factor_info.append({
                'prime': prime_val,
                'exp': exp,
                'index': idx
            })
        else:
            factor_info.append({
                'prime': prime_val,
                'exp': exp,
                'index': f'>p[{len(primes)}]'
            })

    print(f"\nFactorization:")
    for fi in factor_info:
        idx_str = fi['index'] if isinstance(fi['index'], int) else fi['index']
        exp_str = f"^{fi['exp']}" if fi['exp'] > 1 else ""
        print(f"  {fi['prime']:,}{exp_str} = p[{idx_str}]")

    # Generate candidate expressions for this n
    expressions = generate_index_expressions(n)
    expr_dict = {val: desc for val, desc in expressions}

    # Match each factor index against expressions
    print(f"\nPattern matches:")
    pattern_matches = []

    for fi in factor_info:
        if not isinstance(fi['index'], int):
            continue

        idx = fi['index']
        if idx in expr_dict:
            pattern = expr_dict[idx]
            pattern_matches.append({
                'prime': fi['prime'],
                'index': idx,
                'pattern': pattern
            })
            print(f"  p[{idx}] = {fi['prime']:,} → {pattern}")

    # Store discoveries
    if pattern_matches:
        discoveries[n] = {
            'target': target,
            'factorization': [(f['prime'], f['exp'], f['index']) for f in factor_info],
            'pattern_matches': pattern_matches
        }

# ============================================================================
# Summary and Analysis
# ============================================================================

print("\n\n" + "=" * 80)
print("SUMMARY: ALL DISCOVERED PATTERNS")
print("=" * 80)

# Count pattern types
pattern_counts = {}
for n, data in discoveries.items():
    for pm in data['pattern_matches']:
        pattern = pm['pattern']
        # Normalize pattern for counting
        base_pattern = pattern.split('+')[0].split('-')[0].strip()
        if base_pattern.startswith(('2n', '3n', '4n', '5n')):
            base_pattern = 'linear_an+b'
        elif base_pattern == 'n':
            if '+' in pattern or '-' in pattern:
                base_pattern = 'n_offset'

        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

print("\nMost common specific patterns:")
for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1])[:20]:
    print(f"  {pattern}: {count}")

# Look for interesting non-trivial patterns
print("\n\nINTERESTING NON-TRIVIAL PATTERNS:")
print("-" * 60)

for n, data in sorted(discoveries.items()):
    interesting = []
    for pm in data['pattern_matches']:
        pattern = pm['pattern']
        # Skip trivial n+c patterns where |c| < 20
        if pattern.startswith('n+') or pattern.startswith('n-'):
            try:
                c = int(pattern[2:])
                if abs(c) < 20:
                    continue
            except:
                pass
        # Skip m[2] and m[3] (always = 1)
        if pattern in ['m[2]', 'm[3]', 'n+0']:
            continue
        interesting.append(pm)

    if interesting:
        print(f"\nn={n}:")
        for pm in interesting:
            print(f"  p[{pm['index']}] = {pm['prime']:,} → {pm['pattern']}")

# Save results
with open('NESTED_PATTERN_RESULTS.json', 'w') as f:
    json.dump({
        'discoveries': {str(k): v for k, v in discoveries.items()},
        'pattern_counts': pattern_counts
    }, f, indent=2, default=str)

print("\n\nResults saved to NESTED_PATTERN_RESULTS.json")
