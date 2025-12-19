#!/usr/bin/env python3
"""
Cross-Constant Analysis
Investigates the pattern: m[n] = (convergent from constant A) × (convergent from constant B)

Key discovery from enhanced_convergent_analysis.py:
- m[11] = 1921 = 17 × 113
  - 17 = √2 numerator at index 3
  - 113 = π denominator at index 3

Hypothesis: m[n] can be expressed as products of convergents from DIFFERENT constants.
"""

import json
from sympy import isprime, primepi, prime
from convergent_database import continued_fraction_coefficients, compute_convergents

# Load m-sequence
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

M_SEQ = data['m_seq']
D_SEQ = data['d_seq']

def m(n):
    if n < 2 or n > 70:
        return None
    return M_SEQ[n - 2]

def d(n):
    if n < 2 or n > 70:
        return None
    return D_SEQ[n - 2]

# Build comprehensive convergent database
CONSTANTS = {
    'pi': 'π',
    'e': 'e',
    'sqrt2': '√2',
    'sqrt3': '√3',
    'phi': 'φ',
    'ln2': 'ln2',
    'sqrt5': '√5',
    'ln3': 'ln3',
    'gamma': 'γ'  # Euler-Mascheroni constant
}

def build_all_convergents(num_terms=50):
    """Build convergent databases for all constants."""
    database = {}
    for const_name in CONSTANTS.keys():
        try:
            cf = continued_fraction_coefficients(const_name, num_terms)
            convergents = compute_convergents(cf)
            database[const_name] = {
                'numerators': [c['numerator'] for c in convergents],
                'denominators': [c['denominator'] for c in convergents]
            }
        except:
            pass
    return database

def find_cross_constant_products(m_val, database):
    """Find if m_val = (num/den from const A) × (num/den from const B)."""
    matches = []

    const_names = list(database.keys())

    for i, const_a in enumerate(const_names):
        for type_a in ['numerators', 'denominators']:
            for idx_a, val_a in enumerate(database[const_a][type_a]):
                if val_a <= 0 or m_val % val_a != 0:
                    continue

                val_b = m_val // val_a

                # Look for val_b in other constants (or same constant)
                for const_b in const_names:
                    for type_b in ['numerators', 'denominators']:
                        for idx_b, v in enumerate(database[const_b][type_b]):
                            if v == val_b:
                                matches.append({
                                    'val_a': val_a,
                                    'const_a': const_a,
                                    'type_a': type_a,
                                    'idx_a': idx_a,
                                    'val_b': val_b,
                                    'const_b': const_b,
                                    'type_b': type_b,
                                    'idx_b': idx_b
                                })

    return matches

def analyze_17_network(database):
    """Analyze where 17 (key factor) comes from in convergents."""
    print("\n" + "=" * 70)
    print("LOCATING 17 IN CONVERGENTS")
    print("=" * 70)

    for const_name, data in database.items():
        for type_name in ['numerators', 'denominators']:
            for idx, val in enumerate(data[type_name]):
                if val == 17:
                    print(f"  17 = {CONSTANTS[const_name]} {type_name[:-1]} at index {idx}")

