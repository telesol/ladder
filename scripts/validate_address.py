#!/usr/bin/env python3
"""
validate_address.py
Derives a Bitcoin address from a private key and validates it against the CSV.
Uses STRICT cryptographic rules required for Bitcoin address generation.
"""
import sys
import hashlib
import csv

def derive_address(privkey_hex):
    """
    Derives Bitcoin address from private key using strict rules.

    CRITICAL RULES:
    1. Big-Endian Byte Order
    2. Compressed Public Key (33 bytes)
    3. SHA256 → RIPEMD160 (correct order)
    4. Version Byte 0x00 (Bitcoin mainnet)
    5. Base58Check Encoding (with checksum)
    """
    try:
        from ecdsa import SigningKey, SECP256k1
        import base58
    except ImportError:
        sys.exit("❌ Error: Please install required packages:\n  pip install ecdsa base58")

    # Remove 0x prefix if present
    if privkey_hex.startswith('0x'):
        privkey_hex = privkey_hex[2:]

    print(f"🔑 Private Key: {privkey_hex}")
    print()

    # ⚠️ RULE 1: Big-Endian Byte Order
    privkey_bytes = bytes.fromhex(privkey_hex)
    print(f"✅ Rule 1: Big-endian byte order applied")

    # ⚠️ RULE 2: Derive Public Key (secp256k1)
    try:
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
    except Exception as e:
        sys.exit(f"❌ Error deriving signing key: {e}")

    print(f"✅ Rule 2: Signing key derived (secp256k1)")

    # ⚠️ RULE 3: Use COMPRESSED Public Key (33 bytes)
    vk = sk.get_verifying_key()
    try:
        pubkey_compressed = vk.to_string("compressed")
    except:
        # Fallback for older ecdsa versions
        pubkey_uncompressed = vk.to_string()
        x = pubkey_uncompressed[:32]
        y_byte = pubkey_uncompressed[32]
        prefix = b'\x02' if y_byte % 2 == 0 else b'\x03'
        pubkey_compressed = prefix + x

    print(f"✅ Rule 3: Compressed public key (33 bytes, prefix: 0x{pubkey_compressed[0]:02x})")

    # ⚠️ RULE 4: Hash Sequence (SHA256 → RIPEMD160)
    sha256_hash = hashlib.sha256(pubkey_compressed).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    print(f"✅ Rule 4: Hash sequence (SHA256 → RIPEMD160)")

    # ⚠️ RULE 5: Add Version Byte (0x00 for Bitcoin mainnet)
    versioned = b'\x00' + ripemd160_hash
    print(f"✅ Rule 5: Version byte 0x00 added (Bitcoin mainnet P2PKH)")

    # Base58Check encoding (includes 4-byte checksum)
    try:
        address = base58.b58encode_check(versioned).decode()
    except Exception as e:
        sys.exit(f"❌ Error encoding address: {e}")

    print(f"✅ Base58Check encoding with checksum")
    print()

    return address

def get_expected_address(puzzle_num, csv_path='data/btc_puzzle_1_160_full.csv'):
    """Get expected address from CSV file."""
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row and int(row[0]) == puzzle_num:
                    return row[1]  # Column 2 is the address
    except FileNotFoundError:
        sys.exit(f"❌ Error: CSV file not found at {csv_path}")
    except Exception as e:
        sys.exit(f"❌ Error reading CSV: {e}")

    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_address.py <private_key_hex> [puzzle_number]")
        print()
        print("Example:")
        print("  python3 validate_address.py 0x1234...abcd 71")
        print()
        sys.exit(1)

    privkey_hex = sys.argv[1]
    puzzle_num = int(sys.argv[2]) if len(sys.argv) > 2 else None

    print("🔐 Bitcoin Address Validation Tool")
    print("=" * 60)
    print()

    # Derive address
    derived_address = derive_address(privkey_hex)
    print(f"📍 Derived Address: {derived_address}")
    print()

    # Compare with expected if puzzle number provided
    if puzzle_num:
        expected_address = get_expected_address(puzzle_num)
        if expected_address:
            print(f"📋 Expected Address (CSV puzzle {puzzle_num}): {expected_address}")
            print()

            if derived_address == expected_address:
                print("=" * 60)
                print("✅✅✅ MATCH! THE PRIVATE KEY IS CORRECT! ✅✅✅")
                print("=" * 60)
                print()
                print("🎉 SUCCESS! You have generated a correct private key!")
                print(f"🎉 The ladder mathematics is PROVEN for puzzle {puzzle_num}!")
                print()
                return 0
            else:
                print("=" * 60)
                print("❌ MISMATCH! The addresses do not match.")
                print("=" * 60)
                print()
                print("Check these potential issues:")
                print("  1. Big-endian byte order - was it applied correctly?")
                print("  2. Compressed public key - is it 33 bytes with 0x02/0x03 prefix?")
                print("  3. Hash sequence - did you do SHA256 FIRST, then RIPEMD160?")
                print("  4. Version byte - is it 0x00 for mainnet?")
                print("  5. Base58Check - does it include the 4-byte checksum?")
                print()
                return 1
        else:
            print(f"⚠️  No expected address found for puzzle {puzzle_num} in CSV")

    return 0

if __name__ == "__main__":
    sys.exit(main())
