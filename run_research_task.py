#!/usr/bin/env python3
"""
Research task runner for m[71] discovery.
Sends focused queries to LLMs and logs results.
"""

import json
import subprocess
import sys
import time
from datetime import datetime

def query_llm(model, prompt, max_tokens=2000):
    """Query an LLM and return the response."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": max_tokens}
    }

    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "http://localhost:11434/api/generate",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=120
        )
        response = json.loads(result.stdout)
        return response.get("response", "ERROR: No response")
    except Exception as e:
        return f"ERROR: {str(e)}"

def log_result(task_id, model, result):
    """Log result to file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("RESEARCH_RESULTS.md", "a") as f:
        f.write(f"\n## {task_id} - {model} - {timestamp}\n\n")
        f.write(result)
        f.write("\n\n---\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_research_task.py <task_id> <model>")
        sys.exit(1)

    task_id = sys.argv[1]
    model = sys.argv[2]

    # Task definitions
    tasks = {
        "T01": """Analyze these initial pairs for generalized Fibonacci sequences:
- G(189, 92): appears in m[62], indices 2,3
- G(101, 81): appears in m[68], indices 6,7

Properties:
- 189 = 3³×7 = 27×7
- 92 = 2²×23 = 4×23
- 101 is prime
- 81 = 3⁴

Questions:
1. What mathematical relationship connects 189,92 to 101,81?
2. Is there a pattern in the prime factorizations?
3. How do these relate to n=62 and n=68?

Show calculations.""",

        "T02": """Check if m-values for n=50,53,56,59 contain consecutive generalized Fibonacci pairs.

m[50] = 1332997220739910
m[53] = 10676506562464268
m[56] = 87929632728990281
m[59] = 451343703997841395

For each: Factor the number and check if any two factors a,b satisfy a+prev=b for some sequence.

Report any findings.""",

        "T03": """Given two data points for a(n):
- n=62: a=189
- n=68: a=101

The linear formula a(n) = -44n/3 + 3295/3 gives a(71)=57.

But maybe a(n) follows a different pattern:
1. Check if a(n) = floor(c₁/n) for some constant
2. Check if a(n) = c₂ × φ^(-n/k) for some constants
3. Check if a(n) relates to prime(n) or Fibonacci(n)

Find a formula that gives integer outputs for all n.""",

        "T04": """Given two data points for b(n):
- n=62: b=92
- n=68: b=81

The linear formula gives b(71)=75.5 (non-integer).

Try:
1. b(n) = floor(c/n²) patterns
2. b(n) = 3^k for some k(n)
3. b(n) related to powers of 3 (since 81=3⁴)

Find integer-valued formula.""",

        "T05": """Check if initial pairs (189,92) and (101,81) are related to convergents.

Convergents of π: 22/7, 333/106, 355/113...
Convergents of e: 8/3, 11/4, 19/7...
Convergents of √2: 3/2, 7/5, 17/12...
Convergents of φ: 2/1, 3/2, 5/3, 8/5...

Questions:
1. Is 189/92 close to any convergent?
2. Is 101/81 close to any convergent?
3. Are 189, 92, 101, 81 themselves convergent numerators/denominators?""",

        "T06": """Deep analysis of factorizations:
- 189 = 3³ × 7
- 92 = 2² × 23
- 101 = prime
- 81 = 3⁴

Observations:
- 189 and 81 both have factor 3
- 189/81 = 7/3 × 3 = 7×3⁻¹ mod something?

Questions:
1. What is 189 mod 81? What is 101 mod 81?
2. What is gcd(189,101)? gcd(92,81)?
3. Is there a modular arithmetic pattern?""",

        "T07": """Check m-values for n=35,38,41,44,47 for generalized Fibonacci patterns.

m[35] = 2024429090 (d=5)
m[38] = 109469830514 (d=2)
m[41] = 916024625435 (d=2)
m[44] = 17007046382995 (d=1)
m[47] = 123888169938382 (d=1)

Factor each and check for consecutive gen Fib pairs.""",

        "T08": """Analyze arithmetic combinations of initial pairs:

Pair 1: (189, 92) for n=62
Pair 2: (101, 81) for n=68

Compute:
- a+b: 189+92=281, 101+81=182
- a-b: 189-92=97, 101-81=20
- a×b: 189×92=17388, 101×81=8181
- a/b: 189/92≈2.054, 101/81≈1.247
- gcd: gcd(189,92)=1, gcd(101,81)=1

Look for patterns. What about:
- 281 is 60th prime (p_{n-2} for n=62)
- 182 = 2×91 = 2×7×13

Is a+b = p_{n-2} a pattern?""",

        "T09": """Check if initial pairs (a,b) follow their own recurrence.

Data:
- n=62: (189, 92)
- n=68: (101, 81)

If pairs follow: a_new = f(a_old, b_old), b_new = g(a_old, b_old)

Try:
1. Linear: a₂ = c₁a₁ + c₂b₁, b₂ = c₃a₁ + c₄b₁
2. Multiplicative patterns
3. Difference equations

Can you derive (101,81) from (189,92)?""",

        "T10": """Verify generalized Fibonacci pattern on m[38] and m[41] which have d=2.

m[38] = 109469830514
m[41] = 916024625435

Steps:
1. Factor each number
2. Check if any two factors are consecutive gen Fib
3. If yes, find the initial pair (a,b)
4. Check if k = 2(n-59)/3 holds

Expected:
- n=38: k = 2(38-59)/3 = -14 (negative, pattern may not apply)
- n=41: k = 2(41-59)/3 = -12 (negative)

Report findings.""",

        "T11": """Analyze relationship between initial pairs and prime indices.

Data:
- (189, 92) for n=62
- (101, 81) for n=68

101 is the 26th prime.
189 = 3³×7, not prime.

Questions:
1. Is there a prime-index relationship?
2. What primes are near 189, 92, 81?
3. prime(60)=281=189+92. Is this significant?""",

        "T12": """Analyze GCD and LCM patterns:

For (189, 92):
- gcd = 1
- lcm = 17388

For (101, 81):
- gcd = 1
- lcm = 8181

Questions:
1. lcm(189,92)/lcm(101,81) = 17388/8181 ≈ 2.125
2. Is there a pattern in lcm values?
3. Check: 17388 = 2²×3³×7×23, 8181 = 3⁴×101"""
    }

    if task_id not in tasks:
        print(f"Unknown task: {task_id}")
        sys.exit(1)

    prompt = tasks[task_id]
    print(f"Running {task_id} on {model}...")

    result = query_llm(model, prompt)
    log_result(task_id, model, result)

    print(f"Done. Result logged to RESEARCH_RESULTS.md")
    print(result[:500] + "..." if len(result) > 500 else result)
