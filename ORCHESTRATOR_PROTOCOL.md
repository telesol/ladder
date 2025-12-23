# 🤖 ORCHESTRATOR PROTOCOL

**FOR ALL CLAUDE INSTANCES: READ THIS FIRST!**

---

## 🎯 MANDATORY WORKFLOW

### **BEFORE Starting ANY Work:**

1. **CHECK FINDINGS DASHBOARD**
   ```bash
   ./check_findings.sh
   # OR
   cat FINDINGS_DASHBOARD.md
   ```

2. **READ DAILY SUMMARY**
   ```bash
   cat findings/$(date +%Y-%m-%d)/DAILY_SUMMARY.md
   ```

3. **PULL LATEST FROM ALL BRANCHES**
   ```bash
   git fetch --all
   git log --all --oneline --graph -10
   ```

### **DURING Work:**

4. **UPDATE DASHBOARD** when you make a discovery
   - Edit `FINDINGS_DASHBOARD.md`
   - Add your machine's section
   - Update integration status

5. **CREATE DAILY SUMMARY** if it doesn't exist
   ```bash
   mkdir -p findings/$(date +%Y-%m-%d)
   # Create DAILY_SUMMARY.md with your findings
   ```

6. **ORGANIZE YOUR FILES** in the findings directory
   ```bash
   mkdir -p findings/$(date +%Y-%m-%d)/{machine_name}_work/
   # Put all your outputs there
   ```

### **AFTER Work:**

7. **COMMIT TO APPROPRIATE BRANCH**
   ```bash
   git add FINDINGS_DASHBOARD.md findings/
   git commit -m "Session summary: [your discovery]"
   git push origin [your-branch]
   ```

8. **UPDATE TODO LIST**
   - Mark completed tasks
   - Add new tasks discovered
   - Update integration status

---

## 🖥️ MACHINE ASSIGNMENTS

| Machine | Claude Instance | Primary Role | Branch |
|---------|-----------------|--------------|---------|
| **Zbook** | Claude Sonnet 4.5 | Deep Analysis, Formula Discovery | `local-work` |
| **Victus** | Claude Opus 4.5 | Wave Analysis, Dataset Curation | `main` |
| **LA** | Claude Opus 4.5 (YOU) | Orchestration, PySR, Integration | `main` |
| **Dell** | Claude Sonnet 3.5 | Validation, Cross-checking | `dell-validation` |

---

## 📋 STANDARD COMMIT MESSAGE FORMAT

```
[MACHINE] [TYPE]: Brief description

Discovery: [What you found]
Method: [How you found it]
Verification: [How you verified it]
Impact: [What this means]

Files:
- file1.md
- file2.json

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**: `DISCOVERY`, `ANALYSIS`, `VALIDATION`, `INTEGRATION`, `UPDATE`

---

## 🚨 CRITICAL RULES

### ❌ NEVER DO THIS:
1. **Start work without checking dashboard**
2. **Make discoveries without updating dashboard**
3. **Commit without updating findings/**
4. **Duplicate work another machine already did**
5. **Use absolute conclusions without verification**

### ✅ ALWAYS DO THIS:
1. **Read FINDINGS_DASHBOARD.md first**
2. **Check for conflicts with other machines**
3. **Verify findings before committing**
4. **Update integration status**
5. **Cross-reference with CLAUDE.md for history**

---

## 🔄 INTEGRATION PROTOCOL

When you discover something that **conflicts** with another machine's findings:

1. **DON'T override** - flag it in dashboard
2. **Create integration task** in findings/
3. **Tag it** with `[CONFLICT]` in commit message
4. **Wait for orchestrator** to reconcile
5. **Document both findings** until resolved

---

## 📊 DASHBOARD UPDATE TEMPLATE

```markdown
### 🖥️ [MACHINE NAME] ([BRANCH])
**Latest Commit**: `[hash]` - [description]
**Status**: ✅/⏳/❌ [status]
**Key Finding**: [One-line summary]
**Files**:
- file1.md - [description]
- file2.json - [description]

**Impact**: [What this enables]
```

---

## 🎯 QUICK REFERENCE

**Check Status:**
```bash
./check_findings.sh
```

**Start New Session:**
```bash
git fetch --all
cat FINDINGS_DASHBOARD.md
cat findings/$(date +%Y-%m-%d)/DAILY_SUMMARY.md 2>/dev/null || echo "No summary yet"
```

**End Session:**
```bash
# Update dashboard
vim FINDINGS_DASHBOARD.md

# Create/update daily summary
vim findings/$(date +%Y-%m-%d)/DAILY_SUMMARY.md

# Commit
git add FINDINGS_DASHBOARD.md findings/
git commit -m "[MACHINE] SESSION: Summary"
git push origin [branch]
```

---

## 💡 TIPS FOR CLAUDE INSTANCES

1. **Use TodoWrite tool** to track your work
2. **Reference previous waves** in CLAUDE.md (items 1-82)
3. **Check for BREAKTHROUGH/CRITICAL tags** in git log
4. **Validate with multiple methods** before claiming discovery
5. **Document failures too** - they're valuable information

---

## 🔗 INTEGRATION CHECKPOINTS

Before marking anything as ✅ INTEGRATED:

- [ ] Verified by at least 2 machines
- [ ] Documented in FINDINGS_DASHBOARD.md
- [ ] Added to CLAUDE.md if major discovery
- [ ] Files organized in findings/
- [ ] No conflicts with existing findings
- [ ] Peer review completed

---

## 🎓 LEARNING FROM HISTORY

**Key Lessons from Previous Waves:**

1. **Wave 15**: Recurrence is UNDERDETERMINED - need construction, not just formula
2. **Wave 16**: Construction thinking > Prediction thinking
3. **Wave 17**: Phase change at n=70 - rules CHANGE at boundaries
4. **PySR (LA)**: Patterns are complex for n<70, simple for n>70

**DON'T repeat these mistakes:**
- Assuming pattern holds without verification
- Extrapolating without understanding boundaries
- Ignoring phase changes
- Working in isolation without checking dashboard

---

*This protocol is MANDATORY for all Claude instances. Failure to follow = wasted work and conflicts!*

**Version**: 1.0
**Last Updated**: 2025-12-23
**Next Review**: When conflicts occur
