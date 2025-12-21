#!/usr/bin/env python3
"""
Explore the n mod 6 pattern. 
n=62 and n=68 have n≡2 (mod 6) - these have the gen Fib pattern
n=71 has n≡5 (mod 6) - might be different

Look at all m-values grouped by n mod 6.
"""
import json

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

print("=" * 70)
print("N MOD 6 PATTERN ANALYSIS")
print("=" * 70)
print()

# Group m-values by n mod 6
groups = {i: [] for i in range(6)}

for n in range(4, 71):
    m = m_seq[n-2]
    d = d_seq[n-2]
    groups[n % 6].append((n, m, d))

# Look at d-value distribution by n mod 6
print("### d-value distribution by n mod 6 ###")
for mod_val in range(6):
    vals = groups[mod_val]
    d_counts = {}
    for n, m, d in vals:
        d_counts[d] = d_counts.get(d, 0) + 1
    print(f"n ≡ {mod_val} (mod 6): {len(vals)} values, d distribution: {d_counts}")

print()

# Focus on n ≡ 2 and n ≡ 5 (mod 6)
print("### n ≡ 2 (mod 6) cases ###")
for n, m, d in groups[2][-5:]:  # Last 5
    print(f"n={n}: m={m}, d={d}")

print()
print("### n ≡ 5 (mod 6) cases ###")
for n, m, d in groups[5][-5:]:  # Last 5
    print(f"n={n}: m={m}, d={d}")

print()

# Check if m[65] has gen Fib pattern (n=65 ≡ 5 mod 6)
print("### Check m[65] for gen Fib pattern ###")
m65 = m_seq[65-2]
print(f"m[65] = {m65}")
print(f"Factorization: 24239 × 57283 × 1437830129")

# Check if any two factors are consecutive gen Fib
def is_gen_fib_pair(a, b):
    """Check if a, b are consecutive in some generalized Fibonacci."""
    # They must satisfy: there exists prev such that prev + a = b (with a > prev)
    # Or: a = prev + something and b = a + something
    # Simplest: just check if b - a < a (so prev = b - a is positive)
    if a >= b:
        return False
    prev = b - a
    if prev <= 0:
        return False
    # Now verify: prev, a, b is a Fibonacci triple (prev + a = b)
    return prev + a == b

factors_65 = [24239, 57283, 1437830129]
print("Checking pairs:")
for i in range(len(factors_65)):
    for j in range(i+1, len(factors_65)):
        a, b = factors_65[i], factors_65[j]
        if is_gen_fib_pair(a, b):
            prev = b - a
            print(f"  {a}, {b}: YES! prev={prev}, sequence: ({prev}, {a}, {b}, ...)")
        else:
            print(f"  {a}, {b}: No")

print()

# Check what G_8 and G_9 would look like for various (a,b) with mod 11 constraint
print("### G_8, G_9 exploration for n=71 ###")
print("If (a,b) ≡ (2,4) mod 11 holds:")
print()

def gen_fib(a, b, n):
    seq = [a, b]
    for _ in range(n):
        seq.append(seq[-1] + seq[-2])
    return seq

# Candidates from mod 11 and linear extrapolation
# a near 57, b near 75.5
candidates = [
    (57, 70),   # a≡2, b≡4
    (57, 81),   # a≡2, b≡4
    (46, 70),   # a≡2, b≡4
    (46, 81),   # a≡2, b≡4
    (68, 70),   # a≡2, b≡4
    (68, 81),   # a≡2, b≡4
]

for a, b in candidates:
    if a > 0 and b > 0:
        seq = gen_fib(a, b, 10)
        G8, G9 = seq[8], seq[9]
        print(f"({a}, {b}): G_8={G8}, G_9={G9}, G_8*G_9={G8*G9}")

print()

# What if mod 11 constraint is different for n ≡ 5 (mod 6)?
print("### Alternative: Check if constraint changes for n mod 6 ###")
print("n=62: n mod 6 = 2, (a,b) = (189, 92) ≡ (2, 4) mod 11")
print("n=68: n mod 6 = 2, (a,b) = (101, 81) ≡ (2, 4) mod 11")
print()
print("Maybe for n ≡ 5 (mod 6), the mod 11 constraint is different?")
print("Let's check n=65 (n mod 6 = 5)...")
print()

# n=65 has d=5, which is different from d=1 or d=2
print("n=65 has d=5, not d=1 or d=2")
print("The generalized Fibonacci pattern may only apply for d ∈ {1, 2}")
print()
print("For n=71: what is d[71]?")
print("We need to find d[71] first!")

print()
print("=" * 70)
print("KEY INSIGHT: The gen Fib pattern may depend on d[n], not just n mod 6")
print("=" * 70)
