#!/usr/bin/env python3
"""
Test: Are k[n] values related to continued fraction convergents?

The puzzle creator might have used some mathematical constant's
continued fraction expansion to generate the keys.

Test constants: π, e, φ, √2, √3, √5
"""

import sqlite3
from fractions import Fraction
from math import sqrt, pi, e

DB_PATH = "/home/rkh/ladder/db/kh.db"

def load_k_values():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT puzzle_id, priv_hex
        FROM ground_truth
        WHERE priv_hex IS NOT NULL
        ORDER BY puzzle_id
    """)
    rows = c.fetchall()
    conn.close()
    k = {}
    for puzzle_id, priv_hex in rows:
        if priv_hex.startswith('0x'):
            k[puzzle_id] = int(priv_hex, 16)
        else:
            k[puzzle_id] = int(priv_hex, 16)
    return k

def continued_fraction(x, n_terms=50):
    """Generate continued fraction expansion of x."""
    cf = []
    for _ in range(n_terms):
        a = int(x)
        cf.append(a)
        x = x - a
        if abs(x) < 1e-15:
            break
        x = 1.0 / x
    return cf

def convergents(cf):
    """Generate convergents from continued fraction."""
    h_prev, h_curr = 0, 1
    k_prev, k_curr = 1, 0

    convs = []
    for a in cf:
        h_prev, h_curr = h_curr, a * h_curr + h_prev
        k_prev, k_curr = k_curr, a * k_curr + k_prev
        convs.append((h_curr, k_curr))

    return convs

def test_cf_relationship(k_values, constant_name, constant_value):
    """Test if k values appear in continued fraction of constant."""
    cf = continued_fraction(constant_value, 100)
    convs = convergents(cf)

    print(f"\n=== {constant_name} = {constant_value:.10f} ===")
    print(f"CF: [{cf[0]}; {', '.join(map(str, cf[1:20]))}...]")

    # Extract numerators and denominators
    nums = [h for h, k in convs]
    dens = [k for h, k in convs]
    all_cf_values = set(nums + dens + cf)

    # Check which k values appear
    matches = []
    for n, kn in sorted(k_values.items())[:30]:
        if kn in all_cf_values:
            where = []
            if kn in nums:
                where.append(f"num[{nums.index(kn)}]")
            if kn in dens:
                where.append(f"den[{dens.index(kn)}]")
            if kn in cf:
                where.append(f"cf[{cf.index(kn)}]")
            matches.append((n, kn, where))
            print(f"  k[{n}]={kn} appears in {where}")

    if not matches:
        print(f"  No matches found")

    return len(matches)

def test_cf_of_k_ratio(k_values):
    """Check continued fraction of k[n+1]/k[n]"""
    print("\n=== CF of k[n+1]/k[n] ===")

    for n in range(1, min(20, max(k_values.keys()))):
        if n in k_values and (n+1) in k_values:
            ratio = k_values[n+1] / k_values[n]
            cf = continued_fraction(ratio, 10)
            print(f"  k[{n+1}]/k[{n}] = {ratio:.6f} -> CF: [{cf[0]}; {', '.join(map(str, cf[1:5]))}...]")

def test_cf_of_c_sequence(k_values):
    """Check continued fraction of c[n] = k[n]/2^n"""
    print("\n=== CF of c[n] = k[n]/2^n ===")

    c_values = {}
    for n in range(1, min(25, max(k_values.keys()) + 1)):
        if n in k_values:
            c_values[n] = k_values[n] / (2 ** n)

    for n, c in sorted(c_values.items())[:15]:
        cf = continued_fraction(c, 10)
        print(f"  c[{n}] = k[{n}]/2^{n} = {c:.6f} -> CF: [{cf[0]}; {', '.join(map(str, cf[1:6]))}...]")

def test_secp256k1_relationship(k_values):
    """Check if k values relate to secp256k1 curve parameters."""
    print("\n=== secp256k1 Curve Parameters ===")

    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

    # Check if any k value is related to curve order mod something
    print(f"Curve order n = {n}")
    print(f"Curve order bits = {n.bit_length()}")

    for i in range(1, min(15, max(k_values.keys()) + 1)):
        if i in k_values:
            kv = k_values[i]
            # Check n mod k[i]
            if kv > 1:
                n_mod_k = n % kv
                print(f"  n mod k[{i}] ({kv}) = {n_mod_k}")

def main():
    k = load_k_values()
    print(f"Loaded {len(k)} k values\n")
    print(f"k[1..15]: {[k.get(i) for i in range(1, 16)]}")

    # Test various constants
    phi = (1 + sqrt(5)) / 2
    constants = [
        ("π", pi),
        ("e", e),
        ("φ (golden ratio)", phi),
        ("√2", sqrt(2)),
        ("√3", sqrt(3)),
        ("√5", sqrt(5)),
        ("√7", sqrt(7)),
    ]

    for name, val in constants:
        test_cf_relationship(k, name, val)

    test_cf_of_k_ratio(k)
    test_cf_of_c_sequence(k)
    test_secp256k1_relationship(k)

if __name__ == "__main__":
    main()
