#!/usr/bin/env python3
"""
Advanced adj[n] Pattern Search
==============================
Final deep dive looking for missed patterns
"""

import json
import math
import sqlite3
from collections import defaultdict

# Load k-values
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT puzzle_id, priv_hex
    FROM keys
    WHERE puzzle_id BETWEEN 1 AND 70
    ORDER BY puzzle_id
""")
rows = cursor.fetchall()
conn.close()

k_seq = {0: 0}
for puzzle_id, priv_hex in rows:
    k_seq[puzzle_id] = int(priv_hex, 16)

# Compute adj[n]
adj = {}
for n in range(2, 71):
    if n in k_seq and (n-1) in k_seq:
        adj[n] = k_seq[n] - 2 * k_seq[n-1]

# Load m and d
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

m = {i+2: data['m_seq'][i] for i in range(len(data['m_seq']))}
d = {i+2: data['d_seq'][i] for i in range(len(data['d_seq']))}

print("=" * 80)
print("ADVANCED adj[n] PATTERN SEARCH")
print("=" * 80)
print()

# ============================================================================
# Pattern: adj[n] and Mersenne numbers
# ============================================================================

print("PATTERN: Relationship with Mersenne numbers (2^p - 1)")
print("-" * 80)

mersenne_primes = [2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127]
mersenne_nums = {p: 2**p - 1 for p in mersenne_primes}

print("Checking if adj[n] relates to Mersenne numbers:")
for n in range(2, min(32, max(adj.keys())+1)):
    if n in adj:
        for p in mersenne_primes:
            M_p = mersenne_nums[p]
            # Check if adj[n] is divisible by M_p
            if adj[n] != 0 and M_p != 0 and adj[n] % M_p == 0:
                quotient = adj[n] // M_p
                print(f"  adj[{n:2d}] = {quotient:10,d} × M_{p} = {quotient:10,d} × (2^{p}-1)")

print()

# Check adj[n] + 2^n for small n
print("Checking N[n] = 2^n - adj[n] for Mersenne form:")
for n in range(2, min(16, max(adj.keys())+1)):
    if n in adj:
        N_n = 2**n - adj[n]
        # Check if N[n] + 1 is a power of 2
        N_plus_1 = N_n + 1
        if N_plus_1 > 0 and (N_plus_1 & (N_plus_1 - 1)) == 0:
            exp = N_plus_1.bit_length() - 1
            print(f"  2^{n:2d} - adj[{n:2d}] = {N_n:10,d} = 2^{exp} - 1 (Mersenne!)")
        # Check if N[n] is divisible by Mersenne
        for p in mersenne_primes:
            M_p = mersenne_nums[p]
            if N_n % M_p == 0:
                quotient = N_n // M_p
                print(f"  N[{n:2d}] = {quotient:10,d} × M_{p}")

print()

# ============================================================================
# Pattern: adj[n] and Fermat numbers
# ============================================================================

print("PATTERN: Relationship with Fermat numbers (2^(2^k) + 1)")
print("-" * 80)

fermat_nums = {k: 2**(2**k) + 1 for k in range(0, 8)}
print("Fermat numbers:", {k: fermat_nums[k] for k in range(0, 6)})
print()

print("Checking if adj[n] relates to Fermat numbers:")
for n in range(2, min(32, max(adj.keys())+1)):
    if n in adj:
        for k in range(0, 6):
            F_k = fermat_nums[k]
            if F_k > 2**20:  # Skip huge Fermat numbers
                continue
            if adj[n] != 0 and adj[n] % F_k == 0:
                quotient = adj[n] // F_k
                print(f"  adj[{n:2d}] = {quotient:10,d} × F_{k} = {quotient:10,d} × (2^{2**k}+1)")

print()

# ============================================================================
# Pattern: adj[n] mod (n)
# ============================================================================

print("PATTERN: adj[n] mod n")
print("-" * 80)

print("Values of adj[n] mod n:")
for n in range(2, min(31, max(adj.keys())+1)):
    if n in adj:
        mod_val = adj[n] % n
        print(f"  adj[{n:2d}] mod {n:2d} = {mod_val:5d}")

print()

# Check if there's a pattern
print("Looking for pattern in adj[n] ≡ f(n) (mod n):")
# Common patterns: adj[n] ≡ 1, 0, -1, n/2, etc.
pattern_1 = sum(1 for n in range(2, 31) if n in adj and adj[n] % n == 1)
pattern_0 = sum(1 for n in range(2, 31) if n in adj and adj[n] % n == 0)
pattern_m1 = sum(1 for n in range(2, 31) if n in adj and adj[n] % n == n-1)

print(f"  adj[n] ≡ 1 (mod n): {pattern_1}/29 cases")
print(f"  adj[n] ≡ 0 (mod n): {pattern_0}/29 cases")
print(f"  adj[n] ≡ -1 (mod n): {pattern_m1}/29 cases")
print()

# ============================================================================
# Pattern: Relationship with n itself
# ============================================================================

print("PATTERN: Direct arithmetic relationships with n")
print("-" * 80)

print("Testing adj[n] = f(n) for various functions:")
print()

for n in range(2, min(16, max(adj.keys())+1)):
    if n in adj:
        formulas = []

        # Test simple polynomial forms
        # adj[n] = a*n + b
        if abs(adj[n]) < 100:
            for a in range(-20, 21):
                for b in range(-20, 21):
                    if a*n + b == adj[n]:
                        formulas.append(f"{a}n + {b}")
                        break
                if formulas:
                    break

        # Test adj[n] = 2^k ± n
        for k in range(0, 15):
            if 2**k - n == adj[n]:
                formulas.append(f"2^{k} - {n}")
            if 2**k + n == adj[n]:
                formulas.append(f"2^{k} + {n}")

        if formulas:
            print(f"  adj[{n:2d}] = {adj[n]:8d} = {formulas[0]}")
        else:
            print(f"  adj[{n:2d}] = {adj[n]:8d} (no simple formula found)")

print()

# ============================================================================
# Pattern: adj[n] and totient function
# ============================================================================

print("PATTERN: Relationship with Euler's totient φ(n)")
print("-" * 80)

def euler_totient(n):
    """Compute Euler's totient function φ(n)"""
    result = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result

