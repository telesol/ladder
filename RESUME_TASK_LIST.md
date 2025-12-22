# Task List for Resumption - Drift Formula Discovery

**Date Created**: 2025-12-22
**Status**: Ready for Next Session
**Purpose**: Systematic plan to discover the remaining 30% of drift formula

---

## Session Context (READ THIS FIRST!)

### What We've Proven (70%)

✅ **Rule 1**: `drift[k][lane] = 0` if `k < lane × 8` (100% accurate, 764 values)
✅ **Rule 2**: `drift[k][lane] = 1` if `k == lane × 8, lane>0` (100% accurate, 8 lanes)
❌ **Rule 3**: `drift[k][lane] = ???` if `k > lane × 8` (UNKNOWN, 340 values)

### Current Data Quality

✅ Correct data file: `drift_data_CORRECT_BYTE_ORDER.json`
✅ Verified 1,104 drift values (69 transitions × 16 lanes)
✅ No wrong CSV, no missing DB, no byte order errors
✅ Hard proof documented: `HARD_PROOF_VALIDATION_2025-12-22.md`

### Philosophy

**We are scientists, NOT treasure hunters**
**We compute, NOT brute force**
**We prove, NOT predict**

See: `PROJECT_PHILOSOPHY.md`

---

## TASK 1: Review LLM Analysis Results ⏳ IN PROGRESS

**Status**: Nemotron completed, GPT-OSS may still be running

**Actions**:
```bash
cd /home/solo/LadderV3/kh-assist

# 1. Read Nemotron findings
cat llm_tasks/results/nemotron_drift_evolution_analysis.txt

# 2. Check if GPT-OSS finished
ps aux | grep gpt-oss

# 3. Read GPT-OSS findings (if done)
cat llm_tasks/results/gptoss_cross_lane_analysis.txt

# 4. Extract key patterns discovered
```

**Expected Outputs**:
- Pattern hypotheses from Nemotron
- Cross-lane relationships from GPT-OSS
- Formulas to test in PySR

**Deliverable**: Summary document consolidating LLM findings

---

## TASK 2: Validate Data for PySR Training ⏸️ READY

**Critical**: Ensure we don't repeat past mistakes!

**Verification Checklist**:

```bash
# 1. Verify drift data file
python3 << 'EOF'
import json
data = json.load(open('drift_data_CORRECT_BYTE_ORDER.json'))
print(f"✓ Total transitions: {len(data['transitions'])}")
print(f"✓ Total drift values: {data['total_drift_values']}")
print(f"✓ Byte order: {data['byte_order']}")
assert len(data['transitions']) == 69
assert data['total_drift_values'] == 1104
print("✅ DATA VALIDATED")
EOF

# 2. Extract evolution values ONLY (k > lane×8)
python3 << 'EOF'
import json
data = json.load(open('drift_data_CORRECT_BYTE_ORDER.json'))

evolution_count = 0
for trans in data['transitions']:
    k = trans['from_puzzle']
    for lane in range(16):
        activation_k = lane * 8 if lane > 0 else 1
        if k > activation_k:  # Evolution phase
            evolution_count += 1

print(f"✓ Evolution values: {evolution_count}")
print("Expected: ~340 (30% of 1104)")
EOF

# 3. Verify exponents
python3 << 'EOF'
EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]
print(f"✓ Exponents: {EXPONENTS}")
print(f"✓ Lane 6 exponent: {EXPONENTS[6]} (should be 0)")
EOF
```

**Deliverable**: Validated dataset ready for PySR

---

## TASK 3: Prepare PySR Training Script 📝 TODO

**Location**: `experiments/01-pysr-symbolic-regression/train_drift_evolution.py`

**Requirements**:

1. **Use ONLY evolution values** (exclude k < lane×8 and k == lane×8)
2. **Apply discovered rules** (Rules 1 & 2) to filter data
3. **Include correct features**:
   - k (transition index)
   - lane (lane number)
   - steps_since_activation (k - lane×8)
   - exponent (from EXPONENTS array)
   - ❓ X_k[lane] value (if state-dependent)

4. **Separate by lane** (optional - may find simpler formulas)

