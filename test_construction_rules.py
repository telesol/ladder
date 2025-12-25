#!/usr/bin/env python3
"""
Test Construction Rules

Based on our analysis, the construction appears to follow:
1. Bootstrap: k[1,2,3] = Mersenne (2^n - 1)
2. Multiplicative build: k[4,5,6,8] from products/powers
3. Prime resets at n ≡ 0 (mod 3) starting from n=9
4. k[11] = odd primorial (3×5×7×11)

Let's test if these rules predict the actual k values.
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

def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

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

def is_coprime_with_all(k, n):
    """Check if k[n] is coprime with all k[m] for m < n."""
    for m in range(1, n):
        if m in k and gcd(k[n], k[m]) > 1:
            return False
    return True

def main():
    k = load_k_values()

    print("="*70)
    print("TESTING CONSTRUCTION RULES")
    print("="*70)

    # Rule 1: n ≡ 0 (mod 3) positions (3, 6, 9, 12, 15, 18, ...)
    print("\n--- RULE: Positions n ≡ 0 (mod 3) ---")
    print("Hypothesis: These are special (prime or primorial)")
    print()

    mod3_zero = [n for n in sorted(k.keys())[:50] if n % 3 == 0]

    for n in mod3_zero:
        kn = k[n]
        prime = is_prime(kn)
        coprime = is_coprime_with_all(k, n)
        factors = factorize(kn)
        factor_str = ' × '.join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items()))

        status = []
        if prime:
            status.append("PRIME")
        if coprime:
            status.append("COPRIME_ALL")

        print(f"k[{n:>2}] = {kn:>15} = {factor_str:>25}  {', '.join(status) if status else 'composite'}")

    # Rule 2: Check if "coprime reset" happens at specific intervals
    print("\n--- COPRIME RESET POSITIONS ---")
    coprime_positions = []
    for n in sorted(k.keys()):
        if n > 1 and is_coprime_with_all(k, n):
            coprime_positions.append(n)

    print(f"Positions coprime with all previous: {coprime_positions[:20]}")

    if len(coprime_positions) > 1:
        # Check intervals
        intervals = [coprime_positions[i+1] - coprime_positions[i] for i in range(min(10, len(coprime_positions)-1))]
        print(f"Intervals: {intervals}")

    # Rule 3: Check n mod 3 for coprime positions
    print("\nMod 3 analysis of coprime positions:")
    mod3_dist = {0: [], 1: [], 2: []}
    for n in coprime_positions[:20]:
        mod3_dist[n % 3].append(n)

    for m in [0, 1, 2]:
        print(f"  n ≡ {m} (mod 3): {mod3_dist[m]}")

    # Rule 4: Analyze k[15] specifically
    print("\n--- SPECIAL ANALYSIS: k[15] ---")
    k15 = k[15]
    print(f"k[15] = {k15}")
    print(f"Is prime? {is_prime(k15)}")
    print(f"Is coprime with all previous? {is_coprime_with_all(k, 15)}")
    print(f"Factorization: {factorize(k15)}")

    # Check if 15 is a "reset" or "build"
    factors15 = factorize(k15)
    primes_before_15 = set()
    for m in range(1, 15):
        if m in k:
            primes_before_15.update(factorize(k[m]).keys())

    factors15_set = set(factors15.keys())
    new_primes_at_15 = factors15_set - primes_before_15

    print(f"Primes in k[1..14]: {sorted(primes_before_15)}")
    print(f"Primes in k[15]: {sorted(factors15_set)}")
    print(f"NEW primes at k[15]: {new_primes_at_15}")

    # Rule 5: Test the "construction from previous" hypothesis
    print("\n--- CONSTRUCTION HYPOTHESIS ---")
    print("Testing: Can k[n] be expressed using previous k values?")

    for n in range(4, 21):
        if n not in k:
            continue

        kn = k[n]

        # Try to find expression
        found = False

        # k[a] × k[b]
        for a in range(1, n):
            for b in range(a, n):
                if a in k and b in k and k[a] * k[b] == kn:
                    print(f"k[{n}] = k[{a}] × k[{b}] = {k[a]} × {k[b]}")
                    found = True

        # k[a]^p
        for a in range(1, n):
            if a in k:
                for p in range(2, 5):
                    if k[a] ** p == kn:
                        print(f"k[{n}] = k[{a}]^{p}")
                        found = True

        # 2^p × k[a]
        for a in range(1, n):
            if a in k:
                for p in range(1, 20):
                    if (1 << p) * k[a] == kn:
                        print(f"k[{n}] = 2^{p} × k[{a}]")
                        found = True
                    if (1 << p) * k[a] > kn:
                        break

        # Prime
        if is_prime(kn):
            print(f"k[{n}] = {kn} (PRIME)")
            found = True

        if not found:
            factors = factorize(kn)
            print(f"k[{n}] = {kn} = {factors} (NEW PRIMES)")

    # Summary table
    print("\n" + "="*70)
    print("CONSTRUCTION SUMMARY TABLE")
    print("="*70)

    print(f"\n{'n':>3} {'k[n]':>12} {'Type':>12} {'Pattern':>20}")
    print("-"*50)

    type_counts = {'MERSENNE': 0, 'POWER': 0, 'PRODUCT': 0, 'PRIME': 0, 'NEW': 0}

    for n in range(1, 21):
        if n not in k:
            continue

        kn = k[n]

        # Classify
        if n <= 3:
            ktype = "MERSENNE"
            pattern = f"2^{n} - 1"
        elif is_prime(kn):
            ktype = "PRIME"
            pattern = f"prime {kn}"
        elif n == 4:
            ktype = "POWER"
            pattern = "2^3"
        elif n == 5:
            ktype = "PRODUCT"
            pattern = "k[2] × k[3]"
        elif n == 6:
            ktype = "PRODUCT"
            pattern = "k[3]^2"
        elif n == 8:
            ktype = "POWER"
            pattern = "2^5 × k[3]"
        elif n == 11:
            ktype = "PRIMORIAL"
            pattern = "3×5×7×11 (P#5)"
        else:
            ktype = "NEW"
            pattern = str(factorize(kn))

        type_counts[ktype] = type_counts.get(ktype, 0) + 1
        print(f"{n:>3} {kn:>12} {ktype:>12} {pattern:>20}")

    print(f"\nType distribution: {type_counts}")

if __name__ == "__main__":
    main()
