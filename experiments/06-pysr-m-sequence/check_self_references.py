#!/usr/bin/env python3
"""
Check for self-references in the m-sequence.

This script looks for patterns like:
- m[n] appearing as a factor in later m[k] values
- m[n] related to products of earlier m values
- Prime relationships between m values
"""

import json
from pathlib import Path
from math import gcd

def main():
    # Load data
    data_path = Path('/home/rkh/ladder/data_for_csolver.json')
    with open(data_path, 'r') as f:
        data = json.load(f)

    m_seq = data['m_seq'][:30]  # First 30 values

    print("=" * 80)
    print("SELF-REFERENCE ANALYSIS: M-Sequence")
    print("=" * 80)

    # 1. Check if any m[i] divides m[j] for j > i
    print("\n1. DIVISIBILITY PATTERNS (m[i] divides m[j] for j > i)")
    print("-" * 80)

    divisibility_found = False
    for i in range(len(m_seq)):
        for j in range(i + 1, len(m_seq)):
            if m_seq[i] > 1 and m_seq[j] % m_seq[i] == 0:
                quotient = m_seq[j] // m_seq[i]
                print(f"m[{j+2}] = m[{i+2}] × {quotient}")
                print(f"  {m_seq[j]} = {m_seq[i]} × {quotient}")
                divisibility_found = True

    if not divisibility_found:
        print("No divisibility relationships found.")

    # 2. Check GCD patterns
    print("\n2. GCD PATTERNS (looking for common factors)")
    print("-" * 80)

    interesting_gcds = []
    for i in range(len(m_seq)):
        for j in range(i + 1, len(m_seq)):
            g = gcd(m_seq[i], m_seq[j])
            if g > 1 and g != m_seq[i] and g != m_seq[j]:  # Non-trivial GCD
                interesting_gcds.append((i+2, j+2, g, m_seq[i], m_seq[j]))

    # Sort by GCD value (descending) and show top 20
    interesting_gcds.sort(key=lambda x: x[2], reverse=True)

    if interesting_gcds:
        print(f"Found {len(interesting_gcds)} pairs with non-trivial GCD. Top 20:")
        for i, (idx_i, idx_j, g, val_i, val_j) in enumerate(interesting_gcds[:20]):
            print(f"  gcd(m[{idx_i}], m[{idx_j}]) = {g}")
            print(f"    m[{idx_i}] = {val_i}, m[{idx_j}] = {val_j}")
            if i < 19:  # Don't print separator after last item
                print()
    else:
        print("No non-trivial GCD patterns found.")

    # 3. Check for products of earlier m values
    print("\n3. PRODUCT PATTERNS (m[k] = m[i] × m[j])")
    print("-" * 80)

    product_found = False
    for k in range(len(m_seq)):
        for i in range(k):
            for j in range(i, k):
                if m_seq[i] * m_seq[j] == m_seq[k]:
                    print(f"m[{k+2}] = m[{i+2}] × m[{j+2}]")
                    print(f"  {m_seq[k]} = {m_seq[i]} × {m_seq[j]}")
                    product_found = True

    if not product_found:
        print("No exact product relationships found.")

    # 4. Check for sum/difference patterns
    print("\n4. SUM/DIFFERENCE PATTERNS")
    print("-" * 80)

    sum_found = False
    # Only check small values to avoid false positives
    for k in range(min(20, len(m_seq))):
        for i in range(k):
            for j in range(i, k):
                # Check sum
                if m_seq[i] + m_seq[j] == m_seq[k]:
                    print(f"m[{k+2}] = m[{i+2}] + m[{j+2}]")
                    print(f"  {m_seq[k]} = {m_seq[i]} + {m_seq[j]}")
                    sum_found = True
                # Check difference
                if abs(m_seq[i] - m_seq[j]) == m_seq[k]:
                    print(f"m[{k+2}] = |m[{i+2}] - m[{j+2}]|")
                    print(f"  {m_seq[k]} = |{m_seq[i]} - {m_seq[j]}|")
                    sum_found = True

    if not sum_found:
        print("No sum/difference relationships found (checked first 20 values).")

    # 5. Check for m[n] values that are close to ratios of other m values
    print("\n5. RATIO PATTERNS (m[k] / m[j] close to m[i])")
    print("-" * 80)

    ratio_found = False
    for k in range(len(m_seq)):
        for j in range(k):
            if m_seq[j] > 0:
                ratio = m_seq[k] / m_seq[j]
                # Check if ratio is close to any earlier m value
                for i in range(j):
                    if m_seq[i] > 0 and abs(ratio - m_seq[i]) / max(ratio, m_seq[i]) < 0.01:  # Within 1%
                        print(f"m[{k+2}] / m[{j+2}] ≈ m[{i+2}]")
                        print(f"  {m_seq[k]} / {m_seq[j]} = {ratio:.4f} ≈ {m_seq[i]}")
                        ratio_found = True

    if not ratio_found:
        print("No significant ratio relationships found.")

    # 6. Special: Check the 22/7 pattern and similar
    print("\n6. SPECIAL RATIOS (mathematical constants)")
    print("-" * 80)

    print(f"m[4] / m[3] = {m_seq[2]} / {m_seq[1]} = {m_seq[2] / m_seq[1]:.10f}")
    print(f"  Known: 22/7 = {22/7:.10f} ≈ π = {3.141592653589793:.10f}")
    print()

    # Check other interesting ratios
    import math
    for i in range(len(m_seq)):
        for j in range(len(m_seq)):
            if i != j and m_seq[j] > 0:
                ratio = m_seq[i] / m_seq[j]
                # Check against known constants
                if abs(ratio - math.pi) / math.pi < 0.01:
                    print(f"m[{i+2}] / m[{j+2}] ≈ π")
                    print(f"  {m_seq[i]} / {m_seq[j]} = {ratio:.10f}")
                if abs(ratio - math.e) / math.e < 0.01:
                    print(f"m[{i+2}] / m[{j+2}] ≈ e")
                    print(f"  {m_seq[i]} / {m_seq[j]} = {ratio:.10f}")
                phi = (1 + math.sqrt(5)) / 2
                if abs(ratio - phi) / phi < 0.01:
                    print(f"m[{i+2}] / m[{j+2}] ≈ φ (golden ratio)")
                    print(f"  {m_seq[i]} / {m_seq[j]} = {ratio:.10f}")

    # 7. Value repetitions
    print("\n7. VALUE REPETITIONS")
    print("-" * 80)

    value_counts = {}
    for i, val in enumerate(m_seq):
        if val not in value_counts:
            value_counts[val] = []
        value_counts[val].append(i + 2)  # m[2] is at index 0

    repeated = {val: indices for val, indices in value_counts.items() if len(indices) > 1}

    if repeated:
        print("Values that appear multiple times:")
        for val, indices in sorted(repeated.items()):
            indices_str = ', '.join([f'm[{i}]' for i in indices])
            print(f"  {val}: {indices_str}")
    else:
        print("No repeated values found.")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
