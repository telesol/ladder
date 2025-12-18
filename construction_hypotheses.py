#!/usr/bin/env python3
"""
Explore CONSTRUCTION hypotheses for the ladder.
Instead of analyzing, think like the CREATOR.

Key Question: How would YOU build this ladder if you wanted to:
1. Embed π references
2. Use Fibonacci seeds
3. Make it look random but be deterministic?
"""

import sqlite3
from math import pi, sqrt, e
from fractions import Fraction

# Famous constants
PHI = (1 + sqrt(5)) / 2  # Golden ratio
SQRT2 = sqrt(2)

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

def cf_convergents(value, n_terms=20):
    """Get continued fraction convergents for a real value"""
    convergents = []
    a = []
    xi = value
    for _ in range(n_terms):
        ai = int(xi)
        a.append(ai)
        if abs(xi - ai) < 1e-12:
            break
        xi = 1 / (xi - ai)

    # Compute convergents p/q
    p = [0, 1]
    q = [1, 0]
    for i, ai in enumerate(a):
        p_i = ai * p[-1] + p[-2]
        q_i = ai * q[-1] + q[-2]
        p.append(p_i)
        q.append(q_i)
        convergents.append((p_i, q_i))
    return convergents, a

def main():
    keys = load_keys()
    k = [0] + [keys.get(i, 0) for i in range(1, 71)]

    print("=" * 70)
    print("CONSTRUCTION HYPOTHESIS EXPLORATION")
    print("=" * 70)

    # Get m, d sequences
    m_vals = []
    d_vals = []
    for n in range(2, 35):
        m, d = compute_m_d(k, n)
        m_vals.append(m)
        d_vals.append(d)

    print(f"\nm sequence (first 20): {m_vals[:20]}")
    print(f"d sequence (first 20): {d_vals[:20]}")

    # === HYPOTHESIS 1: π-seeded generator ===
    print("\n" + "=" * 50)
    print("HYPOTHESIS 1: π-seeded generator")
    print("=" * 50)
    print("What if the creator used π's continued fraction terms?")

    pi_conv, pi_cf = cf_convergents(pi)
    print(f"\nπ CF terms: {pi_cf}")
    print(f"π convergent nums: {[p for p,q in pi_conv[:8]]}")
    print(f"π convergent dens: {[q for p,q in pi_conv[:8]]}")

    # Check: m[2:5] = 3, 7, 22 matches π CF!
    all_pi_vals = set()
    for p, q in pi_conv[:10]:
        all_pi_vals.add(p)
        all_pi_vals.add(q)

    print(f"\nAll π convergent values (num+den): {sorted(all_pi_vals)}")
    print("\nWhich early m values are in π convergents?")
    for i, m in enumerate(m_vals[:15]):
        if m in all_pi_vals:
            print(f"  m[{i+2}] = {m} ✓ IN π CONVERGENTS")

    # === HYPOTHESIS 2: Combined constant encoding ===
    print("\n" + "=" * 50)
    print("HYPOTHESIS 2: Multiple constants cycling")
    print("=" * 50)

    e_conv, e_cf = cf_convergents(e)
    phi_conv, phi_cf = cf_convergents(PHI)
    sqrt2_conv, sqrt2_cf = cf_convergents(SQRT2)

    all_e_vals = set(p for p,q in e_conv[:10]).union(q for p,q in e_conv[:10])
    all_phi_vals = set(p for p,q in phi_conv[:10]).union(q for p,q in phi_conv[:10])

    print("\nConst  |  n  |  m_n  | Match?")
    print("-" * 40)
    for i, m in enumerate(m_vals[:15]):
        n = i + 2
        matches = []
        if m in all_pi_vals:
            matches.append("π")
        if m in all_e_vals:
            matches.append("e")
        if m in all_phi_vals:
            matches.append("φ")
        if matches:
            print(f"  n={n:2d}  | m={m:5d} | {', '.join(matches)}")

    # === HYPOTHESIS 3: d-sequence has hidden structure ===
    print("\n" + "=" * 50)
    print("HYPOTHESIS 3: d-sequence structure")
    print("=" * 50)
    print("If the creator picked d values, what's the pattern?")

    print(f"\nd sequence: {d_vals[:30]}")

    # Check d-sequence as binary
    d_binary = ''.join(str(d) for d in d_vals[:20])
    print(f"\nd as string: {d_binary}")

    # Check if d relates to n mod something
    print("\nd_n vs n mod 3, n mod 4, n mod 5:")
    for i, d in enumerate(d_vals[:15]):
        n = i + 2
        print(f"  n={n:2d}: d={d}, n%3={n%3}, n%4={n%4}, n%5={n%5}")

    # === HYPOTHESIS 4: Product relationships ===
    print("\n" + "=" * 50)
    print("HYPOTHESIS 4: m products relate to k values")
    print("=" * 50)
    print("Discovery: m[2] × m[3] = 3 × 7 = 21 = k[5]!")

    for i in range(len(m_vals[:12]) - 1):
        for j in range(i+1, min(i+4, len(m_vals))):
            prod = m_vals[i] * m_vals[j]
            # Check if product equals any k value
            for ki, kv in enumerate(k[1:21], 1):
                if prod == kv:
                    print(f"m[{i+2}] × m[{j+2}] = {m_vals[i]} × {m_vals[j]} = {prod} = k[{ki}]!")

    # === HYPOTHESIS 5: Ratios form a sequence ===
    print("\n" + "=" * 50)
    print("HYPOTHESIS 5: Consecutive m ratios")
    print("=" * 50)

    ratios = []
    for i in range(len(m_vals[:15]) - 1):
        if m_vals[i] and m_vals[i] != 0:
            ratio = m_vals[i+1] / m_vals[i]
            ratios.append(ratio)

            # Check if close to famous constant
            candidates = [
                ("π", pi), ("e", e), ("φ", PHI), ("√2", SQRT2),
                ("2", 2), ("3", 3), ("1/2", 0.5), ("1/3", 1/3),
                ("π/2", pi/2), ("e/2", e/2)
            ]
            closest = min(candidates, key=lambda x: abs(ratio - x[1]))
            if abs(ratio - closest[1]) < 0.15:
                print(f"m[{i+3}]/m[{i+2}] = {ratio:.4f} ≈ {closest[0]} ({closest[1]:.4f})")

    # === HYPOTHESIS 6: Fibonacci-style recurrence ===
    print("\n" + "=" * 50)
    print("HYPOTHESIS 6: Does m follow Fibonacci-like recurrence?")
    print("=" * 50)

    # Test: m[n] = a*m[n-1] + b*m[n-2]?
    for i in range(2, 10):
        if m_vals[i-2] != 0 and m_vals[i-1] != 0:
            # Solve for a,b: m[i] = a*m[i-1] + b*m[i-2]
            # Use next pair to verify
            if i+1 < len(m_vals):
                # m[i] = a*m[i-1] + b*m[i-2]
                # m[i+1] = a*m[i] + b*m[i-1]
                pass  # Need 2 equations to solve for a,b

    # Check simpler: m[n] = c * m[n-1] + offset?
    print("Testing m[n] = c * m[n-1] + offset:")
    for i in range(1, 10):
        if m_vals[i-1] != 0:
            c = m_vals[i] / m_vals[i-1]
            print(f"  m[{i+2}]/m[{i+1}] = {m_vals[i]}/{m_vals[i-1]} = {c:.4f}")

    # === HYPOTHESIS 7: Binary representation matters ===
    print("\n" + "=" * 50)
    print("HYPOTHESIS 7: Binary structure of m values")
    print("=" * 50)

    for i, m in enumerate(m_vals[:12]):
        if m:
            bits = bin(abs(m))[2:]
            print(f"m[{i+2}] = {m:5d} = {bits:>15s} ({len(bits)} bits, popcount={bin(abs(m)).count('1')})")

    # === Construction Recipe Proposal ===
    print("\n" + "=" * 70)
    print("PROPOSED CONSTRUCTION RECIPE")
    print("=" * 70)
    print("""
Based on discoveries:

1. SEED VALUES (n=2,3,4):
   - Use π convergent values: m[2]=3, m[3]=7, m[4]=22
   - This gives the famous 22/7 ≈ π ratio

2. TRANSITION (n=5+):
   - Switch to a deterministic but complex rule
   - d_n selection: minimize |m_n| within bounds
   - m_n derived from some PRNG seeded by π?

3. CONSTRAINTS:
   - norm_m = m_n / 2^(n-d_n) must be in [0.72, 2.75]
   - k_n = 2*k_{n-1} + adj_n must be valid

4. MYSTERY TO SOLVE:
   - What generates m_n for n >= 5?
   - Is there a state machine cycling through constants?
""")

    print("=" * 70)
    print("EXPLORATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
