#!/usr/bin/env python3
"""
Extend Patterns to n=71+ and Test Prime 17 Prediction at n=96
==============================================================

Key discoveries from nested pattern search:
1. m-value difference patterns: p[m[a]-m[b]] or p[m[a]+m[b]]
2. Linear patterns: p[an + b]
3. Combined patterns: p[n + m[a] - m[b]]

Prime 17 prediction: 17 should divide m[96] (doubling from 12→24→48→96)
"""

import json
from math import sqrt
from functools import lru_cache

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
m = {n: m_seq[n-2] for n in range(2, 2 + len(m_seq))}
d = {n: d_seq[n-2] for n in range(2, 2 + len(d_seq))}

print("=" * 80)
print("M-SEQUENCE VALUES n=71-75 (If Available)")
print("=" * 80)

# Check if we have data beyond n=70
max_n = 2 + len(m_seq) - 1
print(f"Data available up to n={max_n}")
print()

for n in range(71, min(76, max_n + 1)):
    if n in m:
        print(f"m[{n}] = {m[n]:,}")

# Prime generation
@lru_cache(maxsize=500000)
def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(sqrt(n)) + 1, 2):
        if n % i == 0: return False
    return True

primes = []
candidate = 2
while len(primes) < 500000:
    if is_prime(candidate):
        primes.append(candidate)
    candidate += 1

prime_to_index = {p: i+1 for i, p in enumerate(primes)}

def p(i):
    if i < 1 or i > len(primes): return None
    return primes[i-1]

def pi(prime_val):
    return prime_to_index.get(prime_val)

# ============================================================================
# Verify Prime 17 positions from earlier analysis
# ============================================================================

print("\n" + "=" * 80)
print("PRIME 17 VERIFICATION")
print("=" * 80)

print("\nKnown positions where 17 divides m[n]: [9, 11, 12, 24, 48, 67]")
print("\nVerification:")

for n in [9, 11, 12, 24, 48, 67]:
    if n in m:
        target = m[n]
        if target % 17 == 0:
            quotient = target // 17
            print(f"  n={n}: m[{n}] = {target:,} = 17 × {quotient:,} ✓")
        else:
            print(f"  n={n}: m[{n}] = {target:,} - NOT divisible by 17 ✗")

# ============================================================================
# Check 17 divisibility beyond known
# ============================================================================

print("\n" + "=" * 80)
print("SCANNING FOR MORE POSITIONS WHERE 17 DIVIDES m[n]")
print("=" * 80)

positions_17 = []
for n in range(2, max_n + 1):
    if m[n] % 17 == 0:
        positions_17.append(n)

print(f"\nAll positions where 17 | m[n]: {positions_17}")

# Analyze the pattern
print("\nAnalyzing the doubling pattern:")
print("  12 → 24 → 48 → 96 → 192 ...")
print()

# Check for a pattern in the positions
diffs = [positions_17[i+1] - positions_17[i] for i in range(len(positions_17)-1)]
print(f"Differences between consecutive positions: {diffs}")

# Check for doubling starting from 12
doubling_from_12 = [12, 24, 48, 96, 192]
found_in_doubling = [pos for pos in positions_17 if pos in doubling_from_12]
print(f"\nPositions in doubling sequence from 12: {found_in_doubling}")

# ============================================================================
# Analyze n=71-75 patterns if data exists
# ============================================================================

if max_n >= 71:
    print("\n" + "=" * 80)
    print("PATTERN ANALYSIS FOR n=71-75")
    print("=" * 80)

    for n in range(71, min(76, max_n + 1)):
        if n not in m:
            continue

        target = m[n]
        print(f"\nn={n}: m[{n}] = {target:,}")

        # Check for p[n - m[k]] patterns
        patterns_found = []
        for k in range(2, 9):
            idx = n - m[k]
            if idx >= 1:
                prime_val = p(idx)
                if prime_val and target % prime_val == 0:
                    patterns_found.append(f"p[n-m[{k}]] = p[{idx}] = {prime_val}")

        # Check for p[n + m[k]] patterns
        for k in range(2, 9):
            idx = n + m[k]
            prime_val = p(idx)
            if prime_val and target % prime_val == 0:
                patterns_found.append(f"p[n+m[{k}]] = p[{idx}] = {prime_val}")

        # Check m-value difference patterns
        for a in range(2, 9):
            for b in range(2, 9):
                if a != b:
                    idx = abs(m[a] - m[b])
                    if idx >= 1:
                        prime_val = p(idx)
                        if prime_val and target % prime_val == 0:
                            if m[a] > m[b]:
                                patterns_found.append(f"p[m[{a}]-m[{b}]] = p[{idx}] = {prime_val}")
                            else:
                                patterns_found.append(f"p[m[{b}]-m[{a}]] = p[{idx}] = {prime_val}")

        if patterns_found:
            print("  Patterns found:")
            for pf in set(patterns_found):  # Use set to remove duplicates
                print(f"    {pf}")

