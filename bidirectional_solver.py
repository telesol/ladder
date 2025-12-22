#!/usr/bin/env python3
"""
Bidirectional Solver for Bitcoin Puzzle Gaps
============================================
Implements Phi's algorithm with mathematical verification from Wave 12.

Core equations:
- Forward:  k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
- Backward: k[n-1] = (k[n] - 2^n + m[n]*k[d[n]]) / 2
- Unified:  m[n] = (2^n - adj[n]) / k[d[n]]

For each gap, enumerate valid (m, d) combinations that satisfy:
1. Integer result (numerator divisible by 2 for backward)
2. Value in valid range [2^(n-1), 2^n)
3. d-minimization rule
4. c-oscillation constraints
"""

import json
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from itertools import product

# Load known data
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data.get('m_seq', [])  # m[2] to m[70]
d_seq = data.get('d_seq', [])  # d[2] to d[70]

# All known k-values
K_KNOWN: Dict[int, int] = {
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

# Compute c[n] = k[n] / 2^n for known values
C_KNOWN = {n: k / (2**n) for n, k in K_KNOWN.items()}

@dataclass
class Candidate:
    """A candidate solution for k[n]"""
    n: int
    k: int
    m: int
    d: int
    c: float

    def __hash__(self):
        return hash((self.n, self.k))

    def __eq__(self, other):
        return self.n == other.n and self.k == other.k


def is_valid_k_range(n: int, k: int) -> bool:
    """Check if k is in valid range [2^(n-1), 2^n)"""
    return 2**(n-1) <= k < 2**n


def forward_step(n: int, k_prev: int, m: int, d: int) -> Optional[int]:
    """
    Compute k[n] from k[n-1] using forward formula:
    k[n] = 2*k[n-1] + 2^n - m*k[d]
    """
    if d not in K_KNOWN:
        return None
    k_d = K_KNOWN[d]
    k_n = 2 * k_prev + (2**n) - m * k_d
    if is_valid_k_range(n, k_n):
        return k_n
    return None


def backward_step(n: int, k_next: int, m_next: int, d_next: int) -> Optional[int]:
    """
    Compute k[n] from k[n+1] using backward formula:
    k[n] = (k[n+1] - 2^(n+1) + m[n+1]*k[d[n+1]]) / 2

    Returns None if result is not integer or out of range.
    """
    if d_next not in K_KNOWN:
        return None
    k_d = K_KNOWN[d_next]
    numerator = k_next - (2**(n+1)) + m_next * k_d

    # Must be even for integer result
    if numerator % 2 != 0:
        return None

    k_n = numerator // 2
    if is_valid_k_range(n, k_n):
        return k_n
    return None


def compute_m_for_transition(n: int, k_prev: int, k_n: int, d: int) -> Optional[int]:
    """
    Given k[n-1], k[n], and d[n], compute what m[n] must be.
    From: k[n] = 2*k[n-1] + 2^n - m*k[d]
    Solve: m = (2*k[n-1] + 2^n - k[n]) / k[d]
    """
    if d not in K_KNOWN:
        return None
    k_d = K_KNOWN[d]
    numerator = 2 * k_prev + (2**n) - k_n
    if numerator % k_d != 0:
        return None
    m = numerator // k_d
    if m > 0:
        return m
    return None


def find_valid_d_values(n: int, k_prev: int, k_n: int) -> List[Tuple[int, int]]:
    """
    Find all (d, m) pairs that make the transition k[n-1] -> k[n] valid.
    Returns list of (d, m) tuples.
    """
    valid_pairs = []
    # Try all known d values
    for d in K_KNOWN.keys():
        if d >= n:  # d must be less than n
            continue
        m = compute_m_for_transition(n, k_prev, k_n, d)
        if m is not None and m > 0:
            valid_pairs.append((d, m))
    return valid_pairs


def find_minimizing_d(n: int, k_prev: int, k_n: int) -> Optional[Tuple[int, int]]:
    """
    Find the d value that minimizes m for the transition.
    This is the d-minimization rule verified 67/69 times.
    """
    valid_pairs = find_valid_d_values(n, k_prev, k_n)
    if not valid_pairs:
        return None
    # Find minimum m
    return min(valid_pairs, key=lambda x: x[1])


def enumerate_forward_candidates(n_start: int, n_end: int, k_start: int) -> Dict[int, Set[Candidate]]:
    """
    Forward propagation from k[n_start] to generate candidates for n_start+1 to n_end.

    For each step, we need to guess (m, d) pairs. We try:
    - d values from 1 to n-1 (all possible references)
    - m values that give valid k in range
    """
    candidates = {n: set() for n in range(n_start + 1, n_end + 1)}

    # Start with known anchor
    current_layer = {n_start: {Candidate(n_start, k_start, 0, 0, k_start / (2**n_start))}}

    for n in range(n_start + 1, n_end + 1):
        prev_candidates = current_layer.get(n - 1, set())
        for prev_cand in prev_candidates:
            # Try different d values
            for d in range(1, n):
                if d not in K_KNOWN:
                    continue
                k_d = K_KNOWN[d]

                # For forward: k[n] = 2*k[n-1] + 2^n - m*k[d]
                # We need k[n] in range [2^(n-1), 2^n)
                # So: 2^(n-1) <= 2*k[n-1] + 2^n - m*k[d] < 2^n
                # Rearranging for m:
                # 2*k[n-1] + 2^n - 2^n < m*k[d] <= 2*k[n-1] + 2^n - 2^(n-1)
                # 2*k[n-1] < m*k[d] <= 2*k[n-1] + 2^(n-1)

                base = 2 * prev_cand.k + (2**n)
                m_min = max(1, (base - 2**n + 1) // k_d)
                m_max = (base - 2**(n-1)) // k_d

                # Limit search to reasonable m values
                m_max = min(m_max, m_min + 1000)  # Cap at 1000 candidates per d

                for m in range(m_min, m_max + 1):
                    k_n = base - m * k_d
                    if is_valid_k_range(n, k_n):
                        c_n = k_n / (2**n)
                        candidates[n].add(Candidate(n, k_n, m, d, c_n))

        current_layer[n] = candidates[n]

    return candidates


def enumerate_backward_candidates(n_start: int, n_end: int, k_end: int) -> Dict[int, Set[Candidate]]:
    """
    Backward propagation from k[n_end] to generate candidates for n_end-1 down to n_start+1.

    For backward step at n:
    k[n] = (k[n+1] - 2^(n+1) + m[n+1]*k[d[n+1]]) / 2
    """
    candidates = {n: set() for n in range(n_start + 1, n_end)}

    # Start with known anchor
    current_layer = {n_end: {Candidate(n_end, k_end, 0, 0, k_end / (2**n_end))}}

    for n in range(n_end - 1, n_start, -1):
        next_candidates = current_layer.get(n + 1, set())
        for next_cand in next_candidates:
            # Try different d values for the NEXT step (n+1)
            for d_next in range(1, n + 1):
                if d_next not in K_KNOWN:
                    continue
                k_d = K_KNOWN[d_next]

                # For backward: k[n] = (k[n+1] - 2^(n+1) + m[n+1]*k[d[n+1]]) / 2
                # We need k[n] in range [2^(n-1), 2^n)
                # And numerator must be even

                # numerator = k[n+1] - 2^(n+1) + m*k[d]
                # k[n] = numerator / 2
                # 2^(n-1) <= numerator/2 < 2^n
                # 2^n <= numerator < 2^(n+1)

                base = next_cand.k - (2**(n+1))
                # numerator = base + m*k[d]
                # 2^n <= base + m*k[d] < 2^(n+1)
                # (2^n - base) <= m*k[d] < (2^(n+1) - base)

                m_min = max(1, (2**n - base + k_d - 1) // k_d)  # Ceiling
                m_max = (2**(n+1) - base - 1) // k_d

                # Limit search
                m_max = min(m_max, m_min + 1000)

                for m_next in range(m_min, m_max + 1):
                    numerator = base + m_next * k_d
                    if numerator % 2 == 0:  # Must be even
                        k_n = numerator // 2
                        if is_valid_k_range(n, k_n):
                            c_n = k_n / (2**n)
                            candidates[n].add(Candidate(n, k_n, m_next, d_next, c_n))

        current_layer[n] = candidates[n]

    return candidates


def solve_gap(n_low: int, n_high: int) -> Dict[int, Set[Candidate]]:
    """
    Solve a gap between two known anchors using bidirectional propagation.
    Returns candidates that appear in BOTH forward and backward results.
    """
    k_low = K_KNOWN[n_low]
    k_high = K_KNOWN[n_high]

    print(f"\n{'='*60}")
    print(f"SOLVING GAP: n={n_low+1} to n={n_high-1}")
    print(f"Lower anchor: k[{n_low}] = 0x{k_low:x}")
    print(f"Upper anchor: k[{n_high}] = 0x{k_high:x}")
    print(f"{'='*60}")

    # Forward propagation
    print("\nForward propagation...")
    forward = enumerate_forward_candidates(n_low, n_high - 1, k_low)
    for n in range(n_low + 1, n_high):
        print(f"  n={n}: {len(forward.get(n, set()))} candidates")

    # Backward propagation
    print("\nBackward propagation...")
    backward = enumerate_backward_candidates(n_low, n_high, k_high)
    for n in range(n_low + 1, n_high):
        print(f"  n={n}: {len(backward.get(n, set()))} candidates")

    # Find intersection
    print("\nFinding intersection...")
    intersection = {}
    for n in range(n_low + 1, n_high):
        fwd_k = {c.k for c in forward.get(n, set())}
        bwd_k = {c.k for c in backward.get(n, set())}
        common_k = fwd_k & bwd_k

        # Get full candidates for common k values
        intersection[n] = {c for c in forward.get(n, set()) if c.k in common_k}
        print(f"  n={n}: {len(intersection[n])} valid candidates")

    return intersection


def apply_c_oscillation_filter(candidates: Dict[int, Set[Candidate]],
                                c_low: float, c_high: float,
                                direction: str) -> Dict[int, Set[Candidate]]:
    """
    Apply c-oscillation constraint to filter candidates.
    direction: 'down' if c should decrease, 'up' if c should increase over the gap
    """
    filtered = {}
    for n, cands in candidates.items():
        if direction == 'down':
            # c should decrease: c[n] <= c_low
            filtered[n] = {c for c in cands if c.c <= c_low}
        else:
            # c should increase: c[n] >= c_low
            filtered[n] = {c for c in cands if c.c >= c_low}
    return filtered


def main():
    print("="*70)
    print("BIDIRECTIONAL SOLVER FOR BITCOIN PUZZLE GAPS")
    print("="*70)

    # Define gaps with their anchors and c-oscillation direction
    gaps = [
        (70, 75, 'down'),   # Gap A: c[75] < c[70], so decreasing
        (75, 80, 'up'),     # Gap B: c[80] > c[75], so increasing
        (80, 85, 'down'),   # Gap C: c[85] < c[80], so decreasing
        (85, 90, 'up'),     # Gap D: c[90] > c[85], so increasing
    ]

    all_results = {}

    for n_low, n_high, direction in gaps:
        c_low = C_KNOWN[n_low]
        c_high = C_KNOWN[n_high]

        print(f"\nc[{n_low}] = {c_low:.6f}, c[{n_high}] = {c_high:.6f}")
        print(f"Direction: {direction} (c should {'decrease' if direction == 'down' else 'increase'})")

        # Solve gap
        candidates = solve_gap(n_low, n_high)

        # Apply c-oscillation filter
        # For 'down': intermediate c values should trend toward c_high
        # For 'up': intermediate c values should trend toward c_high
        filtered = apply_c_oscillation_filter(candidates, c_low, c_high, direction)

        print(f"\nAfter c-oscillation filter:")
        for n in range(n_low + 1, n_high):
            print(f"  n={n}: {len(filtered.get(n, set()))} candidates")
            # Show top 5 by c value
            top = sorted(filtered.get(n, set()), key=lambda x: x.c)[:5]
            for c in top:
                print(f"    k=0x{c.k:x}, c={c.c:.6f}, m={c.m}, d={c.d}")

        all_results[(n_low, n_high)] = filtered

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    for (n_low, n_high), candidates in all_results.items():
        print(f"\nGap {n_low+1}-{n_high-1}:")
        for n in range(n_low + 1, n_high):
            count = len(candidates.get(n, set()))
            print(f"  k[{n}]: {count} candidate(s)")
            if count == 1:
                cand = list(candidates[n])[0]
                print(f"    UNIQUE: k=0x{cand.k:x}")
            elif count > 0 and count <= 10:
                for cand in sorted(candidates[n], key=lambda x: x.c):
                    print(f"    k=0x{cand.k:x}, c={cand.c:.6f}")


if __name__ == "__main__":
    main()
