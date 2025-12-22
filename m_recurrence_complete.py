#!/usr/bin/env python3
"""
COMPLETE m-SEQUENCE RECURRENCE RELATION
Based on findings: m[n] = a[n]*m[n-1] + b[n]
where a[n] follows a pattern and b[n] needs to be determined
"""

import numpy as np

# Known m-sequence
m_seq = {
    2: 3, 3: 7, 4: 22, 5: 27, 6: 57, 7: 150, 8: 184, 9: 493,
    10: 1444, 11: 1921, 12: 3723, 13: 8342, 14: 16272, 15: 26989,
    16: 67760, 17: 138269, 18: 255121, 19: 564091, 20: 900329
}

def determine_a_pattern():
    """Determine the pattern for a[n]"""
    print("=" * 80)
    print("PATTERN FOR a[n] IN: m[n] = a[n]*m[n-1] + b[n]")
    print("=" * 80)
    print()

    # Extract a[n] from the observed data
    a_data = {
        3: 2, 4: 3, 5: 1, 6: 2, 7: 3, 8: 1, 9: 3, 10: 3, 11: 1,
        12: 2, 13: 2, 14: 2, 15: 2, 16: 3, 17: 2, 18: 2, 19: 2, 20: 2
    }

    # Analyze by n mod 3
    print("Pattern by n mod 3:")
    for mod in range(3):
        ns = [n for n in range(3, 21) if n % 3 == mod]
        vals = [a_data[n] for n in ns]
        print(f"  n ≡ {mod} (mod 3): n = {ns}")
        print(f"                    a = {vals}")

        # Check if there's a transition point
        for i in range(len(vals) - 1):
            if vals[i] != vals[i+1]:
                transition_n = ns[i+1]
                print(f"    → Transition at n={transition_n}: {vals[i]} → {vals[i+1]}")
        print()

    # Look for the pattern
    print("Hypothesis: a[n] depends on n and position in sequence")
    print()

    # Early pattern (n <= 11)
    print("EARLY PHASE (n ≤ 11):")
    for n in range(3, 12):
        print(f"  n={n:2d}: n%3={n%3}, a[n]={a_data[n]}")

    pattern_early = [
        (0, 2),  # n%3=0 → a=2
        (1, 3),  # n%3=1 → a=3
        (2, 1),  # n%3=2 → a=1
    ]
    print("\nEarly pattern (n=3..11): a[n] = [2,3,1][n%3]")
    print("  Verification:")
    for n in range(3, 12):
        predicted = [2, 3, 1][n % 3]
        actual = a_data[n]
        match = "✓" if predicted == actual else "✗"
        print(f"    n={n:2d}: predicted={predicted}, actual={actual} {match}")

    # Later pattern (n >= 12)
    print("\nLATER PHASE (n ≥ 12):")
    for n in range(12, 21):
        print(f"  n={n:2d}: n%3={n%3}, a[n]={a_data[n]}")

    # Check if pattern stabilizes to a=2 with exceptions
    print("\nLater pattern observation:")
    print("  Most values are a=2")
    exceptions = [(n, a_data[n]) for n in range(12, 21) if a_data[n] != 2]
    print(f"  Exceptions: {exceptions}")

    # Check the exception at n=16
    print("\nException analysis:")
    print("  n=16: a[16]=3")
    print(f"    16 % 3 = {16 % 3}")
    print(f"    16 % 4 = {16 % 4}")
    print(f"    16 % 6 = {16 % 6}")

