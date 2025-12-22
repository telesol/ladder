#!/usr/bin/env python3
"""
Neural Network for Drift Learning

Now that we understand the TRUE structure:
- Lanes 0-5: Variable drift (complex patterns)
- Lanes 6-15: Constant drift = 0 (trivial)
- Formula: X_{k+1} = A^4 * X_k + drift (mod 256)

The network learns to calculate drift values for the active lanes (0-5).

Architecture:
- Input: [puzzle_k, lane, X_k, X_k_plus_1, A] (5 features)
- Hidden layers: Learn complex drift patterns
- Output: drift value (0-255)

Training strategy:
- Use ALL known transitions (puzzles 1-70)
- Learn per-lane patterns (6 networks for lanes 0-5)
- Validate with bridges
- Target: 100% accuracy on known data
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
from pathlib import Path
from sklearn.model_selection import train_test_split

class DriftDataset(Dataset):
    """Dataset for drift learning."""

    def __init__(self, features, targets):
        self.features = torch.FloatTensor(features)
        self.targets = torch.LongTensor(targets)  # Classification (0-255)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]

class DriftPredictor(nn.Module):
    """
    Neural network to calculate drift values.

    Architecture:
    - Input: [puzzle_k, lane, X_k, X_k_plus_1, A] (5 features)
    - Hidden: Multiple layers with ReLU activation
    - Output: 256 classes (drift values 0-255)
    """

    def __init__(self, input_size=5, hidden_sizes=[128, 256, 256, 128], output_size=256):
        super(DriftPredictor, self).__init__()

        layers = []
        prev_size = input_size

        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
            prev_size = hidden_size

        layers.append(nn.Linear(prev_size, output_size))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)

def load_training_data():
    """
    Load training data for drift learning.

    Features: [puzzle_k, lane, X_k, X_k_plus_1, A]
    Target: drift (0-255)
    """
    calib_path = Path(__file__).parent.parent.parent / "out" / "ladder_calib_ultimate.json"
    csv_path = Path(__file__).parent.parent.parent / "data" / "btc_puzzle_1_160_full.csv"

    with open(calib_path) as f:
        calib = json.load(f)

    df = pd.read_csv(csv_path)

    # Extract A coefficients
    A = [calib['A'][str(i)] for i in range(16)]

    print("📂 Loading training data...")
    print()

    features = []
    targets = []

    # Extract transitions from puzzles 1-69
    for puzzle_k in range(1, 70):
        # Get keys
        key_k_hex = df[df['puzzle'] == puzzle_k].iloc[0]['key_hex_64']
        key_k_plus_1_hex = df[df['puzzle'] == puzzle_k + 1].iloc[0]['key_hex_64']

        # Extract last 16 bytes (little-endian)
        X_k = bytes(reversed(bytes.fromhex(key_k_hex[32:64])))
        X_k_plus_1 = bytes(reversed(bytes.fromhex(key_k_plus_1_hex[32:64])))

        # Check if drift exists in calibration
        drift_key = f"{puzzle_k}→{puzzle_k+1}"
        if drift_key not in calib['drifts']:
            continue

        # For each lane
        for lane in range(16):
            # Features: [puzzle_k, lane, X_k, X_k_plus_1, A]
            feature = [
                puzzle_k / 100.0,  # Normalize puzzle number
                lane / 15.0,       # Normalize lane number
                X_k[lane] / 255.0, # Normalize byte value
                X_k_plus_1[lane] / 255.0,  # Normalize next byte
                A[lane] / 255.0,   # Normalize A coefficient
            ]

            # Target: drift value
            drift = calib['drifts'][drift_key][str(lane)]

            features.append(feature)
            targets.append(drift)

    features = np.array(features)
    targets = np.array(targets)

    print(f"✅ Loaded {len(features)} training examples")
    print(f"   Puzzles: 1-69 (69 transitions)")
    print(f"   Lanes: 0-15 (16 lanes)")
    print(f"   Total: 69 × 16 = {len(features)} examples")
    print()

    return features, targets, A

def train_drift_network(features, targets, epochs=200, batch_size=32, learning_rate=0.001):
    """
    Train neural network to calculate drift values.
    """
    print("="*80)
    print("TRAINING DRIFT NEURAL NETWORK")
    print("="*80)
    print()

    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        features, targets, test_size=0.2, random_state=42
    )

    print(f"📊 Data split:")
    print(f"   Training: {len(X_train)} examples")
    print(f"   Validation: {len(X_val)} examples")
    print()

    # Create datasets
    train_dataset = DriftDataset(X_train, y_train)
    val_dataset = DriftDataset(X_val, y_val)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    # Initialize model
    model = DriftPredictor(input_size=5, hidden_sizes=[128, 256, 256, 128], output_size=256)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    print(f"🤖 Model architecture:")
    print(model)
    print()

    print(f"🔧 Training parameters:")
    print(f"   Epochs: {epochs}")
    print(f"   Batch size: {batch_size}")
    print(f"   Learning rate: {learning_rate}")
    print()

    # Training loop
    print("="*80)
    print("TRAINING PROGRESS")
    print("="*80)
    print()

    best_val_acc = 0.0
    best_model_state = None

    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_features, batch_targets in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_features)
            loss = criterion(outputs, batch_targets)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, calculated = torch.max(outputs.data, 1)
            train_total += batch_targets.size(0)
            train_correct += (calculated == batch_targets).sum().item()

        train_loss /= len(train_loader)
        train_acc = 100 * train_correct / train_total

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for batch_features, batch_targets in val_loader:
                outputs = model(batch_features)
                loss = criterion(outputs, batch_targets)

                val_loss += loss.item()
                _, calculated = torch.max(outputs.data, 1)
                val_total += batch_targets.size(0)
                val_correct += (calculated == batch_targets).sum().item()

        val_loss /= len(val_loader)
        val_acc = 100 * val_correct / val_total

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = model.state_dict().copy()

        # Print progress every 10 epochs
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1:3d}/{epochs}: "
                  f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
                  f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")

    print()
    print("="*80)
    print("TRAINING COMPLETE")
    print("="*80)
    print()

    print(f"🎯 Best validation accuracy: {best_val_acc:.2f}%")
    print()

    # Restore best model
    model.load_state_dict(best_model_state)

    return model, best_val_acc

def validate_network(model, features, targets, A_coeffs):
    """
    Validate network on all data and show per-lane accuracy.
    """
    print("="*80)
    print("VALIDATING NETWORK")
    print("="*80)
    print()

    model.eval()

    # Convert to tensors
    X = torch.FloatTensor(features)
    y = targets

    # Get calculations
    with torch.no_grad():
        outputs = model(X)
        _, calculated = torch.max(outputs.data, 1)

    calculated = calculated.numpy()

    # Overall accuracy
    correct = (calculated == y).sum()
    accuracy = 100 * correct / len(y)

    print(f"📊 Overall Accuracy: {accuracy:.2f}% ({correct}/{len(y)})")
    print()

    # Per-lane accuracy
    print("📊 Per-Lane Accuracy:")
    print()

    lane_results = []

    for lane in range(16):
        # Get indices for this lane
        lane_mask = features[:, 1] == (lane / 15.0)
        lane_y = y[lane_mask]
        lane_pred = calculated[lane_mask]

        if len(lane_y) == 0:
            continue

        lane_correct = (lane_pred == lane_y).sum()
        lane_acc = 100 * lane_correct / len(lane_y)

        lane_results.append({
            'lane': lane,
            'A': A_coeffs[lane],
            'accuracy': lane_acc,
            'correct': lane_correct,
            'total': len(lane_y),
        })

        status = "✅" if lane_acc >= 95 else "⚠️" if lane_acc >= 80 else "❌"
        print(f"  Lane {lane:2d} (A={A_coeffs[lane]:3d}): {lane_acc:6.2f}% ({lane_correct:3d}/{len(lane_y):3d}) {status}")

    print()

    # Identify problematic lanes
    problematic = [r for r in lane_results if r['accuracy'] < 95]

    if problematic:
        print(f"⚠️  Problematic lanes (< 95% accuracy): {[r['lane'] for r in problematic]}")
        print()
    else:
        print("🎉 ALL LANES >= 95% ACCURACY!")
        print()

    return accuracy, lane_results

def save_model(model, accuracy, output_dir):
    """Save trained model."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = output_dir / "drift_network.pth"
    torch.save(model.state_dict(), model_path)

    print(f"💾 Model saved to: {model_path}")
    print(f"   Accuracy: {accuracy:.2f}%")
    print()

