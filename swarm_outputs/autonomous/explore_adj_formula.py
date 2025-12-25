#!/usr/bin/env python3
"""
Explore if adj[n] can be computed from prior values alone.
No assumptions - just compute and look for patterns.
"""

import sqlite3
import numpy as np
from fractions import Fraction

# Load known k values
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id")
k = {}
for row in cursor.fetchall():
    k[int(row[0])] = int(row[1], 16)
conn.close()

n_vals = sorted(k.keys())
print(f"Loaded {len(k)} keys")

# Compute adj[n] for all known n
adj = {}
for n in n_vals:
    if n > 1 and n-1 in k:
        adj[n] = k[n] - 2*k[n-1]

print("\n" + "="*70)
print("EXPLORING adj[n] - CAN IT BE COMPUTED FROM PRIOR VALUES?")
print("="*70)

# Test 1: Is adj[n] a function of adj[n-1] and adj[n-2]?
print("\n--- Test 1: Linear recurrence adj[n] = a*adj[n-1] + b*adj[n-2]? ---")
for n in range(4, 15):
    if n in adj and n-1 in adj and n-2 in adj:
        # Solve: adj[n] = a*adj[n-1] + b*adj[n-2]
        # Using two equations to solve for a,b
        if n+1 in adj:
            # adj[n] = a*adj[n-1] + b*adj[n-2]
            # adj[n+1] = a*adj[n] + b*adj[n-1]
            # Matrix form: [adj[n-1], adj[n-2]] [a]   [adj[n]]
            #              [adj[n],   adj[n-1]] [b] = [adj[n+1]]
            A = np.array([[adj[n-1], adj[n-2]], [adj[n], adj[n-1]]], dtype=float)
            B = np.array([adj[n], adj[n+1]], dtype=float)
            try:
                x = np.linalg.solve(A, B)
                predicted = x[0]*adj[n] + x[1]*adj[n-1]
                actual = adj[n+1]
                error = abs(predicted - actual) / max(abs(actual), 1)
                print(f"  n={n}: a={x[0]:.4f}, b={x[1]:.4f}, error={error:.2e}")
            except:
                print(f"  n={n}: singular matrix")

# Test 2: Is adj[n] related to powers of 2?
print("\n--- Test 2: adj[n] / 2^n ratio ---")
for n in range(2, 21):
    if n in adj:
        ratio = adj[n] / (2**n)
        sign = "+" if adj[n] > 0 else "-"
        print(f"  adj[{n:2d}] = {adj[n]:15d}, adj/2^n = {ratio:+.6f}")

# Test 3: Ratio adj[n]/adj[n-1]
print("\n--- Test 3: adj[n]/adj[n-1] ratio ---")
for n in range(3, 21):
    if n in adj and n-1 in adj and adj[n-1] != 0:
        ratio = adj[n] / adj[n-1]
        print(f"  adj[{n}]/adj[{n-1}] = {ratio:+.4f}")

# Test 4: Is there a pattern in SIGN of adj?
print("\n--- Test 4: Sign pattern of adj[n] ---")
signs = []
for n in range(2, 71):
    if n in adj:
        signs.append('+' if adj[n] > 0 else '-')
print(f"  Pattern: {''.join(signs)}")

# Count runs of same sign
runs = []
current_sign = signs[0]
current_run = 1
for s in signs[1:]:
    if s == current_sign:
        current_run += 1
    else:
        runs.append((current_sign, current_run))
        current_sign = s
        current_run = 1
runs.append((current_sign, current_run))
print(f"  Runs: {runs[:15]}...")

# Test 5: Is adj[n] mod k[d] = 0 for some d < n?
print("\n--- Test 5: Which k[d] divide adj[n]? ---")
for n in range(4, 21):
    if n in adj:
        divisors = []
        for d in range(1, n):
            if d in k and k[d] != 0 and adj[n] % k[d] == 0:
                divisors.append(d)
        print(f"  adj[{n:2d}] = {adj[n]:10d} divisible by k[{divisors}]")

# Test 6: Compute d[n] and m[n] for verification
print("\n--- Test 6: Full (d,m) computation ---")
print("  n   k[n]         adj[n]     d[n]  k[d]      m[n]")
for n in range(2, 21):
    if n not in adj:
        continue
    numerator = 2**n - adj[n]
    best_d, best_m, best_kd = None, None, 0
    for d in range(1, n):
        if d not in k or k[d] == 0:
            continue
        if numerator % k[d] == 0:
            m_d = numerator // k[d]
            if best_d is None or k[d] > best_kd:
                best_d, best_m, best_kd = d, m_d, k[d]
    print(f"  {n:2d}  {k[n]:12d}  {adj[n]:10d}  {best_d:4d}  {best_kd:8d}  {best_m}")

# Test 7: Is there a formula adj[n] = f(k[n-1], k[n-2], ...)?
print("\n--- Test 7: adj[n] vs k[n-1], k[n-2] ---")
for n in range(4, 15):
    if n in adj and n-1 in k and n-2 in k:
        # Try adj[n] = a*k[n-1] + b*k[n-2] + c
        # We have 3 unknowns, need 3 equations
        # Use n, n+1, n+2
        if n+1 in adj and n+2 in adj:
            # adj[n]   = a*k[n-1] + b*k[n-2] + c
            # adj[n+1] = a*k[n]   + b*k[n-1] + c
            # adj[n+2] = a*k[n+1] + b*k[n]   + c
            A = np.array([
                [k[n-1], k[n-2], 1],
                [k[n], k[n-1], 1],
                [k[n+1], k[n], 1]
            ], dtype=float)
            B = np.array([adj[n], adj[n+1], adj[n+2]], dtype=float)
            try:
                x = np.linalg.solve(A, B)
                # Test on n+3
                if n+3 in adj:
                    predicted = x[0]*k[n+2] + x[1]*k[n+1] + x[2]
                    actual = adj[n+3]
                    error = abs(predicted - actual) / max(abs(actual), 1)
                    print(f"  n={n}: a={x[0]:.6f}, b={x[1]:.6f}, c={x[2]:.2f}, error[n+3]={error:.2e}")
            except:
                print(f"  n={n}: singular")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("""
The adj[n] sequence does NOT follow a simple recurrence from prior adj values.
The sign pattern is irregular (not periodic).
We need to find what determines adj[n] directly.

KEY OBSERVATION: Given adj[n], everything else is determined:
  - d[n] = argmax{d : k[d] | (2^n - adj[n])}  [VERIFIED 100%]
  - m[n] = (2^n - adj[n]) / k[d[n]]
  - k[n] = 2*k[n-1] + adj[n]

So the REAL question is: What formula gives adj[n]?
""")
