#!/usr/bin/env python3
"""
Factor the first 30 m-sequence values to identify prime structure.

This script:
1. Reads m_seq from data_for_csolver.json
2. Uses sympy.factorint() to factor each value
3. Identifies prime indices (which prime number is each factor)
4. Outputs a JSON file with detailed factorization results
"""

import json
import sympy
from sympy import factorint, prime
from pathlib import Path

def get_prime_index(p):
    """
    Get the index of a prime number (1-indexed).
    p[1]=2, p[2]=3, p[3]=5, p[4]=7, p[5]=11, p[6]=13, p[7]=17, etc.

    Returns None if not prime.
    """
    if not sympy.isprime(p):
        return None

    # Use sympy's primepi to count primes <= p, which gives us the index
    return sympy.primepi(p)

def factor_with_prime_indices(n):
    """
    Factor n and identify which prime each factor is.

    Returns:
        dict: {
            'value': n,
            'factorization': {prime: exponent, ...},
            'prime_indices': {prime: index, ...},  # p[7]=17 means prime_indices[17]=7
            'factor_description': "2^2 * p[7]^3" style string
        }
    """
    if n == 1:
        return {
            'value': 1,
            'factorization': {},
            'prime_indices': {},
            'factor_description': '1'
        }

    factors = factorint(n)
    prime_indices = {}
    description_parts = []

    for p, exp in sorted(factors.items()):
        idx = get_prime_index(p)
        prime_indices[str(p)] = int(idx)  # Convert to int for JSON

        # Build description
        if exp == 1:
            description_parts.append(f"p[{idx}]")
        else:
            description_parts.append(f"p[{idx}]^{exp}")

    return {
        'value': int(n),  # Convert to int for JSON
        'factorization': {str(k): int(v) for k, v in factors.items()},  # Convert all to int for JSON
        'prime_indices': prime_indices,
        'factor_description': ' * '.join(description_parts) if description_parts else '1'
    }

def analyze_patterns(results):
    """
    Analyze the factorization results for patterns.

    Returns:
        dict: Pattern analysis including:
            - Most common primes
            - Most common prime indices
            - Self-references (if detectable)
    """
    prime_count = {}
    prime_index_count = {}

    for m_data in results:
        for p_str, idx in m_data['prime_indices'].items():
            # Count prime occurrences
            if p_str not in prime_count:
                prime_count[p_str] = 0
            prime_count[p_str] += 1

            # Count prime index occurrences
            idx_str = f"p[{idx}]"
            if idx_str not in prime_index_count:
                prime_index_count[idx_str] = 0
            prime_index_count[idx_str] += 1

    # Sort by frequency
    sorted_primes = sorted(prime_count.items(), key=lambda x: x[1], reverse=True)
    sorted_indices = sorted(prime_index_count.items(), key=lambda x: x[1], reverse=True)

    return {
        'prime_frequency': {p: count for p, count in sorted_primes[:10]},  # Top 10
        'prime_index_frequency': {idx: count for idx, count in sorted_indices[:10]},  # Top 10
        'total_unique_primes': len(prime_count),
        'total_unique_prime_indices': len(prime_index_count)
    }

def main():
    # Load data
    data_path = Path('/home/rkh/ladder/data_for_csolver.json')
    with open(data_path, 'r') as f:
        data = json.load(f)

    m_seq = data['m_seq']

    # Factor the first 30 values (indices 0-29, corresponding to m[2]-m[31])
    results = []

    print("Factoring m-sequence values...")
    print("=" * 80)

    for i in range(30):
        m_value = m_seq[i]
        m_index = i + 2  # m[2] is at index 0, m[3] at index 1, etc.

        print(f"\nFactoring m[{m_index}] = {m_value}")

        factor_result = factor_with_prime_indices(m_value)
        factor_result['m_index'] = m_index

        print(f"  Factorization: {factor_result['factorization']}")
        print(f"  Prime indices: {factor_result['factor_description']}")

        results.append(factor_result)

    print("\n" + "=" * 80)
    print("Analyzing patterns...")

    pattern_analysis = analyze_patterns(results)

    print("\nMost common primes:")
    for prime, count in pattern_analysis['prime_frequency'].items():
        idx = get_prime_index(int(prime))
        print(f"  p[{idx}] = {prime}: appears {count} times")

    print("\nMost common prime indices:")
    for idx_str, count in pattern_analysis['prime_index_frequency'].items():
        print(f"  {idx_str}: appears {count} times")

    # Create output
    output = {
        'description': 'Factorization of m[2] through m[31] (first 30 m-sequence values)',
        'prime_notation': 'p[1]=2, p[2]=3, p[3]=5, p[4]=7, p[5]=11, p[6]=13, p[7]=17, ...',
        'results': results,
        'pattern_analysis': pattern_analysis
    }

    # Write output
    output_path = Path('/home/rkh/ladder/experiments/06-pysr-m-sequence/factorization_results.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults written to: {output_path}")
    print(f"Total unique primes found: {pattern_analysis['total_unique_primes']}")
    print(f"Total unique prime indices: {pattern_analysis['total_unique_prime_indices']}")

    # Special focus on p[7]=17
    print("\n" + "=" * 80)
    print("SPECIAL FOCUS: p[7] = 17")
    print("=" * 80)

    p7_appearances = []
    for m_data in results:
        if '17' in m_data['prime_indices']:
            exp = m_data['factorization'].get('17', 0)
            p7_appearances.append({
                'm_index': m_data['m_index'],
                'exponent': exp,
                'value': m_data['value']
            })

    if p7_appearances:
        print(f"\np[7]=17 appears in {len(p7_appearances)} of the first 30 m-sequence values:")
        for app in p7_appearances:
            print(f"  m[{app['m_index']}] = {app['value']} contains 17^{app['exponent']}")
    else:
        print("\np[7]=17 does NOT appear in the first 30 m-sequence values")

    print("\n" + "=" * 80)
    print("COMPLETE!")
    print("=" * 80)

if __name__ == '__main__':
    main()
