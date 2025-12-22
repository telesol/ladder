# Quick Start Guide - PySR Experiment

## Prerequisites

✅ You already have dependencies installed in `.venv`
- pysr
- numpy
- pandas
- scikit-learn
- matplotlib

## Execution Steps

### 1. Activate Virtual Environment

```bash
# Navigate to project root
cd /home/solo/LadderV3/kh-assist

# Activate your venv (adjust path if different)
source .venv/bin/activate
# OR if venv is elsewhere:
# source /path/to/your/venv/bin/activate
```

### 2. Navigate to Experiment Folder

```bash
cd experiments/01-pysr-symbolic-regression
```

### 3. Prepare Data (Phase 2)

```bash
python3 scripts/prepare_data.py
```

**Expected output:**
```
============================================================
Phase 2: Data Preparation for PySR
============================================================
📂 Loading data...
✅ Loaded 82 puzzles
   Lane matrix shape: (82, 32)

📊 Data splits created:
   Training:   (60, 32) - Puzzles 1-60
   Validation: (10, 32) - Puzzles 61-70
   Test:       (5, 32) - Bridge rows 75-95

💾 Saved splits to data/
   - train_matrix.npy
   - val_matrix.npy
   - test_matrix.npy

🔬 Creating per-lane datasets...
✅ Created 16 lane datasets in data/lanes/
   Each lane: X shape (59, 1), y shape (59,)
```

**Time:** ~5 seconds

### 4. Train Single Lane (Phase 3.1 - Proof of Concept)

```bash
# Train lane 0 with 1000 iterations (~30-60 minutes)
python3 scripts/train_single_lane.py --lane 0 --iterations 1000
```

**For faster testing** (5-10 minutes, less accurate):
```bash
python3 scripts/train_single_lane.py --lane 0 --iterations 100
```

**Expected output:**
```
============================================================
Training Lane 0 - Symbolic Regression
============================================================
📊 Data loaded:
   X shape: (59, 1) (previous values)
   y shape: (59,) (next values)

🔬 Configuring PySR...
   Iterations: 1000
   Populations: 15
   Operators: +, *, square, cube
   Target formula form: a*x^k + c (mod 256)

🚀 Starting symbolic regression...
   This may take 30-60 minutes for 1000 iterations
   Progress will be shown below:

[PySR will show progress bars and discovered equations]

✅ Training complete!

🏆 Best equation:
   Complexity: 5
   Loss: 0.000123
   Equation: 245*x^4 + 12  (example)

📊 Training Performance:
   Exact matches: 58/59 (98.31%)
   Mean modular loss: 0.0234

✅ Good accuracy! Formula likely captures the pattern.
```

**Outputs:**
- `results/lane_00_formula.txt`
- `results/lane_00_results.json`

### 5. Check Results

```bash
# View formula
cat results/lane_00_formula.txt

# View JSON results
cat results/lane_00_results.json | python3 -m json.tool
```

### 6. If Successful - Train All Lanes

**IMPORTANT:** This will take 8-12 hours (can run overnight)

```bash
# Create the all-lanes training script (to be added)
python3 scripts/train_all_lanes.py

# OR train lanes individually in parallel/sequentially
for i in {0..15}; do
    python3 scripts/train_single_lane.py --lane $i --iterations 1000
done
```

---

## Troubleshooting

### If PySR is not found:

```bash
# Activate venv first
source .venv/bin/activate

# Verify installation
python3 -c "import pysr; print('PySR OK')"

# If not installed
pip install pysr
python3 -c "import pysr; pysr.install()"
```

### If Julia errors occur:

PySR uses Julia backend. On first run, it will install Julia automatically.
This may take 10-15 minutes.

```bash
# Manual Julia setup (if needed)
python3 -c "import pysr; pysr.install()"
```

### If accuracy is low (<95%):

1. **Increase iterations:**
   ```bash
   python3 scripts/train_single_lane.py --lane 0 --iterations 2000
   ```

2. **Try different lane:**
   Some lanes may have simpler patterns
   ```bash
   python3 scripts/train_single_lane.py --lane 15 --iterations 1000
   ```

3. **Check data:**
   ```bash
   python3 -c "
   import numpy as np
   X = np.load('data/lanes/lane_00_X.npy')
   y = np.load('data/lanes/lane_00_y.npy')
   print('X:', X[:5].flatten())
   print('y:', y[:5])
   "
   ```

---

## Expected Timeline

| Phase | Task | Time | Notes |
|-------|------|------|-------|
| 2 | Data preparation | 5 sec | One-time setup |
| 3.1 | Single lane (PoC) | 30-60 min | Verify approach works |
| 3.2 | All 16 lanes | 8-12 hours | Can run overnight |
| 4-7 | Analysis & export | 30 min | After training completes |

---

## Next Steps After Training

Once all 16 lanes are trained:

1. **Extract coefficients** - Parse A and C_0 from formulas
2. **Validate** - Test forward/reverse accuracy
3. **Export** - Create calibration JSON
4. **Integrate** - Test with existing verify_affine.py

See `TODO_PYSR.md` for detailed Phase 4-7 instructions.

---

## Quick Reference

```bash
# Full workflow
cd /home/solo/LadderV3/kh-assist
source .venv/bin/activate
cd experiments/01-pysr-symbolic-regression

# Phase 2
python3 scripts/prepare_data.py

# Phase 3.1 (PoC)
python3 scripts/train_single_lane.py --lane 0 --iterations 1000

# Phase 3.2 (All lanes - after PoC success)
# [Script to be created or manual loop]

# Check results
ls -lh results/
cat results/lane_00_formula.txt
```

---

**Ready to discover the ladder formula automatically!** 🚀
