#!/usr/bin/env python3
"""
k[n] Prime Factorization Analysis
Analyzes prime factorization patterns in Bitcoin puzzle private keys
"""

import sqlite3
from sympy import factorint, isprime, primefactors
from collections import Counter, defaultdict
from pathlib import Path

# Database path
DB_PATH = "/home/rkh/ladder/db/kh.db"

def query_keys(db_path, start=1, end=70):
    """Query private keys from database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT puzzle_id, priv_hex
    FROM keys
    WHERE puzzle_id BETWEEN ? AND ?
    ORDER BY puzzle_id
    """

    cursor.execute(query, (start, end))
    results = cursor.fetchall()
    conn.close()

    return results

def analyze_factorizations(keys_data):
    """
    Perform complete factorization analysis
    Returns: factorizations, prime_counts, prime_k, highly_composite, mod3_analysis
    """
    factorizations = {}
    prime_counts = Counter()
    prime_k = []
    highly_composite = []

    for puzzle_id, priv_hex in keys_data:
        # Convert hex to integer
        k = int(priv_hex, 16)

        # Get prime factorization
        if k == 0:
            factorizations[puzzle_id] = {0: 1}
            continue
        elif k == 1:
            factorizations[puzzle_id] = {}
            continue

        factors = factorint(k)
        factorizations[puzzle_id] = factors

        # Check if k is prime
        if isprime(k):
            prime_k.append(puzzle_id)

        # Count primes < 100
        for prime in factors.keys():
            if prime < 100:
                prime_counts[prime] += factors[prime]

        # Find highly composite numbers (many distinct prime factors)
        distinct_primes = len(factors)
        total_factors = sum(factors.values())

        # Consider "highly composite" if >= 4 distinct primes or total factor count >= 6
        if distinct_primes >= 4 or total_factors >= 6:
            highly_composite.append({
                'puzzle_id': puzzle_id,
                'k': k,
                'distinct_primes': distinct_primes,
                'total_factors': total_factors,
                'factors': factors
            })

    # Analyze mod 3 sibling patterns
    mod3_analysis = analyze_mod3_siblings(factorizations, keys_data)

    return factorizations, prime_counts, prime_k, highly_composite, mod3_analysis

def analyze_mod3_siblings(factorizations, keys_data):
    """
    Check if k[n] shares factors with k[n mod 3 siblings]
    Siblings: n, n+3, n+6, n+9, ... all have same n mod 3
    """
    # Group by n mod 3
    mod3_groups = defaultdict(list)
    k_values = {}

    for puzzle_id, priv_hex in keys_data:
        k = int(priv_hex, 16)
        k_values[puzzle_id] = k
        mod3_groups[puzzle_id % 3].append(puzzle_id)

    sibling_analysis = {}

    for mod_class in [0, 1, 2]:
        siblings = mod3_groups[mod_class]
        sibling_analysis[mod_class] = {
            'siblings': siblings,
            'shared_factors': []
        }

        # Check pairs of siblings for common factors
        for i, n1 in enumerate(siblings):
            for n2 in siblings[i+1:]:
                if n1 in factorizations and n2 in factorizations:
                    factors1 = set(factorizations[n1].keys())
                    factors2 = set(factorizations[n2].keys())
                    common = factors1 & factors2

                    if common and 0 not in common:  # Ignore the 0 case
                        sibling_analysis[mod_class]['shared_factors'].append({
                            'n1': n1,
                            'n2': n2,
                            'k1': k_values[n1],
                            'k2': k_values[n2],
                            'common_primes': sorted(list(common))
                        })

    return sibling_analysis

def format_factorization(factors):
    """Format factorization as string"""
    if not factors:
        return "1"
    if 0 in factors:
        return "0"

    parts = []
    for prime in sorted(factors.keys()):
        exp = factors[prime]
        if exp == 1:
            parts.append(str(prime))
        else:
            parts.append(f"{prime}^{exp}")

    return " × ".join(parts)

