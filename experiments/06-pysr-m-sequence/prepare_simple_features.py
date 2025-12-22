#!/usr/bin/env python3
"""
Create feature matrix with ONLY basic features (no convergents).
8 features instead of 245!
"""

import pandas as pd
from convergent_database import M_SEQUENCE, D_SEQUENCE

print("=" * 70)
print("CREATING SIMPLE FEATURE MATRIX")
print("=" * 70)

rows = []
for n in range(2, 32):
    row = {
        'n': n,
        'd_n': D_SEQUENCE[n],
        'power_of_2': 2**n,
        'n_squared': n**2,
        'n_cubed': n**3,
        'd_n_squared': D_SEQUENCE[n]**2,
        'prev_m': M_SEQUENCE.get(n-1, 0),
        'prev_d': D_SEQUENCE.get(n-1, 0),
        'target_m': M_SEQUENCE[n]
    }
    rows.append(row)

df = pd.DataFrame(rows)

# Save
df.to_csv('feature_matrix_simple.csv', index=False)

print(f"\n✅ Created simple feature matrix:")
print(f"   Samples: {len(df)}")
print(f"   Features: {len(df.columns) - 1}  (vs 245 before!)")
print(f"   Target: target_m")
print(f"\nFeatures:")
for col in df.columns:
    if col != 'target_m':
        print(f"   - {col}")

print(f"\nSaved to: feature_matrix_simple.csv")

# Show sample
print(f"\nFirst 5 rows:")
print(df.head().to_string())
