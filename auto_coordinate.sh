#!/bin/bash
# Automated Claude Coordination System
# Enables non-stop collaborative research across multiple Claude instances

COORD_DIR="llm_tasks/coordination"
MEMORY_DIR="llm_tasks/memory"
RESULTS_DIR="llm_tasks/results"

mkdir -p "$COORD_DIR"

echo "========================================"
echo "AUTOMATED CLAUDE COORDINATION"
echo "========================================"
echo ""
echo "Instance: $(hostname)"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Step 1: Pull latest from other Claudes
echo "STEP 1: Syncing with other Claude instances..."
git pull origin local-work --no-edit > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Synced successfully"
else
    echo "⚠️  Sync failed (may need manual intervention)"
fi
echo ""

# Step 2: Check what's been done
echo "STEP 2: Analyzing completed work..."
LATEST_FINDINGS="$MEMORY_DIR/LATEST_FINDINGS_2025-12-21.md"
if [ -f "$LATEST_FINDINGS" ]; then
    echo "✅ Latest findings available"
    # Extract current status
    grep -A 5 "CURRENT PRIORITY" "$LATEST_FINDINGS" | head -7
else
    echo "⚠️  No recent findings document"
fi
echo ""

# Step 3: Identify uncovered areas
echo "STEP 3: Identifying research gaps..."
echo ""
echo "COMPLETED AREAS (from git log):"
git log --oneline -20 | grep -E "✅|🎯|📊" | head -10
echo ""

echo "PRIORITY TASKS (from coordination):"
if [ -f "CLAUDE_COORDINATION_2025-12-21.md" ]; then
    grep -A 10 "Remaining Open Questions" "CLAUDE_COORDINATION_2025-12-21.md" | grep "^[0-9]" | head -5
fi
echo ""

# Step 4: Check running tasks
echo "STEP 4: Checking active background tasks..."
RUNNING_COUNT=$(ps aux | grep -E "ollama run" | grep -v grep | wc -l)
echo "Active LLM tasks: $RUNNING_COUNT"
if [ $RUNNING_COUNT -gt 0 ]; then
    echo "Tasks running:"
    ps aux | grep -E "ollama run" | grep -v grep | awk '{print "  -", $NF}'
fi
echo ""

# Step 5: Suggest next tasks
echo "STEP 5: Recommended next actions..."
echo ""

# Check if m-selection is fixed
if [ ! -f "$RESULTS_DIR/m_selection_fixed.txt" ]; then
    echo "🔧 HIGH PRIORITY: Fix m-selection implementation"
    echo "   File: llm_tasks/task20_master_formula_FINAL_FIX.py"
    echo "   Bug: Returns m=0 instead of m≈15.82×10^27"
    echo ""
fi

# Check if PRNG hypothesis explored
if [ ! -f "$RESULTS_DIR/prng_m_values_explored.txt" ]; then
    echo "🔍 RESEARCH: Explore PRNG for m-value generation"
    echo "   Hypothesis: H3 (69.2%) + H4 (70.5%) suggest pattern"
    echo "   Test: Can PRNG generate m-sequence?"
    echo ""
fi

# Check if bridges k135-k160 calculated
if [ ! -f "$RESULTS_DIR/bridges_k135_k160_calculated.txt" ]; then
    echo "🎯 VALIDATION: Calculate bridges k135-k160"
    echo "   Once m-selection fixed, test on high bridges"
    echo "   Expected: 100% accuracy"
    echo ""
fi

# Step 6: Auto-assign tasks based on instance
echo "STEP 6: Instance-specific assignment..."
HOSTNAME=$(hostname)
case "$HOSTNAME" in
    *zbook*|*ZBook*)
        echo "📍 Instance: ZBook (Implementation & Testing)"
        echo "   → Debug m-selection algorithm"
        echo "   → Test fixes on bridges"
        echo "   → Verify 100% accuracy"
        ;;
    *spark*|*Spark*)
        echo "📍 Instance: Spark (PRNG Research)"
        echo "   → Explore PRNG for m-values"
        echo "   → Test LCG/MT19937 patterns"
        echo "   → Combine PRNG + Master Formula"
        ;;
    *dell*|*Dell*|*ASUS*|*B10*)
        echo "📍 Instance: Dell/ASUS (Mathematical Theory)"
        echo "   → Number theory analysis of m"
        echo "   → Prove m-selection correctness"
        echo "   → Bridge construction patterns"
        ;;
    *)
        echo "📍 Instance: Unknown (General Research)"
        echo "   → Pick highest priority uncovered task"
        echo "   → Coordinate with other instances"
        ;;
esac
echo ""

# Step 7: Create task queue file
echo "STEP 7: Creating task queue..."
QUEUE_FILE="$COORD_DIR/task_queue_$(date +%Y%m%d_%H%M%S).json"
cat > "$QUEUE_FILE" << 'EOF'
{
  "timestamp": "$(date -Iseconds)",
  "instance": "$(hostname)",
  "priority_tasks": [
    {
      "id": "M1",
      "priority": 1,
      "title": "Fix m-selection implementation",
      "status": "pending",
      "assigned_to": "ZBook",
      "file": "llm_tasks/task20_master_formula_FINAL_FIX.py",
      "estimated_time": "2-4 hours"
    },
    {
      "id": "P1",
      "priority": 2,
      "title": "PRNG hypothesis for m-values",
      "status": "pending",
      "assigned_to": "Spark",
      "estimated_time": "3-5 hours"
    },
    {
      "id": "T1",
      "priority": 3,
      "title": "Number theory analysis of m",
      "status": "pending",
      "assigned_to": "Dell",
      "estimated_time": "2-3 hours"
    },
    {
      "id": "V1",
      "priority": 4,
      "title": "Validate k135-k160 with fixed formula",
      "status": "blocked_by": ["M1"],
      "assigned_to": "ZBook",
      "estimated_time": "1-2 hours"
    }
  ],
  "coordination_notes": "All instances should sync before starting new tasks"
}
EOF
echo "✅ Queue created: $QUEUE_FILE"
echo ""

# Step 8: Summary
echo "========================================"
echo "COORDINATION SUMMARY"
echo "========================================"
echo "Status: Ready for next research cycle"
echo "Latest sync: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Active tasks: $RUNNING_COUNT"
echo "Priority: Fix m-selection (HIGH)"
echo ""
echo "To start next cycle:"
echo "  1. Review: cat CLAUDE_COORDINATION_2025-12-21.md"
echo "  2. Check: cat $LATEST_FINDINGS"
echo "  3. Begin: Work on assigned priority task"
echo "  4. Update: Push findings to GitHub when done"
echo ""
echo "For continuous coordination:"
echo "  watch -n 300 ./auto_coordinate.sh  # Check every 5 min"
echo "========================================"
