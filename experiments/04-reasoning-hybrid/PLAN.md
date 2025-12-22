# Experiment 04: Reasoning-Hybrid System

**Vision**: AI as the Brain, PySR as the Calculator

## Executive Summary

**Goal**: Train a neural network to REASON about Bitcoin puzzle sequences and orchestrate the proven PySR formula to generate solutions.

**Key Insight**: Instead of trying to learn the pattern from scratch (which failed in experiment 02), we train the AI to:
1. **Understand** the problem structure
2. **Decide** which operations to apply (choose exponents)
3. **Execute** via PySR calculator (proven 100% accurate)
4. **Validate** the results make sense

**Success Criteria**:
- ✅ AI learns to calculate correct exponents for each lane
- ✅ AI validates outputs with >95% confidence
- ✅ System generates puzzles 71-95 matching known solutions
- ✅ System can extrapolate to puzzles 96-160 with high confidence

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    REASONING BRAIN (Neural Network)           │
│                                                               │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │   Sequence     │  │   Exponent     │  │   Validator    │ │
│  │   Encoder      │→ │   Calculator    │→ │   Network      │ │
│  │ (Transformer)  │  │ (Classifier)   │  │  (Scoring)     │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
│         ↓                    ↓                    ↓          │
│    Understanding        Decision              Confidence     │
└──────────────────────────────────────────────────────────────┘
                              ↓
                    Which exponents to use?
                              ↓
┌──────────────────────────────────────────────────────────────┐
│               PYSR CALCULATOR (Symbolic Formula)              │
│                                                               │
│         X_{k+1}(ℓ) = X_k(ℓ)^n mod 256                       │
│                                                               │
│         Exponents: [3,2,3,2,2,3,0,2,2,3,3,2,2,2,2,3]        │
└──────────────────────────────────────────────────────────────┘
                              ↓
                        Next puzzle bytes
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    VALIDATION LOOP                            │
│                                                               │
│  ‣ Does output match expected format?                        │
│  ‣ Are byte distributions reasonable?                        │
│  ‣ Does progression make sense?                              │
│  ‣ Confidence score > threshold?                             │
└──────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Planning (Current)

### 1.1 Architecture Design

**Component A: Sequence Encoder**
- Input: Last N puzzles (e.g., 5-10 puzzles)
- Architecture: Transformer encoder or LSTM
- Output: Context vector (understanding of sequence)
- Purpose: Learn patterns like "lane independence", "polynomial progression"

**Component B: Exponent Calculator**
- Input: Context vector from encoder
- Architecture: 16 independent classifiers (one per lane)
- Output: Exponent per lane (3 classes: {0, 2, 3})
- Purpose: Decide which polynomial to apply per lane

**Component C: Validator Network**
- Input: Calculated puzzle + context
- Architecture: Feedforward network
- Output: Confidence score [0.0, 1.0]
- Purpose: Sanity check - does output look reasonable?

**Component D: PySR Interface**
- Input: Current puzzle bytes + 16 exponents
- Implementation: Pure Python (no ML)
- Output: Next puzzle bytes
- Purpose: Execute calculation with 100% accuracy

### 1.2 Training Strategy

**Dataset Creation**:
```
Known data:
  - Puzzles 1-95 (from CSV)
  - Ground truth exponents: [3,2,3,2,2,3,0,2,2,3,3,2,2,2,2,3]

Synthetic data (optional):
  - Generate 100K transitions using PySR formula
  - Add noise/variations to test robustness
```

**Training Phases**:

**Phase A: Exponent Learning (Supervised)**
- Train on puzzles 1-70
- Ground truth: Known exponents [3,2,3,2,2,3,0,2,2,3,3,2,2,2,2,3]
- Loss: Cross-entropy (classification)
- Goal: AI learns to calculate correct exponents

**Phase B: Validation Learning**
- Train validator on correct vs incorrect outputs
- Positive examples: Real puzzle transitions
- Negative examples: Random bytes, wrong exponents
- Loss: Binary cross-entropy
- Goal: AI learns what "looks right"

**Phase C: Reasoning Integration**
- End-to-end training
- AI predicts exponents → PySR calculates → AI validates
- Loss: Combined (exponent accuracy + validation confidence)
- Goal: AI learns full reasoning pipeline

### 1.3 Evaluation Metrics

**Metric 1: Exponent Calculation Accuracy**
- Per-lane accuracy (16 lanes)
- Overall accuracy (all 16 correct?)
- Confusion matrix: Which exponents get confused?

**Metric 2: Validation Reliability**
- True positive rate: Correct outputs → high confidence
- False positive rate: Incorrect outputs → low confidence
- AUC-ROC curve

