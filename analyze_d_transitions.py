#!/usr/bin/env python3
"""
Analyze d[n] transitions to predict d[71].
From MEMORY.md: d[71] prediction is a key task.
"""
import sqlite3

# Load k values and compute d values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 71):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

d_values = {}
for n in range(2, 71):
    if n in k_values and (n-1) in k_values:
        adj_n = k_values[n] - 2*k_values[n-1]
        N_n = 2**n - adj_n
        best_d = None
        best_m = None
        for try_d in range(1, n):
            if try_d in k_values:
                k_d = k_values[try_d]
                if N_n % k_d == 0:
                    m_try = N_n // k_d
                    if best_m is None or m_try < best_m:
                        best_m = m_try
                        best_d = try_d
        if best_d is not None:
            d_values[n] = best_d

print("=" * 70)
print("D-VALUE TRANSITION ANALYSIS FOR d[71] PREDICTION")
print("=" * 70)
print()

# Show d-sequence
print("### D-Sequence (n=50-70) ###")
d_seq = [d_values.get(n, '?') for n in range(50, 71)]
print(f"d[50:70] = {d_seq}")
print()

# Transition matrix: d[n-1] -> d[n]
print("### Transition Frequencies ###")
transitions = {}
for n in range(3, 71):
    if n in d_values and (n-1) in d_values:
        prev = d_values[n-1]
        curr = d_values[n]
        key = (prev, curr)
        transitions[key] = transitions.get(key, 0) + 1

# Show transitions from d[70]
d70 = d_values[70]
print(f"\nd[70] = {d70}")
print(f"\nTransitions FROM d={d70}:")
relevant = {k: v for k, v in transitions.items() if k[0] == d70}
total = sum(relevant.values())
for (prev, curr), count in sorted(relevant.items(), key=lambda x: -x[1]):
    print(f"  d={d70} -> d={curr}: {count} times ({100*count/total:.1f}%)")

# Most common d values in n=50-70
print("\n### D-Value Distribution (n=50-70) ###")
d_counts = {}
for n in range(50, 71):
    if n in d_values:
        d = d_values[n]
        d_counts[d] = d_counts.get(d, 0) + 1

for d, count in sorted(d_counts.items(), key=lambda x: -x[1]):
    pct = 100 * count / sum(d_counts.values())
    print(f"  d={d}: {count} times ({pct:.1f}%)")

# Check for patterns by n mod 3
print("\n### D-Values by n mod 3 ###")
for phase in range(3):
    phase_ds = [d_values[n] for n in range(50, 71) if n in d_values and n % 3 == phase]
    print(f"  n ≡ {phase} (mod 3): d values = {phase_ds}")

# Predict d[71]
print("\n### PREDICTION FOR d[71] ###")
print(f"71 ≡ {71 % 3} (mod 3)")
print(f"Previous d[n] where n ≡ 2 (mod 3): ", end="")
phase2_ds = [d_values[n] for n in range(50, 71) if n in d_values and n % 3 == 2]
print(phase2_ds)

# Count phase 2 d-values
phase2_counts = {}
for d in phase2_ds:
    phase2_counts[d] = phase2_counts.get(d, 0) + 1

print("\nPhase 2 (n ≡ 2 mod 3) distribution:")
for d, count in sorted(phase2_counts.items(), key=lambda x: -x[1]):
    pct = 100 * count / len(phase2_ds)
    print(f"  d={d}: {count} times ({pct:.1f}%)")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print()
most_likely = max(phase2_counts.items(), key=lambda x: x[1])[0] if phase2_counts else 1
print(f"Most likely d[71] = {most_likely} (based on n ≡ 2 mod 3 pattern)")
print(f"Fallback: d[71] = 1 (most common overall)")
