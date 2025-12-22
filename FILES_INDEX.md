# Files Index - Quick Reference

**Purpose**: Help Claude instances find the right files quickly
**Updated**: 2025-12-22

---

## 🚨 START HERE (Critical Files)

| File | Purpose | Priority |
|------|---------|----------|
| `CRITICAL_NOTE_READ_FIRST.md` | ⚠️ Corrects major data misunderstanding | **READ FIRST!** |
| `CORRECTED_UNDERSTANDING_2025-12-22.md` | Explains what was wrong and what's correct | **READ SECOND** |
| `README_FOR_CLAUDE_INSTANCES.md` | Quick start guide for Claude instances | **READ THIRD** |

---

## 📋 Project Documentation

| File | Purpose |
|------|---------|
| `PROJECT_PHILOSOPHY.md` | Scientific approach: compute, not brute force |
| `RESUME_TASK_LIST.md` | 7-task systematic plan for drift discovery |
| `FILES_INDEX.md` | This file - helps you find things |

---

## 📊 Analysis & Results

| File | Content | Status |
|------|---------|--------|
| `LLM_ANALYSIS_CONSOLIDATED_2025-12-22.md` | Nemotron + GPT-OSS findings | ✅ Complete |
| `TASK_2_VALIDATION_COMPLETE_2025-12-22.md` | Data validation results | ✅ Complete |
| `HARD_PROOF_VALIDATION_2025-12-22.md` | Manual calculation (outdated context) | ⚠️ Context corrected |
| `llm_tasks/results/nemotron_drift_evolution_analysis.txt` | Nemotron's full analysis (192 lines) | ✅ Complete |
| `llm_tasks/results/gptoss_cross_lane_analysis.txt` | GPT-OSS's full analysis (257 lines) | ✅ Complete |

---

## 💾 Data Files

| File | Content | Size | Status |
|------|---------|------|--------|
| `drift_data_CORRECT_BYTE_ORDER.json` | 1,104 drift values (transitions 1-69) | 46.8 KB | ✅ Verified |
| `data/btc_puzzle_1_160_full.csv` | Solved puzzles (1-70 + bridges) | - | ✅ Valid |

**Important**: We have transitions 1→69 ONLY. No transitions 70→75!

---

## 📝 Session Status

| File | Purpose |
|------|---------|
| `last_status.md` | Previous session summary (needs updating) |
| `TASK_2_VALIDATION_COMPLETE_2025-12-22.md` | Most recent completed task |

---

## 🔬 Experiments

| Directory | Purpose | Status |
|-----------|---------|--------|
| `experiments/01-pysr-symbolic-regression/` | PySR training (X formula - complete) | ✅ Done |
| `experiments/01-pysr-symbolic-regression/` | PySR training (drift formula - TODO) | 📝 Next task |

---

## 📁 Task Definitions

| File | Target | Status |
|------|--------|--------|
| `llm_tasks/TASK_NEMOTRON_DRIFT_EVOLUTION.txt` | Nemotron analysis task | ✅ Complete |
| `llm_tasks/TASK_GPT_OSS_CROSS_VALIDATION.txt` | GPT-OSS analysis task | ✅ Complete |
| `llm_tasks/TASK_PYSR_DRIFT_FORMULA.txt` | PySR training task | ⏳ Ready |

---

## 🗂️ Directory Structure

```
/home/solo/LadderV3/kh-assist/
├── CRITICAL_NOTE_READ_FIRST.md ⚠️ ← START HERE!
├── CORRECTED_UNDERSTANDING_2025-12-22.md
├── README_FOR_CLAUDE_INSTANCES.md
├── FILES_INDEX.md (this file)
│
├── PROJECT_PHILOSOPHY.md
├── RESUME_TASK_LIST.md
├── last_status.md
│
├── LLM_ANALYSIS_CONSOLIDATED_2025-12-22.md
├── TASK_2_VALIDATION_COMPLETE_2025-12-22.md
├── HARD_PROOF_VALIDATION_2025-12-22.md
│
├── drift_data_CORRECT_BYTE_ORDER.json
│
├── data/
│   └── btc_puzzle_1_160_full.csv
│
├── llm_tasks/
│   ├── TASK_NEMOTRON_DRIFT_EVOLUTION.txt
│   ├── TASK_GPT_OSS_CROSS_VALIDATION.txt
│   ├── TASK_PYSR_DRIFT_FORMULA.txt
│   └── results/
│       ├── nemotron_drift_evolution_analysis.txt
│       ├── gptoss_cross_lane_analysis.txt
│       └── DRIFT_PATTERN_DISCOVERED_2025-12-22.md
│
└── experiments/01-pysr-symbolic-regression/
    ├── train_drift_evolution.py (TODO: create for drift)
    └── results/
```

---

## 🎯 Current Task

**TASK 3**: Prepare PySR Training Script

**Location**: `experiments/01-pysr-symbolic-regression/train_drift_evolution.py`

**Purpose**: Train on transitions 1-69 to discover drift formula

**Next**: See `RESUME_TASK_LIST.md` for details

---

## 🔍 Quick Search

Looking for specific information?

**Data validation**: `TASK_2_VALIDATION_COMPLETE_2025-12-22.md`
**LLM findings**: `LLM_ANALYSIS_CONSOLIDATED_2025-12-22.md`
**Scientific approach**: `PROJECT_PHILOSOPHY.md`
**Task list**: `RESUME_TASK_LIST.md`
**Critical correction**: `CRITICAL_NOTE_READ_FIRST.md`

---

**Last Updated**: 2025-12-22
**Status**: Index complete, ready for use
**Purpose**: Help Claude instances navigate the project efficiently
