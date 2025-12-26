#!/usr/bin/env python3
"""
QUEST WAVE 1: Pattern Extraction & Rule Derivation

Deploy multiple models in parallel to:
1. Analyze Mersenne impossible positions (n=15, 31, 63)
2. Analyze n=71 special form
3. Find general selection rule
4. Investigate factor 17 role
"""

import subprocess
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

OUTPUT_DIR = Path("swarm_outputs/quest_wave1")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path("db/kh.db")

def load_all_data():
    """Load ALL verified k values from database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT puzzle_id, priv_hex FROM ground_truth WHERE priv_hex IS NOT NULL ORDER BY puzzle_id")
    rows = c.fetchall()
    conn.close()
    return {pid: int(phex, 16) for pid, phex in rows}

def compute_full_analysis(k):
    """Compute comprehensive analysis for all known k values."""
    data = {}
    for n in sorted(k.keys()):
        if n < 2 or (n-1) not in k:
            continue

        target = 2*k[n-1] + (1 << n) - k[n]

        # Find d that minimizes |m|
        best_d, best_m = 1, target
        for d in range(1, n):
            if d in k and k[d] != 0:
                if target % k[d] == 0:
                    m = target // k[d]
                    if abs(m) < abs(best_m):
                        best_m, best_d = m, d

        # Check (2*k[n-1] + 2^n) mod 17
        sum_mod17 = (2*k[n-1] + (1 << n)) % 17

        data[n] = {
            'k': k[n],
            'm': best_m,
            'd': best_d,
            'k_mod17': k[n] % 17,
            'm_mod17': best_m % 17,
            'sum_mod17': sum_mod17,
            'is_impossible': sum_mod17 == 0,
        }

    return data

def build_mersenne_impossible_prompt(k, data):
    """Prompt for analyzing Mersenne impossible positions."""

    # Details for n=15, 31, 63
    details = []
    for n in [15, 31, 63]:
        if n in data:
            d = data[n]
            # Factorize k[n]
            factors = []
            temp = k[n]
            for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
                while temp % p == 0:
                    factors.append(p)
                    temp //= p
            if temp > 1:
                factors.append(temp)

            details.append(f"""
n={n} (Mersenne impossible: 2^{n.bit_length()}-1):
  k[{n}] = {k[n]}
  Factors: {' × '.join(map(str, factors))}
  d={d['d']}, m={d['m']}
  k mod 17 = {d['k_mod17']}
  m mod 17 = {d['m_mod17']}
  (2*k[{n-1}] + 2^{n}) mod 17 = {d['sum_mod17']}
""")

    return f"""
MATHEMATICAL ANALYSIS: MERSENNE IMPOSSIBLE POSITIONS

You are analyzing positions n=15, 31, 63 in a mathematical sequence.

At these positions:
- (2*k[n-1] + 2^n) ≡ 0 (mod 17) - prime reset is BLOCKED
- k[n] is COMPOSITE (not prime)
- m[n] is NOT divisible by 17

DATA:
{''.join(details)}

COMPARISON:
- n=15: k[15] = 67 × 401 (two NEW primes, coprime with all previous k)
- n=31: k[31] = 19² × ... (contains factor 19 from k[7]=76=4×19)
- n=63: k[63] = 2³ × 7 × ... (contains k[3]=7 as factor)

QUESTIONS TO ANSWER:
1. Why does k[15] introduce TWO new primes while k[31], k[63] reuse old factors?
2. Is there a "composite reset" rule (like prime reset but for composites)?
3. What selection criterion determines k[n] among valid candidates?
4. What's the role of coprimality with previous k-values?
5. Can you derive a DETERMINISTIC rule for Mersenne impossible positions?

Think step by step. Show your mathematical reasoning.
Output your conclusions in this format:

OBSERVATIONS: [Key observations from data]
HYPOTHESIS: [Your proposed rule]
VERIFICATION: [How to verify the rule]
FORMULA: [Mathematical formula if found]
"""

def build_n71_prompt(k, data):
    """Prompt for analyzing n=71 specifically."""

    # Compute key values
    k70 = k[70]
    sum_71 = 2*k70 + (1 << 71)

    return f"""
