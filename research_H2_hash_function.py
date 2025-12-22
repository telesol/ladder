#!/usr/bin/env python3
"""
Hypothesis 2 (H2): Cryptographic Hash Function

Theory: drift[k][lane] = hash_function(k, lane) mod 256

Tests:
1. Standard cryptographic hashes (SHA256, MD5, SHA1, SHA512, RIPEMD160)
2. Bitcoin-specific hashes (HASH256, HASH160)
3. Different input encodings (string, bytes, packed)
4. Salted/seeded variations
5. XOR combinations

Machine: Spark 2
Expected time: 2-3 hours
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Callable

def load_data(json_path="drift_data_export.json"):
    """Load drift data from export file"""
    print(f"[1/7] Loading data from {json_path}")
    with open(json_path) as f:
        data = json.load(f)

    transitions = data['transitions']
    print(f"  ✓ Loaded {len(transitions)} transitions ({len(transitions)*16} drift values)")
    return data

def test_hash_function(data, name: str, hash_func: Callable, encoding_variants=None):
    """Test a specific hash function with various encodings"""

    if encoding_variants is None:
        encoding_variants = ['str_concat', 'bytes_concat', 'packed_little', 'packed_big']

    transitions = data['transitions']

    results = {}

    for encoding in encoding_variants:
        matches = 0
        total = 0

        for trans in transitions:
            k = trans['from_puzzle']

            for lane in range(16):
                actual_drift = trans['drifts'][lane]

                # Prepare input based on encoding
                if encoding == 'str_concat':
                    input_data = f"{k}{lane}".encode()
                elif encoding == 'str_sep':
                    input_data = f"{k}_{lane}".encode()
                elif encoding == 'bytes_concat':
                    input_data = k.to_bytes(4, 'big') + lane.to_bytes(1, 'big')
                elif encoding == 'packed_little':
                    input_data = k.to_bytes(4, 'little') + lane.to_bytes(1, 'little')
                elif encoding == 'packed_big':
                    input_data = k.to_bytes(4, 'big') + lane.to_bytes(1, 'big')
                else:
                    continue

                # Compute hash
                predicted_drift = hash_func(input_data) % 256

                if predicted_drift == actual_drift:
                    matches += 1
                total += 1

        accuracy = matches / total if total > 0 else 0.0
        results[encoding] = accuracy

    return results

def sha256_hash(data: bytes) -> int:
    """SHA256 hash -> first byte as int"""
    h = hashlib.sha256(data).digest()
    return h[0]

def md5_hash(data: bytes) -> int:
    """MD5 hash -> first byte as int"""
    h = hashlib.md5(data).digest()
    return h[0]

def sha1_hash(data: bytes) -> int:
    """SHA1 hash -> first byte as int"""
    h = hashlib.sha1(data).digest()
    return h[0]

def sha512_hash(data: bytes) -> int:
    """SHA512 hash -> first byte as int"""
    h = hashlib.sha512(data).digest()
    return h[0]

def ripemd160_hash(data: bytes) -> int:
    """RIPEMD160 hash -> first byte as int"""
    try:
        h = hashlib.new('ripemd160', data).digest()
        return h[0]
    except:
        return 0

def hash256(data: bytes) -> int:
    """Bitcoin HASH256 (double SHA256) -> first byte as int"""
    h1 = hashlib.sha256(data).digest()
    h2 = hashlib.sha256(h1).digest()
    return h2[0]

def hash160(data: bytes) -> int:
    """Bitcoin HASH160 (SHA256 then RIPEMD160) -> first byte as int"""
    h1 = hashlib.sha256(data).digest()
    try:
        h2 = hashlib.new('ripemd160', h1).digest()
        return h2[0]
    except:
        return 0

def test_standard_hashes(data):
    """Test standard cryptographic hash functions"""
    print("\n[2/7] Testing Standard Hash Functions")

    hash_functions = [
        ('SHA256', sha256_hash),
        ('MD5', md5_hash),
        ('SHA1', sha1_hash),
        ('SHA512', sha512_hash),
        ('RIPEMD160', ripemd160_hash)
    ]

    results = {}

    for name, func in hash_functions:
        print(f"\n  Testing {name}...")
        result = test_hash_function(data, name, func)

        # Find best encoding
        best_encoding = max(result.items(), key=lambda x: x[1])
        results[name] = {
            'encodings': result,
            'best_encoding': best_encoding[0],
            'best_accuracy': best_encoding[1]
        }

        if best_encoding[1] == 1.0:
            print(f"    ✅ 100% match with {best_encoding[0]}!")
        elif best_encoding[1] > 0.8:
            print(f"    🔥 {best_encoding[1]*100:.1f}% with {best_encoding[0]}")
        else:
            print(f"    ❌ Best: {best_encoding[1]*100:.1f}% with {best_encoding[0]}")

    return results

def test_bitcoin_hashes(data):
    """Test Bitcoin-specific hash functions"""
    print("\n[3/7] Testing Bitcoin-Specific Hashes")

    hash_functions = [
        ('HASH256', hash256),
        ('HASH160', hash160)
    ]

    results = {}

    for name, func in hash_functions:
        print(f"\n  Testing {name}...")
        result = test_hash_function(data, name, func)

        best_encoding = max(result.items(), key=lambda x: x[1])
        results[name] = {
            'encodings': result,
            'best_encoding': best_encoding[0],
            'best_accuracy': best_encoding[1]
        }

        if best_encoding[1] == 1.0:
            print(f"    ✅ 100% match with {best_encoding[0]}!")
        elif best_encoding[1] > 0.8:
            print(f"    🔥 {best_encoding[1]*100:.1f}% with {best_encoding[0]}")
        else:
            print(f"    ❌ Best: {best_encoding[1]*100:.1f}% with {best_encoding[0]}")

    return results

def test_salted_hashes(data):
    """Test hash functions with various salts/seeds"""
    print("\n[4/7] Testing Salted/Seeded Hashes")

    transitions = data['transitions']

    # Test different salt values
    salts = [0, 1, 42, 123, 255, 1337, 12345, 0x1234, 0xDEADBEEF]

    results = {}

    for salt in salts:
        matches = 0
        total = 0

        for trans in transitions:
            k = trans['from_puzzle']

            for lane in range(16):
                actual_drift = trans['drifts'][lane]

                # Hash with salt: SHA256(salt || k || lane)
                input_data = salt.to_bytes(4, 'big') + k.to_bytes(4, 'big') + lane.to_bytes(1, 'big')
                predicted_drift = sha256_hash(input_data)

                if predicted_drift == actual_drift:
                    matches += 1
                total += 1

        accuracy = matches / total
        results[f'salt_{salt}'] = accuracy

        if accuracy == 1.0:
            print(f"  ✅ 100% match with salt={salt}!")
        elif accuracy > 0.8:
            print(f"  🔥 {accuracy*100:.1f}% with salt={salt}")

    if all(acc < 0.8 for acc in results.values()):
        print("  ❌ No salts found with >80% accuracy")

    return results

def test_xor_combinations(data):
    """Test XOR combinations: hash(k) XOR hash(lane)"""
    print("\n[5/7] Testing XOR Combinations")

    transitions = data['transitions']

    # Test: SHA256(k) XOR SHA256(lane)
    matches = 0
    total = 0

    for trans in transitions:
        k = trans['from_puzzle']

        for lane in range(16):
            actual_drift = trans['drifts'][lane]

            # Hash k and lane separately, then XOR
            hash_k = hashlib.sha256(k.to_bytes(4, 'big')).digest()[0]
            hash_lane = hashlib.sha256(lane.to_bytes(1, 'big')).digest()[0]
            predicted_drift = (hash_k ^ hash_lane) % 256

            if predicted_drift == actual_drift:
                matches += 1
            total += 1

    accuracy = matches / total

    if accuracy == 1.0:
        print(f"  ✅ 100% match with SHA256(k) XOR SHA256(lane)!")
    elif accuracy > 0.8:
        print(f"  🔥 {accuracy*100:.1f}% accuracy")
    else:
        print(f"  ❌ {accuracy*100:.1f}% accuracy")

    return {'sha256_xor': accuracy}

def test_nth_byte_extraction(data):
    """Test using different bytes from hash output"""
    print("\n[6/7] Testing N-th Byte Extraction from Hash")

    transitions = data['transitions']

    results = {}

    # Test first 16 bytes of SHA256 output
    for byte_index in range(16):
        matches = 0
        total = 0

        for trans in transitions:
            k = trans['from_puzzle']

            for lane in range(16):
                actual_drift = trans['drifts'][lane]

                # Use byte_index-th byte of hash
                input_data = f"{k}{lane}".encode()
                hash_output = hashlib.sha256(input_data).digest()
                predicted_drift = hash_output[byte_index]

                if predicted_drift == actual_drift:
                    matches += 1
                total += 1

        accuracy = matches / total
        results[f'byte_{byte_index}'] = accuracy

        if accuracy == 1.0:
            print(f"  ✅ 100% match using byte {byte_index}!")
        elif accuracy > 0.8:
            print(f"  🔥 Byte {byte_index}: {accuracy*100:.1f}%")

    if all(acc < 0.8 for acc in results.values()):
        print("  ❌ No byte positions found with >80% accuracy")

    return results

def generate_report(data, std_hashes, btc_hashes, salted, xor_result, nth_byte):
    """Generate final report"""
    print("\n[7/7] Generating Report")

    # Find overall best result
    all_results = []

    for name, result in std_hashes.items():
        all_results.append((f'{name} ({result["best_encoding"]})', result['best_accuracy']))

    for name, result in btc_hashes.items():
        all_results.append((f'{name} ({result["best_encoding"]})', result['best_accuracy']))

    for name, acc in salted.items():
        if acc > 0.5:
            all_results.append((f'Salted SHA256 ({name})', acc))

    for name, acc in xor_result.items():
        all_results.append((f'XOR: {name}', acc))

    for name, acc in nth_byte.items():
        if acc > 0.5:
            all_results.append((f'SHA256 {name}', acc))

    best = max(all_results, key=lambda x: x[1]) if all_results else ('None', 0.0)

    report = {
        'hypothesis': 'H2: Cryptographic Hash Function',
        'theory': 'drift[k][lane] = hash_function(k, lane) mod 256',
        'results': {
            'standard_hashes': std_hashes,
            'bitcoin_hashes': btc_hashes,
            'salted_hashes': salted,
            'xor_combinations': xor_result,
            'nth_byte_extraction': nth_byte
        },
        'best_approach': {
            'name': best[0],
            'accuracy': best[1]
        },
        'conclusion': 'SUCCESS' if best[1] == 1.0 else
                     'PROMISING' if best[1] > 0.9 else
                     'PARTIAL' if best[1] > 0.7 else 'FAILED'
    }

    # Save report
    output_path = Path("H2_results.json")
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"  ✓ Report saved to: {output_path}")

    # Print summary
    print("\n" + "="*60)
    print("H2 HYPOTHESIS SUMMARY")
    print("="*60)
    print(f"Best approach:  {best[0]}")
    print(f"Accuracy:       {best[1]*100:.2f}%")
    print(f"Conclusion:     {report['conclusion']}")
    print("="*60)

    if best[1] == 1.0:
        print("\n🎉 SUCCESS! Generator found: drift = hash(k, lane) mod 256")
    elif best[1] > 0.9:
        print("\n🔥 Very close! This hypothesis is promising.")
    elif best[1] > 0.7:
        print("\n👍 Partial success. May need hybrid approach.")
    else:
        print("\n🤔 Hypothesis unlikely. Try other approaches.")

    return report

def main():
    # Check if data file exists
    data_file = Path("drift_data_export.json")
    if not data_file.exists():
        print(f"❌ Error: {data_file} not found!")
        print("Please run export_drift_data.py first.")
        sys.exit(1)

    # Load data
    data = load_data(data_file)

    # Run tests
    std_hashes = test_standard_hashes(data)
    btc_hashes = test_bitcoin_hashes(data)
    salted = test_salted_hashes(data)
    xor_result = test_xor_combinations(data)
    nth_byte = test_nth_byte_extraction(data)

    # Generate report
    report = generate_report(data, std_hashes, btc_hashes, salted, xor_result, nth_byte)

    print("\n✅ H2 research complete!")

if __name__ == '__main__':
    main()
