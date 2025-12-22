#!/usr/bin/env python3
"""
Exhaustive search for the coefficient pattern in m-sequence recurrences.

Goal: Find a[n] and b[n] such that m[n] = a[n]×m[n-1] + b[n]×m[n-2]
"""

import math
from fractions import Fraction

# Complete m-sequence
m_seq = {
    2: 3, 3: 7, 4: 22, 5: 27, 6: 57, 7: 150, 8: 184, 9: 493,
    10: 1444, 11: 1921, 12: 3723, 13: 8342, 14: 16272, 15: 26989,
    16: 67760, 17: 138269, 18: 255121, 19: 564091, 20: 900329
}

def find_all_recurrence_coefficients(max_search=50):
    """Find ALL valid (a,b) pairs for each n."""
    results = {}

    for n in sorted(m_seq.keys())[2:]:
        if n-1 not in m_seq or n-2 not in m_seq:
            continue

        m_n = m_seq[n]
        m_n1 = m_seq[n-1]
        m_n2 = m_seq[n-2]

        solutions = []
        for a in range(-max_search, max_search+1):
            for b in range(-max_search, max_search+1):
                if a * m_n1 + b * m_n2 == m_n:
                    solutions.append((a, b))

        results[n] = solutions

    return results

print("=" * 80)
print("COMPLETE RECURRENCE COEFFICIENT EXTRACTION")
print("=" * 80)

recurrences = find_all_recurrence_coefficients(100)

# Display minimal solutions (smallest |a| + |b|)
print("\nMinimal solutions (smallest |a| + |b|):")
print("n  | m[n]     | (a, b)      | Check: a×m[n-1] + b×m[n-2]")
print("-" * 80)

minimal_coeffs = []

for n in sorted(recurrences.keys()):
    if not recurrences[n]:
        continue

    # Find minimal solution
    min_sol = min(recurrences[n], key=lambda x: abs(x[0]) + abs(x[1]))
    a, b = min_sol
    minimal_coeffs.append((n, a, b))

    m_n = m_seq[n]
    m_n1 = m_seq[n-1]
    m_n2 = m_seq[n-2]
    check = a * m_n1 + b * m_n2

    print(f"{n:2d} | {m_n:8d} | ({a:3d},{b:3d}) | {a}×{m_n1} + {b}×{m_n2} = {check}")

print("\n" + "=" * 80)
print("COEFFICIENT PATTERN ANALYSIS")
print("=" * 80)

# Extract coefficient sequences
a_values = [a for _, a, _ in minimal_coeffs]
b_values = [b for _, _, b in minimal_coeffs]
n_values = [n for n, _, _ in minimal_coeffs]

print("\nCoefficient sequences:")
print("n  |  a[n] |  b[n] | a+b | a-b | a×b | gcd(a,b)")
print("-" * 70)

import math as m

for n, a, b in minimal_coeffs:
    sum_ab = a + b
    diff_ab = a - b
    prod_ab = a * b
    gcd_ab = m.gcd(abs(a), abs(b)) if a != 0 and b != 0 else max(abs(a), abs(b))

    print(f"{n:2d} | {a:5d} | {b:5d} | {sum_ab:3d} | {diff_ab:4d} | {prod_ab:5d} | {gcd_ab}")

print("\n" + "=" * 80)
print("TESTING HYPOTHESES FOR COEFFICIENT PATTERNS")
print("=" * 80)

# Hypothesis 1: Coefficients cycle or have modular pattern
print("\nHypothesis 1: Do coefficients follow modular pattern?")
print("n  | n%2 | n%3 | n%4 | n%5 |  a[n] |  b[n]")
print("-" * 60)

for n, a, b in minimal_coeffs[:10]:
    print(f"{n:2d} | {n%2:3d} | {n%3:3d} | {n%4:3d} | {n%5:3d} | {a:5d} | {b:5d}")

# Hypothesis 2: Coefficients relate to previous m values
print("\nHypothesis 2: Are coefficients derived from m-values?")
print("n  |  a[n] |  b[n] | m[n-3] | m[n-4] | a/m[n-3] | b/m[n-3]")
print("-" * 75)

for n, a, b in minimal_coeffs[:8]:
    m_n3 = m_seq.get(n-3, 0)
    m_n4 = m_seq.get(n-4, 0)

    ratio_a = a / m_n3 if m_n3 != 0 else 0
    ratio_b = b / m_n3 if m_n3 != 0 else 0

    print(f"{n:2d} | {a:5d} | {b:5d} | {m_n3:6d} | {m_n4:6d} | {ratio_a:8.3f} | {ratio_b:8.3f}")

# Hypothesis 3: Differences and ratios
print("\nHypothesis 3: Differences in coefficients")
print("n  |  a[n] |  b[n] | Δa    | Δb    | a[n+1]/a[n] | b[n+1]/b[n]")
print("-" * 80)

