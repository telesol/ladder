#!/usr/bin/env python3
"""
Phase Transition Analysis at n=17
Analyzes the algorithmic change at n=17 (Fermat prime F_2)
"""

import json
from sympy import factorint, isprime
from fractions import Fraction

# k values from database
k_values = {
    1: 0x1,
    2: 0x3,
    3: 0x7,
    4: 0x8,
    5: 0x15,
    6: 0x31,
    7: 0x4c,
    8: 0xe0,
    9: 0x1d3,
    10: 0x202,
    11: 0x483,
    12: 0xa7b,
    13: 0x1460,
    14: 0x2930,
    15: 0x68f3,
    16: 0xc936,
    17: 0x1764f,
    18: 0x3080d,
    19: 0x5749f,
}

# Load m and d sequences from data_for_csolver.json
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)
    m_seq = data['m_seq']
    d_seq = data['d_seq']

def compute_adj(n):
    """Compute adj[n] = k[n] - 2*k[n-1]"""
    return k_values[n] - 2 * k_values[n-1]

def analyze_factorization(n, value):
    """Analyze factorization of a value"""
    factors = factorint(value)
    is_prime_val = isprime(value)

    # Count prime factors
    factor_list = []
    for p, exp in sorted(factors.items()):
        if exp == 1:
            factor_list.append(f"{p}")
        else:
            factor_list.append(f"{p}^{exp}")

    factor_str = " × ".join(factor_list)

    # Check for special structure
    structure = []
    if 3 in factors:
        structure.append(f"3^{factors[3]}")
    if 7 in factors:
        structure.append(f"7^{factors[7]}")
    if 13 in factors:
        structure.append(f"13^{factors[13]}")
    if 17 in factors:
        structure.append(f"17^{factors[17]}")

    return {
        'value': value,
        'decimal': str(value),
        'is_prime': is_prime_val,
        'num_distinct_primes': len(factors),
        'total_prime_factors': sum(factors.values()),
        'factorization': factor_str,
        'special_structure': " × ".join(structure) if structure else None,
        'largest_prime': max(factors.keys()) if factors else None,
    }

def analyze_adj_properties(n):
    """Analyze properties of adj[n]"""
    adj = compute_adj(n)
    sign = '+' if adj > 0 else '-'

    # Compute m[n] and d[n] (accounting for index offset)
    if n >= 4:
        m_val = m_seq[n-2]  # Corrected indexing
        d_val = d_seq[n-2]  # Corrected indexing
    else:
        m_val = None
        d_val = None

    # Check if 2^n - adj is divisible by k[d]
    if m_val is not None and d_val is not None:
        numerator = 2**n - adj
        k_d = k_values[d_val]
        is_divisible = (numerator % k_d == 0)
        computed_m = numerator // k_d if is_divisible else None
        m_matches = (computed_m == m_val) if is_divisible else False
    else:
        is_divisible = None
        computed_m = None
        m_matches = None

    return {
        'n': n,
        'adj': adj,
        'sign': sign,
        'abs_adj': abs(adj),
        'm[n]': m_val,
        'd[n]': d_val,
        '2^n - adj divisible by k[d]': is_divisible,
        'computed_m': computed_m,
        'm_matches': m_matches,
        'factorization': analyze_factorization(n, abs(adj)),
    }

def check_sign_pattern():
    """Check the ++- sign pattern"""
    pattern = []
    for n in range(2, 20):
        adj = compute_adj(n)
        sign = '+' if adj > 0 else '-'
        pattern.append((n, sign, adj))

    # Expected pattern: ++- repeating
    expected = []
    for i in range(2, 20):
        idx = (i - 2) % 3
        expected_sign = ['+', '+', '-'][idx]
        expected.append((i, expected_sign))

    # Check matches
    matches = []
    for i, (n, actual_sign, adj) in enumerate(pattern):
        exp_n, exp_sign = expected[i]
        match = (actual_sign == exp_sign)
        matches.append({
            'n': n,
            'expected': exp_sign,
            'actual': actual_sign,
            'match': match,
            'adj': adj,
        })

    return matches

