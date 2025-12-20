#!/usr/bin/env python3
"""
Validate convergent formulas for m[16] through m[31].
Extends the 100% coverage achieved for m[2]-m[15].
"""

import math
from convergent_database import (
    M_SEQUENCE, D_SEQUENCE,
    compute_convergents, continued_fraction_coefficients
)
from itertools import combinations

# Extended m-sequence from data_for_csolver.json
M_SEQUENCE_EXTENDED = {
    2: 1, 3: 1, 4: 22, 5: 9, 6: 19, 7: 50, 8: 23, 9: 493, 10: 19,
    11: 1921, 12: 1241, 13: 8342, 14: 2034, 15: 26989, 16: 8470,
    17: 138269, 18: 255121, 19: 564091, 20: 900329, 21: 670674,
    22: 1603443, 23: 8804812, 24: 1693268, 25: 29226275, 26: 78941020,
    27: 43781837, 28: 264700930, 29: 591430834, 30: 105249691, 31: 2111419265
}

# D-sequence
D_SEQ_EXTENDED = {
    2: 2, 3: 3, 4: 1, 5: 2, 6: 2, 7: 2, 8: 4, 9: 1, 10: 7,
    11: 1, 12: 2, 13: 1, 14: 4, 15: 1, 16: 4, 17: 1, 18: 1,
    19: 1, 20: 1, 21: 2, 22: 2, 23: 1, 24: 4, 25: 1, 26: 1,
    27: 2, 28: 1, 29: 1, 30: 4, 31: 1
}

