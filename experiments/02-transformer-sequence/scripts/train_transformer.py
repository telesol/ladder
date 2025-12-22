#!/usr/bin/env python3
"""
Train Transformer Model for Bitcoin Puzzle Sequence Learning

Compares with PySR baseline (100% accuracy proven)
"""

import argparse
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
import time

# Proven PySR exponents for comparison
PYSR_EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

class PuzzleDataset(Dataset):
    """Dataset for puzzle sequence pairs."""
    def __init__(self, X, y):
        # Convert to float32 and normalize to [0, 1]
        self.X = torch.FloatTensor(X) / 255.0
        self.y = torch.LongTensor(y)  # Keep as integers for classification

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class SimpleLanePredictor(nn.Module):
    """
    Simplified model: Treat each lane independently

    This mirrors the PySR discovery that lanes are independent.
    Each lane has its own small network.
    """
    def __init__(self, hidden_size=64):
        super().__init__()

        # 16 independent networks (one per lane)
        self.lane_networks = nn.ModuleList([
            nn.Sequential(
                nn.Linear(1, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, 256)  # Output: 256 classes (0-255)
            )
            for _ in range(16)
        ])

    def forward(self, x):
        """
        x: (batch, 16) - 16 lanes, normalized [0, 1]
        output: (batch, 16, 256) - 16 lanes, 256 class logits each
        """
        batch_size = x.shape[0]
        outputs = []

        for lane in range(16):
            # Extract single lane value
            lane_input = x[:, lane:lane+1]  # (batch, 1)

            # Pass through lane-specific network
            lane_output = self.lane_networks[lane](lane_input)  # (batch, 256)

            outputs.append(lane_output)

        # Stack: (batch, 16, 256)
        return torch.stack(outputs, dim=1)

def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    correct_bytes = 0
    total_bytes = 0

    for batch_X, batch_y in dataloader:
        batch_X = batch_X.to(device)
        batch_y = batch_y.to(device)

        # Forward pass
        logits = model(batch_X)  # (batch, 16, 256)

        # Calculate loss for all lanes
        loss = 0
        for lane in range(16):
            lane_logits = logits[:, lane, :]  # (batch, 256)
            lane_targets = batch_y[:, lane]  # (batch,)
            loss += criterion(lane_logits, lane_targets)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

        # Calculate accuracy
        calculations = torch.argmax(logits, dim=2)  # (batch, 16)
        correct_bytes += (calculations == batch_y).sum().item()
        total_bytes += batch_y.numel()

    avg_loss = total_loss / len(dataloader)
    accuracy = (correct_bytes / total_bytes) * 100

    return avg_loss, accuracy

def evaluate(model, dataloader, criterion, device):
    """Evaluate model."""
    model.eval()
    total_loss = 0
    correct_bytes = 0
    total_bytes = 0
    all_predictions = []
    all_targets = []

    with torch.no_grad():
        for batch_X, batch_y in dataloader:
            batch_X = batch_X.to(device)
            batch_y = batch_y.to(device)

            # Forward pass
            logits = model(batch_X)

            # Calculate loss
            loss = 0
            for lane in range(16):
                lane_logits = logits[:, lane, :]
                lane_targets = batch_y[:, lane]
                loss += criterion(lane_logits, lane_targets)

            total_loss += loss.item()

            # Get calculations
            calculations = torch.argmax(logits, dim=2)
            correct_bytes += (calculations == batch_y).sum().item()
            total_bytes += batch_y.numel()

            all_predictions.append(calculations.cpu().numpy())
            all_targets.append(batch_y.cpu().numpy())

    avg_loss = total_loss / len(dataloader)
    accuracy = (correct_bytes / total_bytes) * 100

    all_predictions = np.concatenate(all_predictions, axis=0)
    all_targets = np.concatenate(all_targets, axis=0)

    return avg_loss, accuracy, all_predictions, all_targets

