#!/usr/bin/env python3
"""
Correct Coprimality Test

Previous test had bug: reduce(gcd, list) finds GCD of ALL elements,
not whether one element is coprime with all others.
"""

import sqlite3
from pathlib import Path
from math import gcd

DB_PATH = Path(__file__).parent / "db" / "kh.db"

def load_k_values():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT puzzle_id, priv_hex FROM ground_truth WHERE priv_hex IS NOT NULL ORDER BY puzzle_id")
    rows = c.fetchall()
    conn.close()
    return {pid: int(phex, 16) for pid, phex in rows}

def is_coprime_with_all_previous(k, n):
    """Check if k[n] is coprime with ALL k[m] for m < n."""
    for m in range(1, n):
        if m in k:
            if gcd(k[n], k[m]) > 1:
                return False
    return True

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def factorize_small(n, max_factor=1000):
    """Find small prime factors."""
    factors = []
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if p > max_factor:
            break
        while n % p == 0:
            factors.append(p)
            n //= p
    if n > 1:
        factors.append(n)
    return factors

def main():
    k = load_k_values()
    print("="*70)
    print("CORRECT Coprimality Analysis")
    print("="*70)

    # Find truly coprime k values
    coprime_positions = []
    for n in sorted(k.keys()):
        if n <= 1:
            continue

        if is_coprime_with_all_previous(k, n):
            coprime_positions.append(n)
            print(f"k[{n:>3}] = {k[n]} is COPRIME with all previous")

    print(f"\nPositions coprime with all previous: {coprime_positions}")
    print(f"Total: {len(coprime_positions)}")

    # Pattern analysis
    if len(coprime_positions) > 1:
        diffs = [coprime_positions[i+1] - coprime_positions[i] for i in range(len(coprime_positions)-1)]
        print(f"Differences: {diffs}")

        # mod 3 pattern
        mod3 = [n % 3 for n in coprime_positions]
        print(f"n mod 3: {mod3}")

    # Show GCD structure for first 20 values
    print("\n" + "="*70)
    print("GCD Matrix (first 15 values)")
    print("="*70)

    print("    ", end="")
    for m in range(1, 16):
        print(f"{m:>6}", end="")
    print()

    for n in range(1, 16):
        if n not in k:
            continue
        print(f"{n:>3}:", end="")
        for m in range(1, 16):
            if m not in k or m >= n:
                print(f"{'':>6}", end="")
            else:
                g = gcd(k[n], k[m])
                print(f"{g:>6}", end="")
        print()

    # Factorization of early k values
    print("\n" + "="*70)
    print("Prime Factorizations (first 20)")
    print("="*70)

    for n in sorted(k.keys())[:20]:
        factors = factorize_small(k[n])
        print(f"k[{n:>2}] = {k[n]:>10} = {' × '.join(map(str, factors))}")

    # Check multiplicative relationships
    print("\n" + "="*70)
    print("Multiplicative Relationships")
    print("="*70)

    tests = [
        (5, 2, 3, '*'),    # k[5] = k[2] * k[3]?
        (6, 3, 3, '*'),    # k[6] = k[3] * k[3]?
        (8, 4, 3, '*'),    # k[8] = k[4] * k[3]?
        (10, 5, 2, '*'),   # k[10] = k[5] * k[2]?
        (11, 6, 5, '+'),   # k[11] = k[6] + some?
    ]

    for n, a, b, op in tests:
        if n in k and a in k and b in k:
            if op == '*':
                result = k[a] * k[b]
            else:
                result = k[a] + k[b]

            match = "MATCH" if k[n] == result else f"NO (actual={k[n]}, calc={result})"
            print(f"k[{n}] = k[{a}] {op} k[{b}] = {result}? {match}")

    # Deep dive on k[8]
    print("\n" + "="*70)
    print("Special Analysis: k[8] = 224")
    print("="*70)

    print(f"k[8] = 224 = 2^5 × 7 = 32 × k[3]")
    print(f"k[8] / k[3] = {k[8] / k[3]}")
    print(f"k[8] / k[4] = {k[8] / k[4]}")
    print(f"k[8] = k[4] × k[4] / k[2] - k[3] + 1 = {k[4] * k[4] // k[3] - k[3] + 1}")
    print(f"k[8] = 2 * k[7] + 2^8 - m[8]*k[d[8]]")
    # k[8] = 2*76 + 256 - m*k[d] = 152 + 256 - m*k[d] = 408 - m*k[d]
    # 224 = 408 - m*k[d]
    # m*k[d] = 184
    # If d=4, k[4]=8: m = 184/8 = 23
    print(f"Using d=4: m = (2*k[7] + 2^8 - k[8]) / k[4] = (152 + 256 - 224) / 8 = {(152 + 256 - 224) // 8}")

if __name__ == "__main__":
    main()
