#!/usr/bin/env python3
"""
Search for m[13] and m[15] using extended convergent database
"""

import math
from convergent_database import (
    M_SEQUENCE, D_SEQUENCE,
    compute_convergents, continued_fraction_coefficients
)
from itertools import combinations

def compute_additional_constants(n_terms=100):
    """Compute convergents for additional mathematical constants."""

    # Euler-Mascheroni constant γ ≈ 0.5772156649
    # CF: [0; 1, 1, 2, 1, 2, 1, 4, 3, 13, 5, ...]
    gamma_cf = [0, 1, 1, 2, 1, 2, 1, 4, 3, 13, 5, 1, 1, 8, 1, 2, 4, 1, 1, 40,
                1, 11, 3, 7, 1, 7, 1, 1, 5, 1, 49, 4, 1, 65, 1, 4, 7, 11, 1, 399][:n_terms]

    # √5 = [2; 4, 4, 4, 4, ...]
    sqrt5_cf = [2] + [4] * (n_terms - 1)

    # ln(3) ≈ 1.0986122886
    # CF: [1; 10, 2, 1, 1, 6, 1, ...]
    ln3_cf = [1, 10, 2, 1, 1, 6, 1, 3, 3, 1, 1, 2, 2, 1, 1, 1, 6, 1, 10, 2][:n_terms]

    constants = {
        'gamma': gamma_cf,
        'sqrt5': sqrt5_cf,
        'ln3': ln3_cf,
    }

    database = {}
    for name, cf in constants.items():
        database[name] = compute_convergents(cf)

    return database

def build_extended_database(n_terms=200):
    """Build extended convergent database."""
    constants = ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']
    database = {}

    for const in constants:
        cf = continued_fraction_coefficients(const, n_terms)
        database[const] = compute_convergents(cf)

    # Add additional constants
    additional = compute_additional_constants(n_terms)
    database.update(additional)

    return database

def extract_values(database, max_value=100000000):
    """Extract all convergent values."""
    values = set()
    value_sources = {}

    for const_name, convergents in database.items():
        for conv in convergents:
            for val, part in [(conv['numerator'], 'num'), (conv['denominator'], 'den')]:
                if 0 < val <= max_value:
                    values.add(val)
                    if val not in value_sources:
                        value_sources[val] = []
                    value_sources[val].append({
                        'const': const_name,
                        'part': part,
                        'index': conv['index'],
                        'frac': f"{conv['numerator']}/{conv['denominator']}"
                    })

    return sorted(values), value_sources

def search_triple_products(target, values, value_sources, max_check=50):
    """Search for target = v1 × v2 × v3."""
    matches = []

    # Get possible factors
    factors = [v for v in values if v <= target and target % v == 0][:max_check]

    for v1 in factors[:20]:  # Limit search space
        if target % v1 != 0:
            continue
        remainder = target // v1

        for v2 in factors[:20]:
            if remainder % v2 != 0:
                continue
            v3 = remainder // v2

            if v3 in values and v1 <= v2 <= v3:
                matches.append({
                    'type': 'triple_product',
                    'formula': f'{v1} × {v2} × {v3}',
                    'v1': v1, 'v2': v2, 'v3': v3,
                    'sources': [value_sources[v1][0], value_sources[v2][0], value_sources[v3][0]]
                })

    return matches

def search_triple_sums(target, values, value_sources, max_check=100):
    """Search for target = v1 + v2 + v3."""
    matches = []
    possible = [v for v in values if v < target][:max_check]

    for i, v1 in enumerate(possible[:30]):
        for j, v2 in enumerate(possible[i:i+30]):
            v3 = target - v1 - v2
            if v3 > 0 and v3 in values and v1 <= v2 <= v3:
                matches.append({
                    'type': 'triple_sum',
                    'formula': f'{v1} + {v2} + {v3}',
                    'v1': v1, 'v2': v2, 'v3': v3,
                    'sources': [value_sources[v1][0], value_sources[v2][0], value_sources[v3][0]]
                })

    return matches

