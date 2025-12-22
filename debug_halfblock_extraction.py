#!/usr/bin/env python3
"""
Debug: Check what half-block values we're actually extracting
"""

import sqlite3

conn = sqlite3.connect('db/kh.db')
cursor = conn.cursor()

# Get first few half-blocks
cursor.execute("""
    SELECT bits, actual_hex
    FROM lcg_residuals
    WHERE bits BETWEEN 1 AND 10
    ORDER BY bits
""")

print("=== DEBUGGING HALF-BLOCK EXTRACTION ===\n")

for bits, hex_str in cursor.fetchall():
    print(f"Puzzle {bits}:")
    print(f"  Raw from DB: {hex_str}")

    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]

    print(f"  After removing 0x: {hex_str}")
    print(f"  Length: {len(hex_str)} chars")

    # Try both halves
    first_half = hex_str[:32]
    second_half = hex_str[-32:]

    print(f"  First half (first 32 chars):  {first_half}")
    print(f"  Second half (last 32 chars):  {second_half}")

    # Convert to bytes
    try:
        first_bytes = bytes.fromhex(first_half)
        second_bytes = bytes.fromhex(second_half)
        print(f"  First half bytes:  {list(first_bytes)}")
        print(f"  Second half bytes: {list(second_bytes)}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print()

conn.close()
