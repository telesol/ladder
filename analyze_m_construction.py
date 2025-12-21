#!/usr/bin/env python3
"""
Analyze how m[n] is constructed from G_k * G_{k+1} * Q.
What is Q for m[62] and m[68]?
"""
import json

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']

print("=" * 70)
print("M-VALUE CONSTRUCTION FROM GENERALIZED FIBONACCI")
print("=" * 70)
print()

# Known data
cases = [
    {
        'n': 62,
        'm': 1184962853718958602,
        'a': 189, 'b': 92,
        'k': 2,
        'factors': [2, 3, 281, 373, 2843, 10487, 63199]
    },
    {
        'n': 68,
        'm': 340563526170809298635,
        'a': 101, 'b': 81,
        'k': 6,
        'factors': [5, 1153, 1861, 31743327447619]
    },
]

def gen_fib(a, b, n):
    seq = [a, b]
    for _ in range(n):
        seq.append(seq[-1] + seq[-2])
    return seq

for case in cases:
    n = case['n']
    m = case['m']
    a, b = case['a'], case['b']
    k = case['k']
    factors = case['factors']
    
    seq = gen_fib(a, b, 10)
    Gk = seq[k]
    Gk1 = seq[k+1]
    
    print(f"### n={n} ###")
    print(f"m[{n}] = {m}")
    print(f"(a, b) = ({a}, {b})")
    print(f"G_{k} = {Gk}, G_{k+1} = {Gk1}")
    print(f"G_{k} * G_{k+1} = {Gk * Gk1}")
    print(f"Q = m / (G_k * G_{k+1}) = {m // (Gk * Gk1)}")
    print(f"Factors: {factors}")
    print()
    
    # Remove Gk and Gk1 from factors to get remaining factors
    remaining = []
    used_Gk = False
    used_Gk1 = False
    for f in factors:
        if f == Gk and not used_Gk:
            used_Gk = True
        elif f == Gk1 and not used_Gk1:
            used_Gk1 = True
        else:
            remaining.append(f)
    
    print(f"Remaining factors after removing G_k, G_{k+1}: {remaining}")
    Q = 1
    for f in remaining:
        Q *= f
    print(f"Product of remaining = Q = {Q}")
    print()
    
    # Check if Q has any pattern
    # Q might relate to n, a, b, or k
    print(f"Q / n = {Q / n:.4f}")
    print(f"Q / (a*b) = {Q / (a*b):.4f}")
    print(f"Q / 2^n = {Q / (2**n):.2e}")
    print()

# Compare Q values
print("### Q VALUE COMPARISON ###")
Q62 = 2 * 3 * 2843 * 10487 * 63199  # remaining after removing 281, 373
Q68 = 5 * 31743327447619  # remaining after removing 1153, 1861
print(f"Q[62] = {Q62}")
print(f"Q[68] = {Q68}")
print(f"Q[68] / Q[62] = {Q68 / Q62:.6f}")
print()

# Check if Q relates to 2^n
print("### Q vs 2^n relationship ###")
for n, Q in [(62, Q62), (68, Q68)]:
    ratio = Q / (2**n)
    print(f"n={n}: Q = {Q}, 2^n = {2**n}, Q/2^n = {ratio:.10f}")
    print(f"       log2(Q) = {Q.bit_length()}, n = {n}")

print()

# For n=71, estimate Q
print("### Q PREDICTION FOR n=71 ###")
# Linear extrapolation of log(Q)?
import math
log_Q62 = math.log(Q62)
log_Q68 = math.log(Q68)
slope = (log_Q68 - log_Q62) / (68 - 62)
log_Q71 = log_Q68 + slope * (71 - 68)
Q71_pred = int(math.exp(log_Q71))
print(f"log(Q[62]) = {log_Q62:.4f}")
print(f"log(Q[68]) = {log_Q68:.4f}")
print(f"Slope = {slope:.4f}")
print(f"log(Q[71]) predicted = {log_Q71:.4f}")
print(f"Q[71] predicted = {Q71_pred}")
print()

# What G_8 * G_9 would be for candidate pairs
print("### G_8 * G_9 FOR CANDIDATE PAIRS ###")
candidates = [(57, 70), (57, 81), (46, 70), (46, 81), (68, 70), (68, 81)]
for a, b in candidates:
    seq = gen_fib(a, b, 10)
    G8, G9 = seq[8], seq[9]
    m71_pred = G8 * G9 * Q71_pred
    print(f"({a}, {b}): G_8={G8}, G_9={G9}, m[71] ≈ {m71_pred}")

print()
print("=" * 70)