**Metric 3: Extrapolation Performance**
- Test on puzzles 71-95 (held-out known data)
- Generate puzzles 96-160 (unknown data)
- Cross-validate with PySR baseline

---

## Phase 2: Prototype (Next Step)

### 2.1 Minimal Viable Prototype

**Scope**: Simplest possible version to test concept

**Components**:
1. **Simple exponent calculator**: Single MLP per lane
2. **PySR calculator**: Python function (already have this)
3. **Basic validator**: Threshold-based confidence

**Prototype Goals**:
- ✅ Can AI learn exponents from puzzles 1-70?
- ✅ Does PySR interface work correctly?
- ✅ Can system generate puzzle 71 correctly?

**Time Estimate**: 2-4 hours
**Success Threshold**: >80% exponent accuracy on validation set

### 2.2 Prototype Implementation Plan

**File Structure**:
```
experiments/04-reasoning-hybrid/
├── PLAN.md (this file)
├── prototype/
│   ├── reasoning_brain.py       # Neural network components
│   ├── pysr_calculator.py       # PySR interface
│   ├── validator.py             # Validation logic
│   └── train_prototype.py       # Training script
├── data/
│   ├── prepare_data.py          # Load puzzles 1-95 from CSV
│   └── synthetic_data.py        # Generate additional examples
├── scripts/
│   ├── test_prototype.py        # Test on puzzles 71-95
│   └── generate_puzzles.py      # Generate 96-160
└── results/
    └── prototype_results.json
```

**Step 1: PySR Calculator (30 min)**
```python
def pysr_calculate(input_bytes: bytes, exponents: List[int]) -> bytes:
    """
    Apply PySR formula: X_{k+1}(ℓ) = X_k(ℓ)^n mod 256

    Args:
        input_bytes: 16 bytes (current puzzle)
        exponents: 16 integers (one per lane)

    Returns:
        16 bytes (next puzzle)
    """
    output = []
    for lane in range(16):
        x = input_bytes[lane]
        n = exponents[lane]
        output.append((x ** n) % 256)
    return bytes(output)
```

**Step 2: Simple Exponent Calculator (1 hour)**
```python
class SimpleExponentPredictor(nn.Module):
    def __init__(self):
        super().__init__()
        # 16 independent networks (one per lane)
        self.lane_predictors = nn.ModuleList([
            nn.Sequential(
                nn.Linear(16, 64),  # Input: all 16 bytes
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 3)    # Output: {0, 2, 3}
            )
            for _ in range(16)
        ])

    def forward(self, puzzle_bytes):
        # puzzle_bytes: (batch, 16) normalized to [0, 1]
        calculations = []
        for lane in range(16):
            logits = self.lane_predictors[lane](puzzle_bytes)
            calculations.append(logits)
        # Stack: (batch, 16, 3)
        return torch.stack(calculations, dim=1)
```

**Step 3: Training Loop (30 min)**
```python
# Load data
puzzles = load_puzzles_from_csv(1, 70)  # 70 samples
ground_truth_exponents = [3,2,3,2,2,3,0,2,2,3,3,2,2,2,2,3]

# Train exponent calculator
for epoch in range(100):
    for puzzle in puzzles:
        # Calculate exponents
        predicted_exponents = model(puzzle)

        # Compare to ground truth
        loss = cross_entropy(predicted_exponents, ground_truth_exponents)

        # Update
        loss.backward()
        optimizer.step()
```

**Step 4: Test Generation (30 min)**
```python
# Test: Can we generate puzzle 71?
current = puzzles[70]  # Starting point

# AI predicts exponents
predicted_exponents = model(current).argmax(dim=-1)  # (16,)

# Map {0,1,2} → {0,2,3}
exponent_map = [0, 2, 3]
actual_exponents = [exponent_map[e] for e in predicted_exponents]

# PySR calculates
next_puzzle = pysr_calculate(current, actual_exponents)

# Validate
ground_truth_71 = load_puzzle_from_csv(71)
accuracy = (next_puzzle == ground_truth_71).sum() / 16

print(f"Accuracy: {accuracy*100:.1f}%")
```

### 2.3 Prototype Success Criteria

**Must Have** (Go/No-Go Decision):
- ✅ Exponent calculation: >80% accuracy per lane
- ✅ PySR interface: 100% correct calculation (sanity check)
- ✅ Puzzle 71 generation: >50% byte accuracy

**Nice to Have** (Bonus):
- ✅ Exponent calculation: >95% accuracy
- ✅ Puzzle 71 generation: 100% accuracy
- ✅ Puzzles 71-75 generation: >80% accuracy

**Failure Criteria** (Pivot Required):
- ❌ Exponent calculation: <50% accuracy → AI can't learn pattern
- ❌ PySR calculation errors → Formula implementation bug
- ❌ No learning after 100 epochs → Architecture wrong

