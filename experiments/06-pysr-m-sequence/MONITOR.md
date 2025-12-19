# PySR Training Monitor Guide

**Started**: 2025-12-19 21:39 UTC
**PID**: 3451 (saved in `pysr_pid.txt`)
**Expected Duration**: 2-4 hours

---

## 🔍 Quick Status Check

```bash
cd /home/solo/LadderV3/kh-assist/experiments/06-pysr-m-sequence

# Check if still running
ps -p $(cat pysr_pid.txt) && echo "✅ Running" || echo "⚠️ Finished or stopped"

# Check status
cat STATUS.txt

# View recent progress
tail -20 training.log
```

---

## 📊 Monitor Progress

### Real-time Monitoring
```bash
# Follow training log
tail -f training.log

# Watch status updates
watch -n 5 cat STATUS.txt
```

### Check Results
```bash
# Check if results are ready
ls -lh training_results.json 2>/dev/null && echo "✅ Results available!"

# View results
cat training_results.json | python3 -m json.tool
```

---

## 🎯 What to Look For

### During Training

**Good signs**:
- "PySR training..." message appears
- Equation file being created (`pysr_equations.csv`)
- No error messages
- STATUS.txt shows "TRAINING"

**Warning signs**:
- "ERROR" in training.log
- Process not running (check with `ps -p`)
- STATUS.txt shows "ERROR"

### Training Complete

**Success indicators**:
- `training_results.json` created
- `m_sequence_model.pkl` created
- STATUS.txt shows `SUCCESS_XX` (where XX = accuracy %)
- No errors in training.log

---

## 📈 Expected Timeline

| Time | Activity |
|------|----------|
| T+0 | Feature engineering (DONE ✅) |
| T+5min | PySR initialization |
| T+10min | First equations discovered |
| T+30min | ~10-20% progress |
| T+1hr | ~25-30% progress |
| T+2hrs | ~50-60% progress |
| T+3hrs | ~80-90% progress |
| T+4hrs | Validation and completion |

---

## 🚨 If Something Goes Wrong

### Check for Errors
```bash
grep -i error training.log
grep -i exception training.log
```

### Restart if Needed
```bash
# Kill current run
kill $(cat pysr_pid.txt)

# Restart
nohup python3 train_m_sequence.py > training.log 2>&1 &
echo $! > pysr_pid.txt
```

### Get Help
```bash
# Show last 50 lines of log
tail -50 training.log

# Check Python process details
ps aux | grep train_m_sequence
```

---

## ✅ When Training Completes

### View Results
```bash
# Show validation accuracy
cat training_results.json | python3 -c "import json, sys; d=json.load(sys.stdin); print(f'Accuracy: {d[\"validation\"][\"accuracy_percent\"]:.1f}%')"

# Show best equation
cat training_results.json | python3 -c "import json, sys; d=json.load(sys.stdin); print(f'Formula: {d[\"best_equation\"]}')"

# Full results
cat training_results.json | python3 -m json.tool
```

### Success Scenarios

**100% Accuracy** 🎉:
- Formula discovered!
- Generate all 160 puzzles
- Project complete!

**90-99% Accuracy** 🔥:
- Very strong formula
- Refine or use hybrid approach
- Near complete solution

**80-89% Accuracy** 👍:
- Good progress
- Phase-based training
- Combine approaches

**<80% Accuracy** 💡:
- Insights gained
- Try different features
- Neural network backup

---

## 🖥️ On Dell with RTX 6000 Ada

Since you have a powerful GPU, PySR might run faster!

### GPU Acceleration (if configured)
```bash
# Check GPU usage
nvidia-smi

# If PySR uses GPU, you'll see Python process using VRAM
watch -n 1 nvidia-smi
```

### Transfer to Dell
If you want to run on Dell instead:
```bash
# On this machine - stop training
kill $(cat pysr_pid.txt)

# Copy to Dell
scp -r /home/solo/LadderV3/kh-assist/experiments/06-pysr-m-sequence dell:/path/

# On Dell - restart training
cd /path/06-pysr-m-sequence
nohup python3 train_m_sequence.py > training.log 2>&1 &
```

---

## 📁 Key Files

| File | Purpose | Status |
|------|---------|--------|
| `STATUS.txt` | Current status | Updates during run |
| `training.log` | Full output | Appends continuously |
| `pysr_pid.txt` | Process ID | Static (3451) |
| `feature_matrix.csv` | Input data | ✅ Ready |
| `pysr_equations.csv` | Discovered formulas | Created during training |
| `training_results.json` | Final results | Created when done |
| `m_sequence_model.pkl` | Trained model | Created when done |

---

## 🎯 Quick Commands Reference

```bash
# Status
cat STATUS.txt

# Progress
tail -f training.log

# Still running?
ps -p $(cat pysr_pid.txt)

# Results ready?
ls training_results.json

# View results
cat training_results.json | python3 -m json.tool | less

# Kill if needed
kill $(cat pysr_pid.txt)
```

---

**Good luck! May PySR discover the formula!** 🚀

**Next update**: Check back in 2-4 hours for results!
