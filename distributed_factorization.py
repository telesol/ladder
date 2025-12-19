#!/usr/bin/env python3
"""
Distributed factorization of m-sequence values.
Run this script on each box with different n_start and n_end parameters.

Usage:
  python distributed_factorization.py <n_start> <n_end> <output_file>

Example:
  python distributed_factorization.py 36 45 factorization_36_45.json
"""

import sys
import json
import time
from datetime import datetime

# Use sympy for factorization
from sympy import factorint, prime, primepi, isprime

def load_m_sequence():
    """Load m-sequence from data file."""
    with open('data_for_csolver.json') as f:
        data = json.load(f)
    return data['m_seq']

def factor_m_value(n, m_val, timeout_seconds=300):
    """Factor a single m-value and return prime indices."""
    start_time = time.time()
    result = {
        'n': n,
        'm': m_val,
        'bits': m_val.bit_length(),
        'is_prime': False,
        'factors': {},
        'prime_indices': [],
        'factored': False,
        'time_seconds': 0
    }

    # Check if prime first (fast)
    if isprime(m_val):
        result['is_prime'] = True
        result['factors'] = {str(m_val): 1}
        try:
            idx = primepi(m_val)
            result['prime_indices'] = [idx]
            result['prime_index'] = idx
        except:
            result['prime_indices'] = ['too_large']
        result['factored'] = True
        result['time_seconds'] = time.time() - start_time
        return result

    # Try factorization
    try:
        factors = factorint(m_val)  # No timeout parameter in sympy

        result['factors'] = {str(int(p)): int(e) for p, e in factors.items()}
        result['factored'] = True

        # Get prime indices
        indices = []
        for p in sorted(factors.keys()):
            try:
                idx = int(primepi(p))
                indices.append(idx)
            except:
                indices.append(f'pi({p})')

        result['prime_indices'] = indices

        # Also store factor details
        result['factor_details'] = []
        for p, e in sorted(factors.items()):
            try:
                idx = int(primepi(p))
                result['factor_details'].append({
                    'prime': int(p),
                    'exponent': int(e),
                    'index': idx
                })
            except:
                result['factor_details'].append({
                    'prime': int(p),
                    'exponent': int(e),
                    'index': 'large'
                })

    except Exception as e:
        result['error'] = str(e)
        result['factored'] = False

    result['time_seconds'] = time.time() - start_time
    return result

def main():
    if len(sys.argv) < 4:
        print("Usage: python distributed_factorization.py <n_start> <n_end> <output_file>")
        print("Example: python distributed_factorization.py 36 45 factorization_36_45.json")
        sys.exit(1)

    n_start = int(sys.argv[1])
    n_end = int(sys.argv[2])
    output_file = sys.argv[3]

    print("=" * 70)
    print(f"DISTRIBUTED FACTORIZATION: n={n_start} to n={n_end}")
    print(f"Output: {output_file}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    # Load m-sequence
    m_seq = load_m_sequence()

    results = []

    for n in range(n_start, n_end + 1):
        m_val = m_seq[n - 2]  # m[n] = m_seq[n-2]

        print(f"\nProcessing n={n}, m={m_val} ({m_val.bit_length()} bits)...")

        result = factor_m_value(n, m_val)
        results.append(result)

        if result['factored']:
            print(f"  ✓ Factored in {result['time_seconds']:.2f}s")
            print(f"    Factors: {result['factors']}")
            print(f"    Prime indices: {result['prime_indices']}")
        else:
            print(f"  ✗ Failed to factor: {result.get('error', 'unknown')}")

    # Save results
    output = {
        'metadata': {
            'n_range': [n_start, n_end],
            'timestamp': datetime.now().isoformat(),
            'total_values': len(results),
            'factored_count': sum(1 for r in results if r['factored'])
        },
        'results': results
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 70)
    print(f"COMPLETE: {output['metadata']['factored_count']}/{len(results)} factored")
    print(f"Results saved to: {output_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
