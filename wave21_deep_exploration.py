#!/usr/bin/env python3
"""
Wave 21 Deep Exploration - 8 Hour Autonomous Research Session

This orchestrator runs local AI models in extended autonomous mode to discover
the mathematical property that uniquely determines k[n] in the Bitcoin Puzzle sequence.

Models:
- QWQ:32b (mathematician) - Deep mathematical reasoning, 20 min timeout
- Nemotron (statistician) - Statistical analysis, 10 min timeout
- Deepseek-r1:14b (reasoner) - Chain of thought reasoning, 15 min timeout
- Qwen2.5-coder:32b (coder) - Code generation and testing, 10 min timeout

Run time: 8 hours (~480 minutes)
Expected iterations: 20-30 (depending on model response times)
"""

import subprocess
import sqlite3
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
OUTPUT_DIR = Path("swarm_outputs/deep_exploration")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = "db/kh.db"
LOG_FILE = OUTPUT_DIR / "session.log"
FINDINGS_FILE = OUTPUT_DIR / "findings.json"
BREAKTHROUGHS_FILE = OUTPUT_DIR / "BREAKTHROUGHS.md"

# 8 hours = 480 minutes
MAX_RUNTIME_MINUTES = 480
MAX_ITERATIONS = 50  # Safety cap

# Model configurations with generous timeouts for deep thinking
MODELS = {
    "mathematician": {
        "model": "qwq:32b",
        "timeout": 1200,  # 20 minutes - needs time for deep reasoning
        "role": "You are a mathematician specializing in number theory, recurrence relations, and cryptographic sequences. Think deeply and systematically."
    },
    "statistician": {
        "model": "nemotron:latest",
        "timeout": 600,  # 10 minutes
        "role": "You are a statistician analyzing patterns in numerical sequences. Propose and test statistical hypotheses rigorously."
    },
    "reasoner": {
        "model": "deepseek-r1:14b",
        "timeout": 900,  # 15 minutes
        "role": "You are a reasoning specialist. Use chain-of-thought to explore possibilities systematically. Show your thinking process."
    },
    "coder": {
        "model": "qwen2.5-coder:32b",
        "timeout": 600,  # 10 minutes
        "role": "You are a code specialist. Write Python code to test hypotheses and verify mathematical claims. Always include runnable code."
    },
}

# The core mystery to solve
CORE_MYSTERY = """
THE BITCOIN PUZZLE k[n] SELECTION MYSTERY

We have 82 known private keys k[1] through k[130] (with gaps).
They satisfy this recurrence relation (100% verified):

    k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]

Where:
- adj[n] = k[n] - 2*k[n-1] (the "adjustment")
- m[n] = (2^n - adj[n]) / k[d[n]] (MUST be integer)
- d[n] is chosen to minimize |m[n]| among valid divisors

Bootstrap values: k[1]=1, k[2]=3, k[3]=7 (Mersenne: 2^n - 1)

THE MYSTERY: Given k[1..n-1], the recurrence admits INFINITELY MANY valid k[n].
What mathematical property UNIQUELY determines the actual k[n]?

DISPROVEN HYPOTHESES (tested, 0% match):
1. "Minimize |m| globally" - WRONG. For every n, m=0 candidates exist but are never chosen
2. "Smallest k in range" - WRONG. Fails for n≥5
3. "Closest to λ*k[n-1]" (growth rate) - WRONG. 0% match
4. "Simple multiplicative formula" - WRONG. Only 4/27 have exact formulas

VERIFIED FACTS:
- Growth rate λ ≈ 2.01 (geometric mean), but varies 1.1 to 3.4
- Sign pattern ++- holds for n=2-16, breaks at n=17 (Fermat prime)
- k[1,2,4,5] are Fibonacci numbers (1,3,8,21)
- k[1,2,3] are Mersenne numbers (1,3,7)
- Most k[n] for n≥3 contain k[3]=7 as a factor
- k[9], k[12], k[15] are "prime-like" (coprime with all previous)

YOUR MISSION: Discover what property selects k[n] from the infinite valid candidates.

Think about:
- What CONSTRAINT makes one candidate special?
- Is there a hidden seed or PRNG?
- Is there an optimization criterion we missed?
- Is adj[n] itself determined by some formula?
- What patterns exist in the known data?
"""

