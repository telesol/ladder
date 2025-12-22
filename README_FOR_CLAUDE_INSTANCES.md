# README for Claude Instances

**Date**: 2025-12-22
**Target Audience**: Future Claude instances resuming this project
**Priority**: HIGH - Read before doing ANY work

---

## 🚨 CRITICAL: Read These Files FIRST 🚨

**Order matters - read in this sequence:**

1. **CRITICAL_NOTE_READ_FIRST.md** ⚠️
   - Corrects a major misunderstanding about available data
   - **MUST READ** before proceeding

2. **CORRECTED_UNDERSTANDING_2025-12-22.md**
   - Explains what changed and why
   - Details the data reality vs previous assumptions

3. **PROJECT_PHILOSOPHY.md**
   - Scientific approach: we compute, not brute force
   - We prove, not predict

4. **RESUME_TASK_LIST.md**
   - 7-task systematic plan
   - Currently at TASK 3 (prepare PySR script)

5. **LLM_ANALYSIS_CONSOLIDATED_2025-12-22.md**
   - Nemotron + GPT-OSS findings
   - Key discoveries about drift patterns

---

## Quick Summary for Busy Claude

### What This Project Is

**Discovering a mathematical formula to generate Bitcoin puzzle keys**

- We have keys for puzzles 1-70 (solved)
- We have bridge values: 75, 80, 85, 90, 95, ... (solved)
- We DON'T have puzzles 71-74, 76-79, etc. (unknown - this is what we're generating!)

### The Formula

```
X_{k+1}[lane] = ((X_k[lane])^n + drift[k][lane]) mod 256

where:
  n = EXPONENTS[lane] = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]
  drift[k][lane] = ??? ← THIS is what we're discovering!
```

### What We Know

**70% of drift formula discovered**:
- Rule 1: `drift = 0` if `k < lane × 8` (100% proven)
- Rule 2: `drift = 1` if `k == lane × 8` (100% proven)

**30% still unknown**:
- Evolution formula: `drift = ???` if `k > lane × 8`

### Available Data

**What we HAVE**:
- 69 transitions (1→2, 2→3, ..., 69→70)
- 1,104 drift values from these transitions
- 82 solved puzzles total (1-70 + bridges)

**What we DON'T HAVE**:
- Transitions 70→71, 71→72, ..., 74→75 (must GENERATE these!)
- Keys for puzzles 71-74 (unknown - what we're calculating!)

### The Goal

1. Train PySR on transitions 1-69
2. Discover the drift formula
3. **GENERATE** drift for transitions 70+
4. Calculate unknown puzzles using generated drift
5. Validate by comparing calculated X_75 with known bridge value
6. If successful, generate ALL puzzles 71-160!

### Current Status

- ✅ TASK 1: LLM analysis complete (Nemotron + GPT-OSS)
- ✅ TASK 2: Data validation complete
- 📝 TASK 3: Need to prepare PySR training script (next!)
- ⏳ TASK 4-7: Pending

### Key Discoveries (From LLM Analysis)

1. **Drift is NOT random** (χ² p < 10⁻⁶⁸)
2. **>95% of drift values are multiples of 16** (quantized!)
3. **Lanes are independent** (no cross-lane correlation)
4. **Drift is a step function** (jumps once, stays constant)

### Common Mistakes to Avoid

❌ **DON'T** assume we can "test" on transitions 70-75 (we don't have them!)
❌ **DON'T** train on ALL drift values (exclude inactive/initialization)
❌ **DON'T** think we're validating an existing formula (we're discovering it!)

✅ **DO** read CRITICAL_NOTE_READ_FIRST.md
✅ **DO** train on transitions 1-69 ONLY
✅ **DO** use discovered formula to GENERATE transitions 70+
✅ **DO** validate on bridge values (75, 80, 85, ...)

---

## Quick Start

```bash
cd /home/solo/LadderV3/kh-assist

# 1. Read critical corrections first!
cat CRITICAL_NOTE_READ_FIRST.md

# 2. Check current task
cat RESUME_TASK_LIST.md | grep -A 20 "TASK 3"

# 3. Review LLM findings
cat LLM_ANALYSIS_CONSOLIDATED_2025-12-22.md

# 4. Proceed with PySR training script (TASK 3)
```

---

## Files You'll Need

**Critical Documentation**:
- `CRITICAL_NOTE_READ_FIRST.md` ⚠️ (read this!)
- `CORRECTED_UNDERSTANDING_2025-12-22.md` (why things changed)
- `README_FOR_CLAUDE_INSTANCES.md` (this file)

**Project Documentation**:
- `PROJECT_PHILOSOPHY.md` (scientific approach)
- `RESUME_TASK_LIST.md` (7-task plan)
- `LLM_ANALYSIS_CONSOLIDATED_2025-12-22.md` (key findings)

**Data Files**:
- `drift_data_CORRECT_BYTE_ORDER.json` (1,104 drift values, transitions 1-69)
- `data/btc_puzzle_1_160_full.csv` (solved puzzles + bridges)

**Status Files**:
- `last_status.md` (session summary)
- `TASK_2_VALIDATION_COMPLETE_2025-12-22.md` (data validation results)

---

## What Success Looks Like

**Goal**: Discover drift formula with 100% accuracy

**Validation**:
1. Generate transitions 70→75 using formula
2. Calculate X_75 from X_70
3. Compare with known bridge value
4. **SUCCESS**: Perfect match → can generate ALL puzzles 71-160!

**Impact**: Complete the Bitcoin puzzle set mathematically!

---

## Contact/Collaboration

This project uses:
- PySR (symbolic regression)
- Local LLMs (Nemotron, GPT-OSS)
- Claude Code (orchestration)

Task files in `/llm_tasks/` can be delegated to other agents.

---

**Last Updated**: 2025-12-22
**Status**: Tasks 1-2 complete, Task 3 next
**Goal**: Discover the drift formula → generate unknown puzzles!

🚀 **The drift formula is the KEY to the entire project!** 🚀
