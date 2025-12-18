#!/usr/bin/env python3
"""
Pure Mathematical Formula Derivation
NO PREDICTIONS - Only verified math from the database

Usage:
    python derive_formula.py [--all] [--test N] [--deep]
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "db" / "kh.db"

def load_keys():
    """Load all known keys from database"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
    rows = cur.fetchall()
    conn.close()

    keys = {}
    for puzzle_id, priv_hex in rows:
        if puzzle_id is None or priv_hex is None:
            continue
        # Convert hex to int
        try:
            val = int(priv_hex, 16)
            keys[puzzle_id] = val
        except (ValueError, TypeError):
            continue

    return keys

def test_formula(keys, formula_fn, name, max_n=70):
    """Test a formula against all known keys"""
    results = {"verified": [], "failed": [], "skipped": []}

    for n in range(1, max_n + 1):
        if n not in keys:
            continue

        try:
            predicted = formula_fn(keys, n)
            actual = keys[n]

            if predicted == actual:
                results["verified"].append(n)
            else:
                results["failed"].append({
                    "n": n,
                    "predicted": predicted,
                    "actual": actual,
                    "diff": actual - predicted
                })
        except Exception as e:
            results["skipped"].append({"n": n, "error": str(e)})

    print(f"\n=== Formula: {name} ===")
    print(f"Verified: {len(results['verified'])} keys: {results['verified'][:10]}...")
    print(f"Failed: {len(results['failed'])} keys")
    for f in results["failed"][:5]:
        print(f"  k{f['n']}: expected {f['actual']}, got {f['predicted']} (diff={f['diff']})")

    return results

def find_relationship(keys, n, target):
    """Find what relationship produces target from previous keys"""
    if n < 2:
        return None

    results = []

    # Test: k_n = k_a * k_b
    for a in range(1, n):
        for b in range(a, n):
            if a in keys and b in keys:
                if keys[a] * keys[b] == target:
                    results.append(f"k{n} = k{a} × k{b} = {keys[a]} × {keys[b]} = {target}")

    # Test: k_n = k_a²
    for a in range(1, n):
        if a in keys:
            if keys[a] ** 2 == target:
                results.append(f"k{n} = k{a}² = {keys[a]}² = {target}")

    # Test: k_n = k_a * M + C (for small M and C)
    for a in range(1, n):
        if a in keys:
            for m in range(1, 50):
                diff = target - keys[a] * m
                if abs(diff) < 500:
                    results.append(f"k{n} = k{a}×{m} + ({diff}) = {keys[a]}×{m} + ({diff}) = {target}")

    # Test: k_n = k_a * M + k_b
    for a in range(1, n):
        for b in range(1, n):
            if a in keys and b in keys and a != b:
                for m in range(1, 30):
                    if keys[a] * m + keys[b] == target:
                        results.append(f"k{n} = k{a}×{m} + k{b} = {keys[a]}×{m} + {keys[b]} = {target}")
                    if keys[a] * m - keys[b] == target:
                        results.append(f"k{n} = k{a}×{m} - k{b} = {keys[a]}×{m} - {keys[b]} = {target}")

    # Test: k_n = k_a² + C
    for a in range(1, n):
        if a in keys:
            diff = target - keys[a] ** 2
            if abs(diff) < 500:
                results.append(f"k{n} = k{a}² + ({diff}) = {keys[a]}² + ({diff}) = {target}")

    return results

def derive_all(keys, start=5, end=70):
    """Derive formulas for all keys"""
    print("=" * 60)
    print("FORMULA DERIVATION - Pure Math from Database")
    print("=" * 60)

    for n in range(start, end + 1):
        if n not in keys:
            print(f"\nk{n}: NOT IN DATABASE (UNKNOWN)")
            continue

        target = keys[n]
        formulas = find_relationship(keys, n, target)

        print(f"\nk{n} = {target}")
        if formulas:
            print(f"  Found {len(formulas)} formula(s):")
            for f in formulas[:10]:  # Limit output
                print(f"    {f}")
        else:
            print("  NO SIMPLE FORMULA FOUND")

def extract_multipliers(keys):
    """Extract the multiplier sequence from verified formulas"""
    print("\n" + "=" * 60)
    print("MULTIPLIER SEQUENCE EXTRACTION")
    print("=" * 60)

    # Known: k7 uses 9, k8 uses 13, k11 uses 19, k12 uses 12
    verified = {
        7: ("k2×9 + k6", 9),
        8: ("k5×13 - k6", 13),
        11: ("k6×19 + k8", 19),
        12: ("k8×12 - 5", 12),
        14: ("k11×9 + 149", 9),  # 9 returns!
    }

    print("\nVerified multipliers from formulas:")
    for n, (formula, mult) in verified.items():
        print(f"  k{n}: multiplier = {mult} (from {formula})")

    print("\nMultiplier sequence: 9 → 13 → 19 → 12 → 9 (cycles?)")
    print("Differences: +4, +6, -7, -3")
    print("\nThis is NOT arithmetic or geometric progression.")
    print("Hypothesis: The multipliers may be derived from key values themselves.")

def main():
    print("Loading keys from database...")
    keys = load_keys()
    print(f"Loaded {len(keys)} keys: {sorted(keys.keys())[:15]}... up to {max(keys.keys())}")

    # Show first 14 keys
    print("\n=== First 14 Keys (Decimal) ===")
    for n in range(1, 15):
        if n in keys:
            print(f"k{n} = {keys[n]}")

    if "--all" in sys.argv:
        derive_all(keys, 5, 70)
    elif "--test" in sys.argv:
        idx = sys.argv.index("--test")
        n = int(sys.argv[idx + 1])
        if n in keys:
            formulas = find_relationship(keys, n, keys[n])
            print(f"\nk{n} = {keys[n]}")
            print(f"Found {len(formulas)} formula(s):")
            for f in formulas:
                print(f"  {f}")
        else:
            print(f"k{n} NOT IN DATABASE")
    else:
        # Default: derive k5-k14 and extract multipliers
        derive_all(keys, 5, 14)
        extract_multipliers(keys)

if __name__ == "__main__":
    main()
