#!/usr/bin/env python3
"""
Map ALL m-values to continued fraction convergents.

Known matches:
- m[4] = 22 = π convergent numerator (22/7)
- m[6] = 19 = e convergent numerator (19/7)
- m[7] = 50 = √3 convergent numerator?

Goal: Find which mathematical constant each m-value comes from.
"""
import json
from fractions import Fraction
from sympy import pi, E, sqrt, log, Rational

# Load m-values
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)
M_SEQ = data['m_seq']

def continued_fraction_convergents(x, n=30):
    """Compute n convergents of continued fraction of x."""
    convergents = []
    cf = []

    # Get continued fraction coefficients
    val = float(x)
    for _ in range(n):
        a = int(val)
        cf.append(a)
        frac = val - a
        if abs(frac) < 1e-15:
            break
        val = 1 / frac

    # Compute convergents
    h_prev, h_curr = 0, 1
    k_prev, k_curr = 1, 0

    for a in cf:
        h_new = a * h_curr + h_prev
        k_new = a * k_curr + k_prev
        convergents.append((h_new, k_new))
        h_prev, h_curr = h_curr, h_new
        k_prev, k_curr = k_curr, k_new

    return convergents, cf

print("=" * 80)
print("CONTINUED FRACTION MAPPING FOR M-VALUES")
print("=" * 80)
print()

# Mathematical constants to test
import math
constants = {
    'π': math.pi,
    'e': math.e,
    '√2': math.sqrt(2),
    '√3': math.sqrt(3),
    '√5': math.sqrt(5),
    'φ': (1 + math.sqrt(5)) / 2,  # Golden ratio
    'ln(2)': math.log(2),
    '1/π': 1 / math.pi,
    '1/e': 1 / math.e,
    'π/4': math.pi / 4,
    'e/π': math.e / math.pi,
}

# Compute convergents for each constant
all_convergents = {}
for name, val in constants.items():
    convs, cf = continued_fraction_convergents(val, 50)
    all_convergents[name] = {
        'convergents': convs,
        'cf': cf[:15],
        'numerators': set(h for h, k in convs),
        'denominators': set(k for h, k in convs),
    }

# Show first few convergents for key constants
print("### KEY CONSTANT CONVERGENTS ###")
print()
for name in ['π', 'e', '√3', 'φ']:
    info = all_convergents[name]
    print(f"{name}: cf = {info['cf'][:10]}")
    print(f"   convergents: {info['convergents'][:8]}")
    print()

# Try to match each m-value
print("### MATCHING M-VALUES TO CONVERGENTS ###")
print()
print("n    | m[n]        | Matches")
print("-----|-------------|" + "-" * 50)

matches = []
for i in range(min(30, len(M_SEQ))):
    n = i + 2
    m = M_SEQ[i]

    found = []
    for name, info in all_convergents.items():
        if m in info['numerators']:
            found.append(f"{name} NUM")
        if m in info['denominators']:
            found.append(f"{name} DEN")

    match_str = ", ".join(found) if found else "?"
    print(f"{n:4} | {m:11} | {match_str}")

    if found:
        matches.append((n, m, found))

print()
print(f"Total matches: {len(matches)}/{min(30, len(M_SEQ))}")
print()

# Analyze the matched constants
print("### ANALYSIS OF MATCHED CONSTANTS ###")
print()

# Count occurrences of each constant
constant_counts = {}
for n, m, found_list in matches:
    for f in found_list:
        const = f.split()[0]
        constant_counts[const] = constant_counts.get(const, 0) + 1

for const, count in sorted(constant_counts.items(), key=lambda x: -x[1]):
    print(f"  {const}: {count} matches")

print()

# Special focus on first 10 m-values
print("### FIRST 10 M-VALUES DEEP ANALYSIS ###")
print()

for i in range(min(10, len(M_SEQ))):
    n = i + 2
    m = M_SEQ[i]
    print(f"m[{n}] = {m}")

    # Find in which constant's convergents
    found_in = []
    for name, info in all_convergents.items():
        for idx, (h, k) in enumerate(info['convergents']):
            if h == m:
                found_in.append(f"  = {name} convergent[{idx}] numerator ({h}/{k})")
            if k == m:
                found_in.append(f"  = {name} convergent[{idx}] denominator ({h}/{k})")

    if found_in:
        for f in found_in:
            print(f)
    else:
        print("  NOT FOUND in standard convergents")

    # Check if m is a prime
    from sympy import isprime
    if isprime(m):
        print(f"  (PRIME)")

    print()

# Can we predict m[71]?
print("### PREDICTION FOR M[71] ###")
print()
print("If m-values come from continued fractions, m[71] should be")
print("a convergent numerator or denominator of some constant.")
print()

# What's the typical size of m[71]?
# From earlier analysis: m[71] ≈ 2^71 / k[d[71]]
# If d[71] = 1: m[71] ≈ 2^71 ≈ 2.36e21
print("Expected m[71] magnitude: ~10^21")
print()
print("Large convergents of π:")
for idx, (h, k) in enumerate(all_convergents['π']['convergents'][-10:]):
    if h > 1e15:
        print(f"  convergent[{idx+40}]: {h}/{k}")
