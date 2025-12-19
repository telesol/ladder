#!/usr/bin/env python3
"""
Extend formula derivation to n=36-70 (the gap).
This covers the range not yet analyzed by other Claude instances.

Key findings from previous analysis:
- m-sequence values come from continued fraction convergents
- Constants: π, e, √2, √3, φ, ln(2), √5, ln(3), γ
- Operations: direct, product, sum, difference, triple sum
- Self-reference: m[n] divides m[n + m[n]] (50% success rate)
- 17-network: p[7]=17 forms connected subgraph
"""

import json
import sympy
from sympy import factorint, isprime, primepi
from pathlib import Path
from math import gcd
from collections import defaultdict

# Load data
DATA_PATH = Path('/home/rkh/ladder/data_for_csolver.json')
with open(DATA_PATH, 'r') as f:
    data = json.load(f)

M_SEQ = data['m_seq']  # 69 values for n=2 to n=70
D_SEQ = data['d_seq']

def m(n):
    """Get m[n] value (n=2 to 70)"""
    if n < 2 or n > 70:
        return None
    return M_SEQ[n - 2]

def d(n):
    """Get d[n] value (n=2 to 70)"""
    if n < 2 or n > 70:
        return None
    return D_SEQ[n - 2]

def get_prime_index(p):
    """Get 1-indexed position of prime (p[1]=2, p[2]=3, ...)"""
    if not isprime(p):
        return None
    return primepi(p)

def factor_m(n):
    """Get factorization of m[n]"""
    val = m(n)
    if val is None or val < 2:
        return {}
    return factorint(val)

def print_header(title):
    print("\n" + "="*80)
    print(title)
    print("="*80)

