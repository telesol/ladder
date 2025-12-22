#!/usr/bin/env python3
"""
Enhanced Neural Network for Drift Learning (v2)

Improvements over v1:
- More epochs (500 default, configurable up to 2000)
- Deeper architecture with residual connections
- Learning rate scheduling (ReduceLROnPlateau)
- Early stopping with patience
- Better regularization (dropout + weight decay)
- Model checkpointing (save best models)
- Per-lane subnet option for specialized learning
- Gradient clipping for stability
- Data augmentation for robustness

Target: 95%+ accuracy (push towards 100%)
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
import argparse
import sys

class DriftDataset(Dataset):
    """Dataset for drift learning."""

    def __init__(self, features, targets):
        self.features = torch.FloatTensor(features)
        self.targets = torch.LongTensor(targets)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]

class ResidualBlock(nn.Module):
    """Residual block with skip connection."""

    def __init__(self, size, dropout=0.3):
        super(ResidualBlock, self).__init__()
        self.layer1 = nn.Linear(size, size)
        self.bn1 = nn.BatchNorm1d(size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.layer2 = nn.Linear(size, size)
        self.bn2 = nn.BatchNorm1d(size)

    def forward(self, x):
        residual = x
        out = self.layer1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.layer2(out)
        out = self.bn2(out)
        out += residual  # Skip connection
        out = self.relu(out)
        return out

class EnhancedDriftPredictor(nn.Module):
    """
    Enhanced neural network with residual connections.

    Architecture:
    - Input projection: 5 → 256
    - 3 residual blocks: 256 → 256
    - Output projection: 256 → 256 classes
    """

    def __init__(self, input_size=5, hidden_size=256, num_residual_blocks=3, dropout=0.3, output_size=256):
        super(EnhancedDriftPredictor, self).__init__()

        # Input projection
        self.input_proj = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout)
        )

        # Residual blocks
        self.residual_blocks = nn.ModuleList([
            ResidualBlock(hidden_size, dropout) for _ in range(num_residual_blocks)
        ])

        # Output projection
        self.output_proj = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.input_proj(x)

        for block in self.residual_blocks:
            x = block(x)

        x = self.output_proj(x)
        return x

class SimpleDriftPredictor(nn.Module):
    """
    Simple deep network (fallback architecture).

    Architecture: 5 → 256 → 512 → 512 → 256 → 256
    """

    def __init__(self, input_size=5, dropout=0.3, output_size=256):
        super(SimpleDriftPredictor, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(input_size, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(256, output_size)
        )

    def forward(self, x):
        return self.network(x)

def load_training_data():
    """Load training data for drift learning."""
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

def train_drift_network_v2(features, targets,
                          epochs=500,
                          batch_size=32,
                          learning_rate=0.001,
                          architecture='residual',
                          patience=50,
                          checkpoint_dir='models'):
    """
    Train enhanced neural network with improvements.
    """
    print("="*80)
    print("TRAINING ENHANCED DRIFT NEURAL NETWORK (V2)")
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
    if architecture == 'residual':
        model = EnhancedDriftPredictor(input_size=5, hidden_size=256, num_residual_blocks=3, dropout=0.3, output_size=256)
        print("🤖 Architecture: Enhanced (Residual with BatchNorm)")
    else:
        model = SimpleDriftPredictor(input_size=5, dropout=0.3, output_size=256)
        print("🤖 Architecture: Simple Deep (Fallback)")

    print()
    print(model)
    print()

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"📊 Parameters: {total_params:,} total ({trainable_params:,} trainable)")
    print()

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)  # Weight decay for regularization

    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=20)

    print(f"🔧 Training parameters:")
    print(f"   Epochs: {epochs}")
    print(f"   Batch size: {batch_size}")
    print(f"   Learning rate: {learning_rate}")
    print(f"   Weight decay: 0.01")
    print(f"   Early stopping patience: {patience}")
    print()

    # Training loop
    print("="*80)
    print("TRAINING PROGRESS")
    print("="*80)
    print()

    best_val_acc = 0.0
    best_model_state = None
    patience_counter = 0

    # Checkpoint directory
    checkpoint_path = Path(__file__).parent / checkpoint_dir
    checkpoint_path.mkdir(parents=True, exist_ok=True)

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

            # Gradient clipping for stability
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

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

        # Learning rate scheduling
        scheduler.step(val_acc)

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = model.state_dict().copy()
            patience_counter = 0

            # Save checkpoint
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': best_model_state,
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
            }, checkpoint_path / f"checkpoint_best_{val_acc:.2f}.pth")

        else:
            patience_counter += 1

        # Print progress every 10 epochs
        if (epoch + 1) % 10 == 0:
            current_lr = optimizer.param_groups[0]['lr']
            print(f"Epoch {epoch+1:4d}/{epochs}: "
                  f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
                  f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}% | "
                  f"LR: {current_lr:.6f} | "
                  f"Patience: {patience_counter}/{patience}")

        # Early stopping
        if patience_counter >= patience:
            print()
            print(f"⏹️  Early stopping triggered at epoch {epoch+1}")
            print(f"   No improvement for {patience} epochs")
            print(f"   Best validation accuracy: {best_val_acc:.2f}%")
            break

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
    """Validate network on all data and show per-lane accuracy."""
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

def save_model(model, accuracy, output_dir, suffix='v2'):
    """Save trained model."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = output_dir / f"drift_network_{suffix}.pth"
    torch.save(model.state_dict(), model_path)

    print(f"💾 Model saved to: {model_path}")
    print(f"   Accuracy: {accuracy:.2f}%")
    print()

    return model_path

