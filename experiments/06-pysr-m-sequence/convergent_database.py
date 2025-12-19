#!/usr/bin/env python3
"""
Convergent Database Builder
Computes convergents for mathematical constants and cross-references with m-sequence.
"""

from fractions import Fraction
from decimal import Decimal, getcontext
import math

# Set high precision
getcontext().prec = 100

# Known m-sequence (n=2 to 31)
M_SEQUENCE = {
    2: 3, 3: 7, 4: 22, 5: 9, 6: 19, 7: 50, 8: 23, 9: 493, 10: 19,
    11: 1921, 12: 1241, 13: 8342, 14: 2034, 15: 26989, 16: 8470,
    17: 138269, 18: 255121, 19: 564091, 20: 900329, 21: 670674,
    22: 4494340, 23: 7256672, 24: 13127702, 25: 5765582, 26: 50898620,
    27: 23103005, 28: 33504646, 29: 156325542, 30: 536813704, 31: 350549882
}

# D-sequence
D_SEQUENCE = {
    2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 4, 9: 1, 10: 7,
    11: 1, 12: 2, 13: 1, 14: 4, 15: 1, 16: 4, 17: 1, 18: 1,
    19: 1, 20: 1, 21: 2, 22: 2, 23: 2, 24: 1, 25: 1, 26: 3,
    27: 1, 28: 4, 29: 3, 30: 1, 31: 1
}

def continued_fraction_coefficients(constant_name, n_terms=50):
    """Get continued fraction coefficients for various constants."""

    if constant_name == 'pi':
        # π = [3; 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2, 1, 84, 2, 1, 1, 15, ...]
        return [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2, 1, 84, 2, 1, 1, 15, 3, 13, 1, 4, 2, 6, 6, 99, 1, 2, 2, 6, 3, 5, 1, 1, 6, 8, 1, 7, 1, 2, 3, 7][:n_terms]

    elif constant_name == 'e':
        # e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, ...] - pattern: [2; 1, 2k, 1] for k=1,2,3...
        cf = [2, 1, 2]
        for k in range(1, n_terms // 3 + 1):
            cf.extend([1, 1, 2 * (k + 1)])
        return cf[:n_terms]

    elif constant_name == 'sqrt2':
        # sqrt(2) = [1; 2, 2, 2, 2, ...]
        return [1] + [2] * (n_terms - 1)

    elif constant_name == 'sqrt3':
        # sqrt(3) = [1; 1, 2, 1, 2, 1, 2, ...]
        cf = [1]
        for i in range(n_terms - 1):
            cf.append(1 if i % 2 == 0 else 2)
        return cf

    elif constant_name == 'phi':
        # φ (golden ratio) = [1; 1, 1, 1, 1, ...]
        return [1] * n_terms

    elif constant_name == 'ln2':
        # ln(2) = [0; 1, 2, 3, 1, 6, 3, 1, 1, 2, 1, 1, 1, 1, 3, 10, ...]
        return [0, 1, 2, 3, 1, 6, 3, 1, 1, 2, 1, 1, 1, 1, 3, 10, 1, 1, 1, 2, 1, 1, 1, 1, 3, 2, 3, 1, 13, 7, 4, 1, 1, 1, 7, 2, 4, 1, 1, 2, 1, 2, 1, 4, 3, 1, 1, 1, 1, 1][:n_terms]

    else:
        raise ValueError(f"Unknown constant: {constant_name}")

def compute_convergents(cf_coefficients):
    """Compute convergents (h_n, k_n) from continued fraction coefficients."""
    convergents = []

    h_prev2, h_prev1 = 0, 1
    k_prev2, k_prev1 = 1, 0

    for i, a in enumerate(cf_coefficients):
        h = a * h_prev1 + h_prev2
        k = a * k_prev1 + k_prev2

        convergents.append({
            'index': i,
            'a': a,
            'numerator': h,
            'denominator': k,
            'value': h / k if k != 0 else float('inf')
        })

        h_prev2, h_prev1 = h_prev1, h
        k_prev2, k_prev1 = k_prev1, k

    return convergents

def build_database():
    """Build the complete convergent database."""

    constants = ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']
    database = {}

    for const in constants:
        cf = continued_fraction_coefficients(const, 50)
        convergents = compute_convergents(cf)
        database[const] = convergents

    return database

def find_m_matches(database):
    """Find which m values appear in convergent numerators/denominators."""

    m_values = set(M_SEQUENCE.values())
    matches = {}

    for m_val in sorted(m_values):
        matches[m_val] = []

        for const_name, convergents in database.items():
            for conv in convergents:
                if conv['numerator'] == m_val:
                    matches[m_val].append({
                        'constant': const_name,
                        'type': 'numerator',
                        'index': conv['index'],
                        'fraction': f"{conv['numerator']}/{conv['denominator']}"
                    })
                if conv['denominator'] == m_val:
                    matches[m_val].append({
                        'constant': const_name,
                        'type': 'denominator',
                        'index': conv['index'],
                        'fraction': f"{conv['numerator']}/{conv['denominator']}"
                    })

    return matches

def main():
    print("=" * 70)
    print("CONVERGENT DATABASE ANALYSIS")
    print("=" * 70)

    # Build database
    print("\n1. Building convergent database for π, e, sqrt(2), sqrt(3), φ, ln(2)...")
    database = build_database()

    # Show first few convergents for each
    print("\n2. Sample convergents:")
    for const_name, convergents in database.items():
        nums = [c['numerator'] for c in convergents[:12]]
        print(f"   {const_name:8} numerators: {nums}")

    # Find matches
    print("\n3. Cross-referencing m-sequence with convergents...")
    matches = find_m_matches(database)

    print("\n" + "=" * 70)
    print("M-VALUE MATCHES IN CONVERGENT DATABASE")
    print("=" * 70)

    found_count = 0
    for n in sorted(M_SEQUENCE.keys()):
        m_val = M_SEQUENCE[n]
        if matches[m_val]:
            found_count += 1
            print(f"\nm[{n:2}] = {m_val:>10} FOUND:")
            for match in matches[m_val]:
                print(f"         → {match['constant']:8} {match['type']:11} at index {match['index']:2} ({match['fraction']})")
        else:
            print(f"\nm[{n:2}] = {m_val:>10} - no match")

    print("\n" + "=" * 70)
    print(f"SUMMARY: {found_count}/{len(M_SEQUENCE)} m-values found in convergent database")
    print("=" * 70)

    # Additional analysis
    print("\n4. Analyzing patterns in matches...")

    # Which constants contribute most?
    const_counts = {}
    for m_val, match_list in matches.items():
        for match in match_list:
            const = match['constant']
            const_counts[const] = const_counts.get(const, 0) + 1

    print("\n   Matches by constant:")
    for const, count in sorted(const_counts.items(), key=lambda x: -x[1]):
        print(f"   {const:8}: {count} matches")

    # Phase analysis
    print("\n5. Phase analysis (which constant for which n):")
    for n in sorted(M_SEQUENCE.keys())[:15]:
        m_val = M_SEQUENCE[n]
        if matches[m_val]:
            sources = [m['constant'] for m in matches[m_val]]
            print(f"   n={n:2}, m={m_val:>6}: {', '.join(set(sources))}")
        else:
            print(f"   n={n:2}, m={m_val:>6}: UNKNOWN SOURCE")

if __name__ == "__main__":
    main()
