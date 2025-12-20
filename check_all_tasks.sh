#!/bin/bash
# Monitor all running LLM tasks

echo "============================================================"
echo "LLM TASK MONITOR - $(date)"
echo "============================================================"

echo -e "\n=== LOCAL (Spark1) OLLAMA ==="
curl -s http://localhost:11434/api/ps 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for m in d.get('models', []):
        print(f\"  {m['name']}: running\")
except: print('  No models running')
"

echo -e "\n=== SPARK2 OLLAMA ==="
ssh spark2 "curl -s http://localhost:11434/api/ps" 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for m in d.get('models', []):
        print(f\"  {m['name']}: running\")
except: print('  No models running')
"

echo -e "\n=== RESULT FILES ==="
for f in /home/solo/LA/result_*.json; do
    if [ -f "$f" ]; then
        size=$(wc -c < "$f")
        name=$(basename "$f")
        if [ "$size" -gt 100 ]; then
            echo "  ✅ $name: $size bytes (DONE)"
        else
            echo "  ⏳ $name: $size bytes (waiting)"
        fi
    fi
done
