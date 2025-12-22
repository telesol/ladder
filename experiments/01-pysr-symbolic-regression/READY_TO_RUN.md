# ✅ Experiment 01: PySR - READY TO RUN

## Status: All Scripts Created, Dependencies Installed

### What's Ready

✅ **Experiment folder structure** - Clean, organized, isolated
✅ **Training data** - 82 valid puzzles extracted and copied
✅ **Dependencies installed** - PySR, numpy, pandas in your `.venv`
✅ **Scripts created:**
   - `scripts/prepare_data.py` - Data splitting (Phase 2)
   - `scripts/train_single_lane.py` - Single lane training (Phase 3.1)
✅ **Documentation:**
   - `TODO_PYSR.md` - Detailed 7-phase plan
   - `RUN_EXPERIMENT.md` - Quick start guide
   - `ML_STRATEGY.md` - Strategy overview

### Run It Now

```bash
# 1. Activate your virtual environment
cd /home/solo/LadderV3/kh-assist
source .venv/bin/activate  # Or wherever your venv is

# 2. Go to experiment folder
cd experiments/01-pysr-symbolic-regression

# 3. Prepare data (5 seconds)
python3 scripts/prepare_data.py

# 4. Train first lane (30-60 minutes for proof of concept)
python3 scripts/train_single_lane.py --lane 0 --iterations 1000

# Fast test (5-10 min, less accurate):
# python3 scripts/train_single_lane.py --lane 0 --iterations 100
```

### What to Expect

**Phase 2 (Data Prep):**
- Splits data into train/val/test
- Creates per-lane datasets
- Time: 5 seconds

**Phase 3.1 (Single Lane PoC):**
- Discovers symbolic formula for Lane 0
- Uses PySR to search equation space
- Target: `f(x) = A^4 * x + C (mod 256)`
- Time: 30-60 minutes (1000 iterations)
- Output: `results/lane_00_formula.txt`, `results/lane_00_results.json`

**Success Criteria:**
- Accuracy ≥95% (ideally 100%)
- Clean formula discovered (e.g., `245*x^4 + 12`)

### After Successful PoC

If Lane 0 achieves >95% accuracy:

**Option 1: Train remaining lanes individually**
```bash
for i in {1..15}; do
    python3 scripts/train_single_lane.py --lane $i --iterations 1000
done
```
Time: 8-12 hours total (can run overnight)

**Option 2: Create batch training script**
(We can create `scripts/train_all_lanes.py` for parallel execution)

### Files Created

```
experiments/01-pysr-symbolic-regression/
├── data/
│   ├── puzzles_full.json         ✅ 82 puzzles
│   ├── lane_matrix.npy           ✅ 82×32 array
│   ├── half_blocks.json          ✅ Half-block data
│   └── pattern_analysis.json     ✅ Initial stats
├── scripts/
│   ├── prepare_data.py           ✅ Data splitting
│   └── train_single_lane.py      ✅ Single lane training
├── results/                      📁 Empty (outputs go here)
├── models/                       📁 Empty (checkpoints)
├── TODO_PYSR.md                  ✅ 7-phase detailed plan
├── RUN_EXPERIMENT.md             ✅ Quick start guide
├── ML_STRATEGY.md                ✅ Strategy document
└── READY_TO_RUN.md               ✅ This file
```

### Troubleshooting

**PySR not found:**
```bash
source .venv/bin/activate
pip install pysr
python3 -c "import pysr; pysr.install()"  # Installs Julia backend
```

**Low accuracy (<95%):**
- Try more iterations: `--iterations 2000`
- Try different lane: `--lane 15`
- Check if data is correct: `cat data/puzzles_full.json | python3 -m json.tool | head -50`

**Julia installation takes long:**
- First run installs Julia (10-15 min)
- This is normal, only happens once
- Let it complete

### Timeline

| Task | Time | Can Run Unattended? |
|------|------|---------------------|
| Data prep | 5 sec | No |
| Lane 0 (PoC) | 30-60 min | ✅ Yes |
| All 16 lanes | 8-12 hours | ✅ Yes (overnight) |
| Validation | 30 min | No (interactive) |

### Next Session Tasks

After training completes, we'll need to:

1. **Extract coefficients** - Parse A and C_0 from formulas
2. **Validate** - Test forward/reverse calculation
3. **Export calibration JSON** - Make it compatible with existing tools
4. **Integration test** - Run with `verify_affine.py`

But for now, just run Phases 2 and 3.1 to verify the approach works! 🚀

---

## Commands Summary

```bash
# Setup (one-time)
cd /home/solo/LadderV3/kh-assist
source .venv/bin/activate
cd experiments/01-pysr-symbolic-regression

# Run experiment
python3 scripts/prepare_data.py
python3 scripts/train_single_lane.py --lane 0 --iterations 1000

# Check results
cat results/lane_00_formula.txt
cat results/lane_00_results.json | python3 -m json.tool
```

**Everything is ready to go!** 🎯

Just activate your venv and run the commands above.