def log(msg):
    """Log message with timestamp."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_k_data():
    """Load k values and compute derived sequences."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT puzzle_id, priv_hex
        FROM ground_truth
        WHERE priv_hex IS NOT NULL
        ORDER BY puzzle_id
    """)
    rows = c.fetchall()
    conn.close()

    k = {}
    for puzzle_id, priv_hex in rows:
        if priv_hex.startswith('0x'):
            k[puzzle_id] = int(priv_hex, 16)
        else:
            k[puzzle_id] = int(priv_hex, 16)

    # Compute adj, m, d for first 30 values
    adj = {}
    m_vals = {}
    d_vals = {}

    for n in range(2, min(31, max(k.keys()) + 1)):
        if n in k and (n-1) in k:
            adj[n] = k[n] - 2 * k[n-1]

            # Find d that minimizes |m|
            numerator = (1 << n) - adj[n]
            best_d = 1
            best_m = numerator

            for d in range(1, n):
                if d in k and k[d] != 0 and numerator % k[d] == 0:
                    m = numerator // k[d]
                    if abs(m) < abs(best_m):
                        best_m = m
                        best_d = d

            m_vals[n] = best_m
            d_vals[n] = best_d

    return {
        "k": {str(n): str(v) for n, v in k.items()},
        "adj": {str(n): str(v) for n, v in adj.items()},
        "m": {str(n): str(v) for n, v in m_vals.items()},
        "d": {str(n): str(v) for n, v in d_vals.items()},
        "count": len(k)
    }

def query_model(model_name, config, prompt, iteration):
    """Query a model and save response."""
    log(f"  Querying {model_name} ({config['model']}) with {config['timeout']}s timeout...")

    full_prompt = f"{config['role']}\n\n{prompt}"

    try:
        result = subprocess.run(
            ["ollama", "run", config['model'], full_prompt],
            capture_output=True,
            text=True,
            timeout=config['timeout']
        )
        response = result.stdout.strip()

        # Save response
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = OUTPUT_DIR / f"{ts}_{model_name}_{iteration}.txt"
        with open(filename, "w") as f:
            f.write(f"=== {model_name.upper()} - Iteration {iteration} ===\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Model: {config['model']}\n\n")
            f.write(response)

        log(f"    {model_name} completed ({len(response)} chars)")
        return response

    except subprocess.TimeoutExpired:
        log(f"    {model_name} TIMEOUT after {config['timeout']}s")
        return None
    except Exception as e:
        log(f"    {model_name} ERROR: {e}")
        return None

def extract_findings(responses):
    """Extract breakthroughs, hypotheses, and test requests from responses."""
    findings = {
        "breakthroughs": [],
        "hypotheses": [],
        "test_requests": [],
        "code_blocks": []
    }

    for model, response in responses.items():
        if not response:
            continue

        # Look for marked sections
        lines = response.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()

            if 'breakthrough' in line_lower:
                # Get next few lines as context
                context = '\n'.join(lines[i:i+5])
                findings["breakthroughs"].append({
                    "model": model,
                    "content": context
                })

            if 'hypothesis' in line_lower:
                context = '\n'.join(lines[i:i+3])
                findings["hypotheses"].append({
                    "model": model,
                    "content": context
                })

            if 'test this' in line_lower:
                context = '\n'.join(lines[i:i+5])
                findings["test_requests"].append({
                    "model": model,
                    "content": context
                })

        # Extract code blocks
        import re
        code_blocks = re.findall(r'```python\n(.*?)```', response, re.DOTALL)
        for code in code_blocks:
            findings["code_blocks"].append({
                "model": model,
                "code": code
            })

    return findings

def build_iteration_prompt(iteration, k_data, previous_findings, focus_area=None):
    """Build prompt for this iteration."""

    prompt = f"""
{CORE_MYSTERY}

=== CURRENT DATA (first 20 values) ===
k values: {json.dumps({k: v for k, v in list(k_data['k'].items())[:20]}, indent=2)}
adj values: {json.dumps(k_data['adj'], indent=2)}
m values: {json.dumps(k_data['m'], indent=2)}
d values: {json.dumps(k_data['d'], indent=2)}

=== ITERATION {iteration} ===
"""

    if previous_findings:
        prompt += f"""
Previous iteration findings:
- Breakthroughs: {len(previous_findings.get('breakthroughs', []))}
- Hypotheses: {len(previous_findings.get('hypotheses', []))}
- Test requests: {len(previous_findings.get('test_requests', []))}

Key hypotheses to build on:
"""
        for h in previous_findings.get('hypotheses', [])[:3]:
            prompt += f"  - [{h['model']}]: {h['content'][:200]}...\n"

    if focus_area:
        prompt += f"\nFOCUS AREA: {focus_area}\n"

    prompt += """
YOUR TASK:
1. Analyze the data deeply
2. Propose NEW hypotheses about what determines k[n]
3. If you're the coder, write Python code to TEST hypotheses
4. Mark findings with:
   - "BREAKTHROUGH:" for major discoveries
   - "HYPOTHESIS:" for testable theories
   - "TEST THIS:" for experiments to run

