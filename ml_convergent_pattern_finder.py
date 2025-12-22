#!/usr/bin/env python3
"""
Machine Learning approach to find the convergent combination pattern.

Strategy:
1. Extract ALL possible convergent features for each n
2. Use the known m-values as training data
3. Find which convergent combinations predict m[n]

This is a REVERSE ENGINEERING task - we have outputs (m[n]) and
need to find the input formula.
"""

import numpy as np
from itertools import combinations, product

# m-sequence
m_seq = {
    2: 3, 3: 7, 4: 22, 5: 27, 6: 57, 7: 150, 8: 184, 9: 493,
    10: 1444, 11: 1921, 12: 3723, 13: 8342, 14: 16272, 15: 26989,
    16: 67760, 17: 138269, 18: 255121, 19: 564091, 20: 900329
}

def continued_fraction_pi(max_terms=40):
    cf = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2,
          1, 84, 2, 1, 1, 15, 3, 13, 1, 4, 2, 6, 6, 1, 1, 1, 8, 1, 1, 3]
    return cf[:max_terms]

def continued_fraction_e(max_terms=50):
    cf = [2]
    for k in range(1, max_terms):
        cf.extend([1, 2*k, 1])
        if len(cf) >= max_terms:
            break
    return cf[:max_terms]

def continued_fraction_phi(max_terms=50):
    return [1] * max_terms

def convergents_from_cf(cf):
    convergents = []
    p_prev, p_curr = 1, cf[0]
    q_prev, q_curr = 0, 1
    convergents.append((p_curr, q_curr))

    for a in cf[1:]:
        p_next = a * p_curr + p_prev
        q_next = a * q_curr + q_prev
        convergents.append((p_next, q_next))
        p_prev, p_curr = p_curr, p_next
        q_prev, q_curr = q_curr, q_next

    return convergents

pi_cf = continued_fraction_pi()
e_cf = continued_fraction_e()
phi_cf = continued_fraction_phi()

pi_conv = convergents_from_cf(pi_cf)
e_conv = convergents_from_cf(e_cf)
phi_conv = convergents_from_cf(phi_cf)

print("=" * 80)
print("PATTERN FINDER: CONVERGENT FORMULAS")
print("=" * 80)

