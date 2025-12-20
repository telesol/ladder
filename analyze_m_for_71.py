#!/usr/bin/env python3
"""
Analyze m-values near n=71 to find derivation patterns.
Goal: Derive m[71] from the construction rules.
"""

import json
from fractions import Fraction

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

# Recent m and d values (for puzzles 60-70)
print("=" * 80)
print("RECENT M AND D VALUES")
print("=" * 80)
print(f"{'n':>4} {'m[n]':>30} {'d[n]':>6} {'n%3':>4} {'d mod':>6}")
print("-" * 80)

for n in range(60, 71):
    idx = n - 2  # corrected indexing
    if idx < len(m_seq):
        m_n = m_seq[idx]
        d_n = d_seq[idx]
        print(f"{n:>4} {m_n:>30} {d_n:>6} {n%3:>4} {d_n % 3 if d_n else '-':>6}")

print("\n" + "=" * 80)
print("FACTORIZATION ANALYSIS OF RECENT M-VALUES")
print("=" * 80)

def factor_simple(n):
    """Simple factorization for analysis."""
    if n <= 1:
        return {n: 1}
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = 1
    return factors

# Check for 17 (√2 convergent) presence
print("\nChecking for 17 factor (√2 convergent):")
for n in range(60, 71):
    idx = n - 2
    if idx < len(m_seq):
        m_n = m_seq[idx]
        if m_n % 17 == 0:
            print(f"  m[{n}] = {m_n} = 17 × {m_n // 17}")

# Check for 22 (π convergent) presence
print("\nChecking for 22 factor (π convergent):")
for n in range(60, 71):
    idx = n - 2
    if idx < len(m_seq):
        m_n = m_seq[idx]
        if m_n % 22 == 0:
            print(f"  m[{n}] = {m_n} = 22 × {m_n // 22}")

# Check for 113 (π convergent) presence
print("\nChecking for 113 factor (π convergent):")
for n in range(60, 71):
    idx = n - 2
    if idx < len(m_seq):
        m_n = m_seq[idx]
        if m_n % 113 == 0:
            print(f"  m[{n}] = {m_n} = 113 × {m_n // 113}")

# Convergent database
print("\n" + "=" * 80)
print("CONVERGENT VALUES (EXTENDED)")
print("=" * 80)

def cf_expansion(x, n_terms=30):
    """Get continued fraction expansion."""
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
    """Generate convergents from continued fraction."""
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
    'π': (PI, cf_expansion(PI, 30)),
    'e': (E, cf_expansion(E, 30)),
    '√2': (SQRT2, cf_expansion(SQRT2, 30)),
    'φ': (PHI, cf_expansion(PHI, 30)),
    'ln2': (LN2, cf_expansion(LN2, 30)),
    '√3': (SQRT3, cf_expansion(SQRT3, 30)),
}

# Build convergent lookup
all_convergents = {}
for name, (value, cf) in constants.items():
    convs = convergents_from_cf(cf)
    all_convergents[name] = {
        'numerators': [c[0] for c in convs],
        'denominators': [c[1] for c in convs]
    }

print("\nLarge convergent values (useful for m[71]):")
for name, data in all_convergents.items():
    large_nums = [(i, n) for i, n in enumerate(data['numerators']) if n > 10**15]
    if large_nums:
        print(f"\n{name} numerators > 10^15:")
        for i, n in large_nums[:5]:
            print(f"  idx {i}: {n}")

# Analysis for n=71
print("\n" + "=" * 80)
print("PREDICTION FRAMEWORK FOR m[71]")
print("=" * 80)

# Pattern from FORMULA_PATTERNS.md:
# n=71, n%3=2
# If d=1: operation is PRODUCT, constant is √2
# If d=2: constant is ln2

print("\nBased on n=71:")
print(f"  n % 3 = {71 % 3}")
print(f"  If d[71] = 1: Operation = PRODUCT, Constant = √2")
print(f"  If d[71] = 2: Constant = ln2")

# Look at d-sequence pattern
print("\nD-sequence pattern analysis:")
print("Recent: d[66]=1, d[67]=1, d[68]=2, d[69]=1, d[70]=2")

# Count d=1 vs d=2 for n%3=2
d1_count = 0
d2_count = 0
for n in range(10, 71):
    if n % 3 == 2:
        idx = n - 2
        if idx < len(d_seq):
            if d_seq[idx] == 1:
                d1_count += 1
            elif d_seq[idx] == 2:
                d2_count += 1

print(f"\nFor n ≡ 2 (mod 3): d=1 appears {d1_count} times, d=2 appears {d2_count} times")

# Estimate m[71] magnitude
print("\nMagnitude analysis:")
m_66 = m_seq[64]  # 395435327538483377
m_67 = m_seq[65]  # 35869814695994276026
m_68 = m_seq[66]  # 340563526170809298635
m_69 = m_seq[67]  # 34896088136426753598
m_70 = m_seq[68]  # 268234543517713141517

