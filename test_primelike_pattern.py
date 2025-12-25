#!/usr/bin/env python3
"""
Test: Prime-like k[n] Pattern

Observation from PRNG test: k[9], k[12], k[15] are coprime with ALL previous k values.
These are at n ≡ 0 (mod 3). Is this a consistent pattern?
"""

import sqlite3
from pathlib import Path
from math import gcd
from functools import reduce

DB_PATH = Path(__file__).parent / "db" / "kh.db"

def load_k_values():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT puzzle_id, priv_hex FROM ground_truth WHERE priv_hex IS NOT NULL ORDER BY puzzle_id")
    rows = c.fetchall()
    conn.close()
    return {pid: int(phex, 16) for pid, phex in rows}

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def gcd_with_all_previous(k, n):
    """Compute GCD of k[n] with all k[m] for m < n."""
    if n <= 1:
        return 1
    all_prev = [k[m] for m in range(1, n) if m in k]
    if not all_prev:
        return 1
    return reduce(gcd, all_prev + [k[n]])

def main():
    k = load_k_values()
    print("="*70)
    print("Analysis: Prime-like k[n] values (coprime with all previous)")
    print("="*70)

    # Find all prime-like k values
    primelike = []
    for n in sorted(k.keys()):
        if n <= 1:
            continue

        g = gcd_with_all_previous(k, n)

        if g == 1:
            is_prime_val = is_prime(k[n])
            primelike.append(n)
            print(f"k[{n:>3}] = {k[n]:>15} - COPRIME with all prev, is_prime={is_prime_val}")

    print(f"\nTotal prime-like: {len(primelike)}")
    print(f"Positions: {primelike}")

    # Check pattern
    print("\n" + "="*70)
    print("Pattern Analysis")
    print("="*70)

    # Check n mod 3
    mod3_dist = {0: 0, 1: 0, 2: 0}
    for n in primelike:
        mod3_dist[n % 3] += 1
    print(f"n mod 3 distribution: {mod3_dist}")

    # Check differences
    if len(primelike) > 1:
        diffs = [primelike[i+1] - primelike[i] for i in range(len(primelike)-1)]
        print(f"Consecutive differences: {diffs}")

    # Check which are actually prime
    print("\n" + "="*70)
    print("Primality of k[n] values")
    print("="*70)

    actual_primes = []
    for n in sorted(k.keys())[:40]:
        if is_prime(k[n]):
            actual_primes.append(n)
            print(f"k[{n}] = {k[n]} is PRIME")

    print(f"\nActual primes at positions: {actual_primes}")

    # Check factorizations of non-primelike k values
    print("\n" + "="*70)
    print("GCD Structure for non-coprime k[n]")
    print("="*70)

    for n in sorted(k.keys())[:30]:
        if n in primelike or n <= 1:
            continue

        g = gcd_with_all_previous(k, n)
        if g > 1:
            # Find which previous k[m] shares this factor
            shared_with = []
            for m in range(1, n):
                if m in k and gcd(k[n], k[m]) > 1:
                    shared_with.append((m, gcd(k[n], k[m])))
            print(f"k[{n:>2}] = {k[n]:>8}, GCD={g}, shares with: {shared_with}")

    # Key relationship patterns
    print("\n" + "="*70)
    print("Multiplicative Relationships")
    print("="*70)

    relationships = [
        (5, "k[2] * k[3]", k[2] * k[3]),
        (6, "k[3]^2", k[3] ** 2),
        (8, "2^3 * k[3]", 8 * k[3]),
        (11, "3 * 5 * 7 * 11", 3 * 5 * 7 * 11),
    ]

    for n, formula, expected in relationships:
        if n in k:
            match = "MATCH" if k[n] == expected else f"DIFF (actual={k[n]})"
            print(f"k[{n}] = {formula} = {expected}? {match}")

if __name__ == "__main__":
    main()
