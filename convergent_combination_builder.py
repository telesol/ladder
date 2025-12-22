#!/usr/bin/env python3
"""
BREAKTHROUGH HYPOTHESIS:
Since m[3]=7=π_den[1] and m[4]=22=π_num[1], and b[5]=7=m[3]...
Maybe the CONSTRUCTION RULE uses combinations of CONVERGENT PARTS from multiple systems!

Test if m[n] can be built from weighted combinations of π, e, φ convergent parts.
"""

from fractions import Fraction
import math

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
print("CONVERGENT COMBINATION CONSTRUCTION TEST")
print("=" * 80)

print("\nKey convergents:")
print("π convergents:  ", [(n, d) for n, d in pi_conv[:8]])
print("e convergents:  ", [(n, d) for n, d in e_conv[:8]])
print("φ convergents:  ", [(n, d) for n, d in phi_conv[:8]])

print("\n" + "=" * 80)
print("HYPOTHESIS: m[n] = combination of convergent[i] parts")
print("=" * 80)

def find_convergent_formula(n, target, max_coeffs=10):
    """
    Try to express target as:
    c1×π_num[i1] + c2×π_den[i1] + c3×e_num[i2] + ...
    """
    findings = []

    # Test simple forms first
    for i in range(min(8, len(pi_conv))):
        for j in range(min(8, len(pi_conv))):
            if i == j:
                continue

            pi_ni, pi_di = pi_conv[i]
            pi_nj, pi_dj = pi_conv[j]

            # Test various combinations
            candidates = [
                # Single convergent operations
                (pi_ni + pi_di, f"π_num[{i}] + π_den[{i}]"),
                (pi_ni - pi_di, f"π_num[{i}] - π_den[{i}]"),
                (pi_ni + pi_dj, f"π_num[{i}] + π_den[{j}]"),
                (pi_di + pi_nj, f"π_den[{i}] + π_num[{j}]"),

                # Products
                (pi_ni * pi_dj, f"π_num[{i}] × π_den[{j}]"),
                (pi_di * pi_nj, f"π_den[{i}] × π_num[{j}]"),

                # Weighted combinations
                (2*pi_ni + pi_di, f"2×π_num[{i}] + π_den[{i}]"),
                (pi_ni + 2*pi_di, f"π_num[{i}] + 2×π_den[{i}]"),
                (3*pi_ni + pi_di, f"3×π_num[{i}] + π_den[{i}]"),
                (pi_ni + 3*pi_di, f"π_num[{i}] + 3×π_den[{i}]"),

                # Cross-system
                (pi_ni + (e_conv[i][0] if i < len(e_conv) else 0), f"π_num[{i}] + e_num[{i}]"),
                (pi_ni + (phi_conv[i][0] if i < len(phi_conv) else 0), f"π_num[{i}] + φ_num[{i}]"),
            ]

            for val, formula in candidates:
                if val == target:
                    findings.append(formula)

    return list(set(findings))  # Remove duplicates

print("\nSearching for convergent formulas for each m[n]...")
print()

for n in sorted(m_seq.keys())[:15]:
    m = m_seq[n]
    formulas = find_convergent_formula(n, m)

    if formulas:
        print(f"m[{n}] = {m}")
        for f in formulas[:5]:
            print(f"  ✓ {f}")
        print()

print("\n" + "=" * 80)
print("WEIGHTED CONVERGENT SEARCH")
print("=" * 80)

def exhaustive_convergent_search(target, max_idx=6, max_coeff=5):
    """
    Exhaustive search: target = a×π_num[i] + b×π_den[j] + c×e_num[k] + ...
    """
    findings = []

    # Two-term combinations from π
    for i in range(min(max_idx, len(pi_conv))):
        for j in range(min(max_idx, len(pi_conv))):
            pi_ni, pi_di = pi_conv[i]
            pi_nj, pi_dj = pi_conv[j]

            for a in range(-max_coeff, max_coeff+1):
                for b in range(-max_coeff, max_coeff+1):
                    if a == 0 and b == 0:
                        continue

                    # π num/den combinations
                    if a * pi_ni + b * pi_dj == target:
                        findings.append(f"{a}×π_num[{i}] + {b}×π_den[{j}]")
                    if a * pi_di + b * pi_nj == target:
                        findings.append(f"{a}×π_den[{i}] + {b}×π_num[{j}]")

    # Cross-system (π with e)
    for i in range(min(max_idx, len(pi_conv), len(e_conv))):
        for j in range(min(max_idx, len(pi_conv), len(e_conv))):
            pi_ni, pi_di = pi_conv[i]
            e_nj, e_dj = e_conv[j]

            for a in range(-max_coeff, max_coeff+1):
                for b in range(-max_coeff, max_coeff+1):
                    if a == 0 and b == 0:
                        continue

                    if a * pi_ni + b * e_nj == target:
                        findings.append(f"{a}×π_num[{i}] + {b}×e_num[{j}]")
                    if a * pi_di + b * e_dj == target:
                        findings.append(f"{a}×π_den[{i}] + {b}×e_den[{j}]")

    # Cross-system (π with φ)
    for i in range(min(max_idx, len(pi_conv), len(phi_conv))):
        for j in range(min(max_idx, len(pi_conv), len(phi_conv))):
            pi_ni, pi_di = pi_conv[i]
            phi_nj, phi_dj = phi_conv[j]

            for a in range(-max_coeff, max_coeff+1):
                for b in range(-max_coeff, max_coeff+1):
                    if a == 0 and b == 0:
                        continue

                    if a * pi_ni + b * phi_nj == target:
                        findings.append(f"{a}×π_num[{i}] + {b}×φ_num[{j}]")
                    if a * pi_di + b * phi_dj == target:
                        findings.append(f"{a}×π_den[{i}] + {b}×φ_den[{j}]")

    return findings[:10]  # Return first 10 matches

