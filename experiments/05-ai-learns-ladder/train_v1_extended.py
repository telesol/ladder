#!/usr/bin/env python3
"""
Extended training for v1 architecture with more epochs.
Uses the same architecture that achieved 91.39% but trains longer.
"""

import sys
from pathlib import Path

# Import from original drift_neural_network.py
sys.path.insert(0, str(Path(__file__).parent))
from drift_neural_network import load_training_data, validate_network, save_model, DriftPredictor, DriftDataset

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import argparse


def train_v1_extended(features, targets, epochs=1000, batch_size=32, learning_rate=0.001, patience=100):
    """
    Train v1 architecture with more epochs and patience.
    """
    print("="*80)
    print("EXTENDED TRAINING FOR V1 ARCHITECTURE")
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

    # Initialize model (same as v1)
    model = DriftPredictor(input_size=5, hidden_sizes=[128, 256, 256, 128], output_size=256)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=30)

    print(f"🤖 Model architecture (v1):")
    print(model)
    print()

    total_params = sum(p.numel() for p in model.parameters())
    print(f"📊 Parameters: {total_params:,} total")
    print()

    print(f"🔧 Training parameters:")
    print(f"   Epochs: {epochs}")
    print(f"   Batch size: {batch_size}")
    print(f"   Learning rate: {learning_rate}")
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

        # Learning rate scheduling
        scheduler.step(val_acc)

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = model.state_dict().copy()
            patience_counter = 0
        else:
            patience_counter += 1

        # Print progress every 20 epochs
        if (epoch + 1) % 20 == 0:
            current_lr = optimizer.param_groups[0]['lr']
            print(f"Epoch {epoch+1:4d}/{epochs}: "
                  f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
                  f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}% | "
                  f"LR: {current_lr:.6f} | Best: {best_val_acc:.2f}% | "
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


def main():
    """Train v1 architecture with extended epochs."""
    parser = argparse.ArgumentParser(description='Extended training for v1 architecture')
    parser.add_argument('--epochs', type=int, default=1000, help='Number of training epochs (default: 1000)')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size (default: 32)')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate (default: 0.001)')
    parser.add_argument('--patience', type=int, default=100, help='Early stopping patience (default: 100)')

    args = parser.parse_args()

    print("="*80)
    print("EXTENDED TRAINING - V1 ARCHITECTURE")
    print("="*80)
    print()
    print("Goal: Push v1 architecture (91.39%) towards 95%+")
    print("Strategy: Train longer with more patience")
    print()
    print("="*80)
    print()

    # Load data
    features, targets, A_coeffs = load_training_data()

    # Train network
    model, best_val_acc = train_v1_extended(
        features, targets,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        patience=args.patience
    )

    # Validate on all data
    accuracy, lane_results = validate_network(model, features, targets, A_coeffs)

    # Save model
    output_dir = Path(__file__).parent / "models"
    model_path = output_dir / "drift_network_v1_extended.pth"
    output_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_path)

    print(f"💾 Model saved to: {model_path}")
    print(f"   Accuracy: {accuracy:.2f}%")
    print()

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

    print(f"📊 Comparison with original v1:")
    print(f"   v1 original (200 epochs): {v1_accuracy:.2f}%")
    print(f"   v1 extended ({args.epochs} epochs): {accuracy:.2f}%")
    print(f"   Improvement: {improvement:+.2f}%")
    print()

    if accuracy >= 100:
        print("🎉 PERFECT! 100% accuracy achieved!")
        print()
        print("✅ Network has LEARNED the drift pattern!")
    elif accuracy >= 95:
        print(f"🎊 EXCELLENT! {accuracy:.1f}% accuracy")
        print()
        print("Very close to 100% - ready for puzzle generation!")
    elif accuracy > v1_accuracy:
        print(f"✅ IMPROVED! From {v1_accuracy:.1f}% to {accuracy:.1f}%")
        print()
        print("Extended training helped - network is learning better!")
    else:
        print(f"📝 Same accuracy: {accuracy:.1f}%")
        print()
        print("Extended training didn't improve - consider alternative approaches")

    print()
    print("="*80)
    print()


if __name__ == "__main__":
    main()
