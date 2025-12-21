#!/usr/bin/env python3
"""
Deeper pattern analysis - looking at the relationship between n, a, b more carefully.
"""
import json

# Load all m-values
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

print("=" * 70)
print("DEEPER PATTERN ANALYSIS")
print("=" * 70)
print()

# Known generalized Fibonacci data
known = {
    62: {'a': 189, 'b': 92, 'k': 2},
    68: {'a': 101, 'b': 81, 'k': 6},
}

# Look at the ratio a/b more carefully
print("### Ratio Analysis ###")
for n, vals in known.items():
    a, b, k = vals['a'], vals['b'], vals['k']
    ratio = a / b
    print(f"n={n}: a/b = {a}/{b} = {ratio:.10f}")

# Ratio of ratios
r62 = 189 / 92
r68 = 101 / 81
ratio_of_ratios = r62 / r68
print(f"Ratio of ratios: {r62:.6f} / {r68:.6f} = {ratio_of_ratios:.6f}")
print()

# Check if there's a pattern in (a*b)
print("### Product Analysis ###")
for n, vals in known.items():
    a, b, k = vals['a'], vals['b'], vals['k']
    product = a * b
    print(f"n={n}: a*b = {product}")
    print(f"  n^2 = {n*n}, product/n^2 = {product/(n*n):.4f}")
    print(f"  n^3 = {n**3}, product/n^3 = {product/(n**3):.6f}")
    print(f"  2^n = {2**n}, product*2^(-n) = {product/(2**n):.10e}")
print()

# Check relationship to m-values
print("### Relationship to m[n] ###")
for n, vals in known.items():
    a, b, k = vals['a'], vals['b'], vals['k']
    m = m_seq[n-2]  # Index shift!
    d = d_seq[n-2]
    print(f"n={n}: m={m}, d={d}")
    print(f"  a*b = {a*b}, m/(a*b) = {m/(a*b):.6f}")
    
    # What are G_k and G_{k+1}?
    seq = [a, b]
    for i in range(10):
        seq.append(seq[-1] + seq[-2])
    Gk = seq[k]
    Gk1 = seq[k+1]
    print(f"  G_{k} = {Gk}, G_{k+1} = {Gk1}")
    print(f"  G_{k} * G_{k+1} = {Gk * Gk1}")
    print(f"  m[{n}] should be divisible by {Gk} and {Gk1}")
    print(f"  m[{n}] % G_{k} = {m % Gk}, m[{n}] % G_{k+1} = {m % Gk1}")
    print(f"  m[{n}] / (G_{k} * G_{k+1}) = {m / (Gk * Gk1):.6f}")
    print()

# Check relationship between a, b and n
print("### Relationship to n ###")
for n, vals in known.items():
    a, b, k = vals['a'], vals['b'], vals['k']
    print(f"n={n}:")
    print(f"  a = {a}, a/n = {a/n:.4f}, n-a = {n-a}")
    print(f"  b = {b}, b/n = {b/n:.4f}, n-b = {n-b}")
    print(f"  a+b = {a+b}, (a+b)/n = {(a+b)/n:.4f}")
    print(f"  (a+b) - 2n = {(a+b) - 2*n}")
print()

# Check prime relationships
print("### Prime Number Relationships ###")
def nth_prime(n):
    count = 0
    num = 2
    while True:
        is_prime = True
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
            if count == n:
                return num
        num += 1

for n, vals in known.items():
    a, b, k = vals['a'], vals['b'], vals['k']
    p_n_minus_2 = nth_prime(n-2)
    print(f"n={n}: p_{n-2} = {p_n_minus_2}")
    print(f"  a+b = {a+b}")
    if a + b == p_n_minus_2:
        print(f"  a+b = p_{n-2} ✓")
    else:
        print(f"  a+b ≠ p_{n-2}")
    print()

# For n=71
print("### Prediction for n=71 ###")
n = 71
k = 2 * (n - 59) // 3  # k = 2*12/3 = 8
print(f"n=71: k = 2(71-59)/3 = {k}")
print(f"p_{n-2} = p_69 = {nth_prime(69)}")
print()

# Extrapolate using various methods
print("### Extrapolation Methods ###")

# Method 1: Linear
a_71_lin = 189 + (-88/6) * (71 - 62)
b_71_lin = 92 + (-11/6) * (71 - 62)
print(f"Linear: a={a_71_lin:.2f}, b={b_71_lin:.2f}")

# Method 2: Ratio-based
# If a/b follows a pattern...
# r62 = 2.054..., r68 = 1.247...
# delta_r = -0.807 per 6 n, so -0.404 per 3 n
r_71 = r68 + (r68 - r62) * (71 - 68) / (68 - 62)
print(f"Ratio extrapolation: a/b = {r_71:.4f}")

# Method 3: Product-based
# p62 = 17388, p68 = 8181
# Product decreases by (17388-8181)/6 = 1534.5 per n
p_71 = 8181 + (8181 - 17388) * (71 - 68) / (68 - 62)
print(f"Product extrapolation: a*b = {p_71:.2f}")

print()

# Check for continued fraction connection
print("### Continued Fraction Investigation ###")
# 189/92 as CF
from math import floor
def to_cf(num, den, max_terms=10):
    cf = []
    for _ in range(max_terms):
        if den == 0:
            break
        q = num // den
        cf.append(q)
        num, den = den, num - q * den
    return cf

cf_62 = to_cf(189, 92)
cf_68 = to_cf(101, 81)
print(f"CF(189/92) = {cf_62}")
print(f"CF(101/81) = {cf_68}")

# What about the sum a+b?
cf_281 = to_cf(281, 92)  # 281/92
cf_182 = to_cf(182, 81)  # 182/81
print(f"CF(281/92) = {cf_281}")
print(f"CF(182/81) = {cf_182}")

print()
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
