#!/usr/bin/env python3
"""
SEARCH FOR k[71] using the verified formula:
k[71] = 2^71 + 2*k[70] - m[71] * k[d[71]]

For each candidate (m[71], d[71]), compute k[71] and verify the Bitcoin address.
Target address: 1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU
"""

import sqlite3
import hashlib

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

print("=" * 80)
print("SEARCHING FOR k[71]")
print("=" * 80)
print(f"2^71 = {POWER_71:,}")
print(f"k[70] = {K_70:,}")
print(f"Valid range: [{MIN_K71:,}, {MAX_K71:,}]")
print()

# Bitcoin address derivation
try:
    import ecdsa
    from ecdsa import SECP256k1

    def privkey_to_address(privkey):
        """Convert private key integer to Bitcoin address."""
        # Get public key
        sk = ecdsa.SigningKey.from_secret_exponent(privkey, curve=SECP256k1)
        vk = sk.get_verifying_key()
        pub_point = vk.pubkey.point
        x, y = pub_point.x(), pub_point.y()

        # Compressed public key
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        pub_key_compressed = prefix + x.to_bytes(32, 'big')

        # HASH160
        sha256_hash = hashlib.sha256(pub_key_compressed).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        hash160 = ripemd160.digest()

        # Base58Check encoding
        versioned = b'\x00' + hash160
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        address_bytes = versioned + checksum

        # Base58 encode
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        num = int.from_bytes(address_bytes, 'big')
        result = ''
        while num > 0:
            num, rem = divmod(num, 58)
            result = alphabet[rem] + result

        # Add leading 1s for leading zero bytes
        for byte in address_bytes:
            if byte == 0:
                result = '1' + result
            else:
                break

        return result

    CAN_VERIFY = True
except ImportError:
    CAN_VERIFY = False
    print("WARNING: ecdsa not installed, cannot verify addresses")

# Generate candidate (d, m) pairs
# d must be in range [1, 70]
# m must give k[71] in valid range

candidates_found = 0
print("Searching candidate (d, m) pairs...")
print()

# For each d, find the range of valid m
for d in range(1, 71):
    if d not in K:
        continue

    k_d = K[d]

    # k[71] = 2^71 + 2*k[70] - m*k[d]
    # For k[71] to be in [2^70, 2^71-1]:
    # 2^70 <= 2^71 + 2*k[70] - m*k[d] <= 2^71-1
    # m*k[d] <= 2^71 + 2*k[70] - 2^70 = 2^70 + 2*k[70]
    # m*k[d] >= 2^71 + 2*k[70] - (2^71-1) = 2*k[70] + 1

    base = POWER_71 + 2 * K_70

    m_min = max(1, (2 * K_70 + 1 + k_d - 1) // k_d)  # ceil division
    m_max = (MIN_K71 + 2 * K_70) // k_d  # floor division

    if m_min > m_max:
        continue

    # For small ranges, check all. For large ranges, sample
    range_size = m_max - m_min + 1

    if range_size <= 1000:
        # Check all
        for m in range(m_min, m_max + 1):
            k71_candidate = base - m * k_d

            if MIN_K71 <= k71_candidate <= MAX_K71:
                # Check Bitcoin address
                if CAN_VERIFY:
                    addr = privkey_to_address(k71_candidate)
                    if addr == TARGET_ADDRESS:
                        print(f"🎉 FOUND! d={d}, m={m}")
                        print(f"   k[71] = {k71_candidate:,}")
                        print(f"   k[71] hex = {hex(k71_candidate)}")
                        print(f"   Address = {addr}")
                        candidates_found += 1
                        break
    else:
        # For large ranges, we can't enumerate. Print stats
        print(f"d={d}: k[d]={k_d:,}, m_range=[{m_min:,}, {m_max:,}] ({range_size:,} candidates)")

print()
if candidates_found == 0:
    print("No matching k[71] found in small-range candidates.")
    print("Need to search larger m-ranges systematically.")