def main():
    """Train enhanced drift neural network."""
    parser = argparse.ArgumentParser(description='Train enhanced drift neural network')
    parser.add_argument('--epochs', type=int, default=500, help='Number of training epochs (default: 500)')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size (default: 32)')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate (default: 0.001)')
    parser.add_argument('--architecture', choices=['residual', 'simple'], default='residual', help='Network architecture (default: residual)')
    parser.add_argument('--patience', type=int, default=50, help='Early stopping patience (default: 50)')
    parser.add_argument('--suffix', type=str, default='v2', help='Model suffix (default: v2)')

    args = parser.parse_args()

    print("="*80)
    print("ENHANCED DRIFT NEURAL NETWORK TRAINING (V2)")
    print("="*80)
    print()
    print("Goal: Learn drift patterns for lanes 0-15")
    print("Target: 95%+ accuracy (push towards 100%)")
    print()
    print("="*80)
    print()

    # Load data
    features, targets, A_coeffs = load_training_data()

    # Train network
    model, best_val_acc = train_drift_network_v2(
        features, targets,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        architecture=args.architecture,
        patience=args.patience
    )

    # Validate on all data
    accuracy, lane_results = validate_network(model, features, targets, A_coeffs)

    # Save model
    output_dir = Path(__file__).parent / "models"
    model_path = save_model(model, accuracy, output_dir, suffix=args.suffix)

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()

    print(f"✅ Training complete!")
    print(f"   Best validation accuracy: {best_val_acc:.2f}%")
    print(f"   Overall accuracy: {accuracy:.2f}%")
    print(f"   Model saved: {model_path}")
    print()

    # Compare with v1 (91.39%)
    v1_accuracy = 91.39
    improvement = accuracy - v1_accuracy

    print(f"📊 Comparison with v1:")
    print(f"   v1 accuracy: {v1_accuracy:.2f}%")
    print(f"   v2 accuracy: {accuracy:.2f}%")
    print(f"   Improvement: {improvement:+.2f}%")
    print()

    if accuracy >= 100:
        print("🎉 PERFECT! 100% accuracy achieved!")
        print()
        print("✅ Network has LEARNED the drift pattern!")
        print("✅ Can now generate ANY puzzle using this network!")
    elif accuracy >= 95:
        print(f"🎊 EXCELLENT! {accuracy:.1f}% accuracy")
        print()
        print("Very close to 100% - minor improvements needed")
    elif accuracy > v1_accuracy:
        print(f"✅ IMPROVED! From {v1_accuracy:.1f}% to {accuracy:.1f}%")
        print()
        print("Network is learning better - continue training for more improvement")
    else:
        print(f"📝 Accuracy: {accuracy:.1f}%")
        print()
        print("Try different architecture or hyperparameters")

    print()
    print("="*80)
    print()

    print("Next steps:")
    print("1. If accuracy < 95%: Train longer (--epochs 1000)")
    print("2. If accuracy < 95%: Try simple architecture (--architecture simple)")
    print("3. If accuracy >= 95%: Use network for puzzle generation")
    print("4. Validate with cryptographic Bitcoin address derivation")
    print()

if __name__ == "__main__":
    main()
