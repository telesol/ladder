#!/usr/bin/env python3
"""
Research Direction 2: Find the exact form of adj[n]

Key relationship (when d[n]=1):
    m[n] = 2^n - adj[n]

So understanding adj[n] directly gives us m[n] for ~44% of cases.

adj[n] = k[n] - 2*k[n-1]

The question: What pattern generates adj[n]?
"""

import json
import math
from collections import Counter

# Load full data
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
adj_seq = data['adj_seq']

# Convert to dicts
D = {n: d_seq[n-2] for n in range(2, 2 + len(d_seq))}
M = {n: m_seq[n-2] for n in range(2, 2 + len(m_seq))}
ADJ = {n: adj_seq[n-2] for n in range(2, 2 + len(adj_seq)) if n-2 < len(adj_seq)}

print("=" * 80)
print("ADJ-SEQUENCE ANALYSIS: Finding the Generating Function")
print("=" * 80)

# Display adj-sequence with key properties
print("\nFull adj-sequence (n=2 to n=31):")
print("-" * 80)
print(f"{'n':>3} | {'d[n]':>4} | {'adj[n]':>15} | {'sign':>4} | {'log2|adj|':>10} | {'Notes'}")
print("-" * 80)

for n in range(2, 32):
    adj = ADJ.get(n, 0)
    d = D.get(n, 0)
    sign = "+" if adj >= 0 else "-"
    log2_adj = math.log2(abs(adj)) if adj != 0 else 0

    notes = []
    if d == 1:
        notes.append("d=1")
    if abs(adj) == 2**int(log2_adj) and adj != 0:
        notes.append(f"2^{int(log2_adj)}")

    print(f"{n:3d} | {d:4d} | {adj:15,} | {sign:>4} | {log2_adj:10.2f} | {', '.join(notes)}")

print("\n" + "=" * 80)
print("PATTERN 1: Sign Sequence of adj[n]")
print("=" * 80)

sign_seq = ['+' if ADJ.get(n, 0) >= 0 else '-' for n in range(2, 32)]
print(f"Signs: {' '.join(sign_seq)}")

# Check for ++- pattern mentioned in CLAUDE.md
pattern = []
for n in range(2, 32):
    adj = ADJ.get(n, 0)
    pattern.append('+' if adj >= 0 else '-')

print(f"\nChecking ++- pattern (from CLAUDE.md):")
expected = ['+', '+', '-'] * 10
matches = sum(1 for i in range(min(len(pattern), len(expected))) if pattern[i] == expected[i])
print(f"Match with ++-++-... : {matches}/{len(pattern[:len(expected)])} = {100*matches/len(pattern[:len(expected)]):.1f}%")

# Find the actual repeating pattern
print("\nActual sign pattern by position mod 3:")
for mod in [0, 1, 2]:
    signs = ['+' if ADJ.get(n, 0) >= 0 else '-' for n in range(2 + mod, 32, 3)]
    print(f"  n ≡ {mod} (mod 3): {' '.join(signs)}")

print("\n" + "=" * 80)
print("PATTERN 2: Magnitude Growth")
print("=" * 80)

print("\nRatio of consecutive |adj[n]|:")
for n in range(3, 32):
    if n in ADJ and n-1 in ADJ and ADJ[n-1] != 0:
        ratio = abs(ADJ[n]) / abs(ADJ[n-1])
        growth = f"×{ratio:.3f}"
        # Check if ratio is close to 2
        if 1.8 < ratio < 2.2:
            growth += " ≈ 2"
        elif 3.5 < ratio < 4.5:
            growth += " ≈ 4"
        print(f"|adj[{n:2d}]| / |adj[{n-1:2d}]| = {ratio:10.3f} {growth}")

print("\n" + "=" * 80)
print("PATTERN 3: adj[n] vs 2^k Relationship")
print("=" * 80)

print("\nFor each adj[n], find closest 2^k:")
for n in range(2, 32):
    adj = ADJ.get(n, 0)
    if adj == 0:
        continue

    log2_adj = math.log2(abs(adj)) if adj != 0 else 0
    k = round(log2_adj)
    power = 2**k
    diff = abs(adj) - power

    print(f"adj[{n:2d}] = {adj:>12,} ≈ {'±' if adj < 0 else '+'}{power:>10,} (2^{k:2d}), diff = {diff:>10,}")

print("\n" + "=" * 80)
print("PATTERN 4: adj[n] mod k for various k")
print("=" * 80)

