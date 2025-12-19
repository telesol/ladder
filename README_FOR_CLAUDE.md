# 🤖 README FOR ALL CLAUDE INSTANCES

**If you're a Claude instance working on this project, READ THIS FIRST!**

---

## 🚨 **CRITICAL: COORDINATION REQUIRED**

This project has **MULTIPLE CLAUDE INSTANCES** working on **DIFFERENT BOXES** simultaneously.

**Boxes involved:**
- **SPARK1** (qwq:32b) - Hypothesis H1 testing
- **SPARK2** (phi4:14b) - Hypothesis H2 testing
- **ASUS-B10 #1** (mixtral:8x22b) - Hypothesis H3 testing
- **ASUS-B10 #2** (deepseek-r1:70b) - Hypothesis H4 testing
- **ZBOOK/DELL** (Local orchestrator) - PySR experiments, coordination

---

## ⚡ **BEFORE YOU DO ANYTHING**

### **Step 1: Read the Coordination Protocol**

```bash
cat COORDINATION_PROTOCOL.md
```

**This document explains:**
- How to sync with other boxes (pull/push protocol)
- Commit message format (use BOX-NAME prefix!)
- How to check what others are doing
- How to avoid duplicate work
- How to resolve conflicts

### **Step 2: Pull Latest Updates**

```bash
# ALWAYS pull first!
git pull origin local-work

# Check what happened recently
git log --oneline -10
```

### **Step 3: Check Current Status**

```bash
# Read latest session summary
cat last_status.md

# Read project status
cat experiments/STATUS.md

# Check for urgent updates
ls -t URGENT_UPDATE_*.md 2>/dev/null | head -3
```

### **Step 4: Run Sync Check**

```bash
# Check if you're in sync with others
./sync.sh
```

---

## 📋 **Quick Command Reference**

```bash
# START OF SESSION
git pull origin local-work          # Get latest from all boxes
cat last_status.md                  # See what was done last
./sync.sh                           # Check sync status

# DURING WORK
./sync.sh                           # Run every hour to stay synced

# END OF SESSION / AFTER COMPLETING TASK
git add .                           # Stage your changes
git commit -m "BOX-NAME: Summary"   # Commit with box prefix
git push origin local-work          # Share with other boxes
```

---

## 🎯 **Your Box Identity**

Use these prefixes in your commits so others know who did what:

| Box | Prefix | Example Commit |
|-----|--------|----------------|
| Spark 1 | `SPARK1-QWQ:` | `SPARK1-QWQ: H1 testing complete` |
| Spark 2 | `SPARK2-PHI4:` | `SPARK2-PHI4: H2 analysis failed` |
| ASUS B10 #1 | `ASUS-B10-MXT:` | `ASUS-B10-MXT: H3 partial match` |
| ASUS B10 #2 | `ASUS-B10-DS:` | `ASUS-B10-DS: H4 breakthrough!` |
| ZBook/Dell | `ZBOOK-LOCAL:` | `ZBOOK-LOCAL: PySR complete` |

**If you don't know which box you're on, ask the user!**

---

## 📊 **Project Current State**

### **Latest Breakthrough (2025-12-19)**

**From ZBOOK-LOCAL:**
- ✅ PySR training complete (3 minutes)
- ✅ **Convergent hypothesis DISPROVEN** (critical finding!)
- ✅ Simple formula discovered: `m ≈ 2^n / (n² × d_n²)`
- ✅ D-specific corrections validated (33% exact accuracy)

**Read full details:**
```bash
cat experiments/06-pysr-m-sequence/SUMMARY.md
cat experiments/06-pysr-m-sequence/DIAGNOSTIC_REPORT.md
```

### **Critical Implications**

🚨 **STOP convergent feature engineering** - Proven to be useless!
✅ **Use simple features only** - power_of_2, n, d_n
✅ **Try piecewise models** - Separate model per d_n group

---

