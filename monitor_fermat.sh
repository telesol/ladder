#!/bin/bash
# Fermat Investigation - Monitor All 3 Tasks

LOG_DIR="/home/solo/LA/fermat_results"
TIMESTAMP=$(cat "$LOG_DIR/current_run.txt" 2>/dev/null || echo "unknown")

echo "============================================================"
echo "       FERMAT INVESTIGATION - TASK MONITOR"
echo "============================================================"
echo "Run timestamp: $TIMESTAMP"
echo ""

# Check all 3 processes
echo "=== PROCESS STATUS ==="

TASKS=("fermat:Box211/deepseek-r1:70b" "d71:Spark2/qwen3:32b" "mgen:Local/qwq:32b")
PIDS=("pid_fermat" "pid_d71" "pid_mgen")
FILES=("fermat_constraint" "d71_prediction" "m_generation")

for i in 0 1 2; do
    task="${TASKS[$i]}"
    pidfile="${PIDS[$i]}"
    outfile="${FILES[$i]}"

    PID=$(cat "$LOG_DIR/${pidfile}.txt" 2>/dev/null)

    if [ -n "$PID" ] && ps -p $PID > /dev/null 2>&1; then
        echo "✓ $task: RUNNING (PID $PID)"
    elif [ -n "$PID" ]; then
        echo "✗ $task: COMPLETED (PID $PID)"
    else
        echo "? $task: NOT DISPATCHED"
    fi
done

echo ""
echo "=== OUTPUT FILE SIZES ==="
ls -lh "$LOG_DIR"/*.txt 2>/dev/null | grep -v pid | grep -v current | awk '{printf "%-55s %s\n", $9, $5}'

echo ""
echo "=== LATEST OUTPUT (last 10 lines each) ==="

for i in 0 1 2; do
    outfile="${FILES[$i]}"
    task="${TASKS[$i]}"

    echo ""
    echo "--- $task ---"
    FILE="$LOG_DIR/${outfile}_${TIMESTAMP}.txt"
    if [ -f "$FILE" ]; then
        # Strip ANSI codes and show last 10 meaningful lines
        cat "$FILE" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' | grep -v '^\[' | grep -v '^$' | tail -10
    else
        echo "(no output yet)"
    fi
done

echo ""
echo "============================================================"