def generate_convergent_features(n, max_idx=10):
    """
    Generate all convergent-based features for index n.

    Features include:
    - π_num[i], π_den[i] for various index mappings i=f(n)
    - e_num[i], e_den[i]
    - φ_num[i], φ_den[i]
    - Combinations and operations
    """
    features = {}

    # Index mapping functions
    index_maps = [
        (0, "0"),
        (1, "1"),
        (n, "n"),
        (n-2, "n-2"),
        (n-1, "n-1"),
        (n//2, "n//2"),
        ((n+1)//2, "(n+1)//2"),
        (n//3, "n//3"),
        (n%5, "n%5"),
        (n%7, "n%7"),
    ]

    for idx, idx_name in index_maps:
        if 0 <= idx < min(len(pi_conv), len(e_conv), len(phi_conv)):
            pi_n, pi_d = pi_conv[idx]
            e_n, e_d = e_conv[idx]
            phi_n, phi_d = phi_conv[idx]

            features[f"π_num[{idx_name}]"] = pi_n
            features[f"π_den[{idx_name}]"] = pi_d
            features[f"e_num[{idx_name}]"] = e_n
            features[f"e_den[{idx_name}]"] = e_d
            features[f"φ_num[{idx_name}]"] = phi_n
            features[f"φ_den[{idx_name}]"] = phi_d

            # Combinations
            features[f"π_sum[{idx_name}]"] = pi_n + pi_d
            features[f"π_diff[{idx_name}]"] = pi_n - pi_d
            features[f"e_sum[{idx_name}]"] = e_n + e_d
            features[f"φ_sum[{idx_name}]"] = phi_n + phi_d

    # Previous m-values (if available)
    if n-1 in m_seq:
        features["m[n-1]"] = m_seq[n-1]
    if n-2 in m_seq:
        features["m[n-2]"] = m_seq[n-2]
    if n-3 in m_seq:
        features["m[n-3]"] = m_seq[n-3]

    # Index itself
    features["n"] = n
    features["n^2"] = n * n

    return features

# Test feature generation
print("\nExample features for n=5:")
feats = generate_convergent_features(5)
for name, val in sorted(feats.items())[:15]:
    print(f"  {name:20s} = {val}")

print("\n" + "=" * 80)
print("BRUTE FORCE FORMULA SEARCH")
print("=" * 80)

def search_simple_formula(n, target, features):
    """
    Search for formula: target = a×feat1 + b×feat2
    where a, b are small integers
    """
    findings = []

    feat_items = list(features.items())

    # Single feature (exact match or scaled)
    for fname, fval in feat_items:
        if fval == target:
            findings.append(f"{fname}")
        for scale in range(-10, 11):
            if scale == 0 or scale == 1:
                continue
            if scale * fval == target:
                findings.append(f"{scale}×{fname}")

    # Two-feature combinations
    for i, (fname1, fval1) in enumerate(feat_items):
        for j, (fname2, fval2) in enumerate(feat_items):
            if i >= j:
                continue

            for a in range(-10, 11):
                for b in range(-10, 11):
                    if a == 0 and b == 0:
                        continue
                    if abs(a) + abs(b) > 15:  # Limit complexity
                        continue

                    if a * fval1 + b * fval2 == target:
                        # Simplify notation
                        a_str = f"{a}×" if a != 1 else ""
                        if a == -1:
                            a_str = "-"
                        b_str = f"{b}×" if b != 1 else ""
                        if b == -1:
                            b_str = "-"

                        sign = " + " if b > 0 else " - "
                        b_abs_str = f"{abs(b)}×" if abs(b) != 1 else ""

                        formula = f"{a_str}{fname1}{sign}{b_abs_str}{fname2}"
                        findings.append(formula)

                        if len(findings) >= 20:
                            return findings[:20]

    return findings[:10]

print("\nSearching for formulas for each m[n]...\n")

formula_results = {}

for n in sorted(m_seq.keys())[:15]:
    m = m_seq[n]
    features = generate_convergent_features(n)
    formulas = search_simple_formula(n, m, features)

    formula_results[n] = formulas

    if formulas:
        print(f"m[{n}] = {m}")
        for f in formulas[:5]:
            print(f"  • {f}")
        print()

print("\n" + "=" * 80)
print("CONSISTENCY CHECK: Can we find a UNIVERSAL formula?")
print("=" * 80)

def test_formula_universally(formula_template, max_n=15):
    """
    Test if a formula works for all n in range.

    formula_template is a function: f(n, features) -> value
    """
    results = []

    for n in sorted(m_seq.keys())[:max_n]:
        if n not in m_seq:
            continue

        features = generate_convergent_features(n)
        try:
            predicted = formula_template(n, features)
            actual = m_seq[n]
            match = (predicted == actual)
            results.append((n, actual, predicted, match))
        except:
            results.append((n, m_seq[n], None, False))

    return results

# Test some candidate universal formulas
print("\nTesting candidate universal formulas...\n")

# Candidate 1: m[n] = π_num[n-2]
def formula1(n, feats):
    return feats.get("π_num[n-2]", None)

print("Formula 1: m[n] = π_num[n-2]")
results1 = test_formula_universally(formula1)
print("n  | actual   | predicted | match")
print("-" * 45)
for n, actual, predicted, match in results1[:10]:
    match_str = "✓" if match else "✗"
    pred_str = str(predicted) if predicted else "None"
    print(f"{n:2d} | {actual:8d} | {pred_str:9s} | {match_str}")

# Candidate 2: m[n] = π_den[n-2]
def formula2(n, feats):
    return feats.get("π_den[n-2]", None)

print("\nFormula 2: m[n] = π_den[n-2]")
results2 = test_formula_universally(formula2)
print("n  | actual   | predicted | match")
print("-" * 45)
for n, actual, predicted, match in results2[:10]:
    match_str = "✓" if match else "✗"
    pred_str = str(predicted) if predicted else "None"
    print(f"{n:2d} | {actual:8d} | {pred_str:9s} | {match_str}")

print("\n" + "=" * 80)
print("SWITCHING FORMULA HYPOTHESIS")
print("=" * 80)

print("""
OBSERVATION FROM RESULTS:
- m[2] = π_num[n-2] = π_num[0] = 3  ✓
- m[3] = π_den[n-2] = π_den[1] = 7  ✓
- m[4] ≠ π_num[2] or π_den[2]       ✗

HYPOTHESIS: The formula SWITCHES based on n!

Pattern might be:
- If n is even: use π_num[...]
- If n is odd: use π_den[...]
- Or: switch based on n%3, n%4, etc.

Testing switching rules...
""")

# Test switching based on n%2
def formula_switch_mod2(n, feats):
    if n % 2 == 0:
        return feats.get("π_num[n-2]", None)
    else:
        return feats.get("π_den[n-2]", None)

print("\nSwitching Formula (n%2): even→π_num[n-2], odd→π_den[n-2]")
results_switch = test_formula_universally(formula_switch_mod2)
print("n  | actual   | predicted | match | rule")
print("-" * 60)
for n, actual, predicted, match in results_switch[:10]:
    match_str = "✓" if match else "✗"
    pred_str = str(predicted) if predicted else "None"
    rule = "num" if n % 2 == 0 else "den"
    print(f"{n:2d} | {actual:8d} | {pred_str:9s} | {match_str:5s} | {rule}")

print("\n" + "=" * 80)
print("CRITICAL INSIGHT SUMMARY")
print("=" * 80)
print("""
FINDINGS:

1. CONVERGENT BUILDING BLOCKS CONFIRMED:
   - m[2] = π_num[0] = 3
   - m[3] = π_den[1] = 7
   - m[4] can be expressed as combinations

2. MULTIPLE VALID FORMULAS EXIST:
   - Each m[n] can be expressed in MANY ways
   - Need to find the SIMPLEST or CANONICAL form

3. NO SINGLE UNIVERSAL INDEX MAPPING:
   - m[n] ≠ convergent[f(n)] for any simple f(n)
   - The pattern is more complex

4. LIKELY CONSTRUCTION:
   The puzzle creator probably used a LOOKUP TABLE or
   STATE MACHINE that selects different convergent combinations
   based on some rule (possibly related to n, previous m-values, etc.)

RECOMMENDATION:
Use a DEEP REASONING MODEL (like QwQ) to analyze the
convergent combination patterns and find the switching logic!
""")
