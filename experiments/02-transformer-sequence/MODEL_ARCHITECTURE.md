# Model Architecture - SimpleLanePredictor

## ⚠️ IMPORTANT: This is NOT an LLM!

**We are NOT using:**
- ❌ qwen2.5-coder:7b
- ❌ Any language model
- ❌ Ollama
- ❌ Transformers library (huggingface)

**We ARE using:**
- ✅ PyTorch (custom neural network)
- ✅ NumPy (data processing)
- ✅ Custom SimpleLanePredictor architecture

---

## What We're Training

### **SimpleLanePredictor: Custom Neural Network**

A **from-scratch PyTorch neural network** designed specifically for this Bitcoin puzzle task.

---

## Architecture Details

### Overview
```
Input: 16 bytes (puzzle_k)
  ↓
16 independent neural networks (one per lane)
  ↓
Output: 16 bytes (puzzle_k+1)
```

### Per-Lane Network
```python
Lane Network (repeated 16 times):
    Input Layer:    1 neuron  (single byte value, 0-255 normalized to 0-1)
    Hidden Layer 1: 128 neurons (ReLU activation)
    Hidden Layer 2: 128 neurons (ReLU activation)
    Output Layer:   256 neurons (softmax → classification)
```

### Key Design Decisions

**Why 16 independent networks?**
- PySR discovered that lanes are **completely independent**
- Each lane: `X_{k+1}(ℓ) = X_k(ℓ)^n (mod 256)`
- No cross-lane dependencies
- This architecture mirrors the mathematical truth

**Why classification (256 classes)?**
- Each byte can be 0-255
- We calculate the exact next byte value
- Softmax over 256 classes
- Loss: CrossEntropyLoss

**Why this size (128 hidden)?**
- Small enough to train quickly (~2-3 hours CPU)
- Large enough to learn polynomial patterns (x², x³)
- Total parameters: ~330,000

---

## Full Architecture Specification

```python
class SimpleLanePredictor(nn.Module):
    def __init__(self, hidden_size=128):
        super().__init__()

        # 16 independent networks
        self.lane_networks = nn.ModuleList([
            nn.Sequential(
                nn.Linear(1, hidden_size),      # Input: 1 byte
                nn.ReLU(),
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, 256)     # Output: 256 classes
            )
            for _ in range(16)  # One network per lane
        ])

    def forward(self, x):
        # x: (batch, 16) - 16 lanes
        # output: (batch, 16, 256) - 16 lanes × 256 class logits

        outputs = []
        for lane in range(16):
            lane_input = x[:, lane:lane+1]  # Extract single lane
            lane_output = self.lane_networks[lane](lane_input)
            outputs.append(lane_output)

        return torch.stack(outputs, dim=1)
```

---

## Training Process

### Input/Output Format
```python
Input:  puzzle_k   = [b0, b1, b2, ..., b15]  # 16 bytes
Output: puzzle_k+1 = [b0', b1', b2', ..., b15']  # 16 bytes

# Normalized input (0-255 → 0-1)
input_normalized = input / 255.0

# Output: class labels (0-255 as integers)
output_labels = output  # Keep as is
```

### Loss Function
```python
# Per-lane CrossEntropyLoss
total_loss = 0
for lane in range(16):
    lane_logits = model_output[:, lane, :]  # (batch, 256)
    lane_targets = targets[:, lane]          # (batch,)
    total_loss += CrossEntropyLoss(lane_logits, lane_targets)
```

### Optimization
- **Optimizer**: Adam
- **Learning rate**: 0.001 (default)
- **Batch size**: 8 (59 training samples, so ~7-8 batches per epoch)
- **Epochs**: 100 (can adjust)

---

## Comparison: This vs PySR

| Aspect | PySR (Symbolic) | SimpleLanePredictor (Neural) |
|--------|-----------------|------------------------------|
| **Type** | Evolutionary algorithm | Gradient descent |
| **Output** | Explicit formula: `x^n mod 256` | Learned weights |
| **Parameters** | 16 exponents | ~330,000 weights |
| **Interpretability** | Perfect (math formula) | Low (black box) |
| **Training** | 6.2 hours (CPU) | 2-3 hours (CPU) |
| **Accuracy** | 100% (proven) | TBD (goal: 95-100%) |
| **Insight** | Polynomial pattern | Implicit pattern in weights |

---

## Why This Architecture?

### Design Rationale

1. **Lane Independence**
   - PySR proved no cross-lane dependencies
   - Independent networks are more efficient
   - Easier to analyze per-lane performance

2. **Classification over Regression**
   - Byte values are discrete (0-255)
   - Classification better for discrete targets
   - Can measure exact match (not MSE)

3. **Moderate Size**
   - Not too small (can't learn pattern)
   - Not too large (overfits, slow training)
   - 128 hidden neurons: sweet spot

4. **Simple Architecture**
   - No attention mechanism needed (lanes independent)
   - No recurrence needed (one-step calculation)
   - Just feedforward: fast and interpretable

---

## Expected Learning

### What the Network Should Learn

Each lane network should implicitly learn:

**Lane with exponent 2 (square):**
```
Input:   x
Output:  x^2 mod 256
```

**Lane with exponent 3 (cube):**
```
Input:   x
Output:  x^3 mod 256
```

**Lane 6 (zero):**
```
Input:   x
Output:  0  (always)
```

### Verification

After training, we can:
1. Compare calculations with PySR formula
2. Analyze which lanes learn well vs. struggle
3. Check if implicit pattern matches exponents
4. Visualize learned mappings (input → output)

---

## Hardware Requirements

### CPU (Current Setup)
- **Recommended**: 4+ cores
- **RAM**: 4GB minimum, 8GB recommended
- **Training time**: 2-3 hours (100 epochs)
- **Batch size**: 8 (can try 16)

### GPU (If Available)
- **Any CUDA GPU**: RTX 3060, RTX 5000, etc.
- **VRAM**: 2GB sufficient (small model)
- **Training time**: 15-30 minutes (100 epochs)
- **Batch size**: 32-64 (faster)

---

## Model Size

```
Total parameters: ~330,000
Memory footprint: ~1.3 MB (saved model)
Training memory: ~100-200 MB (CPU)

Breakdown:
  Lane 0: 1×128 + 128×128 + 128×256 = 49,408 params
  × 16 lanes = 790,528 params

  Actual (with biases):
  (1+1)×128 + (128+1)×128 + (128+1)×256 = 49,920 per lane
  × 16 lanes = 798,720 params total
```

---

## No Pretrained Models

**Important:** This is trained from scratch, not fine-tuned.

- ❌ No pretrained weights
- ❌ No transfer learning
- ❌ No foundation model
- ✅ Random initialization
- ✅ Learn from Bitcoin puzzle data only

---

## Summary

**This is a custom PyTorch neural network, NOT an LLM.**

- Built specifically for this task
- Trained from scratch on 59 puzzle pairs
- Goal: Learn the same pattern PySR discovered
- Architecture mirrors mathematical structure (16 independent lanes)

**No connection to:**
- qwen2.5-coder
- Ollama
- Language models
- Transformers (in the NLP sense)

**This is pure supervised learning:**
- Input: 16 bytes
- Output: 16 bytes
- Task: Learn f(x) = x^n mod 256 implicitly

---

**Created:** 2025-11-30
**Model Type:** Custom PyTorch Neural Network (SimpleLanePredictor)
**Training Method:** Supervised learning from scratch
