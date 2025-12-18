#!/usr/bin/env python3
"""
Bitcoin Puzzle Configuration - Central data source from DB.
No hardcoded targets, no hardcoded keys.
All data loaded from the database.
"""

import sqlite3
from typing import Dict, List, Optional
from functools import lru_cache

DB_PATH = "/home/solo/LA/db/kh.db"
TOTAL_PUZZLES = 160


@lru_cache(maxsize=1)
def get_known_keys() -> Dict[int, int]:
    """
    Load all known puzzle keys from database.
    Returns dict: {puzzle_number: private_key_decimal}
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT puzzle_id, priv_hex
        FROM keys
        WHERE puzzle_id IS NOT NULL
        ORDER BY puzzle_id
    """)

    keys = {}
    for puzzle_id, hex_key in cur.fetchall():
        hex_clean = hex_key.replace('0x', '').lstrip('0') or '0'
        keys[puzzle_id] = int(hex_clean, 16)

    conn.close()
    return keys


def get_key(puzzle_num: int) -> Optional[int]:
    """Get the private key for a specific puzzle, or None if unsolved."""
    return get_known_keys().get(puzzle_num)


def get_solved() -> List[int]:
    """Get list of all solved puzzle numbers."""
    return sorted(get_known_keys().keys())


def get_unsolved() -> List[int]:
    """Get list of all unsolved puzzle numbers (all targets)."""
    known = set(get_known_keys().keys())
    all_puzzles = set(range(1, TOTAL_PUZZLES + 1))
    return sorted(all_puzzles - known)


def get_puzzle_range(puzzle_num: int) -> tuple:
    """Get the valid range [low, high] for a puzzle number."""
    low = 2 ** (puzzle_num - 1)
    high = 2 ** puzzle_num - 1
    return (low, high)


def get_position_pct(puzzle_num: int) -> Optional[float]:
    """Get the position percentage of a solved key within its range."""
    key = get_key(puzzle_num)
    if key is None:
        return None

    low, high = get_puzzle_range(puzzle_num)
    return (key - low) / (high - low) * 100


def summary() -> Dict:
    """Get summary statistics."""
    known = get_known_keys()
    unsolved = get_unsolved()

    return {
        "total_puzzles": TOTAL_PUZZLES,
        "known_count": len(known),
        "unsolved_count": len(unsolved),
        "known_puzzles": sorted(known.keys()),
        "unsolved_puzzles": unsolved,
    }


# Module-level constants loaded from DB
KEYS = get_known_keys()
SOLVED = get_solved()
UNSOLVED = get_unsolved()


if __name__ == "__main__":
    s = summary()
    print(f"Total puzzles: {s['total_puzzles']}")
    print(f"Known keys: {s['known_count']}")
    print(f"Unsolved (targets): {s['unsolved_count']}")
    print(f"\nKnown: {s['known_puzzles']}")
    print(f"\nUnsolved: {s['unsolved_puzzles']}")
