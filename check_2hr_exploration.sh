#!/bin/bash
# Check status of 2-hour exploration tasks - 2025-12-19

echo "=============================================="
echo "2-HOUR EXPLORATION STATUS - $(date)"
echo "=============================================="

echo ""
echo "=== MODEL STATUS ==="
echo "SPARK1 (qwq - 19 Mystery):" && ollama ps 2>/dev/null | grep -E "qwq|NAME" || echo "  Not running"
echo "SPARK2 (phi4 - D-Sequence):" && ssh spark2 "ollama ps" 2>/dev/null | grep -E "phi4|NAME" || echo "  Not running"
echo "BOX 212 (mixtral - Bitwise):" && ssh solo@192.168.111.212 "ollama ps" 2>/dev/null | grep -E "mixtral|NAME" || echo "  Not running"
echo "BOX 211 (deepseek - Constants):" && ssh solo@192.168.111.211 "ollama ps" 2>/dev/null | grep -E "deepseek|NAME" || echo "  Not running"

echo ""
echo "=== OUTPUT FILES (lines) ==="
echo "Spark1 19-mystery:" && wc -l /home/solo/LA/response_19_mystery.txt 2>/dev/null || echo "  Not started"
echo "Spark2 d-sequence:" && ssh spark2 "wc -l /tmp/response_d_sequence.txt" 2>/dev/null || echo "  Not started"
echo "212 bitwise:" && ssh solo@192.168.111.212 "wc -l /tmp/response_bitwise.txt" 2>/dev/null || echo "  Not started"
echo "211 constants:" && ssh solo@192.168.111.211 "wc -l /tmp/response_constants.txt" 2>/dev/null || echo "  Not started"

echo ""
echo "=== LATEST OUTPUT PREVIEW ==="
echo "--- Spark1 (19-mystery) last 3 lines ---"
tail -5 /home/solo/LA/response_19_mystery.txt 2>/dev/null | tr -d '\000-\010\013\014\016-\037' | sed 's/\[?25[lh]//g' | head -3

echo ""
echo "=============================================="
