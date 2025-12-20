#!/usr/bin/env python3
"""
Investigate the prime index pattern.
281 is the 60th prime and appears in m[62].
Is there a pattern where m[n] contains p_{n-2}?

MODEL: Claude Opus 4.5
DATE: 2025-12-20
"""

import json
from math import sqrt

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def nth_prime(n):
    """Return the n-th prime number."""
    count = 0
    num = 2
    while True:
        if is_prime(num):
            count += 1
            if count == n:
                return num
        num += 1

def prime_index(p):
    """Return the index of prime p."""
    if not is_prime(p):
        return None
    count = 0
    num = 2
    while num <= p:
        if is_prime(num):
            count += 1
        if num == p:
            return count
        num += 1
    return None

# Load m-values
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']

print("=" * 80)
print("PRIME INDEX PATTERN INVESTIGATION")
print("=" * 80)
print("Model: Claude Opus 4.5")
print()

# Check if m[n] is divisible by p_{n-2}
print("### Checking if m[n] % p_{n-2} == 0 ###\n")

matches = []
for n in range(4, 71):
    m = m_seq[n-2]
    p = nth_prime(n-2)

    if m % p == 0:
        quotient = m // p
        matches.append((n, p, quotient))
        print(f"n={n}: m[{n}] = {p} × {quotient}  (p_{n-2}={p} divides m[{n}]) ✓")

print(f"\nTotal matches: {len(matches)} out of 67")

# Check what primes divide each m value for n=62, 65, 68
print("\n### Detailed check for n=62, 65, 68 ###\n")

for n in [62, 65, 68]:
    m = m_seq[n-2]
    print(f"n={n}: m = {m}")

    # Check p_{n-3}, p_{n-2}, p_{n-1}, p_{n}
    for offset in [-3, -2, -1, 0, 1, 2, 3]:
        idx = n + offset
        if idx > 0:
            p = nth_prime(idx)
            if m % p == 0:
                print(f"  p_{idx} = {p} divides m[{n}] (quotient = {m//p})")
    print()

# Look at the specific prime indices
print("### Prime indices in m[62], m[65], m[68] ###\n")

# Known factorizations
factors = {
    62: [2, 3, 281, 373, 2843, 10487, 63199],
    65: [24239, 57283, 1437830129],
    68: [5, 1153, 1861, 31743327447619]
}

for n, facs in factors.items():
    print(f"m[{n}] factors and their prime indices:")
    for f in facs:
        if f < 100000:  # Only compute for manageable primes
            idx = prime_index(f)
            if idx:
                print(f"  {f} is the {idx}-th prime (offset from n: {idx - n})")

# Check if 69th prime divides m[71]
print("\n### Prediction for m[71] ###\n")

p_69 = nth_prime(69)
print(f"If pattern holds, m[71] should be divisible by p_69 = {p_69}")

# 69th prime
p_68 = nth_prime(68)
p_70 = nth_prime(70)
p_71 = nth_prime(71)

print(f"Nearby primes: p_68={p_68}, p_69={p_69}, p_70={p_70}, p_71={p_71}")

# Check for the golden ratio pattern in factors
print("\n### Golden ratio pattern in factors ###\n")

for n, facs in factors.items():
    if len(facs) >= 2:
        print(f"m[{n}] consecutive factor ratios:")
        sorted_facs = sorted(facs)
        for i in range(len(sorted_facs)-1):
            ratio = sorted_facs[i+1] / sorted_facs[i]
            phi = 1.6180339887
            if 1.5 < ratio < 1.8:
                diff = abs(ratio - phi)
                print(f"  {sorted_facs[i+1]}/{sorted_facs[i]} = {ratio:.6f} (diff from φ: {diff:.6f})")

print("\n" + "=" * 80)
print("INVESTIGATION COMPLETE")
print("=" * 80)