def compute_additional_constants(n_terms=300):
    """Compute convergents for additional mathematical constants."""

    # Euler-Mascheroni constant γ ≈ 0.5772156649
    gamma_cf = [0, 1, 1, 2, 1, 2, 1, 4, 3, 13, 5, 1, 1, 8, 1, 2, 4, 1, 1, 40,
                1, 11, 3, 7, 1, 7, 1, 1, 5, 1, 49, 4, 1, 65, 1, 4, 7, 11, 1, 399]

    # √5 = [2; 4, 4, 4, 4, ...]
    sqrt5_cf = [2] + [4] * (n_terms - 1)

    # ln(3) ≈ 1.0986122886
    ln3_cf = [1, 10, 2, 1, 1, 6, 1, 3, 3, 1, 1, 2, 2, 1, 1, 1, 6, 1, 10, 2]

    # √6 = [2; 2, 4, 2, 4, ...]
    sqrt6_cf = [2] + [2, 4] * (n_terms // 2)

    # √7 = [2; 1, 1, 1, 4, 1, 1, 1, 4, ...]
    sqrt7_cf = [2] + [1, 1, 1, 4] * (n_terms // 4)

    # e^2 ≈ 7.389
    e2_cf = [7, 2, 1, 1, 3, 18, 5, 1, 1, 6, 30, 8, 1, 1, 9, 42, 11, 1, 1, 12]

    constants = {
        'gamma': gamma_cf[:n_terms],
        'sqrt5': sqrt5_cf[:n_terms],
        'ln3': ln3_cf[:min(len(ln3_cf), n_terms)],
        'sqrt6': sqrt6_cf[:n_terms],
        'sqrt7': sqrt7_cf[:n_terms],
        'e2': e2_cf[:min(len(e2_cf), n_terms)],
    }

    database = {}
    for name, cf in constants.items():
        database[name] = compute_convergents(cf)

    return database

def build_full_database(n_terms=300):
    """Build complete convergent database with all constants."""
    constants = ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']
    database = {}

    for const in constants:
        cf = continued_fraction_coefficients(const, n_terms)
        database[const] = compute_convergents(cf)

    additional = compute_additional_constants(n_terms)
    database.update(additional)

    return database

def extract_all_values(database, max_value=10**10):
    """Extract all convergent values up to max_value."""
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

    return values, value_sources

def factorize(n):
    """Return prime factorization as list of (prime, power) tuples."""
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            count = 0
            while n % d == 0:
                n //= d
                count += 1
            factors.append((d, count))
        d += 1
    if n > 1:
        factors.append((n, 1))
    return factors

def search_matches(target_n, target_m, values, value_sources, prev_m):
    """Search for all possible matches for a single m-value."""
    matches = []
    d_n = D_SEQ_EXTENDED.get(target_n, 1)

    # Direct convergent match
    if target_m in value_sources:
        for src in value_sources[target_m][:3]:
            matches.append({
                'type': 'direct',
                'formula': f"{target_m} = {src['const']} {src['part']} (idx {src['index']})",
                'constants': [src['const']],
                'score': 10  # High confidence
            })

    # Binary product: a × b = target
    for v in values:
        if 1 < v < target_m and target_m % v == 0:
            other = target_m // v
            if other in value_sources and v in value_sources:
                s1 = value_sources[v][0]
                s2 = value_sources[other][0]
                matches.append({
                    'type': 'product',
                    'formula': f"{v} × {other}",
                    'constants': [s1['const'], s2['const']],
                    'score': 8
                })
                if len(matches) > 20:
                    break

    # Binary sum: a + b = target
    for v in values:
        if 0 < v < target_m:
            other = target_m - v
            if other > 0 and other in value_sources and v in value_sources:
                s1 = value_sources[v][0]
                s2 = value_sources[other][0]
                matches.append({
                    'type': 'sum',
                    'formula': f"{v} + {other}",
                    'constants': [s1['const'], s2['const']],
                    'score': 8
                })
                if len(matches) > 30:
                    break

    # Difference: a - b = target
    for v in values:
        if v > target_m:
            other = v - target_m
            if other > 0 and other in value_sources and v in value_sources:
                s1 = value_sources[v][0]
                s2 = value_sources[other][0]
                matches.append({
                    'type': 'difference',
                    'formula': f"{v} - {other}",
                    'constants': [s1['const'], s2['const']],
                    'score': 7
                })
                if len(matches) > 40:
                    break

    # Recursive from previous m-values
    for i in range(2, target_n):
        mi = prev_m.get(i, 0)
        if mi == 0:
            continue

        # m[n] = m[i] × c (where c is convergent)
        if target_m % mi == 0:
            c = target_m // mi
            if c in value_sources:
                src = value_sources[c][0]
                matches.append({
                    'type': 'recursive_product',
                    'formula': f"m[{i}] × {c} (= {mi} × {c})",
                    'constants': [src['const']],
                    'score': 9
                })

        # m[n] = m[i] + c
        c = target_m - mi
        if c > 0 and c in value_sources:
            src = value_sources[c][0]
            matches.append({
                'type': 'recursive_sum',
                'formula': f"m[{i}] + {c} (= {mi} + {c})",
                'constants': [src['const']],
                'score': 9
            })

        # m[n] = d[n] × m[i] + c
        if d_n > 0:
            scaled = d_n * mi
            c = target_m - scaled
            if c > 0 and c in value_sources:
                src = value_sources[c][0]
                matches.append({
                    'type': 'recursive_scaled',
                    'formula': f"d[{target_n}] × m[{i}] + {c} (= {d_n} × {mi} + {c})",
                    'constants': [src['const']],
                    'score': 9
                })

    # Check for m[n] = m[i] + m[j]
    for i in range(2, target_n):
        for j in range(i, target_n):
            if prev_m.get(i, 0) + prev_m.get(j, 0) == target_m:
                matches.append({
                    'type': 'recursive_double_sum',
                    'formula': f"m[{i}] + m[{j}] (= {prev_m[i]} + {prev_m[j]})",
                    'constants': [],
                    'score': 10  # Pure recursion is elegant
                })

    # Check for 2^k + m[i] patterns
    for k in range(4, 30):
        power = 2**k
        if power > target_m:
            break
        remainder = target_m - power
        if remainder in prev_m.values():
            for idx, val in prev_m.items():
                if val == remainder:
                    matches.append({
                        'type': 'power_plus_m',
                        'formula': f"2^{k} + m[{idx}] (= {power} + {val})",
                        'constants': [],
                        'score': 9
                    })
                    break

    # Check if target contains prime 17 (Fermat prime network)
    factors = factorize(target_m)
    factor_dict = dict(factors)
    if 17 in factor_dict:
        matches.append({
            'type': 'fermat_network',
            'formula': f"Contains Fermat prime 17 = 2^4 + 1 (factor: 17^{factor_dict[17]})",
            'constants': [],
            'score': 6
        })

    return sorted(matches, key=lambda x: -x['score'])

def validate_m16_to_m31():
    """Main validation function."""
    print("=" * 80)
    print("VALIDATING CONVERGENT FORMULAS FOR m[16] through m[31]")
    print("=" * 80)

    print("\nBuilding extended convergent database (300 terms, 12 constants)...")
    database = build_full_database(300)
    print(f"Constants: {list(database.keys())}")

    print("\nExtracting convergent values...")
    values, value_sources = extract_all_values(database, max_value=10**12)
    print(f"Total unique values extracted: {len(values)}")

    results = {}
    coverage_count = 0

    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)

    for n in range(16, 32):
        m_val = M_SEQUENCE_EXTENDED[n]
        d_val = D_SEQ_EXTENDED.get(n, 1)

        print(f"\n{'─' * 70}")
        print(f"n={n:2d}  m[n]={m_val:>12,}  d[n]={d_val}")
        print(f"{'─' * 70}")

        # Factorize
        factors = factorize(m_val)
        factor_str = " × ".join([f"{p}^{e}" if e > 1 else str(p) for p, e in factors])
        print(f"Factorization: {factor_str}")

        # Search for matches
        matches = search_matches(n, m_val, values, value_sources, M_SEQUENCE_EXTENDED)

        if matches:
            coverage_count += 1
            print(f"\n✓ MATCHES FOUND ({len(matches)} total):")
            shown = set()
            for match in matches[:5]:  # Show top 5
                key = match['formula']
                if key not in shown:
                    shown.add(key)
                    consts = ", ".join(match['constants']) if match['constants'] else "recursive"
                    print(f"  [{match['score']:2d}] {match['type']:20s}: {match['formula']}")
                    print(f"       Constants: {consts}")

            results[n] = {
                'm_value': m_val,
                'd_value': d_val,
                'match_count': len(matches),
                'best_match': matches[0]
            }
        else:
            print(f"\n✗ NO DIRECT MATCHES FOUND")
            print(f"  Need extended search (triple operations, exotic constants)")
            results[n] = {
                'm_value': m_val,
                'd_value': d_val,
                'match_count': 0,
                'best_match': None
            }

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total = 16  # n=16 to n=31
    print(f"\nCoverage: {coverage_count}/{total} = {100*coverage_count/total:.1f}%")

    print("\nBest matches by n:")
    for n in range(16, 32):
        if results[n]['best_match']:
            m = results[n]['best_match']
            print(f"  n={n:2d}: {m['type']:20s} → {m['formula'][:50]}")
        else:
            print(f"  n={n:2d}: NO MATCH")

    # Check d=4 pattern (sum operations)
    print("\nPattern check: d[n]=4 correlates with sum operations?")
    d4_indices = [n for n in range(16, 32) if D_SEQ_EXTENDED.get(n) == 4]
    print(f"  d=4 at n={d4_indices}")
    for n in d4_indices:
        if results[n]['best_match']:
            t = results[n]['best_match']['type']
            print(f"    n={n}: {t}")

    # Check prime 17 network
    print("\nPrime 17 (Fermat) network in m[16]-m[31]:")
    for n in range(16, 32):
        m_val = M_SEQUENCE_EXTENDED[n]
        if m_val % 17 == 0:
            print(f"  m[{n}] = {m_val} = 17 × {m_val//17}")

    return results

if __name__ == "__main__":
    validate_m16_to_m31()
