# Experiment 02: Transformer Sequence Learning

**Status:** 🔜 Ready to start
**Goal:** Train transformer to learn Bitcoin puzzle sequence pattern
**Comparison:** Neural network vs symbolic regression (PySR)

---

## Overview

This experiment trains an attention-based transformer model to learn the sequence-to-sequence mapping of Bitcoin puzzle keys. The goal is to compare neural network approach with the **proven PySR formula** from Experiment 01.

### Research Questions

1. **Can transformers discover the polynomial structure?**
   - PySR found: `X_{k+1}(ℓ) = X_k(ℓ)^n (mod 256)`
   - Will transformer learn the same pattern implicitly?

2. **Lane independence**
   - PySR shows 16 independent lanes
   - Will attention weights reflect this independence?

3. **Generalization**
   - PySR: 100% accuracy on validation/test
   - Can transformer match this performance?

4. **Interpretability**
   - PySR: Explicit formula
   - Transformer: Black box (can we extract patterns?)

---

## Dataset

Using the **same data** as PySR experiment:
- **Training:** Puzzles 1-60 (59 transitions)
- **Validation:** Puzzles 61-70 (9 transitions)
- **Test:** Bridge rows 75, 80, 85, 90, 95 (multi-step calculation)

### Data Format

**Input/Output pairs:**
- Input: Current puzzle key (first 16 bytes)
- Output: Next puzzle key (first 16 bytes)

**Representation:**
- Each byte: 0-255 (uint8)
- 16 bytes per puzzle = 16 features
- Can treat as sequence (16 positions) or parallel (16 lanes)

---

## Model Architecture

### Transformer Configuration

```python
{
  "model_type": "transformer",
  "d_model": 64,           # Embedding dimension
  "nhead": 8,              # Number of attention heads
  "num_encoder_layers": 4,
  "num_decoder_layers": 4,
  "dim_feedforward": 256,
  "dropout": 0.1,
  "max_sequence_length": 16
}
```

### Alternative: Seq2Seq with Attention

```python
{
  "model_type": "seq2seq",
  "encoder_hidden": 128,
  "decoder_hidden": 128,
  "num_layers": 2,
  "attention": True
}
```

---

## Training Strategy

### Phase 1: Basic Training
- Train on puzzles 1-60
- Validate on puzzles 61-70
- Goal: Learn next-step calculation

### Phase 2: Multi-Step Calculation
- Test on bridge rows (5-step calculation)
- Compare with PySR formula

### Phase 3: Analysis
- Extract attention weights
- Analyze lane independence
- Compare with PySR exponents

---

## Success Metrics

### Quantitative
1. **Training accuracy**: % of correct byte calculations
2. **Validation accuracy**: Generalization to unseen puzzles
3. **Test accuracy**: Multi-step calculation (bridge rows)
4. **Comparison with PySR**: Gap analysis

### Qualitative
1. **Attention patterns**: Do they show lane independence?
2. **Error analysis**: Where does transformer fail vs PySR?
3. **Interpretability**: Can we extract rules from learned weights?

---

## Expected Outcomes

### Best Case
- **100% accuracy** (matches PySR)
- **Attention weights** show lane independence
- **Implicit discovery** of polynomial pattern

### Likely Case
- **High accuracy** (~95%+) but not perfect
- **Some lane independence** in attention
- **Black box** - hard to extract explicit formula

### Worst Case
- **Overfits** to training data
- **Poor generalization** to validation/test
- **No interpretable pattern** emerges

---

## Files

### Scripts
- `scripts/prepare_transformer_data.py` - Convert PySR data to transformer format
- `scripts/train_transformer.py` - Main training loop
- `scripts/evaluate_transformer.py` - Evaluation on test sets
- `scripts/analyze_attention.py` - Attention weight visualization
- `scripts/compare_with_pysr.py` - Side-by-side comparison

### Results
- `results/training_history.json` - Loss/accuracy over epochs
- `results/validation_results.json` - Performance on validation set
- `results/test_results.json` - Performance on bridge rows
- `results/attention_weights.npy` - Saved attention patterns
- `results/comparison_with_pysr.json` - PySR vs Transformer metrics

### Models
- `models/transformer_checkpoint.pth` - Best model checkpoint
- `models/config.json` - Model configuration

---

## Quick Start

```bash
cd /home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence

# 1. Prepare data (links to PySR data)
python scripts/prepare_transformer_data.py

# 2. Train transformer
python scripts/train_transformer.py \
  --epochs 100 \
  --batch-size 8 \
  --lr 0.001 \
  --device cuda  # or cpu

# 3. Evaluate
python scripts/evaluate_transformer.py \
  --checkpoint models/transformer_checkpoint.pth

# 4. Compare with PySR
python scripts/compare_with_pysr.py
```

---

## Hardware Requirements

### GPU (Recommended)
- RTX 5000 (16GB VRAM) - available
- Training time: ~15-30 minutes

### CPU (Fallback)
- Training time: ~2-4 hours
- May need smaller batch size

---

## Dependencies

```bash
# PyTorch with GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Additional
pip install numpy pandas matplotlib seaborn scikit-learn
```

---

## Comparison with PySR

| Aspect | PySR (Symbolic) | Transformer (Neural) |
|--------|-----------------|----------------------|
| **Approach** | Evolutionary search | Gradient descent |
| **Output** | Explicit formula | Learned weights |
| **Interpretability** | High (math formula) | Low (black box) |
| **Training time** | 6.2 hours (CPU) | ~30 min (GPU) |
| **Accuracy** | 100% (proven) | TBD |
| **Generalization** | Perfect (validated) | TBD |
| **Insight** | Polynomial pattern | Attention patterns |

---

## Next Steps After Training

1. **If transformer matches PySR (100%):**
   - Analyze attention weights
   - Try to extract polynomial rule
   - Publish comparison study

2. **If transformer underperforms:**
   - Analyze failure modes
   - Try different architectures (LSTM, etc.)
   - Understand why symbolic > neural

3. **If transformer outperforms (unlikely):**
   - Investigate what PySR missed
   - Re-verify PySR formula
   - Hybrid approach?

---

**Created:** 2025-11-30
**Status:** Ready to begin training
**Baseline:** PySR formula with 100% proven accuracy
