#!/usr/bin/env python3
"""
Create a new training run folder with configuration

Usage:
    python scripts/create_run.py --name baseline --epochs 100 --hidden-size 128
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

def create_run_folder(name, config):
    """Create a new run folder with configuration."""

    base_dir = Path(__file__).parent.parent / "runs"
    base_dir.mkdir(exist_ok=True)

    # Find next run number
    existing_runs = sorted(base_dir.glob("run_*"))
    if existing_runs:
        last_run = existing_runs[-1].name
        last_num = int(last_run.split('_')[1])
        run_num = last_num + 1
    else:
        run_num = 1

    # Create run folder
    run_name = f"run_{run_num:03d}_{name}"
    run_dir = base_dir / run_name
    run_dir.mkdir(exist_ok=True)

    # Create subdirectories
    (run_dir / "checkpoints").mkdir(exist_ok=True)
    (run_dir / "logs").mkdir(exist_ok=True)

    # Save configuration
    config_full = {
        'run_number': run_num,
        'run_name': run_name,
        'created_at': datetime.now().isoformat(),
        'config': config,
        'status': 'created'
    }

    with open(run_dir / "config.json", 'w') as f:
        json.dump(config_full, f, indent=2)

    # Create README
    readme_content = f"""# Training Run {run_num:03d}: {name}

## Configuration

```json
{json.dumps(config, indent=2)}
```

## Created
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Status
- [ ] Training started
- [ ] Training completed
- [ ] Results analyzed

## Training Command

```bash
cd /home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence

python3 scripts/train_transformer.py \\
  --run-dir runs/{run_name} \\
  --epochs {config['epochs']} \\
  --batch-size {config['batch_size']} \\
  --lr {config['learning_rate']} \\
  --hidden-size {config['hidden_size']} \\
  --device {config['device']}
```

## Results

(Fill in after training completes)

### Final Accuracy
- Training: ___%
- Validation: ___%

### Comparison with PySR
- PySR (baseline): 100.00%
- This run: ___%
- Gap: ___%

### Notes
-
"""

    with open(run_dir / "README.md", 'w') as f:
        f.write(readme_content)

    print(f"✅ Created run folder: {run_dir}")
    print(f"   Run number: {run_num}")
    print(f"   Run name: {run_name}")
    print(f"   Configuration saved to: {run_dir}/config.json")

    return run_dir, config_full

def main():
    parser = argparse.ArgumentParser(description='Create a new training run')
    parser.add_argument('--name', type=str, required=True, help='Run name (e.g., baseline, larger_hidden)')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=8, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--hidden-size', type=int, default=128, help='Hidden layer size')
    parser.add_argument('--device', type=str, default='cpu', help='Device (cpu/cuda)')
    parser.add_argument('--notes', type=str, default='', help='Additional notes')
    args = parser.parse_args()

    config = {
        'epochs': args.epochs,
        'batch_size': args.batch_size,
        'learning_rate': args.lr,
        'hidden_size': args.hidden_size,
        'device': args.device,
        'notes': args.notes
    }

    run_dir, config_full = create_run_folder(args.name, config)

    print(f"\n📋 Next steps:")
    print(f"   1. Review config: cat {run_dir}/config.json")
    print(f"   2. Start training: python3 scripts/train_transformer.py --run-dir {run_dir.name}")
    print(f"   3. Monitor progress: tail -f {run_dir}/logs/training.log")

if __name__ == "__main__":
    main()
