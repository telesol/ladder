#!/usr/bin/env python3
"""
Enhanced Convergent Analysis
Systematically checks for m[n] as:
1. Direct convergent numerators/denominators
2. Products of two convergent values
3. Sums of two convergent values
"""

import sys
from convergent_database import (
    build_database, M_SEQUENCE, D_SEQUENCE,
    continued_fraction_coefficients, compute_convergents
)
from itertools import combinations, product

def get_all_convergent_values(database, max_value=100000000):
    """Extract all unique numerators and denominators from database."""
    values = set()
    value_sources = {}

    for const_name, convergents in database.items():
        for conv in convergents:
            num = conv['numerator']
            den = conv['denominator']

            if num <= max_value and num > 0:
                values.add(num)
                if num not in value_sources:
                    value_sources[num] = []
                value_sources[num].append({
                    'constant': const_name,
                    'type': 'numerator',
                    'index': conv['index'],
                    'fraction': f"{num}/{den}"
                })

            if den <= max_value and den > 0:
                values.add(den)
                if den not in value_sources:
                    value_sources[den] = []
                value_sources[den].append({
                    'constant': const_name,
                    'type': 'denominator',
                    'index': conv['index'],
                    'fraction': f"{num}/{den}"
                })

    return sorted(values), value_sources

def check_direct_match(m_val, value_sources):
    """Check if m_val appears directly in convergents."""
    if m_val in value_sources:
        return value_sources[m_val]
    return None

def check_product_match(m_val, values, value_sources, max_factors=50):
    """Check if m_val is a product of two convergent values."""
    matches = []

    # Only check values that could reasonably be factors
    possible_factors = [v for v in values if v <= m_val and m_val % v == 0]

    for v1 in possible_factors[:max_factors]:
        v2 = m_val // v1
        if v2 in values and v1 <= v2:  # v1 <= v2 to avoid duplicates
            matches.append({
                'v1': v1,
                'v2': v2,
                'v1_sources': value_sources[v1],
                'v2_sources': value_sources[v2]
            })

    return matches if matches else None

def check_sum_match(m_val, values, value_sources, max_terms=100):
    """Check if m_val is a sum of two convergent values."""
    matches = []

    # Only check values smaller than m_val
    possible_terms = [v for v in values if v < m_val][:max_terms]

    for v1 in possible_terms:
        v2 = m_val - v1
        if v2 in values and v1 <= v2:  # v1 <= v2 to avoid duplicates
            matches.append({
                'v1': v1,
                'v2': v2,
                'v1_sources': value_sources[v1],
                'v2_sources': value_sources[v2]
            })

    return matches if matches else None

def check_difference_match(m_val, values, value_sources, max_terms=100):
    """Check if m_val is a difference of two convergent values."""
    matches = []

    # Check v2 - v1 = m_val where v2 > v1
    possible_terms = [v for v in values if v > m_val][:max_terms]

    for v2 in possible_terms:
        v1 = v2 - m_val
        if v1 in values:
            matches.append({
                'operation': 'v2 - v1',
                'v1': v1,
                'v2': v2,
                'v1_sources': value_sources[v1],
                'v2_sources': value_sources[v2]
            })

    return matches if matches else None

def analyze_m_value(n, database, values, value_sources):
    """Comprehensive analysis of single m[n] value."""
    m_val = M_SEQUENCE[n]
    d_val = D_SEQUENCE[n]

    results = {
        'n': n,
        'm': m_val,
        'd': d_val,
        'direct': None,
        'product': None,
        'sum': None,
        'difference': None
    }

    # Check direct match
    direct = check_direct_match(m_val, value_sources)
    if direct:
        results['direct'] = direct

    # Check product match
    product_matches = check_product_match(m_val, values, value_sources)
    if product_matches:
        results['product'] = product_matches

    # Check sum match
    sum_matches = check_sum_match(m_val, values, value_sources)
    if sum_matches:
        results['sum'] = sum_matches

    # Check difference match
    diff_matches = check_difference_match(m_val, values, value_sources)
    if diff_matches:
        results['difference'] = diff_matches

    return results