def analyze_n36_to_n70():
    """Comprehensive analysis of n=36 to n=70."""

    print_header("EXTENDING ANALYSIS TO n=36-70")
    print("\nThis is the GAP where others aren't looking.")
    print("Previous analysis covered n=2 to n=35.")

    # Basic data dump
    print_header("RAW DATA: n=36 to n=70")
    print(f"{'n':>3} {'m[n]':>18} {'d[n]':>5} {'Factorization':>40}")
    print("-" * 80)

    for n in range(36, 71):
        mn = m(n)
        dn = d(n)
        factors = factor_m(n)

        if factors:
            factor_str = ' × '.join([
                f"{p}^{e}" if e > 1 else str(p)
                for p, e in sorted(factors.items())
            ])
        else:
            factor_str = str(mn)

        print(f"{n:3} {mn:>18} {dn:>5} {factor_str:>40}")

    # D-sequence analysis for this range
    print_header("D-SEQUENCE DISTRIBUTION (n=36-70)")
    d_counts = defaultdict(list)
    for n in range(36, 71):
        d_counts[d(n)].append(n)

    for d_val in sorted(d_counts.keys()):
        ns = d_counts[d_val]
        print(f"d={d_val}: {len(ns)} occurrences at n={ns[:10]}{'...' if len(ns) > 10 else ''}")

    # Check for 17-network extension
    print_header("17-NETWORK EXTENSION (n=36-70)")
    print("Looking for m-values divisible by 17...")

    network_17 = []
    for n in range(36, 71):
        factors = factor_m(n)
        if 17 in factors:
            mn = m(n)
            quotient = mn // 17
            network_17.append((n, mn, factors[17], quotient))
            print(f"  m[{n}] = {mn} = 17^{factors[17]} × {quotient}")

    if network_17:
        print(f"\n17 appears in {len(network_17)} values (n=36-70)")
        print("Complete 17-network: n =", [9, 11, 12, 24] + [x[0] for x in network_17])

    # Self-reference test
    print_header("SELF-REFERENCE TEST (n=36-70)")
    print("Testing: Does m[n] divide m[n + m[n]]?")
    print("(Most targets will be out of range, but some early ones may work)")

    for n in range(36, 71):
        mn = m(n)
        target_n = n + mn
        target_m = m(target_n)

        if target_m is None:
            continue  # Out of range

        if mn > 0 and target_m % mn == 0:
            quotient = target_m // mn
            print(f"  ✓ m[{n}]={mn} divides m[{target_n}]={target_m} (quotient={quotient})")

    # GCD analysis
    print_header("GCD ANALYSIS (n=36-70)")
    print("Looking for non-trivial GCD relationships...")

    gcd_pairs = []
    for i in range(36, 71):
        for j in range(i+1, min(i+10, 71)):  # Check nearby values
            mi, mj = m(i), m(j)
            g = gcd(mi, mj)
            if g > 10:  # Only significant GCDs
                gcd_pairs.append((i, j, g))

    gcd_pairs.sort(key=lambda x: -x[2])  # Sort by GCD descending
    print("\nTop GCD pairs:")
    for i, j, g in gcd_pairs[:15]:
        print(f"  gcd(m[{i}], m[{j}]) = {g}")

    # Prime frequency
    print_header("PRIME FREQUENCY (n=36-70)")
    prime_counts = defaultdict(int)

    for n in range(36, 71):
        factors = factor_m(n)
        for p in factors:
            prime_counts[p] += 1

    sorted_primes = sorted(prime_counts.items(), key=lambda x: -x[1])[:15]
    print(f"{'Prime':>10} {'p[i]':>8} {'Count':>6}")
    print("-" * 30)
    for p, count in sorted_primes:
        idx = get_prime_index(p)
        print(f"{p:>10} p[{idx}]{' ' * (4-len(str(idx)))} {count:>6}")

    # Divisibility chains
    print_header("DIVISIBILITY CHAINS")
    print("Checking if earlier m-values divide later ones (n=36-70)...")

    # Check key small m-values against this range
    key_small = [(4, 22), (5, 9), (6, 19), (9, 493), (11, 1921), (12, 1241)]

    for small_n, small_m in key_small:
        divisible_by = []
        for n in range(36, 71):
            if m(n) % small_m == 0:
                divisible_by.append(n)

        if divisible_by:
            print(f"\nm[{small_n}]={small_m} divides:")
            for dn in divisible_by[:8]:
                quotient = m(dn) // small_m
                print(f"  m[{dn}] = {m(dn)} = m[{small_n}] × {quotient}")

    # Ratio analysis (m[n]/2^n)
    print_header("RATIO ANALYSIS: m[n] / 2^n")
    print(f"{'n':>3} {'m[n]':>18} {'2^n':>20} {'ratio':>15}")
    print("-" * 60)

    for n in [36, 40, 45, 50, 55, 60, 65, 70]:
        mn = m(n)
        pow2 = 2**n
        ratio = mn / pow2
        print(f"{n:3} {mn:>18} {pow2:>20} {ratio:>15.6f}")

    # Look for patterns with d-sequence
    print_header("D-SEQUENCE CORRELATION")
    print("Checking if d[n] correlates with m[n] properties...")

    d_to_primality = defaultdict(lambda: {'prime': 0, 'composite': 0})
    for n in range(36, 71):
        dn = d(n)
        mn = m(n)
        if isprime(mn):
            d_to_primality[dn]['prime'] += 1
        else:
            d_to_primality[dn]['composite'] += 1

    print(f"\n{'d':>3} {'Prime':>8} {'Composite':>10}")
    print("-" * 25)
    for d_val in sorted(d_to_primality.keys()):
        stats = d_to_primality[d_val]
        print(f"{d_val:>3} {stats['prime']:>8} {stats['composite']:>10}")

