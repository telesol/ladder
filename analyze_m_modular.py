#!/usr/bin/env python3
"""
Modular pattern analysis for m-sequence
Goal: Find construction rule via modular arithmetic
"""

import json
from collections import defaultdict
from typing import List, Dict, Tuple

# Load m-sequence from database
import sqlite3
import sys

def load_m_sequence():
    """Load m-sequence from task specification"""
    # Task-provided values (may differ from database)
    # m[2]=3, m[3]=7, m[4]=22, m[5]=27, m[6]=57, m[7]=150, m[8]=184, m[9]=493, ...
    m_seq = {
        2: 3,
        3: 7,
        4: 22,
        5: 27,
        6: 57,
        7: 150,
        8: 184,
        9: 493,
        10: 1444,
        11: 1921,
        12: 3723,
        13: 8342,
        14: 16272,
        15: 26989,
        16: 67760
    }

    return m_seq

def analyze_modular_patterns(m_seq: Dict[int, int], primes: List[int]):
    """Analyze m[n] mod p for various primes"""

    print("=" * 80)
    print("MODULAR PATTERN ANALYSIS FOR m-SEQUENCE")
    print("=" * 80)

    results = {}

    for p in primes:
        print(f"\n{'=' * 80}")
        print(f"ANALYZING m[n] mod {p}")
        print(f"{'=' * 80}")

        residues = {}
        for n in sorted(m_seq.keys()):
            residues[n] = m_seq[n] % p

        # Print residues
        print(f"\nn  | m[n] mod {p}")
        print("-" * 30)
        for n in sorted(residues.keys())[:20]:  # First 20
            print(f"{n:2d} | {residues[n]:2d}")

        # Check for periodicity
        period = find_period(list(residues.values()))
        if period:
            print(f"\n*** PERIOD FOUND: {period} ***")
        else:
            print(f"\nNo clear period detected (checked up to length 20)")

        # Check if residue relates to n mod p
        n_relation = check_n_relation(residues, p)
        if n_relation:
            print(f"\n*** RELATION TO n: {n_relation} ***")

        results[p] = {
            'residues': residues,
            'period': period,
            'n_relation': n_relation
        }

    return results

