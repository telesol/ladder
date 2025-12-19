# 🤝 Multi-Claude Coordination Protocol
## For Distributed Work on Ladder Project

**Repository:** `github.com/telesol/ladder`
**Branch:** `local-work` (main collaboration branch)

---

## 🔄 **THE GOLDEN RULE**

### **BEFORE YOU START: PULL**
### **AFTER YOU FINISH: PUSH**
### **EVERY HOUR: SYNC**

---

## 📋 **Quick Start Commands**

### **1. When Starting a New Session**

```bash
cd /home/solo/LadderV3/kh-assist  # Or wherever your repo is

# ALWAYS pull first!
git pull origin local-work

# Check what others have done
git log --oneline -10

# Read latest findings
cat experiments/06-pysr-m-sequence/SUMMARY.md
cat last_status.md
```

### **2. During Your Work**

```bash
# Every hour, check for updates
git fetch origin
git status

# If others pushed, merge their work
git pull origin local-work

# If conflicts, see CONFLICT RESOLUTION below
```

### **3. When You Complete a Task**

```bash
# Stage your changes
git add .

# Commit with clear message (see template below)
git commit -m "BOX-NAME: What you did

Details:
- Specific finding 1
- Specific finding 2

Status: COMPLETE/IN_PROGRESS
Next: What to do next"

# Push immediately!
git push origin local-work
```

---

## 🏷️ **Commit Message Format**

Use this template for **all** commits:

```
BOX-NAME: Brief summary (50 chars max)

Details:
- What you discovered/changed
- Key findings or results
- Any blockers or issues

Status: COMPLETE | IN_PROGRESS | BLOCKED
Next: What should happen next
Files: list of important files

See [filename.md] for full details.
```

### **Examples:**

```
SPARK1-QWQ32B: H1 index-based hypothesis - NO MATCH

Details:
- Tested 15 polynomial patterns
- Tested 8 modular arithmetic formulas
- Best accuracy: 12% (polynomial degree 4)

Status: COMPLETE
Next: Try H4 recursive patterns instead
Files: research_H1_results.json, H1_REPORT.md

See H1_REPORT.md for full analysis.
```

```
ASUS-B10-PHI4: PySR piecewise d=1 group - 80% SUCCESS!

Details:
- Trained PySR on d=1 group only (15 samples)
- Found formula: m ≈ 2^n / (n^1.8)
- Validation: 12/15 exact matches (80%)

Status: COMPLETE
Next: Try d=2 and d=4 groups
Files: experiments/07-piecewise-pysr/d1_results.json

See experiments/07-piecewise-pysr/D1_REPORT.md
```

---

## 📦 **Box Naming Convention**

Use these prefixes for your commits:

| Box | Model | Prefix | Example |
|-----|-------|--------|---------|
| Spark 1 | qwq:32b | `SPARK1-QWQ` | `SPARK1-QWQ: H1 analysis complete` |
| Spark 2 | phi4:14b | `SPARK2-PHI4` | `SPARK2-PHI4: H2 hash test failed` |
| ASUS B10 #1 | mixtral:8x22b | `ASUS-B10-MXT` | `ASUS-B10-MXT: H3 PRNG partial match` |
| ASUS B10 #2 | deepseek-r1:70b | `ASUS-B10-DS` | `ASUS-B10-DS: H4 recursive breakthrough!` |
| ZBook (Dell) | Local (you) | `ZBOOK-LOCAL` | `ZBOOK-LOCAL: PySR convergent disproven` |

---

## 🔍 **Checking What Others Are Doing**

### **See Recent Activity**

```bash
# Last 10 commits from all boxes
git log --oneline --all -10

# See what each box is working on
git log --oneline --all --grep="SPARK1"
git log --oneline --all --grep="ASUS-B10"

# See recent changes to specific files
git log --oneline -- experiments/06-pysr-m-sequence/
```

### **Check Current Status**

```bash
# Read status files
cat STATUS.md                    # Overall project status
cat last_status.md               # Latest session summary
cat experiments/STATUS.md        # Experiment progress

# Check if others are working right now
git log --since="1 hour ago"
```

---

## ⚠️ **Conflict Resolution**

If you see: `CONFLICT (content): Merge conflict in [file]`

### **Option 1: Keep Both Changes (Recommended)**

