#!/usr/bin/env python3
"""
Compute prime indices and other numerical properties for mystery m-values.
"""

import math

def sieve_primes(limit):
    """Generate primes up to limit using Sieve of Eratosthenes."""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(limit + 1) if is_prime[i]]

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def prime_index(p, primes):
    """Find 1-based index of prime p."""
    if p in primes:
        return primes.index(p) + 1
    return None

def factorize(n):
    if n < 2:
        return []
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    return factors

# Generate primes up to 1 million
print("Generating primes...")
primes = sieve_primes(1000000)
print(f"Generated {len(primes)} primes up to 1,000,000")

# Target m-values
targets = {
    15: 26989,
    17: 138269,
    18: 255121,
    20: 900329
}

print("\n" + "="*70)
print("PRIME INDEX ANALYSIS")
print("="*70)

for n, m in sorted(targets.items()):
    print(f"\nm[{n}] = {m}")
    print("-" * 40)

    # Check if prime
    if is_prime(m):
        idx = prime_index(m, primes)
        print(f"  PRIME! Index = {idx} (the {idx}th prime)")

        # Check relationships with n
        print(f"  Index / n = {idx / n:.4f}")
        print(f"  Index - n = {idx - n}")
        print(f"  Index mod n = {idx % n}")
        print(f"  n * something = {idx}? -> {idx / n}")
    else:
        factors = factorize(m)
        print(f"  Factors: {factors}")

        # Get prime indices of factors
        for f in set(factors):
            if is_prime(f):
                idx = prime_index(f, primes)
                count = factors.count(f)
                exp = f"^{count}" if count > 1 else ""
                print(f"    {f}{exp} is the {idx}th prime")

# Additional analysis
print("\n" + "="*70)
print("PRIME INDEX PATTERNS")
print("="*70)

# For m[15] = 137 × 197
print("\nm[15] = 137 × 197:")
idx_137 = prime_index(137, primes)
idx_197 = prime_index(197, primes)
print(f"  137 is the {idx_137}th prime")
print(f"  197 is the {idx_197}th prime")
print(f"  Sum of indices: {idx_137 + idx_197}")
print(f"  Diff of indices: {idx_197 - idx_137}")
print(f"  Product of indices: {idx_137 * idx_197}")
print(f"  idx_137 + idx_197 - 15 = {idx_137 + idx_197 - 15}")

# For m[17] = 37² × 101
print("\nm[17] = 37² × 101:")
idx_37 = prime_index(37, primes)
idx_101 = prime_index(101, primes)
print(f"  37 is the {idx_37}th prime")
print(f"  101 is the {idx_101}th prime")
print(f"  2 × idx_37 + idx_101 = {2 * idx_37 + idx_101}")
print(f"  idx_37 × idx_101 = {idx_37 * idx_101}")

# Check if 255121 and 900329 prime indices have pattern
print("\n" + "="*70)
print("CHECKING PRIME INDICES OF m[18] AND m[20]")
print("="*70)

if is_prime(255121):
    idx_255121 = prime_index(255121, primes)
    print(f"m[18] = 255121 is the {idx_255121}th prime")
    print(f"  {idx_255121} / 18 = {idx_255121 / 18:.4f}")
    print(f"  {idx_255121} - 18 = {idx_255121 - 18}")

if is_prime(900329):
    idx_900329 = prime_index(900329, primes)
    print(f"m[20] = 900329 is the {idx_900329}th prime")
    print(f"  {idx_900329} / 20 = {idx_900329 / 20:.4f}")
    print(f"  {idx_900329} - 20 = {idx_900329 - 20}")

# Look for patterns
print("\n" + "="*70)
print("LOOKING FOR INDEX PATTERNS")
print("="*70)

# Check if indices follow any formula
indices = []
for n, m in sorted(targets.items()):
    if is_prime(m):
        idx = prime_index(m, primes)
        indices.append((n, idx))
        print(f"n={n}: prime_index(m[n]) = {idx}")

# Bitwise analysis
print("\n" + "="*70)
print("BITWISE ANALYSIS")
print("="*70)

for n, m in sorted(targets.items()):
    binary = bin(m)[2:]
    hex_val = hex(m)
    ones = binary.count('1')
    print(f"\nm[{n}] = {m}")
    print(f"  Binary: {binary} ({len(binary)} bits)")
    print(f"  Hex: {hex_val}")
    print(f"  Popcount (1s): {ones}")
    print(f"  n - popcount: {n - ones}")

# XOR patterns
print("\n" + "="*70)
print("XOR PATTERNS")
print("="*70)

m_vals = [26989, 138269, 255121, 900329]
for i in range(len(m_vals)):
    for j in range(i+1, len(m_vals)):
        xor = m_vals[i] ^ m_vals[j]
        print(f"m[{[15,17,18,20][i]}] XOR m[{[15,17,18,20][j]}] = {xor} = {bin(xor)}")
