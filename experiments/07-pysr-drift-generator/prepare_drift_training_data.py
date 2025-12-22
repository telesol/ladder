#!/usr/bin/env python3
"""
Prepare training data for PySR drift generator discovery

Extracts all drift values from calibration and creates train/val/test splits
"""

import json
import pandas as pd
import sys

def load_calibration():
    """Load corrected calibration file"""
    with open('out/ladder_calib_CORRECTED.json', 'r') as f:
        return json.load(f)

def extract_drift_data():
    """Extract all drift values with features"""
    print("Loading calibration...")
    calib = load_calibration()

    # Get A values
    A = [calib['A'][str(i)] for i in range(16)]
    print(f"A values: {A}")

    # Extract drift values
    drift_data = []

    for k in range(1, 70):
        trans_key = f'{k}→{k+1}'

        if trans_key not in calib['drifts']:
            print(f"Warning: Missing transition {trans_key}")
            continue

        for lane in range(16):
            drift_k = calib['drifts'][trans_key][str(lane)]

            # Get previous drift (if exists)
            if k > 1:
                prev_key = f'{k-1}→{k}'
                drift_prev = calib['drifts'][prev_key][str(lane)]
            else:
                drift_prev = 0  # No previous drift for k=1

            drift_data.append({
                'k': k,
                'lane': lane,
                'drift': drift_k,
                'drift_prev': drift_prev,
                'A': A[lane]
            })

    print(f"\nExtracted {len(drift_data)} drift values")
    print(f"  Transitions: {len(drift_data) // 16}")
    print(f"  Lanes: 16")

    return pd.DataFrame(drift_data)

def split_data(df):
    """Split into train/val/test"""
    train = df[df['k'] <= 50].copy()
    val = df[(df['k'] > 50) & (df['k'] <= 60)].copy()
    test = df[df['k'] > 60].copy()

    print(f"\nData splits:")
    print(f"  Train: k=1-50   ({len(train)} samples)")
    print(f"  Val:   k=51-60  ({len(val)} samples)")
    print(f"  Test:  k=61-69  ({len(test)} samples)")

    return train, val, test

def analyze_per_lane(df):
    """Analyze drift patterns per lane"""
    print("\nPer-lane analysis:")
    print("Lane | Unique | Mean  | Std   | Min | Max")
    print("-----|--------|-------|-------|-----|----")

    for lane in range(16):
        lane_data = df[df['lane'] == lane]['drift']
        print(f"  {lane:2d} | {lane_data.nunique():6d} | {lane_data.mean():5.1f} | {lane_data.std():5.1f} | {lane_data.min():3d} | {lane_data.max():3d}")

def main():
    print("="*60)
    print("DRIFT TRAINING DATA PREPARATION")
    print("="*60)
    print()

    # Extract data
    df = extract_drift_data()

    # Analyze
    analyze_per_lane(df)

    # Split
    train, val, test = split_data(df)

    # Save
    output_dir = 'experiments/07-pysr-drift-generator'
    train.to_csv(f'{output_dir}/train.csv', index=False)
    val.to_csv(f'{output_dir}/val.csv', index=False)
    test.to_csv(f'{output_dir}/test.csv', index=False)

    print(f"\n✅ Saved:")
    print(f"  {output_dir}/train.csv")
    print(f"  {output_dir}/val.csv")
    print(f"  {output_dir}/test.csv")

    return 0

if __name__ == '__main__':
    sys.exit(main())