---

## Phase 3: Validation (If Prototype Succeeds)

### 3.1 Full System Development

**Enhanced Components**:
1. **Sequence Encoder**: Transformer (not just single puzzle)
2. **Validator Network**: Proper confidence scoring
3. **Synthetic Data**: Generate 100K examples
4. **Training Pipeline**: Multi-phase training

### 3.2 Comprehensive Testing

**Test Set 1**: Puzzles 71-95 (known solutions)
- Generate using AI+PySR
- Compare byte-for-byte with ground truth
- Target: >95% accuracy

**Test Set 2**: Puzzles 96-160 (unknown)
- Generate using AI+PySR
- Cross-validate with PySR baseline
- Check confidence scores

### 3.3 Comparison with Baselines

| Approach | Accuracy (71-95) | Interpretability | Reasoning |
|----------|------------------|------------------|-----------|
| Pure PySR | 100% | ✅ | ❌ |
| Pure Neural Net (Exp 02) | 0% | ❌ | ❌ |
| Reasoning Hybrid (Exp 04) | **Target: >95%** | ✅ | ✅ |

---

## Phase 4: Production (If Validated)

### 4.1 Generate Puzzles 96-160

**Pipeline**:
```python
# Start from puzzle 95
current = load_puzzle(95)
generated_puzzles = []

for puzzle_num in range(96, 161):
    # AI reasons about exponents
    exponents = ai_brain.predict_exponents(current)
    confidence = ai_brain.validate(current, exponents)

    # PySR calculates
    next_puzzle = pysr_calculate(current, exponents)

    # Validate result
    if confidence > 0.95:
        generated_puzzles.append({
            'puzzle_num': puzzle_num,
            'bytes': next_puzzle,
            'exponents': exponents,
            'confidence': confidence
        })
        current = next_puzzle
    else:
        # Flag for manual review
        logger.warning(f"Low confidence ({confidence}) at puzzle {puzzle_num}")
```

### 4.2 Verification & Documentation

- Cross-check all generated puzzles
- Document confidence scores
- Compare with any known solutions (if available)
- Create proof document

---

## Risk Assessment

### High Risk
❌ **AI can't learn exponents**: Only 70 training samples might not be enough
- Mitigation: Generate synthetic data using PySR

### Medium Risk
⚠️ **Overfitting**: AI memorizes instead of understanding
- Mitigation: Regularization, dropout, validation set

### Low Risk
✅ **PySR calculation errors**: Formula is proven correct
✅ **Implementation bugs**: Can test against known solutions

---

## Resource Requirements

### Compute
- **Prototype**: CPU only (few minutes training)
- **Full system**: GPU helpful but not required (small model)
- **Data generation**: CPU (PySR formula is fast)

### Data
- **Known**: Puzzles 1-95 from CSV (already have)
- **Synthetic**: Can generate unlimited via PySR
- **Storage**: Minimal (<1 MB for all data)

### Time Estimate
- **Prototype**: 2-4 hours
- **Validation**: 4-6 hours (if prototype works)
- **Production**: 2-4 hours (if validation succeeds)
- **Total**: 8-14 hours (assuming success at each stage)

---

## Decision Points

### After Prototype (2-4 hours):
**Question**: Did AI learn to calculate exponents?

- ✅ **YES (>80% accuracy)** → Continue to validation
- ❌ **NO (<50% accuracy)** → Pivot or abandon
- ⚠️ **MAYBE (50-80%)** → Try synthetic data, then decide

### After Validation (8-10 hours total):
**Question**: Does system work on held-out puzzles 71-95?

- ✅ **YES (>95% accuracy)** → Deploy to generate 96-160
- ❌ **NO (<80% accuracy)** → Analyze failure, possibly abandon
- ⚠️ **MAYBE (80-95%)** → Improve validator, retry

---

## Success Metrics Summary

| Phase | Metric | Threshold | Status |
|-------|--------|-----------|--------|
| Prototype | Exponent accuracy | >80% | 🔜 TBD |
| Prototype | Puzzle 71 accuracy | >50% | 🔜 TBD |
| Validation | Puzzles 71-95 accuracy | >95% | 🔜 TBD |
| Production | Confidence scores | >0.95 avg | 🔜 TBD |

---

## Next Steps

1. **Create prototype directory structure** ✅ (Now)
2. **Implement PySR calculator interface** (30 min)
3. **Build simple exponent calculator** (1 hour)
4. **Train on puzzles 1-70** (30 min)
5. **Test on puzzle 71** (30 min)
6. **Evaluate results** (30 min)
7. **Go/No-Go decision** (Based on results)

**Total time to decision point**: ~3-4 hours

---

**Ready to start prototype?** 🚀
