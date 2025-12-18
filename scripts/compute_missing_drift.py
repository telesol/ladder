#!/usr/bin/env python3
"""
compute_missing_drift.py
Computes the missing drift constant C[0][ℓ][0] from bridges 75 and 80
using multi-step affine recurrence and brute-force search.
"""
import json, os, sys

def main():
    # Load calibration file
    try:
        with open('out/ladder_calib_29_70_full.json') as f:
            calib = json.load(f)
    except FileNotFoundError:
        sys.exit("❌ Error: out/ladder_calib_29_70_full.json not found")

    # Extract A values (multipliers for 16 lanes)
    A = {int(k): int(v) for k, v in calib['A'].items()}

    print("🔧 Ladder Drift Computation Tool")
    print("=" * 60)
    print()

    # Get bridge hex values from environment
    HEX75 = os.getenv('HEX75')
    HEX80 = os.getenv('HEX80')

    if not HEX75 or not HEX80:
        print("❌ Error: HEX75 and HEX80 environment variables not set")
        print()
        print("Please run:")
        print("  export HEX75=$(awk -F, '$1==75 {print substr($4,1,32)}' data/btc_puzzle_1_160_full.csv)")
        print("  export HEX80=$(awk -F, '$1==80 {print substr($4,1,32)}' data/btc_puzzle_1_160_full.csv)")
        print()
        sys.exit(1)

    print(f"📊 Input Data:")
    print(f"  HEX75 (puzzle 75): {HEX75} (length: {len(HEX75)})")
    print(f"  HEX80 (puzzle 80): {HEX80} (length: {len(HEX80)})")
    print()

    if len(HEX75) != 32 or len(HEX80) != 32:
        sys.exit("❌ Error: Bridge values must be exactly 32 hex characters")

    # Convert hex to bytes (first 16 bytes only, as the ladder uses the right half)
    X = bytes.fromhex(HEX75.ljust(32, '0'))[:16]
    Y = bytes.fromhex(HEX80.ljust(32, '0'))[:16]

    print("🔬 Computing drift C[0][ℓ][0] for each lane...")
    print()
    print("  Lane | A     | X    | Y    | Drift | Hex")
    print("  " + "-" * 50)

    # Compute drift for each lane
    drift = []
    for lane in range(16):
        a = A[lane]
        x_byte = X[lane]
        y_byte = Y[lane]

        # Compute powers: a^2, a^3, a^4 (mod 256)
        a2 = (a * a) & 0xFF
        a3 = (a2 * a) & 0xFF
        a4 = (a3 * a) & 0xFF

        # Compute coefficient: (a^3 + a^2 + a + 1) mod 256
        coeff = (a3 + a2 + a + 1) & 0xFF

        # Brute-force search for drift d in range [0, 255]
        # We need: (a^4 * x + coeff * d) mod 256 = y
        found = False
        for d in range(256):
            predicted = (a4 * x_byte + coeff * d) & 0xFF
            if predicted == y_byte:
                drift.append(d)
                print(f"  {lane:4d} | {a:5d} | 0x{x_byte:02x} | 0x{y_byte:02x} | {d:5d} | 0x{d:02x}")
                found = True
                break

        if not found:
            print(f"  {lane:4d} | {a:5d} | 0x{x_byte:02x} | 0x{y_byte:02x} | ❌ NOT FOUND!")
            sys.exit(f"\n❌ Error: No drift found for lane {lane}")

    print()
    print("✅ All 16 drifts computed successfully!")
    print()
    print(f"Drift array: {drift}")
    print()

    # Write to file
    output = {"C0_0": [f"0x{d:02x}" for d in drift]}
    with open('missing_c0.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("✅ Drift written to missing_c0.json")
    print()
    print("Next steps:")
    print("  1. Patch the calibration file with this drift")
    print("  2. Run: python3 verify_affine.py")
    print("  3. Expect: 100.000% forward and reverse verification")
    print()

if __name__ == "__main__":
    main()