MATHEMATICAL ANALYSIS: POSITION n=71

n=71 has a SPECIAL FORM: 71 = 64 + 7 = 2^6 + k[3]

This relates n to both a power of 2 AND an earlier k-value!

KNOWN FACTS:
- k[70] = {k70}
- k[70] = 0x{k70:x}
- (2*k[70] + 2^71) mod 17 = {sum_71 % 17}
- n=71 is an IMPOSSIBLE position (sum ≡ 0 mod 17)
- k[71] must be in range [2^70, 2^71)
- k[71] mod 17 ≠ 0 (must be coprime with 17)

TESTED CANDIDATES (ALL FAILED):
1. Multiplicative (2^62 × k[9]): Wrong address
2. Smallest |m| overall (d=49, m≈4.7M): Wrong address

KEY INSIGHT:
At n=8 (power of 2 impossible), the rule is:
  k[8] = multiplicative candidate with smallest |m|
  k[8] = 2^5 × k[3] = 224

But n=71 is NOT a power of 2. It's 2^6 + k[3].

QUESTIONS TO ANSWER:
1. Are there other n with form 2^a + k[b]? What are their k[n] values?
2. Does the relationship n = 2^6 + k[3] affect how k[71] is computed?
3. What's different about n=71 vs n=8, n=15, n=31, n=63?
4. What constraint determines k[71] uniquely?
5. Can you derive a rule that would compute k[71]?

RELATED DATA:
- k[3] = 7
- k[64] is unknown (in gap)
- k[7] = 76 = 4 × 19

Think deeply. The answer is MATHEMATICAL.
"""

def build_general_rule_prompt(k, data):
    """Prompt for finding general selection rule."""

    # Find positions where m=3 candidate exists
    m3_examples = []
    for n in range(4, 20):
        if n-1 in k and n in k:
            m3_cand = (1 << n) - k[n-1]
            if (1 << (n-1)) <= m3_cand < (1 << n):
                m3_examples.append(f"n={n}: m=3 candidate={m3_cand}, actual k[{n}]={k[n]}")

    return f"""
MATHEMATICAL ANALYSIS: GENERAL SELECTION RULE

Every position n ≥ 3 has a candidate with m=3 (using d=n-1):
  k_candidate = 2^n - k[n-1]

This candidate is NEVER chosen. The actual k[n] is ALWAYS different.

EXAMPLES:
{chr(10).join(m3_examples[:10])}

VERIFIED RULE for n=8:
Among MULTIPLICATIVE candidates (2^a × k[b] or k[a] × k[b]),
choose the one with SMALLEST |m|.

QUESTION: Does |m|-minimization apply to ALL positions?

For each position type:
1. Mersenne (n=1,2,3): k[n] = 2^n - 1 (simple)
2. Prime Reset (m ≡ 0 mod 17): Largest prime with coprime q
3. Power-of-2 Impossible (n=8): Multiplicative, smallest |m|
4. Mersenne Impossible (n=15,31,63): ???
5. Other Impossible (n=71,...): ???
6. General positions: ???

TASK:
1. Analyze what all rules have in common
2. Find a UNIFIED selection criterion
3. Express as a single mathematical principle
4. Verify against known data

The ladder has a STRUCTURE. Find the underlying mathematical law.
"""

def build_factor17_prompt(k, data):
    """Prompt for investigating factor 17 role."""

    # Find all positions where 17 appears
    positions_m_div17 = []
    positions_k_div17 = []

    for n in sorted(data.keys()):
        if data[n]['m'] % 17 == 0:
            positions_m_div17.append(n)
        if k[n] % 17 == 0:
            positions_k_div17.append(n)

    return f"""
MATHEMATICAL ANALYSIS: THE ROLE OF 17

17 = 2^4 + 1 is a FERMAT PRIME. It appears EVERYWHERE in this sequence.

POSITIONS WHERE m[n] ≡ 0 (mod 17):
{positions_m_div17}
(These are PRIME RESET positions)

