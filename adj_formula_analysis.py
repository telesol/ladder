#!/usr/bin/env python3
"""
adj[n] Formula Derivation
========================
Systematically analyze adj[n] = k[n] - 2*k[n-1] for n=2 to n=70

Tasks:
1. Extract adj[n] from k-sequence in database
2. Analyze adj[n] mod p for primes p = 2,3,5,7,11,13,17,19
3. Check continued fraction relationships (π, e, √2)
4. Find recurrence relations
5. Test factorization hypothesis: adj[n] = ±2^a × 3^b × p
"""

import json
import math
from fractions import Fraction
from collections import defaultdict
import sqlite3

# Load data
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

# Extract sequences
m_seq = data['m_seq']
d_seq = data['d_seq']
adj_seq = data['adj_seq']  # Only n=2 to n=31 provided
k_base = {int(k): v for k, v in data['k_base'].items()}

print("=" * 80)
print("ADJ[N] FORMULA DERIVATION")
print("=" * 80)
print()

# ============================================================================
# TASK 1.1: Extract adj[n] for n=2 to n=70 from k-sequence
# ============================================================================

print("TASK 1.1: Extracting adj[n] from database k-sequence")
print("-" * 80)

# Load k-values from database
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()

# Get all k-values for puzzles 1-70
cursor.execute("""
    SELECT puzzle_id, priv_hex
    FROM keys
    WHERE puzzle_id BETWEEN 1 AND 70
    ORDER BY puzzle_id
""")
rows = cursor.fetchall()
conn.close()

# Build k-sequence (1-indexed)
k_seq = {0: 0}  # k[0] doesn't exist, but helpful for indexing
for puzzle_id, priv_hex in rows:
    # Convert hex to decimal
    k_seq[puzzle_id] = int(priv_hex, 16)

print(f"Loaded {len(k_seq)-1} k-values from database (k[1] to k[70])")
print()

# Compute adj[n] = k[n] - 2*k[n-1] for n=2 to n=70
adj_computed = {}
for n in range(2, 71):
    if n in k_seq and (n-1) in k_seq:
        adj_computed[n] = k_seq[n] - 2 * k_seq[n-1]

print(f"Computed adj[n] for n=2 to n={max(adj_computed.keys())}")
print()

# Verify against provided adj_seq
print("Verification against data_for_csolver.json:")
mismatches = 0
for i, adj_val in enumerate(adj_seq, start=2):
    if i in adj_computed:
        if adj_computed[i] != adj_val:
            print(f"  MISMATCH at n={i}: computed={adj_computed[i]}, provided={adj_val}")
            mismatches += 1

if mismatches == 0:
    print(f"  ✓ All {len(adj_seq)} provided adj values match computed values")
else:
    print(f"  ✗ {mismatches} mismatches found!")
print()

# Display adj[n] values
print("adj[n] values (n=2 to n=70):")
print("-" * 80)
for n in range(2, min(32, max(adj_computed.keys())+1)):  # First 30 values
    adj_val = adj_computed[n]
    sign = '+' if adj_val >= 0 else '-'
    print(f"  adj[{n:2d}] = {adj_val:20,d}  ({sign})")
print()

# ============================================================================
# TASK 1.2: Analyze adj[n] mod p for primes p = 2,3,5,7,11,13,17,19
# ============================================================================

print("TASK 1.2: Analyzing adj[n] mod p for small primes")
print("-" * 80)

primes = [2, 3, 5, 7, 11, 13, 17, 19]

# For each prime, compute adj[n] mod p
mod_patterns = {p: [] for p in primes}
for n in range(2, 71):
    if n in adj_computed:
        for p in primes:
            mod_patterns[p].append(adj_computed[n] % p)

# Display patterns
for p in primes:
    pattern = mod_patterns[p][:30]  # First 30 values
    print(f"adj[n] mod {p:2d}: {pattern[:20]}")

    # Check for periodicity
    if len(pattern) >= 20:
        # Try period lengths 1-10
        for period in range(1, 11):
            is_periodic = True
            for i in range(period, min(len(pattern), 30)):
                if pattern[i] != pattern[i % period]:
                    is_periodic = False
                    break
            if is_periodic:
                print(f"  → PERIODIC with period {period}: {pattern[:period]}")
                break
print()

# ============================================================================
# TASK 1.3: Check continued fraction relationships (π, e, √2)
# ============================================================================

print("TASK 1.3: Checking continued fraction relationships")
print("-" * 80)

# Continued fraction convergents for π, e, √2
cf_pi = [
    (3, 1), (22, 7), (333, 106), (355, 113), (103993, 33102),
    (104348, 33215), (208341, 66317), (312689, 99532)
]

cf_e = [
    (2, 1), (3, 1), (8, 3), (11, 4), (19, 7), (87, 32),
    (106, 39), (193, 71), (1264, 465), (1457, 536)
]

cf_sqrt2 = [
    (1, 1), (3, 2), (7, 5), (17, 12), (41, 29), (99, 70),
    (239, 169), (577, 408), (1393, 985), (3363, 2378)
]

