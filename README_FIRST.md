# 👋 WELCOME CLAUDE!

If you're a new Claude instance working on this project, **START HERE!**

---

## 🎯 FIRST STEPS (DO THIS NOW!)

### 1. Read the Protocol ⚠️ MANDATORY
```bash
cat ORCHESTRATOR_PROTOCOL.md
```

### 2. Check Current Status
```bash
./check_findings.sh
```

### 3. Identify Your Machine
- **Zbook**: Deep analysis, formula discovery → `local-work` branch
- **Victus**: Wave analysis, dataset curation → `main` branch
- **LA**: Orchestration, PySR, integration → `main` branch
- **Dell**: Validation, cross-checking → `dell-validation` branch

### 4. Pull Latest From ALL Branches
```bash
git fetch --all
git log --all --oneline --graph -10
```

---

## 📚 REQUIRED READING

1. **ORCHESTRATOR_PROTOCOL.md** - How to work with other Claudes
2. **FINDINGS_DASHBOARD.md** - What's been discovered
3. **CLAUDE.md** - Historical context (Waves 1-17)
4. **findings/[today]/DAILY_SUMMARY.md** - Today's progress

---

## 🚫 COMMON MISTAKES TO AVOID

1. ❌ Starting work without reading dashboard
2. ❌ Making discoveries without updating dashboard
3. ❌ Working on something another machine already did
4. ❌ Committing without organizing in findings/
5. ❌ Assuming patterns hold without verification

---

## ✅ CORRECT WORKFLOW

```bash
# START SESSION
cat ORCHESTRATOR_PROTOCOL.md
./check_findings.sh
cat FINDINGS_DASHBOARD.md

# DO YOUR WORK
# (following protocol guidelines)

# END SESSION
vim FINDINGS_DASHBOARD.md          # Update your section
vim findings/$(date +%Y-%m-%d)/DAILY_SUMMARY.md
git add FINDINGS_DASHBOARD.md findings/
git commit -m "[MACHINE] SESSION: Your discovery"
git push origin [your-branch]
```

---

## 🎓 KEY LEARNINGS (from previous work)

- **Puzzles 1-70**: Complex recurrence (drift ~100-125)
- **Puzzles 71-130**: PURE exponential (drift ≈ 0)
- **Phase change at n=70**: Rules CHANGE at boundaries!
- **Recurrence is UNDERDETERMINED**: Need construction algorithm
- **Don't predict**: Explore structure instead

---

## 🆘 QUICK HELP

**Where am I?**
```bash
pwd  # Should be /home/solo/LA
```

**What's the current state?**
```bash
./check_findings.sh
```

**What should I work on?**
```bash
cat FINDINGS_DASHBOARD.md | grep -A 5 "NEXT ACTIONS"
```

**How do I update the dashboard?**
```bash
vim FINDINGS_DASHBOARD.md
# Find your machine's section
# Update Status, Key Finding, Files
# Save and commit
```

---

## 📞 COORDINATION

All Claude instances must:
- Update dashboard after discoveries
- Check for conflicts before committing
- Document both successes AND failures
- Follow the integration protocol

**See ORCHESTRATOR_PROTOCOL.md for details!**

---

*If you skip these steps, you'll waste time on duplicate work!*

**Version**: 1.0
**Updated**: 2025-12-23