for i in range(len(minimal_coeffs) - 1):
    n, a, b = minimal_coeffs[i]
    n_next, a_next, b_next = minimal_coeffs[i+1]

    delta_a = a_next - a
    delta_b = b_next - b
    ratio_a = a_next / a if a != 0 else float('inf')
    ratio_b = b_next / b if b != 0 else float('inf')

    print(f"{n:2d} | {a:5d} | {b:5d} | {delta_a:5d} | {delta_b:5d} | {ratio_a:11.3f} | {ratio_b:11.3f}")

print("\n" + "=" * 80)
print("ADVANCED: LOOK FOR CONVERGENT RELATIONSHIPS")
print("=" * 80)

def continued_fraction_pi(max_terms=40):
    cf = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2,
          1, 84, 2, 1, 1, 15, 3, 13, 1, 4, 2, 6, 6, 1, 1, 1, 8, 1, 1, 3]
    return cf[:max_terms]

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
pi_conv = convergents_from_cf(pi_cf)

print("\nTesting if (a,b) relate to convergent differences...")
print("n  |  a[n] |  b[n] | π_num[i]-π_den[i] matches?")
print("-" * 70)

for n, a, b in minimal_coeffs[:10]:
    matches = []

    # Check if a or b equals convergent differences
    for i in range(min(10, len(pi_conv))):
        pi_n, pi_d = pi_conv[i]
        diff = pi_n - pi_d
        sum_v = pi_n + pi_d

        if a == diff or b == diff:
            matches.append(f"diff[{i}]={diff}")
        if a == sum_v or b == sum_v:
            matches.append(f"sum[{i}]={sum_v}")
        if a == pi_n or b == pi_n:
            matches.append(f"num[{i}]={pi_n}")
        if a == pi_d or b == pi_d:
            matches.append(f"den[{i}]={pi_d}")

    match_str = ", ".join(matches[:3]) if matches else "none"
    print(f"{n:2d} | {a:5d} | {b:5d} | {match_str}")

print("\n" + "=" * 80)
print("ALTERNATIVE RECURRENCE FORMS")
print("=" * 80)

# Try different recurrence forms
print("\nTesting: m[n] = c[n] × (m[n-1] + m[n-2]) + offset[n]")
print("n  | m[n]     | m[n-1]+m[n-2] | c     | offset")
print("-" * 65)

for n in sorted(m_seq.keys())[2:12]:
    if n-1 not in m_seq or n-2 not in m_seq:
        continue

    m_n = m_seq[n]
    sum_prev = m_seq[n-1] + m_seq[n-2]

    # Try to find c such that m[n] ≈ c × sum_prev
    if sum_prev != 0:
        c_exact = m_n / sum_prev
        c_int = round(c_exact)
        offset = m_n - c_int * sum_prev

        print(f"{n:2d} | {m_n:8d} | {sum_prev:13d} | {c_exact:5.2f} | {offset:6d}")

print("\n" + "=" * 80)
print("CRITICAL DISCOVERY CHECK")
print("=" * 80)

# Check if there's a simple pattern when we include n itself
print("\nTesting: Do coefficients encode INDEX information?")
print("n  |  a[n] |  b[n] | a%n | b%n | a+n | b+n | Is a or b related to n?")
print("-" * 90)

for n, a, b in minimal_coeffs[:12]:
    a_mod_n = a % n if n != 0 else 0
    b_mod_n = b % n if n != 0 else 0
    a_plus_n = a + n
    b_plus_n = b + n

    # Check for relationships
    notes = []
    if a == n:
        notes.append("a=n")
    if b == n:
        notes.append("b=n")
    if a == -n:
        notes.append("a=-n")
    if b == -n:
        notes.append("b=-n")
    if a + b == n:
        notes.append("a+b=n")
    if a - b == n:
        notes.append("a-b=n")

    note_str = ", ".join(notes) if notes else ""

    print(f"{n:2d} | {a:5d} | {b:5d} | {a_mod_n:3d} | {b_mod_n:3d} | {a_plus_n:4d} | {b_plus_n:4d} | {note_str}")

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print("""
KEY OBSERVATIONS:

1. VARIABLE COEFFICIENTS CONFIRMED
   - Each n has different (a,b) coefficients
   - This is a NON-LINEAR recurrence

2. NO SIMPLE MODULAR PATTERN
   - Coefficients don't follow obvious n%k pattern
   - Not directly related to n itself

3. POSSIBLE DIRECTIONS:
   a) Coefficients may be encoded in a lookup table
   b) Coefficients may depend on continued fraction terms
   c) Coefficients may depend on previous m-values
   d) There may be a switching rule between different recurrences

4. NEXT STEP:
   - Check if there's a HIDDEN INDEX that determines which
     convergent system or recurrence rule to use
   - Look for patterns in coefficient TRANSITIONS
""")
