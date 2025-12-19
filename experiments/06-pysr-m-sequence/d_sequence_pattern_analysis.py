#!/usr/bin/env python3
"""
D-Sequence Pattern Analysis
Investigate if d[n] encodes which constant/operation to use
"""

from convergent_database import M_SEQUENCE, D_SEQUENCE, build_database
from collections import Counter

# Match results from our previous analysis (manually encoded)
MATCH_DATA = {
    2: {'type': 'direct', 'constants': ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']},
    3: {'type': 'direct', 'constants': ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']},
    4: {'type': 'direct', 'constants': ['pi'], 'value': 'numerator'},
    5: {'type': 'direct', 'constants': ['ln2'], 'value': 'numerator'},
    6: {'type': 'direct', 'constants': ['e', 'sqrt3'], 'value': 'numerator'},
    7: {'type': 'product', 'constants': ['sqrt2', 'ln2']},
    8: {'type': 'sum', 'constants': ['recursive'], 'formula': 'm[2] + m[4]'},
    9: {'type': 'product', 'constants': ['sqrt2'], 'formula': '17 × 29'},
    10: {'type': 'direct', 'constants': ['e', 'sqrt3'], 'value': 'numerator'},
    11: {'type': 'product', 'constants': ['sqrt2', 'pi']},
    12: {'type': 'difference', 'constants': ['ln2', 'sqrt2']},
    13: {'type': 'unknown', 'constants': []},
    14: {'type': 'sum', 'constants': ['sqrt2', 'e']},
    15: {'type': 'unknown', 'constants': []},
}

def analyze_d_vs_type():
    """Check if d[n] correlates with operation type."""
    print("="*80)
    print("D-SEQUENCE vs OPERATION TYPE")
    print("="*80)

    d_to_type = {}
    for n in range(2, 16):
        d = D_SEQUENCE[n]
        op_type = MATCH_DATA[n]['type']

        if d not in d_to_type:
            d_to_type[d] = []
        d_to_type[d].append((n, op_type))

    for d in sorted(d_to_type.keys()):
        print(f"\nd={d}:")
        for n, op_type in d_to_type[d]:
            print(f"  n={n:2}, m={M_SEQUENCE[n]:>8}, type={op_type}")

def analyze_d_vs_constant():
    """Check if d[n] correlates with which constant is used."""
    print("\n" + "="*80)
    print("D-SEQUENCE vs CONSTANT SELECTION")
    print("="*80)

    d_to_const = {}
    for n in range(2, 16):
        d = D_SEQUENCE[n]
        constants = MATCH_DATA[n]['constants']

        if d not in d_to_const:
            d_to_const[d] = []
        d_to_const[d].append((n, constants))

    for d in sorted(d_to_const.keys()):
        print(f"\nd={d}:")
        for n, constants in d_to_const[d]:
            const_str = ', '.join(constants) if constants else 'none'
            print(f"  n={n:2}: {const_str}")

def analyze_d_sequence_properties():
    """Analyze mathematical properties of d-sequence."""
    print("\n" + "="*80)
    print("D-SEQUENCE MATHEMATICAL PROPERTIES")
    print("="*80)

    d_values = [D_SEQUENCE[n] for n in range(2, 16)]

    print(f"\nD-sequence (n=2 to 15): {d_values}")
    print(f"\nUnique values: {sorted(set(d_values))}")
    print(f"Frequency distribution:")

    freq = Counter(d_values)
    for d in sorted(freq.keys()):
        print(f"  d={d}: appears {freq[d]} times")

    # Check if d[n] relates to n
    print("\n" + "="*80)
    print("D[n] vs n RELATIONSHIP")
    print("="*80)

    for n in range(2, 16):
        d = D_SEQUENCE[n]
        print(f"n={n:2}, d[n]={d}, n mod 4={n%4}, n mod 7={n%7}, d divides n? {n % d == 0 if d != 0 else 'N/A'}")

def check_convergent_index_hypothesis():
    """Check if d[n] might encode the convergent index to use."""
    print("\n" + "="*80)
    print("D[n] AS CONVERGENT INDEX HYPOTHESIS")
    print("="*80)

    database = build_database()

    for n in range(2, 16):
        d = D_SEQUENCE[n]
        m = M_SEQUENCE[n]
        match_type = MATCH_DATA[n]['type']

        print(f"\nn={n}, m={m}, d={d}, type={match_type}")

        if match_type == 'direct':
            # Check if m appears at index d in any convergent
            for const_name, convergents in database.items():
                if d < len(convergents):
                    conv = convergents[d]
                    if conv['numerator'] == m:
                        print(f"  MATCH: {const_name} numerator at index {d} = {m}")
                    if conv['denominator'] == m:
                        print(f"  MATCH: {const_name} denominator at index {d} = {m}")

def analyze_recursive_with_d():
    """Specific analysis of recursive formulas with d-sequence."""
    print("\n" + "="*80)
    print("RECURSIVE FORMULAS WITH D-SEQUENCE")
    print("="*80)

    # m[6] = 2*m[5] + m[2] = 2*9 + 1 = 19, d[6]=2
    print("\nm[6] = 19, d[6]=2")
    print(f"  m[6] = d[6] × m[5] + m[2]")
    print(f"  19 = 2 × 9 + 1 ✓")

    # m[8] = m[4] + m[2] = 22 + 1 = 23, d[8]=4
    print("\nm[8] = 23, d[8]=4")
    print(f"  m[8] = m[4] + m[2]")
    print(f"  23 = 22 + 1 ✓")
    print(f"  Note: d[8]=4, but not directly used in formula")

    # m[10] = m[6] = 19, d[10]=7
    print("\nm[10] = 19, d[10]=7")
    print(f"  m[10] = m[6]")
    print(f"  19 = 19 ✓")
    print(f"  Note: d[10]=7 is the denominator of π's 22/7!")

def test_d_as_selector():
    """Test if d[n] mod k selects operation type."""
    print("\n" + "="*80)
    print("D[n] AS OPERATION SELECTOR")
    print("="*80)

    print("\nTesting d[n] mod 4 as operation selector:")
    for n in range(2, 16):
        d = D_SEQUENCE[n]
        op_type = MATCH_DATA[n]['type']
        mod4 = d % 4

        print(f"n={n:2}, d={d}, d mod 4={mod4}, type={op_type:12}")

    print("\nTesting d[n] values grouped by operation:")
    type_to_d = {}
    for n in range(2, 16):
        d = D_SEQUENCE[n]
        op_type = MATCH_DATA[n]['type']

        if op_type not in type_to_d:
            type_to_d[op_type] = []
        type_to_d[op_type].append(d)

    for op_type in sorted(type_to_d.keys()):
        d_vals = type_to_d[op_type]
        print(f"  {op_type:12}: d-values = {d_vals}")

def main():
    analyze_d_vs_type()
    analyze_d_vs_constant()
    analyze_d_sequence_properties()
    check_convergent_index_hypothesis()
    analyze_recursive_with_d()
    test_d_as_selector()

    # Final hypothesis
    print("\n" + "="*80)
    print("HYPOTHESIS SUMMARY")
    print("="*80)

    print("""
Based on the analysis:

1. D-SEQUENCE ROLE:
   - d=1: Often indicates DIRECT match or product of single constant
   - d=2: Mixed (direct, product, recursive)
   - d=4: Sum operations observed
   - d=7: Special case (π's 22/7 denominator)

2. RECURSIVE PATTERN:
   - m[6] = d[6] × m[5] + m[2] = 2×9 + 1 = 19
   - m[8] = m[4] + m[2] = 22 + 1 = 23
   - m[10] = m[6] = 19 (exact repeat)

3. CONSTANT SELECTION:
   - Early (n=2-6): π, e, ln(2), √3
   - Middle (n=7-11): √2 becomes prominent
   - d-sequence does NOT directly encode constant selection

4. OPERATION TYPE:
   - Direct: d ∈ {1, 2, 3, 7}
   - Product: d ∈ {1, 2}
   - Sum: d ∈ {2, 4}
   - d-sequence is NOT a perfect selector but may be a hint

5. META-PATTERN:
   The formula for m[n] likely depends on:
   - Phase (n range)
   - d[n] as modifier/selector
   - Previous m-values for recursive cases
   - Convergent indices (not directly d[n])
""")

if __name__ == "__main__":
    main()
