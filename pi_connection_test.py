#!/usr/bin/env python3
"""
Explore the PI connection!
m[4]/m[3] = 22/7 ≈ π - is this intentional?
"""

import sqlite3
from math import pi

def load_keys():
    conn = sqlite3.connect("db/kh.db")
    cur = conn.cursor()
    cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
    rows = cur.fetchall()
    conn.close()
    return {r[0]: int(r[1], 16) for r in rows}

def compute_m_d(k, n):
    adj_n = k[n] - 2 * k[n-1]
    best_d, best_m = None, None
    best_m_abs = float('inf')
    for d in range(1, min(n, 9)):
        if k[d] == 0:
            continue
        numerator = (1 << n) - adj_n
        if numerator % k[d] == 0:
            m = numerator // k[d]
            if abs(m) < best_m_abs:
                best_m = m
                best_d = d
                best_m_abs = abs(m)
    return best_m, best_d

# Pi's continued fraction: [3; 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, ...]
# Convergents of pi: 3/1, 22/7, 333/106, 355/113, ...
PI_CONVERGENTS = [
    (3, 1),
    (22, 7),
    (333, 106),
    (355, 113),
    (103993, 33102),
    (104348, 33215),
]

def main():
    keys = load_keys()
    k = [0] + [keys.get(i, 0) for i in range(1, 71)]

    print("=" * 70)
    print("PI CONNECTION EXPLORATION")
    print("=" * 70)

    # Get all m values
    m_vals = []
    for n in range(2, 71):
        m, d = compute_m_d(k, n)
        m_vals.append((n, m, d))

    # Check ratios against pi convergents
    print("\n=== Check if m ratios relate to pi convergents ===")
    print("Pi convergents: 3/1, 22/7, 333/106, 355/113, ...")
    print()

    for i in range(1, min(20, len(m_vals))):
        n_prev, m_prev, d_prev = m_vals[i-1]
        n_cur, m_cur, d_cur = m_vals[i]
        if m_prev and m_cur and m_prev != 0:
            ratio = m_cur / m_prev
            # Check against pi convergent ratios
            for num, denom in PI_CONVERGENTS:
                pi_ratio = num / denom
                if abs(ratio - pi_ratio) < 0.1:
                    print(f"n={n_cur}: m[{n_cur}]/m[{n_prev}] = {m_cur}/{m_prev} = {ratio:.6f} ≈ {num}/{denom} = {pi_ratio:.6f} !")

    # Check if m values themselves are pi-related
    print("\n=== Check if m values appear in pi convergents ===")
    pi_nums = {3, 22, 333, 355, 103993, 104348, 7, 106, 113, 33102, 33215}
    for n, m, d in m_vals[:30]:
        if m in pi_nums:
            print(f"n={n:2d}: m={m} appears in pi convergents!")

    # Check m / pi relationships
    print("\n=== m / pi^x for various x ===")
    for n, m, d in m_vals[:20]:
        if m:
            for x in [1, 2, 0.5]:
                ratio = m / (pi ** x)
                if abs(ratio - round(ratio)) < 0.1:
                    print(f"n={n:2d}: m={m}, m/pi^{x} = {ratio:.4f} ≈ {round(ratio)}")

    # Check if consecutive m values multiply/divide by pi
    print("\n=== Check m[n] / m[n-1] patterns ===")
    for i in range(1, 20):
        n_prev, m_prev, _ = m_vals[i-1]
        n_cur, m_cur, _ = m_vals[i]
        if m_prev and m_cur and m_prev != 0:
            ratio = m_cur / m_prev
            mult_pi = ratio / pi
            div_pi = ratio * pi
            print(f"m[{n_cur}]/m[{n_prev}] = {ratio:.4f}, /pi = {mult_pi:.4f}, *pi = {div_pi:.4f}")

    # The sequence 3, 7, 22 - is this pi's convergent numerators?
    print("\n=== Key observation: 3, 7, 22 ===")
    print("Pi convergent numerators: 3, 22, 333, 355, ...")
    print("Pi convergent denominators: 1, 7, 106, 113, ...")
    print()
    print("Our m sequence starts: 3, 7, 22, ...")
    print("  - 3 is a pi numerator!")
    print("  - 7 is a pi denominator!")
    print("  - 22 is a pi numerator!")
    print()
    print("PATTERN: Are m values alternating between pi convergent numerators and denominators?")

    # Test this hypothesis
    print("\n=== Testing alternation hypothesis ===")
    pi_seq = [3, 1, 22, 7, 333, 106, 355, 113]  # Alternating num/denom
    for i, (n, m, d) in enumerate(m_vals[:8]):
        match = "MATCH!" if m == pi_seq[i] else f"expected {pi_seq[i]}"
        print(f"n={n}: m={m}, pi_seq[{i}]={pi_seq[i]} {match}")

    # What about the ratio 22/7?
    print("\n=== The magical 22/7 ===")
    print(f"m[4] / m[3] = 22 / 7 = {22/7:.6f}")
    print(f"π = {pi:.6f}")
    print(f"Difference: {abs(22/7 - pi):.6f}")
    print()
    print("This is one of the most famous rational approximations of π!")
    print("The puzzle creator may have embedded π references in the sequence.")

    # Look at products/sums of consecutive m
    print("\n=== Products and sums ===")
    for i in range(1, 8):
        n_prev, m_prev, _ = m_vals[i-1]
        n_cur, m_cur, _ = m_vals[i]
        if m_prev and m_cur:
            prod = m_prev * m_cur
            summ = m_prev + m_cur
            print(f"m[{n_prev}]*m[{n_cur}] = {m_prev}*{m_cur} = {prod}, sum = {summ}")

    print("\n" + "=" * 70)
    print("PI EXPLORATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