def find_period(sequence: List[int], max_period: int = 20) -> int:
    """Find if sequence has a period"""
    n = len(sequence)

    for period in range(1, min(max_period + 1, n // 2)):
        is_periodic = True
        for i in range(period, min(n, period * 3)):
            if sequence[i] != sequence[i % period]:
                is_periodic = False
                break

        if is_periodic and period < n:
            # Verify more carefully
            valid = True
            for i in range(n):
                if sequence[i] != sequence[i % period]:
                    valid = False
                    break
            if valid:
                return period

    return None

def check_n_relation(residues: Dict[int, int], p: int) -> str:
    """Check if m[n] mod p relates to n mod p"""

    # Check if m[n] ≡ n (mod p)
    if all(residues[n] == n % p for n in residues.keys()):
        return f"m[n] ≡ n (mod {p})"

    # Check if m[n] ≡ a*n (mod p) for some a
    for a in range(p):
        if all(residues[n] == (a * n) % p for n in residues.keys()):
            return f"m[n] ≡ {a}*n (mod {p})"

    # Check if m[n] ≡ a*n + b (mod p) for some a, b
    for a in range(p):
        for b in range(p):
            if all(residues[n] == (a * n + b) % p for n in residues.keys()):
                return f"m[n] ≡ {a}*n + {b} (mod {p})"

    return None

def analyze_mod7_deeply(m_seq: Dict[int, int]):
    """Deep analysis of m[n] mod 7 (since 7 divides m[4])"""

    print("\n" + "=" * 80)
    print("DEEP ANALYSIS: m[n] mod 7")
    print("=" * 80)

    print(f"\nREASON: m[4]/m[3] = 22/7 ≈ π, so 7 is structurally important")

    # Decompose m[n] = 7*q[n] + r[n]
    print(f"\nDecomposition: m[n] = 7*q[n] + r[n]")
    print(f"\nn   | m[n]     | q[n]   | r[n] | n mod 7")
    print("-" * 60)

    q_seq = {}
    r_seq = {}

    for n in sorted(m_seq.keys())[:25]:
        m = m_seq[n]
        q = m // 7
        r = m % 7
        q_seq[n] = q
        r_seq[n] = r
        print(f"{n:2d}  | {m:8d} | {q:6d} | {r:4d} | {n % 7}")

    # Check if r[n] has a pattern
    print(f"\n{'=' * 80}")
    print("PATTERN IN r[n] = m[n] mod 7:")
    print("=" * 80)

    r_list = [r_seq[n] for n in sorted(r_seq.keys())]
    print(f"\nSequence: {r_list[:25]}")

    period = find_period(r_list)
    if period:
        print(f"\n*** PERIOD: {period} ***")
        print(f"Repeating pattern: {r_list[:period]}")

    # Check if r[n] relates to n mod 7
    print(f"\nRelation to n mod 7:")
    for n in sorted(r_seq.keys())[:25]:
        print(f"n={n:2d}: r[n]={r_seq[n]}, n mod 7={n % 7}, diff={r_seq[n] - (n % 7)}")

    # Check if q[n] has a pattern
    print(f"\n{'=' * 80}")
    print("PATTERN IN q[n] = m[n] // 7:")
    print("=" * 80)

    print(f"\nq-sequence: {[q_seq[n] for n in sorted(q_seq.keys())[:15]]}")

    # Check if q[n] relates to m[n-1]
    print(f"\nChecking if q[n] relates to previous m values:")
    for n in sorted(q_seq.keys())[1:15]:
        q = q_seq[n]
        m_prev = m_seq.get(n-1, 0)
        print(f"n={n:2d}: q[n]={q:6d}, m[n-1]={m_prev:6d}, ratio={q/m_prev if m_prev > 0 else 0:.4f}")

    return q_seq, r_seq

def check_crt_reconstruction(m_seq: Dict[int, int], primes: List[int]):
    """Check if m[n] can be reconstructed via Chinese Remainder Theorem"""

    print("\n" + "=" * 80)
    print("CHINESE REMAINDER THEOREM RECONSTRUCTION TEST")
    print("=" * 80)

    # Compute modulus product
    M = 1
    for p in primes:
        M *= p

    print(f"\nPrimes: {primes}")
    print(f"Modulus product: M = {M}")

    # For each n, try to reconstruct m[n] from residues
    print(f"\nTesting reconstruction for first 10 values:")
    print(f"\nn   | m[n] actual | m[n] mod M | Match?")
    print("-" * 60)

    successes = 0
    for n in sorted(m_seq.keys())[:10]:
        m_actual = m_seq[n]
        m_mod_M = m_actual % M

        # The residues uniquely determine m[n] mod M
        # So if m[n] < M, we can reconstruct it exactly
        match = "YES" if m_actual < M else f"NO (m[n] >= M)"
        if m_actual < M:
            successes += 1

        print(f"{n:2d}  | {m_actual:11d} | {m_mod_M:10d} | {match}")

    print(f"\nNote: CRT can reconstruct m[n] exactly if m[n] < M = {M}")
    print(f"For larger m[n], we only know m[n] mod M")

def analyze_differences_mod_p(m_seq: Dict[int, int], primes: List[int]):
    """Analyze differences Δm[n] = m[n] - m[n-1] modulo p"""

    print("\n" + "=" * 80)
    print("DIFFERENCE ANALYSIS: Δm[n] = m[n] - m[n-1]")
    print("=" * 80)

    for p in primes[:3]:  # Just check first few primes
        print(f"\n{'=' * 80}")
        print(f"Δm[n] mod {p}")
        print(f"{'=' * 80}")

        deltas = {}
        for n in sorted(m_seq.keys())[1:]:
            if n-1 in m_seq:
                delta = m_seq[n] - m_seq[n-1]
                deltas[n] = delta % p

        print(f"\nn   | Δm[n] | Δm[n] mod {p}")
        print("-" * 40)
        for n in sorted(deltas.keys())[:20]:
            delta_actual = m_seq[n] - m_seq[n-1]
            print(f"{n:2d}  | {delta_actual:6d} | {deltas[n]:2d}")

        # Check for period in differences
        delta_list = [deltas[n] for n in sorted(deltas.keys())]
        period = find_period(delta_list)
        if period:
            print(f"\n*** PERIOD IN DIFFERENCES: {period} ***")
            print(f"Pattern: {delta_list[:period]}")

def find_recurrence_mod_p(m_seq: Dict[int, int], p: int, order: int = 3):
    """Try to find recurrence relation m[n] = a*m[n-1] + b*m[n-2] + ... (mod p)"""

    print("\n" + "=" * 80)
    print(f"RECURRENCE RELATION SEARCH mod {p} (order {order})")
    print("=" * 80)

    residues = {n: m_seq[n] % p for n in m_seq.keys()}

    # Try to find coefficients for m[n] ≡ a1*m[n-1] + a2*m[n-2] + ... + c (mod p)
    n_values = sorted(residues.keys())

    if order == 2:
        # m[n] ≡ a*m[n-1] + b*m[n-2] + c (mod p)
        print(f"\nSearching for: m[n] ≡ a*m[n-1] + b*m[n-2] + c (mod {p})")

        for a in range(p):
            for b in range(p):
                for c in range(p):
                    valid = True
                    for i in range(2, min(len(n_values), 15)):
                        n = n_values[i]
                        n1 = n_values[i-1]
                        n2 = n_values[i-2]

                        predicted = (a * residues[n1] + b * residues[n2] + c) % p
                        if predicted != residues[n]:
                            valid = False
                            break

                    if valid:
                        print(f"\n*** FOUND: m[n] ≡ {a}*m[n-1] + {b}*m[n-2] + {c} (mod {p}) ***")

                        # Verify on more values
                        print(f"\nVerification:")
                        for i in range(2, min(len(n_values), 20)):
                            n = n_values[i]
                            n1 = n_values[i-1]
                            n2 = n_values[i-2]

                            predicted = (a * residues[n1] + b * residues[n2] + c) % p
                            actual = residues[n]
                            match = "✓" if predicted == actual else "✗"
                            print(f"n={n:2d}: predicted={predicted}, actual={actual} {match}")

                        return (a, b, c)

        print(f"\nNo order-2 recurrence found mod {p}")

    return None

def main():
    print("Loading m-sequence from database...")
    m_seq = load_m_sequence()

    print(f"\nLoaded {len(m_seq)} values: m[2] to m[{max(m_seq.keys())}]")
    print(f"First few values: {[(n, m_seq[n]) for n in sorted(m_seq.keys())[:5]]}")

    # Verify the special ratio
    if 3 in m_seq and 4 in m_seq:
        ratio = m_seq[4] / m_seq[3]
        pi_approx = 22 / 7
        print(f"\nVerifying m[4]/m[3] = {m_seq[4]}/{m_seq[3]} = {ratio:.10f}")
        print(f"22/7 = {pi_approx:.10f}")
        print(f"π     = {3.14159265359:.10f}")

    # Main analyses
    primes = [2, 3, 5, 7, 11, 13]

    print("\n" + "=" * 80)
    print("TASK 1-3: MODULAR PATTERNS FOR VARIOUS PRIMES")
    print("=" * 80)

    results = analyze_modular_patterns(m_seq, primes)

    print("\n" + "=" * 80)
    print("TASK 5: DEEP ANALYSIS OF mod 7 (SPECIAL)")
    print("=" * 80)

    q_seq, r_seq = analyze_mod7_deeply(m_seq)

    print("\n" + "=" * 80)
    print("TASK 4: CHINESE REMAINDER THEOREM")
    print("=" * 80)

    check_crt_reconstruction(m_seq, primes)

    print("\n" + "=" * 80)
    print("BONUS: DIFFERENCE ANALYSIS")
    print("=" * 80)

    analyze_differences_mod_p(m_seq, primes)

    print("\n" + "=" * 80)
    print("BONUS: RECURRENCE RELATION SEARCH")
    print("=" * 80)

    # Try to find recurrence relations for small primes
    for p in [2, 3, 5, 7]:
        find_recurrence_mod_p(m_seq, p, order=2)

    # Save results
    output = {
        'modular_analysis': {
            str(p): {
                'residues': {str(k): v for k, v in results[p]['residues'].items()},
                'period': results[p]['period'],
                'n_relation': results[p]['n_relation']
            }
            for p in primes
        },
        'mod7_decomposition': {
            'q_seq': {str(k): v for k, v in list(q_seq.items())[:25]},
            'r_seq': {str(k): v for k, v in list(r_seq.items())[:25]}
        }
    }

    output_path = '/home/solo/LA/m_modular_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 80}")
    print(f"Results saved to: {output_path}")
    print(f"{'=' * 80}")

    # Final summary
    print("\n" + "=" * 80)
    print("SUMMARY OF FINDINGS")
    print("=" * 80)

    print("\nKey patterns found:")
    for p in primes:
        print(f"\nmod {p}:")
        if results[p]['period']:
            print(f"  - Period: {results[p]['period']}")
        if results[p]['n_relation']:
            print(f"  - Relation: {results[p]['n_relation']}")
        if not results[p]['period'] and not results[p]['n_relation']:
            print(f"  - No simple pattern detected")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
