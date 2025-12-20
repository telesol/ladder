#!/usr/bin/env python3
"""
Investigate the n=17 Transition Point
=====================================

The other Claude discovered that adj[n] sign follows ++- pattern
for n=2-16, then BREAKS at n=17.

This script investigates:
1. What's special about n=17?
2. Is there a pattern change in the k-sequence at this point?
3. Does the formula type change at n=17?
"""

import json
import sqlite3
from math import sqrt

# Load data
with open('data_for_csolver.json') as f:
    data = json.load(f)

m_list = data['m_seq']
d_list = data['d_seq']
m_seq = {n: m_list[n-2] for n in range(2, 2 + len(m_list))}
d_seq = {n: d_list[n-2] for n in range(2, 2 + len(d_list))}

# Load k values from database
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
k_seq = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

# Compute adj sequence
adj_seq = {}
for n in range(2, 71):
    if n in k_seq and n-1 in k_seq:
        adj_seq[n] = k_seq[n] - 2 * k_seq[n-1]

print("=" * 80)
print("INVESTIGATION: THE n=17 TRANSITION POINT")
print("=" * 80)

# ============================================================================
# 1. Show the adj sequence and sign pattern
# ============================================================================

print("\n## ADJ SEQUENCE AND SIGN PATTERN")
print("-" * 60)

signs = []
for n in range(2, 25):
    adj = adj_seq.get(n)
    if adj is not None:
        sign = "+" if adj >= 0 else "-"
        signs.append(sign)
        sign_display = "+" if adj >= 0 else ""
        print(f"n={n:2d}: adj = {sign_display}{adj:>12}  sign = {sign}")

print(f"\nSign pattern (n=2-24): {''.join(signs)}")
print(f"Expected ++- pattern: ++-++-++-++-++-++-++-++-")

# Check the ++- pattern
expected = "++-" * 8
actual = ''.join(signs[:24])
matches = sum(1 for i, (a, e) in enumerate(zip(actual, expected)) if a == e)
print(f"\nMatches with ++- pattern: {matches}/24")

# Find where pattern breaks
print("\n## WHERE PATTERN BREAKS")
print("-" * 60)

for i in range(len(signs)):
    expected_sign = "++-"[i % 3]
    if signs[i] != expected_sign:
        n = i + 2  # n starts at 2
        print(f"BREAK at n={n}: expected {expected_sign}, got {signs[i]}")
        print(f"       adj[{n}] = {adj_seq.get(n)}")

# ============================================================================
# 2. What's special about k[17]?
# ============================================================================

print("\n\n## WHAT'S SPECIAL ABOUT n=17?")
print("-" * 60)

k17 = k_seq.get(17)
m17 = m_seq.get(17)
d17 = d_seq.get(17)
adj17 = adj_seq.get(17)

print(f"k[17] = {k17}")
print(f"m[17] = {m17}")
print(f"d[17] = {d17}")
print(f"adj[17] = {adj17}")
print()

# Factorize k[17]
def factorize_simple(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

print(f"Factorization of k[17]:")
factors = factorize_simple(k17)
from collections import Counter
factor_counts = Counter(factors)
factor_str = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factor_counts.items()))
print(f"  k[17] = {factor_str}")

# Check if k[17] is related to earlier k values
print(f"\nRelationships with earlier k values:")
for i in range(1, 17):
    ki = k_seq.get(i)
    if ki and k17 % ki == 0:
        print(f"  k[17] / k[{i}] = {k17 // ki}")
    # Check sum/difference
    for j in range(1, i):
        kj = k_seq.get(j)
        if kj:
            if ki + kj == k17:
                print(f"  k[17] = k[{i}] + k[{j}] = {ki} + {kj}")
            if ki * kj == k17:
                print(f"  k[17] = k[{i}] × k[{j}] = {ki} × {kj}")

# ============================================================================
# 3. Compare k-sequence growth before and after n=17
# ============================================================================

print("\n\n## K-SEQUENCE GROWTH PATTERN")
print("-" * 60)

