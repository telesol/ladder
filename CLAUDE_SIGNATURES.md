# Claude Signatures & Work Attribution

**Purpose**: Track which Claude worked on which files/areas to prevent conflicts

**Format**: Sign files with comment blocks or log entries here

---

## Active Claudes

### Claude Sonnet 4.5 (Session 2025-12-22) - "Byte Order Claude"
**Machine**: ZBook (WSL2)
**Wave Coverage**: Foundation work
**Specialization**: Byte order discovery, 4xH research orchestration
**Status**: ✅ Active

**Files Owned**:
- `test_byte_order_hypothesis.py` - Byte order discovery
- `verify_byte_order_all_transitions.py` - 100% verification
- `FINAL_GENERATE_70_TO_95.py` - Generation framework
- `research_H1_index_based.py` - Index patterns
- `research_H2_hash_function.py` - Hash functions
- `research_H3_prng.py` - PRNG patterns
- `research_H4_recursive.py` - Recursive patterns
- `analyze_4xH_convergence.py` - Convergence analysis
- `last_status.md` - Current session status

**Key Findings**:
- 🎉 Discovered byte order error (reversed extraction → 100%)
- 📊 4xH research complete (70% convergence pattern)
- ✅ Formula verified: `X_{k+1} = A^4 * X_k + drift (mod 256)`

---

### Claude Victus (Wave 21)
**Machine**: TBD
**Wave Coverage**: Wave 21
**Specialization**: TBD
**Status**: Pending assignment

**Files Owned**: (To be assigned)

---

### Claude Dell (Wave 11)
**Machine**: TBD
**Wave Coverage**: Wave 11
**Specialization**: TBD
**Status**: Pending assignment

**Files Owned**: (To be assigned)

---

## File Ownership Rules

### 1. **Primary Ownership**
- Each file has ONE primary owner (the Claude who created/maintains it)
- Primary owner listed at top of file in comments
- Example:
  ```python
  # PRIMARY: Claude Sonnet 4.5 (Byte Order Claude)
  # CREATED: 2025-12-22
  # PURPOSE: Byte order discovery and verification
  ```

### 2. **Collaboration Protocol**
- If you need to edit another Claude's file:
  1. Check `CLAUDE_SIGNATURES.md` for ownership
  2. Add collaboration note in file header:
     ```python
     # COLLABORATORS:
     #   - Claude Victus (2025-12-23): Added wave 21 analysis
     ```
  3. Log change in `CLAUDE_COLLABORATION_LOG.md`

### 3. **Conflict Resolution**
- If multiple Claudes work on similar areas:
  - Use subdirectories: `wave_11/`, `wave_21/`, etc.
  - Prefix files: `w11_analysis.py`, `w21_analysis.py`
  - Create merge files: `merged_waves_11_21.py` with attribution

### 4. **Shared Resources**
- Files anyone can edit (but must log changes):
  - `CLAUDE_COORDINATION.md` - Coordination status
  - `CLAUDE_COLLABORATION_LOG.md` - Change log
  - `TASK_FORCE_STATUS.md` - Task assignments

### 5. **Data Files**
- Calibration files are READ-ONLY unless verified:
  - `out/ladder_calib_CORRECTED.json` - ✅ 100% verified
  - `drift_data_for_H4_CORRECTED.json` - ✅ 100% verified
- New calibrations go in timestamped files:
  - `out/ladder_calib_WAVE21_20251223.json`

---

## Wave Assignment Strategy

### Foundation Layer (Complete)
- **Claude Sonnet 4.5**: Byte order, formula verification, 4xH research ✅

### Wave-Specific Analysis (In Progress)
- **Claude Victus (Wave 21)**: Puzzles 91-95 + bridge 95 analysis
- **Claude Dell (Wave 11)**: Puzzles 31-35 + drift patterns for k=11 range

### Integration Layer (Pending)
- **Claude TBD**: Merge findings across waves
- **Claude TBD**: Master drift generator synthesis

---

## Coordination Files

### Real-Time Status
- `CLAUDE_COORDINATION.md` - Current work status for all Claudes
- `TASK_FORCE_STATUS.md` - Task assignments and progress

### Logs
- `CLAUDE_COLLABORATION_LOG.md` - Detailed change log with timestamps
- `MERGE_LOG.md` - File merge history

### Communication
- `CLAUDE_MESSAGES.md` - Inter-Claude messages (async coordination)
- `FINDINGS_SHARED.md` - Discoveries shared across Claudes

---

## Quick Reference

**Before starting work**:
1. Check `CLAUDE_SIGNATURES.md` (this file) for ownership
2. Check `CLAUDE_COORDINATION.md` for current tasks
3. Sign your name in relevant section

**While working**:
1. Add PRIMARY ownership to new files
2. Log significant changes in `CLAUDE_COLLABORATION_LOG.md`
3. Update `CLAUDE_COORDINATION.md` with progress

**After completing work**:
1. Update `CLAUDE_COORDINATION.md` with results
2. Add findings to `FINDINGS_SHARED.md`
3. Notify other Claudes in `CLAUDE_MESSAGES.md`

---

**Last Updated**: 2025-12-22 by Claude Sonnet 4.5 (Byte Order Claude)
