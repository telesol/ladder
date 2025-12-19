#!/usr/bin/env python3
"""
Find the formula for convergent index selection.

Known mappings:
- n=4: index=1 (π_num)
- n=5: index=4 (ln2_num)
- n=6: index=4 (e_num)
- n=7: index=3 (φ_num × ln2_den)
- n=11: index=3 (√2_num × π_den)

Goal: Find index = f(n) or f(n, d[n], m[earlier])
"""

import json
from convergent_database import continued_fraction_coefficients, compute_convergents

with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

M_SEQ = data['m_seq']
D_SEQ = data['d_seq']
M_SET = set(M_SEQ)

def m(n):
    if n < 2 or n > 70:
        return None
    return M_SEQ[n - 2]

def d(n):
    if n < 2 or n > 70:
        return None
    return D_SEQ[n - 2]

# Build comprehensive database
CONSTANTS = ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']

def build_database(num_terms=50):
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

database = build_database(50)

print("=" * 70)
print("INDEX SELECTION ANALYSIS")
print("=" * 70)

# For each m-value, find ALL ways it can be expressed as convergent product
# and record the indices used

def find_all_expressions(m_val, database, max_idx=20):
    """Find all ways m_val = conv_A[i] × conv_B[j]"""
    expressions = []

    for const_a in CONSTANTS:
        for type_a in ['num', 'den']:
            vals_a = database.get(const_a, {}).get(type_a, [])[:max_idx]
            for i, va in enumerate(vals_a):
                if va <= 0 or m_val % va != 0:
                    continue
                vb = m_val // va
                for const_b in CONSTANTS:
                    for type_b in ['num', 'den']:
                        vals_b = database.get(const_b, {}).get(type_b, [])[:max_idx]
                        for j, vb_cand in enumerate(vals_b):
                            if vb_cand == vb:
                                expressions.append({
                                    'const_a': const_a, 'type_a': type_a,
                                    'idx_a': i, 'val_a': va,
                                    'const_b': const_b, 'type_b': type_b,
                                    'idx_b': j, 'val_b': vb
                                })
    return expressions

# Analyze n=2 to n=15 to find index patterns
print("\nAnalyzing m[2] to m[15] for index patterns...\n")

for n in range(2, 16):
    mn = m(n)
    dn = d(n)
    exprs = find_all_expressions(mn, database)

    if exprs:
        # Find expressions where idx_a == idx_b (same-index)
        same_idx = [e for e in exprs if e['idx_a'] == e['idx_b']]

        print(f"n={n:2}, m[n]={mn:>8}, d[n]={dn}")

        if same_idx:
            # Get unique indices used
            indices = set(e['idx_a'] for e in same_idx)
            print(f"  Same-index expressions at idx={sorted(indices)}")
            for idx in sorted(indices)[:3]:
                matches = [e for e in same_idx if e['idx_a'] == idx]
                if matches:
                    e = matches[0]
                    print(f"    idx {idx}: {e['val_a']} × {e['val_b']} = {e['const_a']}_{e['type_a']}[{idx}] × {e['const_b']}_{e['type_b']}[{idx}]")
        else:
            # Show different-index expressions
            if exprs:
                print(f"  Different-index expressions only")
                for e in exprs[:3]:
                    print(f"    {e['val_a']} × {e['val_b']} = {e['const_a']}_{e['type_a']}[{e['idx_a']}] × {e['const_b']}_{e['type_b']}[{e['idx_b']}]")
    else:
        print(f"n={n:2}, m[n]={mn:>8}, d[n]={dn}")
        print(f"  No convergent product expression found")

# Check relationship between n and preferred index
print("\n" + "=" * 70)
print("INDEX vs N RELATIONSHIP")
print("=" * 70)

# Collect (n, preferred_index) pairs
n_idx_pairs = []

for n in range(2, 16):
    mn = m(n)
    exprs = find_all_expressions(mn, database)
    same_idx = [e for e in exprs if e['idx_a'] == e['idx_b']]

    if same_idx:
        # Take the smallest non-trivial index
        indices = [e['idx_a'] for e in same_idx if e['val_a'] > 1 or e['val_b'] > 1]
        if indices:
            preferred_idx = min(indices)
            n_idx_pairs.append((n, preferred_idx))

