#!/usr/bin/env python3
"""
Investigate if m[n] can be constructed from π, e, and φ convergents.

VERIFIED: m[4]/m[3] = 22/7 (π convergent)

Goal: Find a FORMULA that generates m[n] for ANY n.
"""

from fractions import Fraction
from typing import List, Tuple
import math

# Known m-sequence from database
m_seq = {
    2: 3, 3: 7, 4: 22, 5: 27, 6: 57, 7: 150, 8: 184, 9: 493,
    10: 1444, 11: 1921, 12: 3723, 13: 8342, 14: 16272, 15: 26989,
    16: 67760, 17: 138269, 18: 255121, 19: 564091, 20: 900329
}

def continued_fraction_pi(max_terms=20):
    """Generate continued fraction for π."""
    # π = [3; 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2, ...]
    cf = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2,
          1, 84, 2, 1, 1, 15, 3, 13, 1, 4, 2, 6, 6, 1, 1, 1, 8, 1, 1, 3]
    return cf[:max_terms]

def continued_fraction_e(max_terms=30):
    """Generate continued fraction for e."""
    # e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, ...]
    # Pattern: [2; 1, 2k, 1] for k=1,2,3,...
    cf = [2]
    for k in range(1, max_terms):
        cf.extend([1, 2*k, 1])
        if len(cf) >= max_terms:
            break
    return cf[:max_terms]

def continued_fraction_phi(max_terms=30):
    """Generate continued fraction for φ (golden ratio)."""
    # φ = [1; 1, 1, 1, 1, ...]
    return [1] * max_terms

def convergents_from_cf(cf: List[int]) -> List[Tuple[int, int]]:
    """Convert continued fraction to convergents."""
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

# Generate convergents
pi_cf = continued_fraction_pi(40)
e_cf = continued_fraction_e(40)
phi_cf = continued_fraction_phi(40)

pi_conv = convergents_from_cf(pi_cf)
e_conv = convergents_from_cf(e_cf)
phi_conv = convergents_from_cf(phi_cf)

print("=" * 80)
print("CONVERGENTS OF π, e, AND φ")
print("=" * 80)

print("\nπ convergents (first 15):")
for i, (num, den) in enumerate(pi_conv[:15]):
    val = num / den
    print(f"  [{i}] {num}/{den} = {val:.10f} (error: {abs(val - math.pi):.2e})")

print("\ne convergents (first 15):")
for i, (num, den) in enumerate(e_conv[:15]):
    val = num / den
    print(f"  [{i}] {num}/{den} = {val:.10f} (error: {abs(val - math.e):.2e})")

print("\nφ convergents (first 15):")
phi = (1 + math.sqrt(5)) / 2
for i, (num, den) in enumerate(phi_conv[:15]):
    val = num / den
    print(f"  [{i}] {num}/{den} = {val:.10f} (error: {abs(val - phi):.2e})")

print("\n" + "=" * 80)
print("ANALYSIS: m[n] vs CONVERGENT COMPONENTS")
print("=" * 80)

# Create lookup dictionaries for convergent parts
pi_nums = {num for num, _ in pi_conv}
pi_dens = {den for _, den in pi_conv}
e_nums = {num for num, _ in e_conv}
e_dens = {den for _, den in e_conv}
phi_nums = {num for num, _ in phi_conv}
phi_dens = {den for _, den in phi_conv}

# Check exact matches
print("\nEXACT MATCHES:")
for n, m in sorted(m_seq.items()):
    matches = []
    if m in pi_nums:
        matches.append(f"π_num[{[i for i,(num,_) in enumerate(pi_conv) if num==m][0]}]")
    if m in pi_dens:
        matches.append(f"π_den[{[i for i,(_,den) in enumerate(pi_conv) if den==m][0]}]")
    if m in e_nums:
        matches.append(f"e_num[{[i for i,(num,_) in enumerate(e_conv) if num==m][0]}]")
    if m in e_dens:
        matches.append(f"e_den[{[i for i,(_,den) in enumerate(e_conv) if den==m][0]}]")
    if m in phi_nums:
        matches.append(f"φ_num[{[i for i,(num,_) in enumerate(phi_conv) if num==m][0]}]")
    if m in phi_dens:
        matches.append(f"φ_den[{[i for i,(_,den) in enumerate(phi_conv) if den==m][0]}]")

    if matches:
        print(f"  m[{n}] = {m:7d} = {', '.join(matches)}")

print("\n" + "=" * 80)
print("HYPOTHESIS TESTING: LINEAR COMBINATIONS")
print("=" * 80)

def test_linear_combinations(n: int, target: int, max_depth=10):
    """Test if target can be expressed as combination of convergents."""
    findings = []

    # Test single convergent components
    for i in range(min(max_depth, len(pi_conv))):
        pi_n, pi_d = pi_conv[i]
        e_n, e_d = e_conv[i] if i < len(e_conv) else (0, 0)
        phi_n, phi_d = phi_conv[i] if i < len(phi_conv) else (0, 0)

        # Test simple operations
        candidates = [
            (pi_n, f"π_num[{i}]"),
            (pi_d, f"π_den[{i}]"),
            (e_n, f"e_num[{i}]"),
            (e_d, f"e_den[{i}]"),
            (phi_n, f"φ_num[{i}]"),
            (phi_d, f"φ_den[{i}]"),
            (pi_n + pi_d, f"π_num[{i}] + π_den[{i}]"),
            (pi_n - pi_d, f"π_num[{i}] - π_den[{i}]"),
            (pi_n * 2, f"2 × π_num[{i}]"),
            (pi_d * 2, f"2 × π_den[{i}]"),
            (pi_n + e_n, f"π_num[{i}] + e_num[{i}]"),
            (pi_n + phi_n, f"π_num[{i}] + φ_num[{i}]"),
        ]

        for val, formula in candidates:
            if val == target:
                findings.append(formula)

    # Test pairwise combinations
    for i in range(min(5, len(pi_conv))):
        for j in range(min(5, len(pi_conv))):
            if i == j:
                continue
            pi_ni, pi_di = pi_conv[i]
            pi_nj, pi_dj = pi_conv[j]

            candidates = [
                (pi_ni + pi_nj, f"π_num[{i}] + π_num[{j}]"),
                (pi_ni * pi_dj, f"π_num[{i}] × π_den[{j}]"),
                (pi_di * pi_nj, f"π_den[{i}] × π_num[{j}]"),
            ]

            for val, formula in candidates:
                if val == target:
                    findings.append(formula)

    return findings

