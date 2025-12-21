#!/usr/bin/env python3
"""
Check what m[n] actually equals given known k, d values
"""
import sqlite3
import json

# Load known k-values
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
K = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

# Load m_seq and d_seq
with open('/home/solo/LA/data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']
d_seq = data['d_seq']

print("=" * 80)
print("CHECKING: m[n] = (2^n - adj[n]) / k[d[n]]")
print("=" * 80)

for n in range(2, 15):
    m_stored = m_seq[n-2]
    d_stored = d_seq[n-2]
    k_n = K[n]
    k_prev = K.get(n-1, 0)
    k_d = K.get(d_stored, 1)
    
    adj_n = k_n - 2*k_prev
    power_2n = 2**n
    
    # Verify: m[n] = (2^n - adj[n]) / k[d[n]]
    m_computed = (power_2n - adj_n) / k_d
    
    # Also check: 2^n / k[d]
    ratio = power_2n / k_d
    
    print(f"n={n:2d}: m={m_stored:6d}, d={d_stored}, k[d]={k_d:5d}")
    print(f"       2^n={power_2n:6d}, adj={adj_n:6d}")
    print(f"       (2^n - adj)/k[d] = {m_computed:.2f}")
    print(f"       2^n / k[d] = {ratio:.2f}")
    print(f"       floor(ratio) = {int(ratio)}, ceil(ratio) = {-(-power_2n//k_d)}")
    print()
