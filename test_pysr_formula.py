#!/usr/bin/env python3
"""
Test the PySR formula with integer arithmetic to find an exact version.

PySR found: m[n] ≈ (2^n + prev_m * 1.17) / (d[n]² + 0.5)

Let's test integer variants to find an exact formula.
"""

import json
from sympy import factorint

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

def m(n):
    if n < 2 or n > 71:
        return None
    return m_seq[n - 2]

def d(n):
    if n < 2 or n > 71:
        return None
    return d_seq[n - 2]

print("=" * 70)
print("TESTING INTEGER VERSIONS OF PYSR FORMULA")
print("=" * 70)

# Test the approximate formula
print("\n### PySR Formula: m[n] ≈ (2^n + prev_m) / d[n]²")
print("n    actual     predicted   ratio     d[n]  2^n           formula")
print("-" * 70)

for n in range(3, 32):
    actual = m(n)
    prev = m(n - 1)
    dn = d(n)
    pow2 = 2 ** n

    # Test different integer formulas
    # Formula 1: (2^n + prev_m) // d[n]²
    pred1 = (pow2 + prev) // (dn ** 2)

    # Formula 2: (2^n) // d[n]
    pred2 = pow2 // dn

    # Formula 3: (2^n + prev_m) // d[n]
    pred3 = (pow2 + prev) // dn

    # Formula 4: 2^n // d[n]²
    pred4 = pow2 // (dn ** 2)

    # Check which is closest
    errors = [
        abs(pred1 - actual) / actual if actual > 0 else float('inf'),
        abs(pred2 - actual) / actual if actual > 0 else float('inf'),
        abs(pred3 - actual) / actual if actual > 0 else float('inf'),
        abs(pred4 - actual) / actual if actual > 0 else float('inf'),
    ]
    best_idx = errors.index(min(errors))
    preds = [pred1, pred2, pred3, pred4]

    ratio = actual / pow2 if pow2 > 0 else 0

    print(f"{n:3}  {actual:<10} {preds[best_idx]:<11} {ratio:.6f}  {dn:4}  {pow2:<13}")

# Test for exact matches
print("\n" + "=" * 70)
print("LOOKING FOR EXACT INTEGER FORMULAS")
print("=" * 70)

exact_matches = {
    'pow2/d': [],
    'pow2/d2': [],
    'pow2+prev/d': [],
    'pow2+prev/d2': [],
}

for n in range(3, 32):
    actual = m(n)
    prev = m(n - 1)
    dn = d(n)
    pow2 = 2 ** n

    if pow2 // dn == actual:
        exact_matches['pow2/d'].append(n)
    if pow2 // (dn ** 2) == actual:
        exact_matches['pow2/d2'].append(n)
    if (pow2 + prev) // dn == actual:
        exact_matches['pow2+prev/d'].append(n)
    if (pow2 + prev) // (dn ** 2) == actual:
        exact_matches['pow2+prev/d2'].append(n)

print("\nExact matches for each formula:")
for formula, matches in exact_matches.items():
    print(f"  {formula}: {len(matches)} matches at n={matches}")

# Check ratio m[n] * d[n]² / 2^n
print("\n" + "=" * 70)
print("RATIO ANALYSIS: m[n] * d[n]² / 2^n")
print("=" * 70)
print("n    m[n]        d[n]   2^n           m*d²/2^n      m*d/2^n")
print("-" * 70)

for n in range(2, 32):
    actual = m(n)
    dn = d(n)
    pow2 = 2 ** n

    ratio1 = actual * (dn ** 2) / pow2
    ratio2 = actual * dn / pow2

    print(f"{n:3}  {actual:<10}  {dn:4}  {pow2:<13} {ratio1:.6f}     {ratio2:.6f}")

# Check if m[n] relates to 2^n / (d[n] * something)
print("\n" + "=" * 70)
print("LOOKING FOR m[n] = 2^n / (d[n] * f(n))")
print("=" * 70)
print("n    m[n]        d[n]   2^n/m[n]      2^n/(m[n]*d[n])  factor")
print("-" * 70)

for n in range(2, 32):
    actual = m(n)
    dn = d(n)
    pow2 = 2 ** n

    if actual > 0:
        ratio1 = pow2 / actual
        ratio2 = pow2 / (actual * dn)
        factor = pow2 / actual
        print(f"{n:3}  {actual:<10}  {dn:4}  {ratio1:<13.4f} {ratio2:<15.4f} {factor:.4f}")

# Test: m[n] = (2^n - offset) / d[n]
print("\n" + "=" * 70)
print("TEST: m[n] = (2^n - offset) / d[n]")
print("=" * 70)
print("If m[n] = (2^n - offset) / d[n], then offset = 2^n - m[n] * d[n]")
print()
print("n    m[n]        d[n]   2^n           offset        offset/2^(n-1)")
print("-" * 70)

for n in range(2, 32):
    actual = m(n)
    dn = d(n)
    pow2 = 2 ** n

    offset = pow2 - actual * dn
    offset_ratio = offset / (2 ** (n - 1)) if n > 1 else 0

    print(f"{n:3}  {actual:<10}  {dn:4}  {pow2:<13} {offset:<13} {offset_ratio:.6f}")

# Check if the offset has a pattern
print("\n" + "=" * 70)
print("OFFSET ANALYSIS: offset = 2^n - m[n] * d[n]")
print("=" * 70)
print("n    offset      factors(offset)")
print("-" * 70)

for n in range(2, 20):
    actual = m(n)
    dn = d(n)
    pow2 = 2 ** n
    offset = pow2 - actual * dn

    if offset > 1:
        factors = factorint(abs(offset))
        factor_str = ' × '.join([f'{p}^{e}' if e > 1 else str(p) for p, e in sorted(factors.items())])
    elif offset == 1:
        factor_str = "1"
    elif offset == 0:
        factor_str = "0"
    else:
        factor_str = f"-{factorint(abs(offset))}"

    print(f"{n:3}  {offset:<10} {factor_str}")

print("\n" + "=" * 70)
print("COMPLETE")
print("=" * 70)
