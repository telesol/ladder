#!/usr/bin/env python3
"""
TASK 2: Offset Formula Verification

Objective: Verify and extend Mistral's offset formula:
offset[n] = (-1)^(n+1) × 2^f(n) × 5^g(n) × h(n)

Sub-tasks:
2.1. Compute offset[n] = k[n] - 9*k[n-3] for n=10 to n=70
2.2. Factorize each offset completely
2.3. Verify Mistral's f(n) = floor(n/3) - 2 hypothesis
2.4. Verify prime selection: 17 for n ≡ 0,3,4 (mod 6), 19 for n ≡ 2 (mod 6)
2.5. Find exceptions and patterns for n ≥ 40

NO ASSUMPTIONS. ALL DATA DERIVED FROM DATABASE.
"""

import sqlite3
from collections import defaultdict
import json

# Database path
DB_PATH = "/home/rkh/ladder/db/kh.db"

def get_k_values(n_min=1, n_max=90):
    """Query all k values from database for puzzle range."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    k_values = {}

    # Query all keys in range
    cursor.execute("""
        SELECT puzzle_id, priv_hex
        FROM keys
        WHERE puzzle_id >= ? AND puzzle_id <= ?
        ORDER BY puzzle_id
    """, (n_min, n_max))

    for puzzle_id, priv_hex in cursor.fetchall():
        # Convert hex to decimal
        k_values[puzzle_id] = int(priv_hex, 16)

    conn.close()
    return k_values

def prime_factorization(n):
    """
    Complete prime factorization of n.
    Returns dict {prime: power}.
    """
    if n == 0:
        return {0: 1}

    # Handle sign
    sign = 1 if n >= 0 else -1
    n = abs(n)

    factors = {}

    # Factor out 2s
    count = 0
    while n % 2 == 0:
        count += 1
        n //= 2
    if count > 0:
        factors[2] = count

    # Try odd primes
    p = 3
    while p * p <= n:
        count = 0
        while n % p == 0:
            count += 1
            n //= p
        if count > 0:
            factors[p] = count
        p += 2

    # Remaining n is prime (if > 1)
    if n > 1:
        factors[n] = 1

    # Add sign as special marker
    if sign == -1:
        factors[-1] = 1

    return factors

def format_factorization(factors):
    """Format factorization dict as readable string."""
    if not factors:
        return "1"

    # Handle sign
    sign_str = ""
    if -1 in factors:
        sign_str = "-"
        factors = {k: v for k, v in factors.items() if k != -1}

    # Handle zero
    if 0 in factors:
        return "0"

    # Format as p1^e1 × p2^e2 × ...
    parts = []
    for prime in sorted(factors.keys()):
        power = factors[prime]
        if power == 1:
            parts.append(str(prime))
        else:
            parts.append(f"{prime}^{power}")

    return sign_str + " × ".join(parts) if parts else "1"

def get_power_of_prime(factors, p):
    """Get the power of prime p in factorization."""
    return factors.get(p, 0)

def compute_offsets_and_verify():
    """
    Main computation and verification function.
    """
    print("=" * 80)
    print("OFFSET FORMULA VERIFICATION")
    print("=" * 80)
    print()

    # Get all k values from database
    print("Loading k values from database...")
    k_values = get_k_values(1, 90)
    print(f"Loaded {len(k_values)} k values")
    print(f"Available puzzles: {sorted(k_values.keys())}")
    print()

    # Compute offsets for n=10 to n=70
    offsets = {}
    offset_factors = {}

    print("Computing offsets: offset[n] = k[n] - 9*k[n-3]")
    print("-" * 80)

    for n in range(10, 71):
        if n in k_values and (n-3) in k_values:
            offset = k_values[n] - 9 * k_values[n-3]
            offsets[n] = offset

            # Factorize
            factors = prime_factorization(offset)
            offset_factors[n] = factors

            # Print
            print(f"n={n:2d}: offset = {offset:20d}")
            print(f"       factorization = {format_factorization(factors)}")
            print()

    print(f"\nTotal offsets computed: {len(offsets)}")
    print("=" * 80)
    print()

    # === VERIFICATION SECTION ===
    print("=" * 80)
    print("FORMULA VERIFICATION")
    print("=" * 80)
    print()

    # 2.3. Verify f(n) = floor(n/3) - 2 for power of 2
    print("2.3. POWER OF 2: Verify f(n) = floor(n/3) - 2")
    print("-" * 80)

    f_matches = 0
    f_total = 0
    f_exceptions = []

    for n in sorted(offsets.keys()):
        factors = offset_factors[n]
        power_of_2 = get_power_of_prime(factors, 2)
        expected_f = n // 3 - 2

        match = power_of_2 == expected_f
        f_total += 1
        if match:
            f_matches += 1
        else:
            f_exceptions.append((n, power_of_2, expected_f))

        marker = "✓" if match else "✗"
        print(f"n={n:2d}: 2^{power_of_2} | expected: 2^{expected_f} | {marker}")

    print()
    print(f"RESULT: {f_matches}/{f_total} matches ({100*f_matches/f_total:.1f}%)")
    if f_exceptions:
        print(f"Exceptions: {len(f_exceptions)}")
        for n, actual, expected in f_exceptions[:10]:
            print(f"  n={n}: actual f={actual}, expected f={expected}, diff={actual-expected}")
    print()

    # 2.4. Verify prime selection hypothesis
    print("2.4. PRIME SELECTION: 17 for n ≡ 0,3,4 (mod 6), 19 for n ≡ 2 (mod 6)")
    print("-" * 80)

    prime_17_count = 0
    prime_19_count = 0
    prime_17_correct = 0
    prime_19_correct = 0

    for n in sorted(offsets.keys()):
        factors = offset_factors[n]
        has_17 = 17 in factors
        has_19 = 19 in factors

        n_mod_6 = n % 6
        expected_17 = n_mod_6 in [0, 3, 4]
        expected_19 = n_mod_6 == 2

        if has_17:
            prime_17_count += 1
            if expected_17:
                prime_17_correct += 1
            print(f"n={n:2d} (mod 6 = {n_mod_6}): has 17 | expected: {expected_17} | {'✓' if expected_17 else '✗'}")

        if has_19:
            prime_19_count += 1
            if expected_19:
                prime_19_correct += 1
            print(f"n={n:2d} (mod 6 = {n_mod_6}): has 19 | expected: {expected_19} | {'✓' if expected_19 else '✗'}")

    print()
    print(f"Prime 17: appears in {prime_17_count}/61 offsets ({100*prime_17_count/61:.1f}%)")
    print(f"  Matches hypothesis: {prime_17_correct}/{prime_17_count} ({100*prime_17_correct/prime_17_count:.1f}% if > 0 else 0)")
    print(f"Prime 19: appears in {prime_19_count}/61 offsets ({100*prime_19_count/61:.1f}%)")
    print(f"  Matches hypothesis: {prime_19_correct}/{prime_19_count} ({100*prime_19_correct/prime_19_count:.1f}% if > 0 else 0)")
    print()

    # 2.5. Analyze patterns for n ≥ 40
    print("2.5. PATTERNS FOR n ≥ 40")
    print("-" * 80)

    large_n_offsets = {n: offset_factors[n] for n in offsets.keys() if n >= 40}

    # Count prime appearances in n >= 40
    prime_counts_large = defaultdict(int)
    for n, factors in large_n_offsets.items():
        for prime in factors.keys():
            if prime > 0:  # Skip sign marker
                prime_counts_large[prime] += 1

    print(f"Prime distribution for n ≥ 40 ({len(large_n_offsets)} offsets):")
    for prime in sorted(prime_counts_large.keys())[:20]:  # Top 20 primes
        count = prime_counts_large[prime]
        print(f"  {prime:6d}: appears in {count:2d}/31 offsets ({100*count/31:.1f}%)")
    print()

    # Sign pattern verification
    print("SIGN PATTERN: (-1)^(n+1)")
    print("-" * 80)

    sign_matches = 0
    sign_total = 0

    for n in sorted(offsets.keys()):
        factors = offset_factors[n]
        is_negative = -1 in factors
        expected_negative = ((n + 1) % 2 == 1)  # (-1)^(n+1) is negative when n+1 is odd

        match = is_negative == expected_negative
        sign_total += 1
        if match:
            sign_matches += 1

        marker = "✓" if match else "✗"
        actual_sign = "-" if is_negative else "+"
        expected_sign = "-" if expected_negative else "+"
        print(f"n={n:2d}: actual={actual_sign} | expected={expected_sign} | {marker}")

    print()
    print(f"RESULT: {sign_matches}/{sign_total} matches ({100*sign_matches/sign_total:.1f}%)")
    print()

    # Additional analysis: Power of 5
    print("POWER OF 5 ANALYSIS")
    print("-" * 80)

    power_5_dist = defaultdict(int)
    for n, factors in offset_factors.items():
        power = get_power_of_prime(factors, 5)
        power_5_dist[power] += 1

    for power in sorted(power_5_dist.keys()):
        count = power_5_dist[power]
        print(f"5^{power}: {count}/61 offsets ({100*count/61:.1f}%)")

    # Find cases where g(n) != 1
    power_5_exceptions = []
    for n, factors in offset_factors.items():
        power = get_power_of_prime(factors, 5)
        if power != 1:
            power_5_exceptions.append((n, power))

    print()
    print(f"Cases where 5^g(n) with g(n) != 1: {len(power_5_exceptions)}")
    for n, power in power_5_exceptions[:10]:
        print(f"  n={n}: 5^{power}")
    print()

    # Overall prime distribution
    print("OVERALL PRIME DISTRIBUTION (all n=10-70)")
    print("-" * 80)

    prime_counts_all = defaultdict(int)
    for n, factors in offset_factors.items():
        for prime in factors.keys():
            if prime > 0:  # Skip sign marker
                prime_counts_all[prime] += 1

    # Top 30 primes
    top_primes = sorted(prime_counts_all.items(), key=lambda x: x[1], reverse=True)[:30]
    for prime, count in top_primes:
        print(f"  {prime:10d}: appears in {count:2d}/61 offsets ({100*count/61:.1f}%)")
    print()

    # Save results to JSON
    results = {
        "offsets": {str(n): offset for n, offset in offsets.items()},
        "factorizations": {str(n): format_factorization(f) for n, f in offset_factors.items()},
        "verification": {
            "f(n)_floor(n/3)-2": {
                "matches": f_matches,
                "total": f_total,
                "percentage": 100 * f_matches / f_total,
                "exceptions": [{"n": n, "actual": a, "expected": e} for n, a, e in f_exceptions]
            },
            "sign_pattern_(-1)^(n+1)": {
                "matches": sign_matches,
                "total": sign_total,
                "percentage": 100 * sign_matches / sign_total
            },
            "prime_17_hypothesis": {
                "appearances": prime_17_count,
                "correct_predictions": prime_17_correct,
                "total_offsets": 61,
                "percentage": 100 * prime_17_count / 61
            },
            "prime_19_hypothesis": {
                "appearances": prime_19_count,
                "correct_predictions": prime_19_correct,
                "total_offsets": 61,
                "percentage": 100 * prime_19_count / 61
            }
        },
        "prime_distribution": {str(p): c for p, c in top_primes}
    }

    with open("/home/rkh/ladder/offset_verification_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("=" * 80)
    print("Results saved to: offset_verification_results.json")
    print("=" * 80)

    return offsets, offset_factors, results

if __name__ == "__main__":
    compute_offsets_and_verify()
