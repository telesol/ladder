#!/usr/bin/env python3
"""
Direct analysis of the adj_n sequence
Looking for patterns: recurrences, modular, GCD, prime factors
"""

import sqlite3
from math import gcd
from functools import reduce

def load_keys():
    conn = sqlite3.connect("db/kh.db")
    cur = conn.cursor()
    cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
    rows = cur.fetchall()
    conn.close()
    return {r[0]: int(r[1], 16) for r in rows}

def prime_factors(n):
    """Get prime factorization"""
    if n == 0:
        return {0: 1}
    factors = {}
    d = 2
    n_abs = abs(n)
    while d * d <= n_abs:
        while n_abs % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n_abs //= d
        d += 1
    if n_abs > 1:
        factors[n_abs] = factors.get(n_abs, 0) + 1
    return factors

def main():
    keys = load_keys()
    k = [0] + [keys.get(i, 0) for i in range(1, 71)]

    # Compute adj sequence
    adj = [0, 0]  # adj_0 and adj_1 don't exist in our formula
    for n in range(2, 71):
        adj.append(k[n] - 2 * k[n-1])

    print("=" * 70)
    print("ADJ SEQUENCE DIRECT ANALYSIS")
    print("=" * 70)

    # Print adj sequence
    print("\n=== adj_n values (n=2..30) ===")
    for n in range(2, 31):
        sign = "+" if adj[n] >= 0 else ""
        print(f"adj[{n:2d}] = {sign}{adj[n]:10d}")

    # Test 1: Is there a recurrence adj_n = c * adj_{n-1} + d?
    print("\n=== Test 1: Linear recurrence adj_n = a*adj_{n-1} + b ===")
    for n in range(4, 20):
        if adj[n-1] != 0:
            ratio = adj[n] / adj[n-1]
            diff = adj[n] - adj[n-1]
            print(f"n={n:2d}: adj[n]/adj[n-1] = {ratio:10.4f}, adj[n]-adj[n-1] = {diff:10d}")

    # Test 2: Check GCD patterns
    print("\n=== Test 2: GCD(adj_n, adj_{n-1}) ===")
    for n in range(3, 25):
        g = gcd(abs(adj[n]), abs(adj[n-1]))
        print(f"n={n:2d}: GCD(|{adj[n]:8d}|, |{adj[n-1]:8d}|) = {g}")

    # Test 3: Check mod patterns
    print("\n=== Test 3: adj_n mod small primes ===")
    for p in [2, 3, 5, 7]:
        print(f"\nadj_n mod {p}:")
        mods = [adj[n] % p for n in range(2, 31)]
        print(f"  {mods}")

    # Test 4: Sign pattern
    print("\n=== Test 4: Sign of adj_n ===")
    signs = []
    for n in range(2, 71):
        signs.append('+' if adj[n] >= 0 else '-')
    print("".join(signs))
    neg_count = signs.count('-')
    print(f"Negative count: {neg_count} / 69 = {neg_count/69*100:.1f}%")

    # Find which n have negative adj
    neg_n = [n for n in range(2, 71) if adj[n] < 0]
    print(f"Negative at n = {neg_n}")

    # Test 5: Prime factorization
    print("\n=== Test 5: Prime factorization of |adj_n| ===")
    for n in range(2, 20):
        pf = prime_factors(adj[n])
        print(f"n={n:2d}: |adj| = {abs(adj[n]):10d} = {pf}")

    # Test 6: Relationship to 2^n
    print("\n=== Test 6: adj_n relative to 2^n ===")
    for n in range(2, 25):
        two_n = 1 << n
        ratio = adj[n] / two_n
        in_range = two_n / 2 <= adj[n] <= two_n if adj[n] > 0 else -two_n <= adj[n] <= -two_n/2
        print(f"n={n:2d}: 2^n = {two_n:10d}, adj/2^n = {ratio:8.4f}, |adj| < 2^n: {abs(adj[n]) < two_n}")

    # Test 7: Check if adj follows any polynomial
    print("\n=== Test 7: Second differences (looking for polynomial) ===")
    first_diff = [adj[n] - adj[n-1] for n in range(3, 25)]
    second_diff = [first_diff[i] - first_diff[i-1] for i in range(1, len(first_diff))]
    print("First differences:", first_diff[:15])
    print("Second differences:", second_diff[:15])

    # Test 8: Check ratios to key values
    print("\n=== Test 8: adj_n / k_d relationships ===")
    for n in range(2, 15):
        for d in range(1, min(n, 9)):
            if k[d] != 0:
                ratio = adj[n] / k[d]
                if abs(ratio - round(ratio)) < 0.01:  # Nearly integer
                    print(f"n={n:2d}, d={d}: adj[n]/k[d] = {ratio:.4f} ≈ {round(ratio)}")

    # Test 9: Bit patterns
    print("\n=== Test 9: Bit patterns in adj_n ===")
    for n in range(2, 20):
        if adj[n] >= 0:
            bits = bin(adj[n])[2:]
            popcount = bits.count('1')
            print(f"n={n:2d}: adj = {adj[n]:10d} = 0b{bits:>20s}, popcount={popcount}")
        else:
            print(f"n={n:2d}: adj = {adj[n]:10d} (negative)")

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
