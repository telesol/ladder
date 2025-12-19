#!/usr/bin/env python3
"""Merge all factorization JSON files into a unified database."""

import json
from datetime import datetime

def main():
    files = [
        'factorization_36_45.json',
        'factorization_46_55.json',
        'factorization_56_70.json'
    ]

    all_results = []

    for f in files:
        print(f"Loading {f}...")
        try:
            with open(f) as fp:
                data = json.load(fp)
                all_results.extend(data['results'])
        except Exception as e:
            print(f"  Error: {e}")

    # Sort by n
    all_results.sort(key=lambda x: x['n'])

    # Create unified database
    db = {
        'metadata': {
            'description': 'Factorization of m-sequence values',
            'n_range': [36, 70],
            'timestamp': datetime.now().isoformat(),
            'total_values': len(all_results),
            'factored_count': sum(1 for r in all_results if r.get('factored', False))
        },
        'results': all_results
    }

    # Save
    with open('factorization_database.json', 'w') as f:
        json.dump(db, f, indent=2)

    print(f"\nCreated factorization_database.json")
    print(f"Total: {len(all_results)} values")
    print(f"Range: n={all_results[0]['n']} to n={all_results[-1]['n']}")

    # Print summary
    print("\n=== FACTORIZATION SUMMARY ===\n")
    for r in all_results:
        n = r['n']
        m = r['m']
        factors = r.get('factors', {})
        indices = r.get('prime_indices', [])
        is_prime = r.get('is_prime', False)

        if is_prime:
            print(f"n={n:2d}: m={m} (PRIME, index={indices[0] if indices else '?'})")
        else:
            factor_str = ' × '.join([f"{p}^{e}" if int(e)>1 else p for p,e in factors.items()])
            print(f"n={n:2d}: m={m} = {factor_str}")
            print(f"       Indices: {indices}")

if __name__ == "__main__":
    main()
