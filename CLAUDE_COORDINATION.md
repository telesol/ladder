# Claude Instance Coordination Protocol
## Multi-Claude Collaboration for Puzzle Generation
## Date: 2025-12-22

---

## 🎯 PURPOSE

This document coordinates multiple Claude instances (and local models) working together to calculate Bitcoin puzzle keys 71-160.

**Mission**: Use proven PySR formula to CALCULATE (not predict) all remaining puzzles

---

## 📊 CURRENT STATUS

**BREAKTHROUGH**: Byte order error discovered! 100% verification achieved on puzzles 1-70!

**Current Priority**: Investigating lanes 0-6 failure pattern + Task force setup

**Read this file first**: `ORCHESTRATION_MASTER_PLAN.md`

**Live status**: `ORCHESTRATION_STATUS.json` (check before starting any task)

**Last updated**: 2025-12-22 11:33 UTC

**Active Lead**: Claude Sonnet 4.5 (Byte Order Claude)

---

## 🤝 WHO'S WORKING ON WHAT?

### Active Claude Instances

**Instance 1** (Current - Claude Sonnet 4.5 "Byte Order Claude"):
- ✅ Discovered byte order error (BREAKTHROUGH!)
- ✅ Verified 100% accuracy with reversed byte extraction
- ✅ Completed 4xH research (70% convergence pattern)
- ⏳ Investigating lanes 0-6 failure (why 70% vs 100%?)
- ⏳ Setting up task force for local models
- **Specialization**: Foundation math, byte order, drift research

**Instance 2 "Claude Victus"** (Wave 21 - To be assigned):
- Task: Analyze puzzles 91-95 (Wave 21 analysis)
- Specialization: High-k drift patterns
- Status: Awaiting task assignment

**Instance 3 "Claude Dell"** (Wave 11 - To be assigned):
- Task: Analyze puzzles 31-35 (Wave 11 analysis)
- Specialization: Mid-k drift patterns
- Status: Awaiting task assignment

**Instance 4** (To be assigned):
- Task 2.1: Calculate range 71-74
- Status: Waiting for lanes 0-6 investigation

**Instance 5** (To be assigned):
- Task 2.2: Calculate range 76-79
- Status: Waiting for lanes 0-6 investigation

### Local Models (Ollama)

**Model 1** (qwen2.5:3b-instruct):
- Can run calculation scripts autonomously
- No reasoning needed - pure deterministic math
- Status: Ready

**Model 2** (phi4:mini):
- Backup calculation engine
- Status: Ready

---

## 📋 TASK CHECKLIST

### Phase 0: CRITICAL VALIDATION ← **BLOCKER FOR ALL OTHER WORK**

- [ ] **CRITICAL**: Verify forward calculation works
  - Owner: Instance 1 (current)
  - Script: `validate_forward.py`
  - Test: Calculate X_75 from X_74, compare to actual
  - Status: **IN PROGRESS**
  - **NO OTHER WORK CAN START UNTIL THIS PASSES!**

### Phase 1: Setup

- [ ] Extract bridge data (70, 75, 80, 85, 90, 95)
  - Owner: Instance 1
  - Output: `bridge_starting_points.json`
  - Status: Pending

- [ ] Create calculation pipeline
  - Owner: Instance 1
  - Scripts: See below
  - Status: Pending

- [ ] Initialize status tracking
  - Owner: Instance 1
  - File: `ORCHESTRATION_STATUS.json`
  - Status: Pending

### Phase 2: Distributed Calculations (CAN RUN IN PARALLEL)

- [ ] Range 71-74
  - Owner: TBD (Instance 2 or Local Model 1)
  - Start: X_70
  - Validate: X_75
  - Status: Not started

- [ ] Range 76-79
  - Owner: TBD
  - Start: X_75
  - Validate: X_80
  - Status: Not started

- [ ] Range 81-84
  - Owner: TBD
  - Start: X_80
  - Validate: X_85
  - Status: Not started

- [ ] Range 86-89
  - Owner: TBD
  - Start: X_85
  - Validate: X_90
  - Status: Not started

