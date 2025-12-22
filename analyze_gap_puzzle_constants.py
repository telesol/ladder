#!/usr/bin/env python3
"""
Analyze gap puzzles (75, 80, 85, 90) for GENERAL constant selector rules
These are CLUES - creator exposed them for a reason!
"""
import sqlite3
import math
import json

# Load all known keys
conn = sqlite3.connect('db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
k = {r[0]: int(r[1], 16) for r in cursor.fetchall()}
conn.close()

# Mathematical constants
CONSTANTS = {
    'pi/4': math.pi/4,
    'ln(2)': math.log(2),
    '1/phi': 2/(1+math.sqrt(5)),
    '1/sqrt(2)': 1/math.sqrt(2),
    'e/pi': math.e/math.pi,
    '2/e': 2/math.e,
    'sqrt(2)-1': math.sqrt(2)-1,
    'pi/e': math.pi/math.e,
    '1/e': 1/math.e,
    'ln(3)/2': math.log(3)/2,
    'sqrt(3)/3': math.sqrt(3)/3,
}

print("=" * 80)
print("GAP PUZZLE ANALYSIS - BRIDGES AS MATHEMATICAL CLUES")
print("=" * 80)

gap_puzzles = [75, 80, 85, 90]

results = []
for n in gap_puzzles:
    ratio = k[n] / (2**n)
    
    # Find best matching constant
    best_match = None
    best_error = float('inf')
    for name, val in CONSTANTS.items():
        error = abs(ratio - val) / val
        if error < best_error:
            best_error = error
            best_match = name
    
    result = {
        'n': n,
        'k': k[n],
        'ratio': ratio,
        'best_const': best_match,
        'const_val': CONSTANTS[best_match],
        'error_pct': best_error * 100,
        'n_mod_5': n % 5,
        'n_mod_10': n % 10,
        'factors': [],
    }
    
    # Factorize n
    temp = n
    for p in [2, 3, 5, 7, 11, 13, 17, 19]:
        while temp % p == 0:
            result['factors'].append(p)
            temp //= p
    
    results.append(result)
    
    print(f"\n{'='*40}")
    print(f"PUZZLE {n}")
    print(f"{'='*40}")
    print(f"  k[{n}] = {k[n]}")
    print(f"  k[{n}]/2^{n} = {ratio:.6f}")
    print(f"  Best constant: {best_match} = {CONSTANTS[best_match]:.6f}")
    print(f"  Error: {best_error*100:.2f}%")
    print(f"  n mod 5 = {n % 5}")
    print(f"  n mod 10 = {n % 10}")
    print(f"  Factorization: {n} = {'×'.join(map(str, result['factors']))}")

print("\n" + "=" * 80)
print("PATTERN ANALYSIS ACROSS ALL GAP PUZZLES")
print("=" * 80)

print("\n| n  | n mod 5 | n mod 10 | ratio   | constant | error  |")
print("|----|---------|-----------|---------|-----------| -------|")
for r in results:
    print(f"| {r['n']} | {r['n_mod_5']}       | {r['n_mod_10']}         | {r['ratio']:.4f}  | {r['best_const']:9} | {r['error_pct']:.2f}% |")

print("\n" + "=" * 80)
print("KEY OBSERVATIONS")
print("=" * 80)

print("""
1. ALL gap puzzles have n mod 5 = 0 (divisible by 5)
2. n mod 10 alternates: 5, 0, 5, 0
3. Constants used:
   - n=75 (mod 10=5): ratio ≈ 0.597
   - n=80 (mod 10=0): ratio ≈ 0.914  
   - n=85 (mod 10=5): ratio ≈ 0.545
   - n=90 (mod 10=0): ratio ≈ 0.701

4. Pattern: n mod 10 = 0 → higher ratio (~0.7-0.9)
            n mod 10 = 5 → lower ratio (~0.5-0.6)
""")

# Now analyze ALL known keys by n mod 5 and n mod 10
print("\n" + "=" * 80)
print("GENERAL PATTERN: ALL KNOWN KEYS BY n mod 10")
print("=" * 80)

for mod_val in range(10):
    subset = [(n, k[n]/2**n) for n in sorted(k.keys()) if n % 10 == mod_val and n >= 10]
    if subset:
        ratios = [r for _, r in subset]
        avg = sum(ratios) / len(ratios)
        print(f"\nn mod 10 = {mod_val}: count={len(subset)}, avg_ratio={avg:.4f}")
        print(f"  Sample ratios: {[f'{r:.3f}' for _, r in subset[:8]]}")

# Save results
with open('/home/solo/LA/gap_puzzle_analysis.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("\n" + "=" * 80)
print("SAVED: gap_puzzle_analysis.json")
print("=" * 80)
