#!/usr/bin/env python3
"""
Find sources for unknown m-values by checking combinations of convergents.
Tests: products, sums, differences, modular operations, digit manipulations.
"""

import math
from itertools import product, combinations
from functools import lru_cache

# Known m-sequence (n=2 to 31)
M_SEQUENCE = {
    2: 3, 3: 7, 4: 22, 5: 9, 6: 19, 7: 50, 8: 23, 9: 493, 10: 19,
    11: 1921, 12: 1241, 13: 8342, 14: 2034, 15: 26989, 16: 8470,
    17: 138269, 18: 255121, 19: 564091, 20: 900329, 21: 670674,
    22: 4494340, 23: 7256672, 24: 13127702, 25: 5765582, 26: 50898620,
    27: 23103005, 28: 33504646, 29: 156325542, 30: 536813704, 31: 350549882
}

# Unknown m-values (not direct convergents)
UNKNOWN_M = {7: 50, 8: 23, 9: 493, 11: 1921, 12: 1241, 13: 8342, 14: 2034,
             15: 26989, 16: 8470, 17: 138269, 18: 255121, 19: 564091,
             20: 900329, 21: 670674}

def get_convergents(constant_name, n_terms=30):
    """Get continued fraction coefficients and compute convergents."""

    if constant_name == 'pi':
        cf = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2, 1, 84, 2, 1, 1, 15, 3, 13, 1, 4]
    elif constant_name == 'e':
        cf = [2, 1, 2]
        for k in range(1, n_terms // 3 + 1):
            cf.extend([1, 1, 2 * (k + 1)])
        cf = cf[:n_terms]
    elif constant_name == 'sqrt2':
        cf = [1] + [2] * (n_terms - 1)
    elif constant_name == 'sqrt3':
        cf = [1] + [1 if i % 2 == 0 else 2 for i in range(n_terms - 1)]
    elif constant_name == 'phi':
        cf = [1] * n_terms
    elif constant_name == 'ln2':
        cf = [0, 1, 2, 3, 1, 6, 3, 1, 1, 2, 1, 1, 1, 1, 3, 10, 1, 1, 1, 2, 1, 1, 1, 1, 3, 2, 3, 1, 13, 7]
    else:
        return [], []

    # Compute convergents
    h_prev2, h_prev1 = 0, 1
    k_prev2, k_prev1 = 1, 0
    numerators, denominators = [], []

    for a in cf[:n_terms]:
        h = a * h_prev1 + h_prev2
        k = a * k_prev1 + k_prev2
        numerators.append(h)
        denominators.append(k)
        h_prev2, h_prev1 = h_prev1, h
        k_prev2, k_prev1 = k_prev1, k

    return numerators, denominators

def build_all_convergents():
    """Build database of all convergent values."""
    constants = ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']
    all_nums = set()
    all_denoms = set()
    all_values = {}  # value -> sources

    for const in constants:
        nums, denoms = get_convergents(const, 30)
        for i, (n, d) in enumerate(zip(nums, denoms)):
            all_nums.add(n)
            all_denoms.add(d)

            if n not in all_values:
                all_values[n] = []
            all_values[n].append(f"{const}_h{i}")

            if d not in all_values:
                all_values[d] = []
            all_values[d].append(f"{const}_k{i}")

    return all_nums, all_denoms, all_values

def digit_sum(n):
    """Sum of digits."""
    return sum(int(d) for d in str(abs(n)))

def digit_product(n):
    """Product of digits."""
    result = 1
    for d in str(abs(n)):
        result *= int(d)
    return result

def check_combinations(target, all_nums, all_denoms, all_values):
    """Check if target can be formed from convergent combinations."""
    results = []

    # All convergent values combined
    all_conv = list(all_nums | all_denoms)
    all_conv = [v for v in all_conv if v > 0 and v < 100000]  # Reasonable range

    # 1. Direct match (already checked, but verify)
    if target in all_values:
        results.append(f"DIRECT: {all_values[target]}")

    # 2. Products of two convergents: a × b = target
    for a in all_conv:
        if target % a == 0:
            b = target // a
            if b in all_values and a in all_values:
                results.append(f"PRODUCT: {a} × {b} = {target} ({all_values[a][0]} × {all_values[b][0]})")

    # 3. Sums: a + b = target
    for a in all_conv:
        b = target - a
        if b > 0 and b in all_values and a in all_values:
            if a <= b:  # Avoid duplicates
                results.append(f"SUM: {a} + {b} = {target} ({all_values[a][0]} + {all_values[b][0]})")

    # 4. Differences: a - b = target or b - a = target
    for a in all_conv:
        # a - b = target => b = a - target
        b = a - target
        if b > 0 and b in all_values and a in all_values:
            results.append(f"DIFF: {a} - {b} = {target} ({all_values[a][0]} - {all_values[b][0]})")

    # 5. a × b + c = target
    for a in all_conv[:20]:  # Limit search
        for b in all_conv[:20]:
            prod = a * b
            c = target - prod
            if c in all_values and a in all_values and b in all_values:
                results.append(f"COMBO: {a}×{b} + {c} = {target}")

    # 6. Digit sum of convergent = target
    for v, sources in all_values.items():
        if digit_sum(v) == target:
            results.append(f"DIGIT_SUM({v}) = {target} ({sources[0]})")

    # 7. Check if target = n × prime where n is convergent
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
    for p in small_primes:
        if target % p == 0:
            q = target // p
            if q in all_values:
                results.append(f"PRIME_MULT: {p} × {q} = {target} (prime × {all_values[q][0]})")

    # 8. Check factorization
    factors = factorize(target)
    if factors:
        results.append(f"FACTORS: {target} = {' × '.join(map(str, factors))}")

    return results

def factorize(n):
    """Simple factorization."""
    if n < 2:
        return []
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def main():
    print("=" * 70)
    print("FINDING SOURCES FOR UNKNOWN M-VALUES")
    print("=" * 70)

    # Build convergent database
    print("\n1. Building convergent database...")
    all_nums, all_denoms, all_values = build_all_convergents()
    print(f"   Total unique numerators: {len(all_nums)}")
    print(f"   Total unique denominators: {len(all_denoms)}")
    print(f"   Total unique values: {len(all_values)}")

    # Check each unknown m-value
    print("\n2. Checking unknown m-values...\n")
    print("=" * 70)

    for n in sorted(UNKNOWN_M.keys()):
        m_val = UNKNOWN_M[n]
        print(f"\nm[{n}] = {m_val}")
        print("-" * 40)

        results = check_combinations(m_val, all_nums, all_denoms, all_values)

        if results:
            for r in results[:10]:  # Limit output
                print(f"  {r}")
        else:
            print("  NO MATCHES FOUND")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Quick summary
    found = 0
    for n in sorted(UNKNOWN_M.keys()):
        m_val = UNKNOWN_M[n]
        results = check_combinations(m_val, all_nums, all_denoms, all_values)
        meaningful = [r for r in results if not r.startswith("FACTORS")]
        if meaningful:
            found += 1
            print(f"m[{n:2}] = {m_val:>10}: {meaningful[0][:50]}...")
        else:
            print(f"m[{n:2}] = {m_val:>10}: UNKNOWN")

    print(f"\nFound potential sources for {found}/{len(UNKNOWN_M)} unknown values")

if __name__ == "__main__":
    main()
