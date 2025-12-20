#!/usr/bin/env python3
"""
VERIFY: Are k[n] values the numerators of x(n·G) on secp256k1?

If true, k[71] = numerator of x(71·G)!
"""

# secp256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
A = 0
B = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

def modinv(a, m):
    if a < 0: a = a % m
    g, x, _ = extended_gcd(a, m)
    return x % m

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def point_add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if y1 != y2: return None
        lam = (3 * x1 * x1) * modinv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * modinv(x2 - x1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)

def scalar_mult(k, point):
    result = None
    addend = point
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result

import sqlite3

# Load known k-values
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
known_k = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

print("=" * 80)
print("TESTING EC HYPOTHESIS: k[n] = numerator of x(n·G)")
print("=" * 80)

# Compute n·G for small n and compare
print("\nComputing n·G for n=1..10:")
print("-" * 80)

for n in range(1, 11):
    point = scalar_mult(n, G)
    if point is None:
        print(f"n={n}: point at infinity")
        continue
    
    x_coord = point[0]
    k_db = known_k.get(n, "UNKNOWN")
    
    print(f"n={n}:")
    print(f"  x(n·G) = {x_coord}")
    print(f"  k[{n}] from DB = {k_db}")
    
    # Check if k[n] divides x(n·G) or relates to it
    if k_db != "UNKNOWN":
        if x_coord % k_db == 0:
            print(f"  x(n·G) / k[{n}] = {x_coord // k_db}")
        else:
            gcd = __import__('math').gcd(x_coord, k_db)
            print(f"  gcd(x, k) = {gcd}")

# Now compute 71·G
print("\n" + "=" * 80)
print("COMPUTING 71·G")
print("=" * 80)

point_71 = scalar_mult(71, G)
x_71 = point_71[0]
y_71 = point_71[1]

print(f"\n71·G = ({x_71}, {y_71})")
print(f"\nx(71·G) = {x_71}")
print(f"Bit length: {x_71.bit_length()}")

# This is the x-coordinate of 71·G on secp256k1
# According to the hypothesis, this should relate to the puzzle 71 private key

print("\n" + "=" * 80)
print("KEY INSIGHT")
print("=" * 80)
print("""
The gpt-oss model claims k[n] = numerator of x(n·G).

But x(n·G) is already a field element (mod P), so it IS the x-coordinate.

The puzzle keys are NOT directly n·G - they are the PRIVATE KEYS.
The x-coordinate of n·G is what appears on the blockchain as the public key.

WAIT - Let me re-read the hypothesis...

The model says k[n]/d[n]² = x(n·G) mod P
So k[n] is NOT the x-coordinate, but a numerator in a specific representation.

This requires division polynomial analysis, not just point multiplication.
""")