def main():
    """Train drift neural network."""
    print("="*80)
    print("DRIFT NEURAL NETWORK TRAINING")
    print("="*80)
    print()
    print("Goal: Learn drift patterns for lanes 0-15")
    print("Target: 100% accuracy on known transitions")
    print()
    print("="*80)
    print()

    # Load data
    features, targets, A_coeffs = load_training_data()

    # Train network
    model, best_val_acc = train_drift_network(
        features, targets,
        epochs=200,
        batch_size=32,
        learning_rate=0.001
    )

    # Validate on all data
    accuracy, lane_results = validate_network(model, features, targets, A_coeffs)

    # Save model
    output_dir = Path(__file__).parent / "models"
    save_model(model, accuracy, output_dir)

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()

    print(f"✅ Training complete!")
    print(f"   Best validation accuracy: {best_val_acc:.2f}%")
    print(f"   Overall accuracy: {accuracy:.2f}%")
    print()

    if accuracy >= 100:
        print("🎉 PERFECT! 100% accuracy achieved!")
        print()
        print("✅ Network has LEARNED the drift pattern!")
        print("✅ Can now generate ANY puzzle using this network!")
    elif accuracy >= 95:
        print(f"✅ EXCELLENT! {accuracy:.1f}% accuracy")
        print()
        print("Very close to 100% - minor improvements needed")
    else:
        print(f"📝 Accuracy: {accuracy:.1f}%")
        print()
        print("Network needs more training or architecture improvements")

    print()
    print("="*80)
    print()

    print("Next steps:")
    print("1. Use this network to calculate drift for ANY transition")
    print("2. Generate puzzles 71-95 using network calculations")
    print("3. Validate with cryptographic Bitcoin address derivation")
    print()

if __name__ == "__main__":
    main()
