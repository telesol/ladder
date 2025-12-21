#!/usr/bin/env python3
"""
Analyze the (a, b) initial pair pattern for generalized Fibonacci.
We have:
- n=62: (a, b) = (189, 92) where 281=G_2, 373=G_3
- n=68: (a, b) = (101, 81) where 1153=G_6, 1861=G_7

Goal: Find (a, b) for n=71 where G_8, G_9 appear.
"""

# Known data points
data = [
    (62, 189, 92, 2, 3),   # (n, a, b, k, k+1)
    (68, 101, 81, 6, 7),
]

print("=" * 70)
print("ANALYSIS OF (a, b) INITIAL PAIRS FOR GENERALIZED FIBONACCI")
print("=" * 70)
print()

# Basic arithmetic patterns
print("### Basic Values ###")
for n, a, b, k1, k2 in data:
    print(f"n={n}: (a,b) = ({a}, {b})")
    print(f"  a + b = {a+b}")
    print(f"  a - b = {a-b}")
    print(f"  a * b = {a*b}")
    print(f"  a / b = {a/b:.6f}")
    print(f"  a % b = {a % b}")
    print(f"  b % a = {b % a}")
    print(f"  a mod 11 = {a % 11}, b mod 11 = {b % 11}")
    print(f"  Fib indices used: k={k1}, k+1={k2}")
    print()

# Linear interpolation analysis
print("### Linear Interpolation ###")
# From (62, 189) to (68, 101): slope = (101-189)/(68-62) = -88/6 = -44/3
# a(n) = 189 + (-44/3)(n - 62) = 189 - 44(n-62)/3
# For n=71: a(71) = 189 - 44*9/3 = 189 - 132 = 57

a_62, a_68 = 189, 101
slope_a = (a_68 - a_62) / (68 - 62)
print(f"a-slope: ({a_68} - {a_62}) / (68 - 62) = {slope_a:.4f}")
a_71_linear = a_62 + slope_a * (71 - 62)
print(f"a(71) linear: {a_71_linear:.4f}")

b_62, b_68 = 92, 81
slope_b = (b_68 - b_62) / (68 - 62)
print(f"b-slope: ({b_68} - {b_62}) / (68 - 62) = {slope_b:.4f}")
b_71_linear = b_62 + slope_b * (71 - 62)
print(f"b(71) linear: {b_71_linear:.4f}")

print()

# Check quadratic fit
print("### Quadratic Fit (need 3rd point) ###")
# With only 2 points, quadratic is underdetermined
# But we can look at the changes
delta_n = 68 - 62
delta_a = a_68 - a_62  # -88
delta_b = b_68 - b_62  # -11
print(f"Δn = {delta_n}")
print(f"Δa = {delta_a} (change per Δn=6: {delta_a/6:.4f})")
print(f"Δb = {delta_b} (change per Δn=6: {delta_b/6:.4f})")

print()

# Mod 11 constraint check
print("### Mod 11 Constraint ###")
print("Both pairs satisfy (a, b) ≡ (2, 4) mod 11")
print()
print("Candidates for a(71) that satisfy a ≡ 2 (mod 11):")
print("Near linear prediction (57):", end=" ")
candidates_a = [x for x in range(30, 80) if x % 11 == 2]
print(candidates_a)
print()
print("Candidates for b(71) that satisfy b ≡ 4 (mod 11):")
print("Near linear prediction (75.5):", end=" ")
candidates_b = [x for x in range(50, 100) if x % 11 == 4]
print(candidates_b)

print()

# Check specific candidate combinations
print("### Testing Candidate Pairs ###")
print("For n=71, k=8, k+1=9 (from formula k=2(n-59)/3)")
print()

def gen_fib(a, b, k):
    """Generate k-th term of generalized Fibonacci G(a,b)"""
    seq = [a, b]
    for i in range(k - 1):
        seq.append(seq[-1] + seq[-2])
    return seq

# Test candidate pairs
test_pairs = []
for a in candidates_a:
    for b in candidates_b:
        if a > b and a > 0 and b > 0:  # a should be larger based on pattern
            test_pairs.append((a, b))

print(f"Testing {len(test_pairs)} candidate pairs with a > b...")
print()

# Generate what G_8 and G_9 would be for each
for a, b in test_pairs[:15]:  # First 15
    seq = gen_fib(a, b, 10)
    G8, G9 = seq[7], seq[8]  # 0-indexed, so G_8 is seq[7]
    # Actually wait - the formula k=2(n-59)/3 gives index in the sequence
    # For n=62: k=2 means G_2 and G_3 (using 0-indexed would be seq[1], seq[2])
    # Let me recalculate
    # G_0 = a, G_1 = b, G_2 = a+b, G_3 = a+2b, etc.
    # For n=62: 281 = G_2 = a + b = 189 + 92 = 281 ✓
    # For n=68: 1153 = G_6 = ?
    # Let's compute: G(101,81): 101, 81, 182, 263, 445, 708, 1153
    # So G_0=101, G_1=81, G_2=182, G_3=263, G_4=445, G_5=708, G_6=1153 ✓
    # So for n=71 with k=8: G_8 and G_9
    seq2 = [a, b]
    for i in range(10):
        seq2.append(seq2[-1] + seq2[-2])
    G8 = seq2[8]  # G_8 at index 8
    G9 = seq2[9]  # G_9 at index 9
    print(f"({a}, {b}): G_8={G8}, G_9={G9}, product={G8*G9}")

print()

# Check the a+b = p_{n-2} pattern
print("### a + b = p_{n-2} Pattern Check ###")
# For n=62: a+b=281 = p_60 (60th prime) ✓
# For n=68: a+b=182 = ? Not prime
print("n=62: a+b = 189+92 = 281 = p_60 ✓")
print("n=68: a+b = 101+81 = 182 = 2×7×13 (not prime)")
print("Pattern does NOT hold universally")

print()

# Check n mod 3 pattern
print("### n mod 3 Pattern ###")
for n, a, b, k1, k2 in data:
    print(f"n={n}: n mod 3 = {n % 3}, n mod 6 = {n % 6}")
print(f"n=71: 71 mod 3 = {71 % 3}, 71 mod 6 = {71 % 6}")

print()

# Prime factorization relationship
print("### Prime Factorization Patterns ###")
# 189 = 3^3 × 7 = 27 × 7
# 92 = 2^2 × 23 = 4 × 23
# 101 = prime
# 81 = 3^4
print("n=62: a=189=3³×7, b=92=2²×23")
print("n=68: a=101=prime, b=81=3⁴")
print()
print("Power of 3 in a: 189=3³×7 (power=3), 101 (power=0)")
print("Power of 3 in b: 92 (power=0), 81=3⁴ (power=4)")
print("Sum of 3-powers: 3+0=3, 0+4=4")
print("Pattern: sum of 3-powers increases by 1?")
print("For n=71: sum of 3-powers should be 5?")

print()

# Exploring 3-power pattern
print("### 3-Power Pattern Exploration ###")
print("If total 3-power = 5 for n=71:")
print("Options: (a has 3^5, b has 3^0) -> a divisible by 243")
print("         (a has 3^4, b has 3^1) -> a=81×?, b=3×?")
print("         (a has 3^3, b has 3^2) -> a=27×?, b=9×?")
print("         (a has 3^2, b has 3^3) -> a=9×?, b=27×?")
print("         (a has 3^1, b has 3^4) -> a=3×?, b=81×?")
print("         (a has 3^0, b has 3^5) -> b divisible by 243")

print()
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
