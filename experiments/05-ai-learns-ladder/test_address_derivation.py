#!/usr/bin/env python3
"""
Test address derivation from CSV keys.

This checks if the addresses in the CSV match the private keys.
"""

import pandas as pd
from pathlib import Path
from crypto_validator import private_key_to_address


def test_csv_addresses():
    """Test that CSV addresses match their private keys."""
    csv_path = Path(__file__).parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"
    df = pd.read_csv(csv_path)

    print("="*80)
    print("TESTING CSV ADDRESS DERIVATION")
    print("="*80)
    print()

    # Test puzzles 1-10
    for puzzle_num in range(1, 11):
        puzzle = df[df['puzzle'] == puzzle_num].iloc[0]

        private_key = puzzle['key_hex_64']
        expected_address = puzzle['address']

        # Try both compressed and uncompressed
        address_uncompressed = private_key_to_address(private_key, compressed=False)
        address_compressed = private_key_to_address(private_key, compressed=True)

        # Check which matches
        if address_uncompressed == expected_address:
            match = "✅ uncompressed"
            status = "✅"
        elif address_compressed == expected_address:
            match = "✅ compressed"
            status = "✅"
        else:
            match = "❌ no match"
            status = "❌"

        print(f"{status} Puzzle {puzzle_num}:")
        print(f"   Private key: {private_key}")
        print(f"   Expected:    {expected_address}")
        if address_uncompressed != expected_address and address_compressed != expected_address:
            print(f"   Generated (uncompressed): {address_uncompressed}")
            print(f"   Generated (compressed):   {address_compressed}")
        print(f"   Match: {match}")
        print()


if __name__ == "__main__":
    test_csv_addresses()