def identify_patterns():
    """Identify specific patterns in n=36-70 range."""

    print_header("PATTERN IDENTIFICATION")

    # Check for arithmetic progressions in d-sequence
    print("\n1. Checking for d-sequence patterns...")
    d_vals = [d(n) for n in range(36, 71)]
    print(f"   d[36:70] = {d_vals}")

    # Check mode of d-sequence
    from collections import Counter
    d_mode = Counter(d_vals).most_common(3)
    print(f"   Mode: {d_mode}")

    # Check for m-values that are powers of 2
    print("\n2. Checking for powers of 2 in m-values...")
    for n in range(36, 71):
        mn = m(n)
        if mn > 0 and (mn & (mn - 1)) == 0:  # Power of 2
            print(f"   m[{n}] = {mn} = 2^{mn.bit_length()-1}")

    # Check for perfect squares
    print("\n3. Checking for perfect squares...")
    for n in range(36, 71):
        mn = m(n)
        sqrt = int(mn ** 0.5)
        if sqrt * sqrt == mn:
            print(f"   m[{n}] = {mn} = {sqrt}²")

    # Check for triangular numbers
    print("\n4. Checking for triangular numbers...")
    for n in range(36, 71):
        mn = m(n)
        # n*(n+1)/2 = mn => n² + n - 2*mn = 0
        # n = (-1 + sqrt(1 + 8*mn)) / 2
        discriminant = 1 + 8 * mn
        sqrt_disc = int(discriminant ** 0.5)
        if sqrt_disc * sqrt_disc == discriminant and (sqrt_disc - 1) % 2 == 0:
            tri_n = (sqrt_disc - 1) // 2
            print(f"   m[{n}] = {mn} = T_{tri_n} (triangular)")

    # Check for Fibonacci-like relationships
    print("\n5. Checking for Fibonacci-like patterns...")
    for n in range(38, 71):
        if m(n) == m(n-1) + m(n-2):
            print(f"   m[{n}] = m[{n-1}] + m[{n-2}] = {m(n-1)} + {m(n-2)} = {m(n)}")

def output_formula_table():
    """Create a formula table for n=36-70 based on discovered patterns."""

    print_header("FORMULA TABLE FOR n=36-70")
    print("\nAttempting to express each m[n] using known patterns...")
    print(f"{'n':>3} {'m[n]':>18} {'d[n]':>5} {'Proposed Formula':>50}")
    print("-" * 80)

    for n in range(36, 71):
        mn = m(n)
        dn = d(n)

        formula = "?"  # Default

        # Try to find pattern
        factors = factor_m(n)

        # Check if divisible by 17
        if 17 in factors:
            cofactor = mn // 17
            if isprime(cofactor):
                p_idx = get_prime_index(cofactor)
                formula = f"17 × p[{p_idx}] = 17 × {cofactor}"
            else:
                formula = f"17 × {cofactor}"

        # Check if prime
        elif isprime(mn):
            p_idx = get_prime_index(mn)
            formula = f"p[{p_idx}] (prime)"

        # Check if product of 2 primes (semiprime)
        elif len(factors) == 2 and all(e == 1 for e in factors.values()):
            primes = list(factors.keys())
            p1_idx = get_prime_index(primes[0])
            p2_idx = get_prime_index(primes[1])
            formula = f"p[{p1_idx}] × p[{p2_idx}] = {primes[0]} × {primes[1]}"

        # Check if divisible by earlier m-values
        else:
            for earlier_n in [4, 5, 6, 9, 11, 12]:
                earlier_m = m(earlier_n)
                if earlier_m > 1 and mn % earlier_m == 0:
                    quotient = mn // earlier_m
                    formula = f"m[{earlier_n}] × {quotient} = {earlier_m} × {quotient}"
                    break

        print(f"{n:3} {mn:>18} {dn:>5} {formula:>50}")

def main():
    print("="*80)
    print("EXTENDING FORMULA DERIVATION TO n=36-70")
    print("This fills the gap where 'others aren't looking'")
    print("="*80)

    analyze_n36_to_n70()
    identify_patterns()
    output_formula_table()

    print_header("SUMMARY")
    print("""
Key observations for n=36-70:

1. D-SEQUENCE: Check distribution and correlation with m-values
2. 17-NETWORK: Look for extension of p[7]=17 pattern
3. SELF-REFERENCE: Most targets out of range, but some early ones testable
4. GCD: Look for connected subgraphs via shared factors
5. DIVISIBILITY: Check if earlier m-values (m[4], m[5], etc.) divide later ones

NEXT STEPS:
1. Verify any discovered formulas
2. Look for convergent relationships (π, e, √2, etc.)
3. Test recursive patterns
4. Sync findings with other Claude instances
""")

if __name__ == '__main__':
    main()