print("Testing if adj[n] relates to φ(2^n - 1) or φ(2^n + 1):")
for n in range(2, min(16, max(adj.keys())+1)):
    if n in adj:
        phi_2n_minus_1 = euler_totient(2**n - 1)
        phi_2n_plus_1 = euler_totient(2**n + 1)

        if abs(adj[n]) == phi_2n_minus_1:
            print(f"  |adj[{n:2d}]| = φ(2^{n}-1) = {phi_2n_minus_1}")
        if abs(adj[n]) == phi_2n_plus_1:
            print(f"  |adj[{n:2d}]| = φ(2^{n}+1) = {phi_2n_plus_1}")

print()

# ============================================================================
# Pattern: Bit patterns in adj[n]
# ============================================================================

print("PATTERN: Bit structure of adj[n]")
print("-" * 80)

print("Hamming weight (number of 1-bits) in |adj[n]|:")
for n in range(2, min(21, max(adj.keys())+1)):
    if n in adj:
        abs_adj = abs(adj[n])
        hamming = bin(abs_adj).count('1')
        total_bits = abs_adj.bit_length()
        density = hamming / total_bits if total_bits > 0 else 0

        print(f"  |adj[{n:2d}]| = {abs_adj:15,d} : {hamming:3d} ones in {total_bits:3d} bits ({density:5.2f})")

print()

# ============================================================================
# Pattern: adj[n] and prime gaps
# ============================================================================

print("PATTERN: Relationship with prime gaps")
print("-" * 80)

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

print("Checking if |adj[n]| relates to prime gaps:")
for n in range(2, min(16, max(adj.keys())+1)):
    if n in adj:
        abs_adj = abs(adj[n])

        # Is adj[n] itself prime?
        if is_prime(abs_adj):
            print(f"  |adj[{n:2d}]| = {abs_adj:10,d} is PRIME")

        # Is adj[n] a prime gap?
        # (difference between consecutive primes)

print()

# ============================================================================
# Pattern: Cross-correlation with k, m, d sequences
# ============================================================================

print("PATTERN: Cross-correlation analysis")
print("-" * 80)

print("Testing if adj[n] = f(k[n], m[n], d[n]):")
print()

# We already know: adj[n] = k[n] - 2*k[n-1]
# And: adj[n] = 2^n - m[n]*k[d[n]]

# Test other combinations
for n in range(2, min(16, max(adj.keys())+1)):
    if n in adj and n in m and n in d and d[n] in k_seq:
        formulas = []

        # adj[n] = m[n] ± offset
        offset_m = adj[n] - m[n]
        if abs(offset_m) < 100:
            formulas.append(f"m[{n}] + {offset_m}")

        # adj[n] = d[n] × something
        if adj[n] % d[n] == 0:
            quotient = adj[n] // d[n]
            if abs(quotient) < 1000:
                formulas.append(f"{d[n]} × {quotient}")

        # adj[n] = k[d[n]] × something
        if adj[n] % k_seq[d[n]] == 0:
            quotient = adj[n] // k_seq[d[n]]
            if abs(quotient) < 1000:
                formulas.append(f"k[{d[n]}] × {quotient}")

        if len(formulas) > 1:
            print(f"  adj[{n:2d}] = {adj[n]:8d} = {', '.join(formulas[:3])}")

print()

# ============================================================================
# Pattern: Look for "magic" n values where adj[n] is special
# ============================================================================

print("PATTERN: Special n values where adj[n] exhibits interesting properties")
print("-" * 80)

print("Cases where adj[n] is particularly simple:")
print()

for n in range(2, min(71, max(adj.keys())+1)):
    if n in adj:
        abs_adj = abs(adj[n])

        # Small absolute value
        if abs_adj < 500:
            # Check if it's a prime
            prime_status = "PRIME" if is_prime(abs_adj) else ""
            # Check if it's a power of 2
            power_of_2 = ""
            if abs_adj > 0 and (abs_adj & (abs_adj - 1)) == 0:
                exp = abs_adj.bit_length() - 1
                power_of_2 = f"= 2^{exp}"

            if prime_status or power_of_2:
                print(f"  n={n:2d}: adj[{n}] = {adj[n]:8,d}  {prime_status} {power_of_2}")

print()

# ============================================================================
# Summary statistics
# ============================================================================

print("SUMMARY STATISTICS")
print("-" * 80)

print(f"Total adj values analyzed: {len(adj)}")
print(f"Positive: {sum(1 for v in adj.values() if v > 0)}")
print(f"Negative: {sum(1 for v in adj.values() if v < 0)}")
print(f"Zero: {sum(1 for v in adj.values() if v == 0)}")
print()

print(f"Minimum: adj[{min(adj.items(), key=lambda x: x[1])[0]}] = {min(adj.values()):,}")
print(f"Maximum: adj[{max(adj.items(), key=lambda x: x[1])[0]}] = {max(adj.values()):,}")
print()

# Count primes
prime_count = sum(1 for v in adj.values() if v > 0 and is_prime(v))
print(f"Prime adj[n] values: {prime_count}/{len(adj)}")
print()

print("=" * 80)
print("ADVANCED PATTERN SEARCH COMPLETE")
print("=" * 80)
