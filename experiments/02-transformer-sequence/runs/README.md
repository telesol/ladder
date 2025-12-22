# Training Runs

This directory contains individual training runs, each in its own subfolder.

## Structure

```
runs/
├── run_001_baseline/           ← First run (baseline config)
│   ├── config.json             (hyperparameters)
│   ├── README.md               (run documentation)
│   ├── checkpoints/
│   │   └── best_model.pth      (saved model)
│   └── logs/
│       ├── training_history.json
│       ├── final_results.json
│       └── training.log
│
├── run_002_larger_hidden/      ← Second run (larger network)
├── run_003_more_epochs/        ← Third run (more training)
└── ...
```

## Creating a New Run

### Method 1: Use master script (recommended)
```bash
./run_experiment.sh baseline 100 128
#                   ↑        ↑   ↑
#                   name   epochs hidden_size
```

### Method 2: Manual creation
```bash
# Create run directory
python3 scripts/create_run.py \
  --name baseline \
  --epochs 100 \
  --hidden-size 128

# Train
python3 scripts/train_transformer.py --run-dir runs/run_001_baseline
```

## Comparing Runs

After running multiple experiments:

```bash
# List all runs
ls -lh runs/

# Compare results
for run in runs/run_*/logs/final_results.json; do
  echo "$(dirname $(dirname $run)):"
  cat $run | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'  Val acc: {d[\"best_val_acc\"]:.2f}%')"
done
```

## Baseline Configuration

**Run 001: Baseline**
- Epochs: 100
- Hidden size: 128
- Batch size: 8
- Learning rate: 0.001
- Device: CPU

**Target:** 95-100% validation accuracy (match PySR)

---

## Experiment Ideas

### Run 002: Larger Network
```bash
./run_experiment.sh larger_hidden 100 256
```

### Run 003: More Training
```bash
./run_experiment.sh more_epochs 200 128
```

### Run 004: Higher Learning Rate
```bash
python3 scripts/create_run.py --name high_lr --lr 0.01
python3 scripts/train_transformer.py --run-dir runs/run_004_high_lr
```

### Run 005: Lower Learning Rate
```bash
python3 scripts/create_run.py --name low_lr --lr 0.0001 --epochs 200
python3 scripts/train_transformer.py --run-dir runs/run_005_low_lr
```

---

## Run Status Legend

- 🆕 Created (config saved, not started)
- 🏃 Running (training in progress)
- ✅ Complete (training finished)
- ⚠️ Incomplete (training interrupted)
- ❌ Failed (error during training)
