#!/usr/bin/env python3
"""
Deep EC Hypothesis Testing
Test if adj_n relates to EC operations using actual key values
"""

import sqlite3
import hashlib

# secp256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def modinv(a, m):
    if a < 0:
        a = a % m
    g, x, _ = extended_gcd(a, m)
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    return gcd, y1 - (b // a) * x1, x1

def ec_add(x1, y1, x2, y2):
    if x1 is None:
        return x2, y2
    if x2 is None:
        return x1, y1
    if x1 == x2:
        if y1 != y2:
            return None, None
        if y1 == 0:
            return None, None
        lam = (3 * x1 * x1 * modinv(2 * y1, P)) % P
    else:
        lam = ((y2 - y1) * modinv(x2 - x1, P)) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return x3, y3

def ec_mul(k, gx, gy):
    rx, ry = None, None
    ax, ay = gx, gy
    while k:
        if k & 1:
            rx, ry = ec_add(rx, ry, ax, ay)
        ax, ay = ec_add(ax, ay, ax, ay)
        k >>= 1
    return rx, ry

def load_keys():
    conn = sqlite3.connect("db/kh.db")
    cur = conn.cursor()
    cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
    rows = cur.fetchall()
    conn.close()
    return {r[0]: int(r[1], 16) for r in rows}

def compute_adj(k, n):
    return k[n] - 2 * k[n-1]

def main():
    keys = load_keys()
    k = [0] + [keys.get(i, 0) for i in range(1, 71)]

    print("=" * 70)
    print("DEEP EC HYPOTHESIS TESTING")
    print("=" * 70)

    # Test 1: adj_n vs x(k_{n-1} * G)
    print("\n=== Test 1: adj_n vs x(k_{n-1} * G) mod 2^n ===")
    for n in range(2, 16):
        adj = compute_adj(k, n)
        x, y = ec_mul(k[n-1], GX, GY)
        if x:
            x_mod = x % (1 << n)
            diff = abs(adj - x_mod)
            ratio = x_mod / adj if adj != 0 else 0
            print(f"n={n:2d}: adj={adj:10d}, x(k[{n-1}]*G) mod 2^n = {x_mod:10d}, diff={diff:10d}, ratio={ratio:.4f}")

    # Test 2: adj_n vs x(k_n * G) - y(k_{n-1} * G)
    print("\n=== Test 2: adj_n vs (x(k_n*G) - x(k_{n-1}*G)) mod 2^n ===")
    for n in range(2, 16):
        adj = compute_adj(k, n)
        x_n, _ = ec_mul(k[n], GX, GY)
        x_prev, _ = ec_mul(k[n-1], GX, GY)
        if x_n and x_prev:
            diff_x = (x_n - x_prev) % (1 << n)
            match = "MATCH!" if diff_x == adj else ""
            print(f"n={n:2d}: adj={adj:10d}, x_diff mod 2^n = {diff_x:10d} {match}")

    # Test 3: Check if adj_n relates to y-coordinate
    print("\n=== Test 3: adj_n vs y(n * G) mod 2^n ===")
    for n in range(2, 16):
        adj = compute_adj(k, n)
        _, y = ec_mul(n, GX, GY)
        if y:
            y_mod = y % (1 << n)
            match = "MATCH!" if y_mod == adj else ""
            print(f"n={n:2d}: adj={adj:10d}, y(n*G) mod 2^n = {y_mod:10d} {match}")

    # Test 4: Check low bits of public key x-coordinate
    print("\n=== Test 4: Low bits of x(k_n * G) ===")
    print("Looking for pattern in public key x-coordinates...")
    for n in range(1, 16):
        x, _ = ec_mul(k[n], GX, GY)
        if x:
            low_8 = x & 0xFF
            low_n = x % (1 << n)
            print(f"n={n:2d}: k={k[n]:10d}, x(k*G) low 8 bits = {low_8:3d}, low {n} bits = {low_n}")

    # Test 5: Is there a constant offset?
    print("\n=== Test 5: Looking for constant offset pattern ===")
    print("Check if adj_n = c * x(n*G) + offset for some c, offset")
    for n in range(2, 16):
        adj = compute_adj(k, n)
        x, _ = ec_mul(n, GX, GY)
        if x:
            x_mod = x % (1 << n)
            if x_mod != 0:
                ratio = adj / x_mod
                remainder = adj - x_mod
                print(f"n={n:2d}: adj={adj:10d}, x_mod={x_mod:10d}, adj/x_mod={ratio:10.4f}, adj-x_mod={remainder:10d}")

    # Test 6: Hash-based derivation
    print("\n=== Test 6: SHA256 hash of n ===")
    for n in range(2, 16):
        adj = compute_adj(k, n)
        h = int(hashlib.sha256(n.to_bytes(8, 'big')).hexdigest(), 16)
        h_mod = h % (1 << n)
        match = "MATCH!" if h_mod == adj else ""
        print(f"n={n:2d}: adj={adj:10d}, SHA256(n) mod 2^n = {h_mod:10d} {match}")

    print("\n" + "=" * 70)
    print("EC DEEP TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
