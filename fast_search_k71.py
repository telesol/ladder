#!/usr/bin/env python3
"""
FAST K[71] SEARCH using coincurve (C-based libsecp256k1)
Uses multiprocessing for parallel search
"""

import sqlite3
import hashlib
import sys
from multiprocessing import Pool, cpu_count
import coincurve

# Load k-values
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
K = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

TARGET_ADDRESS = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
TARGET_HASH160 = None  # Will be computed

# Constants
POWER_71 = 2 ** 71
K_70 = K[70]
MIN_K71 = 2 ** 70
MAX_K71 = 2 ** 71 - 1
BASE = POWER_71 + 2 * K_70

def base58_decode(s):
    """Decode base58 string to bytes"""
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = 0
    for c in s:
        n = n * 58 + alphabet.index(c)
    return n.to_bytes(25, 'big')

def get_target_hash160():
    """Extract HASH160 from target address"""
    decoded = base58_decode(TARGET_ADDRESS)
    return decoded[1:21]  # Skip version byte, take 20 bytes

def privkey_to_hash160(privkey):
    """Convert private key to HASH160 using coincurve (FAST)"""
    # Private key to 32 bytes
    privkey_bytes = privkey.to_bytes(32, 'big')

    # Get compressed public key
    pk = coincurve.PrivateKey(privkey_bytes)
    pubkey_compressed = pk.public_key.format(compressed=True)

    # HASH160: SHA256 then RIPEMD160
    sha256_hash = hashlib.sha256(pubkey_compressed).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    return ripemd160.digest()

def search_range(args):
    """Search a range of m values for a given d"""
    d, m_start, m_end, k_d, target_hash160 = args

    found = []
    for m in range(m_start, m_end):
        k71_candidate = BASE - m * k_d

        if MIN_K71 <= k71_candidate <= MAX_K71:
            h160 = privkey_to_hash160(k71_candidate)
            if h160 == target_hash160:
                found.append((d, m, k71_candidate))

    return found

def main():
    global TARGET_HASH160
    TARGET_HASH160 = get_target_hash160()

    print("=" * 80)
    print("FAST PARALLEL K[71] SEARCH")
    print("=" * 80)
    print(f"Target: {TARGET_ADDRESS}")
    print(f"Target HASH160: {TARGET_HASH160.hex()}")
    print(f"CPUs available: {cpu_count()}")
    print()

    # Priority d values based on recent patterns
    priority_d = [1, 2, 5, 8, 3, 4, 6, 7]

    for d in priority_d:
        if d not in K:
            continue

        k_d = K[d]

        # Calculate m range
        m_min = max(1, (2 * K_70 + 1 + k_d - 1) // k_d)
        m_max = (MIN_K71 + 2 * K_70) // k_d

        if m_min > m_max:
            continue

        range_size = m_max - m_min + 1

        if range_size > 100_000_000_000:  # 100B limit
            print(f"d={d}: {range_size:,} candidates (too large, skipping)")
            continue

        print(f"d={d}: Searching {range_size:,} candidates with {cpu_count()} workers...")

        # Split into chunks for parallel processing
        chunk_size = max(10000, range_size // (cpu_count() * 10))
        chunks = []
        for start in range(m_min, m_max + 1, chunk_size):
            end = min(start + chunk_size, m_max + 1)
            chunks.append((d, start, end, k_d, TARGET_HASH160))

        # Process in parallel
        with Pool(cpu_count()) as pool:
            results = pool.map(search_range, chunks)

        # Check for matches
        for result in results:
            if result:
                for d_found, m_found, k71_found in result:
                    print(f"\n🎉 FOUND! 🎉")
                    print(f"d[71] = {d_found}")
                    print(f"m[71] = {m_found:,}")
                    print(f"k[71] = {k71_found:,}")
                    print(f"k[71] hex = {hex(k71_found)}")
                    return

        print(f"d={d}: ✗")

    print("\nNo match found in priority d values.")

if __name__ == "__main__":
    main()
