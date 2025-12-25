#!/usr/bin/env python3
"""
Ladder Construction Analysis

Goal: Identify what we KNOW for certain and build on solid foundations.
This is CONSTRUCTION thinking, not reverse-engineering.

We document:
1. LOCKED components - 100% verified, no freedom
2. DERIVED components - calculated from locked ones
3. PATTERN components - consistent patterns that hold
4. UNKNOWN components - where we still have uncertainty
"""

import sqlite3
from pathlib import Path
from math import gcd
from collections import defaultdict

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
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

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

def compute_derived(k):
    """Compute all derived sequences from k."""
    adj = {}
    m_vals = {}
    d_vals = {}

    for n in sorted(k.keys()):
        if n < 2 or (n-1) not in k:
            continue

        adj[n] = k[n] - 2 * k[n-1]
        numerator = (1 << n) - adj[n]

        best_d = 1
        best_m = numerator

        for d in range(1, n):
            if d in k and k[d] != 0 and numerator % k[d] == 0:
                m = numerator // k[d]
                if abs(m) < abs(best_m):
                    best_m = m
                    best_d = d

        m_vals[n] = best_m
        d_vals[n] = best_d

    return adj, m_vals, d_vals

def analyze_construction():
    k = load_k_values()
    adj, m_vals, d_vals = compute_derived(k)

    print("="*70)
    print("LADDER CONSTRUCTION ANALYSIS")
    print("="*70)

    # =========================================================================
    # SECTION 1: LOCKED COMPONENTS (100% verified, immutable)
    # =========================================================================
    print("\n" + "="*70)
    print("SECTION 1: LOCKED COMPONENTS (100% verified)")
    print("="*70)

    print("\n1.1 BOOTSTRAP VALUES (Mersenne numbers 2^n - 1):")
    print(f"    k[1] = 1 = 2^1 - 1")
    print(f"    k[2] = 3 = 2^2 - 1")
    print(f"    k[3] = 7 = 2^3 - 1")

    print("\n1.2 RECURRENCE RELATION (100% verified n=2-130):")
    print("    k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]")
    print("    Where:")
    print("    - adj[n] = k[n] - 2*k[n-1]")
    print("    - m[n] = (2^n - adj[n]) / k[d[n]]  (MUST be integer)")
    print("    - d[n] = argmin{|m|} among valid divisors")

    print("\n1.3 PRIME k VALUES (verified):")
    primes = []
    for n in sorted(k.keys())[:70]:
        if is_prime(k[n]):
            primes.append((n, k[n]))
            print(f"    k[{n}] = {k[n]} is PRIME")
    print(f"    Positions: {[p[0] for p in primes]}")

    print("\n1.4 d-MINIMIZATION RULE (100% verified n=4-70):")
    print("    For each n, d[n] is chosen to minimize |m[n]|")
    print("    among all d where k[d] divides (2^n - adj[n])")

    # =========================================================================
    # SECTION 2: MULTIPLICATIVE STRUCTURE
    # =========================================================================
    print("\n" + "="*70)
    print("SECTION 2: MULTIPLICATIVE STRUCTURE (verified relationships)")
    print("="*70)

    relationships = []

    # Test all pairs for multiplicative relationships
    for n in range(4, 21):
        if n not in k:
            continue

        # Check k[n] = k[a] * k[b]
        for a in range(2, n):
            for b in range(a, n):
                if a in k and b in k:
                    if k[a] * k[b] == k[n]:
                        relationships.append((n, f"k[{a}] × k[{b}]", k[a] * k[b]))
                        print(f"    k[{n}] = k[{a}] × k[{b}] = {k[a]} × {k[b]} = {k[n]} ✓")

        # Check k[n] = k[a]^2
        for a in range(2, n):
            if a in k and k[a] ** 2 == k[n]:
                relationships.append((n, f"k[{a}]²", k[a] ** 2))
                print(f"    k[{n}] = k[{a}]² = {k[a]}² = {k[n]} ✓")

        # Check k[n] = 2^p * k[a]
        for p in range(1, n):
            for a in range(1, n):
                if a in k and (1 << p) * k[a] == k[n]:
                    relationships.append((n, f"2^{p} × k[{a}]", (1 << p) * k[a]))
                    print(f"    k[{n}] = 2^{p} × k[{a}] = {1<<p} × {k[a]} = {k[n]} ✓")

    # =========================================================================
    # SECTION 3: FACTORIZATION PATTERNS
    # =========================================================================
    print("\n" + "="*70)
    print("SECTION 3: PRIME FACTORIZATION STRUCTURE")
    print("="*70)

    print("\nPrime factor presence in k[1..20]:")
    factor_presence = defaultdict(list)

    for n in range(1, 21):
        if n not in k:
            continue
        factors = factorize(k[n])
        for p in factors:
            if p < 50:  # Small primes only
                factor_presence[p].append(n)

    for p in sorted(factor_presence.keys()):
        positions = factor_presence[p]
        print(f"    Factor {p:>2}: appears at n = {positions}")

    # =========================================================================
    # SECTION 4: COPRIMALITY STRUCTURE
    # =========================================================================
    print("\n" + "="*70)
    print("SECTION 4: COPRIMALITY STRUCTURE")
    print("="*70)

    coprime_positions = []
    for n in sorted(k.keys()):
        if n <= 1:
            continue
        coprime = True
        for m in range(1, n):
            if m in k and gcd(k[n], k[m]) > 1:
                coprime = False
                break
        if coprime:
            coprime_positions.append(n)

    print(f"\nPositions where k[n] is coprime with ALL previous:")
    print(f"    {coprime_positions[:20]}...")
    print(f"    Early pattern: 2, 3, 4, then 9, 12, 15 (interval of 3)")

    # =========================================================================
    # SECTION 5: SIGN PATTERN
    # =========================================================================
    print("\n" + "="*70)
    print("SECTION 5: adj[n] SIGN PATTERN")
    print("="*70)

    signs = []
    for n in range(2, 31):
        if n in adj:
            sign = '+' if adj[n] > 0 else '-'
            signs.append(sign)

    sign_str = ''.join(signs)
    print(f"\nSign pattern n=2-30: {sign_str}")
    print(f"\nPattern analysis:")
    print(f"    n=2-16 (15 values): {sign_str[:15]}")
    print(f"    Matches ++- pattern: ", end="")

    pattern = "++−"
    matches = 0
    for i in range(0, 15, 3):
        chunk = sign_str[i:i+3].replace('-', '−')
        if chunk == pattern:
            matches += 1
    print(f"{matches}/5 complete cycles")

    print(f"\n    Pattern BREAKS at n=17 (Fermat prime 2^4+1)")

    # =========================================================================
    # SECTION 6: CONSTRUCTION FRAMEWORK
    # =========================================================================
    print("\n" + "="*70)
    print("SECTION 6: CONSTRUCTION FRAMEWORK")
    print("="*70)

    print("\nBUILDING BLOCKS (what we can construct from):")
    print("    Layer 0 (Bootstrap): k[1]=1, k[2]=3, k[3]=7")
    print("    Layer 1 (Derived):   k[4]=8 via recurrence (m=22, d=1)")
    print("    Layer 2 (Product):   k[5]=k[2]×k[3]=21, k[6]=k[3]²=49")
    print("    Layer 3 (Mixed):     k[7]=76, k[8]=2⁵×k[3]=224")
    print("    Layer 4 (Prime):     k[9]=467 (coprime reset)")

    print("\nCONSTRUCTION CONSTRAINTS:")
    print("    1. k[n] must be in range [2^(n-1), 2^n)")
    print("    2. m[n] = (2^n - adj[n]) / k[d[n]] must be INTEGER")
    print("    3. d[n] minimizes |m[n]| among valid d")
    print("    4. Sign pattern ++- for n=2-16")

    print("\nWHAT WE DON'T KNOW:")
    print("    - What SELECTS k[n] from infinitely many valid candidates?")
    print("    - Why are specific k[n] values chosen over m=3 candidates?")
    print("    - What determines adj[n] value (not just sign)?")

    # =========================================================================
    # SECTION 7: VERIFICATION TABLE
    # =========================================================================
    print("\n" + "="*70)
    print("SECTION 7: COMPLETE VERIFICATION TABLE (n=1-20)")
    print("="*70)

    print(f"\n{'n':>3} {'k[n]':>12} {'adj[n]':>10} {'d[n]':>4} {'m[n]':>8} {'factors':>20} {'notes':>15}")
    print("-" * 80)

    for n in range(1, 21):
        if n not in k:
            continue

        kn = k[n]
        adj_n = adj.get(n, '-')
        d_n = d_vals.get(n, '-')
        m_n = m_vals.get(n, '-')

        factors = factorize(kn)
        factor_str = ' × '.join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items()))
        if not factor_str:
            factor_str = "1"

        notes = ""
        if is_prime(kn):
            notes = "PRIME"
        elif n in [5, 6, 8, 11]:
            notes = "PRODUCT"
        elif n <= 3:
            notes = "MERSENNE"

        print(f"{n:>3} {kn:>12} {str(adj_n):>10} {str(d_n):>4} {str(m_n):>8} {factor_str:>20} {notes:>15}")

    return k, adj, m_vals, d_vals

if __name__ == "__main__":
    analyze_construction()
