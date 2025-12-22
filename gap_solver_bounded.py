#!/usr/bin/env python3
"""
Gap Solver with C-Interpolation Bounds
======================================
Uses Phi's insight: Linear interpolation of c[n] gives TIGHT bounds on k[n].
"""

# Known k values
K = {
    1: 1, 2: 3, 3: 7, 4: 8, 5: 21, 6: 49, 7: 76, 8: 224,
    70: 970436974005023690481,
    75: 22538323240989823823367,
    80: 1105520030589234487939456,
    85: 21090315766411506144426920,
    90: 868012190417726402719548863
}

# Compute c values
C = {n: k / (2**n) for n, k in K.items()}

def linear_interpolate_c(n, n_low, n_high, c_low, c_high):
    """Linear interpolation of c value"""
    return c_low + (n - n_low) * (c_high - c_low) / (n_high - n_low)

def compute_k_bounds(n, c_target, tolerance=0.05):
    """Compute k bounds from c with tolerance"""
    c_min = c_target * (1 - tolerance)
    c_max = c_target * (1 + tolerance)
    k_min = int(c_min * (2**n))
    k_max = int(c_max * (2**n))
    return k_min, k_max

def forward_compute(n, k_prev, m, d):
    """k[n] = 2*k[n-1] + 2^n - m*k[d]"""
    if d not in K:
        return None
    return 2 * k_prev + (2**n) - m * K[d]

def backward_compute(n, k_next, m_next, d_next):
    """k[n] = (k[n+1] - 2^(n+1) + m*k[d]) / 2"""
    if d_next not in K:
        return None
    numerator = k_next - (2**(n+1)) + m_next * K[d_next]
    if numerator % 2 != 0:
        return None
    return numerator // 2

