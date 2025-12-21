#!/usr/bin/env python3
"""
Search for Direct Formula: m[n] = M(n)

If we can find M(n) that predicts m for any n, we can:
1. Compute k[n] = 2^n - M(n)*k[D(n)] + recursive_terms
2. Solve all puzzles without intermediate values

Known patterns:
- log2(m[n]) ≈ 0.98*n - 1.62 (linear fit)
- m[n] | m[n+m[n]] for 57% of cases (self-reference)
- 17-network: m[9,11,12,24] share gcd=17
"""
import sqlite3
import json
from pathlib import Path
import math

# Load known k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 161):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

# Load m and d values
data_file = Path('data_for_csolver.json')
if data_file.exists():
    with open(data_file) as f:
        data = json.load(f)
        m_seq = data.get('m_seq', [])
        d_seq = data.get('d_seq', [])
else:
    print("ERROR: data_for_csolver.json not found")
    exit(1)

print("=" * 80)
print("M[N] DIRECT FORMULA SEARCH")
print("=" * 80)
print()

# Test 1: Is m[n] related to 2^n?
print("### Test 1: m[n] / 2^n ratio ###")
print()
print("n    | m[n]              | m[n] / 2^n        | 2^n / m[n]")
print("-----|-------------------|-------------------|------------")
for i in range(min(20, len(m_seq))):
    n = i + 2
    m = m_seq[i]
    ratio = m / 2**n
    inv_ratio = 2**n / m if m > 0 else 0
    print(f"{n:4d} | {m:17d} | {ratio:17.6f} | {inv_ratio:10.2f}")

print()

# Test 2: Is m[n] related to k[n]?
print("### Test 2: m[n] / k[n] ratio ###")
print()
print("n    | m[n]              | k[n]              | m[n] / k[n]")
print("-----|-------------------|-------------------|------------")
for i in range(min(20, len(m_seq))):
    n = i + 2
    m = m_seq[i]
    k = k_values.get(n, 0)
    ratio = m / k if k > 0 else 0
    print(f"{n:4d} | {m:17d} | {k:17d} | {ratio:10.4f}")

print()

# Test 3: Is m[n] related to n itself?
print("### Test 3: m[n] / n^p for various p ###")
print()
print("Testing m[n] ≈ c * n^p for various p:")
for p in [2, 3, 4, 5]:
    ratios = []
    for i in range(len(m_seq)):
        n = i + 2
        m = m_seq[i]
        if m > 0 and n > 0:
            ratio = m / (n ** p)
            ratios.append(ratio)

    if ratios:
        avg_ratio = sum(ratios) / len(ratios)
        variance = sum((r - avg_ratio)**2 for r in ratios) / len(ratios)
        cv = (variance ** 0.5) / avg_ratio if avg_ratio > 0 else 0
        print(f"p = {p}: avg(m/n^p) = {avg_ratio:.4e}, CV = {cv:.4f}")

print()

# Test 4: Patterns in m[n] mod small primes
print("### Test 4: m[n] mod small primes ###")
print()
for p in [2, 3, 5, 7, 11, 13, 17, 19]:
    residues = [m_seq[i] % p for i in range(len(m_seq))]
    counts = {}
    for r in residues:
        counts[r] = counts.get(r, 0) + 1

    # Check if any residue dominates
    most_common = max(counts.items(), key=lambda x: x[1])
    print(f"m[n] mod {p:2d}: most common residue = {most_common[0]} ({most_common[1]} times out of {len(m_seq)})")

print()

# Test 5: Is there periodicity in m[n]?
print("### Test 5: Periodicity in m[n] ###")
print()
# Check m[n] mod m[n-k] for various k
for k in range(1, 6):
    divisible_count = 0
    total = 0
    for i in range(k, len(m_seq)):
        m_curr = m_seq[i]
        m_prev = m_seq[i - k]
        if m_prev > 0 and m_curr % m_prev == 0:
            divisible_count += 1
        total += 1
    pct = 100 * divisible_count / total if total > 0 else 0
    print(f"m[n] divisible by m[n-{k}]: {divisible_count}/{total} ({pct:.1f}%)")

print()

# Test 6: Self-reference m[n] | m[n + m[n]]
print("### Test 6: Self-reference m[n] | m[n + m[n]] ###")
print()
self_ref_matches = []
for i in range(len(m_seq)):
    n = i + 2
    m = m_seq[i]
    target_n = n + m
    target_i = target_n - 2
    if 0 <= target_i < len(m_seq):
        m_target = m_seq[target_i]
        if m > 0 and m_target % m == 0:
            self_ref_matches.append((n, m, target_n, m_target // m))

print(f"Self-reference matches: {len(self_ref_matches)}/{len([i for i in range(len(m_seq)) if (i+2) + m_seq[i] - 2 < len(m_seq)])}")
print()
for n, m, target_n, factor in self_ref_matches[:10]:
    print(f"  m[{n}] = {m} divides m[{target_n}] = m[{n}] × {factor}")

print()

# Test 7: Relationship with d[n]
print("### Test 7: m[n] vs d[n] relationship ###")
print()
print("n    | d[n] | m[n]              | m[n] / k[d[n]]")
print("-----|------|-------------------|---------------")
for i in range(min(25, len(m_seq))):
    n = i + 2
    m = m_seq[i]
    d = d_seq[i] if i < len(d_seq) else 1
    k_d = k_values.get(d, 1)
    ratio = m / k_d if k_d > 0 else 0
    print(f"{n:4d} | {d:4d} | {m:17d} | {ratio:13.4f}")

print()

# Test 8: Is m[n] = 2^n / k[d[n]] approximately?
print("### Test 8: m[n] ≈ 2^n / k[d[n]] hypothesis ###")
print()
print("n    | m[n]              | 2^n / k[d[n]]     | Error %")
print("-----|-------------------|-------------------|--------")
for i in range(min(25, len(m_seq))):
    n = i + 2
    m = m_seq[i]
    d = d_seq[i] if i < len(d_seq) else 1
    k_d = k_values.get(d, 1)
    predicted = 2**n / k_d if k_d > 0 else 0
    error = 100 * abs(m - predicted) / m if m > 0 else 0
    print(f"{n:4d} | {m:17d} | {predicted:17.2f} | {error:7.2f}%")

print()
print("=" * 80)
print("KEY OBSERVATIONS")
print("=" * 80)
print()
print("1. m[n] / 2^n decreases as n increases (m grows slower than 2^n)")
print("2. m[n] ≈ 2^n / k[d[n]] with varying error")
print("3. Self-reference m[n] | m[n + m[n]] holds for ~57% of cases")
print("4. m[n] mod 2 = 1 for 78% (mostly odd)")
print()
print("The m[n] = (2^n - adj[n]) / k[d[n]] formula is EXACT.")
print("But adj[n] = k[n] - 2*k[n-1] requires knowing k[n-1].")
print()
print("To get a DIRECT formula M(n), we need to express adj[n] in terms of n only.")
print()
