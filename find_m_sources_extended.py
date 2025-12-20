#!/usr/bin/env python3
"""
Extended search for m-value sources (n≥15).
Computes more convergent terms and tries complex combinations.
"""

import math
from itertools import combinations, product as iterproduct
from functools import lru_cache

# Known m-sequence (n=2 to 31)
M_SEQUENCE = {
    2: 3, 3: 7, 4: 22, 5: 9, 6: 19, 7: 50, 8: 23, 9: 493, 10: 19,
    11: 1921, 12: 1241, 13: 8342, 14: 2034, 15: 26989, 16: 8470,
    17: 138269, 18: 255121, 19: 564091, 20: 900329, 21: 670674,
    22: 4494340, 23: 7256672, 24: 13127702, 25: 5765582, 26: 50898620,
    27: 23103005, 28: 33504646, 29: 156325542, 30: 536813704, 31: 350549882
}

def get_extended_convergents(constant_name, n_terms=60):
    """Get extended continued fraction convergents."""

    if constant_name == 'pi':
        # Extended π continued fraction
        cf = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2,
              1, 84, 2, 1, 1, 15, 3, 13, 1, 4, 2, 6, 6, 99, 1, 2, 2, 6, 3, 5,
              1, 1, 6, 8, 1, 7, 1, 2, 3, 7, 1, 2, 1, 1, 12, 1, 1, 1, 3, 1]
    elif constant_name == 'e':
        cf = [2, 1, 2]
        for k in range(1, n_terms // 3 + 2):
            cf.extend([1, 1, 2 * (k + 1)])
    elif constant_name == 'sqrt2':
        cf = [1] + [2] * (n_terms - 1)
    elif constant_name == 'sqrt3':
        cf = [1] + [1 if i % 2 == 0 else 2 for i in range(n_terms - 1)]
    elif constant_name == 'phi':
        cf = [1] * n_terms
    elif constant_name == 'ln2':
        cf = [0, 1, 2, 3, 1, 6, 3, 1, 1, 2, 1, 1, 1, 1, 3, 10, 1, 1, 1, 2,
              1, 1, 1, 1, 3, 2, 3, 1, 13, 7, 4, 1, 1, 1, 7, 2, 4, 1, 1, 2,
              1, 2, 1, 4, 3, 1, 1, 1, 1, 1, 1, 1, 1, 15, 1, 4, 1, 3, 1, 1]
    else:
        return [], []

    cf = cf[:n_terms]

    # Compute convergents
    h_prev2, h_prev1 = 0, 1
    k_prev2, k_prev1 = 1, 0
    numerators, denominators = [], []

    for a in cf:
        h = a * h_prev1 + h_prev2
        k = a * k_prev1 + k_prev2
        numerators.append(h)
        denominators.append(k)
        h_prev2, h_prev1 = h_prev1, h
        k_prev2, k_prev1 = k_prev1, k

    return numerators, denominators

def build_extended_database():
    """Build extended convergent database."""
    constants = ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']
    all_values = {}  # value -> list of sources

    for const in constants:
        nums, denoms = get_extended_convergents(const, 60)
        for i, (h, k) in enumerate(zip(nums, denoms)):
            if h not in all_values:
                all_values[h] = []
            all_values[h].append((const, 'h', i))

            if k not in all_values:
                all_values[k] = []
            all_values[k].append((const, 'k', i))

    return all_values

def factorize(n):
    """Factorize a number."""
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

def check_extended_combinations(target, all_values, max_val=1000000):
    """Check extended combinations for target value."""
    results = []

    # Get all convergent values up to a reasonable limit
    conv_values = [v for v in all_values.keys() if 0 < v < max_val]
    conv_set = set(conv_values)

    # 1. Direct match
    if target in all_values:
        for src in all_values[target]:
            results.append(f"DIRECT: {src[0]}_{src[1]}{src[2]}")

    # 2. Products a × b
    for a in conv_values:
        if a > 1 and target % a == 0:
            b = target // a
            if b in all_values and a in all_values:
                src_a = all_values[a][0]
                src_b = all_values[b][0]
                results.append(f"PRODUCT: {a} × {b} = {target} ({src_a[0]}_{src_a[1]}{src_a[2]} × {src_b[0]}_{src_b[1]}{src_b[2]})")

    # 3. Sums a + b
    for a in conv_values:
        b = target - a
        if b > 0 and b in conv_set and a <= b:
            src_a = all_values[a][0]
            src_b = all_values[b][0]
            results.append(f"SUM: {a} + {b} = {target} ({src_a[0]}_{src_a[1]}{src_a[2]} + {src_b[0]}_{src_b[1]}{src_b[2]})")

    # 4. Differences a - b
    for a in conv_values:
        if a > target:
            b = a - target
            if b in conv_set:
                src_a = all_values[a][0]
                src_b = all_values[b][0]
                results.append(f"DIFF: {a} - {b} = {target} ({src_a[0]}_{src_a[1]}{src_a[2]} - {src_b[0]}_{src_b[1]}{src_b[2]})")

    # 5. Triple products a × b × c (limited search)
    small_convs = [v for v in conv_values if v < 1000]
    for a in small_convs[:30]:
        if target % a == 0:
            remainder = target // a
            for b in small_convs[:30]:
                if b > 1 and remainder % b == 0:
                    c = remainder // b
                    if c in conv_set and a in all_values and b in all_values:
                        src_a = all_values[a][0]
                        src_b = all_values[b][0]
                        src_c = all_values[c][0]
                        results.append(f"TRIPLE: {a} × {b} × {c} = {target}")

    # 6. a × b + c
    for a in small_convs[:20]:
        for b in small_convs[:20]:
            prod = a * b
            if prod < target:
                c = target - prod
                if c in conv_set:
                    results.append(f"COMBO: {a} × {b} + {c} = {target}")

    # 7. a × b - c
    for a in small_convs[:20]:
        for b in small_convs[:20]:
            prod = a * b
            if prod > target:
                c = prod - target
                if c in conv_set:
                    results.append(f"COMBO: {a} × {b} - {c} = {target}")

    # 8. (a + b) × c
    for c in small_convs[:30]:
        if c > 1 and target % c == 0:
            sum_ab = target // c
            for a in conv_values:
                if a < sum_ab:
                    b = sum_ab - a
                    if b in conv_set:
                        results.append(f"COMBO: ({a} + {b}) × {c} = {target}")
                        break  # Just find one

    # 9. Check if factors are convergents
    factors = factorize(target)
    factor_sources = []
    for f in set(factors):
        if f in all_values:
            src = all_values[f][0]
            factor_sources.append(f"{f}({src[0]}_{src[1]}{src[2]})")
    if factor_sources:
        results.append(f"FACTOR_MATCH: {target} has convergent factors: {', '.join(factor_sources)}")

    # 10. Factorization for reference
    if factors:
        if len(factors) <= 6:
            results.append(f"FACTORS: {target} = {' × '.join(map(str, factors))}")

    return results

def main():
    print("=" * 70)
    print("EXTENDED SEARCH FOR M-VALUE SOURCES (n ≥ 13)")
    print("=" * 70)

    # Build extended database
    print("\n1. Building extended convergent database (60 terms each)...")
    all_values = build_extended_database()
    print(f"   Total unique convergent values: {len(all_values)}")

    # Show some large convergent values
    large_convs = sorted([v for v in all_values.keys() if v > 10000])[:20]
    print(f"   Sample large convergents: {large_convs[:10]}")

    # Unknown m-values to search
    unknown_m = {n: M_SEQUENCE[n] for n in range(13, 32) if n in M_SEQUENCE}

    print(f"\n2. Searching for sources of {len(unknown_m)} unknown m-values...\n")
    print("=" * 70)

    found_count = 0
    for n in sorted(unknown_m.keys()):
        m_val = unknown_m[n]
        print(f"\nm[{n}] = {m_val:,}")
        print("-" * 50)

        results = check_extended_combinations(m_val, all_values)

        # Filter to show most relevant
        meaningful = [r for r in results if not r.startswith("FACTORS")]

        if meaningful:
            found_count += 1
            for r in meaningful[:5]:
                print(f"  ✓ {r}")
        else:
            # Show factorization anyway
            factors = factorize(m_val)
            print(f"  ? No convergent match found")
            print(f"    Factors: {' × '.join(map(str, factors[:8]))}")

    print("\n" + "=" * 70)
    print(f"SUMMARY: Found potential sources for {found_count}/{len(unknown_m)} values")
    print("=" * 70)

    # Additional analysis
    print("\n3. Looking for patterns in factorizations...")
    print("-" * 50)

    for n in [13, 15, 16, 17, 18, 19, 20, 21]:
        m_val = M_SEQUENCE[n]
        factors = factorize(m_val)

        # Check each factor
        conv_factors = []
        for f in set(factors):
            if f in all_values:
                src = all_values[f][0]
                conv_factors.append(f"{f}={src[0]}_{src[1]}{src[2]}")

        print(f"m[{n}] = {m_val:>10}: factors = {factors[:6]}")
        if conv_factors:
            print(f"           convergent factors: {conv_factors}")

if __name__ == "__main__":
    main()