def check_cf_match(adj_val, cf_list, constant_name):
    """Check if adj_val matches any convergent numerator or denominator"""
    abs_adj = abs(adj_val)
    matches = []
    for num, den in cf_list:
        if abs_adj == num:
            matches.append(f"{constant_name} numerator {num}")
        if abs_adj == den:
            matches.append(f"{constant_name} denominator {den}")
    return matches

print("Checking if adj[n] values match continued fraction convergents:")
print()

cf_matches = defaultdict(list)
for n in range(2, 71):
    if n in adj_computed:
        adj_val = adj_computed[n]

        matches = []
        matches.extend(check_cf_match(adj_val, cf_pi, "π"))
        matches.extend(check_cf_match(adj_val, cf_e, "e"))
        matches.extend(check_cf_match(adj_val, cf_sqrt2, "√2"))

        if matches:
            cf_matches[n] = matches

if cf_matches:
    for n in sorted(cf_matches.keys()):
        print(f"  adj[{n:2d}] = {adj_computed[n]:15,d}  →  {', '.join(cf_matches[n])}")
else:
    print("  No direct matches found with standard convergents")
print()

# Check relationships like adj[n] = convergent_i ± convergent_j
print("Checking linear combinations of convergents:")
all_cf_values = set()
for num, den in cf_pi + cf_e + cf_sqrt2:
    all_cf_values.add(num)
    all_cf_values.add(den)

combo_matches = defaultdict(list)
for n in range(2, min(20, max(adj_computed.keys())+1)):  # Check first 18 values
    if n in adj_computed:
        adj_val = adj_computed[n]
        abs_adj = abs(adj_val)

        # Check if adj_val = a ± b where a, b are convergent values
        for a in all_cf_values:
            if abs_adj < a:
                continue
            b = abs_adj - a
            if b in all_cf_values:
                combo_matches[n].append(f"{a} + {b}")
            b = a - abs_adj
            if b in all_cf_values and b > 0:
                combo_matches[n].append(f"{a} - {b}")

if combo_matches:
    for n in sorted(combo_matches.keys())[:5]:  # Show first 5 matches
        print(f"  adj[{n:2d}] = {adj_computed[n]:10,d}  →  {combo_matches[n][0]}")
print()

# ============================================================================
# TASK 1.4: Find recurrence relations
# ============================================================================

print("TASK 1.4: Searching for recurrence relations")
print("-" * 80)

# Test linear recurrences of form: adj[n] = c1*adj[n-1] + c2*adj[n-2] + ... + offset

def test_recurrence(adj_dict, order, start_n):
    """Test if adj[n] follows a linear recurrence of given order"""
    # Collect data points
    n_values = sorted([n for n in adj_dict.keys() if n >= start_n])

    if len(n_values) < order + 5:
        return None

    # Try to find coefficients using first few values
    # For simplicity, test small integer coefficients [-5, 5]
    from itertools import product

    for coeffs in product(range(-5, 6), repeat=order):
        if all(c == 0 for c in coeffs):
            continue

        # Test if recurrence holds for multiple values
        matches = 0
        total_tested = 0

        for i, n in enumerate(n_values[order:order+10]):  # Test on 10 values
            if n not in adj_dict:
                continue

            # Compute predicted value
            predicted = sum(coeffs[j] * adj_dict[n-j-1] for j in range(order))
            actual = adj_dict[n]

            total_tested += 1
            if predicted == actual:
                matches += 1

        if matches >= 8 and total_tested >= 8:  # At least 8/10 matches
            return coeffs, matches, total_tested

    return None

print("Testing linear recurrences (order 1-4):")
for order in range(1, 5):
    result = test_recurrence(adj_computed, order, 2)
    if result:
        coeffs, matches, total = result
        print(f"  Order {order}: adj[n] = {' + '.join(f'{c}*adj[n-{i+1}]' for i, c in enumerate(coeffs))}")
        print(f"    → Matched {matches}/{total} test cases")

print()

# Test specific patterns
print("Testing specific recurrence patterns:")

# Pattern 1: adj[n] = -adj[n-3] (from sign pattern ++-)
print("  Testing: adj[n] = -adj[n-3]")
pattern1_matches = 0
for n in range(5, 17):  # Test on n=5-16 where sign pattern holds
    if n in adj_computed and (n-3) in adj_computed:
        if adj_computed[n] == -adj_computed[n-3]:
            pattern1_matches += 1
            print(f"    ✓ n={n}: adj[{n}] = -adj[{n-3}]")
        else:
            ratio = adj_computed[n] / adj_computed[n-3] if adj_computed[n-3] != 0 else None
            print(f"    ✗ n={n}: ratio = {ratio:.6f}" if ratio else f"    ✗ n={n}")

print()

