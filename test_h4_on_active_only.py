#!/usr/bin/env python3
"""
Re-test H4 (recursive pattern) on ACTIVE drift values only.
Now that we know drift[k][lane] = 0 if k < lane*8, test if
ACTIVE drift follows a recursive pattern.
"""

import json
import numpy as np

# Load drift data
with open('drift_data_CORRECT_BYTE_ORDER.json', 'r') as f:
    data = json.load(f)

transitions = data['transitions']

print("=== H4 RECURSIVE PATTERN (ACTIVE VALUES ONLY) ===\n")

# Build sequences of ACTIVE drift values per lane
active_sequences = {lane: [] for lane in range(16)}
for t in transitions:
    k = t['from_puzzle']
    drifts = t['drifts']
    for lane in range(16):
        if k >= lane * 8:  # Lane is active
            active_sequences[lane].append(drifts[lane])

# Test recursive pattern: drift[i] = (a * drift[i-1] + b) mod 256
def test_affine_recurrence(sequence):
    """Test if sequence follows drift[i] = (a*drift[i-1] + b) mod 256"""
    if len(sequence) < 3:
        return None, None, 0

    best_a, best_b, best_acc = 0, 0, 0

    # Try all possible a, b values
    for a in range(256):
        for b in range(256):
            correct = 0
            for i in range(1, len(sequence)):
                predicted = (a * sequence[i-1] + b) % 256
                if predicted == sequence[i]:
                    correct += 1

            accuracy = 100 * correct / (len(sequence) - 1)
            if accuracy > best_acc:
                best_a, best_b, best_acc = a, b, accuracy

    return best_a, best_b, best_acc

# Test polynomial: drift[i] = (a * drift[i-1]^2 + b * drift[i-1] + c) mod 256
def test_quadratic_recurrence(sequence):
    """Test quadratic recurrence"""
    if len(sequence) < 3:
        return None, None, None, 0

    best_a, best_b, best_c, best_acc = 0, 0, 0, 0

    # Sample parameter space (full search would be 256^3)
    for a in range(0, 256, 8):
        for b in range(0, 256, 8):
            for c in range(0, 256, 8):
                correct = 0
                for i in range(1, len(sequence)):
                    prev = sequence[i-1]
                    predicted = (a * prev * prev + b * prev + c) % 256
                    if predicted == sequence[i]:
                        correct += 1

                accuracy = 100 * correct / (len(sequence) - 1)
                if accuracy > best_acc:
                    best_a, best_b, best_c, best_acc = a, b, c, accuracy

    return best_a, best_b, best_c, best_acc

print("1. AFFINE RECURRENCE: drift[i] = (a*drift[i-1] + b) mod 256\n")
for lane in range(9):  # Test lanes 0-8
    seq = active_sequences[lane]
    if len(seq) < 3:
        continue

    a, b, acc = test_affine_recurrence(seq)
    status = "✅" if acc == 100 else "⚠️" if acc > 90 else ""
    print(f"   Lane {lane}: a={a:3d}, b={b:3d}, accuracy={acc:6.2f}% ({int(acc*(len(seq)-1)/100)}/{len(seq)-1}) {status}")

print("\n2. QUADRATIC RECURRENCE (sampled): drift[i] = (a*drift[i-1]^2 + b*drift[i-1] + c) mod 256\n")
for lane in range(9):
    seq = active_sequences[lane]
    if len(seq) < 3:
        continue

    a, b, c, acc = test_quadratic_recurrence(seq)
    status = "✅" if acc == 100 else "⚠️" if acc > 90 else ""
    print(f"   Lane {lane}: a={a:3d}, b={b:3d}, c={c:3d}, accuracy={acc:6.2f}% {status}")

# Test two-step recurrence: drift[i] = f(drift[i-1], drift[i-2])
def test_two_step_affine(sequence):
    """Test drift[i] = (a*drift[i-1] + b*drift[i-2] + c) mod 256"""
    if len(sequence) < 4:
        return None, None, None, 0

    best_a, best_b, best_c, best_acc = 0, 0, 0, 0

    # Sample parameter space
    for a in range(0, 256, 8):
        for b in range(0, 256, 8):
            for c in range(0, 256, 8):
                correct = 0
                for i in range(2, len(sequence)):
                    predicted = (a * sequence[i-1] + b * sequence[i-2] + c) % 256
                    if predicted == sequence[i]:
                        correct += 1

                accuracy = 100 * correct / (len(sequence) - 2)
                if accuracy > best_acc:
                    best_a, best_b, best_c, best_acc = a, b, c, accuracy

    return best_a, best_b, best_c, best_acc

print("\n3. TWO-STEP AFFINE (sampled): drift[i] = (a*drift[i-1] + b*drift[i-2] + c) mod 256\n")
for lane in range(9):
    seq = active_sequences[lane]
    if len(seq) < 4:
        continue

    a, b, c, acc = test_two_step_affine(seq)
    status = "✅" if acc == 100 else "⚠️" if acc > 90 else ""
    print(f"   Lane {lane}: a={a:3d}, b={b:3d}, c={c:3d}, accuracy={acc:6.2f}% {status}")

print("\n" + "="*70)
print("NOTE: Quadratic and two-step tests use sampled parameter space (step=8)")
print("      If high accuracy found, can refine with full search in that region")
print("="*70)
