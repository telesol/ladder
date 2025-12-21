#!/usr/bin/env python3
"""
Analyze d-value pattern to predict d[71].
d[n] is the value that minimizes m[n].
"""
import json

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

d_seq = data['d_seq']
m_seq = data['m_seq']

print("=" * 70)
print("D-VALUE PATTERN ANALYSIS FOR d[71] PREDICTION")
print("=" * 70)
print()

# d-values for high n
print("### Recent d-values ###")
for n in range(55, 71):
    d = d_seq[n-2]
    m = m_seq[n-2]
    print(f"n={n}: d={d}")

print()

# Look for patterns in d for n≡2, n≡5, n≡8 (mod 9) - the cases with k = 2(n-59)/3 valid
print("### d-values for n where k = 2(n-59)/3 is integer ###")
print("k is integer when (n-59) is divisible by 3, i.e., n ≡ 59 ≡ 2 (mod 3)")
print()
for n in range(35, 71):
    if (n - 59) % 3 == 0:
        d = d_seq[n-2]
        k = 2 * (n - 59) // 3
        print(f"n={n}: k={k}, d={d}")

print()

# n=71: k = 2(71-59)/3 = 2*12/3 = 8
print("### n=71 prediction ###")
print("n=71: k = 2(71-59)/3 = 8")
print()

# Look at d-pattern for recent values where k-formula applies
print("### d-values for n=62, 65, 68 (recent k-formula cases) ###")
for n in [62, 65, 68, 71]:
    if n < 71:
        d = d_seq[n-2]
        k = 2 * (n - 59) // 3
        print(f"n={n}: k={k}, d={d}")
    else:
        k = 2 * (n - 59) // 3
        print(f"n=71: k={k}, d=??? (to find)")

print()

# Pattern analysis
print("### Pattern observation ###")
print("n=62: d=2, k=2")
print("n=65: d=5, k=4")
print("n=68: d=1, k=6")
print()
print("Observation: d cycles or varies")

# Check d-sequence for periodicity
print("### d-sequence recent values ###")
recent_d = [d_seq[n-2] for n in range(50, 71)]
print(f"d[50:70] = {recent_d}")
print()

# Count d values in recent range
from collections import Counter
d_counts = Counter(recent_d)
print(f"d-value counts for n=50-70: {dict(d_counts)}")

# Most common d
most_common_d = d_counts.most_common(1)[0][0]
print(f"Most common d: {most_common_d}")

print()

# Alternative: Look at d mod 3 pattern
print("### d mod 3 pattern ###")
for n in range(62, 71):
    d = d_seq[n-2]
    print(f"n={n}: d={d}, n mod 3 = {n%3}, d mod 3 = {d%3}")

print()

# Check for d = n mod something
print("### Check if d relates to n ###")
for n in range(50, 71):
    d = d_seq[n-2]
    # Check various relationships
    if d == n % 8:
        print(f"n={n}: d={d} = n mod 8")
    elif d == n % 7:
        print(f"n={n}: d={d} = n mod 7")
    elif d == n % 6:
        print(f"n={n}: d={d} = n mod 6")
    elif d == n % 5:
        print(f"n={n}: d={d} = n mod 5")

print()

# What are the possible d values for n=71?
print("### Possible d[71] candidates ###")
print("Based on patterns observed:")
print("  - d ∈ {1, 2, 5} appear most often for high n")
print("  - n=71 ≡ 2 (mod 3), similar to n=62,65,68")
print()

# The key insight: d[n] minimizes m[n]
# We can't know m[71] until we solve the puzzle
# But we can try each candidate d and see which gives valid construction

print("### Approach for d[71] ###")
print("Since d[n] minimizes m[n], we need to:")
print("  1. Try d ∈ {1, 2, 5} as primary candidates")
print("  2. For each d, check if gen Fib pattern gives valid m")
print("  3. The correct d will produce m that solves k[71]")

print()
print("=" * 70)
print("NEXT STEP: Try each candidate d and verify")
print("=" * 70)
