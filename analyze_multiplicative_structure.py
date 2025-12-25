#!/usr/bin/env python3
"""
Deep Analysis of Multiplicative Structure

Goal: Understand why some k[n] are products of previous k values,
while others (like k[9], k[12]) introduce new primes.

Key questions:
1. Which k[n] can be expressed using only previous k values?
2. When do new primes get introduced?
3. Is there a pattern to prime "resets"?
4. Can we predict whether k[n] will be multiplicative or prime?
"""

import sqlite3
from pathlib import Path
from math import gcd
from collections import defaultdict
from functools import reduce

DB_PATH = Path(__file__).parent / "db" / "kh.db"

def load_k_values():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT puzzle_id, priv_hex FROM ground_truth WHERE priv_hex IS NOT NULL ORDER BY puzzle_id")
    rows = c.fetchall()
    conn.close()
    return {pid: int(phex, 16) for pid, phex in rows}

def prime_factors(n):
    """Return set of prime factors."""
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors

def factorize(n):
    """Return prime factorization as dict {prime: exponent}."""
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

def get_prime_pool(k, n):
    """Get all prime factors that appear in k[1..n-1]."""
    pool = set()
    for m in range(1, n):
        if m in k:
            pool.update(prime_factors(k[m]))
    return pool

def can_build_from_pool(value, prime_pool):
    """Check if value can be built using only primes from the pool."""
    factors = prime_factors(value)
    return factors.issubset(prime_pool)

def find_multiplicative_expression(k, n, max_terms=3):
    """
    Try to express k[n] as a product/power of previous k values.
    Returns list of expressions that work.
    """
    if n not in k:
        return []

    target = k[n]
    expressions = []

    # Check k[a] alone
    for a in range(1, n):
        if a in k and k[a] == target:
            expressions.append(f"k[{a}]")

    # Check k[a]^p
    for a in range(1, n):
        if a in k:
            for p in range(2, 10):
                if k[a] ** p == target:
                    expressions.append(f"k[{a}]^{p}")
                if k[a] ** p > target:
                    break

    # Check 2^p * k[a]
    for a in range(1, n):
        if a in k:
            for p in range(1, 20):
                if (1 << p) * k[a] == target:
                    expressions.append(f"2^{p} × k[{a}]")
                if (1 << p) * k[a] > target:
                    break

    # Check k[a] * k[b]
    for a in range(1, n):
        for b in range(a, n):
            if a in k and b in k:
                if k[a] * k[b] == target:
                    if a == b:
                        expressions.append(f"k[{a}]^2")
                    else:
                        expressions.append(f"k[{a}] × k[{b}]")

    # Check k[a] * k[b] * k[c]
    if max_terms >= 3:
        for a in range(1, n):
            for b in range(a, n):
                for c in range(b, n):
                    if a in k and b in k and c in k:
                        product = k[a] * k[b] * k[c]
                        if product == target:
                            expressions.append(f"k[{a}] × k[{b}] × k[{c}]")
                        if product > target * 10:
                            break

    return expressions