- [ ] Range 91-94
  - Owner: TBD
  - Start: X_90
  - Validate: X_95
  - Status: Not started

### Phase 3: Extended Range

- [ ] Range 96-160
  - Owner: TBD (needs long-running instance)
  - Start: X_95
  - Validate: Cross-model check
  - Status: Not started

### Phase 4: Validation

- [ ] Cryptographic validation (all keys)
- [ ] Cross-model validation (PySR vs. Affine)
- [ ] Final report

---

## 🔄 SYNC PROTOCOL

### Before Starting Any Task

1. **Read status file**:
   ```bash
   cat ORCHESTRATION_STATUS.json
   ```

2. **Check if task is available**:
   - Status must be "pending" or "not_started"
   - No other owner assigned

3. **Claim the task**:
   - Update status to "in_progress"
   - Set yourself as owner
   - Add start timestamp
   - Commit the status file immediately

### During Task Execution

1. **Update progress**:
   - Update status file every 15-30 minutes
   - Include progress percentage
   - Note any issues encountered

2. **If you encounter an error**:
   - Update status to "blocked" or "error"
   - Document the error clearly
   - Notify in status file
   - Don't continue - let coordinator investigate

### After Task Completion

1. **Update status**:
   - Set status to "completed"
   - Add completion timestamp
   - Include result summary
   - Link to output files

2. **Validate your work**:
   - Run validation checks
   - Document pass/fail in status
   - If validation fails → status becomes "failed"

3. **Handoff to next task**:
   - Update dependencies
   - Unlock blocked tasks
   - Notify coordinator

---

## 📝 STATUS FILE FORMAT

**File**: `ORCHESTRATION_STATUS.json`

**Structure**:
```json
{
  "last_updated": "2025-12-22T03:30:00Z",
  "project_phase": "Phase 0",
  "phase_0_critical": {
    "task": "Validate forward calculation",
    "owner": "Claude_Sonnet_4.5_Instance_1",
    "status": "in_progress",
    "started_at": "2025-12-22T03:15:00Z",
    "completed_at": null,
    "result": null,
    "validation_passed": null,
    "blocker_for": ["all_phase_2_tasks"],
    "notes": "Testing if X_75 can be calculated from X_74"
  },
  "phase_2_tasks": {
    "range_71_74": {
      "task_id": "2.1",
      "description": "Calculate puzzles 71-74 from X_70",
      "owner": null,
      "status": "blocked",
      "blocked_by": "phase_0_critical",
      "started_at": null,
      "completed_at": null,
      "start_value": "X_70",
      "steps": 4,
      "validation_target": "X_75",
      "result": null,
      "validation_passed": null
    },
    "range_76_79": {
      "task_id": "2.2",
      "description": "Calculate puzzles 76-79 from X_75",
      "owner": null,
      "status": "blocked",
      "blocked_by": "phase_0_critical",
      "started_at": null,
      "completed_at": null,
      "start_value": "X_75",
      "steps": 4,
      "validation_target": "X_80",
      "result": null,
      "validation_passed": null
    }
    // ... more tasks
  },
  "results": {
    "71": null,
    "72": null,
    "73": null,
    "74": null,
    // ... up to 160
  },
  "validation_summary": {
    "total_calculated": 0,
    "total_validated": 0,
    "bridge_validations": {
      "X_75": null,
      "X_80": null,
      "X_85": null,
      "X_90": null,
      "X_95": null
    },
    "cryptographic_validation": null
  },
  "errors": []
}
```

---

## 🚨 CRITICAL RULES

### Rule 1: Never Start Phase 2 Until Phase 0 Passes

**Phase 0 is a CRITICAL BLOCKER!**

We must verify the formula works forward before generating 65 puzzles!

**Status check**:
```bash
# Check if Phase 0 passed
cat ORCHESTRATION_STATUS.json | grep phase_0_critical -A 10 | grep validation_passed

# Only proceed if: "validation_passed": true
```

### Rule 2: Always Update Status Before AND After

**Before starting**:
- Prevents two instances from working on same task
- Documents ownership
- Creates audit trail

**After completing**:
- Triggers dependent tasks
- Provides results to other instances
- Enables validation