Think step by step. Show your reasoning. Be creative but rigorous.
"""

    return prompt

def update_breakthroughs_file(all_findings, iteration):
    """Update the breakthroughs markdown file."""
    with open(BREAKTHROUGHS_FILE, "a") as f:
        f.write(f"\n\n## Iteration {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        if all_findings.get("breakthroughs"):
            f.write("### Breakthroughs\n")
            for b in all_findings["breakthroughs"]:
                f.write(f"- **[{b['model']}]**: {b['content'][:500]}\n")

        if all_findings.get("hypotheses"):
            f.write("\n### Hypotheses\n")
            for h in all_findings["hypotheses"]:
                f.write(f"- **[{h['model']}]**: {h['content'][:300]}\n")

def run_exploration():
    """Main exploration loop."""
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=MAX_RUNTIME_MINUTES)

    log("=" * 60)
    log("DEEP EXPLORATION SESSION STARTED")
    log(f"Start time: {start_time}")
    log(f"Planned end: {end_time}")
    log(f"Max iterations: {MAX_ITERATIONS}")
    log("=" * 60)

    # Initialize breakthroughs file
    with open(BREAKTHROUGHS_FILE, "w") as f:
        f.write("# Deep Exploration Session - Breakthroughs Log\n")
        f.write(f"Started: {start_time}\n")
        f.write(f"Mission: Discover the k[n] selection property\n\n")

    # Load data
    k_data = load_k_data()
    log(f"Loaded {k_data['count']} k values from database")

    # Focus areas to cycle through
    focus_areas = [
        "What makes adj[n] take its specific value?",
        "Is there a hidden optimization criterion?",
        "Could the sequence be PRNG-generated? What seed?",
        "What's special about the binary representation of k[n]?",
        "How do the 'prime-like' k[n] (k[9], k[12], k[15]) differ?",
        "Is there a continued fraction or Diophantine connection?",
        "Could k[n] be the solution to some equation involving previous terms?",
        "What role does the Fermat prime 17 play in the pattern break?",
        "Is there an elliptic curve interpretation we're missing?",
        "Could adj[n] follow a chaotic but deterministic map?",
    ]

    all_findings = {"breakthroughs": [], "hypotheses": [], "test_requests": [], "code_blocks": []}
    iteration = 0

    while datetime.now() < end_time and iteration < MAX_ITERATIONS:
        iteration += 1
        log("")
        log("=" * 60)
        log(f"ITERATION {iteration}")
        log("=" * 60)

        # Pick focus area for this iteration
        focus = focus_areas[(iteration - 1) % len(focus_areas)]
        log(f"Focus: {focus}")

        # Build prompt
        prompt = build_iteration_prompt(iteration, k_data, all_findings, focus)

        # Query all models
        responses = {}
        for model_name, config in MODELS.items():
            responses[model_name] = query_model(model_name, config, prompt, iteration)

            # Check if we should stop
            if datetime.now() >= end_time:
                log("Time limit reached during model queries")
                break

        # Extract findings
        iteration_findings = extract_findings(responses)

        # Accumulate findings
        for key in all_findings:
            all_findings[key].extend(iteration_findings.get(key, []))

        # Log findings
        log(f"Iteration {iteration} findings:")
        log(f"  Breakthroughs: {len(iteration_findings.get('breakthroughs', []))}")
        log(f"  Hypotheses: {len(iteration_findings.get('hypotheses', []))}")
        log(f"  Test requests: {len(iteration_findings.get('test_requests', []))}")
        log(f"  Code blocks: {len(iteration_findings.get('code_blocks', []))}")

        # Update breakthroughs file
        update_breakthroughs_file(iteration_findings, iteration)

        # Save accumulated findings
        with open(FINDINGS_FILE, "w") as f:
            json.dump(all_findings, f, indent=2)

        # Brief pause between iterations
        time.sleep(5)

        # Check for significant breakthroughs
        if len(iteration_findings.get("breakthroughs", [])) >= 2:
            log("*** MULTIPLE BREAKTHROUGHS - Continuing with focus ***")

    # Final summary
    elapsed = datetime.now() - start_time
    log("")
    log("=" * 60)
    log("EXPLORATION COMPLETE")
    log(f"Total time: {elapsed}")
    log(f"Iterations completed: {iteration}")
    log(f"Total breakthroughs: {len(all_findings['breakthroughs'])}")
    log(f"Total hypotheses: {len(all_findings['hypotheses'])}")
    log(f"Total test requests: {len(all_findings['test_requests'])}")
    log(f"Total code blocks: {len(all_findings['code_blocks'])}")
    log("=" * 60)

    # Final summary in breakthroughs file
    with open(BREAKTHROUGHS_FILE, "a") as f:
        f.write(f"\n\n## Final Summary\n")
        f.write(f"- Total time: {elapsed}\n")
        f.write(f"- Iterations: {iteration}\n")
        f.write(f"- Breakthroughs: {len(all_findings['breakthroughs'])}\n")
        f.write(f"- Hypotheses: {len(all_findings['hypotheses'])}\n")

    return all_findings

if __name__ == "__main__":
    try:
        findings = run_exploration()
        print("\nExploration complete! Check:")
        print(f"  - {OUTPUT_DIR}/session.log")
        print(f"  - {OUTPUT_DIR}/BREAKTHROUGHS.md")
        print(f"  - {OUTPUT_DIR}/findings.json")
    except KeyboardInterrupt:
        log("\nExploration interrupted by user")
    except Exception as e:
        log(f"\nExploration error: {e}")
        raise
