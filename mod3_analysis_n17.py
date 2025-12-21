#!/usr/bin/env python3
"""
Mod-3 recursion analysis around n=17
From MISTRAL_SYNTHESIS: k[n] = 9 × k[n-3] + offset for n≥10
"""

import json

# Extended k values
k_values = {
    1: 0x1,
    2: 0x3,
    3: 0x7,
    4: 0x8,
    5: 0x15,
    6: 0x31,
    7: 0x4c,
    8: 0xe0,
    9: 0x1d3,
    10: 0x202,
    11: 0x483,
    12: 0xa7b,
    13: 0x1460,
    14: 0x2930,
    15: 0x68f3,
    16: 0xc936,
    17: 0x1764f,
    18: 0x3080d,
    19: 0x5749f,
    20: 0xd2c55,
}

def check_mod3_recursion():
    """Check if k[n] = 9 × k[n-3] + offset"""
    print("MOD-3 RECURSION: k[n] = 9 × k[n-3] + offset")
    print("=" * 80)

    for n in range(10, 21):
        if n in k_values and n-3 in k_values:
            k_n = k_values[n]
            k_n_minus_3 = k_values[n-3]

            expected = 9 * k_n_minus_3
            offset = k_n - expected

            # Check if offset is small relative to k[n]
            ratio = abs(offset) / k_n * 100

            print(f"\nn={n}:")
            print(f"  k[{n}] = {k_n}")
            print(f"  9 × k[{n-3}] = {expected}")
            print(f"  offset = {offset:+d}")
            print(f"  offset/k[{n}] = {ratio:.4f}%")

            # Check offset magnitude
            if abs(offset) < k_n * 0.01:  # Less than 1%
                print(f"  ✓ Small offset (<1%)")
            else:
                print(f"  ⚠️  Large offset (≥1%)")

def check_offset_pattern():
    """Check if offsets follow any pattern"""
    print("\n" + "=" * 80)
    print("OFFSET PATTERN ANALYSIS")
    print("=" * 80)

    offsets = []
    for n in range(10, 21):
        if n in k_values and n-3 in k_values:
            k_n = k_values[n]
            k_n_minus_3 = k_values[n-3]
            offset = k_n - 9 * k_n_minus_3
            offsets.append((n, offset))

    print("\nBefore n=17:")
    for n, offset in offsets:
        if n < 17:
            print(f"  offset[{n}] = {offset:+10d}")

    print("\nAt n=17:")
    for n, offset in offsets:
        if n == 17:
            print(f"  offset[{n}] = {offset:+10d}")

    print("\nAfter n=17:")
    for n, offset in offsets:
        if n > 17:
            print(f"  offset[{n}] = {offset:+10d}")

    # Check offset growth
    print("\nOffset growth rate:")
    for i in range(1, len(offsets)):
        n_prev, offset_prev = offsets[i-1]
        n_curr, offset_curr = offsets[i]

        if offset_prev != 0:
            growth = abs(offset_curr) / abs(offset_prev)
            print(f"  |offset[{n_curr}]| / |offset[{n_prev}]| = {growth:.4f}")

def check_mod3_coefficient_change():
    """Check if coefficient changes from 9 to something else"""
    print("\n" + "=" * 80)
    print("COEFFICIENT OPTIMIZATION AROUND N=17")
    print("=" * 80)

    # Test different coefficients
    for n in [14, 15, 16, 17, 18, 19, 20]:
        if n in k_values and n-3 in k_values:
            k_n = k_values[n]
            k_n_minus_3 = k_values[n-3]

            # Find best integer coefficient
            best_coef = round(k_n / k_n_minus_3)

            # Test coefficients around 9
            print(f"\nn={n}:")
            for coef in [8, 9, 10]:
                expected = coef * k_n_minus_3
                offset = k_n - expected
                ratio = abs(offset) / k_n * 100

                marker = "←" if coef == best_coef else ""
                print(f"  {coef} × k[{n-3}] + {offset:+10d} = k[{n}], "
                      f"offset/k = {ratio:.4f}% {marker}")

def main():
    check_mod3_recursion()
    check_offset_pattern()
    check_mod3_coefficient_change()

if __name__ == '__main__':
    main()
