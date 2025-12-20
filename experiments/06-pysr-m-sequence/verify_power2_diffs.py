#!/usr/bin/env python3
"""
Verify if differences from 2^n match adj-sequence or other patterns.
"""

import math

# Complete m-sequence
M_SEQ = {
    2: 1, 3: 1, 4: 22, 5: 9, 6: 19, 7: 50, 8: 23, 9: 493, 10: 19,
    11: 1921, 12: 1241, 13: 8342, 14: 2034, 15: 26989, 16: 8470,
    17: 138269, 18: 255121, 19: 564091, 20: 900329, 21: 670674,
    22: 1603443, 23: 8804812, 24: 1693268, 25: 29226275, 26: 78941020,
    27: 43781837, 28: 264700930, 29: 591430834, 30: 105249691, 31: 2111419265
}

# adj-sequence (from data_for_csolver.json)
ADJ_SEQ = {
    2: 1, 3: 1, 4: -6, 5: 5, 6: 7, 7: -22, 8: 72, 9: 19, 10: -420,
    11: 127, 12: 373, 13: -150, 14: 112, 15: 5779, 16: -2224, 17: -7197,
    18: 7023, 19: -39803, 20: 148247, 21: 85130, 22: -616025, 23: -416204,
    24: 3231072, 25: 4328157, 26: -11832156, 27: 2872217, 28: 3734526,
    29: -54559922, 30: 231744296, 31: 36064383
}

D_SEQ = {
    2: 2, 3: 3, 4: 1, 5: 2, 6: 2, 7: 2, 8: 4, 9: 1, 10: 7,
    11: 1, 12: 2, 13: 1, 14: 4, 15: 1, 16: 4, 17: 1, 18: 1,
    19: 1, 20: 1, 21: 2, 22: 2, 23: 1, 24: 4, 25: 1, 26: 1,
    27: 2, 28: 1, 29: 1, 30: 4, 31: 1
}

print("=" * 80)
print("POWER-OF-2 DIFFERENCE ANALYSIS")
print("=" * 80)

print("\nFor each m[n], find closest 2^k and analyze the difference:")
print()

for n in range(16, 32):
    m_n = M_SEQ[n]
    adj_n = ADJ_SEQ.get(n, 0)
    d_n = D_SEQ.get(n, 1)

    # Find closest power of 2
    log2_m = math.log2(m_n) if m_n > 0 else 0
    k_low = int(log2_m)
    k_high = k_low + 1

    # Check both 2^k_low and 2^k_high
    diff_low = m_n - 2**k_low  # m_n = 2^k_low + diff
    diff_high = 2**k_high - m_n  # m_n = 2^k_high - diff

    # Use whichever gives smaller absolute difference
    if abs(diff_low) <= abs(diff_high):
        k = k_low
        diff = diff_low
        formula = f"2^{k} + {diff}"
    else:
        k = k_high
        diff = -diff_high
        formula = f"2^{k} - {-diff}"

    print(f"n={n:2d}: m[n]={m_n:>12,}  d[n]={d_n}")
    print(f"       Best: m[{n}] = {formula}")
    print(f"       diff = {diff:>12,}")
    print(f"       adj[{n}] = {adj_n:>12,}")

    # Check if diff matches any adj value or m value
    matches = []
    for i in range(2, n):
        if abs(diff) == abs(ADJ_SEQ.get(i, float('inf'))):
            matches.append(f"±adj[{i}]")
        if abs(diff) == M_SEQ.get(i, 0):
            matches.append(f"m[{i}]")

    # Check if diff = adj[n]
    if diff == adj_n:
        matches.append(f"adj[{n}] EXACT MATCH!")
    elif abs(diff) == abs(adj_n):
        matches.append(f"|adj[{n}]|")

    # Check if diff = -adj[n] (sign flip)
    if diff == -adj_n:
        matches.append(f"-adj[{n}] EXACT!")

    if matches:
        print(f"       MATCHES: {', '.join(matches)}")
    print()

print("=" * 80)
print("CHECKING m[n] = 2^k + adj[n] RELATIONSHIP")
print("=" * 80)
print()

for n in range(16, 32):
    m_n = M_SEQ[n]
    adj_n = ADJ_SEQ.get(n, 0)

    # Check various k values
    for k in range(4, 35):
        power = 2**k
        if power > m_n * 100:
            break

        # m[n] = 2^k + adj[n]?
        if power + adj_n == m_n:
            print(f"m[{n}] = 2^{k} + adj[{n}] = {power} + {adj_n} = {m_n} ✓")

        # m[n] = 2^k - adj[n]?
        if power - adj_n == m_n:
            print(f"m[{n}] = 2^{k} - adj[{n}] = {power} - {adj_n} = {m_n} ✓")

print()
print("=" * 80)
print("CHECKING m[n] + adj[n] = 2^k RELATIONSHIP")
print("=" * 80)
print()

for n in range(16, 32):
    m_n = M_SEQ[n]
    adj_n = ADJ_SEQ.get(n, 0)

    sum_val = m_n + adj_n
    if sum_val > 0:
        log2 = math.log2(sum_val)
        if abs(log2 - round(log2)) < 0.0001:  # Is power of 2?
            k = round(log2)
            print(f"m[{n}] + adj[{n}] = {m_n} + {adj_n} = {sum_val} = 2^{k} ✓")

    diff_val = m_n - adj_n
    if diff_val > 0:
        log2 = math.log2(diff_val)
        if abs(log2 - round(log2)) < 0.0001:  # Is power of 2?
            k = round(log2)
            print(f"m[{n}] - adj[{n}] = {m_n} - {adj_n} = {diff_val} = 2^{k} ✓")
