#!/usr/bin/env python3
"""
Deep analysis of recurrence relations in m-sequence.

DISCOVERED RECURRENCES:
m[4] = 1×m[3] + 5×m[2]
m[5] = -1×m[4] + 7×m[3]
m[6] = 7×m[5] - 6×m[4]
m[7] = 5×m[6] - 5×m[5]

Goal: Find if coefficients relate to π, e, φ convergents.
"""

from fractions import Fraction
import math

# Known m-sequence
m_seq = {
    2: 3, 3: 7, 4: 22, 5: 27, 6: 57, 7: 150, 8: 184, 9: 493,
    10: 1444, 11: 1921, 12: 3723, 13: 8342, 14: 16272, 15: 26989,
    16: 67760, 17: 138269, 18: 255121, 19: 564091, 20: 900329
}

def continued_fraction_pi(max_terms=40):
    """Generate continued fraction for π."""
    cf = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2,
          1, 84, 2, 1, 1, 15, 3, 13, 1, 4, 2, 6, 6, 1, 1, 1, 8, 1, 1, 3]
    return cf[:max_terms]

def continued_fraction_e(max_terms=50):
    """Generate continued fraction for e."""
    cf = [2]
    for k in range(1, max_terms):
        cf.extend([1, 2*k, 1])
        if len(cf) >= max_terms:
            break
    return cf[:max_terms]

def continued_fraction_phi(max_terms=50):
    """Generate continued fraction for φ."""
    return [1] * max_terms

def convergents_from_cf(cf):
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
pi_cf = continued_fraction_pi()
e_cf = continued_fraction_e()
phi_cf = continued_fraction_phi()

pi_conv = convergents_from_cf(pi_cf)
e_conv = convergents_from_cf(e_cf)
phi_conv = convergents_from_cf(phi_cf)

print("=" * 80)
print("RECURRENCE RELATION EXTRACTION")
print("=" * 80)

# Find all recurrence relations: m[n] = a×m[n-1] + b×m[n-2]
recurrences = {}

for n in sorted(m_seq.keys())[2:]:
    if n-1 in m_seq and n-2 in m_seq:
        m_n = m_seq[n]
        m_n1 = m_seq[n-1]
        m_n2 = m_seq[n-2]

        # Solve for a, b in: m[n] = a×m[n-1] + b×m[n-2]
        found = []
        for a in range(-20, 20):
            for b in range(-20, 20):
                if a * m_n1 + b * m_n2 == m_n:
                    found.append((a, b))

        recurrences[n] = found

# Display all recurrences
print("\nAll recurrence relations found:")
print("n  | m[n]     | Recurrence: m[n] = a×m[n-1] + b×m[n-2]")
print("-" * 80)

for n in sorted(recurrences.keys()):
    m_n = m_seq[n]
    if recurrences[n]:
        # Show first few solutions
        solutions = recurrences[n][:3]
        sol_str = ", ".join([f"({a},{b})" for a, b in solutions])
        print(f"{n:2d} | {m_n:8d} | (a,b) = {sol_str}")

print("\n" + "=" * 80)
print("COEFFICIENT ANALYSIS")
print("=" * 80)

# Extract coefficient sequences
a_seq = []
b_seq = []

for n in sorted(recurrences.keys()):
    if recurrences[n]:
        # Take the first solution (arbitrary choice)
        a, b = recurrences[n][0]
        a_seq.append((n, a))
        b_seq.append((n, b))

print("\nCoefficient 'a' sequence:")
for n, a in a_seq[:15]:
    print(f"  a[{n}] = {a:3d}")

print("\nCoefficient 'b' sequence:")
for n, b in b_seq[:15]:
    print(f"  b[{n}] = {b:3d}")

print("\n" + "=" * 80)
print("TESTING: DO COEFFICIENTS COME FROM CONVERGENTS?")
print("=" * 80)

print("\nπ continued fraction terms:", pi_cf[:20])
print("e continued fraction terms:", e_cf[:20])
print("φ continued fraction terms:", phi_cf[:20])

# Check if coefficients match CF terms
print("\nChecking if a[n] or b[n] match CF terms...")

for n, a in a_seq[:12]:
    _, b = b_seq[n - a_seq[0][0]]  # Get corresponding b

    # Check against CF terms
    matches = []
    if n < len(pi_cf) and (a == pi_cf[n] or b == pi_cf[n]):
        matches.append(f"π_cf[{n}]")
    if n < len(e_cf) and (a == e_cf[n] or b == e_cf[n]):
        matches.append(f"e_cf[{n}]")
    if n < len(phi_cf) and (a == phi_cf[n] or b == phi_cf[n]):
        matches.append(f"φ_cf[{n}]")

    # Check convergent components
    if n < len(pi_conv):
        pi_n, pi_d = pi_conv[n]
        if a in [pi_n, pi_d] or b in [pi_n, pi_d]:
            matches.append("π_conv")

    if matches:
        print(f"  n={n}: a={a:3d}, b={b:3d} → {', '.join(matches)}")

print("\n" + "=" * 80)
print("HIGHER-ORDER RECURRENCES: m[n] = a×m[n-1] + b×m[n-2] + c×m[n-3]")
print("=" * 80)