def analyze_structure():
    k = load_k_values()

    print("="*80)
    print("MULTIPLICATIVE STRUCTURE ANALYSIS")
    print("="*80)

    # Track prime pool evolution
    prime_pool = set()

    results = []

    print(f"\n{'n':>3} {'k[n]':>12} {'Type':>10} {'New Primes':>15} {'Expression':>25}")
    print("-"*80)

    for n in range(1, 31):
        if n not in k:
            continue

        kn = k[n]
        factors = prime_factors(kn)
        new_primes = factors - prime_pool

        # Find expressions
        expressions = find_multiplicative_expression(k, n)

        # Classify
        if is_prime(kn):
            ktype = "PRIME"
        elif can_build_from_pool(kn, prime_pool):
            ktype = "COMPOSITE"
        else:
            ktype = "NEW_PRIME"

        # Best expression
        expr = expressions[0] if expressions else "-"
        new_str = str(new_primes) if new_primes else "-"

        results.append({
            'n': n,
            'k': kn,
            'type': ktype,
            'new_primes': new_primes,
            'expressions': expressions,
            'prime_pool_before': prime_pool.copy()
        })

        print(f"{n:>3} {kn:>12} {ktype:>10} {new_str:>15} {expr:>25}")

        # Update pool
        prime_pool.update(factors)

    # Analysis
    print("\n" + "="*80)
    print("PATTERN ANALYSIS")
    print("="*80)

    # Group by type
    primes = [r for r in results if r['type'] == 'PRIME']
    composites = [r for r in results if r['type'] == 'COMPOSITE']
    new_prime_intro = [r for r in results if r['type'] == 'NEW_PRIME']

    print(f"\nPRIME k values (entirely new): {[r['n'] for r in primes]}")
    print(f"COMPOSITE k values (built from pool): {[r['n'] for r in composites]}")
    print(f"NEW_PRIME intro (adds new prime factor): {[r['n'] for r in new_prime_intro]}")

    # Prime introduction pattern
    print("\n" + "-"*80)
    print("PRIME INTRODUCTION TIMELINE")
    print("-"*80)

    all_primes_seen = {}
    for r in results:
        for p in r['new_primes']:
            if p not in all_primes_seen:
                all_primes_seen[p] = r['n']

    for p in sorted(all_primes_seen.keys()):
        n = all_primes_seen[p]
        print(f"  Prime {p:>5} first appears at n={n}")

    # Check intervals between pure primes
    print("\n" + "-"*80)
    print("INTERVALS BETWEEN PRIME k VALUES")
    print("-"*80)

    prime_positions = [r['n'] for r in primes]
    if len(prime_positions) > 1:
        intervals = [prime_positions[i+1] - prime_positions[i] for i in range(len(prime_positions)-1)]
        print(f"Prime positions: {prime_positions}")
        print(f"Intervals: {intervals}")

    # Analyze what determines multiplicative vs prime
    print("\n" + "-"*80)
    print("MULTIPLICATIVE EXPRESSIONS (all found)")
    print("-"*80)

    for r in results:
        if r['expressions']:
            print(f"\nk[{r['n']}] = {r['k']}")
            for expr in r['expressions']:
                print(f"    = {expr}")

    # Check if primes appear at specific positions
    print("\n" + "-"*80)
    print("POSITION ANALYSIS")
    print("-"*80)

    print("\nn mod 3 for PRIME k values:")
    for r in primes:
        print(f"  n={r['n']}: n mod 3 = {r['n'] % 3}")

    print("\nn mod 3 for COMPOSITE k values:")
    mod3_count = {0: 0, 1: 0, 2: 0}
    for r in composites:
        mod3_count[r['n'] % 3] += 1
    print(f"  Distribution: {mod3_count}")

    return results

def analyze_construction_rules():
    """
    Analyze what rules might govern construction.
    """
    k = load_k_values()

    print("\n" + "="*80)
    print("CONSTRUCTION RULES ANALYSIS")
    print("="*80)

    # For each composite k[n], find the "simplest" construction
    print("\nSimplest construction for each k[n]:")
    print("-"*80)

    constructions = {}

    for n in range(4, 21):
        if n not in k:
            continue

        kn = k[n]
        expressions = find_multiplicative_expression(k, n)

        if expressions:
            # Score by complexity (fewer terms = simpler)
            def complexity(expr):
                if '^' in expr and '×' not in expr:
                    return 1  # Pure power
                elif '×' not in expr:
                    return 2  # Single reference
                else:
                    return expr.count('×') + 2  # Product

            expressions.sort(key=complexity)
            simplest = expressions[0]
            constructions[n] = simplest
            print(f"  k[{n}] = {simplest}")
        else:
            print(f"  k[{n}] = {kn} (no simple expression - introduces new primes)")

    # Check if there's a pattern in construction choices
    print("\n" + "-"*80)
    print("CONSTRUCTION CHOICE ANALYSIS")
    print("-"*80)

    print("\nk values that are SQUARES of previous:")
    for n, expr in constructions.items():
        if '^2' in expr or ('^' in expr and '×' not in expr):
            print(f"  k[{n}] = {expr}")

    print("\nk values that are PRODUCTS of two previous:")
    for n, expr in constructions.items():
        if '×' in expr and expr.count('×') == 1 and '^' not in expr:
            print(f"  k[{n}] = {expr}")

    print("\nk values that are POWER_OF_2 times previous:")
    for n, expr in constructions.items():
        if expr.startswith('2^'):
            print(f"  k[{n}] = {expr}")

def main():
    results = analyze_structure()
    analyze_construction_rules()

    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)
    print("""
    1. BOOTSTRAP (n=1,2,3): Mersenne primes 2^n-1
       k[1]=1, k[2]=3, k[3]=7

    2. MULTIPLICATIVE PHASE (n=4-8):
       - k[4] = 2³ (power of 2)
       - k[5] = k[2] × k[3] (product of bootstraps)
       - k[6] = k[3]² (square)
       - k[7] introduces NEW prime 19
       - k[8] = 2⁵ × k[3] (power × bootstrap)

    3. PRIME RESET (n=9):
       - k[9] = 467 is PRIME
       - Coprime with everything before
       - "Resets" the multiplicative chain

    4. PATTERN CONTINUES:
       - Mix of multiplicative and new-prime introductions
       - k[12] = 2683 is next PRIME reset

    HYPOTHESIS: The ladder alternates between:
       a) Building from existing primes (multiplicative)
       b) Introducing new primes when needed
       c) Periodic PRIME resets (coprime with all previous)
    """)

if __name__ == "__main__":
    main()
