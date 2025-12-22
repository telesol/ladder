#!/usr/bin/env python3
"""
Optimized Gap Solver v2 - Using d-minimization and tighter bounds
=================================================================
Key optimizations:
1. Use d-minimization: try d=1,2 first (covers 72% of cases)
2. Use c-oscillation bounds to limit k range
3. Work backwards from upper anchor with known constraints
"""

import json
from typing import Dict, List, Tuple, Optional, Set

# Load known data
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data.get('m_seq', [])
d_seq = data.get('d_seq', [])

# All known k-values
K = {
    1: 0x1, 2: 0x3, 3: 0x7, 4: 0x8, 5: 0x15, 6: 0x31, 7: 0x4c, 8: 0xe0,
    9: 0x1d3, 10: 0x202, 11: 0x483, 12: 0xa7b, 13: 0x1460, 14: 0x2930, 15: 0x68f3,
    16: 0xc936, 17: 0x1764f, 18: 0x3080d, 19: 0x5749f, 20: 0xd2c55,
    21: 0x1ba534, 22: 0x2de40f, 23: 0x556e52, 24: 0xdc2a04, 25: 0x1fa5ee5,
    26: 0x340326e, 27: 0x6ac3875, 28: 0xd916ce8, 29: 0x17e2551e, 30: 0x3d94cd64,
    31: 0x7d4fe747, 32: 0xb862a62e, 33: 0x1a96ca8d8, 34: 0x34a65911d, 35: 0x4aed21170,
    36: 0x9de820a7c, 37: 0x1757756a93, 38: 0x22382facd0, 39: 0x4b5f8303e9, 40: 0xe9ae4933d6,
    41: 0x153869acc5b, 42: 0x2a221c58d8f, 43: 0x6bd3b27c591, 44: 0xe02b35a358f,
    45: 0x122fca143c05, 46: 0x2ec18388d544, 47: 0x6cd610b53cba, 48: 0xade6d7ce3b9b,
    49: 0x174176b015f4d, 50: 0x22bd43c2e9354, 51: 0x75070a1a009d4, 52: 0xefae164cb9e3c,
    53: 0x180788e47e326c, 54: 0x236fb6d5ad1f43, 55: 0x6abe1f9b67e114, 56: 0x9d18b63ac4ffdf,
    57: 0x1eb25c90795d61c, 58: 0x2c675b852189a21, 59: 0x7496cbb87cab44f, 60: 0xfc07a1825367bbe,
    61: 0x13c96a3742f64906, 62: 0x363d541eb611abee, 63: 0x7cce5efdaccf6808, 64: 0xf7051f27b09112d4,
    65: 0x1a838b13505b26867, 66: 0x2832ed74f2b5e35ee, 67: 0x730fc235c1942c1ae, 68: 0xbebb3940cd0fc1491,
    69: 0x101d83275fb2bc7e0c, 70: 0x349b84b6431a6c4ef1,
    75: 0x4c5ce114686a1336e07, 80: 0xea1a5c66dcc11b5ad180,
    85: 0x11720c4f018d51b8cebba8, 90: 0x2ce00bb2136a445c71e85bf
}

# Compute c values
C = {n: k / (2**n) for n, k in K.items()}

# Most common d values from n=2 to n=70
D_COMMON = [1, 2, 3, 4, 5, 8]  # Cover ~95% of cases

def is_valid_range(n: int, k: int) -> bool:
    """Check if k is in valid n-bit range"""
    return 2**(n-1) <= k < 2**n


