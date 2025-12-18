#!/usr/bin/env python3
"""
Prepare Training Data for Ladder Pattern Learning
Converts ladder puzzle data into instruction-response pairs for fine-tuning
"""
import sqlite3
import json
import os

def load_ladder_data():
    """Load puzzle data from database"""
    db_path = 'kh-assist/db/kh.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT bits, actual_hex
        FROM lcg_residuals
        ORDER BY bits
    """)

    puzzles = []
    for row in cur.fetchall():
        puzzles.append({
            'bits': row[0],
            'hex': row[1]
        })

    conn.close()
    return puzzles

def load_calibration():
    """Load calibration data"""
    calib_path = 'kh-assist/out/ladder_calib_29_70_full.json'
    with open(calib_path) as f:
        return json.load(f)

def create_training_examples():
    """Create instruction-response training pairs"""
    puzzles = load_ladder_data()
    calib = load_calibration()

    training_data = []

    # Example 1: Pattern Recognition
    training_data.append({
        "instruction": "Analyze the Bitcoin puzzle ladder structure. What mathematical model governs the pattern?",
        "input": f"We have {len(puzzles)} known puzzles ranging from bits 1-70 and bridges at 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130.",
        "output": "The Bitcoin puzzle ladder follows an affine recurrence relation: y = A×x + C (mod 256), where:\n- y is the next byte value\n- x is the previous byte value\n- A is the multiplier matrix (per lane)\n- C is the drift constant (per block, lane, occurrence)\n- All arithmetic is modulo 256 (byte-level)\n\nThe structure has 16 parallel lanes (ℓ = 0 to 15), each processing one byte position of the 16-byte private keys. Each lane has its own multiplier A[ℓ] and drift constants C[k][ℓ][occ]."
    })

    # Example 2: Verification Understanding
    training_data.append({
        "instruction": "What does 100% verification mean in the ladder system?",
        "input": "",
        "output": "100% verification means the affine recurrence model (y = A×x + C mod 256) perfectly predicts all 16 bytes of all known puzzles (1-70 plus bridges). This confirms:\n1. The A matrix multipliers are correct for all 16 lanes\n2. All drift constants C[k][ℓ][occ] are properly calibrated\n3. The model can reliably generate unknown puzzles (like puzzle 71)\n\nLess than 100% indicates missing or incorrect drift constants that need to be computed from bridge puzzles."
    })

    # Example 3: Byte Order Critical Knowledge
    training_data.append({
        "instruction": "When extracting puzzle data, what critical detail must be remembered about byte order?",
        "input": "",
        "output": "CRITICAL: The database (kh.db) stores private keys in LITTLE-ENDIAN byte order, while the CSV file uses BIG-ENDIAN. Always extract from the database, never from CSV.\n\nFor example, puzzle 70:\n- Database: 076e33a1864611cec504... (little-endian, CORRECT)\n- CSV: 04c5ce114686a1336e07... (big-endian, WRONG)\n\nExtraction command:\n```bash\nsqlite3 kh.db \"SELECT substr(actual_hex, 3, 32) FROM lcg_residuals WHERE bits=70;\"\n```"
    })

    # Example 4: Drift Computation
    training_data.append({
        "instruction": "How do we compute the missing drift constant C[0][ℓ][0]?",
        "input": "",
        "output": "The missing drift C[0][ℓ][0] is computed using bridge puzzles 75 and 80:\n\n1. Extract hex values from database (little-endian):\n   HEX75=$(sqlite3 db/kh.db \"SELECT substr(actual_hex, 3, 32) FROM lcg_residuals WHERE bits=75;\")\n   HEX80=$(sqlite3 db/kh.db \"SELECT substr(actual_hex, 3, 32) FROM lcg_residuals WHERE bits=80;\")\n\n2. Run computation script:\n   python3 compute_missing_drift.py\n\n3. This produces missing_c0.json with C[0][ℓ][0] values for all 16 lanes\n\n4. Patch the calibration:\n   python3 patch_calibration.py\n\n5. Re-verify to confirm 100%"
    })

    # Example 5: Prediction Workflow
    training_data.append({
        "instruction": "What is the complete workflow to predict puzzle 71?",
        "input": "",
        "output": "Complete workflow:\n\n**Phase 1: Verify**\n```bash\ncd kh-assist && python3 verify_affine.py\n```\nExpect: Should be < 100% initially\n\n**Phase 2: Compute Missing Drift**\n```bash\npython3 compute_missing_drift.py\n```\nThis computes C[0][ℓ][0] from bridges 75 and 80\n\n**Phase 3: Patch Calibration**\n```bash\npython3 patch_calibration.py\n```\nUpdates ladder_calib_29_70_full.json\n\n**Phase 4: Re-verify**\n```bash\npython3 verify_affine.py\n```\nExpect: 100% verification (REQUIRED)\n\n**Phase 5: Generate**\n```bash\npython3 predict_next_halfblock.py\n```\nProduces puzzle 71 private key\n\n**Phase 6: Validate**\n```bash\npython3 validate_address.py <privkey_hex> 71\n```\nCryptographically proves correctness"
    })

    # Add examples for each puzzle with patterns
    for i in range(min(10, len(puzzles))):
        puzzle = puzzles[i]
        training_data.append({
            "instruction": f"What is the private key for Bitcoin puzzle {puzzle['bits']}?",
            "input": "",
            "output": f"Puzzle {puzzle['bits']} private key: {puzzle['hex']}\n\nThis is a {puzzle['bits']}-bit puzzle, meaning the private key's most significant bit is at position {puzzle['bits']}."
        })

    # Add A matrix examples
    a_matrix = calib.get('A', {})
    training_data.append({
        "instruction": "What are the multipliers A[ℓ] for each lane in the ladder?",
        "input": "",
        "output": f"The 16 lane multipliers are:\n" + "\n".join([f"Lane {i}: A[{i}] = {a_matrix.get(str(i), 'unknown')}" for i in range(16)])
    })

    # System configuration
    training_data.append({
        "instruction": "What GPU and software configuration is required for this project?",
        "input": "",
        "output": "Required configuration:\n\n**GPU**: NVIDIA GB10 (Blackwell architecture)\n- VRAM: 119.7 GB\n- CUDA: 13.0\n- Compute Capability: 12.1\n\n**Software**:\n- PyTorch nightly (CUDA 13 support)\n- Transformers 4.57+\n- Qwen2.5-72B-Instruct (4-bit quantization)\n- Python 3.12\n\n**Installation**:\n```bash\npip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu130\npip3 install transformers accelerate bitsandbytes\n```"
    })

    return training_data

def save_training_data(data, output_path='training_data.json'):
    """Save training data in format for fine-tuning"""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved {len(data)} training examples to {output_path}")
    print(f"📊 Total tokens (estimated): {sum(len(json.dumps(ex)) for ex in data)}")

def main():
    print("🔄 Preparing Training Data for Ladder Pattern Learning")
    print("=" * 70)
    print()

    print("📥 Loading ladder data...")
    training_data = create_training_examples()

    print(f"✅ Created {len(training_data)} training examples")
    print()

    print("💾 Saving training data...")
    save_training_data(training_data)

    print()
    print("=" * 70)
    print("✅ Training data prepared!")
    print()
    print("Next steps:")
    print("  1. Review training_data.json")
    print("  2. Run: python3 train_ladder_model.py")
    print()

if __name__ == '__main__':
    main()
