#!/usr/bin/env python3
"""
Test: Are k[n] values selected based on multiplicative relationships?

Known multiplicative patterns:
- k[5] = k[2] * k[3] = 3 × 7 = 21
- k[6] = k[3]² = 7² = 49
- k[8] = 2⁵ * k[3] = 32 × 7 = 224
- k[11] = 3 × 5 × 7 × 11 = 1155

Question: Is k[n] always expressible as a product/power of previous k values?
"""

import sqlite3
from itertools import combinations_with_replacement

DB_PATH = "/home/rkh/ladder/db/kh.db"

def load_k_values():
    """Load actual k values from database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT puzzle_id, priv_hex
        FROM ground_truth
        WHERE priv_hex IS NOT NULL
        ORDER BY puzzle_id
    """)
    rows = c.fetchall()
    conn.close()
    k = {}
    for puzzle_id, priv_hex in rows:
        if priv_hex.startswith('0x'):
            k[puzzle_id] = int(priv_hex, 16)
        else:
            k[puzzle_id] = int(priv_hex, 16)
    return k

def factorize_in_terms_of_k(k, n, max_factors=4):
    """
    Try to express k[n] as product of previous k values and powers of 2.
    Returns (factors, power_of_2) if found, None otherwise.
    """
    target = k[n]
    available = [(i, k[i]) for i in range(1, n)]

    # Try products of 1, 2, 3, 4 k-values
    for num_factors in range(1, max_factors + 1):
        for combo in combinations_with_replacement(available, num_factors):
            product = 1
            for _, val in combo:
                product *= val

            # Check if target = product
            if product == target:
                indices = [i for i, _ in combo]
                return (indices, 0, "direct product")

            # Check if target = product * 2^p for some p
            if target % product == 0:
                ratio = target // product
                # Check if ratio is a power of 2
                if ratio > 0 and (ratio & (ratio - 1)) == 0:
                    p = ratio.bit_length() - 1
                    if p <= 20:  # Reasonable power
                        indices = [i for i, _ in combo]
                        return (indices, p, "product with 2^" + str(p))

            # Check if target = product / 2^p for some p
            for p in range(1, 10):
                if product % (2**p) == 0 and product // (2**p) == target:
                    indices = [i for i, _ in combo]
                    return (indices, -p, "product / 2^" + str(p))

    return None

def find_divisor_chain(k, n):
    """
    Check if k[n] is divisible by any previous k[i].
    """
    divisors = []
    for i in range(2, n):  # Skip k[1]=1
        if k[n] % k[i] == 0:
            quotient = k[n] // k[i]
            divisors.append((i, k[i], quotient))
    return divisors

def main():
    k = load_k_values()
    print(f"Loaded {len(k)} k values")
    print(f"k[1..15]: {[k.get(i) for i in range(1, 16)]}")
    print()

    print("=== Multiplicative Structure Analysis ===\n")

    for n in range(4, min(31, max(k.keys()) + 1)):
        if n not in k:
            continue

        print(f"n={n}: k[{n}] = {k[n]}")

        # Find factorization
        result = factorize_in_terms_of_k(k, n)
        if result:
            indices, p, desc = result
            formula = " × ".join([f"k[{i}]" for i in indices])
            if p > 0:
                formula = f"2^{p} × {formula}"
            elif p < 0:
                formula = f"{formula} / 2^{-p}"
            print(f"  = {formula} ({desc})")
        else:
            # Find divisors
            divisors = find_divisor_chain(k, n)
            if divisors:
                print(f"  Divisible by: {[(f'k[{i}]={ki}', f'quotient={q}') for i, ki, q in divisors[:5]]}")
            else:
                print(f"  No simple multiplicative structure found")

        print()

    # Summary: Count how many have multiplicative structure
    print("\n=== Summary ===")
    count_mult = 0
    count_divisible = 0
    for n in range(4, min(31, max(k.keys()) + 1)):
        if n not in k:
            continue
        result = factorize_in_terms_of_k(k, n)
        if result:
            count_mult += 1
        elif find_divisor_chain(k, n):
            count_divisible += 1

    total = min(30, max(k.keys())) - 3
    print(f"Has exact multiplicative formula: {count_mult}/{total}")
    print(f"Divisible by some k[i]: {count_divisible}/{total}")
    print(f"No clear structure: {total - count_mult - count_divisible}/{total}")

if __name__ == "__main__":
    main()