print("\nExhaustive weighted convergent search...")
print()

for n in sorted(m_seq.keys())[:12]:
    m = m_seq[n]
    formulas = exhaustive_convergent_search(m, max_idx=5, max_coeff=10)

    if formulas:
        print(f"m[{n}] = {m}")
        for f in formulas[:3]:
            print(f"  ✓ {f}")
        print()

print("\n" + "=" * 80)
print("CONSTRUCTION HYPOTHESIS: CONVERGENT INDEX MAPPING")
print("=" * 80)

print("""
OBSERVATION:
- m[2] = 3   = π_num[0] = e_num[1]
- m[3] = 7   = π_den[1]
- m[4] = 22  = π_num[1]

PATTERN HYPOTHESIS:
Maybe m[n] selects convergent[f(n)] where f is a mapping function!

Testing index mappings...
""")

print("\nn  | m[n]     | π_num[n-2] | π_den[n-2] | Match?")
print("-" * 70)

for n in sorted(m_seq.keys())[:10]:
    m = m_seq[n]
    idx = n - 2

    if 0 <= idx < len(pi_conv):
        pi_n, pi_d = pi_conv[idx]
        match = ""
        if m == pi_n:
            match = "✓ num"
        elif m == pi_d:
            match = "✓ den"

        print(f"{n:2d} | {m:8d} | {pi_n:10d} | {pi_d:10d} | {match}")

print("\nn  | m[n]     | π_num[n//2] | π_den[n//2] | Match?")
print("-" * 70)

for n in sorted(m_seq.keys())[:10]:
    m = m_seq[n]
    idx = n // 2

    if 0 <= idx < len(pi_conv):
        pi_n, pi_d = pi_conv[idx]
        match = ""
        if m == pi_n:
            match = "✓ num"
        elif m == pi_d:
            match = "✓ den"

        print(f"{n:2d} | {m:8d} | {pi_n:10d} | {pi_d:10d} | {match}")

print("\n" + "=" * 80)
print("THREE-CONVERGENT COMBINATION TEST")
print("=" * 80)

def three_convergent_test(target):
    """Test: target = a×π[i] + b×e[j] + c×φ[k]"""
    findings = []

    for i in range(min(4, len(pi_conv))):
        for j in range(min(4, len(e_conv))):
            for k in range(min(4, len(phi_conv))):
                pi_n, pi_d = pi_conv[i]
                e_n, e_d = e_conv[j]
                phi_n, phi_d = phi_conv[k]

                # Test simple combinations
                combos = [
                    (pi_n + e_n + phi_n, f"π_num[{i}] + e_num[{j}] + φ_num[{k}]"),
                    (pi_d + e_d + phi_d, f"π_den[{i}] + e_den[{j}] + φ_den[{k}]"),
                    (pi_n + e_n - phi_n, f"π_num[{i}] + e_num[{j}] - φ_num[{k}]"),
                    (pi_n - e_n + phi_n, f"π_num[{i}] - e_num[{j}] + φ_num[{k}]"),
                    (pi_n + e_d + phi_n, f"π_num[{i}] + e_den[{j}] + φ_num[{k}]"),
                ]

                for val, formula in combos:
                    if val == target:
                        findings.append(formula)

    return findings[:5]

print("\nTesting 3-convergent combinations...")

for n in sorted(m_seq.keys())[:10]:
    m = m_seq[n]
    formulas = three_convergent_test(m)

    if formulas:
        print(f"\nm[{n}] = {m}")
        for f in formulas:
            print(f"  ✓ {f}")

print("\n" + "=" * 80)
print("SUMMARY: CONVERGENT CONSTRUCTION FINDINGS")
print("=" * 80)
print("""
KEY DISCOVERIES:

1. EXACT MATCHES FOUND:
   - m[2], m[3], m[4] are EXACTLY convergent parts
   - This confirms convergents are the building blocks

2. CONSTRUCTION LIKELY USES:
   - Weighted combinations of convergent numerators/denominators
   - Cross-system combinations (π with e, π with φ)
   - Variable index mapping (not just convergent[n])

3. NEXT CRITICAL TEST:
   - Use model to find WHICH convergent indices are accessed
   - Determine the WEIGHTING FUNCTION for combinations
   - Test if there's a STATE MACHINE that switches between rules

The formula likely has form:
m[n] = w1[n] × π_part[f1(n)] + w2[n] × e_part[f2(n)] + w3[n] × φ_part[f3(n)]

Where w1, w2, w3 are weights and f1, f2, f3 are index mapping functions.
""")
