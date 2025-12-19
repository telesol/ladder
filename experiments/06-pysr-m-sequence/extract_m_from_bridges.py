#!/usr/bin/env python3
"""
Extract actual m-values from bridge puzzles using reverse calculation.

Bridge puzzles (n=75, 80, 85, 90, 95) have known correct k-values from CSV.
We use the master formula to reverse-engineer m-values:

Master formula: k_n = 2 × k_{n-1} + (2^n - m_n × k_{d_n})

Solve for m_n:
    k_n - 2×k_{n-1} = 2^n - m_n × k_{d_n}
    m_n × k_{d_n} = 2^n - (k_n - 2×k_{n-1})
    m_n = (2^n - (k_n - 2×k_{n-1})) / k_{d_n}
"""

import pandas as pd
import json
from pathlib import Path

# Import d-sequence
from convergent_database import D_SEQUENCE

def extract_m_from_bridges():
    print("=" * 70)
    print("EXTRACT M-VALUES FROM BRIDGE PUZZLES")
    print("=" * 70)

    # Step 1: Load Bitcoin puzzle CSV
    print("\n1. Loading Bitcoin puzzle data...")
    csv_path = Path('../../data/btc_puzzle_1_160_full.csv')

    if not csv_path.exists():
        print(f"   ERROR: CSV not found at {csv_path}")
        print("   Please ensure btc_puzzle_1_160_full.csv is in data/ directory")
        return

    df = pd.read_csv(csv_path)
    print(f"   Loaded {len(df)} puzzles from CSV")

    # Step 2: Define bridge puzzles
    print("\n2. Extracting bridge puzzle k-values...")
    bridges = [75, 80, 85, 90, 95]

    bridge_data = []

    for n in bridges:
        # Get k_n (current puzzle key)
        row = df[df['puzzle'] == n]
        if len(row) == 0:
            print(f"   WARNING: Puzzle {n} not found in CSV")
            continue

        k_n_hex = row['key_hex'].values[0]
        k_n = int(k_n_hex, 16)

        # Get k_{n-1} (previous puzzle key)
        row_prev = df[df['puzzle'] == n-1]
        if len(row_prev) == 0:
            print(f"   WARNING: Puzzle {n-1} not found in CSV")
            continue

        k_prev_hex = row_prev['key_hex'].values[0]
        k_prev = int(k_prev_hex, 16)

        # Get d_n
        d_n = D_SEQUENCE.get(n)
        if d_n is None:
            print(f"   WARNING: d_{n} not in D_SEQUENCE")
            continue

        # Get k_{d_n} (dependency key)
        row_d = df[df['puzzle'] == d_n]
        if len(row_d) == 0:
            print(f"   WARNING: Puzzle {d_n} not found in CSV")
            continue

        k_d_hex = row_d['key_hex'].values[0]
        k_d = int(k_d_hex, 16)

        print(f"   n={n}: k_n={k_n_hex[:16]}..., k_prev={k_prev_hex[:16]}..., d={d_n}, k_d={k_d_hex[:16]}...")

        bridge_data.append({
            'n': n,
            'd_n': d_n,
            'k_n': k_n,
            'k_prev': k_prev,
            'k_d': k_d
        })

    # Step 3: Reverse-engineer m-values
    print("\n3. Reverse-engineering m-values...")

    extracted_m = {}

    for data in bridge_data:
        n = data['n']
        k_n = data['k_n']
        k_prev = data['k_prev']
        d_n = data['d_n']
        k_d = data['k_d']

        # Calculate 2^n
        power_of_2 = 2 ** n

        # Reverse-engineer m_n
        # m_n = (2^n - (k_n - 2×k_{n-1})) / k_{d_n}
        numerator = power_of_2 - (k_n - 2 * k_prev)

        if numerator % k_d != 0:
            print(f"   WARNING: n={n} gives non-integer m! ({numerator} / {k_d})")
            m_n = numerator / k_d
            is_exact = False
        else:
            m_n = numerator // k_d
            is_exact = True

        extracted_m[n] = {
            'm': int(m_n) if is_exact else m_n,
            'd_n': d_n,
            'is_exact': is_exact
        }

        print(f"   n={n}: m={m_n:>15}, d={d_n}, exact={is_exact}")

    # Step 4: Validate reverse calculation
    print("\n4. Validating reverse-engineered m-values...")

    validation_passed = 0
    validation_failed = 0

    for data in bridge_data:
        n = data['n']
        k_n = data['k_n']
        k_prev = data['k_prev']
        d_n = data['d_n']
        k_d = data['k_d']

        m_n = extracted_m[n]['m']

        # Recalculate k_n using master formula
        k_check = 2 * k_prev + (2**n - int(m_n) * k_d)

        if k_check == k_n:
            print(f"   ✅ n={n}: validation PASSED (k_check == k_n)")
            validation_passed += 1
        else:
            print(f"   ❌ n={n}: validation FAILED (k_check != k_n)")
            print(f"      Expected: {k_n}")
            print(f"      Got:      {k_check}")
            print(f"      Diff:     {k_check - k_n}")
            validation_failed += 1

    print(f"\n   Validation: {validation_passed} passed, {validation_failed} failed")

    # Step 5: Test PySR formula on bridges
    print("\n5. Testing PySR formula on bridge m-values...")

    # Best PySR formula: m ≈ 2^n × 1077.5 / (n × (d_n + 0.4066))²

    results = []

    for n in bridges:
        if n not in extracted_m:
            continue

        m_actual = extracted_m[n]['m']
        d_n = extracted_m[n]['d_n']

        # PySR prediction
        m_pysr = (2**n) * 1077.4889 / ((n**2) * ((-d_n - 0.40659702)**2))

        accuracy_pct = (m_pysr / m_actual) * 100 if m_actual != 0 else 0

        results.append({
            'n': n,
            'm_actual': m_actual,
            'm_pysr': int(m_pysr),
            'd_n': d_n,
            'accuracy_pct': accuracy_pct,
            'error': abs(m_actual - int(m_pysr))
        })

        print(f"   n={n}: actual={m_actual:>15}, pysr={int(m_pysr):>15}, accuracy={accuracy_pct:>6.2f}%, error={abs(m_actual - int(m_pysr)):>15}")

    avg_accuracy = sum(r['accuracy_pct'] for r in results) / len(results) if results else 0
    print(f"\n   Average PySR accuracy on bridges: {avg_accuracy:.2f}%")

    # Step 6: Save results
    print("\n6. Saving results...")

    output = {
        'metadata': {
            'description': 'Reverse-engineered m-values from bridge puzzles',
            'bridges': bridges,
            'validation_passed': validation_passed,
            'validation_failed': validation_failed
        },
        'extracted_m_values': extracted_m,
        'pysr_validation': {
            'formula': 'power_of_2 * 1077.4889 / (n**2 * (-d_n - 0.40659702)**2)',
            'avg_accuracy_pct': avg_accuracy,
            'results': results
        }
    }

    with open('bridge_m_values.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("   Saved results to: bridge_m_values.json")

    # Step 7: Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nExtracted m-values for {len(extracted_m)} bridge puzzles:")
    for n in sorted(extracted_m.keys()):
        print(f"  m[{n}] = {extracted_m[n]['m']}, d[{n}] = {extracted_m[n]['d_n']}")

    print(f"\nPySR formula accuracy on bridges: {avg_accuracy:.2f}%")

    if avg_accuracy >= 90:
        print("\n🎉 EXCELLENT! PySR formula is highly accurate on bridges!")
        print("   → Next: Calibrate coefficients for 100% accuracy")
    elif avg_accuracy >= 70:
        print("\n👍 GOOD! PySR formula captures general pattern on bridges")
        print("   → Next: Try hybrid approach (PySR + correction factors)")
    elif avg_accuracy >= 50:
        print("\n🤔 MODERATE. PySR formula partially works on bridges")
        print("   → Next: Analyze error patterns, try piecewise models")
    else:
        print("\n❌ POOR. PySR formula doesn't generalize to bridges")
        print("   → Next: Try different approach (modular arithmetic, etc.)")

if __name__ == "__main__":
    extract_m_from_bridges()