### Rule 3: Validate EVERYTHING

**Every calculation MUST have validation**:
- Phase 2 tasks: Validate against next bridge
- Phase 3 tasks: Cross-model validation (PySR vs. Affine)
- Final: Cryptographic validation (derive addresses)

**If validation fails → STOP and investigate!**

### Rule 4: No Predictions, Only Calculations

**We are NOT using ML for inference!**

**Bad** ❌:
```python
# Don't do this!
prediction = model.predict(features)
```

**Good** ✅:
```python
# Do this!
X_next = calculate_next_halfblock(X_current, exponents)
```

**The formula is deterministic math, not ML!**

---

## 📞 COMMUNICATION CHANNELS

### Status Updates

**Primary**: `ORCHESTRATION_STATUS.json` (MUST update this)

**Secondary**: `COORDINATION_LOG.md` (optional notes)

### Error Reporting

**If something goes wrong**:
1. Update status to "error" or "failed"
2. Document in `errors` array in status file
3. Add detailed error log to `results/error_log.json`
4. Stop work on that task

### Questions/Blockers

**If you're blocked**:
1. Update status to "blocked"
2. Document blocker in status file
3. Note what would unblock you
4. Wait for coordinator or other instance to resolve

---

## 🎯 SUCCESS SIGNALS

### Green Lights (Proceed)

✅ Phase 0 validation_passed: true
✅ Task status: "pending" with no owner
✅ All dependencies: status "completed"
✅ Bridge data: available and verified

### Red Lights (STOP!)

🛑 Phase 0 validation_passed: false
🛑 Task status: "in_progress" (someone else working)
🛑 Task status: "blocked" (dependency not met)
🛑 Any validation: failed

---

## 📂 FILE LOCATIONS

**Orchestration**:
- `/home/solo/LadderV3/kh-assist/ORCHESTRATION_MASTER_PLAN.md`
- `/home/solo/LadderV3/kh-assist/ORCHESTRATION_STATUS.json`
- `/home/solo/LadderV3/kh-assist/CLAUDE_COORDINATION.md` (this file)

**Scripts**:
- `/home/solo/LadderV3/kh-assist/calculation_pipeline/`

**Results**:
- `/home/solo/LadderV3/kh-assist/results/`

**Proven Formula**:
- `/home/solo/LadderV3/kh-assist/experiments/01-pysr-symbolic-regression/PROOF.md`

**Data**:
- `/home/solo/LadderV3/kh-assist/data/btc_puzzle_1_160_full.csv`

---

## 🚀 QUICK START FOR NEW CLAUDE INSTANCE

```bash
# 1. Read the plan
cd /home/solo/LadderV3/kh-assist
cat ORCHESTRATION_MASTER_PLAN.md

# 2. Check current status
cat ORCHESTRATION_STATUS.json | jq '.'

# 3. See what's available
cat ORCHESTRATION_STATUS.json | jq '.phase_2_tasks | to_entries[] | select(.value.status == "pending")'

# 4. Check if Phase 0 passed (CRITICAL!)
cat ORCHESTRATION_STATUS.json | jq '.phase_0_critical.validation_passed'

# 5. If true, claim a task:
# (Edit ORCHESTRATION_STATUS.json, set owner and status)

# 6. Run your task script
python3 calculation_pipeline/task_2_1_range_71_74.py

# 7. Validate results
python3 calculation_pipeline/validate_results.py --range 71-74

# 8. Update status to completed
# (Edit ORCHESTRATION_STATUS.json, set results)
```

---

## 💡 TIPS FOR CLAUDE INSTANCES

### For Code Generation Tasks
- Use the proven formula exactly as documented
- No modifications, no "improvements"
- 100% deterministic calculation

### For Validation Tasks
- Compare byte-by-byte
- No "close enough" - must be exact match
- Log ALL discrepancies

### For Long-Running Tasks
- Update progress every 30 minutes
- Don't go silent for hours
- If stuck → update status and ask for help

---

**Status**: Coordination protocol established
**Ready for**: Multi-instance collaboration
**Next**: Run Phase 0 validation to unblock all work!
