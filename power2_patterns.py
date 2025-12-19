#!/usr/bin/env python3
"""Search for m[n] = 2^k ± m[j] patterns."""

import json

# Load data
with open('/home/solo/LA/data_for_csolver.json') as f:
    data = json.load(f)

m_list = data['m_seq']
d_list = data['d_seq']
m_seq = {n: m_list[n-2] for n in range(2, 2 + len(m_list))}
d_seq = {n: d_list[n-2] for n in range(2, 2 + len(d_list))}

print("="*80)
print("POWER OF 2 RELATIONSHIPS: m[n] = 2^k ± m[j]")
print("="*80)
print()

found = []

for n in range(2, 71):
    m = m_seq[n]
    d = d_seq[n]

    # Check all possible powers of 2
    for k in range(1, 70):
        pow2 = 2**k

        # Check 2^k - m[j] = m[n]
        for j in range(2, n):
            mj = m_seq[j]
            if pow2 - mj == m:
                found.append({
                    'n': n, 'm': m, 'd': d,
                    'formula': f"2^{k} - m[{j}] = {pow2} - {mj}",
                    'type': 'sub', 'k': k, 'j': j
                })
                break

        # Check 2^k + m[j] = m[n]
        for j in range(2, n):
            mj = m_seq[j]
            if pow2 + mj == m:
                found.append({
                    'n': n, 'm': m, 'd': d,
                    'formula': f"2^{k} + m[{j}] = {pow2} + {mj}",
                    'type': 'add', 'k': k, 'j': j
                })
                break

print(f"Found {len(found)} power-of-2 relationships:")
print()
print(f"{'n':>3} | {'m':>15} | {'d':>2} | Formula")
print("-"*70)
for f in found:
    print(f"{f['n']:>3} | {f['m']:>15} | {f['d']:>2} | {f['formula']}")

print()
print("="*80)
print("PATTERN ANALYSIS")
print("="*80)
print()

# Check if k relates to n
print("Relationship between n and k (in 2^k ± m[j]):")
for f in found:
    n, k, j = f['n'], f['k'], f['j']
    print(f"  n={n:2d}: k={k:2d}, j={j:2d}, k-n={k-n:3d}, k/n={k/n:.2f}, n-j={n-j:2d}")

print()
print("="*80)
print("CHECKING: Is k always equal to n?")
print("="*80)
print()

# Check m[n] = 2^n ± m[j]
for n in range(2, 71):
    m = m_seq[n]
    pow2_n = 2**n

    for j in range(2, n):
        mj = m_seq[j]
        if pow2_n - mj == m:
            print(f"n={n:2d}: m = 2^{n} - m[{j}] = {pow2_n} - {mj} = {m}")
        if pow2_n + mj == m:
            print(f"n={n:2d}: m = 2^{n} + m[{j}] = {pow2_n} + {mj} = {m}")

print()
print("="*80)
print("CHECKING: m[n] = 2^n - m[n - d[n]] for all n")
print("="*80)
print()

matches = 0
for n in range(4, 71):
    m = m_seq[n]
    d = d_seq[n]
    pow2_n = 2**n

    # Try m[n-d[n]]
    lookup_idx = n - d
    if lookup_idx in m_seq:
        m_lookup = m_seq[lookup_idx]
        predicted = pow2_n - m_lookup
        match = "✓" if predicted == m else "✗"
        if predicted == m:
            matches += 1
        print(f"n={n:2d}: 2^{n} - m[{lookup_idx}] = {pow2_n} - {m_lookup} = {predicted} {'✓ MATCH' if predicted == m else f'✗ (actual: {m})'}")

print()
print(f"Total matches: {matches}")
