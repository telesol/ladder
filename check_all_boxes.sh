#!/bin/bash
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           FULL CLUSTER STATUS - $(date +%H:%M:%S)                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"

for box in "localhost:Spark1" "spark2:Spark2" "box211:Box211" "box212:Box212"; do
    host=${box%:*}
    name=${box#*:}
    echo ""
    echo "┌─ $name ────────────────────────────────────────────────────┐"
    if [ "$host" = "localhost" ]; then
        models=$(curl -s http://localhost:11434/api/ps 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(', '.join([m['name'] for m in d.get('models',[])]))" 2>/dev/null)
    else
        models=$(ssh -o ConnectTimeout=2 $host "curl -s http://localhost:11434/api/ps" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(', '.join([m['name'] for m in d.get('models',[])]))" 2>/dev/null)
    fi
    echo "│ Running: ${models:-none}"
    echo "└───────────────────────────────────────────────────────────────┘"
done

echo ""
echo "┌─ RESULT FILES ──────────────────────────────────────────────┐"
for f in /home/solo/LA/result_box211*.json /home/solo/LA/result_box212*.json; do
    [ -f "$f" ] && echo "│ $(basename $f): $(wc -c < $f) bytes"
done
echo "└───────────────────────────────────────────────────────────────┘"
