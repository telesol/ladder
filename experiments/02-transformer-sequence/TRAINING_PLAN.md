# Transformer Training Plan

## Quick Start (Recommended)

### Step 1: Quick Test (5 minutes)
```bash
cd /home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence

python scripts/train_transformer.py \
  --epochs 10 \
  --batch-size 8 \
  --lr 0.001 \
  --hidden-size 128 \
  --device cpu
```

**Expected result:** 50-70% accuracy after 10 epochs

---

### Step 2: Full Training (2-3 hours)
```bash
python scripts/train_transformer.py \
  --epochs 100 \
  --batch-size 8 \
  --lr 0.001 \
  --hidden-size 128 \
  --device cpu
```

**Target:** 95-100% validation accuracy (to match PySR baseline)

---

### Step 3: Compare with PySR
After training completes, the script will automatically show:
```
PySR (symbolic regression): 100.00% (PROVEN)
Transformer (neural network): XX.XX%
```

---

## Model Architecture

**SimpleLanePredictor:**
- 16 independent neural networks (one per lane)
- Each lane: 1 → 128 → 128 → 256
- Total parameters: ~330,000
- Mirrors PySR's discovery of lane independence

---

## Training Data

Already prepared ✅:
- Training: 59 puzzle pairs (puzzles 1-60)
- Validation: 9 puzzle pairs (puzzles 61-70)
- Format: NumPy → PyTorch tensors

---

## Success Metrics

| Accuracy | Meaning |
|----------|---------|
| 100% | Perfect! Matches PySR formula |
| 95-99% | Very good, minor differences |
| 80-94% | Good, but significant gap |
| <80% | Needs investigation |

---

## If Results Are Good (≥95%)

Next steps:
1. Analyze which lanes the model learns easily vs. struggles with
2. Compare lane-by-lane accuracy with PySR exponents
3. Test on bridge rows (multi-step calculation)
4. Extract learned patterns (visualize weights)

---

## If Results Are Poor (<95%)

Try:
1. Larger hidden size (256 instead of 128)
2. More epochs (200 instead of 100)
3. Different learning rate (0.01 or 0.0001)
4. Add regularization (dropout, weight decay)

---

## Hardware Notes

**CPU (Current):**
- Training time: ~2-3 hours for 100 epochs
- Batch size: 8 (can try 16 if RAM allows)

**GPU (If available):**
- Add `--device cuda`
- Training time: ~15-30 minutes
- Can use larger batch size (32-64)

---

## Checkpointing

Model automatically saves to:
```
models/best_model.pth  (best validation accuracy)
```

Resume training from checkpoint (future feature):
```bash
python scripts/train_transformer.py --resume models/best_model.pth
```

---

## Comparison Baseline

**PySR Formula (PROVEN):**
- Accuracy: 100.00%
- Verified on 74 puzzles
- Formula: X_{k+1}(ℓ) = X_k(ℓ)^n (mod 256)
- Exponents: [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

**Goal:** Neural network should learn the same pattern implicitly.
