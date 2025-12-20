#!/usr/bin/env python3
"""
Generate continued fraction convergents for mathematical constants.

This is a HELPER SCRIPT for deriving m[71].

Run: python3 generate_convergents.py
"""

from fractions import Fraction
from decimal import Decimal, getcontext
import math

# Set high precision
getcontext().prec = 100

def cf_expansion(x, n_terms=50):
    """Get continued fraction expansion of x."""
    result = []
    for _ in range(n_terms):
        a = int(x)
        result.append(a)
        frac = x - a
        if abs(frac) < 1e-15:
            break
        x = 1 / frac
    return result

def convergents_from_cf(cf):
    """Generate convergents (p/q pairs) from continued fraction."""
    convergents = []
    p_prev, p_curr = 0, 1
    q_prev, q_curr = 1, 0

    for a in cf:
        p_new = a * p_curr + p_prev
        q_new = a * q_curr + q_prev
        convergents.append((p_new, q_new))
        p_prev, p_curr = p_curr, p_new
        q_prev, q_curr = q_curr, q_new

    return convergents

# Mathematical constants
PI = 3.14159265358979323846264338327950288419716939937510
E = 2.71828182845904523536028747135266249775724709369995
SQRT2 = 1.41421356237309504880168872420969807856967187537694
PHI = 1.61803398874989484820458683436563811772030917980576
LN2 = 0.69314718055994530941723212145817656807550013436026
SQRT3 = 1.73205080756887729352744634150587236694280525381038

constants = {
    'π': PI,
    'e': E,
    '√2': SQRT2,
    'φ': PHI,
    'ln2': LN2,
    '√3': SQRT3,
}

print("=" * 80)
print("CONVERGENT TABLES FOR MATHEMATICAL CONSTANTS")
print("=" * 80)

for name, value in constants.items():
    cf = cf_expansion(value, 30)
    convs = convergents_from_cf(cf)

    print(f"\n### {name} = {value}")
    print(f"CF: [{', '.join(map(str, cf[:15]))}...]")
    print(f"{'idx':>3} {'num':>20} {'den':>15}")
    print("-" * 45)

    for i, (p, q) in enumerate(convs[:20]):
        print(f"{i:>3} {p:>20} {q:>15}")

# Also show some useful combinations
print("\n" + "=" * 80)
print("USEFUL PRODUCTS AND SUMS")
print("=" * 80)

# Get first 15 convergents for key constants
pi_convs = convergents_from_cf(cf_expansion(PI, 20))
e_convs = convergents_from_cf(cf_expansion(E, 20))
sqrt2_convs = convergents_from_cf(cf_expansion(SQRT2, 20))
ln2_convs = convergents_from_cf(cf_expansion(LN2, 20))

print("\n### Key convergent numerators:")
print(f"π:   {[c[0] for c in pi_convs[:12]]}")
print(f"e:   {[c[0] for c in e_convs[:12]]}")
print(f"√2:  {[c[0] for c in sqrt2_convs[:12]]}")
print(f"ln2: {[c[0] for c in ln2_convs[:12]]}")

print("\n### Key convergent denominators:")
print(f"π:   {[c[1] for c in pi_convs[:12]]}")
print(f"e:   {[c[1] for c in e_convs[:12]]}")
print(f"√2:  {[c[1] for c in sqrt2_convs[:12]]}")
print(f"ln2: {[c[1] for c in ln2_convs[:12]]}")

# Products of convergents (used in Type 2)
print("\n### Products of convergents at same index:")
for i in range(10):
    pi_num = pi_convs[i][0]
    sqrt2_num = sqrt2_convs[i][0]
    e_num = e_convs[i][0]

    print(f"idx {i}: π×√2 = {pi_num * sqrt2_num}, π×e = {pi_num * e_num}")

# Known m-values for verification
print("\n" + "=" * 80)
print("VERIFICATION: KNOWN m-VALUES")
print("=" * 80)

known_m = {
    4: 22,   # π numerator[1] = 22/7
    5: 9,    # ln2 numerator[4] = 9
    6: 19,   # e numerator[4] = 19
    7: 50,   # φ_num[3] × ln2_den[3] = 5 × 10
    8: 23,   # π_den[0] + π_num[1] = 1 + 22
    11: 1921, # √2_num[3] × π_den[3] = 17 × 113
}

print("\nVerifying construction rules:")
for n, m in known_m.items():
    print(f"m[{n}] = {m}")
