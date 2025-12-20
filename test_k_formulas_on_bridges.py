#!/usr/bin/env python3
"""Test k-sequence formula hypotheses on bridge validation points.

Strategy:
- We know k1-k70 from database
- We have bridges: k75, k80, k85, k90, k95
- Test various formula types to predict bridges from k70
- If any formula works → we found the k-sequence pattern!
"""

import json
import sqlite3

# Load k-sequence from database
conn = sqlite3.connect('/home/solo/LadderV3/kh-assist/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 95 ORDER BY puzzle_id")
rows = cur.fetchall()
conn.close()

k_seq = {row[0]: int(row[1], 16) for row in rows}

print("="*80)
print("BRIDGE VALIDATION: Testing K-Sequence Formula Hypotheses")
print("="*80)
print()

# Known values
print("Known k-values available:")
print(f"  k1-k70: {len([n for n in k_seq if n <= 70])} values")
bridges = [75, 80, 85, 90, 95]
available_bridges = [b for b in bridges if b in k_seq]
print(f"  Bridges: {available_bridges}")
print()

# Test various formula types
print("="*80)
print("HYPOTHESIS TESTING")
print("="*80)
print()

results = []

# HYPOTHESIS 1: Linear Combination (a*k_i + b*k_j)
print("H1: Linear Combination - k_n = a*k_i + b*k_j")
print("-" * 60)

for bridge in available_bridges:
    if bridge not in k_seq:
        continue

    k_actual = k_seq[bridge]
    best_match = None
    best_error = float('inf')

    # Try different index combinations
    for i in range(max(1, bridge-20), bridge):
        if i not in k_seq:
            continue
        for j in range(max(1, bridge-20), bridge):
            if j not in k_seq or j == i:
                continue

            # Try small integer coefficients
            for a in range(-20, 21):
                for b in range(-20, 21):
                    if a == 0 and b == 0:
                        continue

                    k_pred = a * k_seq[i] + b * k_seq[j]
                    error = abs(k_pred - k_actual)

                    if error < best_error:
                        best_error = error
                        best_match = {
                            'formula': f'k{bridge} = {a}*k{i} + {b}*k{j}',
                            'predicted': k_pred,
                            'actual': k_actual,
                            'error': error,
                            'error_pct': 100 * error / k_actual if k_actual != 0 else 0
                        }

    if best_match:
        results.append(('H1_Linear', bridge, best_match))
        status = "✅ EXACT" if best_match['error'] == 0 else f"~{best_match['error_pct']:.2f}% error"
        print(f"  {best_match['formula']}: {status}")

print()

# HYPOTHESIS 2: Multiplication (k_n = k_i * k_j)
print("H2: Multiplication - k_n = k_i * k_j")
print("-" * 60)

for bridge in available_bridges:
    if bridge not in k_seq:
        continue

    k_actual = k_seq[bridge]
    best_match = None
    best_error = float('inf')

    for i in range(max(1, bridge-20), bridge):
        if i not in k_seq:
            continue
        for j in range(max(1, bridge-20), bridge):
            if j not in k_seq:
                continue

            k_pred = k_seq[i] * k_seq[j]
            error = abs(k_pred - k_actual)

            if error < best_error:
                best_error = error
                best_match = {
                    'formula': f'k{bridge} = k{i} * k{j}',
                    'predicted': k_pred,
                    'actual': k_actual,
                    'error': error,
                    'error_pct': 100 * error / k_actual if k_actual != 0 else 0
                }

    if best_match:
        results.append(('H2_Mult', bridge, best_match))
        status = "✅ EXACT" if best_match['error'] == 0 else f"~{best_match['error_pct']:.2f}% error"
        print(f"  {best_match['formula']}: {status}")

print()

# HYPOTHESIS 3: Power (k_n = k_i^p)
print("H3: Power - k_n = k_i^p")
print("-" * 60)

for bridge in available_bridges:
    if bridge not in k_seq:
        continue

    k_actual = k_seq[bridge]
    best_match = None
    best_error = float('inf')

    for i in range(max(1, bridge-20), bridge):
        if i not in k_seq:
            continue

        # Try small powers
        for p in range(2, 6):
            try:
                k_pred = k_seq[i] ** p
                error = abs(k_pred - k_actual)

                if error < best_error:
                    best_error = error
                    best_match = {
                        'formula': f'k{bridge} = k{i}^{p}',
                        'predicted': k_pred,
                        'actual': k_actual,
                        'error': error,
                        'error_pct': 100 * error / k_actual if k_actual != 0 else 0
                    }
            except OverflowError:
                continue

    if best_match:
        results.append(('H3_Power', bridge, best_match))
        status = "✅ EXACT" if best_match['error'] == 0 else f"~{best_match['error_pct']:.2f}% error"
        print(f"  {best_match['formula']}: {status}")

print()

# HYPOTHESIS 4: Modular Pattern (k_n mod some_value)
print("H4: Modular - k_n = f(k_prev) mod M")
print("-" * 60)

for bridge in available_bridges:
    if bridge not in k_seq or bridge-1 not in k_seq:
        continue

    k_actual = k_seq[bridge]
    k_prev = k_seq[bridge-1]
    best_match = None
    best_error = float('inf')

    # Try modular multiplier
    for mult in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
        for offset in range(-100, 101):
            k_pred = (mult * k_prev + offset)
            error = abs(k_pred - k_actual)

            if error < best_error:
                best_error = error
                best_match = {
                    'formula': f'k{bridge} = {mult}*k{bridge-1} + {offset}',
                    'predicted': k_pred,
                    'actual': k_actual,
                    'error': error,
                    'error_pct': 100 * error / k_actual if k_actual != 0 else 0
                }

    if best_match:
        results.append(('H4_Modular', bridge, best_match))
        status = "✅ EXACT" if best_match['error'] == 0 else f"~{best_match['error_pct']:.2f}% error"
        print(f"  {best_match['formula']}: {status}")

print()

# HYPOTHESIS 5: Master Formula Reverse (predict m from k)
print("H5: Derive from Master Formula - k_n = 2*k_{n-1} + (2^n - m*k_d)")
print("-" * 60)

# Load m and d sequences
with open('/home/solo/LadderV3/kh-assist/data_for_csolver.json') as f:
    data = json.load(f)

m_list = data['m_seq']
d_list = data['d_seq']
m_seq = {n: m_list[n-2] for n in range(2, min(71, 2 + len(m_list)))}
d_seq = {n: d_list[n-2] for n in range(2, min(71, 2 + len(d_list)))}

for bridge in available_bridges:
    if bridge not in k_seq or bridge-1 not in k_seq:
        continue

    k_actual = k_seq[bridge]
    k_prev = k_seq[bridge-1]

    # Try to find (d, m) that would generate this k
    valid_pairs = []
    for d_candidate in range(1, bridge):
        if d_candidate not in k_seq:
            continue

        k_d = k_seq[d_candidate]
        if k_d == 0:
            continue

        # Solve for m: k_n = 2*k_{n-1} + (2^n - m*k_d)
        # m = (2^n - (k_n - 2*k_{n-1})) / k_d
        numerator = (2**bridge - (k_actual - 2*k_prev))
        if numerator % k_d == 0:
            m_candidate = numerator // k_d
            if m_candidate > 0:
                valid_pairs.append((d_candidate, m_candidate))

    if valid_pairs:
        # Find minimum m (per the discovery from other Claudes)
        min_pair = min(valid_pairs, key=lambda x: x[1])
        d_min, m_min = min_pair

        # Reconstruct k to verify
        k_d = k_seq[d_min]
        k_reconstructed = 2*k_prev + (2**bridge - m_min * k_d)

        match = {
            'formula': f'k{bridge} = 2*k{bridge-1} + (2^{bridge} - {m_min}*k{d_min})',
            'predicted': k_reconstructed,
            'actual': k_actual,
            'error': abs(k_reconstructed - k_actual),
            'd': d_min,
            'm': m_min,
            'valid_pairs_count': len(valid_pairs)
        }

        results.append(('H5_MasterFormula', bridge, match))
        status = "✅ EXACT" if match['error'] == 0 else f"❌ ERROR"
        print(f"  {match['formula']}")
        print(f"    d={d_min}, m={m_min} (from {len(valid_pairs)} valid pairs): {status}")

print()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)
print()

exact_matches = [r for r in results if r[2]['error'] == 0]
print(f"Exact matches found: {len(exact_matches)}/{len(results)}")
print()

if exact_matches:
    print("✅ FORMULAS THAT WORK:")
    for hyp_type, bridge, match in exact_matches:
        print(f"  [{hyp_type}] {match['formula']}")
else:
    print("No exact formulas found. Best approximations:")
    sorted_results = sorted(results, key=lambda r: r[2]['error_pct'] if 'error_pct' in r[2] else float('inf'))
    for hyp_type, bridge, match in sorted_results[:5]:
        if 'error_pct' in match:
            print(f"  [{hyp_type}] {match['formula']} ({match['error_pct']:.2f}% error)")

print()
print("="*80)

# Save results
output = {
    'total_tests': len(results),
    'exact_matches': len(exact_matches),
    'results': [
        {
            'hypothesis': r[0],
            'bridge': r[1],
            'formula': r[2]['formula'],
            'error': r[2]['error'],
            'predicted': r[2]['predicted'],
            'actual': r[2]['actual']
        }
        for r in results
    ]
}

with open('/home/solo/LadderV3/kh-assist/bridge_formula_validation.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Results saved to bridge_formula_validation.json")
