#!/bin/bash
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           TASK MONITOR - $(date +%H:%M:%S)                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"

echo ""
echo "┌─ PRNG Analysis (box211 - deepseek-r1:70b) ─────────────────┐"
if [ -f /home/solo/LA/result_prng_analysis.json ]; then
    size=$(wc -c < /home/solo/LA/result_prng_analysis.json)
    if [ "$size" -gt 100 ]; then
        echo "│ ✓ Complete ($size bytes)"
    else
        echo "│ ⏳ Running..."
    fi
else
    echo "│ ⏳ Not started"
fi
echo "└───────────────────────────────────────────────────────────────┘"

echo ""
echo "┌─ Binary Structure (Spark2 - qwen3:32b) ────────────────────┐"
if [ -f /home/solo/LA/result_binary_analysis.json ]; then
    size=$(wc -c < /home/solo/LA/result_binary_analysis.json)
    if [ "$size" -gt 100 ]; then
        echo "│ ✓ Complete ($size bytes)"
    else
        echo "│ ⏳ Running..."
    fi
else
    echo "│ ⏳ Not started"
fi
echo "└───────────────────────────────────────────────────────────────┘"

echo ""
echo "┌─ Block Connection (Spark1 - qwq:32b) ──────────────────────┐"
if [ -f /home/solo/LA/result_block_analysis.json ]; then
    size=$(wc -c < /home/solo/LA/result_block_analysis.json)
    if [ "$size" -gt 100 ]; then
        echo "│ ✓ Complete ($size bytes)"
    else
        echo "│ ⏳ Running..."
    fi
else
    echo "│ ⏳ Not started"
fi
echo "└───────────────────────────────────────────────────────────────┘"

echo ""
echo "┌─ MEMORY.md Status ─────────────────────────────────────────┐"
echo "│ $(wc -l < /home/solo/LA/MEMORY.md) lines, $(wc -c < /home/solo/LA/MEMORY.md) bytes"
echo "└───────────────────────────────────────────────────────────────┘"