def solve_gap_a():
    """Solve Gap A: k[71]-k[74] between k[70] and k[75]"""
    print("="*70)
    print("SOLVING GAP A: k[71] to k[74]")
    print("="*70)

    k70 = K[70]
    k75 = K[75]
    c70 = C[70]
    c75 = C[75]

    print(f"\nAnchors:")
    print(f"  k[70] = {k70} (c={c70:.6f})")
    print(f"  k[75] = {k75} (c={c75:.6f})")

    # Compute expected c values using linear interpolation
    print(f"\nLinear interpolation of c values:")
    c_expected = {}
    k_bounds = {}
    for n in [71, 72, 73, 74]:
        c_n = linear_interpolate_c(n, 70, 75, c70, c75)
        c_expected[n] = c_n
        k_min, k_max = compute_k_bounds(n, c_n, tolerance=0.03)  # 3% tolerance
        k_bounds[n] = (k_min, k_max)
        k_target = int(c_n * (2**n))
        print(f"  c[{n}] = {c_n:.6f}, k[{n}] ≈ {k_target}")
        print(f"    Bounds: [{k_min}, {k_max}]")
        print(f"    Range size: {k_max - k_min} ({(k_max-k_min)/(2**(n-1))*100:.4f}% of valid range)")

    # Strategy: Start from k[70], enumerate candidates for k[71]
    # Then check if they can lead to k[75] through the chain

    print(f"\n{'='*70}")
    print("BACKWARD CHAIN FROM k[75]")
    print(f"{'='*70}")

    # Try common d values: 1, 2, 3, 5
    d_candidates = [1, 2, 3, 5, 8]

    # k[74] from k[75]
    k74_candidates = []
    k74_min, k74_max = k_bounds[74]

    print(f"\nSearching for k[74] in range [{k74_min}, {k74_max}]...")

    for d75 in d_candidates:
        if d75 not in K:
            continue
        k_d75 = K[d75]

        # k[74] = (k[75] - 2^75 + m[75]*k[d75]) / 2
        # For k[74] in [k74_min, k74_max]:
        # 2*k74_min <= k[75] - 2^75 + m[75]*k[d75] <= 2*k74_max
        # m[75] >= (2*k74_min - k[75] + 2^75) / k[d75]
        # m[75] <= (2*k74_max - k[75] + 2^75) / k[d75]

        base = K[75] - 2**75
        m_min = max(1, (2*k74_min - K[75] + 2**75 + k_d75 - 1) // k_d75)
        m_max = (2*k74_max - K[75] + 2**75) // k_d75

        if m_max < m_min:
            continue

        print(f"\n  d[75]={d75}: m[75] in [{m_min}, {m_max}]")

        for m75 in range(m_min, min(m_max + 1, m_min + 100)):  # Limit search
            k74 = backward_compute(74, K[75], m75, d75)
            if k74 is not None and k74_min <= k74 <= k74_max:
                c74 = k74 / (2**74)
                k74_candidates.append((k74, m75, d75, c74))
                if len(k74_candidates) <= 10:
                    print(f"    m[75]={m75}: k[74]=0x{k74:x}, c={c74:.6f}")

    print(f"\nFound {len(k74_candidates)} k[74] candidates")

    # Continue backward to k[73], k[72], k[71]
    k73_candidates = []
    k73_min, k73_max = k_bounds[73]

    print(f"\nSearching for k[73] from {len(k74_candidates)} k[74] candidates...")

    for k74, m75, d75, c74 in k74_candidates[:50]:  # Limit to top 50
        for d74 in d_candidates:
            if d74 not in K:
                continue
            k_d74 = K[d74]

            m_min = max(1, (2*k73_min - k74 + 2**74 + k_d74 - 1) // k_d74)
            m_max = (2*k73_max - k74 + 2**74) // k_d74

            if m_max < m_min:
                continue

            for m74 in range(m_min, min(m_max + 1, m_min + 50)):
                k73 = backward_compute(73, k74, m74, d74)
                if k73 is not None and k73_min <= k73 <= k73_max:
                    c73 = k73 / (2**73)
                    k73_candidates.append((k73, k74, m74, d74, c73))

    print(f"Found {len(k73_candidates)} k[73] candidates")

    # Continue to k[72]
    k72_candidates = []
    k72_min, k72_max = k_bounds[72]

    print(f"\nSearching for k[72] from {len(k73_candidates)} k[73] candidates...")

    for k73, k74, m74, d74, c73 in k73_candidates[:100]:
        for d73 in d_candidates:
            if d73 not in K:
                continue
            k_d73 = K[d73]

            m_min = max(1, (2*k72_min - k73 + 2**73 + k_d73 - 1) // k_d73)
            m_max = (2*k72_max - k73 + 2**73) // k_d73

            if m_max < m_min:
                continue

            for m73 in range(m_min, min(m_max + 1, m_min + 50)):
                k72 = backward_compute(72, k73, m73, d73)
                if k72 is not None and k72_min <= k72 <= k72_max:
                    c72 = k72 / (2**72)
                    k72_candidates.append((k72, k73, k74, m73, d73, c72))

    print(f"Found {len(k72_candidates)} k[72] candidates")

    # Continue to k[71]
    k71_candidates = []
    k71_min, k71_max = k_bounds[71]

    print(f"\nSearching for k[71] from {len(k72_candidates)} k[72] candidates...")

    for k72, k73, k74, m73, d73, c72 in k72_candidates[:200]:
        for d72 in d_candidates:
            if d72 not in K:
                continue
            k_d72 = K[d72]

            m_min = max(1, (2*k71_min - k72 + 2**72 + k_d72 - 1) // k_d72)
            m_max = (2*k71_max - k72 + 2**72) // k_d72

            if m_max < m_min:
                continue

            for m72 in range(m_min, min(m_max + 1, m_min + 50)):
                k71 = backward_compute(71, k72, m72, d72)
                if k71 is not None and k71_min <= k71 <= k71_max:
                    c71 = k71 / (2**71)
                    k71_candidates.append({
                        'k71': k71, 'k72': k72, 'k73': k73, 'k74': k74,
                        'm72': m72, 'd72': d72, 'c71': c71
                    })

    print(f"Found {len(k71_candidates)} k[71] candidates from backward chain")

    # Now verify forward from k[70]
    print(f"\n{'='*70}")
    print("FORWARD VERIFICATION FROM k[70]")
    print(f"{'='*70}")

    verified = []
    for cand in k71_candidates:
        k71 = cand['k71']

        # Check if k[71] can be computed from k[70]
        # k[71] = 2*k[70] + 2^71 - m[71]*k[d[71]]
        for d71 in d_candidates:
            if d71 not in K:
                continue
            k_d71 = K[d71]

            # m[71] = (2*k[70] + 2^71 - k[71]) / k[d71]
            numerator = 2*K[70] + 2**71 - k71
            if numerator % k_d71 == 0:
                m71 = numerator // k_d71
                if m71 > 0:
                    # Verify forward
                    k71_check = forward_compute(71, K[70], m71, d71)
                    if k71_check == k71:
                        cand['m71'] = m71
                        cand['d71'] = d71
                        verified.append(cand)
                        break

    print(f"\nVerified {len(verified)} complete solutions!")

    # Print results
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")

    for i, sol in enumerate(verified[:10]):
        print(f"\nSolution {i+1}:")
        print(f"  k[71] = 0x{sol['k71']:x} (c={sol['c71']:.6f})")
        print(f"    m[71]={sol['m71']}, d[71]={sol['d71']}")
        print(f"  k[72] = 0x{sol['k72']:x}")
        print(f"  k[73] = 0x{sol['k73']:x}")
        print(f"  k[74] = 0x{sol['k74']:x}")

    return verified


if __name__ == "__main__":
    solutions = solve_gap_a()

    if solutions:
        print(f"\n{'='*70}")
        print(f"TOTAL SOLUTIONS FOUND: {len(solutions)}")
        print(f"{'='*70}")
    else:
        print("\nNo solutions found - may need to expand search bounds")
