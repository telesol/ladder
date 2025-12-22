# Drift Formula Discovery - Training Log

**Session Date**: 2025-12-02
**Goal**: Discover the mathematical formula for drift values using PySR
**Status**: 🔄 IN PROGRESS (48% complete)

---

## The Real Challenge: Discovering the Drift Formula

### What We Learned

The ladder formula is:
```
X_{k+1}[lane] = (A[lane]^4 * X_k[lane] + drift[k→k+1][lane]) mod 256
```

Where:
- **A coefficients**: KNOWN (16 values, one per lane)
- **drift values**: UNKNOWN formula - this is what we need to discover!

The calibration file `ladder_calib_ultimate.json` contains 1,296 drift values (81 transitions × 16 lanes), but these are **lookup table data**, not a formula.

**The breakthrough**: If we can discover `drift = f(puzzle_k, lane, X_k)`, we can generate ANY future puzzle!

---

## Training Progress

### Phase 1: Understanding the Problem ✅ COMPLETE

**Key Findings**:
1. Previous Experiment 01 claimed "100% accuracy" but only tested on zero-padding bytes
2. The real pattern is NOT simple per-byte polynomials (x², x³)
3. Drift values change for every puzzle transition
4. Low correlation: drift vs puzzle_k (0.138), drift vs X_k (0.068)

### Phase 2: Data Preparation ✅ COMPLETE

**Training Data**:
- **Source**: `ladder_calib_ultimate.json` (known drift values)
- **Samples**: 1,104 training examples
- **Puzzles**: 1-69 (69 transitions)
- **Lanes**: 0-15 (16 lanes per puzzle)
- **Features**: `puzzle_k` (1-69), `lane` (0-15), `X_k` (0-255)
- **Target**: `drift` (0-255)

**Lane 0 Example Data**:
```
puzzle_k | X_k | drift | Result (X_k + drift mod 256)
---------|-----|-------|------------------------------
    1    |  1  |   2   |   3
    2    |  3  |   4   |   7
    3    |  7  |   1   |   8
    4    |  8  |  13   |  21
    5    | 21  |  28   |  49
```

### Phase 3: PySR Training 🔄 IN PROGRESS

**Started**: 2025-12-02 (current session)
**Configuration**:
- Iterations: 100
- Binary operators: +, *, -, /
- Unary operators: square, cube
- Populations: 30
- Population size: 100
- Max formula size: 30
- Timeout: 30 minutes

**Current Progress** (at 48%):
```
Training Progress: 48/100 iterations complete
ETA: 1:39 remaining
Evaluations/sec: ~68,600
```

**Hall of Fame** (Best Discovered Equations):

| Complexity | Loss  | Equation |
|------------|-------|----------|
| 1 | 3,090 | `y = X_k` (baseline) |
| 3 | 2,813 | `y = X_k * 0.76504` |
| 7 | 1,741 | `y = X_k * (124.13 / (X_k + lane))` ✨ |
| 9 | 1,727 | `y = (X_k / (X_k + lane + 1.1954)) * 127.69` |
| 29 | **1,622** | `y = ((X_k + X_k) * 64.944) / (...complex...)` |

**Key Observations**:
1. ✅ **Loss decreasing**: 3,090 → 1,622 (48% reduction!)
2. ✅ **AI discovering lane interaction**: Best formulas include `(X_k + lane)`
3. ✅ **Complexity increasing**: More complex formulas = better fit
4. ✅ **puzzle_k appearing**: Some equations use puzzle_k in denominators

**Best Simple Formula So Far** (Complexity 7, Loss 1,741):
```python
drift ≈ X_k * (124.13 / (X_k + lane))
```

This is interpretable! It shows:
- drift scales with X_k
- drift inversely related to (X_k + lane)
- As lane increases, drift decreases

---

## Next Steps (After Training Completes)

### Step 1: Extract Best Formula
- Wait for training to reach 100% (~2 more minutes)
- Analyze final Hall of Fame
- Select best formula (balance accuracy vs complexity)

### Step 2: Validate on Training Set
- Apply discovered formula to puzzles 1-69
- Calculate drift calculations
- Apply full ladder formula: `X_{k+1} = (A^4 * X_k + drift_predicted) mod 256`
- Target: >95% byte-level accuracy

### Step 3: Test on Puzzle 70
- Generate puzzle 70 using discovered drift formula
- Compare to known puzzle 70 in CSV
- This tests **extrapolation** (one step beyond training)

### Step 4: Generate Puzzles 71-95
- Iteratively apply formula:
  - Start from puzzle 70 (known)
  - Generate 71 using drift formula
  - Generate 72 from 71, 73 from 72, etc.
