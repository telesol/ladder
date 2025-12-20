#!/usr/bin/env python3
"""
Look for self-referential patterns in m-sequence.
Hypothesis: m[n] might involve m[earlier] values or combinations of them.
"""

import json

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

print("=" * 80)
print("SELF-REFERENTIAL PATTERN ANALYSIS")
print("=" * 80)

# Check if m[n] is a multiple of earlier m values
print("\n### Checking m[n] = a × m[k] for various k ###\n")

for n in range(60, 71):
    idx = n - 2
    if idx < len(m_seq):
        m_n = m_seq[idx]
        print(f"\nm[{n}] = {m_n}")

        # Check divisibility by earlier m-values
        for k in range(4, min(n, 30)):
            k_idx = k - 2
            if k_idx < len(m_seq) and m_seq[k_idx] > 1:
                m_k = m_seq[k_idx]
                if m_n % m_k == 0:
                    quotient = m_n // m_k
                    if quotient < 10**12:  # Only show if quotient is reasonable
                        print(f"  m[{n}] = m[{k}] × {quotient} = {m_k} × {quotient}")

# Check pattern: m[n] = m[n-3] × ratio
print("\n" + "=" * 80)
print("CHECKING m[n] / m[n-3] RATIOS")
print("=" * 80)

for n in range(10, 71):
    idx = n - 2
    if idx < len(m_seq) and idx >= 3:
        m_n = m_seq[idx]
        m_n3 = m_seq[idx - 3]
        if m_n3 > 0:
            ratio = m_n / m_n3
            if n >= 60:
                print(f"m[{n}] / m[{n-3}] = {ratio:.6f}")

# Check if m[n] relates to 2^k for some k
print("\n" + "=" * 80)
print("CHECKING m[n] vs 2^n")
print("=" * 80)

for n in range(60, 71):
    idx = n - 2
    if idx < len(m_seq):
        m_n = m_seq[idx]
        two_n = 2**n
        ratio = m_n / two_n
        print(f"m[{n}] / 2^{n} = {ratio:.10f}")
        print(f"  m[{n}] = {ratio:.10f} × 2^{n}")

# Key convergent values
print("\n" + "=" * 80)
print("SPECIFIC CONVERGENT CHECKS")
print("=" * 80)

# Important numbers from convergents
key_nums = {
    17: "√2_num[3]",
    113: "π_den[3]",
    22: "π_num[1]",
    19: "e_num[4]",
    355: "π_num[3]",
    577: "√2_num[7]",
    1393: "√2_num[8]",
}

for n in range(60, 71):
    idx = n - 2
    if idx < len(m_seq):
        m_n = m_seq[idx]
        print(f"\nm[{n}] = {m_n}")
        for num, name in key_nums.items():
            if m_n % num == 0:
                print(f"  divisible by {num} ({name}): m[{n}] = {num} × {m_n // num}")

# Look at the differences between m-values
print("\n" + "=" * 80)
print("DIFFERENCE PATTERNS")
print("=" * 80)

for n in range(61, 71):
    idx = n - 2
    if idx < len(m_seq) and idx > 0:
        m_n = m_seq[idx]
        m_prev = m_seq[idx - 1]
        diff = m_n - m_prev
        print(f"m[{n}] - m[{n-1}] = {diff}")
        # Check if diff is divisible by key numbers
        for num in [17, 19, 22, 113]:
            if diff % num == 0:
                print(f"  = {num} × {diff // num}")

# Critical: analyze the index selection pattern
print("\n" + "=" * 80)
print("INDEX SELECTION PATTERN")
print("=" * 80)

print("\nFor each n, the convergent index seems to follow a pattern.")
print("Let's look at what index would be needed:\n")

# For known m-values that are direct convergent values
direct_matches = {
    4: ("π_num", 1, 22),
    5: ("ln2_num", 4, 9),
    6: ("e_num", 4, 19),
    9: ("product", "17×29", 493),
    10: ("e_num", 4, 19),
    11: ("product", "17×113", 1921),
}

for n, (const, idx, val) in direct_matches.items():
    print(f"n={n}: m={val}, from {const}[{idx}]")
    if isinstance(idx, int):
        # Check if idx relates to n
        print(f"      idx={idx}, n-idx={n-idx}, n%8={n%8}")
