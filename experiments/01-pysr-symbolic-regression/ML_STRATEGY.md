# ML Strategy for Bitcoin Puzzle Ladder Discovery

## Overview

Train a local AI model on RTX 5000 (16GB VRAM) to discover the affine recurrence pattern in Bitcoin puzzle keys, rather than manually reverse-engineering it.

## Data Available

- **82 valid puzzles** with complete 64-hex keys
  - Puzzles 1-70 (continuous sequence)
  - Bridge rows: 75, 80, 85, 90, ..., 130 (every 5th puzzle)
- **Data files created:**
  - `ml-training/data/puzzles_full.json` - Complete puzzle metadata
  - `ml-training/data/half_blocks.json` - First/second 16-byte halves
  - `ml-training/data/lane_matrix.npy` - 82×32 numpy array (bytes)
  - `ml-training/data/pattern_analysis.json` - Initial statistical analysis

## Problem Formulation

### What We Want to Discover

The ladder follows an **affine recurrence relation** in GF(2^8):

```
X_{k+1}(ℓ) = A_ℓ^4 * X_k(ℓ) + Γ_ℓ * C_0(ℓ) (mod 256)
```

Where:
- `X_k(ℓ)` = byte at lane ℓ for puzzle k
- `A_ℓ` = multiplication factor for lane ℓ (16 values, one per lane)
- `C_0(ℓ)` = drift constant for lane ℓ (16 values)
- Γ_ℓ = cumulative polynomial coefficient

### ML Task

**Supervised Sequence Calculation:**
- Input: Previous N puzzle keys (as byte sequences)
- Output: Next puzzle key (32 bytes)
- Goal: Learn the recurrence coefficients A and C_0

## Recommended Models for RTX 5000 (16GB VRAM)

### Option 1: Transformer-based Sequence Model (RECOMMENDED)
**Model:** Custom Transformer or fine-tuned GPT-2 Small
- **Architecture:** Encoder-decoder or autoregressive transformer
- **Input:** Tokenized byte sequences (vocabulary size = 256)
- **Advantages:**
  - Excellent at capturing sequential patterns
  - Can model long-range dependencies
  - Pre-trained weights available
- **VRAM Usage:** ~4-6 GB for training
- **Framework:** PyTorch + HuggingFace Transformers

### Option 2: LSTM/GRU Recurrent Network
**Model:** Stacked LSTM with attention
- **Architecture:** 2-3 layer LSTM, 256-512 hidden units
- **Advantages:**
  - Proven for sequence-to-sequence tasks
  - Lower memory footprint (~2-3 GB)
  - Faster training on smaller datasets
- **VRAM Usage:** ~2-4 GB for training
- **Framework:** PyTorch or TensorFlow

### Option 3: Graph Neural Network (GNN)
**Model:** GCN or GAT for lane interactions
- **Architecture:** Model each lane as a node, learn inter-lane relationships
- **Advantages:**
  - Can discover lane coupling patterns
  - Interpretable learned coefficients
- **VRAM Usage:** ~3-5 GB
- **Framework:** PyTorch Geometric

### Option 4: Symbolic Regression (Hybrid AI)
**Model:** Neural-guided symbolic search
- **Tools:**
  - PySR (Python Symbolic Regression)
  - AI Feynman
  - GPLearn with neural pre-filtering
- **Advantages:**
  - **Directly outputs mathematical formula**
  - Interpretable results (A and C_0 coefficients)
  - Can discover exact recurrence relation
- **VRAM Usage:** Minimal (~1-2 GB)
- **Best for:** Discovering the exact mathematical structure

## Recommended Approach: Hybrid Strategy

### Phase 1: Symbolic Regression (Days 1-2)
1. Use **PySR** to discover symbolic patterns in lane transformations
2. Search space: `f(x) = a*x^k + c` where k ∈ {1,2,3,4,5}
3. Constraints: coefficients mod 256
4. **Expected Output:** Exact A and C_0 values per lane

### Phase 2: Transformer Validation (Days 3-4)
1. Train small transformer to calculate next puzzle
2. Validate discovered formula against transformer calculations
3. Use transformer for confidence scoring