def find_3term_recurrence(n):
    """Find m[n] = a×m[n-1] + b×m[n-2] + c×m[n-3]"""
    if n-1 not in m_seq or n-2 not in m_seq or n-3 not in m_seq:
        return []

    m_n = m_seq[n]
    m_n1 = m_seq[n-1]
    m_n2 = m_seq[n-2]
    m_n3 = m_seq[n-3]

    found = []
    for a in range(-10, 10):
        for b in range(-10, 10):
            for c in range(-10, 10):
                if a * m_n1 + b * m_n2 + c * m_n3 == m_n:
                    found.append((a, b, c))
                    if len(found) >= 5:
                        return found
    return found

print("\n3-term recurrences:")
for n in range(5, min(15, max(m_seq.keys())+1)):
    if n in m_seq:
        rels = find_3term_recurrence(n)
        if rels:
            a, b, c = rels[0]
            print(f"  m[{n}] = {a}×m[{n-1}] + {b}×m[{n-2}] + {c}×m[{n-3}]")

print("\n" + "=" * 80)
print("VARIABLE RECURRENCE: TESTING IF COEFFICIENTS CHANGE WITH n")
print("=" * 80)

print("\nExtracting coefficient pattern...")
print("n  | (a, b) | a-pattern? | b-pattern?")
print("-" * 60)

coeff_table = []
for n in sorted(recurrences.keys())[:12]:
    if recurrences[n]:
        a, b = recurrences[n][0]
        coeff_table.append((n, a, b))

        # Look for patterns
        a_notes = []
        b_notes = []

        # Is a related to n?
        if a == n:
            a_notes.append("a=n")
        if a == n - 2:
            a_notes.append("a=n-2")
        if a == 2*n - 3:
            a_notes.append("a=2n-3")

        # Is b related to n?
        if b == -n:
            b_notes.append("b=-n")
        if b == n:
            b_notes.append("b=n")
        if b == 5:
            b_notes.append("b=5")

        a_str = ", ".join(a_notes) if a_notes else ""
        b_str = ", ".join(b_notes) if b_notes else ""

        print(f"{n:2d} | ({a:3d},{b:3d}) | {a_str:12s} | {b_str}")

print("\n" + "=" * 80)
print("FIBONACCI-STYLE ANALYSIS")
print("=" * 80)

print("\nFibonacci: F[n] = F[n-1] + F[n-2]")
print("Testing if m-sequence has varying Fibonacci-like form...")

# Check if there's a pattern in the "excess" beyond Fibonacci
print("\nDefine: excess[n] = m[n] - (m[n-1] + m[n-2])")
print()
print("n  | m[n]     | m[n-1]+m[n-2] | excess")
print("-" * 55)

for n in sorted(m_seq.keys())[2:15]:
    if n-1 in m_seq and n-2 in m_seq:
        m_n = m_seq[n]
        fib_like = m_seq[n-1] + m_seq[n-2]
        excess = m_n - fib_like

        print(f"{n:2d} | {m_n:8d} | {fib_like:13d} | {excess:6d}")

print("\n" + "=" * 80)
print("CONSTRUCTION TEST: Can we generate m[n] iteratively?")
print("=" * 80)

def test_construction_formula(formula_func, start_values, max_n=20):
    """Test if a formula can generate the m-sequence."""
    generated = {k: v for k, v in start_values.items()}

    for n in range(max(start_values.keys()) + 1, max_n + 1):
        try:
            generated[n] = formula_func(n, generated)
        except:
            break

    return generated

# Test various formulas
print("\nTesting construction formulas...")

# Formula 1: m[n] = coefficient[n] × m[n-1] + ...
def formula1(n, prev):
    if n < 4 or n-1 not in prev or n-2 not in prev:
        return None
    # Use first recurrence coefficients
    if n in recurrences and recurrences[n]:
        a, b = recurrences[n][0]
        return a * prev[n-1] + b * prev[n-2]
    return None

start = {2: 3, 3: 7}
result1 = test_construction_formula(formula1, start, 20)

print("\nFormula 1 (using discovered recurrences):")
print("n  | actual   | generated | match")
print("-" * 45)
for n in sorted(m_seq.keys())[:12]:
    actual = m_seq.get(n, None)
    gen = result1.get(n, None)
    match = "✓" if actual == gen else "✗"
    print(f"{n:2d} | {actual or 'N/A':8} | {gen or 'N/A':9} | {match}")

print("\n" + "=" * 80)
print("KEY INSIGHT SUMMARY")
print("=" * 80)
print("""
CRITICAL FINDINGS:

1. TWO-TERM RECURRENCES EXIST:
   m[4] = 1×m[3] + 5×m[2]
   m[5] = -1×m[4] + 7×m[3]
   m[6] = 7×m[5] - 6×m[4]
   m[7] = 5×m[6] - 5×m[5]

2. COEFFICIENTS ARE VARIABLE:
   The (a,b) coefficients change with n!
   This is NOT a constant-coefficient recurrence like Fibonacci.

3. PATTERN NEEDED:
   Need to find: a[n] = f(n, convergents, ...)
                b[n] = g(n, convergents, ...)

4. CONVERGENT LINKS:
   m[2]=3, m[3]=7, m[4]=22 are EXACTLY π convergent parts
   The sequence might SWITCH between different convergent systems

NEXT: Find the rule for coefficients a[n] and b[n]
""")
