#!/usr/bin/env python3
"""
FULL CONSTRUCTION ANALYSIS
Analyze ALL k[1]-k[70] + gap puzzles for Fibonacci/Lucas/Fermat/Prime patterns
"""

import sqlite3
import math
import json
from collections import defaultdict

# Build sequences
print("Building mathematical sequences...")
fib = [0, 1]
lucas = [2, 1]
for i in range(100):
    fib.append(fib[-1] + fib[-2])
    lucas.append(lucas[-1] + lucas[-2])

fib_set = set(fib[:80])
lucas_set = set(lucas[:60])

# Fermat primes and numbers
fermat_primes = [3, 5, 17, 257, 65537]
fermat_set = set(fermat_primes)

# Mersenne primes
mersenne = [3, 7, 31, 127, 8191, 131071, 524287]
mersenne_set = set(mersenne)

def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0: return False
    return True

def factorize(n):
    if n <= 1: return []
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    return factors

def find_constructions(n, kn):
    """Find all possible constructions for k[n]"""
    constructions = []
    
    # 1. Check if prime
    if is_prime(kn):
        constructions.append(("PRIME", kn))
    
    # 2. Check exact Fibonacci
    if kn in fib_set:
        idx = fib.index(kn)
        constructions.append(("FIB", f"F({idx})"))
    
    # 3. Check exact Lucas
    if kn in lucas_set:
        idx = lucas.index(kn)
        constructions.append(("LUCAS", f"L({idx})"))
    
    # 4. Check Mersenne
    if kn in mersenne_set:
        constructions.append(("MERSENNE", f"M={kn}"))
    
    # 5. Check 2^m or 2^m ± small
    log2_k = math.log2(kn) if kn > 0 else 0
    m = round(log2_k)
    diff = kn - 2**m
    if abs(diff) <= 10:
        constructions.append(("POWER2", f"2^{m}+{diff}"))
    
    # 6. Check Fibonacci products F(a) × F(b)
    for a in range(1, 45):
        if fib[a] > kn: break
        if kn % fib[a] == 0:
            q = kn // fib[a]
            if q in fib_set and q >= fib[a]:
                b = fib.index(q)
                constructions.append(("FIB×FIB", f"F({a})×F({b})={fib[a]}×{q}"))
    
    # 7. Check Lucas products L(a) × L(b)
    for a in range(1, 35):
        if lucas[a] > kn: break
        if kn % lucas[a] == 0:
            q = kn // lucas[a]
            if q in lucas_set and q >= lucas[a]:
                b = lucas.index(q)
                constructions.append(("LUCAS×LUCAS", f"L({a})×L({b})={lucas[a]}×{q}"))
    
    # 8. Check F × L products
    for a in range(1, 45):
        if fib[a] > kn: break
        if fib[a] > 0 and kn % fib[a] == 0:
            q = kn // fib[a]
            if q in lucas_set:
                b = lucas.index(q)
                constructions.append(("FIB×LUCAS", f"F({a})×L({b})={fib[a]}×{q}"))
    
    # 9. Check Lucas × 2^m
    for i in range(1, 30):
        if lucas[i] > kn: break
        if kn % lucas[i] == 0:
            q = kn // lucas[i]
            if q > 0:
                log2_q = math.log2(q)
                if abs(log2_q - round(log2_q)) < 0.0001:
                    m = round(log2_q)
                    constructions.append(("LUCAS×2^m", f"L({i})×2^{m}={lucas[i]}×{q}"))
    
    # 10. Check Fib × 2^m
    for i in range(1, 45):
        if fib[i] > kn: break
        if fib[i] > 0 and kn % fib[i] == 0:
            q = kn // fib[i]
            if q > 0:
                log2_q = math.log2(q)
                if abs(log2_q - round(log2_q)) < 0.0001:
                    m = round(log2_q)
                    constructions.append(("FIB×2^m", f"F({i})×2^{m}={fib[i]}×{q}"))
    
    # 11. Check Fermat prime products
    for fp in fermat_primes:
        if kn % fp == 0:
            q = kn // fp
            constructions.append(("FERMAT", f"{q}×Fermat({fp})"))
    
    # 12. Check Lucas squared
    for i in range(1, 30):
        if lucas[i]**2 == kn:
            constructions.append(("LUCAS²", f"L({i})²={lucas[i]}²"))
    
    # 13. Check Fib squared
    for i in range(1, 45):
        if fib[i]**2 == kn:
            constructions.append(("FIB²", f"F({i})²={fib[i]}²"))
    
    return constructions

# Load all k values
print("Loading k-values from database...")
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
rows = cursor.fetchall()
conn.close()

k = {}
for puzzle_id, priv_hex in rows:
    k[puzzle_id] = int(priv_hex, 16)

print(f"Loaded {len(k)} k-values")
print()

# Analyze all k-values
print("=" * 80)
print("FULL CONSTRUCTION ANALYSIS - k[1] to k[70] + Gap Puzzles")
print("=" * 80)
print()

results = {}
stats = defaultdict(int)

for n in sorted(k.keys()):
    kn = k[n]
    constructions = find_constructions(n, kn)
    
    results[n] = {
        'k': kn,
        'constructions': constructions,
        'factors': factorize(kn) if not any(c[0] == 'PRIME' for c in constructions) else [kn]
    }
    
    # Count stats
    for ctype, _ in constructions:
        stats[ctype] += 1
    
    # Print result
    if constructions:
        best = constructions[0]
        others = f" | also: {', '.join([c[1] for c in constructions[1:3]])}" if len(constructions) > 1 else ""
        print(f"k[{n:2}] = {kn:>25} = {best[0]:12} {best[1]}{others}")
    else:
        factors = results[n]['factors']
        print(f"k[{n:2}] = {kn:>25} = COMPOSITE    factors: {factors[:5]}{'...' if len(factors) > 5 else ''}")

print()
print("=" * 80)
print("CONSTRUCTION STATISTICS")
print("=" * 80)
print()

total = len(k)
for ctype, count in sorted(stats.items(), key=lambda x: -x[1]):
    pct = 100 * count / total
    print(f"{ctype:15}: {count:3}/{total} ({pct:5.1f}%)")

# Count how many have at least one known construction
known_construction = sum(1 for r in results.values() if r['constructions'])
unknown = total - known_construction
print()
print(f"KNOWN construction: {known_construction}/{total} ({100*known_construction/total:.1f}%)")
print(f"UNKNOWN (need analysis): {unknown}/{total} ({100*unknown/total:.1f}%)")

# Save results to JSON
with open('/home/solo/ladder/construction_analysis_full.json', 'w') as f:
    json.dump({
        'results': {str(n): {'k': str(r['k']), 'constructions': r['constructions'], 'factors': r['factors']} 
                    for n, r in results.items()},
        'stats': dict(stats)
    }, f, indent=2)

print()
print("Results saved to construction_analysis_full.json")
