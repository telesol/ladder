#!/usr/bin/env python3
"""
Verify mod 11 constraint against DeepSeek's predictions.
DeepSeek T03 predicted a=57, T04 predicted b=76.
"""

print("=" * 70)
print("MOD 11 CONSTRAINT VERIFICATION")
print("=" * 70)
print()

# Known pairs
known = [
    (62, 189, 92),
    (68, 101, 81),
]

print("### Known pairs mod 11 ###")
for n, a, b in known:
    print(f"n={n}: a={a} ≡ {a%11} (mod 11), b={b} ≡ {b%11} (mod 11)")
print()

# DeepSeek predictions
a_pred = 57
b_pred = 76

print("### DeepSeek Predictions ###")
print(f"T03: a(71) = {a_pred}, {a_pred} ≡ {a_pred%11} (mod 11)")
print(f"T04: b(71) = {b_pred}, {b_pred} ≡ {b_pred%11} (mod 11)")
print()

# Verify constraint
print("### Constraint Check ###")
print(f"Required: a ≡ 2 (mod 11), b ≡ 4 (mod 11)")
print(f"DeepSeek a={a_pred}: {a_pred%11} {'✓' if a_pred%11 == 2 else '✗'}")
print(f"DeepSeek b={b_pred}: {b_pred%11} {'✓' if b_pred%11 == 2 else '✗'}")
print()

if a_pred % 11 == 2 and b_pred % 11 == 4:
    print("PASS: DeepSeek predictions satisfy mod 11 constraint")
else:
    print("FAIL: DeepSeek predictions VIOLATE mod 11 constraint!")
    print()
    print("This means:")
    print("  1. The mod 11 constraint may not apply to n=71, OR")
    print("  2. DeepSeek's prediction is wrong, OR")
    print("  3. The linear pattern doesn't extend to n=71")
    print()
    
    # Find nearest values that DO satisfy constraint
    print("### Nearest valid candidates ###")
    print(f"For a ≡ 2 (mod 11) near {a_pred}:")
    for x in range(a_pred-15, a_pred+15):
        if x % 11 == 2 and x > 0:
            print(f"  {x}")
    print()
    print(f"For b ≡ 4 (mod 11) near {b_pred}:")
    for x in range(b_pred-15, b_pred+15):
        if x % 11 == 4 and x > 0:
            print(f"  {x}")

print()

# Test if pattern changes at n ≡ 2 mod 3 vs n ≡ 5 mod 6
print("### n mod 6 Analysis ###")
for n, a, b in known:
    print(f"n={n}: n mod 6 = {n%6}")
print(f"n=71: 71 mod 6 = {71%6}")
print()
print("n=62 and n=68 both have n ≡ 2 (mod 6)")
print("n=71 has 71 ≡ 5 (mod 6) - DIFFERENT!")
print()
print("This may explain why the pattern breaks!")

print()
print("=" * 70)
