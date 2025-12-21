#!/bin/bash
echo "=== DeepSeek Autonomous Progress ==="
echo "Log tail:"
tail -5 /home/solo/ladder/autonomous_deepseek.log 2>/dev/null || echo "No log yet"
echo ""
echo "Results so far:"
ls -la /home/solo/ladder/result_task*.txt 2>/dev/null || echo "No results yet"
echo ""
echo "Process status:"
ps aux | grep -E "autonomous_deepseek|deepseek-v3" | grep -v grep | head -3
