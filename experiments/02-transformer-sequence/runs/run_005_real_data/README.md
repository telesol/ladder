# Training Run 005: real_data

## Configuration

```json
{
  "epochs": 100,
  "batch_size": 8,
  "learning_rate": 0.001,
  "hidden_size": 128,
  "device": "cpu",
  "notes": "Training on REAL Bitcoin puzzle keys (not zeros)"
}
```

## Created
2025-12-01 14:50:24

## Status
- [ ] Training started
- [ ] Training completed
- [ ] Results analyzed

## Training Command

```bash
cd /home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence

python3 scripts/train_transformer.py \
  --run-dir runs/run_005_real_data \
  --epochs 100 \
  --batch-size 8 \
  --lr 0.001 \
  --hidden-size 128 \
  --device cpu
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
