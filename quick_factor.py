#!/usr/bin/env python3
"""
Quick factorization - just factors, skips expensive primepi for large primes.
"""

import sys
import json
import subprocess
import time
from datetime import datetime

# Only compute primepi for primes under this threshold
PRIMEPI_THRESHOLD = 10_000_000_000  # 10 billion

def factor_with_gnu(n):
    """Use GNU factor (much faster than sympy)."""
    result = subprocess.run(['factor', str(n)], capture_output=True, text=True)
    output = result.stdout.strip()
    parts = output.split(':')[1].strip().split()

    factors = {}
    for p in parts:
        p_int = int(p)
        factors[p_int] = factors.get(p_int, 0) + 1

    return factors

# Precomputed small prime indices (primes under 1000)
SMALL_PRIMES = {
    2:1, 3:2, 5:3, 7:4, 11:5, 13:6, 17:7, 19:8, 23:9, 29:10,
    31:11, 37:12, 41:13, 43:14, 47:15, 53:16, 59:17, 61:18, 67:19, 71:20,
    73:21, 79:22, 83:23, 89:24, 97:25, 101:26, 103:27, 107:28, 109:29, 113:30,
    127:31, 131:32, 137:33, 139:34, 149:35, 151:36, 157:37, 163:38, 167:39, 173:40,
    179:41, 181:42, 191:43, 193:44, 197:45, 199:46, 211:47, 223:48, 227:49, 229:50,
    233:51, 239:52, 241:53, 251:54, 257:55, 263:56, 269:57, 271:58, 277:59, 281:60,
    283:61, 293:62, 307:63, 311:64, 313:65, 317:66, 331:67, 337:68, 347:69, 349:70,
    353:71, 359:72, 367:73, 373:74, 379:75, 383:76, 389:77, 397:78, 401:79, 409:80,
    419:81, 421:82, 431:83, 433:84, 439:85, 443:86, 449:87, 457:88, 461:89, 463:90,
    467:91, 479:92, 487:93, 491:94, 499:95, 503:96, 509:97, 521:98, 523:99, 541:100,
}

def get_prime_index_fast(p):
    """Get prime index - fast for small primes, marks large ones."""
    if p in SMALL_PRIMES:
        return SMALL_PRIMES[p]
    if p < PRIMEPI_THRESHOLD:
        # Use sympy for medium primes
        from sympy import primepi
        return int(primepi(p))
    else:
        # Too large, mark as unknown
        return f"pi({p})"

def load_m_sequence():
    """Load m-sequence from data file."""
    with open('data_for_csolver.json') as f:
        data = json.load(f)
    return data['m_seq']

def main():
    if len(sys.argv) < 4:
        print("Usage: python quick_factor.py <n_start> <n_end> <output_file>")
        sys.exit(1)

    n_start = int(sys.argv[1])
    n_end = int(sys.argv[2])
    output_file = sys.argv[3]

    print("=" * 70)
    print(f"QUICK FACTORIZATION: n={n_start} to n={n_end}")
    print(f"Output: {output_file}")
    print("=" * 70)

    m_seq = load_m_sequence()
    results = []

    for n in range(n_start, n_end + 1):
        m_val = m_seq[n - 2]
        print(f"\nn={n}: m={m_val} ({m_val.bit_length()} bits)...", end=" ", flush=True)

        start = time.time()
        factors = factor_with_gnu(m_val)
        factor_time = time.time() - start

        # Get indices
        indices = []
        factor_details = []
        for p in sorted(factors.keys()):
            e = factors[p]
            idx = get_prime_index_fast(p)
            indices.append(idx)
            factor_details.append({
                'prime': p,
                'exponent': e,
                'index': idx
            })

        total_time = time.time() - start

        is_prime = len(factors) == 1 and list(factors.values())[0] == 1

        result = {
            'n': n,
            'm': m_val,
            'bits': m_val.bit_length(),
            'is_prime': is_prime,
            'factors': {str(p): e for p, e in factors.items()},
            'prime_indices': indices,
            'factor_details': factor_details,
            'factored': True,
            'time_seconds': total_time
        }
        results.append(result)

        print(f"Done in {total_time:.3f}s")
        print(f"   Factors: {result['factors']}")
        print(f"   Indices: {indices}")

    # Save
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
    print(f"COMPLETE: {len(results)}/{len(results)} factored")
    print(f"Results saved to: {output_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