- **Critical test**: Can we reach puzzle 95 accurately?

### Step 5: Cryptographic Validation
For each generated puzzle:
1. Construct full 32-byte private key
2. Derive public key (ECDSA secp256k1)
3. Hash (SHA256 + RIPEMD160)
4. Encode (Base58Check) → Bitcoin address
5. Compare to CSV addresses

**Success Criteria**: >80% Bitcoin address matches on puzzles 71-95

---

## Success Metrics

### Training Phase (Current)
- ✅ PySR running without errors
- ✅ Loss decreasing (3,090 → 1,622)
- ✅ Formula includes all features (puzzle_k, lane, X_k)
- ⏳ Final loss < 1,000 (pending)
- ⏳ Training accuracy > 80% (pending)

### Validation Phase (Next)
- 🔜 Training set (1-69): >95% byte accuracy
- 🔜 Puzzle 70 calculation: >90% byte accuracy
- 🔜 Formula is interpretable (human-readable)

### Extrapolation Phase (Future)
- 🔜 Puzzles 71-95 generated successfully
- 🔜 Bitcoin address matches: >80%
- 🔜 Cryptographic proof: Keys are valid

---

## Why This Matters

**If we discover the drift formula**:
1. ✅ Generate ANY future puzzle (71-160)
2. ✅ No need for calibration lookup tables
3. ✅ Prove pattern is mathematical, not random
4. ✅ Validate with cryptographic proof (Bitcoin addresses)

**If we DON'T discover it**:
1. Pattern may be cryptographically random
2. Need to use calibration data directly (known puzzles only)
3. Cannot calculate beyond puzzle 70 reliably
4. May need neural network instead of symbolic regression

---

## Current Status Summary

**What's Working**:
- ✅ PySR training running smoothly (48% complete)
- ✅ Loss decreasing significantly (48% reduction)
- ✅ Formulas discovering lane + X_k interactions
- ✅ puzzle_k appearing in equations

**What's In Progress**:
- 🔄 PySR evolution (48/100 iterations)
- 🔄 Formula refinement (current best: Loss 1,622)

**What's Pending**:
- 🔜 Training completion (~2 minutes)
- 🔜 Final formula extraction
- 🔜 Validation on training set
- 🔜 Extrapolation test (puzzles 71-95)
- 🔜 Cryptographic validation (Bitcoin addresses)

---

## Technical Details

### Why Drift Formula Discovery is Hard

1. **Non-stationary pattern**: Drift changes every puzzle
2. **Low correlation**: No simple linear relationship
3. **High complexity**: Likely requires non-linear terms
4. **Modular arithmetic**: Results mod 256 (byte overflow)
5. **Multi-byte dependencies**: Lanes may interact via carries

### PySR Advantages

1. **Symbolic regression**: Discovers actual mathematical formulas
2. **Evolutionary search**: Explores vast formula space
3. **Interpretability**: Formulas are human-readable
4. **No black box**: Can analyze and verify discovered patterns

### Formula Evaluation Criteria

**Good formula characteristics**:
- Low loss (<1,000)
- High accuracy (>80%)
- Reasonable complexity (<20 operators)
- Includes all features (puzzle_k, lane, X_k)
- Interpretable (makes mathematical sense)

**Red flags**:
- Very high complexity (>30 operators) - likely overfitting
- Zero use of puzzle_k - missing temporal pattern
- Perfect accuracy - suspicious, check for data leakage

---

## Files Created

```
experiments/05-ai-learns-ladder/
├── train_drift_formula.py         # 🔄 Currently running
├── training_drift_formula.log     # 🔄 Live training output
├── DRIFT_TRAINING_LOG.md          # 📝 This file
│
├── crypto_validator.py            # ✅ Bitcoin address derivation
├── prepare_training_data.py       # ✅ Per-lane data extraction
├── train_lane0.py                 # ⚠️ Failed (wrong approach)
├── TRAINING_LOG.md                # 📝 Original training log
│
├── data/                          # ✅ Per-lane training data
│   ├── lane_00_train.csv
│   ├── ...
│   └── lane_15_train.csv
│
├── models/                        # 🔜 Will contain trained models
│   └── drift_formula.pkl          # 🔜 After training completes
│
└── requirements.txt               # ✅ Dependencies
```

---

## Last Updated

**Time**: 2025-12-02 (current session)
**Training Progress**: 48%
**Status**: ACTIVELY DISCOVERING DRIFT FORMULA 🧠

**Next Update**: When training completes (ETA ~2 minutes)
