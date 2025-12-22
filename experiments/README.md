# Experiments: ML-Based Ladder Discovery

This directory contains organized machine learning experiments to automatically discover the Bitcoin puzzle ladder recurrence formula.

## Experiment Structure

Each experiment has its own isolated folder with:
```
XX-experiment-name/
├── data/              # Clean copy of training data
├── scripts/           # Training and analysis scripts
├── results/           # Discovered formulas, metrics, visualizations
├── models/            # Saved model checkpoints
├── TODO_*.md          # Detailed execution plan
└── ML_STRATEGY.md     # (if applicable)
```

## Available Experiments

### 01 - PySR Symbolic Regression (PRIMARY)
**Status:** ⏳ Ready to execute
**Goal:** Use symbolic regression to discover exact mathematical formula
**Approach:** PySR (Python Symbolic Regression) with Julia backend
**Expected Duration:** 10-14 hours
**Expected Output:** Exact `A` and `C_0` coefficients for all 16 lanes

**Why This First:**
- Outputs interpretable mathematical formula
- Low VRAM usage (~1-2 GB)
- Discovers exact coefficients, not just calculations
- Proven for discovering physical laws and patterns

**See:** `01-pysr-symbolic-regression/TODO_PYSR.md`

---

### 02 - Transformer Sequence Model (BACKUP)
**Status:** 🔒 Ready for future use
**Goal:** Sequence-to-sequence calculation using transformers
**Approach:** Fine-tuned GPT-2 Small or custom transformer
**Expected Duration:** 1-2 days
**Expected Output:** Byte-level calculations, learned representations

**Use Case:**
- If PySR doesn't converge
- For validation of symbolic results
- For confidence scoring

---

### 03 - LSTM Recurrent Model (BACKUP)
**Status:** 🔒 Ready for future use
**Goal:** Recurrent sequence calculation
**Approach:** Stacked LSTM with attention
**Expected Duration:** 1 day
**Expected Output:** Next-puzzle calculations

**Use Case:**
- Lighter alternative to transformers
- Faster training iterations
- Good for time-series patterns

---

## Execution Order

1. **Start with Experiment 01 (PySR)**
   - Most likely to discover exact formula
   - Lowest resource requirements
   - Interpretable results

2. **If Experiment 01 succeeds:**
   - Use results immediately
   - Skip other experiments unless validation needed

3. **If Experiment 01 fails:**
   - Analyze failure mode
   - Try Experiment 02 or 03
   - Or refine PySR constraints

## Hardware Requirements

**Available:** RTX 5000 (16GB VRAM)

| Experiment | VRAM Usage | CPU Usage | Training Time |
|------------|------------|-----------|---------------|
| 01 - PySR | 1-2 GB | High | 10-14 hours |
| 02 - Transformer | 6-8 GB | Medium | 1-2 days |
| 03 - LSTM | 2-4 GB | Medium | 1 day |

**Note:** All experiments can run concurrently if desired (total VRAM < 16GB)

## Data Summary

**Source:** `data/btc_puzzle_1_160_full.csv`
**Valid puzzles extracted:** 82
- Puzzles 1-70 (continuous sequence)
- Bridge rows: 75, 80, 85, 90, ..., 130

**Training split:**
- Train: Puzzles 1-60 (60 samples)
- Validation: Puzzles 61-70 (10 samples)
- Test: Bridge rows 75, 80, 85, 90, 95 (5 samples)

## Success Criteria

✅ **Minimum Success:**
- Forward accuracy: ≥95% on validation set
- Discovered pattern generalizes to test set

✅ **Full Success:**
- Forward accuracy: 100% (exact byte matches)
- Reverse accuracy: 100%
- Clean A and C_0 coefficients extracted
- Compatible with existing verification tools

## Quick Start

```bash
# Navigate to primary experiment
cd experiments/01-pysr-symbolic-regression

# Read execution plan
cat TODO_PYSR.md

# Install dependencies
pip install pysr numpy pandas scikit-learn matplotlib

# Run experiment
./run_experiment.sh  # (to be created)
```

## Comparison: Manual vs ML Approach

| Aspect | Manual Decoding | ML Discovery |
|--------|-----------------|--------------|
| **Time** | Weeks/months | 1-2 weeks |
| **Error prone** | High (format issues) | Low (automated) |
| **Interpretability** | High | High (symbolic) |
| **Validation** | Manual | Automated |
| **Generalization** | Unknown | Testable |
| **Fun factor** | 😅 Tedious | 🚀 Exciting |

## Next Steps

1. Review `01-pysr-symbolic-regression/TODO_PYSR.md`
2. Install dependencies
3. Execute Phase 1-3 (data prep + training)
4. Validate results
5. Export coefficients
6. Integrate with existing tools

**Ready to discover the ladder automatically!** 🎯
