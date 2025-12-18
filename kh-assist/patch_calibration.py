#!/usr/bin/env python3
"""
patch_calibration.py
Patches the calibration JSON file with the computed drift C[0][ℓ][0].
"""
import json
import sys
import os

def main():
    calib_path = 'out/ladder_calib_29_70_full.json'
    drift_path = 'missing_c0.json'

    # Check if files exist
    if not os.path.exists(calib_path):
        sys.exit(f"❌ Error: {calib_path} not found")

    if not os.path.exists(drift_path):
        sys.exit(f"❌ Error: {drift_path} not found\n   Run compute_missing_drift.py first")

    print("🔧 Calibration Patch Tool")
    print("=" * 60)
    print()

    # Load existing calibration
    with open(calib_path) as f:
        calib = json.load(f)

    print(f"✅ Loaded calibration from {calib_path}")

    # Load computed drift
    with open(drift_path) as f:
        drift_data = json.load(f)

    if 'C0_0' not in drift_data:
        sys.exit("❌ Error: missing_c0.json does not contain 'C0_0' key")

    drift = drift_data['C0_0']

    # Convert hex strings to integers if needed
    drift_values = []
    for v in drift:
        if isinstance(v, str):
            # Remove 0x prefix and convert
            drift_values.append(int(v.replace('0x', ''), 16))
        else:
            drift_values.append(int(v))

    if len(drift_values) != 16:
        sys.exit(f"❌ Error: Expected 16 drift values, got {len(drift_values)}")

    print(f"✅ Loaded drift C[0][ℓ][0] from {drift_path}")
    print(f"   Values: {drift_values}")
    print()

    # Patch the calibration
    # Ensure Cstar structure exists
    if 'Cstar' not in calib:
        calib['Cstar'] = {}

    if '0' not in calib['Cstar']:
        calib['Cstar']['0'] = {}

    if '1' not in calib['Cstar']:
        calib['Cstar']['1'] = {}

    # Patch C[0][lane][0] for each lane
    for lane in range(16):
        lane_str = str(lane)

        # Initialize lane if not present
        if lane_str not in calib['Cstar']['0']:
            calib['Cstar']['0'][lane_str] = [0, 0]

        # Ensure it's a 2-element list
        if not isinstance(calib['Cstar']['0'][lane_str], list):
            calib['Cstar']['0'][lane_str] = [0, 0]

        if len(calib['Cstar']['0'][lane_str]) < 2:
            calib['Cstar']['0'][lane_str] = [0, 0]

        # Patch occurrence 0 with computed drift
        old_value = calib['Cstar']['0'][lane_str][0]
        calib['Cstar']['0'][lane_str][0] = drift_values[lane]

        print(f"  Lane {lane:2d}: C[0][{lane:2d}][0] = {drift_values[lane]:3d} (0x{drift_values[lane]:02x}) [was: {old_value}]")

    print()

    # Write back to file (create backup first)
    backup_path = calib_path + '.backup'
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            json.dump(calib, f, indent=2)
        print(f"📦 Backup created at {backup_path}")

    with open(calib_path, 'w') as f:
        json.dump(calib, f, indent=2)

    print(f"✅ Calibration file patched successfully!")
    print()
    print("Next steps:")
    print("  1. Run: python3 verify_affine.py")
    print("  2. Expect: 100.000% forward and reverse verification")
    print("  3. If not 100%, check out/ladder_mismatch_log.csv")
    print()

if __name__ == "__main__":
    main()
