#!/bin/bash
# N17 Investigation - Parallel Dispatch Script
# Dispatches tasks to available compute nodes

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="/home/solo/LA/n17_results"
mkdir -p "$LOG_DIR"

echo "=== N17 INVESTIGATION DISPATCH ==="
echo "Timestamp: $TIMESTAMP"
echo ""

# Task B - Local qwq:32b (THE BREAKPOINT - most critical)
echo "Dispatching Task B (Breakpoint) to local qwq:32b..."
nohup bash -c '
cat /home/solo/LA/N17_TASK_B_BREAKPOINT.txt | ollama run qwq:32b --verbose 2>&1
' > "$LOG_DIR/task_b_breakpoint_$TIMESTAMP.txt" 2>&1 &
PID_B=$!
echo "Task B PID: $PID_B"

# Task A - Spark2 qwen3:32b (BEFORE n=17)
echo "Dispatching Task A (Before) to Spark2 qwen3:32b..."
nohup ssh solo@10.0.0.2 "cat /dev/stdin | ollama run qwen3:32b --verbose" < /home/solo/LA/N17_TASK_A_BEFORE.txt > "$LOG_DIR/task_a_before_$TIMESTAMP.txt" 2>&1 &
PID_A=$!
echo "Task A PID: $PID_A"

echo ""
echo "=== DISPATCH COMPLETE ==="
echo "Task A (Before): Spark2/qwen3:32b - PID $PID_A"
echo "Task B (Breakpoint): Local/qwq:32b - PID $PID_B"
echo ""
echo "Monitor with:"
echo "  tail -f $LOG_DIR/task_a_before_$TIMESTAMP.txt"
echo "  tail -f $LOG_DIR/task_b_breakpoint_$TIMESTAMP.txt"
echo ""
echo "Remaining tasks (run after these complete):"
echo "  Task C (After): Spark2/phi4-reasoning:14b"
echo "  Task D (Why17): Spark2/nemotron:30b"

# Save PIDs for monitoring
echo "$PID_A" > "$LOG_DIR/pid_task_a.txt"
echo "$PID_B" > "$LOG_DIR/pid_task_b.txt"
echo "$TIMESTAMP" > "$LOG_DIR/current_run.txt"