# Pattern 2: Fibonacci-like recurrence
print("  Testing: adj[n] = adj[n-1] + adj[n-2]")
fib_matches = 0
for n in range(4, 20):
    if n in adj_computed and (n-1) in adj_computed and (n-2) in adj_computed:
        predicted = adj_computed[n-1] + adj_computed[n-2]
        actual = adj_computed[n]
        if predicted == actual:
            fib_matches += 1
            print(f"    ✓ n={n}")
        else:
            diff = actual - predicted
            print(f"    ✗ n={n}: diff = {diff:,}")

print()

# ============================================================================
# TASK 1.5: Test factorization hypothesis
# ============================================================================

print("TASK 1.5: Testing factorization hypothesis adj[n] = ±2^a × 3^b × p")
print("-" * 80)

def prime_factorization(n):
    """Return prime factorization as dict {prime: exponent}"""
    if n == 0:
        return {}

    n = abs(n)
    factors = {}

    # Factor out 2s
    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2

    # Factor out 3s
    while n % 3 == 0:
        factors[3] = factors.get(3, 0) + 1
        n //= 3

    # Try other small primes
    p = 5
    while p * p <= n:
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
        p += 2

    if n > 1:
        factors[n] = 1

    return factors

print("Prime factorizations of adj[n] (n=2 to n=31):")
print()

factorizations = {}
for n in range(2, min(32, max(adj_computed.keys())+1)):
    if n in adj_computed:
        factors = prime_factorization(adj_computed[n])
        factorizations[n] = factors

        # Format factorization
        if not factors:
            fact_str = "0"
        else:
            parts = []
            for p in sorted(factors.keys()):
                exp = factors[p]
                if exp == 1:
                    parts.append(f"{p}")
                else:
                    parts.append(f"{p}^{exp}")
            fact_str = " × ".join(parts)

        sign = '-' if adj_computed[n] < 0 else '+'
        print(f"  adj[{n:2d}] = {sign}{fact_str:40s}  (value: {adj_computed[n]:,})")

print()

# Check hypothesis: only powers of 2 and 3, plus one other prime
print("Checking hypothesis: adj[n] = ±2^a × 3^b × p")
hypothesis_matches = 0
hypothesis_total = 0

for n in range(2, min(32, max(adj_computed.keys())+1)):
    if n in adj_computed and n in factorizations:
        factors = factorizations[n]

        # Count primes other than 2 and 3
        other_primes = [p for p in factors.keys() if p not in [2, 3]]

        hypothesis_total += 1
        if len(other_primes) <= 1:
            hypothesis_matches += 1
            status = "✓"
        else:
            status = "✗"

        print(f"  {status} adj[{n:2d}]: {len(other_primes)} prime(s) besides 2,3: {other_primes}")

print()
print(f"Hypothesis match rate: {hypothesis_matches}/{hypothesis_total} = {100*hypothesis_matches/hypothesis_total:.1f}%")
print()

# ============================================================================
# Sign Pattern Analysis
# ============================================================================

print("SIGN PATTERN ANALYSIS")
print("-" * 80)

signs = []
for n in range(2, 71):
    if n in adj_computed:
        signs.append('+' if adj_computed[n] >= 0 else '-')

print("Sign pattern (n=2 to n=70):")
for i in range(0, len(signs), 20):
    chunk = ''.join(signs[i:i+20])
    n_start = i + 2
    print(f"  n={n_start:2d}-{min(n_start+19, 71)}: {chunk}")

print()

# Check ++- pattern
expected_pattern = ['+', '+', '-']
matches = 0
total = 0

for i in range(len(signs)):
    expected = expected_pattern[i % 3]
    actual = signs[i]
    total += 1
    if expected == actual:
        matches += 1

print(f"++- pattern match rate: {matches}/{total} = {100*matches/total:.1f}%")
print()

# Find where pattern breaks
print("Pattern breaks:")
for i in range(min(30, len(signs))):
    expected = expected_pattern[i % 3]
    actual = signs[i]
    if expected != actual:
        n = i + 2
        print(f"  n={n:2d}: expected '{expected}', got '{actual}' (adj[{n}] = {adj_computed[n]:,})")

print()

# ============================================================================
# Statistical Analysis
# ============================================================================

print("STATISTICAL ANALYSIS")
print("-" * 80)

# Magnitude growth
print("Magnitude growth (log2):")
for n in [2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]:
    if n in adj_computed:
        mag = abs(adj_computed[n])
        log2_mag = math.log2(mag) if mag > 0 else 0
        log2_2n = n
        ratio = log2_mag / log2_2n if log2_2n > 0 else 0
        print(f"  n={n:2d}: |adj[n]| = 2^{log2_mag:.2f}, expected ~2^{log2_2n}, ratio={ratio:.3f}")

print()

# Check if |adj[n]| / 2^n approaches a constant
print("Ratio |adj[n]| / 2^n:")
for n in range(2, min(31, max(adj_computed.keys())+1)):
    if n in adj_computed:
        mag = abs(adj_computed[n])
        power2 = 2 ** n
        ratio = mag / power2
        print(f"  adj[{n:2d}] / 2^{n:2d} = {ratio:.6f}")

print()

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
