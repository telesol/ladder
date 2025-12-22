#!/bin/bash
# Monitor piecewise PySR training progress

PID=$(cat pysr_piecewise_pid.txt 2>/dev/null | grep -oP '\d+')

if [ -z "$PID" ]; then
    echo "No PID found"
    exit 1
fi

echo "======================================================================="
echo "  PIECEWISE PYSR TRAINING MONITOR"
echo "======================================================================="
echo ""
echo "PID: $PID"

if ps -p $PID > /dev/null 2>&1; then
    echo "Status: RUNNING ✅"
else
    echo "Status: COMPLETED ✓"
fi

echo ""
echo "--- Last 40 lines of log ---"
tail -40 piecewise_training.log

echo ""
echo "======================================================================="

if ps -p $PID > /dev/null 2>&1; then
    echo "Training still running. Check again with: ./monitor_piecewise.sh"
else
    echo "Training complete! Check results:"
    echo "  cat piecewise_results.json"
fi
