#!/usr/bin/env python3
"""
THOROUGH SEARCH FOR k[71]
Search ALL candidates for d values with less than 1 million candidates
"""

import sqlite3
import hashlib
import sys

# Load k-values
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
K = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

TARGET_ADDRESS = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

# Constants
POWER_71 = 2 ** 71
K_70 = K[70]
MIN_K71 = 2 ** 70
MAX_K71 = 2 ** 71 - 1

# Bitcoin address derivation
try:
    import ecdsa
    from ecdsa import SECP256k1

    def privkey_to_address(privkey):
        """Convert private key integer to Bitcoin address."""
        sk = ecdsa.SigningKey.from_secret_exponent(privkey, curve=SECP256k1)
        vk = sk.get_verifying_key()
        pub_point = vk.pubkey.point
        x, y = pub_point.x(), pub_point.y()

        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        pub_key_compressed = prefix + x.to_bytes(32, 'big')

        sha256_hash = hashlib.sha256(pub_key_compressed).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        hash160 = ripemd160.digest()

        versioned = b'\x00' + hash160
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        address_bytes = versioned + checksum

        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        num = int.from_bytes(address_bytes, 'big')
        result = ''
        while num > 0:
            num, rem = divmod(num, 58)
            result = alphabet[rem] + result

        for byte in address_bytes:
            if byte == 0:
                result = '1' + result
            else:
                break

        return result

except ImportError:
    print("ERROR: ecdsa not installed")
    sys.exit(1)

print("=" * 80)
print("THOROUGH K[71] SEARCH")
print("=" * 80)
print(f"Target: {TARGET_ADDRESS}")
print()

base = POWER_71 + 2 * K_70

total_checked = 0
found = False

# Search d values with small candidate ranges
for d in range(70, 0, -1):  # Start from largest d (smallest ranges)
    if d not in K:
        continue

    k_d = K[d]

    # Calculate m range
    m_min = max(1, (2 * K_70 + 1 + k_d - 1) // k_d)
    m_max = (MIN_K71 + 2 * K_70) // k_d

    if m_min > m_max:
        continue

    range_size = m_max - m_min + 1

    if range_size > 10000000:  # Skip ranges > 10M for now
        continue

    print(f"d={d}: Checking {range_size:,} candidates...", end=" ", flush=True)

    for m in range(m_min, m_max + 1):
        k71_candidate = base - m * k_d

        if MIN_K71 <= k71_candidate <= MAX_K71:
            total_checked += 1
            addr = privkey_to_address(k71_candidate)
            if addr == TARGET_ADDRESS:
                print(f"\n\n🎉 FOUND! 🎉")
                print(f"d[71] = {d}")
                print(f"m[71] = {m:,}")
                print(f"k[71] = {k71_candidate:,}")
                print(f"k[71] hex = {hex(k71_candidate)}")
                print(f"Address = {addr}")
                found = True
                break

    if found:
        break

    print("✗")

print()
print(f"Total candidates checked: {total_checked:,}")

if not found:
    print("k[71] not found in searched ranges.")
    print("May need to search larger d values or the formula may be different for n=71.")
