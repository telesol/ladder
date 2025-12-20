#!/bin/bash
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           DISTRIBUTED FACTORIZATION STATUS                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"

echo ""
echo "┌─ SPARK1 (local) - n=36-45 ───────────────────────────────────┐"
if [ -f /home/solo/LA/factorization_36_45.json ]; then
    echo "✓ COMPLETE"
    cat /home/solo/LA/factorization_36_45.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"  Factored: {d['metadata']['factored_count']}/{d['metadata']['total_values']}\")"
else
    echo "⏳ Running..."
    tail -3 /home/solo/LA/factor_spark1.log 2>/dev/null | head -2
fi
echo "└───────────────────────────────────────────────────────────────┘"

echo ""
echo "┌─ SPARK2 (10.0.0.2) - n=46-55 ────────────────────────────────┐"
if ssh spark2 "test -f /tmp/factorization_46_55.json" 2>/dev/null; then
    echo "✓ COMPLETE"
    ssh spark2 "cat /tmp/factorization_46_55.json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"  Factored: {d['metadata']['factored_count']}/{d['metadata']['total_values']}\")"
else
    echo "⏳ Running..."
    ssh spark2 "tail -3 /tmp/factor_spark2.log 2>/dev/null | head -2"
fi
echo "└───────────────────────────────────────────────────────────────┘"

echo ""
echo "┌─ BOX 211 (192.168.111.211) - n=56-63 ────────────────────────┐"
if ssh solo@192.168.111.211 "test -f /tmp/factorization_56_63.json" 2>/dev/null; then
    echo "✓ COMPLETE"
    ssh solo@192.168.111.211 "cat /tmp/factorization_56_63.json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"  Factored: {d['metadata']['factored_count']}/{d['metadata']['total_values']}\")"
else
    echo "⏳ Running..."
    ssh solo@192.168.111.211 "tail -3 /tmp/factor_box211.log 2>/dev/null | head -2"
fi
echo "└───────────────────────────────────────────────────────────────┘"

echo ""
echo "┌─ BOX 212 (192.168.111.212) - n=64-70 ────────────────────────┐"
if ssh solo@192.168.111.212 "test -f /tmp/factorization_64_70.json" 2>/dev/null; then
    echo "✓ COMPLETE"
    ssh solo@192.168.111.212 "cat /tmp/factorization_64_70.json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"  Factored: {d['metadata']['factored_count']}/{d['metadata']['total_values']}\")"
else
    echo "⏳ Running..."
    ssh solo@192.168.111.212 "tail -3 /tmp/factor_box212.log 2>/dev/null | head -2"
fi
echo "└───────────────────────────────────────────────────────────────┘"
