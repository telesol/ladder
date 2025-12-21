#!/usr/bin/env python3
"""
Deep analysis of m-sequence for patterns that could help derive m[71].
"""
import sqlite3
import math

# Load known k values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 91):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

# Compute adj, d, and m values
adj_values = {}
d_values = {}
m_values = {}

for n in range(2, 71):
    if n in k_values and (n-1) in k_values:
        adj_n = k_values[n] - 2*k_values[n-1]
        adj_values[n] = adj_n
        N_n = 2**n - adj_n
        best_d = None
        best_m = None
        for try_d in range(1, n):
            if try_d in k_values:
                k_d = k_values[try_d]
                if N_n % k_d == 0:
                    m_try = N_n // k_d
                    if best_m is None or m_try < best_m:
                        best_m = m_try
                        best_d = try_d
        if best_m is not None:
            m_values[n] = best_m
            d_values[n] = best_d

print("=" * 70)
print("M-SEQUENCE ANALYSIS")
print("=" * 70)
print()

print("### M-values for n=55-70 ###")
for n in range(55, 71):
    if n in m_values:
        growth = ""
        if (n-1) in m_values and m_values[n-1] != 0:
            g = m_values[n] / m_values[n-1]
            growth = f"growth={g:.4f}"
        print(f"m[{n}] = {m_values[n]:>20} (d={d_values[n]}) {growth}")

print()
print("### D-value Distribution (n=50-70) ###")
d_counts = {}
for n in range(50, 71):
    if n in d_values:
        d = d_values[n]
        d_counts[d] = d_counts.get(d, 0) + 1
for d, count in sorted(d_counts.items()):
    print(f"  d={d}: {count} times")

print()
print("### m[n] vs 2^n/k[d[n]] ###")
for n in range(60, 71):
    if n in m_values and n in d_values:
        k_d = k_values[d_values[n]]
        approx = 2**n / k_d
        actual = m_values[n]
        ratio = actual / approx
        print(f"n={n}: ratio = {ratio:.6f}")

print()
print("### Predicting m[71] range ###")
k70 = k_values[70]
min_k71 = 2**70
max_k71 = 2**71 - 1
print(f"k[70] = {k70}")
print()
print("If d[71] = 1:")
min_adj71 = min_k71 - 2*k70
max_adj71 = max_k71 - 2*k70
min_m71_d1 = 2**71 - max_adj71
max_m71_d1 = 2**71 - min_adj71
print(f"  adj[71] range: [{min_adj71:.4e}, {max_adj71:.4e}]")
print(f"  m[71] range: [{min_m71_d1:.4e}, {max_m71_d1:.4e}]")

print()
print("If d[71] = 2 (must divide evenly by 3):")
min_m71_d2 = (2**71 - max_adj71) // 3
max_m71_d2 = (2**71 - min_adj71) // 3
print(f"  m[71] range: [{min_m71_d2:.4e}, {max_m71_d2:.4e}]")
