#!/usr/bin/env python3
"""
Fast factorization using GNU factor + sympy primepi for indices.
Much faster than pure sympy factorint.
"""

import sys
import json
import subprocess
import time
from datetime import datetime

from sympy import primepi, isprime

def factor_with_gnu(n):
    """Use GNU factor (much faster than sympy)."""
    result = subprocess.run(['factor', str(n)], capture_output=True, text=True)
    output = result.stdout.strip()
    # Output format: "n: p1 p2 p3..." or "n: p1^e1 p2^e2..."
    parts = output.split(':')[1].strip().split()

    factors = {}
    for p in parts:
        p_int = int(p)
        factors[p_int] = factors.get(p_int, 0) + 1

    return factors

def load_m_sequence():
    """Load m-sequence from data file."""
    with open('data_for_csolver.json') as f:
        data = json.load(f)
    return data['m_seq']

def factor_m_value(n, m_val):
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

    try:
        # Use GNU factor (fast!)
        factors = factor_with_gnu(m_val)

        # Check if prime
        if len(factors) == 1 and list(factors.values())[0] == 1:
            result['is_prime'] = True

        result['factors'] = {str(p): e for p, e in factors.items()}
        result['factored'] = True

        # Get prime indices (this can be slow for large primes)
        indices = []
        result['factor_details'] = []

        for p in sorted(factors.keys()):
            e = factors[p]
            try:
                idx = int(primepi(p))
                indices.append(idx)
                result['factor_details'].append({
                    'prime': p,
                    'exponent': e,
                    'index': idx
                })
            except:
                indices.append(f'pi({p})')
                result['factor_details'].append({
                    'prime': p,
                    'exponent': e,
                    'index': 'large'
                })

        result['prime_indices'] = indices

    except Exception as e:
        result['error'] = str(e)
        result['factored'] = False

    result['time_seconds'] = time.time() - start_time
    return result

def main():
    if len(sys.argv) < 4:
        print("Usage: python fast_factorization.py <n_start> <n_end> <output_file>")
        print("Example: python fast_factorization.py 56 70 factorization_56_70.json")
        sys.exit(1)

    n_start = int(sys.argv[1])
    n_end = int(sys.argv[2])
    output_file = sys.argv[3]

    print("=" * 70)
    print(f"FAST FACTORIZATION: n={n_start} to n={n_end}")
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
            print(f"  Factored in {result['time_seconds']:.3f}s")
            print(f"    Factors: {result['factors']}")
            print(f"    Prime indices: {result['prime_indices']}")
        else:
            print(f"  Failed to factor: {result.get('error', 'unknown')}")

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