print("\nSearching for construction formulas...")
for n in sorted(m_seq.keys())[:10]:  # Test first 10
    m = m_seq[n]
    formulas = test_linear_combinations(n, m)
    if formulas:
        print(f"\nm[{n}] = {m}")
        for f in formulas[:5]:  # Show first 5 matches
            print(f"  ✓ {f}")

print("\n" + "=" * 80)
print("PATTERN DETECTION: INDEXED ACCESS")
print("=" * 80)

print("\nTesting if m[n] uses convergent[n] or convergent[f(n)]...")
print()
print("n  | m[n]     | π_num[n] | π_den[n] | e_num[n] | e_den[n] | φ_num[n] | φ_den[n]")
print("-" * 85)

for n in sorted(m_seq.keys())[:12]:
    m = m_seq[n]

    # Get convergents at index n (if available)
    pi_n, pi_d = pi_conv[n] if n < len(pi_conv) else (None, None)
    e_n, e_d = e_conv[n] if n < len(e_conv) else (None, None)
    phi_n, phi_d = phi_conv[n] if n < len(phi_conv) else (None, None)

    print(f"{n:2d} | {m:8d} | {pi_n or 'N/A':8} | {pi_d or 'N/A':8} | "
          f"{e_n or 'N/A':8} | {e_d or 'N/A':8} | {phi_n or 'N/A':8} | {phi_d or 'N/A':8}")

print("\n" + "=" * 80)
print("ADVANCED: RATIO AND RECURRENCE TESTING")
print("=" * 80)

print("\nRatios m[n+1]/m[n]:")
for n in sorted(m_seq.keys())[:-1]:
    if n + 1 in m_seq:
        ratio = m_seq[n+1] / m_seq[n]
        print(f"  m[{n+1}]/m[{n}] = {ratio:.6f}")

print("\nRecurrence relation tests (m[n] = a×m[n-1] + b×m[n-2]):")
for n in sorted(m_seq.keys())[2:10]:
    if n-1 in m_seq and n-2 in m_seq:
        m_n = m_seq[n]
        m_n1 = m_seq[n-1]
        m_n2 = m_seq[n-2]

        # Solve for a, b
        # m[n] = a×m[n-1] + b×m[n-2]
        # Try integer solutions
        for a in range(-5, 10):
            for b in range(-10, 10):
                if a * m_n1 + b * m_n2 == m_n:
                    print(f"  m[{n}] = {a}×m[{n-1}] + {b}×m[{n-2}]")
                    break

print("\n" + "=" * 80)
print("CONSTRUCTION FORMULA SEARCH")
print("=" * 80)

def search_formula_with_convergents(n: int, target: int):
    """Search for formula: m[n] = f(convergent[g(n)])"""
    findings = []

    # Test different index mappings
    index_maps = [
        (n, "n"),
        (n-2, "n-2"),
        (n//2, "n//2"),
        ((n+1)//2, "(n+1)//2"),
        (n%10, "n%10"),
    ]

    for idx, idx_name in index_maps:
        if idx < 0 or idx >= len(pi_conv):
            continue

        pi_n, pi_d = pi_conv[idx]
        e_n, e_d = e_conv[idx] if idx < len(e_conv) else (0, 0)
        phi_n, phi_d = phi_conv[idx] if idx < len(phi_conv) else (0, 0)

        # Test various formulas
        tests = [
            (pi_n, f"π_num[{idx_name}]"),
            (pi_d, f"π_den[{idx_name}]"),
            (pi_n + n, f"π_num[{idx_name}] + n"),
            (pi_d + n, f"π_den[{idx_name}] + n"),
            (pi_n * n, f"π_num[{idx_name}] × n"),
            (n * pi_d, f"n × π_den[{idx_name}]"),
            (pi_n + pi_d, f"π_num[{idx_name}] + π_den[{idx_name}]"),
            (pi_n * e_n, f"π_num[{idx_name}] × e_num[{idx_name}]"),
        ]

        for val, formula in tests:
            if val == target:
                findings.append(formula)

    return findings

print("\nSearching for indexed convergent formulas...")
for n in sorted(m_seq.keys())[:10]:
    m = m_seq[n]
    formulas = search_formula_with_convergents(n, m)
    if formulas:
        print(f"\nm[{n}] = {m}")
        for f in set(formulas[:3]):
            print(f"  ✓ {f}")

print("\n" + "=" * 80)
print("SUMMARY: CONVERGENT CONSTRUCTION INVESTIGATION")
print("=" * 80)
print("""
KEY FINDINGS:
1. m[3]=7 = π_den[1] (exact match!)
2. m[4]=22 = π_num[1] (exact match!)
3. m[4]/m[3] = 22/7 = first convergent of π

NEXT STEPS:
- Investigate if m[n] uses convergent[f(n)] for some function f
- Test combinations of multiple convergent systems
- Look for recurrence relations involving convergent indices
""")