print("\n(n, preferred_index) pairs:")
for n, idx in n_idx_pairs:
    dn = d(n)
    print(f"  n={n:2}, d[n]={dn}, idx={idx}, n-idx={n-idx}, n//idx={n//idx if idx > 0 else 'N/A'}, n%idx={n%idx if idx > 0 else 'N/A'}")

# Test various formulas
print("\n" + "=" * 70)
print("TESTING INDEX FORMULAS")
print("=" * 70)

formulas = [
    ("idx = n - 7", lambda n, d: n - 7),
    ("idx = n // 3", lambda n, d: n // 3),
    ("idx = n // 4", lambda n, d: n // 4),
    ("idx = d[n]", lambda n, d: d),
    ("idx = d[n] + 1", lambda n, d: d + 1),
    ("idx = n - d[n] - 4", lambda n, d: n - d - 4),
    ("idx = (n + d[n]) // 4", lambda n, d: (n + d) // 4),
]

for formula_name, formula_fn in formulas:
    matches = 0
    for n, actual_idx in n_idx_pairs:
        dn = d(n)
        predicted = formula_fn(n, dn)
        if predicted == actual_idx:
            matches += 1

    print(f"{formula_name:25}: {matches}/{len(n_idx_pairs)} matches")

# Check sums and differences for uncovered values
print("\n" + "=" * 70)
print("SUMS/DIFFERENCES FOR UNCOVERED VALUES")
print("=" * 70)

def find_sums(m_val, database, max_idx=20):
    """Find m_val = conv_A + conv_B"""
    sums = []
    all_vals = {}

    for const in CONSTANTS:
        for type_name in ['num', 'den']:
            vals = database.get(const, {}).get(type_name, [])[:max_idx]
            for idx, v in enumerate(vals):
                if v not in all_vals:
                    all_vals[v] = []
                all_vals[v].append((const, type_name, idx))

    for v1, sources1 in all_vals.items():
        v2 = m_val - v1
        if v2 > 0 and v2 in all_vals and v1 <= v2:
            sums.append({
                'v1': v1, 'sources1': sources1,
                'v2': v2, 'sources2': all_vals[v2]
            })

    return sums

def find_diffs(m_val, database, max_idx=20):
    """Find m_val = conv_A - conv_B"""
    diffs = []
    all_vals = {}

    for const in CONSTANTS:
        for type_name in ['num', 'den']:
            vals = database.get(const, {}).get(type_name, [])[:max_idx]
            for idx, v in enumerate(vals):
                if v not in all_vals:
                    all_vals[v] = []
                all_vals[v].append((const, type_name, idx))

    for v2, sources2 in all_vals.items():
        v1 = v2 - m_val
        if v1 > 0 and v1 in all_vals:
            diffs.append({
                'v1': v1, 'sources1': all_vals[v1],
                'v2': v2, 'sources2': sources2
            })

    return diffs

# Test on uncovered values
uncovered = [8, 12, 13, 14, 15]

for n in uncovered:
    mn = m(n)
    dn = d(n)

    print(f"\nn={n}, m[n]={mn}, d[n]={dn}")

    sums = find_sums(mn, database)
    if sums:
        print(f"  SUM expressions ({len(sums)} found):")
        for s in sums[:3]:
            src1 = s['sources1'][0]
            src2 = s['sources2'][0]
            print(f"    {mn} = {s['v1']} + {s['v2']} = {src1[0]}_{src1[1]}[{src1[2]}] + {src2[0]}_{src2[1]}[{src2[2]}]")

    diffs = find_diffs(mn, database)
    if diffs:
        print(f"  DIFF expressions ({len(diffs)} found):")
        for d_expr in diffs[:3]:
            src1 = d_expr['sources1'][0]
            src2 = d_expr['sources2'][0]
            print(f"    {mn} = {d_expr['v2']} - {d_expr['v1']} = {src2[0]}_{src2[1]}[{src2[2]}] - {src1[0]}_{src1[1]}[{src1[2]}]")

    if not sums and not diffs:
        print("  No sum or difference expression found")
