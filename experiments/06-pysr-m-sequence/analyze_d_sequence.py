#!/usr/bin/env python3
"""
Research Direction 1: Define d[n] explicitly from constants

Hypotheses to test:
1. d[n] from interleaved digits of π, e, φ
2. d[n] from continued fraction coefficients
3. d[n] as maximizer of some divisibility condition
4. d[n] from prime factorization patterns
"""

import math
import json
from fractions import Fraction

# Load full data
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

d_seq = data['d_seq']
m_seq = data['m_seq']
adj_seq = data['adj_seq']

# Convert to dicts (index 0 = n=2)
D = {n: d_seq[n-2] for n in range(2, 2 + len(d_seq))}
M = {n: m_seq[n-2] for n in range(2, 2 + len(m_seq))}
ADJ = {n: adj_seq[n-2] for n in range(2, 2 + len(adj_seq)) if n-2 < len(adj_seq)}

print("=" * 80)
print("D-SEQUENCE ANALYSIS: Finding the Generation Rule")
print("=" * 80)

# Display d-sequence
print("\nFull d-sequence (n=2 to n=70):")
for start in range(2, len(D)+2, 20):
    end = min(start + 20, len(D)+2)
    line = " ".join([f"{D.get(n, '?'):1d}" for n in range(start, end)])
    print(f"n={start:2d}-{end-1:2d}: {line}")

print("\n" + "=" * 80)
print("HYPOTHESIS 1: Digits of Mathematical Constants")
print("=" * 80)

# Get digits of various constants
def get_digits(x, n_digits=100):
    """Get first n decimal digits of x."""
    s = f"{x:.{n_digits}f}"
    # Remove "0." or "3." etc.
    parts = s.split('.')
    if len(parts) == 2:
        return [int(d) for d in parts[0] + parts[1]][:n_digits]
    return [int(d) for d in parts[0]][:n_digits]

pi_digits = get_digits(math.pi, 80)
e_digits = get_digits(math.e, 80)
phi = (1 + math.sqrt(5)) / 2
phi_digits = get_digits(phi, 80)
sqrt2_digits = get_digits(math.sqrt(2), 80)

print(f"\nπ digits: {pi_digits[:30]}")
print(f"e digits: {e_digits[:30]}")
print(f"φ digits: {phi_digits[:30]}")
print(f"√2 digits: {sqrt2_digits[:30]}")

# Check if d[n] matches any constant's digits
d_list = [D[n] for n in range(2, min(72, len(D)+2))]
print(f"\nd-sequence: {d_list[:30]}")

# Direct match?
def check_digit_match(digits, d_list, offset=0):
    """Check how many d[n] values match digits."""
    matches = 0
    for i, d in enumerate(d_list):
        if i + offset < len(digits) and digits[i + offset] == d:
            matches += 1
    return matches

for const_name, digits in [("π", pi_digits), ("e", e_digits), ("φ", phi_digits), ("√2", sqrt2_digits)]:
    for offset in range(10):
        matches = check_digit_match(digits, d_list, offset)
        if matches > len(d_list) * 0.3:  # More than 30% match
            print(f"{const_name} (offset {offset}): {matches}/{len(d_list)} matches ({100*matches/len(d_list):.1f}%)")

print("\n" + "=" * 80)
print("HYPOTHESIS 2: Continued Fraction Coefficients")
print("=" * 80)

