# Experiments Status - 2025-11-27

## Setup Complete ✅

**Created:** 3 organized experiment folders with isolated data copies
**Primary:** Experiment 01 - PySR Symbolic Regression
**Backups:** Experiments 02 (Transformer) and 03 (LSTM)

## Experiment 01: PySR Symbolic Regression

### Status: ⏳ READY TO EXECUTE

### Structure
```
experiments/01-pysr-symbolic-regression/
├── data/                          ✅ 88KB, 4 files
│   ├── puzzles_full.json          (82 puzzles)
│   ├── lane_matrix.npy            (82×32 array)
│   ├── half_blocks.json
│   └── pattern_analysis.json
├── scripts/                       ⏳ To be created
├── results/                       ⏳ Empty (for outputs)
├── models/                        ⏳ Empty (for checkpoints)
├── TODO_PYSR.md                   ✅ Complete execution plan
└── ML_STRATEGY.md                 ✅ Strategy document
```

### TODO Plan Summary

**Phase 1:** Environment Setup (15 min)
- Install PySR, numpy, pandas, scikit-learn
- Verify Julia backend

**Phase 2:** Data Preparation (5 min)
- Split: Train (60), Val (10), Test (5)

**Phase 3:** Symbolic Regression Training
- 3.1: Single lane PoC (1 hour)
- 3.2: All 16 lanes (8-12 hours) ⚠️ LONG RUNNING

**Phase 4:** Coefficient Extraction (5 min)
- Parse formulas to get A and C_0

**Phase 5:** Validation (20 min)
- Forward, reverse, bridge testing

**Phase 6:** Export & Integration (10 min)
- Create calibration JSON
- Test with existing tools

**Phase 7:** Documentation (25 min)
- Generate report and visualizations

**Total Time:** ~10-14 hours (mostly Phase 3.2)

### Expected Outputs

1. `results/discovered_coefficients.json` - A and C_0 for all lanes
2. `results/lane_XX_formula.txt` - 16 symbolic formulas
3. `results/ladder_calib_pysr.json` - Calibration file
4. `results/PYSR_REPORT.md` - Full analysis report
5. `results/figures/` - Visualizations

### Success Criteria

✅ **Minimum:** 95%+ forward accuracy
✅ **Target:** 100% forward + reverse accuracy
✅ **Integration:** Works with existing verify_affine.py

---

## Experiment 02: Transformer Sequence Model

### Status: 🔒 STANDBY (Backup approach)

**Structure:**
```
experiments/02-transformer-sequence/
├── data/           ✅ 88KB (copy ready)
├── scripts/        ⏳ Not created yet
├── results/        ⏳ Empty
└── models/         ⏳ Empty
```

**Use if:** PySR doesn't converge or for validation

---

## Experiment 03: LSTM Recurrent Model

### Status: 🔒 STANDBY (Backup approach)

**Structure:**
```
experiments/03-lstm-recurrent/
├── data/           ✅ 88KB (copy ready)
├── scripts/        ⏳ Not created yet
├── results/        ⏳ Empty
└── models/         ⏳ Empty
```

**Use if:** Need faster/lighter alternative to transformers

---

## Next Actions

### Immediate (Ready Now)
1. Review `experiments/01-pysr-symbolic-regression/TODO_PYSR.md`
2. Navigate to experiment folder
3. Install dependencies: `pip install pysr numpy pandas scikit-learn matplotlib`
4. Create training scripts (Phase 2-3)
5. Execute experiment

### Execution Command
```bash
cd /home/solo/LadderV3/kh-assist/experiments/01-pysr-symbolic-regression

# Option 1: Manual step-by-step (recommended for first time)
# Follow TODO_PYSR.md phases 1-7

# Option 2: Automated (once scripts are created)
./run_experiment.sh
```

---

## Why This Approach?

**vs Manual Ladder Decoding:**
- ✅ Automatic formula discovery
- ✅ No format confusion issues
- ✅ Built-in validation
- ✅ Reproducible results
- ✅ Can generalize to missing puzzles

**vs Other ML Models:**
- ✅ Symbolic regression outputs exact math formula
- ✅ Interpretable A and C_0 coefficients
- ✅ Low VRAM usage (~2GB vs 6-8GB for transformers)
- ✅ Proven for scientific equation discovery

---

## Resources

**Hardware:** RTX 5000 (16GB VRAM) - More than sufficient
**Time:** ~10-14 hours for full discovery
**Monitoring:** Can run overnight with checkpointing

**Key Files:**
- Execution plan: `01-pysr-symbolic-regression/TODO_PYSR.md`
- Strategy: `01-pysr-symbolic-regression/ML_STRATEGY.md`
- Overview: `experiments/README.md`

---

## Auto-Sync Status

✅ All files backing up to NAS automatically
- Backup location: `C:\temp\ZBook-Ladder-Backup-20251127_121742\`
- NAS target: `\\Boyz-NAS\Public\home\projects\ZBook-Ladder`
- Sync running: Background process 16d95c

---

**Ready to start Experiment 01!** 🚀
