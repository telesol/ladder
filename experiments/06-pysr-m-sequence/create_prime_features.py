#!/usr/bin/env python3
"""
Create enhanced feature matrix with prime-related features.

Since adding a custom prime(i) operator to PySR is complex,
we pre-compute prime-related features that PySR can use directly.
"""

import pandas as pd
import numpy as np
import json
from sympy import prime, primepi

# First 200 primes for lookup
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
          73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
          157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
          239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
          331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419,
          421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503]

def main():
    print("Creating enhanced feature matrix with prime features...")

    # Load existing feature matrix
    df = pd.read_csv('feature_matrix.csv')

    # Load m-sequence data
    with open('/home/solo/LA/data_for_csolver.json') as f:
        data = json.load(f)

    m_seq = {i+2: v for i, v in enumerate(data['m_seq'])}
    d_seq = {i+2: v for i, v in enumerate(data['d_seq'])}

    print(f"Loaded {len(df)} samples")

    # Add new prime-related features
    new_features = []

    for idx, row in df.iterrows():
        n = int(row['n'])
        features = {}

        # Basic n-based features
        features['n'] = n

        # Prime at index n
        if n <= 200:
            features['prime_n'] = PRIMES[n-1]  # p[n]
        else:
            features['prime_n'] = prime(n)

        # p[7] = 17 appears often
        features['p7'] = 17
        features['p8'] = 19
        features['p10'] = 29
        features['p7_times_p10'] = 17 * 29  # = 493 = m[9]

        # Self-referential features using earlier m values
        if n >= 7 and (n-1) in m_seq:
            features['prev_m'] = m_seq[n-1]
        else:
            features['prev_m'] = 0

        if n >= 8 and (n-2) in m_seq:
            features['prev2_m'] = m_seq[n-2]
        else:
            features['prev2_m'] = 0

        # d_n value
        if n in d_seq:
            features['d_n'] = d_seq[n]
        else:
            features['d_n'] = 1

        # m[d_n] - self-referential
        d_val = d_seq.get(n, 1)
        if d_val in m_seq:
            features['m_at_d'] = m_seq[d_val]
        else:
            features['m_at_d'] = 1

        # p[n + m[6]] = p[n + 19]
        features['p_n_plus_19'] = prime(n + 19)

        # p[n + m[5]] = p[n + 9]
        features['p_n_plus_9'] = prime(n + 9)

        # 2^n
        features['pow2_n'] = 2**n

        # Products of small primes
        features['p7_times_pn'] = 17 * PRIMES[min(n-1, 199)]  # p[7] * p[n]

        # n^2, n^3
        features['n_sq'] = n * n
        features['n_cube'] = n * n * n

        # Target
        if n in m_seq:
            features['target_m'] = m_seq[n]
        else:
            features['target_m'] = 0

        new_features.append(features)

    # Create new dataframe
    new_df = pd.DataFrame(new_features)

    # Save
    new_df.to_csv('feature_matrix_enhanced.csv', index=False)

    print(f"\nCreated feature_matrix_enhanced.csv")
    print(f"Features: {list(new_df.columns)}")
    print(f"Samples: {len(new_df)}")

    # Show sample
    print("\nFirst 5 rows:")
    print(new_df.head())

if __name__ == "__main__":
    main()
