#!/usr/bin/env python3
"""
Verify m[71] candidates against construction patterns.
"""

import sqlite3

# Candidates from constraint analysis
k_71_est = 1602101676614237534489
m_71_d1 = 2699955512830632453321
m_71_d2 = 899985170943544151107

# Load k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {row[0]: int(row[1], 16) for row in cur.fetchall()}
conn.close()

print("=" * 80)
print("VERIFYING m[71] CANDIDATES")
print("=" * 80)

def factor_basic(n):
    """Basic factorization for small factors."""
    factors = []
    orig = n
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        while n % p == 0:
            factors.append(p)
            n //= p
    if n > 1:
        factors.append(n)
    return factors

def is_prime_simple(n, checks=100):
    """Simple primality test."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if n == p:
            return True
        if n % p == 0:
            return False
    # Miller-Rabin for larger numbers
    import random
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(min(checks, 20)):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

print("\n" + "-" * 80)
print("CANDIDATE 1: d[71] = 1, m[71] = 2699955512830632453321")
print("-" * 80)

m1 = m_71_d1
print(f"\nm[71] = {m1}")
print(f"Magnitude: 10^{len(str(m1))-1}")

# Check small factors
small_factors = []
n = m1
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 113, 355]:
    while n % p == 0:
        small_factors.append(p)
        n //= p
print(f"Small factors: {small_factors}")
print(f"Remaining: {n}")

# Check 17-network
if m1 % 17 == 0:
    quotient = m1 // 17
    print(f"17-network: m[71] = 17 × {quotient}")
    if is_prime_simple(quotient):
        print(f"  {quotient} is prime!")
else:
    print("Not in 17-network (not divisible by 17)")

# Check 22-network (π)
if m1 % 22 == 0:
    print(f"π-network: m[71] = 22 × {m1 // 22}")

# Check 113-network (π)
if m1 % 113 == 0:
    print(f"π-network: m[71] = 113 × {m1 // 113}")

print("\n" + "-" * 80)
print("CANDIDATE 2: d[71] = 2, m[71] = 899985170943544151107")
print("-" * 80)

m2 = m_71_d2
print(f"\nm[71] = {m2}")
print(f"Magnitude: 10^{len(str(m2))-1}")

# Check small factors
small_factors = []
n = m2
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 113, 355]:
    while n % p == 0:
        small_factors.append(p)
        n //= p
print(f"Small factors: {small_factors}")
print(f"Remaining: {n}")

# Check 17-network
if m2 % 17 == 0:
    quotient = m2 // 17
    print(f"17-network: m[71] = 17 × {quotient}")
    if is_prime_simple(quotient):
        print(f"  {quotient} is prime!")
else:
    print("Not in 17-network (not divisible by 17)")

# Check if quotient/3 is more interesting for d=2
if m2 % 3 == 0:
    print(f"Divisible by 3: m[71] = 3 × {m2 // 3}")

print("\n" + "=" * 80)
print("D-MINIMIZATION CHECK")
print("=" * 80)

# The key constraint: d[n] minimizes m[n]
# Check if d=1 gives smaller m than d=2

print(f"\nm[71] for d=1: {m_71_d1}")
print(f"m[71] for d=2: {m_71_d2}")
print(f"\nd=2 gives smaller m ({m_71_d2} < {m_71_d1})")
print(f"Ratio: m[71,d=1] / m[71,d=2] = {m_71_d1 / m_71_d2:.6f}")

# If d-minimizes-m principle holds, d[71] should be 2!
if m_71_d2 < m_71_d1:
    print("\n*** According to d-minimizes-m principle: d[71] = 2 ***")
    print(f"*** m[71] = {m_71_d2} ***")

print("\n" + "=" * 80)
print("VERIFYING k[71] WITH SELECTED m[71]")
print("=" * 80)

# Use d=2 since it minimizes m
d_71 = 2
m_71 = m_71_d2
k_d = k[d_71]

# Verify formula: k[71] = 2*k[70] + 2^71 - m[71] * k[d[71]]
k_70 = k[70]
k_71_verify = 2 * k_70 + 2**71 - m_71 * k_d

print(f"\nUsing d[71] = {d_71}, m[71] = {m_71}:")
print(f"k[71] = 2*k[70] + 2^71 - m[71]*k[{d_71}]")
print(f"     = 2*{k_70} + {2**71} - {m_71}*{k_d}")
print(f"     = {k_71_verify}")

print(f"\nCompare with constraint estimate: {k_71_est}")
print(f"Match: {'YES' if k_71_verify == k_71_est else 'NO'}")

# Verify bit range
if 2**70 <= k_71_verify <= 2**71 - 1:
    print("✓ k[71] is in valid 71-bit range")
else:
    print("✗ k[71] is NOT in valid range!")

print(f"\nFinal k[71] = {k_71_verify}")
print(f"Hex: {hex(k_71_verify)}")

# Now let's verify by chaining to k[75]
print("\n" + "=" * 80)
print("CHAIN VERIFICATION TO k[75]")
print("=" * 80)

# We need m[72], m[73], m[74] to chain forward
# But we don't have them. Let's use the offset-based approach instead.

# The mod-3 relationship gives us:
# k[75] = 9*k[72] + off[75]
# and k[72] = 9*k[69] + off[72]
# So k[75] = 81*k[69] + 9*off[72] + off[75]

k_69 = k[69]
k_75 = k[75]

constraint_75 = k_75 - 81 * k_69
print(f"k[69] = {k_69}")
print(f"k[75] = {k_75}")
print(f"Constraint: 9*off[72] + off[75] = {constraint_75}")

# This doesn't directly involve k[71], but we can use it to cross-check
# once we have k[72] estimate

print("\n(Note: k[72] is on a different mod-3 chain than k[71])")
print("(k[71] is on the 68→71→74→77→80 chain)")
