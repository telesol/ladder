#!/usr/bin/env python3
"""
Analyze the d-sequence to find the selection algorithm.
We know d[n] minimizes m[n] - but is there a pattern to predict d without computing all candidates?
"""

import json

with open('/home/solo/LA/data_for_csolver.json', 'r') as f:
    data = json.load(f)
d_seq = data['d_seq']  # Index 0 = n=2
m_seq = data['m_seq']

print("=" * 80)
print("d-SEQUENCE ANALYSIS")
print("=" * 80)

print("\nFull d-sequence (n=2 to n=70):")
for i in range(0, len(d_seq), 15):
    chunk = d_seq[i:i+15]
    n_start = i + 2
    labels = [f"d[{n_start+j}]={v}" for j, v in enumerate(chunk)]
    print("  " + ", ".join(labels))

print("\n" + "-" * 80)
print("d-VALUE FREQUENCIES")
print("-" * 80)

from collections import Counter
freq = Counter(d_seq)
for d, count in sorted(freq.items()):
    pct = count / len(d_seq) * 100
    print(f"  d={d}: {count} times ({pct:.1f}%)")

print("\n" + "-" * 80)
print("d-VALUE BY MOD 3")
print("-" * 80)

for r in range(3):
    indices = [i for i in range(len(d_seq)) if (i+2) % 3 == r]
    d_vals = [d_seq[i] for i in indices]
    n_vals = [i+2 for i in indices]
    print(f"\nn ≡ {r} (mod 3):")
    print(f"  n values: {n_vals[:15]}...")
    print(f"  d values: {d_vals[:15]}...")
    print(f"  d frequencies: {dict(Counter(d_vals))}")

print("\n" + "-" * 80)
print("d-VALUE TRANSITIONS")
print("-" * 80)

print("\nWhen does d change from previous value?")
changes = []
for i in range(1, len(d_seq)):
    if d_seq[i] != d_seq[i-1]:
        n = i + 2
        changes.append((n, d_seq[i-1], d_seq[i]))
        if len(changes) <= 20:
            print(f"  n={n}: d changed from {d_seq[i-1]} to {d_seq[i]}")

print(f"\nTotal changes: {len(changes)}")

print("\n" + "-" * 80)
print("d > 3 OCCURRENCES (special cases)")
print("-" * 80)

special = [(i+2, d_seq[i]) for i in range(len(d_seq)) if d_seq[i] > 3]
for n, d in special:
    print(f"  n={n}: d={d}, m[{n}]={m_seq[n-2]:,}")

print("\n" + "-" * 80)
print("PREDICTION HYPOTHESIS")
print("-" * 80)

print("""
Based on the data:
1. d[n] = 2 is most common (about 55%)
2. d[n] = 3 is second (about 30%)
3. d[n] > 3 appears at specific n values

Hypothesis: d[n] follows a rule based on n mod something
and m[n-1], m[n-2] values.

For n=71:
- 71 mod 3 = 2
- Looking at n ≡ 2 (mod 3): d values are often 2

Most likely d[71] ∈ {2, 3, 5, 8} based on historical patterns.
""")
