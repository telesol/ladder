#!/usr/bin/env python3
"""
Strategy 2: Find the constant selector rule
Strategy 3: Predict d[71]
"""
import json
import sqlite3
import math

# Load data
conn = sqlite3.connect('db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {r[0]: int(r[1], 16) for r in cursor.fetchall()}
conn.close()

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']
d_seq = data['d_seq']

# Mathematical constants
CONSTANTS = {
    'pi/4': math.pi/4,           # 0.7854
    'ln(2)': math.log(2),        # 0.6931
    '1/phi': 2/(1+math.sqrt(5)), # 0.6180
    '1/sqrt(2)': 1/math.sqrt(2), # 0.7071
    'e/pi': math.e/math.pi,      # 0.8653
    'phi-1': (math.sqrt(5)-1)/2, # 0.6180 (same as 1/phi)
    'sqrt(2)-1': math.sqrt(2)-1, # 0.4142
    'pi/e': math.pi/math.e,      # 1.1557
    '2/e': 2/math.e,             # 0.7358
    'ln(pi)': math.log(math.pi)/math.pi, # 0.3647
}

print("=" * 80)
print("CONSTANT SELECTOR ANALYSIS")
print("=" * 80)

# For each n, find the best matching constant
def find_best_constant(n, k_n):
    ratio = k_n / (2**n)
    best_const = None
    best_error = float('inf')
    for name, val in CONSTANTS.items():
        error = abs(ratio - val) / val
        if error < best_error:
            best_error = error
            best_const = name
    return best_const, best_error, ratio

print(f"\n{'n':>3} {'ratio':>12} {'constant':>12} {'error%':>8} {'n%5':>4} {'prime':>6} {'d[n]':>4}")
print("-" * 70)

matches = []
for n in range(2, 71):
    if n in k:
        const, error, ratio = find_best_constant(n, k[n])
        is_prime = all(n % i != 0 for i in range(2, int(n**0.5)+1)) if n > 1 else False
        d_n = d_seq[n-2] if n-2 < len(d_seq) else '?'
        matches.append({
            'n': n, 'ratio': ratio, 'const': const, 'error': error,
            'n_mod_5': n % 5, 'prime': is_prime, 'd': d_n
        })
        if error < 0.05:  # Show good matches
            print(f"{n:>3} {ratio:>12.6f} {const:>12} {error*100:>8.2f} {n%5:>4} {str(is_prime):>6} {d_n:>4}")

print("\n" + "=" * 80)
print("CONSTANT SELECTION RULES BY n mod 5")
print("=" * 80)

for mod_val in range(5):
    subset = [m for m in matches if m['n_mod_5'] == mod_val and m['error'] < 0.05]
    const_counts = {}
    for m in subset:
        const_counts[m['const']] = const_counts.get(m['const'], 0) + 1
    print(f"\nn mod 5 = {mod_val}:")
    for c, cnt in sorted(const_counts.items(), key=lambda x: -x[1]):
        print(f"  {c}: {cnt} times")

print("\n" + "=" * 80)
print("PREDICTING d[71]")
print("=" * 80)

# n=71 properties
print("\n71 properties:")
print(f"  71 mod 5 = {71 % 5}")
print(f"  71 is prime: True")
print(f"  71 = 70 + 1 (after k[70] with d=2)")

# Look at similar cases
print("\nSimilar cases (prime, n mod 5 = 1):")
similar = [(n, d_seq[n-2]) for n in range(2, 71) 
           if n % 5 == 1 and all(n % i != 0 for i in range(2, int(n**0.5)+1))]
for n, d in similar:
    print(f"  n={n}: d={d}")

# Count d values for primes with n mod 5 = 1
d_counts = {}
for n, d in similar:
    d_counts[d] = d_counts.get(d, 0) + 1
print(f"\nPredicted d[71] distribution:")
total = sum(d_counts.values())
for d, cnt in sorted(d_counts.items(), key=lambda x: -x[1]):
    print(f"  d={d}: {cnt}/{total} ({100*cnt/total:.1f}%)")

print("\n" + "=" * 80)
print("IF d[71] = 1, WHAT IS m[71]?")
print("=" * 80)

# If d[71] = 1, then adj[71] = 2^71 - m[71]
# And k[71] = 2*k[70] + adj[71] = 2*k[70] + 2^71 - m[71]
# k[71] must be in [2^70, 2^71-1]

k70 = k[70]
print(f"\nk[70] = {k70}")
print(f"2^71 = {2**71}")
print(f"2*k[70] = {2*k70}")

# k[71] = 2*k[70] + 2^71 - m[71]
# 2^70 <= k[71] <= 2^71 - 1
# 2^70 <= 2*k[70] + 2^71 - m[71] <= 2^71 - 1
# 2^70 - 2*k[70] - 2^71 <= -m[71] <= 2^71 - 1 - 2*k[70] - 2^71
# m[71] >= 2*k[70] + 2^71 - (2^71 - 1) = 2*k[70] + 1
# m[71] <= 2*k[70] + 2^71 - 2^70

m71_min = 2*k70 + 1
m71_max = 2*k70 + 2**71 - 2**70
print(f"\nm[71] constraints (if d=1):")
print(f"  min: {m71_min:,}")
print(f"  max: {m71_max:,}")

# What ratio would this give?
ratio_min = (2**71 - m71_max) / 2**71 + 2*k70 / 2**71
ratio_max = (2**71 - m71_min) / 2**71 + 2*k70 / 2**71

print(f"\nCorresponding k[71]/2^71 range:")
print(f"  If m[71] = {m71_min:,}: k[71]/2^71 = {(2*k70 + 2**71 - m71_min)/(2**71):.6f}")
print(f"  If m[71] = {m71_max:,}: k[71]/2^71 = {(2*k70 + 2**71 - m71_max)/(2**71):.6f}")

# Check which constant would match
print(f"\nPossible constants for n=71 (prime, n mod 5 = 1):")
# Looking at pattern: primes with n mod 5 = 1 often use 1/phi
print(f"  1/phi = {1/(1+math.sqrt(5))*2:.6f}")
print(f"  pi/4 = {math.pi/4:.6f}")

# If k[71]/2^71 = 1/phi:
target_ratio = 2/(1+math.sqrt(5))  # 1/phi
k71_if_phi = int(target_ratio * 2**71)
m71_if_phi = 2*k70 + 2**71 - k71_if_phi
print(f"\nIf C(71) = 1/phi:")
print(f"  k[71] ≈ {k71_if_phi:,}")
print(f"  m[71] = {m71_if_phi:,}")
print(f"  m[71]/2^71 = {m71_if_phi/2**71:.6f}")
