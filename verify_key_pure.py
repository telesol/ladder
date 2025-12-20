#!/usr/bin/env python3
"""
Pure Python Bitcoin address verification.
No external dependencies beyond standard library.
"""

import hashlib
import sys

# secp256k1 curve parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
A = 0
B = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def modinv(a, m):
    """Extended Euclidean Algorithm for modular inverse."""
    if a < 0:
        a = a % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def point_add(p1, p2):
    """Add two points on the curve."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1

    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2 and y1 != y2:
        return None

    if x1 == x2:
        m = (3 * x1 * x1 + A) * modinv(2 * y1, P)
    else:
        m = (y2 - y1) * modinv(x2 - x1, P)

    m = m % P
    x3 = (m * m - x1 - x2) % P
    y3 = (m * (x1 - x3) - y1) % P
    return (x3, y3)

def point_multiply(k, point):
    """Multiply a point by a scalar."""
    result = None
    addend = point

    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1

    return result

def privkey_to_pubkey(privkey_int):
    """Derive public key from private key."""
    return point_multiply(privkey_int, (Gx, Gy))

def pubkey_to_compressed(pubkey):
    """Convert public key to compressed format (33 bytes)."""
    x, y = pubkey
    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    return prefix + x.to_bytes(32, 'big')

def hash160(data):
    """SHA256 followed by RIPEMD160."""
    sha = hashlib.sha256(data).digest()
    return hashlib.new('ripemd160', sha).digest()

def base58_encode(data):
    """Base58 encoding."""
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    # Count leading zeros
    leading_zeros = 0
    for byte in data:
        if byte == 0:
            leading_zeros += 1
        else:
            break

    # Convert to integer
    num = int.from_bytes(data, 'big')

    # Encode
    result = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        result = alphabet[remainder] + result

    return '1' * leading_zeros + result

def base58check_encode(version_byte, payload):
    """Base58Check encoding with checksum."""
    versioned = bytes([version_byte]) + payload
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    return base58_encode(versioned + checksum)

def privkey_to_address(privkey_int):
    """Convert private key to Bitcoin address."""
    # Get public key
    pubkey = privkey_to_pubkey(privkey_int)

    # Compress public key
    pubkey_compressed = pubkey_to_compressed(pubkey)

    # Hash160
    pubkey_hash = hash160(pubkey_compressed)

    # Base58Check encode with version 0x00 (mainnet P2PKH)
    address = base58check_encode(0x00, pubkey_hash)

    return address, pubkey_compressed.hex()

def privkey_to_wif(privkey_int, compressed=True):
    """Convert private key to WIF format."""
    # Pad to 32 bytes
    privkey_bytes = privkey_int.to_bytes(32, 'big')

    if compressed:
        # Add 0x01 suffix for compressed
        payload = privkey_bytes + b'\x01'
    else:
        payload = privkey_bytes

    # Version byte 0x80 for mainnet
    return base58check_encode(0x80, payload)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 verify_key_pure.py <private_key_hex> [expected_address]")
        sys.exit(1)

    privkey_hex = sys.argv[1]
    expected_address = sys.argv[2] if len(sys.argv) > 2 else None

    # Parse private key
    if privkey_hex.startswith('0x'):
        privkey_hex = privkey_hex[2:]
    privkey_int = int(privkey_hex, 16)

    print("=" * 70)
    print("BITCOIN ADDRESS VERIFICATION (Pure Python)")
    print("=" * 70)
    print()
    print(f"Private Key (hex): {privkey_hex}")
    print(f"Private Key (int): {privkey_int}")
    print()

    # Derive address
    address, pubkey_hex = privkey_to_address(privkey_int)

    print(f"Public Key (compressed): {pubkey_hex}")
    print(f"Derived Address: {address}")
    print()

    # Generate WIF
    wif_compressed = privkey_to_wif(privkey_int, compressed=True)
    wif_uncompressed = privkey_to_wif(privkey_int, compressed=False)

    print(f"WIF (compressed):   {wif_compressed}")
    print(f"WIF (uncompressed): {wif_uncompressed}")
    print()

    # Compare with expected
    if expected_address:
        print("=" * 70)
        print("VERIFICATION")
        print("=" * 70)
        print()
        print(f"Expected Address: {expected_address}")
        print(f"Derived Address:  {address}")
        print()

        if address == expected_address:
            print("✅✅✅ MATCH! PRIVATE KEY IS CORRECT! ✅✅✅")
            print()
            print(f"WIF: {wif_compressed}")
            return 0
        else:
            print("❌ MISMATCH - Address does not match target")
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