def generate_report(factorizations, prime_counts, prime_k, highly_composite, mod3_analysis, keys_data):
    """Generate markdown report"""

    # Create k_values mapping
    k_values = {}
    for puzzle_id, priv_hex in keys_data:
        k_values[puzzle_id] = int(priv_hex, 16)

    report = []
    report.append("# k[n] Prime Factorization Patterns Analysis\n")
    report.append("Analysis of private key (k[n]) prime factorizations for Bitcoin puzzles 1-70.\n")
    report.append(f"Generated: 2025-12-21\n")

    # Section 1: Complete Factorization Table
    report.append("\n## 1. Complete Factorization Table\n")
    report.append("| n | k[n] (decimal) | k[n] (hex) | Prime Factorization |")
    report.append("|---|----------------|------------|---------------------|")

    for puzzle_id, priv_hex in keys_data:
        k = k_values[puzzle_id]
        factors = factorizations.get(puzzle_id, {})
        factorization_str = format_factorization(factors)

        # Truncate very long numbers for display
        k_dec_str = str(k) if len(str(k)) <= 25 else f"{str(k)[:22]}..."
        hex_str = priv_hex if len(priv_hex) <= 25 else f"{priv_hex[:22]}..."

        report.append(f"| {puzzle_id} | {k_dec_str} | {hex_str} | {factorization_str} |")

    # Section 2: Prime Frequency Statistics
    report.append("\n## 2. Prime Frequency Statistics (p < 100)\n")
    report.append("Count of how many times each prime p < 100 appears in factorizations.\n")
    report.append("\n| Prime | Occurrences | Percentage |")
    report.append("|-------|-------------|------------|")

    total_occurrences = sum(prime_counts.values())
    for prime in sorted(prime_counts.keys()):
        count = prime_counts[prime]
        percentage = (count / 70) * 100  # Out of 70 puzzles
        report.append(f"| {prime} | {count} | {percentage:.1f}% |")

    report.append(f"\nTotal prime factor occurrences (p < 100): {total_occurrences}")

    # Top 10 most common primes
    report.append("\n### Top 10 Most Common Primes\n")
    top_primes = prime_counts.most_common(10)
    report.append("| Rank | Prime | Occurrences |")
    report.append("|------|-------|-------------|")
    for rank, (prime, count) in enumerate(top_primes, 1):
        report.append(f"| {rank} | {prime} | {count} |")

    # Section 3: Prime k[n]
    report.append("\n## 3. Prime k[n] Values\n")
    report.append(f"Found {len(prime_k)} prime values among k[1] to k[70]:\n")

    if prime_k:
        report.append("\n| n | k[n] (prime) |")
        report.append("|---|--------------|")
        for n in prime_k:
            k = k_values[n]
            report.append(f"| {n} | {k} |")
    else:
        report.append("\nNo prime k[n] values found in range.")

    # Section 4: Highly Composite k[n]
    report.append("\n## 4. Highly Composite k[n] Values\n")
    report.append("k[n] values with many prime factors (≥4 distinct primes or ≥6 total prime factors):\n")

    if highly_composite:
        report.append("\n| n | k[n] | Distinct Primes | Total Factors | Factorization |")
        report.append("|---|------|-----------------|---------------|---------------|")

        # Sort by distinct primes (descending), then by total factors
        highly_composite.sort(key=lambda x: (x['distinct_primes'], x['total_factors']), reverse=True)

        for hc in highly_composite:
            n = hc['puzzle_id']
            k_str = str(hc['k']) if len(str(hc['k'])) <= 20 else f"{str(hc['k'])[:17]}..."
            factorization_str = format_factorization(hc['factors'])
            report.append(f"| {n} | {k_str} | {hc['distinct_primes']} | {hc['total_factors']} | {factorization_str} |")
    else:
        report.append("\nNo highly composite k[n] values found in range.")

    # Section 5: Mod 3 Sibling Analysis
    report.append("\n## 5. Mod 3 Sibling Analysis\n")
    report.append("Analysis of whether k[n] shares factors with k[m] where n ≡ m (mod 3).\n")

    for mod_class in [0, 1, 2]:
        analysis = mod3_analysis[mod_class]
        siblings = analysis['siblings']
        shared = analysis['shared_factors']

        report.append(f"\n### Class: n ≡ {mod_class} (mod 3)\n")
        report.append(f"Siblings: {', '.join(map(str, siblings))}\n")

        if shared:
            report.append(f"\nFound {len(shared)} pairs with shared prime factors:\n")
            report.append("\n| n1 | n2 | Common Primes |")
            report.append("|----|----|--------------:|")

            for pair in shared:
                primes_str = ', '.join(map(str, pair['common_primes']))
                report.append(f"| {pair['n1']} | {pair['n2']} | {primes_str} |")
        else:
            report.append("\nNo shared prime factors found among siblings in this class.")

    # Section 6: Notable Patterns
    report.append("\n## 6. Notable Patterns and Observations\n")

    # Pattern 1: Powers of 2
    powers_of_2 = []
    for n, factors in factorizations.items():
        if len(factors) == 1 and 2 in factors:
            powers_of_2.append(n)

    if powers_of_2:
        report.append(f"\n### Powers of 2\n")
        report.append(f"k[n] values that are pure powers of 2: {', '.join(map(str, powers_of_2))}\n")

    # Pattern 2: Small primes dominance
    small_primes = [p for p in prime_counts.keys() if p <= 10]
    if small_primes:
        small_prime_total = sum(prime_counts[p] for p in small_primes)
        report.append(f"\n### Small Prime Dominance\n")
        report.append(f"Primes ≤ 10 account for {small_prime_total} occurrences ({small_prime_total/total_occurrences*100:.1f}% of all prime factors < 100).\n")

    # Pattern 3: Largest prime factors
    report.append(f"\n### Largest Prime Factors\n")
    largest_primes = []
    for n, factors in factorizations.items():
        if factors and 0 not in factors:
            max_prime = max(factors.keys())
            largest_primes.append((n, max_prime, k_values[n]))

    largest_primes.sort(key=lambda x: x[1], reverse=True)
    report.append("\nTop 10 k[n] by largest prime factor:\n")
    report.append("\n| n | k[n] | Largest Prime Factor |")
    report.append("|---|------|----------------------|")
    for n, max_prime, k in largest_primes[:10]:
        k_str = str(k) if len(str(k)) <= 25 else f"{str(k)[:22]}..."
        report.append(f"| {n} | {k_str} | {max_prime} |")

    return "\n".join(report)

def main():
    print("Starting k[n] Prime Factorization Analysis...")

    # Query database
    print("Querying database...")
    keys_data = query_keys(DB_PATH, 1, 70)
    print(f"Retrieved {len(keys_data)} keys")

    # Perform analysis
    print("Performing factorization analysis...")
    factorizations, prime_counts, prime_k, highly_composite, mod3_analysis = analyze_factorizations(keys_data)

    print(f"- Factorized {len(factorizations)} values")
    print(f"- Found {len(prime_k)} prime k[n] values")
    print(f"- Found {len(highly_composite)} highly composite k[n] values")
    print(f"- Counted {len(prime_counts)} distinct primes < 100")

    # Generate report
    print("Generating report...")
    report = generate_report(factorizations, prime_counts, prime_k, highly_composite, mod3_analysis, keys_data)

    # Write to file
    output_file = "/home/rkh/ladder/k_factorization_patterns.md"
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"\nReport written to: {output_file}")
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