def determine_b_pattern():
    """Analyze the pattern for b[n]"""
    print("\n" + "=" * 80)
    print("PATTERN FOR b[n] IN: m[n] = a[n]*m[n-1] + b[n]")
    print("=" * 80)
    print()

    # Extract b[n]
    a_data = {
        3: 2, 4: 3, 5: 1, 6: 2, 7: 3, 8: 1, 9: 3, 10: 3, 11: 1,
        12: 2, 13: 2, 14: 2, 15: 2, 16: 3, 17: 2, 18: 2, 19: 2, 20: 2
    }

    b_data = {}
    for n in range(3, 21):
        b_data[n] = m_seq[n] - a_data[n] * m_seq[n-1]

    print("Computed b[n] values:")
    for n in range(3, 21):
        print(f"  b[{n:2d}] = {b_data[n]:7d}")

    # Check if b[n] relates to other values
    print("\nCheck if b[n] relates to m values, 2^n, or other patterns:")
    for n in range(3, 21):
        b = b_data[n]

        # Check relation to 2^n
        power = 2**n
        ratio_power = b / power if power != 0 else 0

        # Check relation to m[n-2], m[n-3], etc.
        relations = []
        for k in range(2, n-1):
            if k in m_seq:
                ratio = b / m_seq[k] if m_seq[k] != 0 else 0
                if 0.01 < abs(ratio) < 5:
                    relations.append(f"m[{k}]×{ratio:.2f}")

        # Check if b is close to ±m[k] for some k
        close_matches = []
        for k in range(2, n):
            if k in m_seq:
                if abs(b - m_seq[k]) < 10:
                    close_matches.append(f"+m[{k}]")
                if abs(b + m_seq[k]) < 10:
                    close_matches.append(f"-m[{k}]")

        print(f"  n={n:2d}: b={b:7d}, 2^n×{ratio_power:.4f}, close: {', '.join(close_matches[:2]) if close_matches else 'none'}")

def test_complete_formula():
    """Test if we can reconstruct m-sequence using the discovered patterns"""
    print("\n" + "=" * 80)
    print("RECONSTRUCTION TEST")
    print("=" * 80)
    print()

    # Use the discovered a[n] pattern
    def get_a(n):
        """Get a[n] based on discovered pattern"""
        if n <= 11:
            # Early pattern: cycles [2,3,1] based on n%3
            return [2, 3, 1][n % 3]
        elif n == 16:
            return 3
        else:
            return 2

    # Extract actual b[n] values
    b_lookup = {}
    for n in range(3, 21):
        a_n = get_a(n)
        b_lookup[n] = m_seq[n] - a_n * m_seq[n-1]

    print("Testing reconstruction with pattern-based a[n]:")
    print()

    m_reconstructed = {2: 3}  # Start with m[2]=3

    for n in range(3, 21):
        a_n = get_a(n)
        b_n = b_lookup[n]  # Use actual b for now

        m_reconstructed[n] = a_n * m_reconstructed[n-1] + b_n

        actual = m_seq[n]
        reconstructed = m_reconstructed[n]
        match = "✓" if reconstructed == actual else "✗"

        print(f"  m[{n:2d}] = {a_n}×m[{n-1:2d}] + {b_n:7d} = {a_n}×{m_reconstructed[n-1]:7d} + {b_n:7d} = {reconstructed:7d} (actual: {actual:7d}) {match}")

def analyze_b_recurrence():
    """Check if b[n] itself follows a recurrence"""
    print("\n" + "=" * 80)
    print("RECURRENCE FOR b[n]")
    print("=" * 80)
    print()

    # Get b values
    a_data = {
        3: 2, 4: 3, 5: 1, 6: 2, 7: 3, 8: 1, 9: 3, 10: 3, 11: 1,
        12: 2, 13: 2, 14: 2, 15: 2, 16: 3, 17: 2, 18: 2, 19: 2, 20: 2
    }

    b_data = {}
    for n in range(3, 21):
        b_data[n] = m_seq[n] - a_data[n] * m_seq[n-1]

    print("Looking for patterns in b[n]:")
    print()

    # Check differences
    print("First differences: Δb[n] = b[n] - b[n-1]")
    for n in range(4, 21):
        diff = b_data[n] - b_data[n-1]
        print(f"  Δb[{n:2d}] = {diff:7d}")

    # Check if b[n] can be expressed in terms of previous b values
    print("\nTest: b[n] = c*b[n-1] + d")
    for n in range(4, 21):
        for c in [-2, -1, 0, 1, 2]:
            d = b_data[n] - c * b_data[n-1]
            if abs(d) < 100:
                print(f"  b[{n:2d}] = {c}×b[{n-1:2d}] + {d:5d} = {c}×{b_data[n-1]:7d} + {d:5d}")
                break

def main():
    print("COMPLETE RECURRENCE RELATION ANALYSIS FOR m-SEQUENCE")
    print("Formula: m[n] = a[n]×m[n-1] + b[n]")
    print()

    determine_a_pattern()
    determine_b_pattern()
    test_complete_formula()
    analyze_b_recurrence()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