**Script Template**:
```python
import json
import pandas as pd
from pysr import PySRRegressor

# Load CORRECT drift data
with open('../../drift_data_CORRECT_BYTE_ORDER.json') as f:
    data = json.load(f)

EXPONENTS = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

# Extract evolution values ONLY
features = []
targets = []

for trans in data['transitions']:
    k = trans['from_puzzle']

    for lane in range(16):
        activation_k = lane * 8 if lane > 0 else 1

        # EVOLUTION PHASE ONLY
        if k > activation_k:
            drift = trans['drifts'][lane]

            features.append({
                'k': k,
                'lane': lane,
                'steps_since_activation': k - activation_k,
                'exponent': EXPONENTS[lane]
            })
            targets.append(drift)

# Split train/test (puzzles 1-60 train, 61-70 test)
# ... rest of PySR training ...
```

**Deliverable**: Tested training script

---

## TASK 4: Run PySR Symbolic Regression 🔬 TODO

**Execution Plan**:

### Option A: Single Unified Model
```bash
cd experiments/01-pysr-symbolic-regression
python3 train_drift_evolution.py --mode unified --timeout 7200
```
**Pros**: May find universal formula
**Cons**: Harder to find (more complex)

### Option B: Per-Lane Models (RECOMMENDED)
```bash
# Train 16 separate models (can parallelize!)
for lane in {0..15}; do
    python3 train_drift_evolution.py --lane $lane --timeout 1800 &
done
wait
```
**Pros**: Simpler formulas per lane
**Cons**: 16 separate formulas to manage

### Option C: By Exponent Groups
```bash
# Exponent=2 lanes
python3 train_drift_evolution.py --exponent 2 --timeout 3600

# Exponent=3 lanes
python3 train_drift_evolution.py --exponent 3 --timeout 3600

# Lane 6 (exponent=0) separately
python3 train_drift_evolution.py --lane 6 --timeout 1800
```
**Pros**: Groups similar lanes
**Cons**: Still multiple models

**Time Estimate**: 2-8 hours depending on approach

**Deliverable**: PySR formula results with accuracy metrics

---

## TASK 5: Integrate LLM + PySR Findings 🧩 TODO

**After** both LLM analysis and PySR complete:

```bash
cd /home/solo/LadderV3/kh-assist

# 1. Compare findings
python3 << 'EOF'
# Load nemotron hypotheses
# Load gpt-oss patterns
# Load PySR formulas
# Cross-validate them
EOF

# 2. Test combined approach
# If LLM found: "drift related to k mod 32"
# And PySR found: "drift = (a*k + b) mod 256"
# Then test: drift = f(k mod 32)
```

**Deliverable**: Integrated formula with >90% accuracy

---

## TASK 6: Validate by Generating X_70→X_75 ✅ TODO

**⚠️ CRITICAL**: We DON'T have transitions 70→75 in our data!
This task is about GENERATING those transitions using the discovered formula.

**The Ultimate Test**:

```python
# Step 1: Use discovered formula to GENERATE drift for transitions 70→75
drift_70_to_71 = discovered_formula(k=70, lane=0..15)
drift_71_to_72 = discovered_formula(k=71, lane=0..15)
drift_72_to_73 = discovered_formula(k=72, lane=0..15)
drift_73_to_74 = discovered_formula(k=73, lane=0..15)
drift_74_to_75 = discovered_formula(k=74, lane=0..15)

# Step 2: Calculate unknown puzzles using GENERATED drift
X_71 = (X_70^n + drift_70_to_71) mod 256  # X_70 is known (puzzle 70)
X_72 = (X_71^n + drift_71_to_72) mod 256
X_73 = (X_72^n + drift_72_to_73) mod 256
X_74 = (X_73^n + drift_73_to_74) mod 256
X_75 = (X_74^n + drift_74_to_75) mod 256

# Step 3: Validate against known bridge value
X_75_bridge = <known from CSV>  # This is what we're comparing against

if X_75_calculated == X_75_bridge:
    # SUCCESS: 16/16 lanes match → Formula works!
    # PARTIAL: 12-15/16 lanes match → Refine formula
    # FAIL: <12/16 lanes match → Back to research
```

**This is GENERATION, not testing on existing data!**

**Deliverable**: Validation proof document showing generated vs actual X_75

---

## TASK 7: Generate Puzzles 71-95 (If Validated) 🎯 TODO

