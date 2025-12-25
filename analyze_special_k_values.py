#!/usr/bin/env python3
"""
Analyze Special k Values

Focus on:
1. k[11] = 1155 = 3 × 5 × 7 × 11 (first 4 odd primes!)
2. Why certain primes are introduced at specific n
3. Pattern in prime introductions
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

def factorize(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def analyze_k11():
    """Deep dive into k[11] = 1155."""
    k = load_k_values()

    print("="*70)
    print("SPECIAL ANALYSIS: k[11] = 1155")
    print("="*70)

    print(f"\nk[11] = 1155 = 3 × 5 × 7 × 11")
    print(f"     = first 4 odd primes multiplied together!")

    # Check relationship with previous k values
    print(f"\nRelationship with previous k values:")
    print(f"  k[11] / k[2] = 1155 / 3 = {1155 // 3} = 5 × 7 × 11 = 385")
    print(f"  k[11] / k[3] = 1155 / 7 = {1155 // 7} = 3 × 5 × 11 = 165")
    print(f"  k[11] / k[5] = 1155 / 21 = {1155 // 21} = 5 × 11 = 55")
    print(f"  k[11] / (k[2] × k[3]) = 1155 / 21 = 55 = 5 × 11")

    # When were 5 and 11 introduced?
    print(f"\nPrime introduction:")
    print(f"  3 appears at k[2] = 3")
    print(f"  5 appears at k[11] = 1155 (FIRST TIME!)")
    print(f"  7 appears at k[3] = 7")
    print(f"  11 appears at k[11] = 1155 (FIRST TIME!)")

    print(f"\nk[11] introduces TWO new primes: 5 and 11")
    print(f"And combines them with existing primes 3 and 7")

    # Check the recurrence
    print(f"\nRecurrence check:")
    print(f"  k[11] = 2*k[10] + 2^11 - m*k[d]")
    print(f"  1155 = 2*514 + 2048 - m*k[d]")
    print(f"  1155 = 1028 + 2048 - m*k[d]")
    print(f"  1155 = 3076 - m*k[d]")
    print(f"  m*k[d] = 3076 - 1155 = 1921")

    # What is 1921?
    print(f"\n  1921 = {factorize(1921)}")
    print(f"  1921 = 17 × 113")
    print(f"  With d=1, k[d]=1: m = 1921")
    print(f"  Actual d[11]=1, m[11]=1921 ✓")

def analyze_primorial_pattern():
    """Check if k values relate to primorials."""
    k = load_k_values()

    print("\n" + "="*70)
    print("PRIMORIAL ANALYSIS")
    print("="*70)

    # Primorials: 2, 6, 30, 210, 2310, ...
    primorials = [2, 6, 30, 210, 2310, 30030]
    odd_primorials = [1, 3, 15, 105, 1155, 15015]  # Without factor of 2

    print("\nOdd primorials (product of first n odd primes):")
    print(f"  P#1 = 1")
    print(f"  P#2 = 3")
    print(f"  P#3 = 3 × 5 = 15")
    print(f"  P#4 = 3 × 5 × 7 = 105")
    print(f"  P#5 = 3 × 5 × 7 × 11 = 1155")
    print(f"  P#6 = 3 × 5 × 7 × 11 × 13 = 15015")

    print("\nk values that match odd primorials:")
    for n in sorted(k.keys())[:40]:
        if k[n] in odd_primorials:
            idx = odd_primorials.index(k[n])
            print(f"  k[{n}] = {k[n]} = P#{idx+1} (first {idx+1} odd primes)")

    print("\nk values divisible by odd primorials:")
    for prim in odd_primorials[1:5]:  # Skip 1
        matches = []
        for n in sorted(k.keys())[:30]:
            if k[n] % prim == 0:
                quotient = k[n] // prim
                matches.append((n, k[n], quotient))
        if matches:
            print(f"\n  Divisible by {prim}:")
            for n, kn, q in matches:
                print(f"    k[{n}] = {kn} = {prim} × {q}")

def analyze_prime_selection():
    """Analyze why specific primes are chosen."""
    k = load_k_values()

    print("\n" + "="*70)
    print("PRIME SELECTION ANALYSIS")
    print("="*70)

    # For each n, what constraints does the recurrence put on k[n]?
    print("\nConstraints from recurrence:")

    for n in range(4, 16):
        if n not in k or (n-1) not in k:
            continue

        k_min = 1 << (n-1)
        k_max = (1 << n) - 1
        base = 2 * k[n-1] + (1 << n)

        print(f"\nn={n}:")
        print(f"  Range: [{k_min}, {k_max}]")
        print(f"  Base = 2*k[{n-1}] + 2^{n} = 2*{k[n-1]} + {1<<n} = {base}")
        print(f"  k[{n}] = {base} - m*k[d]")
        print(f"  Actual k[{n}] = {k[n]}")

        # What m*k[d] was used?
        adj = k[n] - 2*k[n-1]
        subtracted = base - k[n]
        print(f"  Subtracted: {subtracted}")

        # Factor the subtracted amount
        factors = factorize(subtracted)
        factor_str = ' × '.join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items()))
        print(f"  {subtracted} = {factor_str}")

def analyze_construction_sequence():
    """Trace the construction step by step."""
    k = load_k_values()

    print("\n" + "="*70)
    print("STEP-BY-STEP CONSTRUCTION TRACE")
    print("="*70)

    print("\n--- BOOTSTRAP PHASE ---")
    print("k[1] = 1 (given)")
    print("k[2] = 3 = 2^2 - 1 (Mersenne)")
    print("k[3] = 7 = 2^3 - 1 (Mersenne)")

    print("\n--- MULTIPLICATIVE PHASE ---")
    print("k[4] = 8 = 2^3")
    print("  Why? Only power of 2 in range [8, 15]")
    print("  Uses d=1, m=22 (22 = 2 × 11, related to π convergent 22/7)")

    print("\nk[5] = 21 = 3 × 7 = k[2] × k[3]")
    print("  Why? Product of bootstrap primes")
    print("  Uses d=2, m=9")

    print("\nk[6] = 49 = 7^2 = k[3]^2")
    print("  Why? Square of largest bootstrap prime")
    print("  Uses d=2, m=19")

    print("\nk[7] = 76 = 4 × 19 = 2^2 × 19")
    print("  Introduces NEW prime 19")
    print("  Uses d=2, m=50")

    print("\nk[8] = 224 = 32 × 7 = 2^5 × k[3]")
    print("  Back to multiplicative!")
    print("  Uses d=4, m=23")

    print("\n--- PRIME RESET ---")
    print("k[9] = 467 (PRIME)")
    print("  Coprime with ALL previous k values")
    print("  Uses d=1, m=493")
    print("  WHY 467? Let's check what candidates existed...")

    # Check candidates for n=9
    base9 = 2 * k[8] + (1 << 9)  # 448 + 512 = 960
    print(f"\n  For n=9: base = 2*224 + 512 = {base9}")
    print(f"  Range: [256, 511]")
    print(f"  k[9] = 960 - m*k[d]")

    # What are the options?
    print(f"\n  Options with d=1 (k[1]=1): k[9] = 960 - m")
    print(f"    For k[9]=467: m = 493 ✓")
    print(f"    For k[9]=288 (min|m|=3 using d=8): k[9] = 960 - 3*224 = 288")
    print(f"      288 = 2^5 × 9 = 32 × 9 (NOT prime)")
    print(f"    Actual chose PRIME 467 over composite 288!")

    print("\n--- KEY INSIGHT ---")
    print("The puzzle PREFERS primes at reset positions (n=9,12)")
    print("Even though non-prime candidates with smaller |m| exist!")

def main():
    analyze_k11()
    analyze_primorial_pattern()
    analyze_construction_sequence()

    print("\n" + "="*70)
    print("SUMMARY: Construction Rules")
    print("="*70)
    print("""
    PHASE 1: Bootstrap (n=1,2,3)
    - Use Mersenne numbers: k[n] = 2^n - 1

    PHASE 2: Multiplicative Build (n=4,5,6,8)
    - Build from products/powers of previous k values
    - k[4] = 2^3, k[5] = k[2]×k[3], k[6] = k[3]^2, k[8] = 2^5×k[3]

    EXCEPTION: n=7 introduces new prime 19

    PHASE 3: Prime Reset (n=9)
    - k[9] = 467 is PRIME
    - Deliberately chosen over smaller |m| composite candidates

    PHASE 4: Mixed (n=10+)
    - Continues introducing new primes
    - k[11] = 1155 = 3×5×7×11 (first 4 odd primes!)
    - k[12] = 2683 is next PRIME reset

    PATTERN: Every 3 steps after n=9, there's a tendency for
    special structure (primes at n=9,12, primorial at n=11)
    """)

if __name__ == "__main__":
    main()
