#!/usr/bin/env python3
"""
Cryptographic Validator - Bitcoin Address Derivation

This module provides FULL cryptographic validation:
Private Key → Public Key → Bitcoin Address

This PROVES that generated keys are cryptographically correct,
not just hex pattern matches.
"""

import hashlib
import ecdsa
from typing import Tuple


def private_key_to_public_key(private_key_hex: str) -> Tuple[str, str]:
    """
    Derive public key from private key using ECDSA secp256k1.

    Args:
        private_key_hex: 64-char hex string (32 bytes)

    Returns:
        Tuple of (uncompressed_pubkey_hex, compressed_pubkey_hex)
    """
    # Convert hex to integer
    private_key_int = int(private_key_hex, 16)

    # Create signing key
    sk = ecdsa.SigningKey.from_secret_exponent(
        private_key_int,
        curve=ecdsa.SECP256k1
    )

    # Get verifying key (public key)
    vk = sk.get_verifying_key()

    # Uncompressed format: 04 + x + y (65 bytes)
    uncompressed = b'\x04' + vk.to_string()
    uncompressed_hex = uncompressed.hex()

    # Compressed format: 02/03 + x (33 bytes)
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()

    if y % 2 == 0:
        prefix = b'\x02'
    else:
        prefix = b'\x03'

    compressed = prefix + x.to_bytes(32, 'big')
    compressed_hex = compressed.hex()

    return uncompressed_hex, compressed_hex


def hash160(data_hex: str) -> str:
    """
    Perform SHA256 + RIPEMD160 on data.

    This is the standard Bitcoin address hashing.

    Args:
        data_hex: Hex string of data to hash

    Returns:
        20-byte hash (40 hex chars)
    """
    data = bytes.fromhex(data_hex)

    # SHA256
    sha256_hash = hashlib.sha256(data).digest()

    # RIPEMD160
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

    return ripemd160_hash.hex()


def base58_encode(data: bytes) -> str:
    """
    Encode data to Base58 (Bitcoin alphabet).

    Args:
        data: Bytes to encode

    Returns:
        Base58-encoded string
    """
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    # Convert bytes to integer
    num = int.from_bytes(data, 'big')

    # Convert to base58
    encoded = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        encoded = alphabet[remainder] + encoded

    # Handle leading zeros
    for byte in data:
        if byte == 0:
            encoded = '1' + encoded
        else:
            break

    return encoded


def base58check_encode(version: int, payload_hex: str) -> str:
    """
    Encode with Base58Check (includes checksum).

    Args:
        version: Version byte (0x00 for Bitcoin mainnet)
        payload_hex: Payload to encode (40 hex chars for pubkey hash)

    Returns:
        Base58Check-encoded string (Bitcoin address)
    """
    payload = bytes.fromhex(payload_hex)

    # Version + payload
    versioned = bytes([version]) + payload

    # Double SHA256 for checksum
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

    # Encode: version + payload + checksum
    full_payload = versioned + checksum

    return base58_encode(full_payload)


def private_key_to_address(private_key_hex: str, compressed: bool = False) -> str:
    """
    Derive Bitcoin address from private key.

    Full pipeline:
    1. Private key → Public key (ECDSA)
    2. Public key → Hash160 (SHA256 + RIPEMD160)
    3. Hash160 → Base58Check (Bitcoin address)

    Args:
        private_key_hex: 64-char hex string (32 bytes)
        compressed: Use compressed public key format

    Returns:
        Bitcoin address (1xxx... for mainnet)
    """
    # Step 1: Derive public key
    uncompressed_pubkey, compressed_pubkey = private_key_to_public_key(private_key_hex)

    pubkey = compressed_pubkey if compressed else uncompressed_pubkey

    # Step 2: Hash public key
    pubkey_hash = hash160(pubkey)

    # Step 3: Encode to Bitcoin address
    address = base58check_encode(0x00, pubkey_hash)

    return address


