#!/usr/bin/env python3
"""
Test ALL constant pairs for same-index products.

Key discovery: m[11] = √2_num[3] × π_den[3] = 17 × 113

Hypothesis: Many m-values = const_A_num[i] × const_B_den[i] for SAME index i
"""

import json
from convergent_database import continued_fraction_coefficients, compute_convergents

# Load m-sequence
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

M_SEQ = data['m_seq']
M_SET = set(M_SEQ)  # For fast lookup

def m(n):
    if n < 2 or n > 70:
        return None
    return M_SEQ[n - 2]

# Build convergent databases
CONSTANTS = ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']

def build_database(num_terms=30):
    database = {}
    for const in CONSTANTS:
        try:
            cf = continued_fraction_coefficients(const, num_terms)
            convergents = compute_convergents(cf)
            database[const] = {
                'num': [c['numerator'] for c in convergents],
                'den': [c['denominator'] for c in convergents]
            }
        except:
            pass
    return database

print("=" * 80)
print("SAME-INDEX PRODUCT ANALYSIS")
print("=" * 80)

database = build_database(30)

# Test all pairs of (const_A, type_A) × (const_B, type_B) at same index
pairs = []
for const_a in CONSTANTS:
    for type_a in ['num', 'den']:
        for const_b in CONSTANTS:
            for type_b in ['num', 'den']:
                pairs.append((const_a, type_a, const_b, type_b))

print(f"\nTesting {len(pairs)} constant-type pairs...")

# For each pair, find products that match m-values
results = []

for const_a, type_a, const_b, type_b in pairs:
    if const_a not in database or const_b not in database:
        continue

    vals_a = database[const_a][type_a]
    vals_b = database[const_b][type_b]

    matches = []
    for idx in range(min(len(vals_a), len(vals_b), 20)):
        product = vals_a[idx] * vals_b[idx]
        if product in M_SET:
            # Find which n
            n_matches = [n for n in range(2, 71) if m(n) == product]
            matches.append({
                'idx': idx,
                'val_a': vals_a[idx],
                'val_b': vals_b[idx],
                'product': product,
                'n_values': n_matches
            })

    if matches:
        results.append({
            'pair': f"{const_a}_{type_a} × {const_b}_{type_b}",
            'matches': matches
        })

# Sort by number of matches
results.sort(key=lambda x: -len(x['matches']))

print("\n" + "=" * 80)
print("PAIRS WITH M-SEQUENCE MATCHES (sorted by # matches)")
print("=" * 80)

for result in results:
    if len(result['matches']) > 0:
        print(f"\n{result['pair']} ({len(result['matches'])} matches):")
        for match in result['matches']:
            ns = match['n_values']
            print(f"  idx {match['idx']:2}: {match['val_a']} × {match['val_b']} = {match['product']} → m{ns}")

# Summary
print("\n" + "=" * 80)
print("TOP PAIRS BY NUMBER OF MATCHES")
print("=" * 80)

for result in results[:15]:
    print(f"  {result['pair']:25}: {len(result['matches'])} matches")

# Create complete coverage analysis
print("\n" + "=" * 80)
print("M-SEQUENCE COVERAGE BY SAME-INDEX PRODUCTS")
print("=" * 80)

# Track which n values are covered
covered = set()
coverage_map = {}

for result in results:
    for match in result['matches']:
        for n in match['n_values']:
            covered.add(n)
            if n not in coverage_map:
                coverage_map[n] = []
            coverage_map[n].append({
                'pair': result['pair'],
                'idx': match['idx'],
                'formula': f"{match['val_a']} × {match['val_b']}"
            })

print(f"\nCovered: {len(covered)}/69 m-values ({100*len(covered)/69:.1f}%)")

print("\nCovered m-values:")
for n in sorted(covered):
    formulas = coverage_map[n]
    formula_strs = [f['formula'] for f in formulas[:3]]
    print(f"  m[{n:2}] = {m(n):>10}: {' | '.join(formula_strs)}")

print("\n" + "=" * 80)
print("UNCOVERED M-VALUES")
print("=" * 80)

uncovered = [n for n in range(2, 71) if n not in covered]
print(f"Uncovered: {len(uncovered)}/69 m-values")
for n in uncovered[:20]:
    print(f"  m[{n:2}] = {m(n)}")

# Try to find patterns in uncovered values
print("\n" + "=" * 80)
print("PATTERN SEARCH FOR UNCOVERED VALUES")
print("=" * 80)

# For uncovered values, check if they're products of TWO convergents at DIFFERENT indices
from itertools import product as cartesian_product

def find_different_index_products(m_val, database, max_idx=15):
    """Find if m_val = conv_A[i] × conv_B[j] where i ≠ j"""
    matches = []

    for const_a in CONSTANTS:
        for type_a in ['num', 'den']:
            for const_b in CONSTANTS:
                for type_b in ['num', 'den']:
                    if const_a not in database or const_b not in database:
                        continue

                    vals_a = database[const_a][type_a][:max_idx]
                    vals_b = database[const_b][type_b][:max_idx]

                    for i, va in enumerate(vals_a):
                        if va <= 0 or m_val % va != 0:
                            continue
                        vb = m_val // va
                        for j, vb_cand in enumerate(vals_b):
                            if vb_cand == vb and i != j:  # Different indices
                                matches.append({
                                    'const_a': const_a, 'type_a': type_a, 'idx_a': i, 'val_a': va,
                                    'const_b': const_b, 'type_b': type_b, 'idx_b': j, 'val_b': vb
                                })

    return matches

print("\nSearching for different-index products in uncovered values...")

for n in uncovered[:10]:
    mn = m(n)
    matches = find_different_index_products(mn, database)
    if matches:
        print(f"\nm[{n}] = {mn}:")
        for match in matches[:3]:
            print(f"  = {match['val_a']} × {match['val_b']}")
            print(f"    {match['const_a']}_{match['type_a']}[{match['idx_a']}] × {match['const_b']}_{match['type_b']}[{match['idx_b']}]")
    else:
        print(f"\nm[{n}] = {mn}: NO PRODUCT MATCH")