def main():
    parser = argparse.ArgumentParser(description='Train transformer for puzzle sequence')
    parser.add_argument('--run-dir', type=str, default=None, help='Run directory (e.g., runs/run_001_baseline)')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=8, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--hidden-size', type=int, default=128, help='Hidden layer size')
    parser.add_argument('--device', type=str, default='auto', help='Device (cuda/cpu/auto)')
    parser.add_argument('--real-data', action='store_true', help='Use real Bitcoin puzzle data')
    args = parser.parse_args()

    # Setup run directory
    if args.run_dir:
        # Handle both "run_004_baseline" and "runs/run_004_baseline"
        if not args.run_dir.startswith('runs/'):
            run_dir = Path(__file__).parent.parent / "runs" / args.run_dir
        else:
            run_dir = Path(__file__).parent.parent / args.run_dir

        if not run_dir.exists():
            print(f"❌ Run directory not found: {run_dir}")
            print(f"   Available runs:")
            runs_dir = Path(__file__).parent.parent / "runs"
            if runs_dir.exists():
                for d in sorted(runs_dir.glob("run_*")):
                    print(f"      {d.name}")
            print(f"\n   Create new run: python scripts/create_run.py --name baseline")
            return

        # Load config from run directory if exists
        config_file = run_dir / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                run_config = json.load(f)
                # Override with config values if not specified in command line
                if 'config' in run_config:
                    cfg = run_config['config']
                    args.epochs = cfg.get('epochs', args.epochs)
                    args.batch_size = cfg.get('batch_size', args.batch_size)
                    args.lr = cfg.get('learning_rate', args.lr)
                    args.hidden_size = cfg.get('hidden_size', args.hidden_size)
                    args.device = cfg.get('device', args.device)

        checkpoint_dir = run_dir / "checkpoints"
        log_dir = run_dir / "logs"
    else:
        # Default: save to models/ and results/
        run_dir = Path(__file__).parent.parent
        checkpoint_dir = run_dir / "models"
        log_dir = run_dir / "results"

    checkpoint_dir.mkdir(exist_ok=True)
    log_dir.mkdir(exist_ok=True)

    # Setup device
    if args.device == 'auto':
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(args.device)

    print("=" * 70)
    print("Transformer Training for Bitcoin Puzzle Sequence")
    print("=" * 70)
    print(f"\n⚙️  Configuration:")
    print(f"   Device: {device}")
    print(f"   Epochs: {args.epochs}")
    print(f"   Batch size: {args.batch_size}")
    print(f"   Learning rate: {args.lr}")
    print(f"   Hidden size: {args.hidden_size}")

    # Load data
    data_dir = Path(__file__).parent.parent / "data"

    print(f"\n📂 Loading data from {data_dir}...")

    if args.real_data:
        print(f"   Using REAL Bitcoin puzzle data")
        train_X = np.load(data_dir / "train_X_real.npy")
        train_y = np.load(data_dir / "train_y_real.npy")
        val_X = np.load(data_dir / "val_X_real.npy")
        val_y = np.load(data_dir / "val_y_real.npy")
    else:
        train_X = np.load(data_dir / "train_X.npy")
        train_y = np.load(data_dir / "train_y.npy")
        val_X = np.load(data_dir / "val_X.npy")
        val_y = np.load(data_dir / "val_y.npy")

    print(f"   Train: {train_X.shape} -> {train_y.shape}")
    print(f"   Val: {val_X.shape} -> {val_y.shape}")

    # Create datasets
    train_dataset = PuzzleDataset(train_X, train_y)
    val_dataset = PuzzleDataset(val_X, val_y)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)

    # Create model
    model = SimpleLanePredictor(hidden_size=args.hidden_size).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    print(f"\n🧠 Model: SimpleLanePredictor (16 independent lane networks)")
    print(f"   Total parameters: {total_params:,}")
    print(f"   Architecture: 1 -> {args.hidden_size} -> {args.hidden_size} -> 256 (per lane)")

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    # Training loop
    print(f"\n🚀 Starting training...")
    print("=" * 70)

    best_val_acc = 0
    best_epoch = 0
    history = []

    start_time = time.time()

    for epoch in range(1, args.epochs + 1):
        # Train
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)

        # Validate
        val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, device)

        # Save history
        history.append({
            'epoch': epoch,
            'train_loss': float(train_loss),
            'train_acc': float(train_acc),
            'val_loss': float(val_loss),
            'val_acc': float(val_acc)
        })

        # Print progress
        if epoch % 10 == 0 or epoch == 1:
            print(f"Epoch {epoch:3d}/{args.epochs} | "
                  f"Train Loss: {train_loss:.4f} Acc: {train_acc:6.2f}% | "
                  f"Val Loss: {val_loss:.4f} Acc: {val_acc:6.2f}%")

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch

            # Save checkpoint
            checkpoint_path = checkpoint_dir / "best_model.pth"

            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'config': {
                    'hidden_size': args.hidden_size,
                    'input_dim': 16,
                    'output_dim': 16
                }
            }, checkpoint_path)

    elapsed_time = time.time() - start_time

    print("=" * 70)
    print(f"\n✅ Training complete!")
    print(f"   Total time: {elapsed_time:.1f}s ({elapsed_time/60:.1f} min)")
    print(f"   Best validation accuracy: {best_val_acc:.2f}% (epoch {best_epoch})")

    # Compare with PySR
    print(f"\n📊 Comparison with PySR:")
    print(f"   PySR (symbolic regression): 100.00% (PROVEN)")
    print(f"   Transformer (neural network): {best_val_acc:.2f}%")

    if best_val_acc >= 100.0:
        print(f"   ✅ PERFECT! Transformer matches PySR formula!")
    elif best_val_acc >= 95.0:
        print(f"   ⚠️  Good, but not perfect. Gap: {100.0 - best_val_acc:.2f}%")
    else:
        print(f"   ❌ Transformer underperforms. Gap: {100.0 - best_val_acc:.2f}%")

    # Save results
    with open(log_dir / "training_history.json", 'w') as f:
        json.dump(history, f, indent=2)

    # Save final results summary
    final_results = {
        'best_epoch': best_epoch,
        'best_val_acc': best_val_acc,
        'final_train_acc': history[-1]['train_acc'],
        'pysr_baseline': 100.0,
        'gap': 100.0 - best_val_acc,
        'training_time_seconds': elapsed_time,
        'config': {
            'epochs': args.epochs,
            'batch_size': args.batch_size,
            'learning_rate': args.lr,
            'hidden_size': args.hidden_size,
            'device': str(device)
        }
    }

    with open(log_dir / "final_results.json", 'w') as f:
        json.dump(final_results, f, indent=2)

    print(f"\n💾 Results saved:")
    print(f"   {log_dir}/training_history.json")
    print(f"   {log_dir}/final_results.json")
    print(f"   {checkpoint_path}")

    print("\n📝 Next steps:")
    print(f"   1. Evaluate on test set: python scripts/evaluate_transformer.py")
    print(f"   2. Compare with PySR: python scripts/compare_with_pysr.py")

if __name__ == "__main__":
    main()
