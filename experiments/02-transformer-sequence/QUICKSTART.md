# Quick Start Guide - Transformer Training

## ✅ Everything Is Ready!

**Current Status:**
- ✅ Data prepared (59 training pairs, 9 validation pairs)
- ✅ Model architecture created (SimpleLanePredictor - 16 independent networks)
- ✅ Training scripts ready
- ✅ Run management system set up
- ✅ First run created: `run_001_baseline`

---

## 🚀 Start Training Now (3 Options)

### **Option 1: Full Automated Run (EASIEST)**

```bash
cd /home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence

./run_experiment.sh baseline 100 128
```

**What this does:**
1. Creates run directory (or uses existing run_001_baseline)
2. Runs quick test (10 epochs, ~5 min)
3. Asks if you want to continue
4. Runs full training (100 epochs, ~2-3 hours)
5. Saves all results

---

### **Option 2: Manual Step-by-Step**

```bash
cd /home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence

# Run 001 is already created, just train it
python3 scripts/train_transformer.py --run-dir run_001_baseline
```

This uses the config from `runs/run_001_baseline/config.json` automatically.

---

### **Option 3: Quick Test First (5 minutes)**

```bash
cd /home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence

# Quick 10-epoch test
python3 scripts/train_transformer.py \
  --run-dir run_001_baseline \
  --epochs 10
```

Then if it looks good:

```bash
# Full 100-epoch training
python3 scripts/train_transformer.py \
  --run-dir run_001_baseline \
  --epochs 100
```

---

## 📊 What to Expect

### Quick Test (10 epochs, ~5 min)
```
Epoch   1/10 | Train Loss: 2.3456 Acc: 12.34% | Val Loss: 2.4567 Acc: 11.23%
Epoch  10/10 | Train Loss: 0.9876 Acc: 65.43% | Val Loss: 1.0234 Acc: 62.15%

✅ Training complete!
   Best validation accuracy: 62.15% (epoch 10)

📊 Comparison with PySR:
   PySR (symbolic regression): 100.00% (PROVEN)
   Transformer (neural network): 62.15%
   ⚠️  Good progress, but not perfect. Gap: 37.85%
```

**If you see 50-70% after 10 epochs** → Good! Continue to 100 epochs

---

### Full Training (100 epochs, ~2-3 hours)
```
Epoch   1/100 | Train Loss: 2.3456 Acc: 12.34% | Val Loss: 2.4567 Acc: 11.23%
Epoch  10/100 | Train Loss: 0.9876 Acc: 65.43% | Val Loss: 1.0234 Acc: 62.15%
Epoch  20/100 | Train Loss: 0.4321 Acc: 85.67% | Val Loss: 0.5432 Acc: 82.34%
Epoch  30/100 | Train Loss: 0.2109 Acc: 93.45% | Val Loss: 0.3210 Acc: 91.23%
...
Epoch 100/100 | Train Loss: 0.0123 Acc: 99.87% | Val Loss: 0.0234 Acc: 98.76%

✅ Training complete!
   Total time: 7823.4s (130.4 min)
   Best validation accuracy: 98.76% (epoch 92)

📊 Comparison with PySR:
   PySR (symbolic regression): 100.00% (PROVEN)
   Transformer (neural network): 98.76%
   ⚠️  Good, but not perfect. Gap: 1.24%
```

---

## 📁 Where Results Are Saved

After training, check:

```bash
cd runs/run_001_baseline

# Configuration
cat config.json

# Final results summary
cat logs/final_results.json

# Full training history (loss/accuracy per epoch)
cat logs/training_history.json

# Saved model
ls -lh checkpoints/best_model.pth
```

---

## 🎯 Success Criteria

| Validation Accuracy | Result |
|---------------------|--------|
| **100%** | 🎉 Perfect! Neural network learned exact pattern |
| **95-99%** | ✅ Very good! Almost matches PySR |
| **85-94%** | ⚠️ Good, but gap exists |
| **<85%** | ❌ Needs investigation |

---

## 🔄 Running More Experiments

### Create Run 002 (larger network)
```bash
./run_experiment.sh larger_hidden 100 256
```

### Create Run 003 (more epochs)
```bash
./run_experiment.sh more_epochs 200 128
```

### Compare results
```bash
# View all run results
for run in runs/run_*/logs/final_results.json; do
  echo ""
  echo "$(dirname $(dirname $run)):"
  cat $run | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'  Val acc: {d[\"best_val_acc\"]:.2f}%  |  Gap: {d[\"gap\"]:.2f}%')"
done
```

---

## ⚡ Ready to Start?

**Recommended command:**

```bash
cd /home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence
./run_experiment.sh baseline 100 128
```

This will:
1. ✅ Use existing run_001_baseline configuration
2. ✅ Quick test first (10 epochs, ask to continue)
3. ✅ Full training if approved (100 epochs)
4. ✅ Save all results

**Estimated time:**
- Quick test: ~5 minutes
- Full training: ~2-3 hours (CPU)

---

## 📝 Monitoring Progress

**In another terminal:**
```bash
# Watch training progress
tail -f runs/run_001_baseline/logs/training.log

# Check latest results
cat runs/run_001_baseline/logs/final_results.json | python3 -m json.tool
```

---

**🚀 Ready when you are!**
