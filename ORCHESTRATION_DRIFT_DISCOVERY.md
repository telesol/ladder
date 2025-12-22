# Drift Generator Discovery - Orchestrated Multi-Agent Plan

**STATUS**: 🚀 ACTIVE ORCHESTRATION
**DATE**: 2025-12-22
**LEAD**: Claude Sonnet 4.5 (Byte Order Claude)

---

## 🎯 Mission

Discover the complete drift generator function using regime-aware, multi-agent approach.

**Goal**: `drift[k][lane] = f(k, lane, ...)` with >95% accuracy

---

## 🔥 Breakthrough Context

**Discovered**:
1. k=64 is UNIVERSAL regime boundary (9/16 lanes transition)
2. Gradual complexity increase (6% → 52% transition rate)
3. Three lane categories:
   - **Trivial (9-15)**: Always 0 ✅
   - **Learnable (7-8)**: Stable k<64, complex k≥64 ⚠️
   - **Complex (0-6)**: Always changing 🔥

---

## 📋 Orchestrated Tasks (6 Parallel Agents)

### Task 1: PySR Lane 8 (k<64 filter) - EXPECT 100%
**Agent**: Cloud Agent Alpha
**Priority**: 🔴 CRITICAL
**ETA**: 30 minutes
**Approach**:
- Filter training data: k=1-63 only
- Run PySR on lane 8
- Expected: 100% accuracy (drift=0 formula)

### Task 2: PySR Lane 7 (k<64 filter)
**Agent**: Cloud Agent Beta
**Priority**: 🔴 CRITICAL
**ETA**: 1 hour
**Approach**:
- Filter training data: k=1-50 (keep in stable zone)
- Run PySR on lane 7
- Expected: >90% accuracy (affine with A=23)

### Task 3: Cross-Lane Dependency Analysis (Lanes 0-6)
**Agent**: Cloud Agent Gamma
**Priority**: 🟡 HIGH
**ETA**: 1-2 hours
**Approach**:
- Test hypothesis: lanes 0-6 depend on multiple lanes
- For each lane L: `drift[k][L] = f(drift[k-1][0..L])`
- Use linear regression, then non-linear if needed
- Report which lanes have dependencies

### Task 4: Index-Based Pattern Analysis (Lanes 0-6)
**Agent**: Cloud Agent Delta
**Priority**: 🟡 HIGH
**ETA**: 1-2 hours
**Approach**:
- Test hypothesis: lanes 0-6 are index-based (f(k, lane))
- Try polynomial fits, modular arithmetic
- Compare with H1 results (69.57%)
- Find best formula per lane

### Task 5: Regime-Specific PySR (Lanes 0-6)
**Agent**: Cloud Agent Epsilon
**Priority**: 🟢 MEDIUM
**ETA**: 2-3 hours
**Approach**:
- Split data: k<32, k=32-63, k≥64
- Train separate PySR models per regime
- Test if regime-specific formulas improve accuracy

### Task 6: Hybrid Generator Construction
**Agent**: Me (Coordinator)
**Priority**: 🟢 LOW (after others complete)
**ETA**: 1 hour
**Approach**:
- Synthesize results from Tasks 1-5
- Build hybrid generator:
  ```python
  def drift_generator(k, lane, drift_prev):
      if lane >= 9:
          return 0  # Trivial
      elif lane == 8:
          return 0 if k < 64 else bridge_value(k, lane)
      elif lane == 7:
          return pysr_formula_lane7(k, drift_prev) if k < 64 else bridge_value(k, lane)
      else:  # lanes 0-6
          return complex_generator(k, lane, drift_prev)
  ```

---

## 📊 Success Metrics

| Task | Target Accuracy | Status |
|------|-----------------|--------|
| Task 1 (Lane 8, k<64) | 100% | 📋 Pending |
| Task 2 (Lane 7, k<64) | >90% | 📋 Pending |
| Task 3 (Cross-lane) | Identify dependencies | 📋 Pending |
| Task 4 (Index-based) | >80% for 1+ lane | 📋 Pending |
| Task 5 (Regime PySR) | >85% overall | 📋 Pending |
| Task 6 (Hybrid) | >95% overall | 📋 Pending |

---

## 🔄 Coordination Protocol

**Status Updates**: Every 30 minutes
**Results Location**: `experiments/07-pysr-drift-generator/results/`
**Communication**: `ORCHESTRATION_STATUS.json`

**When Agent Completes**:
1. Save results to JSON
2. Update status file
3. Report key findings
4. Unblock dependent tasks

---

## 📁 File Organization

```
experiments/07-pysr-drift-generator/
├── results/
│   ├── task1_lane8_k64_filtered.json
│   ├── task2_lane7_k64_filtered.json
│   ├── task3_cross_lane_analysis.json
│   ├── task4_index_based_analysis.json
│   ├── task5_regime_specific.json
│   └── task6_hybrid_generator.py
├── train_k64_filtered.csv (k<64 only)
├── train_stable.csv (k<32 only)
└── train_regime*.csv (per regime)
```

---

## 🚀 Launch Sequence

1. ✅ Commit breakthrough findings
2. ⏳ Prepare filtered datasets (k<64, k<32, etc.)
3. 🚀 Launch Tasks 1-5 in parallel (5 cloud agents)
4. ⏳ Monitor progress
5. 🔄 Synthesize results (Task 6)
6. ✅ Validate hybrid generator on all 1,104 values
7. 🎉 Report final accuracy

---

**Status**: 🟢 READY TO LAUNCH
**Next**: Prepare datasets, launch 5 parallel agents

---

*Orchestrator: Claude Sonnet 4.5 (Byte Order Claude)*
*Date: 2025-12-22*
*Strategy: Regime-aware, multi-agent, parallel execution*