print(f"m[66] = {m_66:>30} (10^{len(str(m_66))-1})")
print(f"m[67] = {m_67:>30} (10^{len(str(m_67))-1})")
print(f"m[68] = {m_68:>30} (10^{len(str(m_68))-1})")
print(f"m[69] = {m_69:>30} (10^{len(str(m_69))-1})")
print(f"m[70] = {m_70:>30} (10^{len(str(m_70))-1})")

# Growth rate
ratio_67_66 = m_67 / m_66
ratio_68_67 = m_68 / m_67
ratio_69_68 = m_69 / m_68
ratio_70_69 = m_70 / m_69

print(f"\nGrowth ratios:")
print(f"m[67]/m[66] = {ratio_67_66:.4f}")
print(f"m[68]/m[67] = {ratio_68_67:.4f}")
print(f"m[69]/m[68] = {ratio_69_68:.4f}")
print(f"m[70]/m[69] = {ratio_70_69:.4f}")

# The pattern is NOT simple growth - it varies by d[n]!
# Let's look at same d-values
print("\nLooking at pairs with same d:")
for d_val in [1, 2]:
    print(f"\nd[n] = {d_val}:")
    prev_m = None
    prev_n = None
    for n in range(60, 71):
        idx = n - 2
        if idx < len(d_seq) and d_seq[idx] == d_val:
            m_n = m_seq[idx]
            if prev_m:
                ratio = m_n / prev_m
                print(f"  m[{n}]/m[{prev_n}] = {ratio:.4f} (gap={n-prev_n})")
            prev_m = m_n
            prev_n = n

# If we assume d[71]=1 or d[71]=2, estimate m[71]
print("\n" + "=" * 80)
print("ESTIMATES FOR m[71]")
print("=" * 80)

# Last m with d=1: m[69] = 34896088136426753598
# Last m with d=2: m[70] = 268234543517713141517

# Average ratio for d=1 sequences in this range
# m[67]/m[66] ≈ 90.7 (both d=1)
# m[69]/m[67] ≈ 0.97 (both d=1)

# The formula gives us constraints!
# k[71] = 2*k[70] + 2^71 - m[71]*k[d[71]]
# We need k[71] to be in [2^70, 2^71-1]

# From earlier analysis:
# k[71] ≈ 1,859,734,427,016,643,246,361 (from constraint analysis)
# k[70] = 970,436,974,005,023,690,481

import sqlite3
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

k_70 = k[70]
two_71 = 2**71

print(f"\nk[70] = {k_70}")
print(f"2^71 = {two_71}")

# If d[71] = 1, k[d[71]] = k[1] = 1
# k[71] = 2*k[70] + 2^71 - m[71]*1
# m[71] = 2*k[70] + 2^71 - k[71]

# If d[71] = 2, k[d[71]] = k[2] = 3
# k[71] = 2*k[70] + 2^71 - m[71]*3
# m[71] = (2*k[70] + 2^71 - k[71]) / 3

# We estimated k[71] ≈ 1,859,734,427,016,643,246,361
k_71_est = 1859734427016643246361

if True:  # d=1 case
    m_71_d1 = 2*k_70 + two_71 - k_71_est
    print(f"\nIf d[71]=1: m[71] = 2*k[70] + 2^71 - k[71]")
    print(f"           m[71] = {m_71_d1}")
    print(f"           Magnitude: 10^{len(str(abs(m_71_d1)))-1}")

if True:  # d=2 case
    numerator = 2*k_70 + two_71 - k_71_est
    if numerator % 3 == 0:
        m_71_d2 = numerator // 3
        print(f"\nIf d[71]=2: m[71] = (2*k[70] + 2^71 - k[71]) / 3")
        print(f"           m[71] = {m_71_d2}")
        print(f"           Magnitude: 10^{len(str(abs(m_71_d2)))-1}")
    else:
        print(f"\nIf d[71]=2: NOT DIVISIBLE BY 3 - d[71] ≠ 2")

# Compare with expected magnitude
print("\n" + "=" * 80)
print("MAGNITUDE COMPARISON")
print("=" * 80)
print(f"Expected m[71] magnitude: ~10^20 (based on m[67..70])")
print(f"If d=1: |m[71]| = 10^{len(str(abs(m_71_d1)))-1}")
if 'numerator' in dir() and numerator % 3 == 0:
    print(f"If d=2: |m[71]| = 10^{len(str(abs(m_71_d2)))-1}")

# Check if m[71] candidates appear in convergent products
print("\n" + "=" * 80)
print("CONVERGENT MATCH CHECK")
print("=" * 80)

# For d=1 case, check if m_71_d1 is a product of convergents
if m_71_d1 > 0:
    print(f"\nChecking if m[71]={m_71_d1} matches convergent patterns...")

    # Check for 17 factor (common in √2 products)
    if m_71_d1 % 17 == 0:
        quotient = m_71_d1 // 17
        print(f"  m[71] = 17 × {quotient}")
        # Check if quotient is a prime
        is_prime = True
        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
            if quotient % p == 0 and quotient != p:
                is_prime = False
                break
        if is_prime and quotient < 10**15:
            print(f"  {quotient} might be prime!")