def search_recursive_formulas(target_n, values, value_sources):
    """Search for recursive formulas involving previous m-values."""
    target = M_SEQUENCE[target_n]
    matches = []

    # Test various recursive patterns
    for i in range(2, target_n):
        for j in range(2, target_n):
            mi = M_SEQUENCE[i]
            mj = M_SEQUENCE[j]

            # With convergent values
            for v in [v for v in values if v < 10000][:50]:
                tests = [
                    (mi * mj + v, f'm[{i}] × m[{j}] + {v}'),
                    (mi * mj - v, f'm[{i}] × m[{j}] - {v}'),
                    (mi + mj * v, f'm[{i}] + m[{j}] × {v}'),
                    (mi * v + mj, f'm[{i}] × {v} + m[{j}]'),
                ]

                for val, formula in tests:
                    if val == target:
                        matches.append({
                            'type': 'recursive',
                            'formula': formula,
                            'convergent': v,
                            'source': value_sources[v][0] if v in value_sources else None
                        })

    return matches

def search_m13_and_m15():
    """Comprehensive search for m[13] and m[15]."""
    print("="*80)
    print("SEARCHING FOR m[13]=8342 AND m[15]=26989")
    print("="*80)

    print("\nBuilding extended convergent database (200 terms)...")
    database = build_extended_database(200)

    print(f"Constants included: {list(database.keys())}")

    print("\nExtracting convergent values...")
    values, value_sources = extract_values(database, max_value=100000000)
    print(f"Total unique values: {len(values)}")

    for target_n in [13, 15]:
        target = M_SEQUENCE[target_n]
        print(f"\n{'='*80}")
        print(f"Searching for m[{target_n}] = {target}")
        print(f"{'='*80}")

        # Direct match
        if target in value_sources:
            print(f"\nDIRECT MATCH FOUND:")
            for src in value_sources[target][:3]:
                print(f"  {src['const']:8} {src['part']:3} (idx {src['index']:2}) {src['frac']}")

        # Products
        print(f"\nSearching for products...")
        for v in values:
            if v > 1 and v < target and target % v == 0:
                other = target // v
                if other in values:
                    s1 = value_sources[v][0]
                    s2 = value_sources[other][0]
                    print(f"  {target} = {v} × {other}")
                    print(f"    {v}: {s1['const']} {s1['part']} (idx {s1['index']})")
                    print(f"    {other}: {s2['const']} {s2['part']} (idx {s2['index']})")
                    break  # Just show first match

        # Triple products
        print(f"\nSearching for triple products...")
        triple_prods = search_triple_products(target, values, value_sources)
        if triple_prods:
            print(f"  Found {len(triple_prods)} triple product matches (showing first 3):")
            for match in triple_prods[:3]:
                print(f"  {match['formula']}")
                for src in match['sources']:
                    print(f"    {src['const']} {src['part']} (idx {src['index']})")

        # Sums
        print(f"\nSearching for sums...")
        for v in values:
            if v < target:
                other = target - v
                if other in values:
                    s1 = value_sources[v][0]
                    s2 = value_sources[other][0]
                    print(f"  {target} = {v} + {other}")
                    print(f"    {v}: {s1['const']} {s1['part']} (idx {s1['index']})")
                    print(f"    {other}: {s2['const']} {s2['part']} (idx {s2['index']})")
                    break  # Just show first match

        # Triple sums
        print(f"\nSearching for triple sums...")
        triple_sums = search_triple_sums(target, values, value_sources)
        if triple_sums:
            print(f"  Found {len(triple_sums)} triple sum matches (showing first 3):")
            for match in triple_sums[:3]:
                print(f"  {match['formula']}")
                for src in match['sources']:
                    print(f"    {src['const']} {src['part']} (idx {src['index']})")

        # Recursive
        print(f"\nSearching for recursive formulas...")
        recursive = search_recursive_formulas(target_n, values, value_sources)
        if recursive:
            print(f"  Found {len(recursive)} recursive matches (showing first 5):")
            for match in recursive[:5]:
                print(f"  {match['formula']}")
                if match['source']:
                    src = match['source']
                    print(f"    convergent: {src['const']} {src['part']} (idx {src['index']})")

        print()

def main():
    search_m13_and_m15()

    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("""
If matches were found above, they represent possible formulas for m[13] and m[15].
The most likely candidates are:
1. Direct convergent matches (new constants)
2. Products of convergent values
3. Sums of convergent values
4. Recursive formulas involving previous m-values

Next step: Validate any promising formula against m[16] through m[31].
""")

if __name__ == "__main__":
    main()
