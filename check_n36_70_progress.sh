#!/bin/bash
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           N=36-70 FORMULA EXPLORATION PROGRESS               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

check_result() {
    local file=$1
    local name=$2
    local range=$3

    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        size=$(du -h "$file" | cut -f1)
        if [ "$lines" -gt 5 ]; then
            echo "✓ $name ($range): $lines lines, $size"
            echo "  Last output: $(tail -1 "$file" | head -c 60)..."
        else
            echo "⏳ $name ($range): Running... ($lines lines)"
        fi
    else
        echo "✗ $name ($range): Not started"
    fi
}

echo "┌─ TASK STATUS ─────────────────────────────────────────────────┐"
check_result "result_spark1_n36_45.txt" "Spark1 (qwq:32b)" "n=36-45"
check_result "result_spark2_n46_55.txt" "Spark2 (phi4:14b)" "n=46-55"
check_result "result_box211_n56_63.txt" "Box211 (deepseek:70b)" "n=56-63"
check_result "result_box212_n64_70.txt" "Box212 (mixtral:8x22b)" "n=64-70"
echo "└───────────────────────────────────────────────────────────────┘"

echo ""
echo "┌─ RUNNING MODELS ────────────────────────────────────────────┐"
echo "Local:"
ollama ps 2>/dev/null | head -5
echo ""
echo "Spark2:"
ssh spark2 "ollama ps" 2>/dev/null | head -3
echo "└───────────────────────────────────────────────────────────────┘"