def analyze_m_formula_changes():
    """Analyze m[n] formula changes at n=17"""
    results = []

    for n in range(4, 20):
        m_val = m_seq[n-2]
        d_val = d_seq[n-2]
        k_val = k_values[n]
        k_prev = k_values[n-1]
        adj = compute_adj(n)

        # Check formula: m[n] = (2^n - adj[n]) / k[d[n]]
        numerator = 2**n - adj
        k_d = k_values[d_val]
        computed_m = numerator // k_d

        # Analyze m[n] factorization
        m_factors = analyze_factorization(n, m_val)

        # Check if 17 divides m[n]
        has_17 = (17 in factorint(m_val))

        # Check if 13 divides m[n]
        has_13 = (13 in factorint(m_val))

        results.append({
            'n': n,
            'm[n]': m_val,
            'd[n]': d_val,
            'k[n]': k_val,
            'adj[n]': adj,
            'm_factorization': m_factors['factorization'],
            'has_17': has_17,
            'has_13': has_13,
            'is_prime': m_factors['is_prime'],
            'num_distinct_primes': m_factors['num_distinct_primes'],
        })

    return results

def check_2_16_threshold():
    """Check if 2^16 = 65536 is a threshold"""
    threshold = 2**16

    results = []
    for n in range(14, 20):
        k_val = k_values[n]
        ratio = k_val / threshold
        below_threshold = k_val < threshold

        results.append({
            'n': n,
            'k[n]': k_val,
            '2^16': threshold,
            'k[n] / 2^16': f"{ratio:.6f}",
            'k[n] < 2^16': below_threshold,
        })

    return results

def analyze_growth_rates():
    """Analyze growth rate changes before and after n=17"""
    results = []

    for n in range(3, 20):
        k_val = k_values[n]
        k_prev = k_values[n-1]

        # Growth ratio
        ratio = k_val / k_prev

        # Log2 ratio (bits added)
        import math
        bits_n = math.log2(k_val)
        bits_prev = math.log2(k_prev)
        bits_added = bits_n - bits_prev

        results.append({
            'n': n,
            'k[n]': k_val,
            'k[n]/k[n-1]': f"{ratio:.6f}",
            'bits_added': f"{bits_added:.6f}",
        })

    return results

