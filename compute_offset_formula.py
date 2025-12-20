#!/usr/bin/env python3
"""
Compute the ACTUAL formula for offset[n]
offset[n] = k[n] - 9*k[n-3]

But also: k[n] = 2*k[n-1] + adj[n]
And: adj[n] = 2^n - m[n]*k[d[n]]

So offset[n] should be expressible in terms of m, d, k values!
"""

import sqlite3
import json

# Load known keys
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
keys = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

# Load m_seq and d_seq
with open('/home/solo/LA/data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']  # Index 0 = n=2
d_seq = data['d_seq']  # Index 0 = n=2

def get_m(n):
    """Get m[n] - note index shift: m_seq[i] corresponds to n=i+2"""
    if n < 2 or n > 70:
        return None
    return m_seq[n-2]

def get_d(n):
    """Get d[n] - note index shift"""
    if n < 2 or n > 70:
        return None
    return d_seq[n-2]

print("=" * 80)
print("COMPUTING OFFSET FORMULA")
print("=" * 80)

print("\nFormula derivation:")
print("k[n] = 2*k[n-1] + adj[n]")
print("k[n-1] = 2*k[n-2] + adj[n-1]")
print("k[n-2] = 2*k[n-3] + adj[n-2]")
print()
print("Substituting:")
print("k[n] = 2*(2*k[n-2] + adj[n-1]) + adj[n]")
print("     = 4*k[n-2] + 2*adj[n-1] + adj[n]")
print("     = 4*(2*k[n-3] + adj[n-2]) + 2*adj[n-1] + adj[n]")
print("     = 8*k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]")
print()
print("Therefore:")
print("offset[n] = k[n] - 9*k[n-3]")
print("          = 8*k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n] - 9*k[n-3]")
print("          = -k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]")

print("\n" + "=" * 80)
print("VERIFYING THE FORMULA")
print("=" * 80)

print("\noffset[n] = -k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n]")
print("-" * 80)

matches = 0
for n in range(34, 71):
    if n not in keys or (n-3) not in keys:
        continue
    
    # Compute adj values
    adj_n = keys[n] - 2*keys[n-1] if (n-1) in keys else None
    adj_n1 = keys[n-1] - 2*keys[n-2] if (n-2) in keys else None
    adj_n2 = keys[n-2] - 2*keys[n-3] if (n-3) in keys else None
    
    if adj_n is None or adj_n1 is None or adj_n2 is None:
        continue
    
    # Actual offset
    actual = keys[n] - 9*keys[n-3]
    
    # Computed offset
    computed = -keys[n-3] + 4*adj_n2 + 2*adj_n1 + adj_n
    
    match = "YES" if actual == computed else "NO"
    if actual == computed:
        matches += 1
    
    if n >= 65:  # Show last few
        print(f"n={n}: actual={actual:,}, computed={computed:,}, match={match}")

print(f"\nTotal matches: {matches}")

print("\n" + "=" * 80)
print("EXPRESSING adj IN TERMS OF m, d, k")
print("=" * 80)

print("\nadj[n] = 2^n - m[n]*k[d[n]]")
print()
print("So offset[n] = -k[n-3] + 4*(2^(n-2) - m[n-2]*k[d[n-2]])")
print("                       + 2*(2^(n-1) - m[n-1]*k[d[n-1]])")
print("                       + (2^n - m[n]*k[d[n]])")
print()
print("             = -k[n-3] + 4*2^(n-2) + 2*2^(n-1) + 2^n")
print("                       - 4*m[n-2]*k[d[n-2]]")
print("                       - 2*m[n-1]*k[d[n-1]]")
print("                       - m[n]*k[d[n]]")
print()
print("             = -k[n-3] + 2^n + 2^n + 2^n  (since 4*2^(n-2) = 2^n, etc)")
print("                       - 4*m[n-2]*k[d[n-2]] - 2*m[n-1]*k[d[n-1]] - m[n]*k[d[n]]")
print()
print("             = -k[n-3] + 3*2^n - (4*m[n-2]*k[d[n-2]] + 2*m[n-1]*k[d[n-1]] + m[n]*k[d[n]])")

print("\n" + "=" * 80)
print("SIMPLIFIED OFFSET FORMULA")
print("=" * 80)

print("\noffset[n] = 3*2^n - k[n-3] - (4*m[n-2]*k[d[n-2]] + 2*m[n-1]*k[d[n-1]] + m[n]*k[d[n]])")

print("\n" + "-" * 80)
print("VERIFICATION:")
print("-" * 80)

for n in range(65, 71):
    if n not in keys or (n-3) not in keys:
        continue
    
    m_n = get_m(n)
    m_n1 = get_m(n-1)
    m_n2 = get_m(n-2)
    d_n = get_d(n)
    d_n1 = get_d(n-1)
    d_n2 = get_d(n-2)
    
    if None in [m_n, m_n1, m_n2, d_n, d_n1, d_n2]:
        continue
    
    k_d_n = keys.get(d_n, 0)
    k_d_n1 = keys.get(d_n1, 0)
    k_d_n2 = keys.get(d_n2, 0)
    
    # Actual offset
    actual = keys[n] - 9*keys[n-3]
    
    # Computed with new formula
    term1 = 3 * (2**n)
    term2 = keys[n-3]
    term3 = 4*m_n2*k_d_n2 + 2*m_n1*k_d_n1 + m_n*k_d_n
    computed = term1 - term2 - term3
    
    match = "MATCH" if actual == computed else "DIFFER"
    print(f"n={n}: m[n]={m_n}, d[n]={d_n}")
    print(f"      actual offset   = {actual:,}")
    print(f"      computed offset = {computed:,}")
    print(f"      {match}")
    print()