# CF coefficients of various constants
cf_pi = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2, 1, 84, 2, 1, 1, 15, 3, 13, 1, 4]
cf_e = [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, 1, 1, 12, 1, 1, 14, 1, 1, 16, 1, 1, 18, 1, 1, 20]
cf_sqrt2 = [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
cf_phi = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

print(f"\nπ CF: {cf_pi[:20]}")
print(f"e CF: {cf_e[:20]}")
print(f"d-seq: {d_list[:20]}")

# Check CF pattern (clamped to max 8 since d-values are small)
def check_cf_match(cf, d_list, clamp=8):
    matches = 0
    for i, d in enumerate(d_list):
        if i < len(cf):
            cf_clamped = min(cf[i], clamp)
            if cf_clamped == d:
                matches += 1
    return matches

for const_name, cf in [("π", cf_pi), ("e", cf_e), ("√2", cf_sqrt2), ("φ", cf_phi)]:
    matches = check_cf_match(cf, d_list)
    print(f"{const_name} CF: {matches}/{len(d_list[:len(cf)])} matches")

print("\n" + "=" * 80)
print("HYPOTHESIS 3: d[n] as Maximizer (Already Verified)")
print("=" * 80)
print("""
From NEMOTRON analysis, we already know:
    d[n] = max{i : k[i] divides (2^n - adj[n])}

This was verified 67/67 for n=4 to n=70.

This is a DERIVED property, not a generation rule.
The question is: what GENERATES adj[n] such that this d[n] results?
""")

print("\n" + "=" * 80)
print("HYPOTHESIS 4: d[n] Frequency Distribution")
print("=" * 80)

from collections import Counter
d_counts = Counter(d_list)
print("\nFrequency distribution of d-values:")
for d_val in sorted(d_counts.keys()):
    count = d_counts[d_val]
    pct = 100 * count / len(d_list)
    bar = "█" * int(pct / 2)
    print(f"d={d_val}: {count:3d} ({pct:5.1f}%) {bar}")

print("\n" + "=" * 80)
print("HYPOTHESIS 5: d[n] Periodic or Quasi-Periodic?")
print("=" * 80)

# Check for periodicity
def check_periodicity(seq, max_period=20):
    """Check if sequence has any periodicity."""
    results = []
    for period in range(1, max_period + 1):
        matches = 0
        total = 0
        for i in range(period, len(seq)):
            if seq[i] == seq[i - period]:
                matches += 1
            total += 1
        if total > 0:
            results.append((period, matches / total))
    return sorted(results, key=lambda x: -x[1])[:5]

print("\nPeriodicity analysis (top matches):")
periods = check_periodicity(d_list)
for period, match_rate in periods:
    print(f"Period {period}: {100*match_rate:.1f}% match")

print("\n" + "=" * 80)
print("HYPOTHESIS 6: d[n] Related to n's Properties")
print("=" * 80)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

print("\nn | d[n] | n mod 3 | n mod 6 | is_prime(n)")
print("-" * 50)
for n in range(2, 32):
    d = D.get(n, '?')
    mod3 = n % 3
    mod6 = n % 6
    prime = "✓" if is_prime(n) else ""
    print(f"{n:2d} | {d:4} | {mod3:7d} | {mod6:7d} | {prime}")

# Check if d[n]=1 correlates with n being prime or other property
d1_indices = [n for n in range(2, 72) if D.get(n) == 1]
print(f"\nIndices where d[n]=1: {d1_indices[:20]}...")
print(f"Of these, primes: {[n for n in d1_indices if is_prime(n)][:15]}")

print("\n" + "=" * 80)
print("HYPOTHESIS 7: Interleaved Patterns")
print("=" * 80)

# Check if d[n] for even/odd n follow different patterns
d_even = [D[n] for n in range(2, 72, 2) if n in D]
d_odd = [D[n] for n in range(3, 72, 2) if n in D]

print(f"\nd[n] for even n: {d_even[:20]}")
print(f"d[n] for odd n:  {d_odd[:20]}")

print("\n" + "=" * 80)
print("KEY OBSERVATION: d=1 Dominates for Large n")
print("=" * 80)

# Count d=1 in ranges
ranges = [(2, 20), (21, 40), (41, 60), (61, 72)]
for start, end in ranges:
    subset = [D.get(n, 0) for n in range(start, end) if n in D]
    d1_count = subset.count(1)
    print(f"n={start:2d}-{end:2d}: d=1 appears {d1_count}/{len(subset)} times ({100*d1_count/len(subset):.1f}%)")

print("""
CONCLUSION:
The d-sequence appears to be DERIVED from the divisibility condition:
    d[n] = max{i : k[i] | (2^n - adj[n])}

Rather than being generated from constant digits, d[n] is a CONSEQUENCE
of the adj[n] values. The key to understanding d[n] is understanding adj[n].

Next step: Analyze adj[n] patterns to find the generating function.
""")