```bash
# Open the conflicting file
nano [conflicted_file]

# You'll see:
<<<<<<< HEAD
Your changes
=======
Their changes
>>>>>>> origin/local-work

# Edit to combine both (remove markers, keep both)

# Then:
git add [conflicted_file]
git commit -m "BOX-NAME: Merged changes from [other box]"
git push origin local-work
```

### **Option 2: Ask User**

If the conflict is complex:
```bash
git merge --abort  # Cancel the merge
# Ask user which version to keep
```

---

## 📊 **Coordination Scripts**

### **sync.sh** - Auto-sync script (run every hour)

```bash
#!/bin/bash
# Save as: sync.sh

echo "=== SYNC CHECK $(date) ==="

cd /home/solo/LadderV3/kh-assist

# Fetch updates
git fetch origin

# Check if behind
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "⚠️  NEW UPDATES FROM OTHER BOXES!"
    echo ""
    echo "Recent commits:"
    git log --oneline HEAD..@{u}
    echo ""
    echo "Run: git pull origin local-work"
else
    echo "✅ You're up to date"
fi

# Check uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  You have uncommitted changes!"
    echo "Run: git add . && git commit -m '...' && git push"
fi

echo "==========================="
```

**Usage:**
```bash
chmod +x sync.sh
./sync.sh  # Run manually

# Or set up cron (every hour)
crontab -e
# Add: 0 * * * * /home/solo/LadderV3/kh-assist/sync.sh >> /tmp/sync.log 2>&1
```

---

## 🎯 **Workflow Example**

### **Box: SPARK1 (User starts you on hypothesis H1)**

```bash
# 1. START: Pull latest
git pull origin local-work

# 2. CHECK: What are others doing?
git log --oneline -5
cat experiments/06-pysr-m-sequence/SUMMARY.md  # Read: convergents disproven!

# 3. WORK: Run your task
python3 research_H1_index_based.py

# 4. COMMIT: Save your findings
git add research_H1_results.json H1_REPORT.md
git commit -m "SPARK1-QWQ: H1 index-based complete - no match (12%)

Details:
- Tested 15 polynomial patterns
- Tested 8 modular formulas
- Best: 12% accuracy (poly degree 4)
- Conclusion: Index-based approach insufficient

Status: COMPLETE
Next: Skip H1, try H4 recursive instead
Files: research_H1_results.json, H1_REPORT.md"

# 5. PUSH: Share with others
git push origin local-work

# 6. SYNC: Check every hour
# (Run sync.sh via cron)
```

---

## 📢 **Broadcasting Important Findings**

When you discover something **critical**, create a broadcast file:

```bash
# Create urgent update
cat > URGENT_UPDATE_$(date +%Y%m%d_%H%M).md << 'EOF'
# 🚨 URGENT: [Your Discovery]

**Box:** SPARK1-QWQ
**Date:** 2025-12-19 23:00
**Priority:** HIGH

## Discovery

[What you found]

## Impact

[How this affects other boxes]

## Action Required

- [ ] Box Spark2: Stop H2 hash tests, try H4 instead
- [ ] Box ASUS-B10-1: Pivot to piecewise approach
- [ ] Box ASUS-B10-2: Continue current work

## Details

See [your_report.md] for full analysis.
EOF

git add URGENT_UPDATE_*.md
git commit -m "🚨 URGENT: [Brief summary]"
git push origin local-work
```

---

## 📅 **Daily Sync Protocol**

### **Morning (Start of Session)**

```bash
git pull origin local-work
cat URGENT_UPDATE_*.md 2>/dev/null | tail -100
git log --oneline --since="24 hours ago"
```

### **Hourly (During Work)**

```bash
./sync.sh  # Auto-check for updates
```

### **Evening (End of Session)**

```bash
# Save all work
git add .
git commit -m "BOX-NAME: End of day checkpoint

Progress:
- [List what you did]

Status: IN_PROGRESS
Next: [What to do tomorrow]"

git push origin local-work
```

---

## 🛠️ **Setup Instructions**

### **First Time Setup (Run Once Per Box)**

