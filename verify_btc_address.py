#!/usr/bin/env python3
"""
Bitcoin Address Verification Tool

Derives BTC address from private key and verifies against puzzle addresses.
Used to confirm mathematical derivations are correct.
"""

import hashlib
import sqlite3

# secp256k1 curve parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = a % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("No modular inverse")
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def point_add(p1, p2):
    """Add two points on secp256k1."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if y1 != y2:
            return None  # Point at infinity
        # Point doubling
        lam = (3 * x1 * x1) * modinv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * modinv(x2 - x1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)

def scalar_mult(k, point):
    """Multiply point by scalar k."""
    result = None
    addend = point
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result

def privkey_to_pubkey(privkey):
    """Convert private key to public key point."""
    return scalar_mult(privkey, G)

def pubkey_to_hash160(pubkey, compressed=True):
    """Convert public key to HASH160."""
    x, y = pubkey
    if compressed:
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        pubkey_bytes = prefix + x.to_bytes(32, 'big')
    else:
        pubkey_bytes = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')

    sha256 = hashlib.sha256(pubkey_bytes).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    return ripemd160

def hash160_to_address(hash160, version=0x00):
    """Convert HASH160 to Base58Check address."""
    versioned = bytes([version]) + hash160
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    return base58_encode(versioned + checksum)

def base58_encode(data):
    """Base58 encoding."""
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = int.from_bytes(data, 'big')
    result = ''
    while n > 0:
        n, r = divmod(n, 58)
        result = alphabet[r] + result
    # Handle leading zeros
    for byte in data:
        if byte == 0:
            result = '1' + result
        else:
            break
    return result

def privkey_to_address(privkey, compressed=True):
    """Convert private key to Bitcoin address."""
    pubkey = privkey_to_pubkey(privkey)
    hash160 = pubkey_to_hash160(pubkey, compressed)
    return hash160_to_address(hash160)

def verify_puzzle(n, privkey):
    """Verify a puzzle solution."""
    # Generate both compressed and uncompressed addresses
    addr_compressed = privkey_to_address(privkey, compressed=True)
    addr_uncompressed = privkey_to_address(privkey, compressed=False)

    # Check bit range
    min_val = 2 ** (n - 1)
    max_val = 2 ** n - 1
    in_range = min_val <= privkey <= max_val

    return {
        'puzzle': n,
        'privkey_dec': privkey,
        'privkey_hex': hex(privkey),
        'address_compressed': addr_compressed,
        'address_uncompressed': addr_uncompressed,
        'in_range': in_range,
        'bit_length': privkey.bit_length()
    }

def main():
    print("=" * 80)
    print("BITCOIN PUZZLE VERIFICATION TOOL")
    print("=" * 80)

    # Load known solutions from database
    try:
        conn = sqlite3.connect('/home/solo/LA/db/kh.db')
        cursor = conn.cursor()
        cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IN (70, 71, 75, 80) ORDER BY puzzle_id")
        known = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
        conn.close()
    except:
        known = {}

    # Derived k[71]
    k71_derived = 1602101676614237534489

    print("\n" + "-" * 80)
    print("VERIFYING DERIVED k[71]")
    print("-" * 80)

    result = verify_puzzle(71, k71_derived)
    print(f"\nPuzzle: {result['puzzle']}")
    print(f"Private Key (dec): {result['privkey_dec']:,}")
    print(f"Private Key (hex): {result['privkey_hex']}")
    print(f"Bit length: {result['bit_length']} (expected: 71)")
    print(f"In range [2^70, 2^71-1]: {result['in_range']}")
    print(f"\nCompressed Address:   {result['address_compressed']}")
    print(f"Uncompressed Address: {result['address_uncompressed']}")

    # Verify known puzzles
    print("\n" + "-" * 80)
    print("VERIFYING KNOWN PUZZLES FROM DATABASE")
    print("-" * 80)

    for n, privkey in sorted(known.items()):
        result = verify_puzzle(n, privkey)
        print(f"\nPuzzle {n}: {result['address_compressed']}")
        print(f"  Key: {result['privkey_hex']}")

    # Show what addresses to check
    print("\n" + "=" * 80)
    print("TO VERIFY k[71]:")
    print("=" * 80)
    print(f"\n1. Check Bitcoin blockchain for address: {privkey_to_address(k71_derived, True)}")
    print(f"2. If puzzle 71 is solved, the address should have transactions")
    print(f"3. Compare with puzzle list at: https://privatekeys.pw/puzzles/bitcoin-puzzle-tx")

if __name__ == "__main__":
    main()
