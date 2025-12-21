#!/usr/bin/env python3
"""
Compute modular arithmetic properties for Bitcoin puzzle analysis.
Task 9: Modular Arithmetic Properties
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

# Convert hex to decimal for k values
k_values = {}
for puzzle_id, priv_hex in results:
    k_values[puzzle_id] = int(priv_hex, 16)

print(f"Loaded {len(k_values)} k values from database")
print(f"Loaded {len(m_seq)} m values and {len(d_seq)} d values")

# Define primes to analyze
primes = [7, 17, 19, 37, 41]

# 9.1 & 9.2: Compute k[n] mod p and find periodicity
print("\n" + "="*80)
print("TASK 9.1 & 9.2: k[n] mod p and Periodicity Analysis")
print("="*80)

k_mod_results = {}
for p in primes:
    k_mod_results[p] = {}
    k_mod_seq = []

    for n in sorted(k_values.keys()):
        k_mod = k_values[n] % p
        k_mod_results[p][n] = k_mod
        k_mod_seq.append(k_mod)

    # Find period by looking for repeating subsequences
    print(f"\nPrime p = {p}:")
    print(f"k[n] mod {p} sequence (n=1 to 70):")
    print(k_mod_seq[:30])  # First 30 values

    # Check for periodicity
    max_period = min(50, len(k_mod_seq) // 2)
    period_found = None

    for period in range(1, max_period + 1):
        is_periodic = True
        for i in range(period, len(k_mod_seq)):
            if k_mod_seq[i] != k_mod_seq[i % period]:
                is_periodic = False
                break

        if is_periodic:
            period_found = period
            break

    if period_found:
        print(f"Period found: {period_found}")
        print(f"Repeating pattern: {k_mod_seq[:period_found]}")
    else:
        # Check for eventual periodicity (after some initial terms)
        print(f"No simple period found in first {max_period} terms")

        # Look for repeating cycles within the sequence
        for start in range(1, min(20, len(k_mod_seq) // 3)):
            for period in range(1, min(30, (len(k_mod_seq) - start) // 2)):
                matches = 0
                for i in range(start, len(k_mod_seq) - period):
                    if k_mod_seq[i] == k_mod_seq[i + period]:
                        matches += 1

                if matches >= min(period * 2, 20):  # Strong evidence of periodicity
                    print(f"Possible eventual period: {period} (starting from position {start}, {matches} matches)")
                    break

# 9.3: Check k[n] ≡ 0 (mod p) patterns
print("\n" + "="*80)
print("TASK 9.3: Zero Patterns (k[n] ≡ 0 mod p)")
print("="*80)

zero_patterns = {}
for p in primes:
    zeros = [n for n in sorted(k_values.keys()) if k_values[n] % p == 0]
    zero_patterns[p] = zeros

    print(f"\np = {p}:")
    if zeros:
        print(f"  n values where k[n] ≡ 0 (mod {p}): {zeros}")
        print(f"  Count: {len(zeros)}/{len(k_values)}")

        # Check for patterns in differences
        if len(zeros) > 1:
            diffs = [zeros[i+1] - zeros[i] for i in range(len(zeros)-1)]
            print(f"  Differences: {diffs}")

            # Check if differences are constant
            if len(set(diffs)) == 1:
                print(f"  *** Constant difference: {diffs[0]} (periodic!) ***")
    else:
        print(f"  No n values where k[n] ≡ 0 (mod {p})")

# 9.4: Check m[n] mod 17 and m[n] mod 19 patterns
print("\n" + "="*80)
print("TASK 9.4: m[n] Modular Patterns")
print("="*80)

for p in [17, 19]:
    print(f"\np = {p}:")
    m_mod_seq = [m % p for m in m_seq]

    print(f"m[n] mod {p} sequence (first 30 values):")
    print(m_mod_seq[:30])

    # Count occurrences
    from collections import Counter
    counts = Counter(m_mod_seq)
    print(f"\nDistribution of m[n] mod {p}:")
    for val in sorted(counts.keys()):
        print(f"  {val}: {counts[val]} times ({100*counts[val]/len(m_mod_seq):.1f}%)")

    # Check for zeros
    zeros = [n + n_range[0] for n, m in enumerate(m_seq) if m % p == 0]
    if zeros:
        print(f"\nn values where m[n] ≡ 0 (mod {p}): {zeros}")
    else:
        print(f"\nNo n values where m[n] ≡ 0 (mod {p})")

# 9.5: Fermat's Little Theorem check
print("\n" + "="*80)
print("TASK 9.5: Fermat's Little Theorem Analysis")
print("="*80)
print("\nFermat's Little Theorem: If p is prime and gcd(a,p)=1, then a^(p-1) ≡ 1 (mod p)")

for p in primes:
    print(f"\np = {p}:")

    # Check k[n]^(p-1) mod p for non-zero k[n]
    non_zero_k = [n for n in sorted(k_values.keys()) if k_values[n] % p != 0]

    if len(non_zero_k) >= 5:
        print(f"Checking k[n]^{p-1} ≡ 1 (mod {p}) for non-zero k[n]:")

        # Check first few
        for n in non_zero_k[:5]:
            k = k_values[n]
            result = pow(k, p - 1, p)
            print(f"  k[{n}]^{p-1} ≡ {result} (mod {p}) {'✓' if result == 1 else '✗'}")

        # Verify all satisfy FLT
        all_satisfy = all(pow(k_values[n], p - 1, p) == 1 for n in non_zero_k)
        if all_satisfy:
            print(f"  *** ALL non-zero k[n] satisfy Fermat's Little Theorem for p={p} ***")

    # Check if order divides p-1
    print(f"\nOrder analysis for p = {p} (p-1 = {p-1}):")

    # Find the order of k[1] = 1 (trivial)
    # Find the order of k[2] = 3
    if 2 in k_values and k_values[2] % p != 0:
        k2 = k_values[2]
        for order in range(1, p):
            if pow(k2, order, p) == 1:
                print(f"  Order of k[2]={k2} (mod {p}): {order}")
                if (p - 1) % order == 0:
                    print(f"    {order} divides {p-1} ✓")
                break

    # Check 2^(p-1) mod p (should be 1 by FLT)
    result = pow(2, p - 1, p)
    print(f"  2^{p-1} ≡ {result} (mod {p}) {'(FLT satisfied)' if result == 1 else ''}")

# Summary statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

for p in primes:
    print(f"\np = {p}:")
    print(f"  Range of k[n] mod {p}: {set(k_mod_results[p].values())}")
    print(f"  Number of distinct residues: {len(set(k_mod_results[p].values()))}/{p}")
    print(f"  Zeros: {len(zero_patterns[p])} values")

print("\nAnalysis complete!")
