#!/bin/bash
# Monitor autonomous exploration progress

LOG="/home/rkh/ladder/swarm_outputs/autonomous/orchestrator.log"
OUT_DIR="/home/rkh/ladder/swarm_outputs/autonomous"

echo "=========================================="
echo "EXPLORATION MONITOR - $(date)"
echo "=========================================="

# Check if process is running
PID=$(pgrep -f "wave21_orchestrator")
if [ -n "$PID" ]; then
    echo "Status: RUNNING (PID: $PID)"
    RUNTIME=$(ps -o etime= -p $PID | tr -d ' ')
    echo "Runtime: $RUNTIME"
else
    echo "Status: COMPLETED or STOPPED"
fi

# Current iteration
echo ""
echo "--- Last Log Entries ---"
tail -20 "$LOG" 2>/dev/null

# Count outputs
echo ""
echo "--- Output Files ---"
ls -la "$OUT_DIR"/*.txt 2>/dev/null | tail -10

# Check for breakthroughs
echo ""
echo "--- Breakthroughs Found ---"
grep -i "BREAKTHROUGH" "$OUT_DIR"/*.txt 2>/dev/null | head -20

# Check for hypotheses
echo ""
echo "--- Hypotheses Generated ---"
grep -i "HYPOTHESIS" "$OUT_DIR"/*.txt 2>/dev/null | head -20

echo ""
echo "=========================================="
