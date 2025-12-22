#!/usr/bin/env python3
"""
M-SEQUENCE GENERATOR
Uses discovered recurrence relation: m[n] = a[n]×m[n-1] + b[n]
"""

# Known m-sequence values
m_known = {
    2: 3, 3: 7, 4: 22, 5: 27, 6: 57, 7: 150, 8: 184, 9: 493,
    10: 1444, 11: 1921, 12: 3723, 13: 8342, 14: 16272, 15: 26989,
    16: 67760, 17: 138269, 18: 255121, 19: 564091, 20: 900329
}

# Known a[n] pattern
a_known = {
    3: 2, 4: 3, 5: 1, 6: 2, 7: 3, 8: 1, 9: 3, 10: 3, 11: 1,
    12: 2, 13: 2, 14: 2, 15: 2, 16: 3, 17: 2, 18: 2, 19: 2, 20: 2
}

# Computed b[n] values from known data
b_known = {
    3: 1, 4: 1, 5: 5, 6: 3, 7: -21, 8: 34, 9: -59, 10: -35,
    11: 477, 12: -119, 13: 896, 14: -412, 15: -5555, 16: -13207,
    17: 2749, 18: -21417, 19: 53849, 20: -227853
}

def get_a(n):
    """
    Get coefficient a[n] based on discovered pattern.

    Pattern:
    - n ∈ [3,8]: a[n] = [2,3,1][n%3] (with exceptions)
    - n = 9, 10: a[n] = 3
    - n = 11: a[n] = 1
    - n ≥ 12: mostly a[n] = 2, except a[16] = 3
    """
    if n in a_known:
        return a_known[n]

    # For unknown n, use the pattern
    if n <= 11:
        # Early pattern with mod-3 cycling
        if n == 9 or n == 10:
            return 3
        return [2, 3, 1][n % 3]
    elif n == 16:
        return 3
    else:
        # Default to 2 for later values
        # Note: This may need adjustment for n > 20
        return 2

def get_b(n):
    """
    Get offset b[n].

    For n ≤ 20: use known values
    For n > 20: would need to determine pattern or compute
    """
    if n in b_known:
        return b_known[n]
    else:
        # For unknown n, we'd need to find the pattern
        # Current limitation: cannot compute b[n] for n > 20 without more data
        raise ValueError(f"b[{n}] not known. Pattern for b[n] needs to be determined.")

def compute_m(n, m_cache=None):
    """
    Compute m[n] using recurrence relation: m[n] = a[n]×m[n-1] + b[n]

    Args:
        n: Index to compute
        m_cache: Dictionary to cache computed values (optional)

    Returns:
        m[n] value
    """
    if m_cache is None:
        m_cache = m_known.copy()

    if n in m_cache:
        return m_cache[n]

    if n < 2:
        raise ValueError("m[n] only defined for n ≥ 2")

    if n == 2:
        return 3

    # Compute recursively
    m_prev = compute_m(n-1, m_cache)
    a_n = get_a(n)
    b_n = get_b(n)

    m_n = a_n * m_prev + b_n
    m_cache[n] = m_n

    return m_n

def verify_known_values():
    """Verify that our recurrence correctly reproduces all known m values"""
    print("=" * 80)
    print("VERIFICATION OF RECURRENCE RELATION")
    print("=" * 80)
    print()
    print("Formula: m[n] = a[n]×m[n-1] + b[n]")
    print()

    m_cache = {2: 3}
    all_correct = True

    for n in range(3, 21):
        computed = compute_m(n, m_cache)
        expected = m_known[n]
        match = computed == expected
        all_correct = all_correct and match

        a_n = get_a(n)
        b_n = get_b(n)
        m_prev = m_cache[n-1]

        status = "✓" if match else "✗"
        print(f"m[{n:2d}] = {a_n}×{m_prev:7d} + {b_n:7d} = {computed:7d}  (expected: {expected:7d}) {status}")

    print()
    if all_correct:
        print("SUCCESS: All known values correctly reproduced!")
    else:
        print("ERROR: Some values do not match!")

    return all_correct

def display_pattern_summary():
    """Display summary of the discovered pattern"""
    print("\n" + "=" * 80)
    print("PATTERN SUMMARY")
    print("=" * 80)
    print()

    print("a[n] pattern:")
    print("  n ∈ [3,8]:  a[n] = [2,3,1][n%3]")
    print("  n = 9,10:   a[n] = 3")
    print("  n = 11:     a[n] = 1")
    print("  n ∈ [12,15]: a[n] = 2")
    print("  n = 16:     a[n] = 3")
    print("  n ≥ 17:     a[n] = 2 (observed)")
    print()

    print("b[n] observations:")
    print("  Early phase (n=3-7): Small values, some follow b[n] ≈ -2×b[n-1] + offset")
    print("  Middle phase (n=8-15): Moderate values, mixed signs")
    print("  Later phase (n≥16): Large values, alternating signs")
    print()

def analyze_a_pattern_extended():
    """Analyze a[n] pattern to predict future values"""
    print("\n" + "=" * 80)
    print("EXTENDED a[n] PATTERN ANALYSIS")
    print("=" * 80)
    print()

    print("Observed a[n] values by position:")
    print()
    print("n:    3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20")
    print("a[n]: 2  3  1  2  3  1  3  3  1  2  2  2  2  3  2  2  2  2")
    print("                           ^transition")
    print()

    # Count occurrences
    a_values = [a_known[n] for n in range(3, 21)]
    print(f"Distribution: 1={a_values.count(1)}, 2={a_values.count(2)}, 3={a_values.count(3)}")
    print()

    # Pattern by phase
    print("Phase-based pattern:")
    print("  Phase 1 (n=3-8):   Cycling [2,3,1] by n%3")
    print("  Phase 2 (n=9-11):  Transition [3,3,1]")
    print("  Phase 3 (n≥12):    Mostly 2, occasional 3")
    print()

    # Hypothesis for n > 20
    print("HYPOTHESIS for n > 20:")
    print("  Most likely: a[n] = 2 (default)")
    print("  Possible exceptions at specific n (similar to n=16)")
    print()

def generate_adj_from_m(n):
    """
    Generate adj[n] from m[n]
    adj[n] = 2^n - m[n]
    """
    m_n = compute_m(n)
    adj_n = (2**n) - m_n
    return adj_n

def main():
    print("M-SEQUENCE GENERATOR")
    print("Based on discovered recurrence: m[n] = a[n]×m[n-1] + b[n]")
    print()

    # Verify the recurrence
    verify_known_values()

    # Display pattern summary
    display_pattern_summary()

    # Analyze extended pattern
    analyze_a_pattern_extended()

    print("\n" + "=" * 80)
    print("USAGE NOTES")
    print("=" * 80)
    print()
    print("To extend beyond n=20:")
    print("1. Pattern for a[n] is mostly understood (likely continues as a[n]=2)")
    print("2. Pattern for b[n] needs to be determined")
    print("3. Once b[n] pattern is found, can generate m[n] for any n")
    print()
    print("Key limitation: b[n] values are currently stored, not computed")
    print("Next step: Find recurrence or formula for b[n]")
    print()

if __name__ == "__main__":
    main()