def backward_candidates(n: int, k_next: int, d_candidates: List[int]) -> List[Tuple[int, int, int]]:
    """
    Find all valid (k[n], m, d) from k[n+1].
    k[n] = (k[n+1] - 2^(n+1) + m*k[d]) / 2

    Returns list of (k_n, m, d) tuples.
    """
    results = []
    for d in d_candidates:
        if d not in K or d >= n + 1:
            continue
        k_d = K[d]

        # numerator = k[n+1] - 2^(n+1) + m*k[d] must be even
        # k[n] = numerator / 2 must be in [2^(n-1), 2^n)
        # So: 2^n <= numerator < 2^(n+1)

        base = k_next - 2**(n+1)
        # numerator = base + m*k_d
        # 2^n <= base + m*k_d < 2^(n+1)

        # Solve for m bounds
        m_min = max(1, (2**n - base + k_d - 1) // k_d)
        m_max = (2**(n+1) - 1 - base) // k_d

        for m in range(m_min, m_max + 1):
            numerator = base + m * k_d
            if numerator % 2 == 0:
                k_n = numerator // 2
                if is_valid_range(n, k_n):
                    results.append((k_n, m, d))

    return results


def forward_verify(n: int, k_prev: int, k_n: int, m: int, d: int) -> bool:
    """
    Verify that k[n] = 2*k[n-1] + 2^n - m*k[d]
    """
    if d not in K:
        return False
    expected = 2 * k_prev + 2**n - m * K[d]
    return expected == k_n


def solve_gap_backward(n_low: int, n_high: int) -> Dict[int, List[Tuple[int, int, int]]]:
    """
    Solve gap by backward propagation from upper anchor.
    More efficient because we have a concrete starting point.
    """
    k_high = K[n_high]

    print(f"\n{'='*60}")
    print(f"GAP {n_low+1}-{n_high-1}: Backward from k[{n_high}]=0x{k_high:x}")
    print(f"{'='*60}")

    # Track candidates at each level: {n: [(k, m, d), ...]}
    candidates = {n_high: [(k_high, 0, 0)]}

    # Propagate backward
    for n in range(n_high - 1, n_low, -1):
        candidates[n] = []
        prev_candidates = candidates[n + 1]

        print(f"\nn={n}: propagating from {len(prev_candidates)} candidates at n={n+1}")

        for k_next, _, _ in prev_candidates:
            # Get backward candidates
            new_cands = backward_candidates(n, k_next, D_COMMON)
            candidates[n].extend(new_cands)

        # Remove duplicates (same k value)
        seen_k = {}
        for (k_n, m, d) in candidates[n]:
            if k_n not in seen_k:
                seen_k[k_n] = (m, d)
        candidates[n] = [(k, m, d) for k, (m, d) in seen_k.items()]

        c_values = [k / (2**n) for k, _, _ in candidates[n]]
        if c_values:
            print(f"  Found {len(candidates[n])} candidates")
            print(f"  c range: [{min(c_values):.6f}, {max(c_values):.6f}]")

    return candidates


def verify_forward_chain(candidates: Dict[int, List], n_low: int, n_high: int) -> Dict[int, List]:
    """
    Verify candidates by forward propagation from lower anchor.
    Only keep candidates that form a valid forward chain.
    """
    k_low = K[n_low]

    print(f"\nVerifying forward chain from k[{n_low}]=0x{k_low:x}")

    valid = {n_low: [(k_low, 0, 0)]}

    for n in range(n_low + 1, n_high):
        valid[n] = []

        for k_prev, _, _ in valid[n - 1]:
            for k_n, m, d in candidates.get(n, []):
                if forward_verify(n, k_prev, k_n, m, d):
                    valid[n].append((k_n, m, d))

        # Remove duplicates
        seen_k = {}
        for (k_n, m, d) in valid[n]:
            if k_n not in seen_k:
                seen_k[k_n] = (m, d)
        valid[n] = [(k, m, d) for k, (m, d) in seen_k.items()]

        print(f"  n={n}: {len(valid[n])} valid after forward verification")

    return valid


def apply_c_constraint(candidates: Dict[int, List], n_low: int, n_high: int) -> Dict[int, List]:
    """
    Apply c-oscillation constraint.
    For 70->75 (DOWN): c should decrease
    For 75->80 (UP): c should increase
    """
    c_low = C[n_low]
    c_high = C[n_high]
    going_down = c_high < c_low

    print(f"\nApplying c-constraint: c[{n_low}]={c_low:.4f} -> c[{n_high}]={c_high:.4f}")
    print(f"Direction: {'DOWN' if going_down else 'UP'}")

    filtered = {}
    for n in range(n_low + 1, n_high):
        filtered[n] = []
        for k_n, m, d in candidates.get(n, []):
            c_n = k_n / (2**n)
            # Check if c_n is between c_low and c_high (or reasonable interpolation)
            if going_down:
                if c_n <= c_low * 1.1 and c_n >= c_high * 0.9:
                    filtered[n].append((k_n, m, d))
            else:
                if c_n >= c_low * 0.9 and c_n <= c_high * 1.1:
                    filtered[n].append((k_n, m, d))

        print(f"  n={n}: {len(filtered[n])} candidates after c-filter")

    return filtered


def main():
    print("="*70)
    print("OPTIMIZED GAP SOLVER V2")
    print("="*70)

    gaps = [
        (70, 75),  # Gap A
        (75, 80),  # Gap B
        (80, 85),  # Gap C
        (85, 90),  # Gap D
    ]

    all_results = {}

    for n_low, n_high in gaps:
        # Step 1: Backward propagation
        candidates = solve_gap_backward(n_low, n_high)

        # Step 2: Forward verification
        verified = verify_forward_chain(candidates, n_low, n_high)

        # Step 3: C-oscillation filter
        filtered = apply_c_constraint(verified, n_low, n_high)

        all_results[(n_low, n_high)] = filtered

        # Print results
        print(f"\n{'='*60}")
        print(f"RESULTS FOR GAP {n_low+1}-{n_high-1}")
        print(f"{'='*60}")

        for n in range(n_low + 1, n_high):
            cands = filtered.get(n, [])
            print(f"\nk[{n}]: {len(cands)} candidate(s)")
            for k_n, m, d in sorted(cands, key=lambda x: x[0])[:10]:
                c_n = k_n / (2**n)
                print(f"  k=0x{k_n:x}, c={c_n:.6f}, m={m}, d={d}")

    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)

    for (n_low, n_high), candidates in all_results.items():
        print(f"\nGap {n_low+1}-{n_high-1}:")
        for n in range(n_low + 1, n_high):
            cands = candidates.get(n, [])
            if len(cands) == 0:
                print(f"  k[{n}]: NO CANDIDATES")
            elif len(cands) == 1:
                k_n, m, d = cands[0]
                print(f"  k[{n}]: UNIQUE = 0x{k_n:x}")
            else:
                print(f"  k[{n}]: {len(cands)} candidates")


if __name__ == "__main__":
    main()
