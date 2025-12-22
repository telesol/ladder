#!/usr/bin/env python3
"""
VERIFY HASH FORMULA HYPOTHESIS

The analysis showed that seed "bitcoin" matched 4/5 early keys.
Let's verify this rigorously against ALL 74 known keys.

Formula to test: k[n] = 2^(n-1) + (SHA256(seed || n) mod 2^(n-1))
"""

import sqlite3
import hashlib
import hmac

DB_PATH = "/home/solo/LA/db/kh.db"

def get_all_keys():
    """Load ALL 74 known keys from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id")
    rows = cursor.fetchall()
    keys = {}
    for pid, hex_val in rows:
        keys[pid] = int(hex_val, 16)
    conn.close()
    return keys

def hash_formula_sha256(seed, n):
    """Generate key using SHA256(seed || n)"""
    min_val = 2**(n-1)
    max_val = 2**n - 1
    range_size = max_val - min_val + 1

    # Hash: seed + str(n)
    hash_input = seed + str(n).encode()
    hash_output = hashlib.sha256(hash_input).digest()
    hash_int = int.from_bytes(hash_output, byteorder='big')

    # Constrain to range
    k = min_val + (hash_int % range_size)
    return k

def hash_formula_sha256_bytes(seed, n):
    """Generate key using SHA256(seed || n_as_bytes)"""
    min_val = 2**(n-1)
    max_val = 2**n - 1
    range_size = max_val - min_val + 1

    # Hash: seed + n as 4-byte integer
    hash_input = seed + n.to_bytes(4, byteorder='big')
    hash_output = hashlib.sha256(hash_input).digest()
    hash_int = int.from_bytes(hash_output, byteorder='big')

    # Constrain to range
    k = min_val + (hash_int % range_size)
    return k

def hash_formula_sha512(seed, n):
    """Generate key using SHA512(seed || n)"""
    min_val = 2**(n-1)
    max_val = 2**n - 1
    range_size = max_val - min_val + 1

    hash_input = seed + str(n).encode()
    hash_output = hashlib.sha512(hash_input).digest()
    hash_int = int.from_bytes(hash_output, byteorder='big')

    k = min_val + (hash_int % range_size)
    return k

def hash_formula_hmac(seed, n):
    """Generate key using HMAC-SHA256(seed, n)"""
    min_val = 2**(n-1)
    max_val = 2**n - 1
    range_size = max_val - min_val + 1

    msg = str(n).encode()
    hash_output = hmac.new(seed, msg, hashlib.sha256).digest()
    hash_int = int.from_bytes(hash_output, byteorder='big')

    k = min_val + (hash_int % range_size)
    return k

def test_formula(formula_func, seed_str, keys):
    """Test a hash formula against all known keys"""
    seed = seed_str.encode()

    matches = []
    mismatches = []

    for n, k_actual in sorted(keys.items()):
        k_predicted = formula_func(seed, n)

        if k_predicted == k_actual:
            matches.append(n)
        else:
            mismatches.append((n, k_actual, k_predicted))

    return matches, mismatches

def main():
    print("="*80)
    print("HASH FORMULA VERIFICATION")
    print("="*80)

    keys = get_all_keys()
    print(f"\nLoaded {len(keys)} known keys from database\n")

    # Test various seed candidates
    seeds = [
        "bitcoin",
        "puzzle",
        "satoshi",
        "1",
        "2015",
        "creator",
        "btc",
        "key",
        "challenge",
        "",  # Empty seed
    ]

    formulas = [
        ("SHA256(seed || str(n))", hash_formula_sha256),
        ("SHA256(seed || bytes(n))", hash_formula_sha256_bytes),
        ("SHA512(seed || str(n))", hash_formula_sha512),
        ("HMAC-SHA256(seed, str(n))", hash_formula_hmac),
    ]

    best_match_count = 0
    best_match_formula = None
    best_match_seed = None

    for seed in seeds:
        print(f"\n{'='*80}")
        print(f"TESTING SEED: '{seed}'")
        print(f"{'='*80}")

        for formula_name, formula_func in formulas:
            matches, mismatches = test_formula(formula_func, seed, keys)

            print(f"\n{formula_name}:")
            print(f"  Matches: {len(matches)}/{len(keys)}")

            if len(matches) > 0:
                print(f"  Matched puzzles: {matches[:10]}{'...' if len(matches) > 10 else ''}")

            if len(matches) > best_match_count:
                best_match_count = len(matches)
                best_match_formula = formula_name
                best_match_seed = seed

            if len(mismatches) > 0 and len(mismatches) <= 10:
                print(f"  Mismatches (n, actual, predicted):")
                for n, actual, predicted in mismatches[:5]:
                    print(f"    n={n}: actual={actual}, predicted={predicted}")

            # If we get ALL matches, we found it!
            if len(matches) == len(keys):
                print("\n" + "="*80)
                print("✓✓✓ FORMULA FOUND! ✓✓✓")
                print("="*80)
                print(f"\nFormula: {formula_name}")
                print(f"Seed: '{seed}'")
                print(f"\nVerified against ALL {len(keys)} known keys!")

                # Generate predictions for unsolved puzzles
                print("\n" + "="*80)
                print("PREDICTIONS FOR UNSOLVED PUZZLES")
                print("="*80)

                unsolved = [71, 72, 73, 74, 76, 77, 78, 79, 81, 82, 83, 84, 86, 87, 88, 89]
                for n in unsolved[:10]:  # Show first 10
                    k_pred = formula_func(seed.encode(), n)
                    print(f"k[{n}] = {k_pred}")
                    print(f"       = {hex(k_pred)}")

                return

    # Summary if no perfect match found
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    if best_match_count > 0:
        print(f"\nBest match: {best_match_count}/{len(keys)} keys")
        print(f"Formula: {best_match_formula}")
        print(f"Seed: '{best_match_seed}'")
        print("\n⚠ No perfect formula found - continue investigating")
    else:
        print("\n✗ No hash formula matches found")
        print("The keys are likely NOT generated via simple hash(seed, n)")

if __name__ == "__main__":
    main()