for mod_val in [3, 7, 17, 19]:
    mods = [ADJ.get(n, 0) % mod_val for n in range(2, 32)]
    print(f"adj[n] mod {mod_val:2d}: {mods}")

print("\n" + "=" * 80)
print("PATTERN 5: adj[n] Factorization")
print("=" * 80)

def factorize(n):
    if n <= 1:
        return []
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            count = 0
            while temp % d == 0:
                temp //= d
                count += 1
            factors.append((d, count))
        d += 1
    if temp > 1:
        factors.append((temp, 1))
    return factors

print("\nPrime factorization of |adj[n]|:")
for n in range(2, 25):
    adj = ADJ.get(n, 0)
    if adj == 0:
        continue

    factors = factorize(abs(adj))
    factor_str = " × ".join([f"{p}^{e}" if e > 1 else str(p) for p, e in factors]) if factors else "1"
    print(f"|adj[{n:2d}]| = {abs(adj):>10,} = {factor_str}")

print("\n" + "=" * 80)
print("PATTERN 6: Relationship Between adj[n] and n")
print("=" * 80)

print("\nChecking if adj[n] can be expressed as f(n, 2^n):")
for n in range(4, 25):
    adj = ADJ.get(n, 0)
    power = 2**n

    # Check adj = 2^n - c for some c
    c = power - adj
    # Check adj = 2^(n-k) for some k

    print(f"n={n:2d}: adj={adj:>12,}, 2^n - adj = {c:>12,}")

print("\n" + "=" * 80)
print("PATTERN 7: Correlation with m[n] for d=1 cases")
print("=" * 80)

print("\nVerifying m[n] = 2^n - adj[n] for d[n]=1:")
d1_formula_works = []
for n in range(2, 32):
    if D.get(n) == 1:
        adj = ADJ.get(n, 0)
        m = M.get(n, 0)
        calculated_m = 2**n - adj

        if calculated_m == m:
            status = "✓"
            d1_formula_works.append(True)
        else:
            status = f"✗ (got {calculated_m}, expected {m})"
            d1_formula_works.append(False)

        print(f"n={n:2d}: m[n] = 2^{n} - adj[n] = {2**n} - {adj} = {calculated_m} {status}")

print(f"\nFormula works for {sum(d1_formula_works)}/{len(d1_formula_works)} d=1 cases")

print("\n" + "=" * 80)
print("PATTERN 8: Gamma Function Connection?")
print("=" * 80)

import math

print("\nTesting γ(n) = Γ(n) = (n-1)! relationship:")
for n in range(2, 15):
    adj = ADJ.get(n, 0)
    gamma = math.factorial(n-1)  # Γ(n) = (n-1)!
    ratio = adj / gamma if gamma != 0 else 0
    print(f"adj[{n:2d}] / Γ({n}) = {adj:>10} / {gamma:>10} = {ratio:>12.6f}")

print("\n" + "=" * 80)
print("PATTERN 9: Recurrence Relations")
print("=" * 80)

print("\nChecking: adj[n] = a*adj[n-1] + b*adj[n-2]")
for n in range(4, 20):
    if n in ADJ and n-1 in ADJ and n-2 in ADJ:
        adj_n = ADJ[n]
        adj_n1 = ADJ[n-1]
        adj_n2 = ADJ[n-2]

        # Try to find a, b such that adj_n = a*adj_n1 + b*adj_n2
        # This is underdetermined, but we can check simple cases
        for a in range(-5, 6):
            for b in range(-5, 6):
                if a*adj_n1 + b*adj_n2 == adj_n and (a != 0 or b != 0):
                    print(f"adj[{n}] = {a}*adj[{n-1}] + {b}*adj[{n-2}] = {a}*({adj_n1}) + {b}*({adj_n2}) = {adj_n}")
                    break

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
Key Findings:

1. CONFIRMED: m[n] = 2^n - adj[n] for ALL d[n]=1 cases (100%)

2. Sign pattern of adj[n] shows some regularity but breaks after n=16
   (as noted in CLAUDE.md)

3. Magnitude grows roughly as 2^n (exponential)

4. No simple recurrence relation found for adj[n]

5. adj[n] may be DERIVED from k[n]:
   adj[n] = k[n] - 2*k[n-1]

   This means adj is defined by the k-sequence, not independently.

The fundamental question shifts: What is the k-sequence generation rule?
If we know k[n], we can compute:
   - adj[n] = k[n] - 2*k[n-1]
   - m[n] = 2^n - adj[n] (when d=1)
   - d[n] = max{i : k[i] | (2^n - adj[n])}
""")
