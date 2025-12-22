# Training Run 004: baseline

## Configuration

```json
{
  "epochs": 100,
  "batch_size": 8,
  "learning_rate": 0.001,
  "hidden_size": 128,
  "device": "cpu",
  "notes": ""
}
```

## Created
2025-12-01 14:04:12

## Status
- [ ] Training started
- [ ] Training completed
- [ ] Results analyzed

## Training Command

```bash
cd /home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence

python3 scripts/train_transformer.py \
  --run-dir runs/run_004_baseline \
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
