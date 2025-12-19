#!/usr/bin/env python3
"""
Feature Engineering: Prepare convergent-based features for PySR training.

This script builds a feature matrix where each row represents one n value (2..31)
and columns are convergent numerators and denominators for all 6 mathematical constants.
"""

import json
import pandas as pd
from convergent_database import build_database, M_SEQUENCE, D_SEQUENCE

def main():
    print("=" * 70)
    print("FEATURE ENGINEERING: Convergent-based Features for m-sequence")
    print("=" * 70)

    # Step 1: Build convergent database
    print("\n1. Building convergent database...")
    database = build_database()

    # Step 2: Extract convergent values (first 20 for each constant)
    print("\n2. Extracting convergent values (numerators and denominators)...")

    convergent_features = {}
    for const_name in ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']:
        convergents = database[const_name]

        # Numerators (h values)
        nums = [c['numerator'] for c in convergents[:20]]
        # Denominators (k values)
        dens = [c['denominator'] for c in convergents[:20]]

        convergent_features[f'{const_name}_h'] = nums
        convergent_features[f'{const_name}_k'] = dens

    print(f"   Extracted {len(convergent_features)} feature arrays (6 constants × 2 types)")

    # Step 3: Build feature matrix for n=2..31
    print("\n3. Building feature matrix...")

    rows = []
    targets = []

    for n in range(2, 32):  # n=2 to n=31
        row = {
            'n': n,
            'd_n': D_SEQUENCE[n],
            'power_of_2': 2 ** n,
        }

        # Add previous m and d values (for context)
        if n > 2:
            row['prev_m'] = M_SEQUENCE[n-1]
            row['prev_d'] = D_SEQUENCE[n-1]
        else:
            row['prev_m'] = 0
            row['prev_d'] = 0

        # Add convergent features (first 20 numerators and denominators for each constant)
        for const_name in ['pi', 'e', 'sqrt2', 'sqrt3', 'phi', 'ln2']:
            for i in range(20):
                row[f'{const_name}_h_{i}'] = convergent_features[f'{const_name}_h'][i]
                row[f'{const_name}_k_{i}'] = convergent_features[f'{const_name}_k'][i]

        rows.append(row)
        targets.append(M_SEQUENCE[n])

    # Step 4: Create DataFrame
    df = pd.DataFrame(rows)
    df['target_m'] = targets

    print(f"   Feature matrix shape: {df.shape}")
    print(f"   Features: {len(df.columns) - 1} (excluding target)")
    print(f"   Samples: {len(df)} (n=2..31)")

    # Step 5: Save to CSV
    output_file = 'feature_matrix.csv'
    df.to_csv(output_file, index=False)
    print(f"\n4. Saved feature matrix to: {output_file}")

    # Step 6: Show summary statistics
    print("\n5. Summary Statistics:")
    print(f"   n range: [{df['n'].min()}, {df['n'].max()}]")
    print(f"   m range: [{df['target_m'].min()}, {df['target_m'].max()}]")
    print(f"   d range: [{df['d_n'].min()}, {df['d_n'].max()}]")

    # Step 7: Save a human-readable version
    print("\n6. Creating human-readable feature summary...")

    summary = {
        'metadata': {
            'samples': len(df),
            'features': len(df.columns) - 1,
            'n_range': [int(df['n'].min()), int(df['n'].max())],
            'm_range': [int(df['target_m'].min()), int(df['target_m'].max())],
        },
        'feature_groups': {
            'basic': ['n', 'd_n', 'power_of_2', 'prev_m', 'prev_d'],
            'pi_convergents': [f'pi_h_{i}' for i in range(20)] + [f'pi_k_{i}' for i in range(20)],
            'e_convergents': [f'e_h_{i}' for i in range(20)] + [f'e_k_{i}' for i in range(20)],
            'sqrt2_convergents': [f'sqrt2_h_{i}' for i in range(20)] + [f'sqrt2_k_{i}' for i in range(20)],
            'sqrt3_convergents': [f'sqrt3_h_{i}' for i in range(20)] + [f'sqrt3_k_{i}' for i in range(20)],
            'phi_convergents': [f'phi_h_{i}' for i in range(20)] + [f'phi_k_{i}' for i in range(20)],
            'ln2_convergents': [f'ln2_h_{i}' for i in range(20)] + [f'ln2_k_{i}' for i in range(20)],
        },
        'target': 'target_m',
        'samples': df[['n', 'd_n', 'target_m']].to_dict('records')
    }

    with open('feature_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print("   Saved feature summary to: feature_summary.json")

    # Step 8: Show first few rows
    print("\n7. First few rows of feature matrix:")
    print(df[['n', 'd_n', 'prev_m', 'target_m', 'pi_h_0', 'pi_h_1', 'e_h_0', 'sqrt2_h_0']].head(10))

    print("\n" + "=" * 70)
    print("FEATURE ENGINEERING COMPLETE")
    print("=" * 70)
    print(f"\nOutputs:")
    print(f"  - {output_file} (CSV for PySR)")
    print(f"  - feature_summary.json (human-readable summary)")
    print(f"\nNext step: Run train_m_sequence.py")

if __name__ == "__main__":
    main()