```bash
cd /home/solo/LadderV3/kh-assist

# Configure Git identity
git config user.name "Claude on [BoxName]"
git config user.email "claude@[boxname].local"

# Set up remote (if not already done)
git remote add origin git@github.com:telesol/ladder.git

# Fetch latest
git fetch origin

# Create/switch to collaboration branch
git checkout -b local-work origin/local-work || git checkout local-work

# Create sync script
cat > sync.sh << 'SYNCEOF'
#!/bin/bash
echo "=== SYNC CHECK $(date) ==="
cd /home/solo/LadderV3/kh-assist
git fetch origin
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
if [ "$LOCAL" != "$REMOTE" ]; then
    echo "⚠️  NEW UPDATES FROM OTHER BOXES!"
    git log --oneline HEAD..@{u}
    echo "Run: git pull origin local-work"
else
    echo "✅ Up to date"
fi
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Uncommitted changes! Push when ready."
fi
SYNCEOF

chmod +x sync.sh

# Test it
./sync.sh
```

---

## ✅ **Checklist for Every Session**

```
Session Start:
[ ] git pull origin local-work
[ ] Read git log --oneline -10
[ ] Check URGENT_UPDATE_*.md files
[ ] Read last_status.md and SUMMARY.md

During Work:
[ ] Run ./sync.sh every hour
[ ] Commit logical chunks (not everything at once)
[ ] Use clear commit messages with BOX prefix

Session End:
[ ] git add [all your files]
[ ] git commit -m "BOX-NAME: [clear message]"
[ ] git push origin local-work
[ ] Update last_status.md if you're the coordinator
```

---

## 🎓 **Best Practices**

### **DO:**
✅ Pull before starting work
✅ Push after completing each task
✅ Use descriptive commit messages with box prefix
✅ Check for updates every hour
✅ Read others' findings before duplicating work
✅ Create URGENT_UPDATE_*.md for critical discoveries
✅ Commit working code/data (even if incomplete)

### **DON'T:**
❌ Work for hours without pushing
❌ Commit broken code without explanation
❌ Ignore conflicts (resolve them immediately)
❌ Use vague messages like "update" or "fix"
❌ Push binary files > 10MB without asking
❌ Modify others' files without checking with user

---

## 🆘 **Common Issues**

### **"I forgot to pull and now I have conflicts"**

```bash
# Save your work
git stash

# Pull latest
git pull origin local-work

# Restore your work
git stash pop

# If conflicts, resolve manually
# Then: git add . && git commit && git push
```

### **"Other box pushed while I was working"**

```bash
# Commit your work first
git add .
git commit -m "BOX-NAME: Work in progress"

# Pull with merge
git pull origin local-work

# Push merged result
git push origin local-work
```

### **"I need to see what Box X is doing RIGHT NOW"**

```bash
git fetch origin
git log --oneline --author="Box X" -5
git show HEAD  # See their latest commit details
```

---

## 📞 **Communication Channels**

Since Claude instances can't talk directly:

1. **Git commits** - Primary communication (use detailed messages)
2. **URGENT_UPDATE_*.md** - For critical findings
3. **STATUS.md** - Overall project status
4. **last_status.md** - Latest session summary
5. **Individual reports** - Each experiment creates its own report

---

## 🎯 **Success Metrics**

You're doing it right if:
- ✅ All boxes pull before starting
- ✅ All boxes push after finishing tasks
- ✅ No work duplication (boxes check what others did)
- ✅ Critical findings shared within 1 hour
- ✅ Merge conflicts are rare (< 1 per day)
- ✅ Everyone knows what everyone else is doing

---

## 📝 **Template Files**

### **last_status.md** (Update at end of each session)

```markdown
# Last Session Status
**Date:** 2025-12-19
**Box:** ZBOOK-LOCAL

## What We Did
- Ran PySR training on m-sequence
- Disproved convergent hypothesis
- Achieved 33% accuracy with d-specific corrections

## Key Findings
- Convergents are useless (PySR ignored all 240 features)
- Simple formula works: 2^n / (n² × d_n²)
- D-specific corrections get exact matches

## Next Steps
- HIGH: Piecewise PySR by d_n groups
- HIGH: Simplify features to 8-10 basic
- MEDIUM: Hybrid approach

## Files Updated
- experiments/06-pysr-m-sequence/SUMMARY.md
- experiments/06-pysr-m-sequence/DIAGNOSTIC_REPORT.md

## For Other Boxes
- STOP convergent feature work (proven wrong)
- TRY piecewise models instead
- READ experiments/06-pysr-m-sequence/SUMMARY.md
```

---

**This protocol ensures all Claude instances stay synchronized and avoid duplicating work!**

**Print this and keep it visible when working on the project.**
