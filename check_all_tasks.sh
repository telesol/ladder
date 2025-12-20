#!/bin/bash
# Check status of all distributed LLM tasks

echo "=== LLM TASK STATUS CHECK ==="
echo "Time: $(date)"
echo

echo "=== Task 1: qwq:32b on Spark1 (n=17 mystery) ==="
if [ -f /home/solo/LA/result_qwq_n17.json ]; then
    SIZE=$(wc -c < /home/solo/LA/result_qwq_n17.json)
    if [ "$SIZE" -gt 100 ]; then
        echo "COMPLETE - $SIZE bytes"
        echo "First 200 chars of response:"
        cat /home/solo/LA/result_qwq_n17.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('response','')[:200])" 2>/dev/null
    else
        echo "RUNNING... ($SIZE bytes so far)"
    fi
else
    echo "NOT STARTED or file missing"
fi
echo

echo "=== Task 2: deepseek-r1:70b on Box211 (k[17-25] formulas) ==="
ssh -o ConnectTimeout=2 solo@192.168.111.211 "
if [ -f /tmp/result_deepseek_k17_25.json ]; then
    SIZE=\$(wc -c < /tmp/result_deepseek_k17_25.json)
    if [ \"\$SIZE\" -gt 100 ]; then
        echo \"COMPLETE - \$SIZE bytes\"
    else
        echo \"RUNNING... (\$SIZE bytes so far)\"
    fi
else
    echo \"NOT STARTED or file missing\"
fi
" 2>/dev/null || echo "SSH connection failed"
echo

echo "=== Task 3: phi4:14b on Spark2 (coefficient patterns) ==="
ssh -o ConnectTimeout=2 spark2 "
if [ -f /tmp/result_phi4_coefficients.json ]; then
    SIZE=\$(wc -c < /tmp/result_phi4_coefficients.json)
    if [ \"\$SIZE\" -gt 100 ]; then
        echo \"COMPLETE - \$SIZE bytes\"
    else
        echo \"RUNNING... (\$SIZE bytes so far)\"
    fi
else
    echo \"NOT STARTED or file missing\"
fi
" 2>/dev/null || echo "SSH connection failed"
echo

echo "=== Task 4: deepseek-math:7b on Box212 (meta-rule) ==="
ssh -o ConnectTimeout=2 solo@192.168.111.212 "
if [ -f /tmp/result_deepseek_math.json ]; then
    SIZE=\$(wc -c < /tmp/result_deepseek_math.json)
    if [ \"\$SIZE\" -gt 100 ]; then
        echo \"COMPLETE - \$SIZE bytes\"
    else
        echo \"RUNNING... (\$SIZE bytes so far)\"
    fi
else
    echo \"NOT STARTED or file missing\"
fi
" 2>/dev/null || echo "SSH connection failed"
echo

echo "=== END STATUS CHECK ==="
