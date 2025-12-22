#!/bin/bash
# N17 Investigation - Monitor All 4 Tasks

LOG_DIR="/home/solo/LA/n17_results"
TIMESTAMP=$(cat "$LOG_DIR/current_run.txt" 2>/dev/null || echo "unknown")

echo "============================================================"
echo "       N17 INVESTIGATION - PARALLEL TASK MONITOR"
echo "============================================================"
echo "Run timestamp: $TIMESTAMP"
echo ""

# Check all 4 processes
echo "=== PROCESS STATUS ==="
for task in a b c d; do
    PID=$(cat "$LOG_DIR/pid_task_$task.txt" 2>/dev/null)
    TASK_NAME=""
    case $task in
        a) TASK_NAME="Task A (Before n=17)" ;;
        b) TASK_NAME="Task B (Breakpoint)" ;;
        c) TASK_NAME="Task C (After n=17)" ;;
        d) TASK_NAME="Task D (Why 17?)" ;;
    esac

    if [ -n "$PID" ] && ps -p $PID > /dev/null 2>&1; then
        echo "✓ $TASK_NAME: RUNNING (PID $PID)"
    elif [ -n "$PID" ]; then
        echo "✗ $TASK_NAME: COMPLETED (PID $PID)"
    else
        echo "? $TASK_NAME: NOT DISPATCHED"
    fi
done

echo ""
echo "=== OUTPUT FILE SIZES ==="
ls -lh "$LOG_DIR"/task_*.txt 2>/dev/null | awk '{printf "%-50s %s\n", $9, $5}'

echo ""
echo "=== TASK ASSIGNMENTS ==="
echo "Task A: Spark2 / qwen3:32b"
echo "Task B: Local / qwq:32b"
echo "Task C: Box211 / devstral-small-2:24b"
echo "Task D: Box212 / mixtral:8x22b"

echo ""
echo "=== LATEST OUTPUT (last 5 lines each) ==="

for task in a b c d; do
    TASK_NAME=""
    FILE_PATTERN=""
    case $task in
        a) TASK_NAME="Task A (Before)"; FILE_PATTERN="task_a_before" ;;
        b) TASK_NAME="Task B (Breakpoint)"; FILE_PATTERN="task_b_breakpoint" ;;
        c) TASK_NAME="Task C (After)"; FILE_PATTERN="task_c_after" ;;
        d) TASK_NAME="Task D (Why17)"; FILE_PATTERN="task_d_why17" ;;
    esac

    echo ""
    echo "--- $TASK_NAME ---"
    FILE="$LOG_DIR/${FILE_PATTERN}_${TIMESTAMP}.txt"
    if [ -f "$FILE" ]; then
        # Strip ANSI codes and show last 5 meaningful lines
        cat "$FILE" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' | grep -v '^\[' | grep -v '^$' | tail -5
    else
        echo "(no output yet)"
    fi
done

echo ""
echo "============================================================"