POSITIONS WHERE k[n] ≡ 0 (mod 17):
{positions_k_div17}
(k[n] divisible by 17)

IMPOSSIBLE POSITIONS (sum ≡ 0 mod 17):
n = 8, 15, 31, 63, 71, ...
At these, prime reset is BLOCKED.

KEY OBSERVATIONS:
1. At prime reset: m = 17 × q where q coprime with previous k
2. At impossible: m is coprime with 17
3. The Fermat prime 17 = 2^4 + 1 creates a mod-17 cycle

QUESTIONS:
1. Why is 17 (not 3, 5, 7, 11, 13) the critical modulus?
2. Is there a connection to 17 = 2^4 + 1 being a Fermat prime?
3. Do other Fermat primes (3, 5, 257, 65537) appear in the structure?
4. What's the complete role of 17 in the construction?
5. Can we use mod-17 arithmetic to derive missing k-values?

The answer involves NUMBER THEORY. Think deeply.
"""

def query_model(name, model, prompt, timeout=3600):
    """Query model with extended timeout."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting {name} ({model})...")

    start_time = time.time()

    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        response = result.stdout.strip()
        elapsed = time.time() - start_time

        # Save output
        output_file = OUTPUT_DIR / f"{name}.txt"
        with open(output_file, "w") as f:
            f.write(f"Model: {model}\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Elapsed: {elapsed/60:.1f} minutes\n\n")
            f.write(response)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] {name} completed ({len(response)} chars, {elapsed/60:.1f}min)")
        return name, response

    except subprocess.TimeoutExpired:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {name} TIMEOUT")
        return name, None
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {name} ERROR: {e}")
        return name, None

def main():
    print("=" * 80)
    print("QUEST WAVE 1: Pattern Extraction & Rule Derivation")
    print("=" * 80)
    print(f"Started: {datetime.now()}")
    print()

    # Load data
    k = load_all_data()
    data = compute_full_analysis(k)

    # Build prompts
    prompts = {
        "mersenne_impossible": build_mersenne_impossible_prompt(k, data),
        "n71_special": build_n71_prompt(k, data),
        "general_rule": build_general_rule_prompt(k, data),
        "factor17": build_factor17_prompt(k, data),
    }

    # Save prompts
    for name, prompt in prompts.items():
        with open(OUTPUT_DIR / f"{name}_prompt.txt", "w") as f:
            f.write(prompt)

    print(f"Saved {len(prompts)} prompts to {OUTPUT_DIR}/")
    print()

    # Deploy models
    tasks = [
        ("qwq_mersenne", "qwq:32b", prompts["mersenne_impossible"], 3600),
        ("nemotron_n71", "nemotron:70b", prompts["n71_special"], 3600),
        ("deepseek_general", "deepseek-r1:14b", prompts["general_rule"], 1800),
        ("phi4_factor17", "phi4-reasoning:14b", prompts["factor17"], 1800),
    ]

    print(f"Deploying {len(tasks)} models...")
    print()

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(query_model, name, model, prompt, timeout): name
            for name, model, prompt, timeout in tasks
        }

        for future in as_completed(futures):
            name, response = future.result()
            if response:
                # Check for key findings
                keywords = ["FORMULA", "RULE", "HYPOTHESIS", "k[71]", "deterministic"]
                found = [kw for kw in keywords if kw.lower() in response.lower()]
                if found:
                    print(f"  → {name} found: {', '.join(found)}")

    print()
    print("=" * 80)
    print(f"QUEST WAVE 1 COMPLETE - {datetime.now()}")
    print("=" * 80)
    print(f"Results in: {OUTPUT_DIR}/")

    # Git commit
    try:
        subprocess.run(["git", "add", str(OUTPUT_DIR)], capture_output=True, timeout=30)
        subprocess.run(
            ["git", "commit", "-m", f"Quest Wave 1: Pattern extraction results"],
            capture_output=True,
            timeout=30
        )
        print("Results committed to repo")
    except:
        pass

if __name__ == "__main__":
    main()