def main():
    print("=" * 70)
    print("CROSS-CONSTANT CONVERGENT ANALYSIS")
    print("=" * 70)

    print("\nBuilding convergent database for all constants...")
    database = build_all_convergents(50)
    print(f"Built database for: {', '.join(database.keys())}")

    # Show where 17 appears
    analyze_17_network(database)

    # Analyze 17-network m-values
    print("\n" + "=" * 70)
    print("ANALYZING 17-NETWORK M-VALUES")
    print("=" * 70)

    network_17 = [9, 11, 12, 24, 48, 67]

    for n in network_17:
        mn = m(n)
        dn = d(n)
        cofactor = mn // 17 if mn % 17 == 0 else None

        print(f"\n{'='*60}")
        print(f"n={n}: m[{n}]={mn}, d[{n}]={dn}")
        if cofactor:
            print(f"m[{n}] = 17 × {cofactor}")
            if isprime(cofactor):
                pi = primepi(cofactor)
                print(f"  cofactor = p[{pi}] (prime)")
        print(f"{'='*60}")

        # Find cross-constant products
        matches = find_cross_constant_products(mn, database)

        if matches:
            print(f"Found {len(matches)} cross-constant products:")
            # Show unique patterns
            seen = set()
            for match in matches[:20]:
                key = (match['const_a'], match['type_a'], match['idx_a'],
                       match['const_b'], match['type_b'], match['idx_b'])
                if key not in seen:
                    seen.add(key)
                    print(f"  {mn} = {match['val_a']} × {match['val_b']}")
                    print(f"    {match['val_a']}: {CONSTANTS[match['const_a']]} {match['type_a'][:-1]} (idx {match['idx_a']})")
                    print(f"    {match['val_b']}: {CONSTANTS[match['const_b']]} {match['type_b'][:-1]} (idx {match['idx_b']})")
        else:
            print("No cross-constant products found")

    # Check the verified formulas
    print("\n" + "=" * 70)
    print("VERIFYING: m[n] = 17 × p[n + m[earlier]]")
    print("=" * 70)

    # From findings: m[9]=17×p[10], m[11]=17×p[30], m[12]=17×p[21]
    # where p[10]=29, p[30]=113, p[21]=73

    tests = [
        (9, 2),   # m[9] = 17 × p[9 + m[2]] = 17 × p[10]
        (11, 6),  # m[11] = 17 × p[11 + m[6]] = 17 × p[30]
        (12, 5),  # m[12] = 17 × p[12 + m[5]] = 17 × p[21]
    ]

    for n, earlier in tests:
        mn = m(n)
        m_earlier = m(earlier)
        target_idx = n + m_earlier
        target_prime = prime(target_idx)
        predicted = 17 * target_prime
        match = "✓" if predicted == mn else "✗"
        print(f"\nm[{n}] = 17 × p[{n} + m[{earlier}]]")
        print(f"     = 17 × p[{target_idx}]")
        print(f"     = 17 × {target_prime}")
        print(f"     = {predicted}")
        print(f"  Actual m[{n}] = {mn} {match}")

    # Analyze primes in convergents
    print("\n" + "=" * 70)
    print("PRIMES 29, 113, 73 IN CONVERGENTS")
    print("=" * 70)

    target_primes = [29, 73, 113]

    for p in target_primes:
        print(f"\nLooking for {p}:")
        for const_name, data in database.items():
            for type_name in ['numerators', 'denominators']:
                for idx, val in enumerate(data[type_name]):
                    if val == p:
                        print(f"  {p} = {CONSTANTS[const_name]} {type_name[:-1]} at index {idx}")

    # Key insight: Check if the prime index relates to convergent index
    print("\n" + "=" * 70)
    print("KEY INSIGHT: Prime indices vs Convergent indices")
    print("=" * 70)

    # For m[11] = 17 × 113:
    # - 17 = √2 numerator at index 3
    # - 113 = π denominator at index 3
    # Both at INDEX 3!

    print("\nFor m[11] = 17 × 113:")
    print("  17 = √2 numerator at index 3")
    print("  113 = π denominator at index 3")
    print("  SAME INDEX!")

    # Check if this pattern holds for other 17-network values
    print("\n" + "=" * 70)
    print("TESTING SAME-INDEX HYPOTHESIS")
    print("=" * 70)

    # Check √2 numerators and π denominators at same index
    sqrt2_nums = database.get('sqrt2', {}).get('numerators', [])
    pi_dens = database.get('pi', {}).get('denominators', [])

    print("\n√2 numerators × π denominators (same index):")
    for idx in range(min(len(sqrt2_nums), len(pi_dens), 15)):
        product = sqrt2_nums[idx] * pi_dens[idx]
        # Check if this product is in m-sequence
        in_m = [n for n in range(2, 71) if m(n) == product]
        marker = f" ← m{in_m}" if in_m else ""
        print(f"  idx {idx}: {sqrt2_nums[idx]} × {pi_dens[idx]} = {product}{marker}")

if __name__ == '__main__':
    main()