### Phase 3: Pattern Refinement (Day 5)
1. Test discovered formula on all 82 puzzles
2. Compute forward/reverse verification scores
3. Refine coefficients if needed

## Training Data Strategy

### Data Splits
- **Training:** Puzzles 1-60 (60 samples)
- **Validation:** Puzzles 61-70 (10 samples)
- **Test:** Bridge rows 75, 80, 85, 90, 95 (5 samples)

### Data Augmentation
1. **Byte permutations:** Treat each lane independently
2. **Sliding windows:** Create sequences of length 5, 10, 15
3. **Synthetic interpolation:** Generate intermediate values

### Features
- **Raw bytes:** Direct 256-dim categorical
- **Differences:** Δ between consecutive puzzles
- **Cumulative sums:** Running totals per lane
- **Frequency encoding:** Lane-specific patterns

## Implementation Steps

### Step 1: Install Dependencies
```bash
pip install torch transformers datasets
pip install pysr scikit-learn matplotlib
pip install torch-geometric  # if using GNN
```

### Step 2: Run Symbolic Regression
```python
from pysr import PySRRegressor

# Configure for modular arithmetic
model = PySRRegressor(
    niterations=1000,
    binary_operators=["+", "*"],
    unary_operators=["square", "cube"],
    constraints={'pow': (1, 5)},
    model_selection="best"
)

# Fit per-lane models
for lane in range(16):
    X_train = puzzles[:-1, lane].reshape(-1, 1)  # X_k
    y_train = puzzles[1:, lane]                   # X_{k+1}
    model.fit(X_train, y_train)
    print(f"Lane {lane}: {model.sympy()}")
```

### Step 3: Train Transformer (if needed)
```python
from transformers import GPT2Config, GPT2LMHeadModel

config = GPT2Config(
    vocab_size=256,      # Byte vocabulary
    n_positions=32,      # Sequence length
    n_embd=256,
    n_layer=6,
    n_head=8
)

model = GPT2LMHeadModel(config)
# Training loop...
```

### Step 4: Validate and Export
```python
# Test on validation set
calculations = model.calculate(X_val)
accuracy = np.mean(calculations == y_val)

# Export discovered coefficients
coefficients = {
    'A': [model_lane_0.coef_, ...],
    'C0': [drift_lane_0, ...],
    'accuracy': accuracy
}
json.dump(coefficients, open('discovered_ladder.json', 'w'))
```

## Expected Outcomes

### Success Criteria
1. **Forward calculation:** 95%+ accuracy on validation set
2. **Reverse verification:** Can reconstruct previous puzzles
3. **Coefficient extraction:** Clean A and C_0 values (preferably integers mod 256)

### Timeline
- **Days 1-2:** Symbolic regression discovers base patterns
- **Days 3-4:** Transformer training and validation
- **Day 5:** Testing and coefficient extraction
- **Total:** ~1 week for complete discovery

## Hardware Utilization (RTX 5000)

### Training Configuration
- **Batch size:** 16-32 (for transformer)
- **Mixed precision:** FP16 to save VRAM
- **Gradient checkpointing:** If needed for larger models
- **Expected VRAM usage:** 6-8 GB peak
- **Remaining VRAM:** Available for batch size tuning

### Optimization Tips
1. Use **PyTorch 2.0 compile()** for 2x speedup
2. Enable **TensorFloat-32** on RTX 5000
3. Profile with `torch.profiler` to identify bottlenecks

## Next Steps

1. ✅ **Data extraction complete** (82 puzzles)
2. ⏳ **Install symbolic regression tools** (PySR)
3. ⏳ **Create training scripts**
4. ⏳ **Run discovery pipeline**
5. ⏳ **Validate and export coefficients**

## Files to Create

1. `train_symbolic_regression.py` - PySR-based discovery
2. `train_transformer.py` - Transformer sequence model
3. `validate_ladder.py` - Test discovered patterns
4. `export_coefficients.py` - Convert to usable format
5. `visualize_patterns.py` - Plot learned relationships

---

**Bottom Line:** Using symbolic regression (PySR) is likely the fastest path to discovering the exact mathematical formula, while transformers provide validation. The RTX 5000 is more than powerful enough for this task.
