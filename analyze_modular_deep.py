#!/usr/bin/env python3
"""
Deep analysis of modular patterns - looking for connections and relationships.
"""

import json
import sqlite3
from collections import defaultdict

# Read data
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
n_range = data['n_range']

# Query k values from database
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
results = cursor.fetchall()
conn.close()

k_values = {puzzle_id: int(priv_hex, 16) for puzzle_id, priv_hex in results}

primes = [7, 17, 19, 37, 41]

print("="*80)
print("DEEP MODULAR ANALYSIS")
print("="*80)

# Analyze the recurrence k[n] = 2*k[n-1] + adj[n] modulo p
print("\n1. RECURRENCE MODULO p ANALYSIS")
print("-" * 80)
print("Analyzing: k[n] ≡ 2*k[n-1] + adj[n] (mod p)")

for p in primes:
    print(f"\np = {p}:")

    # Check if the recurrence holds mod p
    errors = 0
    for n in range(3, min(31, len(m_seq) + 2)):  # n=3 to 30
        if n in k_values and (n-1) in k_values:
            k_n = k_values[n] % p
            k_n1 = k_values[n-1] % p

            # Get adj[n] from the formula
            # adj[n] = 2^n - m[n] * k[d[n]]
            if n >= n_range[0] and n <= n_range[1]:
                m_n = m_seq[n - n_range[0]]
                d_n = d_seq[n - n_range[0]]

                adj_n = (pow(2, n, p*1000000) - m_n * k_values[d_n]) % p

                # Check recurrence
                expected = (2 * k_n1 + adj_n) % p
                if expected != k_n:
                    errors += 1

    if errors == 0:
        print(f"  ✓ Recurrence k[n] ≡ 2*k[n-1] + adj[n] (mod {p}) holds for all tested n")
    else:
        print(f"  ✗ Recurrence has {errors} errors")

# Analyze 2^n mod p behavior
print("\n2. POWERS OF 2 MODULO p")
print("-" * 80)

for p in primes:
    print(f"\np = {p}:")

    # Find the order of 2 mod p
    order_2 = None
    for order in range(1, p):
        if pow(2, order, p) == 1:
            order_2 = order
            break

    if order_2:
        print(f"  Order of 2 (mod {p}): {order_2}")
        print(f"  2^{order_2} ≡ 1 (mod {p})")

        # Show the cycle
        cycle = [pow(2, i, p) for i in range(order_2)]
        print(f"  Cycle: {cycle}")

        # Check if p-1 is divisible by order
        if (p - 1) % order_2 == 0:
            print(f"  {order_2} divides {p-1} ✓")

# Analyze relationships between k[n] mod p zeros and m[n]
print("\n3. RELATIONSHIP: k[n] ≡ 0 (mod p) and m-values")
print("-" * 80)

for p in primes[:3]:  # Focus on 7, 17, 19
    zeros = [n for n in sorted(k_values.keys()) if k_values[n] % p == 0]

    if len(zeros) > 0:
        print(f"\np = {p}:")
        print(f"  n where k[n] ≡ 0 (mod {p}): {zeros}")

        # Check m[n] for these n values
        print(f"  Corresponding m[n] values:")
        for n in zeros[:10]:  # First 10
            if n >= n_range[0] and n <= n_range[1]:
                m_n = m_seq[n - n_range[0]]
                print(f"    m[{n}] = {m_n}, m[{n}] mod {p} = {m_n % p}")

        # Check d[n] for these n values
        print(f"  Corresponding d[n] values:")
        for n in zeros[:10]:
            if n >= n_range[0] and n <= n_range[1]:
                d_n = d_seq[n - n_range[0]]
                print(f"    d[{n}] = {d_n}")

# Check for Fermat primes (primes of form 2^(2^k) + 1)
print("\n4. FERMAT PRIME ANALYSIS")
print("-" * 80)
print("\nFermat primes: 3, 5, 17, 257, 65537")
print("We have 17 in our analysis set!")

# 17 = 2^4 + 1
print("\np = 17 (Fermat prime: 2^4 + 1):")
print(f"  Special property: 17 = 2^4 + 1")

# Check if 2^16 ≡ 1 (mod 17)
print(f"  2^16 ≡ {pow(2, 16, 17)} (mod 17) - order is 16 = p-1")

# Check frequency of m[n] ≡ 0 (mod 17)
m_zeros_17 = [n + n_range[0] for n, m in enumerate(m_seq) if m % 17 == 0]
print(f"\n  m[n] ≡ 0 (mod 17) for n: {m_zeros_17}")

# Connection to k[n]
print(f"  k[n] ≡ 0 (mod 17) for n: {[n for n in sorted(k_values.keys()) if k_values[n] % 17 == 0]}")

# Analyze specific patterns in d[n] values
print("\n5. d[n] MODULAR PATTERNS")
print("-" * 80)

for p in [7, 17, 19]:
    print(f"\np = {p}:")
    d_mod_seq = [d % p for d in d_seq[:30]]
    print(f"  d[n] mod {p} (first 30): {d_mod_seq}")

    # Count distribution
    from collections import Counter
    counts = Counter(d_mod_seq)
    print(f"  Distribution:")
    for val in sorted(counts.keys()):
        print(f"    {val}: {counts[val]} times")

# Check if there's a relationship between m[n] mod 17 and n mod 17
print("\n6. POSITION vs RESIDUE ANALYSIS")
print("-" * 80)

for p in [17, 19]:
    print(f"\np = {p}:")

    # Create matrix: position mod p vs m[n] mod p
    matrix = defaultdict(list)
    for i, m in enumerate(m_seq[:p*2]):  # First 2 periods
        n = i + n_range[0]
        matrix[n % p].append(m % p)

    print(f"  n mod {p} -> m[n] mod {p} distribution:")
    for pos in sorted(matrix.keys())[:5]:  # Show first 5
        residues = matrix[pos]
        print(f"    n ≡ {pos} (mod {p}): m[n] mod {p} = {residues}")

# Analyze the relationship m[n] = (2^n - adj[n]) / k[d[n]] modulo p
print("\n7. UNIFIED FORMULA MODULO p")
print("-" * 80)
print("Formula: m[n] = (2^n - adj[n]) / k[d[n]]")

for p in [17, 19]:
    print(f"\np = {p}:")

    # Verify the formula mod p
    errors = 0
    for i in range(min(30, len(m_seq))):
        n = i + n_range[0]
        m_n = m_seq[i]
        d_n = d_seq[i]

        if n in k_values and d_n in k_values:
            # Compute adj[n] = 2^n - m[n] * k[d[n]]
            adj_n = pow(2, n) - m_n * k_values[d_n]

            # Check: m[n] * k[d[n]] ≡ 2^n - adj[n] (mod p)
            lhs = (m_n * k_values[d_n]) % p
            rhs = (pow(2, n, p) - adj_n) % p

            if lhs != rhs:
                errors += 1

    if errors == 0:
        print(f"  ✓ Formula m[n] * k[d[n]] ≡ 2^n - adj[n] (mod {p}) verified")
    else:
        print(f"  ✗ Formula has {errors} errors")

# Check for Sophie Germain primes (p where 2p+1 is also prime)
print("\n8. SOPHIE GERMAIN PRIME CHECK")
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

for p in primes:
    sg = 2 * p + 1
    if is_prime(sg):
        print(f"p = {p} is a Sophie Germain prime! (2p+1 = {sg} is prime)")
    else:
        print(f"p = {p} is NOT a Sophie Germain prime (2p+1 = {sg})")

print("\n" + "="*80)
print("Deep analysis complete!")