def print_analysis(results):
    """Pretty print the analysis results."""
    n = results['n']
    m = results['m']
    d = results['d']

    print(f"\n{'='*80}")
    print(f"n={n}, m[{n}]={m}, d[{n}]={d}")
    print(f"{'='*80}")

    found_something = False

    # Direct matches
    if results['direct']:
        found_something = True
        print(f"\nDIRECT MATCH:")
        for source in results['direct'][:3]:  # Limit to first 3
            print(f"  {source['constant']:8} {source['type']:11} at index {source['index']:2} ({source['fraction']})")

    # Product matches
    if results['product']:
        found_something = True
        print(f"\nPRODUCT MATCHES ({len(results['product'])} found):")
        for i, match in enumerate(results['product'][:5]):  # Limit to first 5
            v1, v2 = match['v1'], match['v2']
            print(f"  {m} = {v1} × {v2}")
            # Show first source for each
            if match['v1_sources']:
                s1 = match['v1_sources'][0]
                print(f"    {v1}: {s1['constant']} {s1['type']} (idx {s1['index']})")
            if match['v2_sources']:
                s2 = match['v2_sources'][0]
                print(f"    {v2}: {s2['constant']} {s2['type']} (idx {s2['index']})")

    # Sum matches
    if results['sum']:
        found_something = True
        print(f"\nSUM MATCHES ({len(results['sum'])} found):")
        for i, match in enumerate(results['sum'][:5]):  # Limit to first 5
            v1, v2 = match['v1'], match['v2']
            print(f"  {m} = {v1} + {v2}")
            # Show first source for each
            if match['v1_sources']:
                s1 = match['v1_sources'][0]
                print(f"    {v1}: {s1['constant']} {s1['type']} (idx {s1['index']})")
            if match['v2_sources']:
                s2 = match['v2_sources'][0]
                print(f"    {v2}: {s2['constant']} {s2['type']} (idx {s2['index']})")

    # Difference matches
    if results['difference']:
        found_something = True
        print(f"\nDIFFERENCE MATCHES ({len(results['difference'])} found):")
        for i, match in enumerate(results['difference'][:5]):  # Limit to first 5
            v1, v2 = match['v1'], match['v2']
            print(f"  {m} = {v2} - {v1}")
            # Show first source for each
            if match['v1_sources']:
                s1 = match['v1_sources'][0]
                print(f"    {v1}: {s1['constant']} {s1['type']} (idx {s1['index']})")
            if match['v2_sources']:
                s2 = match['v2_sources'][0]
                print(f"    {v2}: {s2['constant']} {s2['type']} (idx {s2['index']})")

    if not found_something:
        print("\nNO MATCHES FOUND")

def main():
    print("="*80)
    print("ENHANCED CONVERGENT ANALYSIS")
    print("="*80)

    # Build database with more terms
    print("\nBuilding convergent database (100 terms per constant)...")
    database = {}
    constants = ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']

    for const in constants:
        cf = continued_fraction_coefficients(const, 100)
        convergents = compute_convergents(cf)
        database[const] = convergents

    # Extract all values
    print("Extracting convergent values...")
    values, value_sources = get_all_convergent_values(database, max_value=100000000)
    print(f"Found {len(values)} unique convergent values")

    # Analyze m[2] through m[15]
    print("\n" + "="*80)
    print("ANALYZING m[2] through m[15]")
    print("="*80)

    all_results = []
    for n in range(2, 16):
        results = analyze_m_value(n, database, values, value_sources)
        all_results.append(results)
        print_analysis(results)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    for results in all_results:
        n = results['n']
        m = results['m']
        matches = []
        if results['direct']: matches.append('DIRECT')
        if results['product']: matches.append('PRODUCT')
        if results['sum']: matches.append('SUM')
        if results['difference']: matches.append('DIFF')

        if matches:
            print(f"m[{n:2}] = {m:>8}: {', '.join(matches)}")
        else:
            print(f"m[{n:2}] = {m:>8}: NO MATCH")

if __name__ == "__main__":
    main()
