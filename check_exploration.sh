#!/bin/bash
# Check status of all 6-hour exploration tasks

echo "=============================================="
echo "EXPLORATION STATUS - $(date)"
echo "=============================================="

echo ""
echo "=== MODEL STATUS ==="
echo "SPARK1 (local):" && ollama ps 2>/dev/null | grep -v "^NAME" || echo "  No models"
echo "SPARK2:" && ssh spark2 "ollama ps" 2>/dev/null | grep -v "^NAME" || echo "  No models"
echo "BOX 212:" && ssh solo@192.168.111.212 "ollama ps" 2>/dev/null | grep -v "^NAME" || echo "  No models"
echo "BOX 211:" && ssh solo@192.168.111.211 "ollama ps" 2>/dev/null | grep -v "^NAME" || echo "  No models"

echo ""
echo "=== OUTPUT FILES ==="
echo "Spark1 qwq:" && wc -l /home/solo/LA/response_spark1_qwq.txt 2>/dev/null || echo "  Not started"
echo "Spark2 phi4:" && ssh spark2 "wc -l /tmp/response_phi4.txt" 2>/dev/null || echo "  Not started"
echo "212 mixtral:" && ssh solo@192.168.111.212 "wc -l /tmp/response_mixtral.txt" 2>/dev/null || echo "  Not started"
echo "211 deepseek:" && ssh solo@192.168.111.211 "wc -l /tmp/response_deepseek.txt" 2>/dev/null || echo "  Not started"

echo ""
echo "=== LATEST OUTPUT (last 5 lines each) ==="
echo "--- Spark1 qwq ---"
tail -5 /home/solo/LA/response_spark1_qwq.txt 2>/dev/null | head -3
echo "--- 211 deepseek ---"
ssh solo@192.168.111.211 "tail -5 /tmp/response_deepseek.txt" 2>/dev/null | head -3

echo ""
echo "=============================================="
