#!/usr/bin/env python3
"""
Data Loader - Load and understand Bitcoin puzzle data

The AI Brain needs to understand what data we're working with.
This module helps the AI "see" and "understand" the puzzle structure.
"""

import csv
from pathlib import Path
from typing import Dict, Tuple

def load_puzzles_from_csv(csv_path: str) -> Dict[int, dict]:
    """
    Load Bitcoin puzzles from CSV and understand their structure.

    The AI needs to understand:
    1. Each puzzle has a 64-char hex key (32 bytes total)
    2. The key has two halves: first 16 bytes, last 16 bytes
    3. For small puzzles, first half is zeros, last half has the value
    4. For large puzzles, both halves may have data

    Returns:
        Dictionary mapping puzzle_num -> puzzle_data

        puzzle_data = {
            'full_hex': 64-char hex string,
            'first_16_bytes': bytes (first half),
            'last_16_bytes': bytes (second half),
            'address': Bitcoin address
        }
    """
    puzzles = {}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                puzzle_num = int(row['puzzle'])
            except ValueError:
                continue  # Skip header

            full_hex = row['key_hex_64'].strip()

            if len(full_hex) != 64:
                print(f"⚠️  Puzzle {puzzle_num}: key length {len(full_hex)}, expected 64")
                continue

            # Split into two halves
            first_32_hex = full_hex[:32]   # First 16 bytes
            last_32_hex = full_hex[32:64]  # Last 16 bytes

            puzzles[puzzle_num] = {
                'full_hex': full_hex,
                'first_16_bytes': bytes.fromhex(first_32_hex),
                'last_16_bytes': bytes.fromhex(last_32_hex),
                'address': row['address'],
                'puzzle_num': puzzle_num
            }

    return puzzles


def analyze_data_structure(puzzles: Dict[int, dict]) -> dict:
    """
    AI analyzes the data structure to understand what it's working with.

    Questions the AI should answer:
    1. Which half has the actual puzzle data?
    2. Are there patterns in how the data is distributed?
    3. What range of puzzles do we have?
    """
    analysis = {
        'total_puzzles': len(puzzles),
        'first_half_nonzero': [],
        'last_half_nonzero': [],
        'both_halves_nonzero': [],
        'puzzle_range': (min(puzzles.keys()), max(puzzles.keys()))
    }

    for num, puzzle in puzzles.items():
        first_nonzero = any(b != 0 for b in puzzle['first_16_bytes'])
        last_nonzero = any(b != 0 for b in puzzle['last_16_bytes'])

        if first_nonzero:
            analysis['first_half_nonzero'].append(num)
        if last_nonzero:
            analysis['last_half_nonzero'].append(num)
        if first_nonzero and last_nonzero:
            analysis['both_halves_nonzero'].append(num)

    return analysis


def ai_report_data_understanding(puzzles: Dict[int, dict]):
    """
    AI reports its understanding of the data to the human.

    This is the AI being transparent about what it sees.
    """
    analysis = analyze_data_structure(puzzles)

    print("\n" + "="*70)
    print("AI BRAIN: Data Understanding Report")
    print("="*70)

    print(f"\n📊 Dataset Overview:")
    print(f"   Total puzzles loaded: {analysis['total_puzzles']}")
    print(f"   Puzzle range: {analysis['puzzle_range'][0]} to {analysis['puzzle_range'][1]}")

    print(f"\n🔍 Data Distribution Analysis:")
    print(f"   First 16 bytes have data: {len(analysis['first_half_nonzero'])} puzzles")
    print(f"   Last 16 bytes have data: {len(analysis['last_half_nonzero'])} puzzles")
    print(f"   Both halves have data: {len(analysis['both_halves_nonzero'])} puzzles")

    # AI's conclusion
    print(f"\n🧠 AI Conclusion:")
    if len(analysis['last_half_nonzero']) > len(analysis['first_half_nonzero']):
        print(f"   ✅ Primary data is in LAST 16 bytes (last 32 hex chars)")
        print(f"   ✅ First 16 bytes are mostly zeros (padding)")
        which_half = 'last'
    elif len(analysis['first_half_nonzero']) > len(analysis['last_half_nonzero']):
        print(f"   ✅ Primary data is in FIRST 16 bytes (first 32 hex chars)")
        print(f"   ✅ Last 16 bytes are mostly zeros")
        which_half = 'first'
    else:
        print(f"   ⚠️  Data distributed across both halves - need manual inspection")
        which_half = 'both'

    # Show examples
    print(f"\n📝 Example Puzzles:")
    for num in [1, 2, 10, 70]:
        if num in puzzles:
            p = puzzles[num]
            print(f"\n   Puzzle {num}:")
            print(f"      Full:   {p['full_hex']}")
            print(f"      First:  {p['first_16_bytes'].hex()}")
            print(f"      Last:   {p['last_16_bytes'].hex()}")

    print("\n" + "="*70)

    return which_half


if __name__ == "__main__":
    # Test
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"

    print("AI Brain: Loading and analyzing data...")
    puzzles = load_puzzles_from_csv(csv_path)

    which_half = ai_report_data_understanding(puzzles)

    print(f"\n✅ AI understands: Work with the {which_half.upper()} 16 bytes")