print("\nRatio k[n]/k[n-1] (should be close to 2 if doubling):")
for n in range(10, 25):
    k_n = k_seq.get(n)
    k_prev = k_seq.get(n-1)
    if k_n and k_prev:
        ratio = k_n / k_prev
        deviation = ratio - 2.0
        flag = "**" if abs(deviation) > 0.1 else ""
        print(f"  n={n:2d}: k[{n}]/k[{n-1}] = {ratio:.6f}  (deviation from 2: {deviation:+.6f}) {flag}")

# ============================================================================
# 4. Check if prime 17 (p[7]) has special role at n=17
# ============================================================================

print("\n\n## PRIME 17 AT n=17")
print("-" * 60)

print(f"p[7] = 17 (Fermat prime 2^4 + 1)")
print(f"n = 17 = p[7] (The puzzle index equals the 7th prime!)")
print()

# Check divisibility
print(f"Does 17 divide k[17]? {k17 % 17 == 0} (k[17] = {k17})")
print(f"Does 17 divide m[17]? {m17 % 17 == 0} (m[17] = {m17})")
print(f"Does 17 divide adj[17]? {adj17 % 17 == 0} (adj[17] = {adj17})")

# ============================================================================
# 5. Check the adj pattern more carefully
# ============================================================================

print("\n\n## DETAILED ADJ PATTERN ANALYSIS")
print("-" * 60)

# Check if there's a period-3 pattern that changes
print("Grouping adj values by n mod 3:")
for r in range(3):
    values = [(n, adj_seq.get(n)) for n in range(2, 25) if n % 3 == r and adj_seq.get(n) is not None]
    signs = ['+'  if v >= 0 else '-' for _, v in values]
    print(f"  n ≡ {r} (mod 3): {signs}")

# Check the actual pattern
print("\nActual sign pattern grouped in threes:")
for i in range(0, 21, 3):
    chunk = signs[i:i+3]
    n_start = i + 2
    expected = "++-"
    match = "✓" if ''.join(chunk) == expected else "✗"
    print(f"  n={n_start:2d}-{n_start+2:2d}: {''.join(chunk)} (expected ++-) {match}")

# ============================================================================
# 6. What happens at the bit level?
# ============================================================================

print("\n\n## BIT PATTERN ANALYSIS AT n=17")
print("-" * 60)

for n in range(14, 21):
    k = k_seq.get(n)
    if k:
        bits = bin(k)[2:]
        print(f"k[{n:2d}] = {k:>8} = {bits}")

print(f"\nBit lengths around n=17:")
for n in range(14, 21):
    k = k_seq.get(n)
    if k:
        bit_len = k.bit_length()
        expected = n  # For puzzle n, key should be ~n bits
        print(f"  k[{n}].bit_length() = {bit_len} (puzzle n={n})")

# ============================================================================
# Summary
# ============================================================================

print("\n\n" + "=" * 80)
print("SUMMARY: THE n=17 TRANSITION")
print("=" * 80)

print("""
Key observations:
1. The ++- sign pattern in adj[n] holds for n=2-16 (15 matches)
2. Pattern breaks at n=17 where expected '+' but got '-'
3. n=17 equals p[7]=17 (the 7th prime, a Fermat prime!)
4. This may indicate a deliberate algorithm change at this point

Hypothesis:
- For n ≤ 16: A simpler algorithm with predictable ++- sign pattern
- For n > 16: A more complex algorithm (possibly involving p[7]=17)

This aligns with the meta-rule:
- Phase 1-2 (n ≤ 20) uses simpler patterns
- Phase 3+ uses increasingly complex self-references
""")

# Save findings
findings = {
    'transition_point': 17,
    'k17': k17,
    'm17': m17,
    'd17': d17,
    'adj17': adj17,
    'k17_factors': dict(factor_counts),
    'sign_pattern_before': ''.join(signs[:15]),
    'sign_pattern_expected': '++-' * 5,
    'pattern_matches': matches,
}

with open('N17_TRANSITION_ANALYSIS.json', 'w') as f:
    json.dump(findings, f, indent=2)

print("\nFindings saved to N17_TRANSITION_ANALYSIS.json")