## 🔍 **How to Check What Others Are Doing**

```bash
# See all recent commits
git log --oneline --all -20

# See what a specific box did
git log --oneline --all --grep="SPARK1"

# See activity in last 24 hours
git log --oneline --all --since="24 hours ago"

# Run the sync script
./sync.sh
```

---

## ⚠️ **IMPORTANT RULES**

### **DO:**
✅ **PULL before starting work** - `git pull origin local-work`
✅ **PUSH after completing tasks** - `git push origin local-work`
✅ **Use box prefix in commits** - `BOXNAME: message`
✅ **Check sync every hour** - `./sync.sh`
✅ **Read others' findings** - Don't duplicate work!

### **DON'T:**
❌ Work for hours without pulling/pushing
❌ Use vague commit messages
❌ Ignore what other boxes are doing
❌ Skip reading URGENT_UPDATE_*.md files
❌ Modify files another box is working on

---

## 📁 **Important Files to Know**

| File | Purpose | When to Read |
|------|---------|--------------|
| `COORDINATION_PROTOCOL.md` | **Full sync protocol** | **READ FIRST!** |
| `last_status.md` | Latest session summary | Every session start |
| `experiments/STATUS.md` | All experiments status | Before starting new work |
| `URGENT_UPDATE_*.md` | Critical findings | Check every hour |
| `CLAUDE.md` | Project documentation | For context |
| `sync.sh` | Auto-sync checker | Run every hour |

---

## 🚀 **Typical Session Workflow**

```bash
# 1. START
cd /home/solo/LadderV3/kh-assist
git pull origin local-work
cat last_status.md
./sync.sh

# 2. CHECK FOR URGENT UPDATES
ls URGENT_UPDATE_*.md

# 3. WORK ON YOUR TASK
# (Do your research, run experiments, etc.)

# 4. SYNC DURING WORK (every hour)
./sync.sh

# 5. SAVE YOUR WORK
git add [your files]
git commit -m "BOXNAME: What you did

Details:
- Finding 1
- Finding 2

Status: COMPLETE
Next: What's next"

# 6. SHARE WITH OTHERS
git push origin local-work

# 7. UPDATE STATUS (if you're the coordinator)
# Edit last_status.md with your findings
```

---

## 🆘 **Common Questions**

### **Q: Which box am I on?**
**A:** Ask the user! Then use the correct prefix from the table above.

### **Q: What if I get merge conflicts?**
**A:** See "Conflict Resolution" section in COORDINATION_PROTOCOL.md

### **Q: How do I know if someone else is working right now?**
**A:** Run `git log --since="1 hour ago"` or `./sync.sh`

### **Q: What if I discover something urgent?**
**A:** Create `URGENT_UPDATE_YYYYMMDD_HHMM.md` with your findings and push immediately!

### **Q: Can I work on the same file as another box?**
**A:** Check `git log -- [filename]` first. If someone worked on it recently, coordinate with user.

---

## 📞 **Need Help?**

1. Read `COORDINATION_PROTOCOL.md` - Most questions answered there
2. Run `./sync.sh` - Shows current status and common commands
3. Check `git log` - See what others did
4. Ask the user - They coordinate all boxes

---

## ✅ **Quick Checklist**

Before you start working:
- [ ] `git pull origin local-work`
- [ ] Read `last_status.md`
- [ ] Run `./sync.sh`
- [ ] Check for `URGENT_UPDATE_*.md` files
- [ ] Know your box identity (ask user if unsure)

After you finish working:
- [ ] `git add [your files]`
- [ ] `git commit -m "BOXNAME: ..."`
- [ ] `git push origin local-work`
- [ ] Run `./sync.sh` to confirm push succeeded

---

**NOW GO READ:** `COORDINATION_PROTOCOL.md` for full details!

**REMEMBER:** We're all working together on this. Communication through Git is essential!

🤝 **Good luck, fellow Claude instance!**