# ============================================================================
# Extend pattern prediction
# ============================================================================

print("\n" + "=" * 80)
print("PATTERN PREDICTIONS FOR n > max available")
print("=" * 80)

print("""
Based on discovered patterns, for n beyond available data:

1. **p[n - m[7]] = p[n-50]** should appear at n where:
   - n-50 yields a prime index that divides m[n]
   - Already seen at n=51, 55, 58

2. **p[n - m[8]] = p[n-23]** should appear at n where:
   - n-23 yields a prime index that divides m[n]
   - Already seen at n=43, 70

3. **Prime 17 (p[7])** prediction:
   - Doubling sequence: 12 → 24 → 48 → 96 → 192
   - PREDICTION: 17 | m[96] and 17 | m[192]

4. **Linear patterns p[an+b]** are common:
   - p[2n-23], p[3n-49], p[4n-1], etc.
   - These likely continue for higher n

5. **m-value combination patterns**:
   - p[m[4]-m[6]] = p[3] = 5 (very frequent)
   - p[m[8]-m[4]] = p[1] = 2 (very frequent)
   - p[m[4]+m[8]] = p[45] = 197
   - p[n+m[5]-m[7]] = p[n-41] (seen at n=70)
""")

# ============================================================================
# Summary of key formula patterns
# ============================================================================

print("=" * 80)
print("KEY FORMULA PATTERNS SUMMARY")
print("=" * 80)

summary = """
The m-sequence formulas follow these structural patterns:

## PHASE 4+ FORMULA VOCABULARY (n > 35)

### Small Prime Factors (almost always present):
- p[1] = 2 via p[m[8]-m[4]] = p[23-22] = p[1]
- p[3] = 5 via p[m[4]-m[6]] = p[22-19] = p[3]
- p[2] = 3 via p[m[2]+m[3]] = p[1+1] = p[2]

### Self-Referential Patterns:
- p[n - m[7]] (n - 50): seen at n=51, 55, 58
- p[n - m[8]] (n - 23): seen at n=43, 70
- p[n + m[5]] (n + 9): seen at n=61

### Direct m-value References:
- p[m[7]] = p[50] = 229: seen at n=55
- p[m[5]] = p[9] = 23: seen at n=47

### m-value Combinations:
- p[m[a] - m[b]]: various combinations
- p[m[a] + m[b]]: various combinations
- p[n + m[a] - m[b]]: combined patterns (n=70)

### Linear in n:
- p[2n + c] for various c
- p[3n + c] for various c
- p[4n + c] for various c

### Coefficient × m[k]:
- p[c × m[k]] for small c and k in [5,6,7,8]

### The "Remaining Large Prime":
- Most formulas have a large prime factor that may require:
  - Very large prime index (> 1M)
  - Nested combination of multiple m-values
  - Recursive reference to later m-values (forward reference?)
"""
print(summary)

# Save summary
with open('PATTERN_EXTENSION_SUMMARY.json', 'w') as f:
    json.dump({
        'prime_17_positions': positions_17,
        'max_n_available': max_n,
        'key_patterns': {
            'small_primes': ['p[m[8]-m[4]]', 'p[m[4]-m[6]]', 'p[m[2]+m[3]]'],
            'self_referential': ['p[n-m[7]]', 'p[n-m[8]]', 'p[n+m[5]]'],
            'direct_m_ref': ['p[m[7]]', 'p[m[5]]'],
            'linear_n': ['p[2n+c]', 'p[3n+c]', 'p[4n+c]'],
        },
        'prime_17_prediction': {
            'next_expected': 96,
            'doubling_sequence': [12, 24, 48, 96, 192, 384]
        }
    }, f, indent=2)

print("\nSummary saved to PATTERN_EXTENSION_SUMMARY.json")