def validate_key_generates_address(private_key_hex: str,
                                     expected_address: str,
                                     try_compressed: bool = True) -> dict:
    """
    Validate that a private key generates the expected Bitcoin address.

    This is the PROOF that our generated key is correct.

    Args:
        private_key_hex: Generated private key (64 hex chars)
        expected_address: Known Bitcoin address from CSV
        try_compressed: Try both compressed and uncompressed formats

    Returns:
        dict with validation results:
        {
            'match': True/False,
            'generated_address': '1xxx...',
            'expected_address': '1xxx...',
            'format': 'compressed' or 'uncompressed',
            'pubkey_hash': '...',
        }
    """
    # Try uncompressed first (puzzle challenge uses uncompressed)
    address_uncompressed = private_key_to_address(private_key_hex, compressed=False)

    if address_uncompressed == expected_address:
        _, compressed_pubkey = private_key_to_public_key(private_key_hex)
        uncompressed_pubkey, _ = private_key_to_public_key(private_key_hex)

        return {
            'match': True,
            'generated_address': address_uncompressed,
            'expected_address': expected_address,
            'format': 'uncompressed',
            'pubkey_uncompressed': uncompressed_pubkey,
            'pubkey_hash': hash160(uncompressed_pubkey),
        }

    # Try compressed if requested
    if try_compressed:
        address_compressed = private_key_to_address(private_key_hex, compressed=True)

        if address_compressed == expected_address:
            _, compressed_pubkey = private_key_to_public_key(private_key_hex)

            return {
                'match': True,
                'generated_address': address_compressed,
                'expected_address': expected_address,
                'format': 'compressed',
                'pubkey_compressed': compressed_pubkey,
                'pubkey_hash': hash160(compressed_pubkey),
            }

    # No match
    return {
        'match': False,
        'generated_address_uncompressed': address_uncompressed,
        'generated_address_compressed': private_key_to_address(private_key_hex, compressed=True) if try_compressed else None,
        'expected_address': expected_address,
        'format': None,
    }


def test_crypto_validator():
    """Test the crypto validator with known puzzle 1."""
    print("="*80)
    print("Testing Cryptographic Validator")
    print("="*80)

    # Puzzle 1 (known values from CSV)
    private_key = "0000000000000000000000000000000000000000000000000000000000000001"
    expected_address = "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH"

    print(f"\n🔑 Private Key: {private_key}")
    print(f"📍 Expected Address: {expected_address}")

    # Derive public key
    uncompressed, compressed = private_key_to_public_key(private_key)
    print(f"\n📡 Public Key (uncompressed): {uncompressed[:80]}...")
    print(f"📡 Public Key (compressed):   {compressed}")

    # Try both formats
    address_uncompressed = private_key_to_address(private_key, compressed=False)
    address_compressed = private_key_to_address(private_key, compressed=True)

    print(f"\n🏠 Derived Address (uncompressed): {address_uncompressed}")
    print(f"🏠 Derived Address (compressed):   {address_compressed}")

    # Validate
    result = validate_key_generates_address(private_key, expected_address)

    if result['match']:
        print(f"\n✅ SUCCESS! Address matches!")
        print(f"   Format: {result['format']}")
        print(f"   PubKey Hash: {result['pubkey_hash']}")
        print(f"\n💡 Bitcoin puzzle uses {result['format'].upper()} public keys")
    else:
        print(f"\n❌ FAILED! Address mismatch")
        print(f"   Generated (uncompressed): {result.get('generated_address_uncompressed')}")
        print(f"   Generated (compressed):   {result.get('generated_address_compressed')}")
        print(f"   Expected:  {result['expected_address']}")

    print(f"\n{'='*80}\n")

    return result['match']


if __name__ == "__main__":
    # Test with puzzle 1
    success = test_crypto_validator()

    if success:
        print("🎉 Crypto validator is working correctly!")
        print("Ready to validate PySR-generated keys.")
    else:
        print("❌ Crypto validator has issues - needs debugging")
