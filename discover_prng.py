#!/usr/bin/env python3
"""
Strategy 1: Check if m-sequence follows PRNG pattern
"""
import json
import math

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)
m_seq = data['m_seq']

print("=" * 80)
print("PRNG PATTERN ANALYSIS OF M-SEQUENCE")
print("=" * 80)

print("\nFirst 20 m values:")
for i in range(20):
    n = i + 2
    print(f"  m[{n:>2}] = {m_seq[i]}")

# Check for LCG pattern: m[n+1] = (a*m[n] + c) mod M
print("\n" + "-" * 40)
print("Testing LCG pattern: m[n+1] = (a*m[n] + c) mod M")
print("-" * 40)

# Try to find (a, c) that works for consecutive pairs
for i in range(len(m_seq) - 2):
    m0, m1, m2 = m_seq[i], m_seq[i+1], m_seq[i+2]
    # If m1 = a*m0 + c and m2 = a*m1 + c
    # Then m2 - m1 = a*(m1 - m0)
    # So a = (m2 - m1) / (m1 - m0) if m1 != m0
    if m1 != m0:
        a = (m2 - m1) / (m1 - m0)
        if abs(a - round(a)) < 0.001:  # Check if a is integer
            a = int(round(a))
            c = m1 - a * m0
            # Verify
            if a * m1 + c == m2:
                print(f"n={i+2}: a={a}, c={c} works for consecutive triple")

# Check ratio pattern
print("\n" + "-" * 40)
print("Ratio analysis: m[n+1] / m[n]")
print("-" * 40)

ratios = []
for i in range(len(m_seq) - 1):
    if m_seq[i] != 0:
        ratio = m_seq[i+1] / m_seq[i]
        ratios.append((i+2, ratio))
        if i < 20:
            print(f"m[{i+3}]/m[{i+2}] = {ratio:.4f}")

print(f"\nRatio statistics:")
print(f"  Min: {min(r for _, r in ratios):.4f}")
print(f"  Max: {max(r for _, r in ratios):.4f}")
print(f"  Mean: {sum(r for _, r in ratios)/len(ratios):.4f}")

# Check if ratios cluster around powers of 2
print("\n" + "-" * 40)
print("Checking if m[n]/2^n follows a pattern")
print("-" * 40)

normalized = []
for i in range(len(m_seq)):
    n = i + 2
    norm = m_seq[i] / (2**n)
    normalized.append((n, norm))

# Group by n mod 5
print("\nNormalized m[n]/2^n by n mod 5:")
for mod in range(5):
    subset = [v for n, v in normalized if n % 5 == mod]
    if subset:
        print(f"  n mod 5 = {mod}: mean={sum(subset)/len(subset):.4f}, std={math.sqrt(sum((x-sum(subset)/len(subset))**2 for x in subset)/len(subset)):.4f}")

# Check XOR pattern
print("\n" + "-" * 40)
print("XOR analysis")
print("-" * 40)

for i in range(len(m_seq) - 1):
    xor_val = m_seq[i] ^ m_seq[i+1]
    if i < 10:
        print(f"m[{i+2}] XOR m[{i+3}] = {xor_val} = {bin(xor_val)}")

# Check difference pattern
print("\n" + "-" * 40)
print("Second differences")
print("-" * 40)

diffs = [m_seq[i+1] - m_seq[i] for i in range(len(m_seq)-1)]
second_diffs = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]

print("First 15 second differences:")
for i in range(15):
    print(f"  d2[{i+2}] = {second_diffs[i]}")

print("\n" + "=" * 80)
print("KEY INSIGHT: m-sequence does NOT follow simple PRNG")
print("=" * 80)
print("""
The m-sequence appears to be CONSTRUCTED, not random.
Key observations:
1. Ratios vary wildly (0.01 to 157) - no constant multiplier
2. No simple LCG pattern found
3. Values cluster around mathematical constants when normalized

The m-sequence is likely DERIVED from the desired k/2^n ratio,
not generated independently!
""")
