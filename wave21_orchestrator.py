#!/usr/bin/env python3
"""
Wave 21+ Agentic Orchestrator
=============================
Autonomous multi-model exploration with orchestration rules.

Models explore freely within constraints:
- Time limits per task
- DB sanity checks
- Cross-model result sharing
- Iteration until breakthrough or budget exhausted
"""

import subprocess
import sqlite3
import json
import os
import time
from datetime import datetime
from pathlib import Path

# Configuration
OUTPUT_DIR = Path("/home/rkh/ladder/swarm_outputs/autonomous")
DB_PATH = "/home/rkh/ladder/db/kh.db"
LOG_FILE = OUTPUT_DIR / "orchestrator.log"

# Model configurations with specializations
MODELS = {
    "mathematician": {
        "model": "qwq:32b",
        "timeout": 1200,
        "specialty": "algebraic structures, recurrence relations, number theory"
    },
    "statistician": {
        "model": "nemotron:latest",
        "timeout": 600,
        "specialty": "statistical analysis, hypothesis testing, distributions"
    },
    "reasoner": {
        "model": "deepseek-r1:14b",
        "timeout": 900,
        "specialty": "deep reasoning, construction algorithms, proofs"
    },
    "coder": {
        "model": "qwen2.5-coder:32b",
        "timeout": 600,
        "specialty": "implementation, testing, verification code"
    }
}

# Verified facts that all models must know
VERIFIED_FACTS = """
## VERIFIED FACTS (100% confirmed n=2-70)
1. k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
2. adj[n] = k[n] - 2*k[n-1]
3. m[n] = (2^n - adj[n]) / k[d[n]]  <- MUST BE INTEGER
4. d[n] minimizes |m[n]| among d where k[d] divides (2^n - adj[n])
5. Bootstrap: k[1]=1, k[2]=3, k[3]=7 (Mersenne: 2^n - 1)
6. Growth rate lambda ~ 2.0073

## RULED OUT
- "Smallest k[n] in range" - FAILS for n>=5
- "Globally smallest |m|" - FAILS for all n>=4
- Predicting d[n] from n alone - max 55% accuracy

## THE MYSTERY
Given k[1..n-1], many valid k[n] satisfy the recurrence.
WHAT PROPERTY SELECTS THE ACTUAL k[n]?
"""

