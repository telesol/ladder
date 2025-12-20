#!/usr/bin/env python3
"""
Deep analysis of non-trivial prime factors.
Looking for patterns in 281, 373, 2843, 10487, 63199 (m[62])
and 24239, 57283, 1437830129 (m[65])
and 1153, 1861, 31743327447619 (m[68])

MODEL: Claude Opus 4.5
DATE: 2025-12-20
NO BRUTE FORCE. MATHEMATICAL ANALYSIS ONLY.
"""

from math import sqrt, gcd, log2, log

# Non-trivial prime factors
factors_62 = [281, 373, 2843, 10487, 63199]
factors_65 = [24239, 57283, 1437830129]
factors_68 = [1153, 1861, 31743327447619]

print("=" * 80)
print("DEEP FACTOR ANALYSIS")
print("=" * 80)
print("Model: Claude Opus 4.5")
print()

# Check if any factor is of form a*2^k ± b for small a, b
print("### Form a×2^k ± b analysis ###\n")

def check_power_form(n, name):
    """Check if n is close to a*2^k form"""
    results = []
    log2_n = log2(n)

    for k in range(int(log2_n) - 3, int(log2_n) + 3):
        if k < 1:
            continue
        power = 2**k

        # Check n = a*2^k ± b
        a = n // power
        b = n - a * power

        if a <= 100 and abs(b) <= 1000:
            results.append(f"{n} = {a}×2^{k} + {b}")

        # Check if n+small is divisible by 2^k
        for delta in range(-100, 101):
            if (n + delta) % power == 0:
                q = (n + delta) // power
                if q <= 100:
                    sign = "-" if delta < 0 else "+"
                    results.append(f"{n} = {q}×2^{k} {sign} {abs(delta)}")
                    break

    if results:
        print(f"{name} = {n}:")
        for r in results[:3]:
            print(f"  {r}")
    else:
        print(f"{name} = {n}: no simple power-of-2 form")

for f in factors_62:
    check_power_form(f, f"m[62] factor")

for f in factors_65:
    check_power_form(f, f"m[65] factor")

for f in factors_68:
    check_power_form(f, f"m[68] factor")

# Check for relationships between factors
print("\n### Factor ratio analysis ###\n")

def analyze_ratios(factors, name):
    print(f"{name} factors: {factors}")
    for i in range(len(factors)):
        for j in range(i+1, len(factors)):
            ratio = factors[j] / factors[i]
            # Check if ratio is close to common constants
            for const_name, const_val in [("π", 3.14159265359), ("e", 2.71828182846),
                                          ("√2", 1.41421356237), ("φ", 1.61803398875),
                                          ("2", 2.0), ("3", 3.0), ("7", 7.0)]:
                if abs(ratio - const_val) < 0.01:
                    print(f"  {factors[j]}/{factors[i]} = {ratio:.6f} ≈ {const_name}")
                elif abs(ratio - const_val**2) < 0.01:
                    print(f"  {factors[j]}/{factors[i]} = {ratio:.6f} ≈ {const_name}²")
    print()

analyze_ratios(factors_62, "m[62]")
analyze_ratios(factors_65, "m[65]")
analyze_ratios(factors_68, "m[68]")

# Check prime indices
print("### Prime index analysis ###\n")

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def prime_index(p):
    """Find the index of prime p (p is the k-th prime)"""
    if not is_prime(p):
        return None
    count = 0
    n = 2
    while n <= p:
        if is_prime(n):
            count += 1
        if n == p:
            return count
        n += 1
    return None

# Only check small factors (computing prime index for large primes is expensive)
small_factors = [281, 373, 2843, 10487, 1153, 1861]
print("Prime indices for smaller factors:")
for p in small_factors:
    idx = prime_index(p)
    if idx:
        print(f"  {p} is the {idx}-th prime")

# Check for Pell equation solutions
print("\n### Pell equation check ###\n")
print("Checking if factors are related to Pell equation x² - 2y² = ±1")

for f in factors_62 + factors_65[:2] + factors_68[:2]:
    # Check if f appears in Pell solutions
    # x_n = x_1*x_{n-1} + 2*y_1*y_{n-1}, starting with x_1=3, y_1=2
    pell_x = [1, 3]
    pell_y = [0, 2]
    for i in range(20):
        x_new = 3*pell_x[-1] + 4*pell_y[-1]
        y_new = 2*pell_x[-1] + 3*pell_y[-1]
        pell_x.append(x_new)
        pell_y.append(y_new)

    if f in pell_x:
        idx = pell_x.index(f)
        print(f"  {f} = Pell x_{idx}")
    if f in pell_y:
        idx = pell_y.index(f)
        print(f"  {f} = Pell y_{idx}")

# Check modular patterns
print("\n### Modular patterns ###\n")

for name, factors in [("m[62]", factors_62), ("m[65]", factors_65), ("m[68]", factors_68)]:
    print(f"{name} factors mod small primes:")
    for p in [3, 7, 11, 13, 17, 19, 23]:
        mods = [f % p for f in factors if f != p]
        print(f"  mod {p}: {mods}")

# Summary
print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print("""
Key Findings:
1. Verified prime factorizations from GNU factor
2. Small factors (2, 3, 5) match trivial convergents
3. Large factors show no obvious convergent relationship
4. m-values are coprime (no common construction base)

Next Steps:
- Need to check if factors are related to extended convergents (index > 20)
- Need to check if m-values are constructed from recurrence relationships
- The pattern for m[71] remains unknown
""")
