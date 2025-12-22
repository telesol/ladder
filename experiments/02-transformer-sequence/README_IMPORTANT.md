# ⚠️ IMPORTANT: READ THIS FIRST

## This is NOT an LLM Training

### What This Is NOT:
- ❌ **NOT** qwen2.5-coder:7b
- ❌ **NOT** any language model
- ❌ **NOT** Ollama-based
- ❌ **NOT** transformer (in the NLP sense)
- ❌ **NOT** using pretrained models

### What This Actually Is:
- ✅ **Custom PyTorch neural network**
- ✅ **SimpleLanePredictor** architecture
- ✅ **Trained from scratch** on Bitcoin puzzle data
- ✅ **Supervised learning**: byte → byte calculation
- ✅ **16 independent networks** (one per lane)

---

## Quick Facts

**Model Type:** Custom feedforward neural network
**Framework:** PyTorch
**Task:** Learn f(x) = x^n mod 256 implicitly
**Training:** From random initialization (no pretrained weights)
**Data:** 59 puzzle pairs (16 bytes → 16 bytes)
**Goal:** Match PySR's 100% proven accuracy

---

## Architecture Overview

```
SimpleLanePredictor:
  ├── Lane 0 Network: 1 → 128 → 128 → 256
  ├── Lane 1 Network: 1 → 128 → 128 → 256
  ├── ...
  └── Lane 15 Network: 1 → 128 → 128 → 256

Total: 16 independent neural networks
Parameters: ~330,000 (very small!)
Training time: 2-3 hours (CPU)
```

---

## Why "Transformer" in Folder Name?

**Historical naming** - originally planned to use transformer architecture (attention mechanism).

**Actual implementation** - simplified to independent lane networks after PySR proved lanes are independent.

**More accurate name** would be: "neural-network-sequence" or "lane-calculator"

But we kept "transformer-sequence" to maintain experiment numbering.

---

## Installation

```bash
# 1. Install dependencies
./install_deps.sh

# 2. Verify installation
python3 -c "import torch; print(f'PyTorch: {torch.__version__}')"

# 3. Run training
./run_experiment.sh baseline 100 128
```

---

## Documentation

- **INSTALL.md** - Installation guide
- **MODEL_ARCHITECTURE.md** - Detailed architecture (must read!)
- **QUICKSTART.md** - How to start training
- **TRAINING_PLAN.md** - Training strategy
- **requirements.txt** - Python dependencies

---

## Key Differences: This vs PySR

| Aspect | PySR | This (Neural) |
|--------|------|---------------|
| Method | Symbolic regression | Gradient descent |
| Output | Math formula | Learned weights |
| Accuracy | 100% (proven) | TBD (goal: 95-100%) |
| Interpretability | Perfect | Low |
| Training | 6.2 hours | 2-3 hours |

---

## Expected Training Output

```
Epoch   1/100 | Train Acc: 15.23% | Val Acc: 14.56%
Epoch  10/100 | Train Acc: 68.45% | Val Acc: 65.23%
Epoch  50/100 | Train Acc: 94.32% | Val Acc: 91.87%
Epoch 100/100 | Train Acc: 99.12% | Val Acc: 97.34%

Best validation accuracy: 97.34%
PySR baseline: 100.00%
Gap: 2.66%
```

---

## If You Have Questions

**Q: Is this training a language model?**
A: No. This is a custom neural network for byte calculation.

**Q: Do I need Ollama?**
A: No. Only PyTorch and NumPy.

**Q: Is this related to qwen2.5-coder?**
A: No. Completely separate. Different task.

**Q: How big is the model?**
A: ~330K parameters (~1.3MB saved model). Very small!

**Q: Why not use a pretrained model?**
A: This is a specific mathematical task. Pretrained LLMs won't help.

---

**Read MODEL_ARCHITECTURE.md for full details!**
