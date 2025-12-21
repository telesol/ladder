#!/usr/bin/env python3
"""
Distributed k[71] search - split work across multiple machines
"""

import sqlite3
import hashlib
import sys
import coincurve

# Load k-values
conn = sqlite3.connect('/home/solo/LA/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
K = {row[0]: int(row[1], 16) for row in cursor.fetchall()}
conn.close()

TARGET_HASH160 = bytes.fromhex('f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8')
BASE = 2**71 + 2*K[70]  # 4,302,057,189,444,869,987,810
MIN_K71 = 2**70
MAX_K71 = 2**71 - 1

def privkey_to_hash160(privkey):
    privkey_bytes = privkey.to_bytes(32, 'big')
    pk = coincurve.PrivateKey(privkey_bytes)
    pubkey = pk.public_key.format(compressed=True)
    sha256_hash = hashlib.sha256(pubkey).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    return ripemd160.digest()

def search_d(d, start_m, end_m):
    """Search a range of m values for given d"""
    k_d = K[d]
    checked = 0

    for m in range(start_m, end_m):
        k71 = BASE - m * k_d

        if MIN_K71 <= k71 <= MAX_K71:
            checked += 1
            if checked % 100000 == 0:
                print(f"  d={d} checked {checked:,}...", flush=True)

            h160 = privkey_to_hash160(k71)
            if h160 == TARGET_HASH160:
                print(f"\n{'='*60}")
                print(f"FOUND! d={d}, m={m}")
                print(f"k[71] = {k71}")
                print(f"k[71] hex = {hex(k71)}")
                print(f"{'='*60}")
                return True

    return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: distributed_search.py <d> <start_m> <end_m>")
        sys.exit(1)

    d = int(sys.argv[1])
    start_m = int(sys.argv[2])
    end_m = int(sys.argv[3])

    print(f"Searching d={d}, m=[{start_m:,}, {end_m:,})")
    search_d(d, start_m, end_m)