**Only proceed if Task 6 achieves 16/16 match!**

```bash
python3 generate_puzzles.py --start 71 --end 95 --validate-bridges

# Validate against known bridges: 75, 80, 85, 90, 95
# Derive Bitcoin addresses
# Compare with CSV addresses
```

**Deliverable**: Generated puzzles with cryptographic validation

---

## Quick Resume Commands

**When you return**:

```bash
cd /home/solo/LadderV3/kh-assist

# 1. Check project philosophy
cat PROJECT_PHILOSOPHY.md

# 2. Read this task list
cat RESUME_TASK_LIST.md

# 3. Check current progress
cat last_status.md

# 4. Review LLM results
cat llm_tasks/results/nemotron_drift_evolution_analysis.txt
cat llm_tasks/results/gptoss_cross_lane_analysis.txt

# 5. Verify data
python3 -c "import json; d=json.load(open('drift_data_CORRECT_BYTE_ORDER.json')); print(f'Drift values: {d[\"total_drift_values\"]}, Byte order: {d[\"byte_order\"]}')"

# 6. Continue with next task
```

---

## Files Structure

```
/home/solo/LadderV3/kh-assist/
├── PROJECT_PHILOSOPHY.md                    ← Read this for context
├── RESUME_TASK_LIST.md                      ← This file
├── last_status.md                           ← Session summary
├── HARD_PROOF_VALIDATION_2025-12-22.md      ← Hard proof results
├── drift_data_CORRECT_BYTE_ORDER.json       ← CORRECT data (verified)
├── llm_tasks/
│   ├── TASK_NEMOTRON_DRIFT_EVOLUTION.txt    ← Task definition
│   ├── TASK_GPT_OSS_CROSS_VALIDATION.txt    ← Task definition
│   ├── TASK_PYSR_DRIFT_FORMULA.txt          ← Task definition
│   └── results/
│       ├── nemotron_drift_evolution_analysis.txt  ← ✅ Done
│       ├── gptoss_cross_lane_analysis.txt         ← ⏳ Running
│       └── DRIFT_PATTERN_DISCOVERED_2025-12-22.md ← Summary
└── experiments/01-pysr-symbolic-regression/
    ├── train_drift_evolution.py             ← TODO: Create this
    └── results/
        └── drift_formula_results.json       ← PySR output

```

---

## Success Criteria

| Level | Accuracy | Status | Next Action |
|-------|----------|--------|-------------|
| 1 | 50-70% | Good start | Refine formula |
| 2 | 70-90% | Very good | Minor corrections |
| 3 | 90-99% | Excellent | Test edge cases |
| 4 | 100% | **COMPLETE** | Generate all puzzles! |

---

## Notes for Next Session

### What NOT to Do

❌ Don't train PySR on ALL drift values (includes inactive zeros)
❌ Don't use wrong CSV or missing DB data
❌ Don't ignore Rules 1 & 2 (they're 100% proven!)
❌ Don't rush - verify data first

### What TO Do

✅ Review LLM results thoroughly
✅ Validate data quality
✅ Apply discovered rules
✅ Train on evolution values only
✅ Test on X_70→X_75
✅ Document everything

---

## Estimated Timeline

**Session 1** (2-3 hours):
- Review LLM results
- Prepare PySR training script
- Launch PySR training (runs overnight)

**Session 2** (1-2 hours):
- Review PySR results
- Integrate LLM + PySR findings
- Test combined formula

**Session 3** (1 hour):
- Validate on X_70→X_75
- If successful, generate puzzles 71-95

**Total**: 4-6 hours of active work + overnight PySR

---

## Questions to Answer

1. ❓ Do LLMs agree on any specific patterns?
2. ❓ Does PySR find formulas per-lane or universal?
3. ❓ Is drift state-dependent (depends on X_k values)?
4. ❓ Are there cross-lane relationships (GPT-OSS findings)?
5. ❓ Can we achieve 100% accuracy or only asymptotic?

---

**Status**: Tasks 1-2 in progress, Tasks 3-7 ready to execute
**Blocker**: None - data validated, tools ready
**Next**: Review LLM results → Prepare PySR → Train → Validate

---

*Created: 2025-12-22*
*Purpose: Systematic resumption of drift discovery*
*Goal: 100% accurate formula for complete key generation*
