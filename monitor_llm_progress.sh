#!/bin/bash
# Monitor progress of LLM analysis tasks

echo "LLM Analysis Progress Monitor"
echo "=============================="
echo ""

# Check if results directory exists
if [ ! -d "llm_tasks/results" ]; then
    echo "No results directory yet. Tasks not started?"
    exit 1
fi

# Check each task
echo "Task Completion Status:"
echo ""

for i in 1 2 3 4; do
    result_file="llm_tasks/results/task${i}_*.txt"
    if ls $result_file 1> /dev/null 2>&1; then
        size=$(ls -lh $result_file | awk '{print $5}')
        lines=$(wc -l $result_file | awk '{print $1}')
        echo "  Task $i: ✓ Complete ($lines lines, $size)"
    else
        echo "  Task $i: ⏳ Running..."
    fi
done

echo ""
echo "Latest output:"
echo ""

# Show last result file being written
latest=$(ls -t llm_tasks/results/*.txt 2>/dev/null | head -1)
if [ -n "$latest" ]; then
    echo "File: $latest"
    echo ""
    tail -20 "$latest"
else
    echo "No output yet"
fi

echo ""
echo "=============================="
echo "Run this script again to check progress"
echo "Or: tail -f llm_tasks/results/task1_*.txt"