def main():
    """Main analysis"""
    print("=" * 80)
    print("PHASE TRANSITION ANALYSIS AT n=17")
    print("=" * 80)
    print()

    # 4.1. Compare k[n] factorization for n=14,15,16 vs n=17,18,19
    print("4.1. K-VALUE FACTORIZATION COMPARISON")
    print("-" * 80)

    for n in [14, 15, 16, 17, 18, 19]:
        k_val = k_values[n]
        analysis = analyze_factorization(n, k_val)

        print(f"\nn={n}: k[{n}] = {k_val}")
        print(f"  Decimal: {analysis['decimal']}")
        print(f"  Factorization: {analysis['factorization']}")
        print(f"  Prime? {analysis['is_prime']}")
        print(f"  Distinct primes: {analysis['num_distinct_primes']}")
        print(f"  Total prime factors: {analysis['total_prime_factors']}")
        if analysis['special_structure']:
            print(f"  Special structure: {analysis['special_structure']}")

    print()
    print("=" * 80)

    # 4.2. Compare adj[n] properties before/after n=17
    print("\n4.2. ADJ[N] PROPERTIES BEFORE/AFTER N=17")
    print("-" * 80)

    for n in range(14, 20):
        adj_analysis = analyze_adj_properties(n)
        print(f"\nn={n}:")
        print(f"  adj[{n}] = {adj_analysis['sign']}{adj_analysis['abs_adj']}")
        print(f"  m[{n}] = {adj_analysis['m[n]']}")
        print(f"  d[{n}] = {adj_analysis['d[n]']}")
        print(f"  Formula check: m[n] = (2^n - adj) / k[d] → {adj_analysis['m_matches']}")

    print()
    print("=" * 80)

    # Sign pattern analysis
    print("\n4.2.1. SIGN PATTERN ANALYSIS (++- pattern)")
    print("-" * 80)

    sign_matches = check_sign_pattern()
    consecutive_matches = 0
    max_consecutive = 0
    break_point = None

    for item in sign_matches:
        print(f"n={item['n']:2d}: expected={item['expected']}, actual={item['actual']}, "
              f"match={item['match']}, adj={item['adj']:+6d}")

        if item['match']:
            consecutive_matches += 1
            max_consecutive = max(max_consecutive, consecutive_matches)
        else:
            if consecutive_matches > 0 and break_point is None:
                break_point = item['n']
            consecutive_matches = 0

    print(f"\nMax consecutive matches: {max_consecutive}")
    print(f"Pattern breaks at: n={break_point}")

    print()
    print("=" * 80)

    # 4.3. Check if 2^16 = 65536 is a threshold
    print("\n4.3. 2^16 = 65536 THRESHOLD ANALYSIS")
    print("-" * 80)

    threshold_results = check_2_16_threshold()
    for item in threshold_results:
        print(f"n={item['n']}: k[{item['n']}] = {item['k[n]']:7d}, "
              f"k/2^16 = {item['k[n] / 2^16']}, below? {item['k[n] < 2^16']}")

    print()
    print(f"Transition: k[16] = {k_values[16]} < 2^16 = 65536")
    print(f"           k[17] = {k_values[17]} > 2^16 = 65536")
    print(f"\nn=17 is the FIRST puzzle where k[n] > 2^16")

    print()
    print("=" * 80)

    # 4.4. Analyze m[n] formula changes at n=17
    print("\n4.4. M[N] FORMULA CHANGES AT N=17")
    print("-" * 80)

    m_changes = analyze_m_formula_changes()

    print("\nBEFORE n=17:")
    for item in m_changes:
        if item['n'] < 17:
            print(f"n={item['n']:2d}: m[{item['n']}] = {item['m[n]']:8d} = {item['m_factorization']}, "
                  f"has_17={item['has_17']}, d[{item['n']}]={item['d[n]']}")

    print("\nAT n=17:")
    for item in m_changes:
        if item['n'] == 17:
            print(f"n={item['n']:2d}: m[{item['n']}] = {item['m[n]']:8d} = {item['m_factorization']}, "
                  f"has_17={item['has_17']}, d[{item['n']}]={item['d[n]']}")

    print("\nAFTER n=17:")
    for item in m_changes:
        if item['n'] > 17:
            print(f"n={item['n']:2d}: m[{item['n']}] = {item['m[n]']:8d} = {item['m_factorization']}, "
                  f"has_17={item['has_17']}, d[{item['n']}]={item['d[n]']}")

    print()
    print("=" * 80)

    # 4.5. Growth rate analysis
    print("\n4.5. GROWTH RATE ANALYSIS")
    print("-" * 80)

    growth_rates = analyze_growth_rates()

    print("\nBEFORE n=17:")
    for item in growth_rates:
        if item['n'] < 17:
            print(f"n={item['n']:2d}: k[{item['n']}]/k[{item['n']-1}] = {item['k[n]/k[n-1]']}, "
                  f"bits_added = {item['bits_added']}")

    print("\nAT n=17:")
    for item in growth_rates:
        if item['n'] == 17:
            print(f"n={item['n']:2d}: k[{item['n']}]/k[{item['n']-1}] = {item['k[n]/k[n-1]']}, "
                  f"bits_added = {item['bits_added']}")

    print("\nAFTER n=17:")
    for item in growth_rates:
        if item['n'] > 17:
            print(f"n={item['n']:2d}: k[{item['n']}]/k[{item['n']-1}] = {item['k[n]/k[n-1]']}, "
                  f"bits_added = {item['bits_added']}")

    # Calculate average growth before and after
    avg_before = sum(float(item['k[n]/k[n-1]']) for item in growth_rates if 3 <= item['n'] < 17) / 14
    avg_at_17 = float(growth_rates[14]['k[n]/k[n-1]'])
    avg_after = sum(float(item['k[n]/k[n-1]']) for item in growth_rates if item['n'] > 17) / 2

    print(f"\nAverage growth ratio before n=17: {avg_before:.6f}")
    print(f"Growth ratio at n=17: {avg_at_17:.6f}")
    print(f"Average growth ratio after n=17: {avg_after:.6f}")

    print()
    print("=" * 80)

    # Special analysis of k[17]
    print("\nSPECIAL ANALYSIS: k[17] = 95823")
    print("-" * 80)

    k17_factors = factorint(k_values[17])
    print(f"k[17] = 95823 = 3^4 × 7 × 13^2")
    print(f"       = 81 × 7 × 169")
    print(f"       = 567 × 169")
    print()
    print("HIGHLY STRUCTURED:")
    print("  - Powers: 3^4, 13^2")
    print("  - Prime 7 (single)")
    print("  - 17 = F_2 (Fermat prime 2^4 + 1)")
    print("  - NO prime 17 in k[17] itself!")
    print("  - Suggests: possibly hardcoded or special construction")

    print()
    print("=" * 80)

if __name__ == '__main__':
    main()
