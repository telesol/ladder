#!/usr/bin/env python3
"""
Analyze what m[71] values are valid and how they relate to the pattern.
"""
import json

K = {1: 1, 2: 3, 5: 21, 70: 970436974005023690481}

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']

print("=" * 70)
print("M[71] RANGE ANALYSIS")
print("=" * 70)
print()

# k[71] = 2*k[70] + 2^71 - m[71]*k[d]
# For valid k[71]: 2^70 <= k[71] <= 2^71 - 1

base = 2 * K[70] + 2**71
min_k71 = 2**70
max_k71 = 2**71 - 1

print(f"base = 2*k[70] + 2^71 = {base:.4e}")
print(f"min_k71 = 2^70 = {min_k71:.4e}")
print(f"max_k71 = 2^71-1 = {max_k71:.4e}")
print()

print("### Valid m[71] ranges for each d ###")
for d in [1, 2, 5]:
    kd = K[d]
    m71_min = (base - max_k71) // kd
    m71_max = (base - min_k71) // kd
    print(f"d={d}: m[71] ∈ [{m71_min:.4e}, {m71_max:.4e}]")
    print(f"       bit_length: [{m71_min.bit_length()}, {m71_max.bit_length()}]")
print()

print("### Recent m[n] values for comparison ###")
for n in range(60, 71):
    m = m_seq[n-2]
    d = data['d_seq'][n-2]
    print(f"m[{n}] = {m:.4e} (d={d}), bit_length={m.bit_length()}")
print()

# Key observation
print("### Key Observation ###")
print("m[70] has 68 bits, but for d=1, m[71] needs ~71 bits")
print("m[71] should be ~10x larger than m[70]!")
print()

# Expected m[71] based on growth pattern
m70 = m_seq[70-2]
m69 = m_seq[69-2]
m68 = m_seq[68-2]

print("### m-value growth ###")
print(f"m[68] = {m68:.4e}")
print(f"m[69] = {m69:.4e}")
print(f"m[70] = {m70:.4e}")
print(f"m[69]/m[68] = {m69/m68:.4f}")
print(f"m[70]/m[69] = {m70/m69:.4f}")
print()

# Rough estimate for m[71]
avg_growth = (m70/m68) ** 0.5
m71_est = m70 * (m70/m69)
print(f"Rough estimate for m[71]: {m71_est:.4e}")
print()

# Check if this falls in valid range for each d
print("### Checking if m[71] estimate is valid ###")
for d in [1, 2, 5]:
    kd = K[d]
    m71_min = (base - max_k71) // kd
    m71_max = (base - min_k71) // kd
    
    if m71_min <= m71_est <= m71_max:
        print(f"d={d}: m[71]={m71_est:.4e} is VALID")
        k71 = base - int(m71_est) * kd
        print(f"       k[71] would be ~{k71:.4e}")
    else:
        if m71_est < m71_min:
            print(f"d={d}: m[71]={m71_est:.4e} is TOO SMALL (min={m71_min:.4e})")
        else:
            print(f"d={d}: m[71]={m71_est:.4e} is TOO LARGE (max={m71_max:.4e})")

print()

# The generalized Fibonacci Q values
print("### Generalized Fibonacci Q Analysis ###")
print("From known cases:")
print("Q[62] = 11305495059954")
print("Q[68] = 158716637238095")
print()

Q62 = 11305495059954
Q68 = 158716637238095

# If Q grows exponentially with n
import math
slope = (math.log(Q68) - math.log(Q62)) / (68 - 62)
Q71_exp = Q68 * math.exp(slope * (71 - 68))
print(f"Exponential extrapolation: Q[71] = {Q71_exp:.4e}")
print()

# What G_8 * G_9 * Q would give
def gen_fib(a, b, n):
    seq = [a, b]
    for _ in range(n):
        seq.append(seq[-1] + seq[-2])
    return seq

for a, b in [(57, 70), (57, 81), (68, 70), (68, 81)]:
    seq = gen_fib(a, b, 10)
    G8, G9 = seq[8], seq[9]
    m71_from_genfib = G8 * G9 * Q71_exp
    print(f"({a},{b}): G_8*G_9*Q = {m71_from_genfib:.4e}")

print()
print("### CONCLUSION ###")
print("The generalized Fibonacci formula gives m[71] ~5×10^21")
print("But valid m[71] for d=1 is 1.9-3.1×10^21")
print("This suggests Q extrapolation is WRONG or pattern doesn't apply")
print()
print("ALTERNATIVE: m[71] might follow a simpler pattern")
print("=" * 70)