class Orchestrator:
    def __init__(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.findings = []
        self.iterations = 0
        self.max_iterations = 10

    def log(self, msg):
        """Log to file and print"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {msg}"
        print(entry)
        with open(LOG_FILE, "a") as f:
            f.write(entry + "\n")

    def db_sanity_check(self):
        """Verify database integrity before/after operations"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Count keys
        cursor.execute("SELECT COUNT(*) FROM keys WHERE puzzle_id IS NOT NULL")
        key_count = cursor.fetchone()[0]

        # Verify k[1], k[2], k[3] bootstrap
        cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IN (1,2,3) ORDER BY puzzle_id")
        bootstrap = cursor.fetchall()

        expected = [(1, '1'), (2, '3'), (3, '7')]
        bootstrap_ok = all(
            int(row[0]) == exp[0] and int(row[1], 16) == int(exp[1], 16)
            for row, exp in zip(bootstrap, expected)
        )

        # Verify recurrence for sample
        cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id LIMIT 20")
        rows = cursor.fetchall()
        k = {int(r[0]): int(r[1], 16) for r in rows}

        recurrence_ok = True
        for n in range(4, min(21, max(k.keys()) + 1)):
            if n not in k or n-1 not in k:
                continue
            adj = k[n] - 2 * k[n-1]
            found_valid_d = False
            for d in range(1, n):
                if d not in k:
                    continue
                if (2**n - adj) % k[d] == 0:
                    found_valid_d = True
                    break
            if not found_valid_d:
                recurrence_ok = False
                break

        conn.close()

        return {
            "key_count": key_count,
            "bootstrap_ok": bootstrap_ok,
            "recurrence_ok": recurrence_ok,
            "sanity_passed": bootstrap_ok and recurrence_ok
        }

    def load_k_values(self, limit=82):
        """Load k values from database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id LIMIT ?",
            (limit,)
        )
        k = {}
        for row in cursor.fetchall():
            k[int(row[0])] = int(row[1], 16)
        conn.close()
        return k

    def query_model(self, role, prompt, context=""):
        """Query a model with timeout and capture output"""
        config = MODELS[role]
        model = config["model"]
        timeout = config["timeout"]

        full_prompt = f"""You are the {role} in a research team.
Your specialty: {config["specialty"]}

{VERIFIED_FACTS}

{context}

YOUR TASK:
{prompt}

Think deeply. Show your reasoning. Report any breakthroughs clearly with "BREAKTHROUGH:" prefix.
If you find something worth testing, prefix with "TEST THIS:" for the coder.
If you have a new hypothesis, prefix with "HYPOTHESIS:"
"""

        self.log(f"Querying {role} ({model}) with {timeout}s timeout...")

        try:
            result = subprocess.run(
                ["ollama", "run", model, full_prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout

            # Save output
            outfile = OUTPUT_DIR / f"{self.session_id}_{role}_{self.iterations}.txt"
            with open(outfile, "w") as f:
                f.write(f"=== {role.upper()} - Iteration {self.iterations} ===\n")
                f.write(f"Time: {datetime.now()}\n")
                f.write(f"Model: {model}\n\n")
                f.write(output)

            self.log(f"  {role} completed ({len(output)} chars)")
            return output

        except subprocess.TimeoutExpired:
            self.log(f"  {role} TIMEOUT after {timeout}s")
            return f"TIMEOUT after {timeout}s"
        except Exception as e:
            self.log(f"  {role} ERROR: {e}")
            return f"ERROR: {e}"

    def extract_insights(self, output):
        """Extract breakthroughs, hypotheses, and test requests"""
        insights = {
            "breakthroughs": [],
            "hypotheses": [],
            "test_requests": []
        }

        for line in output.split("\n"):
            line_upper = line.upper()
            if "BREAKTHROUGH:" in line_upper:
                insights["breakthroughs"].append(line)
            elif "HYPOTHESIS:" in line_upper:
                insights["hypotheses"].append(line)
            elif "TEST THIS:" in line_upper:
                insights["test_requests"].append(line)

        return insights

    def run_exploration(self, focus_question):
        """Run one iteration of multi-model exploration"""
        self.iterations += 1
        self.log(f"\n{'='*60}")
        self.log(f"ITERATION {self.iterations}: {focus_question[:50]}...")
        self.log(f"{'='*60}")

        # Sanity check
        sanity = self.db_sanity_check()
        if not sanity["sanity_passed"]:
            self.log(f"DB SANITY FAILED: {sanity}")
            return None
        self.log(f"DB sanity OK: {sanity['key_count']} keys")

        # Load current data
        k = self.load_k_values()
        k_summary = f"k values loaded: n=1..{max(k.keys())}"

        # Phase 1: Mathematician analyzes
        math_output = self.query_model(
            "mathematician",
            focus_question,
            context=k_summary
        )
        math_insights = self.extract_insights(math_output)

        # Phase 2: Statistician tests
        stat_context = f"Mathematician found:\n" + "\n".join(
            math_insights["hypotheses"][:3] + math_insights["breakthroughs"][:3]
        )
        stat_output = self.query_model(
            "statistician",
            f"Test these mathematical insights statistically:\n{stat_context}",
            context=k_summary
        )
        stat_insights = self.extract_insights(stat_output)

        # Phase 3: Coder implements tests
        test_requests = math_insights["test_requests"] + stat_insights["test_requests"]
        if test_requests:
            code_output = self.query_model(
                "coder",
                f"Write Python code to test:\n" + "\n".join(test_requests[:5]),
                context=f"Database: {DB_PATH}\nTable: keys (puzzle_id, priv_hex)"
            )
        else:
            code_output = ""

        # Phase 4: Reasoner synthesizes
        all_insights = {
            "math": math_insights,
            "stat": stat_insights
        }
        synth_output = self.query_model(
            "reasoner",
            f"Synthesize these findings and identify the most promising direction:\n{json.dumps(all_insights, indent=2)}"
        )
        synth_insights = self.extract_insights(synth_output)

        # Collect all breakthroughs
        all_breakthroughs = (
            math_insights["breakthroughs"] +
            stat_insights["breakthroughs"] +
            synth_insights["breakthroughs"]
        )

        if all_breakthroughs:
            self.log(f"\nBREAKTHROUGHS FOUND:")
            for b in all_breakthroughs:
                self.log(f"  * {b}")
                self.findings.append(b)

        return {
            "iteration": self.iterations,
            "breakthroughs": all_breakthroughs,
            "hypotheses": math_insights["hypotheses"] + stat_insights["hypotheses"],
            "next_question": synth_insights.get("hypotheses", [focus_question])
        }

    def run_autonomous(self, initial_question, max_iter=None):
        """Run autonomous exploration loop"""
        if max_iter:
            self.max_iterations = max_iter

        self.log(f"\n{'#'*60}")
        self.log("AUTONOMOUS EXPLORATION STARTED")
        self.log(f"Initial question: {initial_question}")
        self.log(f"Max iterations: {self.max_iterations}")
        self.log(f"{'#'*60}\n")

        current_question = initial_question

        while self.iterations < self.max_iterations:
            result = self.run_exploration(current_question)

            if result is None:
                self.log("Stopping due to sanity check failure")
                break

            if result["breakthroughs"]:
                self.log("\n*** SIGNIFICANT BREAKTHROUGHS - PAUSING FOR REVIEW ***")
                break

            # Next iteration focuses on most promising hypothesis
            if result["hypotheses"]:
                current_question = f"Investigate further: {result['hypotheses'][0]}"
            else:
                current_question = "Try a completely different approach to find what selects k[n]"

            time.sleep(2)  # Brief pause between iterations

        self.log(f"\n{'#'*60}")
        self.log(f"EXPLORATION COMPLETE - {self.iterations} iterations")
        self.log(f"Total findings: {len(self.findings)}")
        self.log(f"{'#'*60}")

        return self.findings


def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Wave 21+ Agentic Orchestrator")
    parser.add_argument("--question", "-q", type=str,
                        default="What mathematical property selects the actual k[n] among valid candidates?",
                        help="Initial research question")
    parser.add_argument("--iterations", "-n", type=int, default=3,
                        help="Maximum iterations")
    parser.add_argument("--single", "-s", type=str,
                        help="Run single model (mathematician|statistician|reasoner|coder)")
    args = parser.parse_args()

    orch = Orchestrator()

    if args.single:
        # Single model mode
        output = orch.query_model(args.single, args.question)
        print(output)
    else:
        # Full autonomous mode
        findings = orch.run_autonomous(args.question, args.iterations)

        if findings:
            print("\n=== FINDINGS ===")
            for f in findings:
                print(f"  * {f}")


if __name__ == "__main__":
    main()
