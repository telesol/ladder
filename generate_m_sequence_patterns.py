#!/usr/bin/env python3
"""
Generate m-sequence for n>70 using discovered patterns.

Based on 5-tier pattern catalog from RKH Claude:
Tier 1: Direct convergents
Tier 2: Cross-constant products
Tier 3: Prime-index formulas
Tier 4: Divisibility chains
Tier 5: Self-reference
"""

import json
import sympy
from fractions import Fraction

# Load verified m and d sequences
with open('data_for_csolver.json') as f:
    data = json.load(f)
    n_start = data['n_range'][0]
    M_SEQ = {n_start + i: val for i, val in enumerate(data['m_seq'])}
    D_SEQ = {n_start + i: val for i, val in enumerate(data['d_seq'])}

print("=" * 80)
print("M-SEQUENCE PATTERN-BASED GENERATOR")
print("=" * 80)
print(f"\nLoaded {len(M_SEQ)} verified m-values (n=2-70)")

# Generate convergents for mathematical constants
def convergents(cf, limit=100):
    """Generate convergents from continued fraction."""
    p0, p1 = 1, cf[0]
    q0, q1 = 0, 1

    result = [(p1, q1)]

    for i in range(1, min(len(cf), limit)):
        p2 = cf[i] * p1 + p0
        q2 = cf[i] * q1 + q0
        result.append((p2, q2))
        p0, p1 = p1, p2
        q0, q1 = q1, q2

    return result

# Mathematical constants (continued fractions - first 50 terms)
import math

def pi_cf():
    """π continued fraction."""
    return [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2, 1, 84, 2, 1, 1]

def e_cf():
    """e continued fraction."""
    return [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, 1, 1, 12, 1, 1, 14]

def sqrt2_cf():
    """√2 continued fraction."""
    return [1] + [2] * 50

def sqrt3_cf():
    """√3 continued fraction."""
    return [1, 1, 2] + [1, 2] * 15

def phi_cf():
    """φ (golden ratio) continued fraction."""
    return [1] * 50

def ln2_cf():
    """ln(2) continued fraction."""
    return [0, 1, 2, 3, 1, 6, 3, 1, 1, 2, 1, 1, 1, 1, 3, 10]

# Generate convergent databases
print("\nGenerating convergent databases...")
PI_CONV = convergents(pi_cf())
E_CONV = convergents(e_cf())
SQRT2_CONV = convergents(sqrt2_cf())
SQRT3_CONV = convergents(sqrt3_cf())
PHI_CONV = convergents(phi_cf())
LN2_CONV = convergents(ln2_cf())

print(f"  π: {len(PI_CONV)} convergents")
print(f"  e: {len(E_CONV)} convergents")
print(f"  √2: {len(SQRT2_CONV)} convergents")
print(f"  √3: {len(SQRT3_CONV)} convergents")
print(f"  φ: {len(PHI_CONV)} convergents")
print(f"  ln(2): {len(LN2_CONV)} convergents")

# Pattern testing functions
def test_tier1_direct_convergent(n):
    """Tier 1: Check if m[n] is a direct convergent value."""
    candidates = []

    for name, convs in [('π', PI_CONV), ('e', E_CONV), ('√2', SQRT2_CONV),
                         ('√3', SQRT3_CONV), ('φ', PHI_CONV), ('ln(2)', LN2_CONV)]:
        for i, (num, den) in enumerate(convs):
            if num < 10**15:  # Reasonable limit
                if num not in [v for v in M_SEQ.values()]:  # Not already known
                    candidates.append((num, f"{name}_num[{i}]"))
                if den not in [v for v in M_SEQ.values()]:
                    candidates.append((den, f"{name}_den[{i}]"))

    return candidates[:10]  # Return top 10 candidates

def test_tier2_cross_constant(n):
    """Tier 2: Check for cross-constant products."""
    # Pattern: m[n] = const1[i] × const2[i] (same index)
    candidates = []

    all_convs = [
        ('π', PI_CONV), ('e', E_CONV), ('√2', SQRT2_CONV),
        ('√3', SQRT3_CONV), ('φ', PHI_CONV), ('ln(2)', LN2_CONV)
    ]

    for i in range(min(10, len(SQRT2_CONV))):  # Check indices 0-9
        for name1, convs1 in all_convs:
            for name2, convs2 in all_convs:
                if i < len(convs1) and i < len(convs2):
                    num1, den1 = convs1[i]
                    num2, den2 = convs2[i]

                    products = [
                        (num1 * num2, f"{name1}_num[{i}] × {name2}_num[{i}]"),
                        (num1 * den2, f"{name1}_num[{i}] × {name2}_den[{i}]"),
                        (den1 * num2, f"{name1}_den[{i}] × {name2}_num[{i}]"),
                        (den1 * den2, f"{name1}_den[{i}] × {name2}_den[{i}]"),
                    ]

                    for val, formula in products:
                        if val < 10**18 and val > 1:
                            candidates.append((val, formula))

    return candidates[:20]

def test_tier3_prime_index(n):
    """Tier 3: Prime-index formula m[n] = 17 × p[n + m[k]]."""
    candidates = []

    # Try all earlier m-values as k
    for k in range(2, min(n, 71)):
        if k in M_SEQ:
            index = n + M_SEQ[k]
            if 1 <= index <= 100000:  # Reasonable range
                try:
                    p = sympy.prime(index)
                    val = 17 * p
                    candidates.append((val, f"17 × p[{n} + m[{k}]] = 17 × p[{index}]"))
                except:
                    pass

    return candidates[:10]

def test_tier4_divisibility(n):
    """Tier 4: Check if known m-values divide this m[n]."""
    # This requires knowing m[n] first, so skip for generation
    return []

def test_tier5_self_reference(n):
    """Tier 5: m[n] might divide m[n + m[n]]."""
    # This is a validation pattern, not generation pattern
    return []

# Test on a few target values
print("\n" + "=" * 80)
print("PATTERN TESTING FOR n=71-75")
print("=" * 80)

for n in range(71, 76):
    print(f"\nn={n}:")
    print("-" * 80)

    # Test all tiers
    t1 = test_tier1_direct_convergent(n)
    t2 = test_tier2_cross_constant(n)
    t3 = test_tier3_prime_index(n)

    print(f"  Tier 1 (Direct convergent) candidates: {len(t1)}")
    if t1:
        for val, formula in t1[:3]:
            print(f"    {val:15d} = {formula}")

    print(f"  Tier 2 (Cross-constant product) candidates: {len(t2)}")
    if t2:
        for val, formula in t2[:3]:
            print(f"    {val:15d} = {formula}")

    print(f"  Tier 3 (Prime-index formula) candidates: {len(t3)}")
    if t3:
        for val, formula in t3[:3]:
            print(f"    {val:15d} = {formula}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

print("""
The pattern-based approach generates MANY candidates for each n.

**Problem**: We have multiple candidates but no way to select the correct one.

**Options**:
1. We need ADDITIONAL CONSTRAINTS to pick the right candidate
2. We need the BRIDGE VALUES (k75, k80, etc.) to validate
3. We need to find the META-RULE that selects which tier/formula to use

**Next steps**:
1. Extend d-sequence prediction (power-of-2 pattern)
2. Use d-sequence to constrain m-sequence search
3. Validate candidates against master formula
4. Run H2-H4 drift tests if patterns fail
""")

print("\n✅ Pattern analysis complete")
