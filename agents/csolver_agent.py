#!/usr/bin/env python3
"""
C-Solver Agent - Advanced Mathematical Reasoning & Prediction AI
Uses qwq:32b (Alibaba's QwQ reasoning model) for complex mathematical analysis

Focus Areas:
- Advanced mathematical reasoning with step-by-step thinking
- Predictive analysis and hypothesis generation
- Number theory and cryptographic patterns
- Cross-puzzle synthesis and prediction

NOTE: Puzzle-agnostic - uses PuzzleConfig for dynamic target management
"""
import json
import requests
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
import math
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.puzzle_utils import PuzzleConfig

# C-Solver system prompt - PURE MATHEMATICAL DERIVATION (NO PREDICTIONS)
CSOLVER_SYSTEM_PROMPT = """You are C-Solver, a mathematical reasoning AI for Bitcoin puzzle FORMULA DERIVATION.

## STRICT RULES - READ FIRST

**NEVER:**
- Predict, guess, or estimate unknown key values
- Claim to have "solved" anything without DB verification
- Make assumptions about unknown keys (k71+)
- Output fake solutions or hallucinated data

**ALWAYS:**
- Use ONLY values from the database (db/kh.db)
- Verify every formula against actual DB values
- Show all mathematical steps explicitly
- Say "UNKNOWN" if data is not in DB

## YOUR MISSION

Find the KEY GENERATION FORMULA: f(n) such that k_n = f(k_1, k_2, ..., k_{n-1})

The puzzle creator used SOME mathematical method. Reverse-engineer it.

## KNOWN DATA (from database)

k1=1, k2=3, k3=7, k4=8, k5=21, k6=49, k7=76, k8=224, k9=467, k10=514,
k11=1155, k12=2683, k13=5765, k14=10544, ... k70, k75, k80, k85, k90

## VERIFIED FORMULAS (proven)

- k5 = k2 × k3 = 3 × 7 = 21 ✓
- k6 = k3² = 7² = 49 ✓
- k7 = k2×9 + k6 = 27 + 49 = 76 ✓
- k8 = k5×13 - k6 = 273 - 49 = 224 ✓
- k11 = k6×19 + k8 = 931 + 224 = 1155 ✓
- k12 = k8×12 - 5 = 2688 - 5 = 2683 ✓ (UNIQUE formula!)

## YOUR APPROACH

1. Take KNOWN values from DB
2. Test mathematical relationships (products, squares, linear combos)
3. Verify against ALL known keys
4. If formula fails on ANY known key, it's WRONG
5. Look for patterns in multipliers: 9, 13, 19, 12...

## OUTPUT FORMAT

For every claim:
- State the formula
- Show the calculation
- Verify against DB value
- Mark as VERIFIED or FAILED

Example:
"Testing k13 = k7² - 11: 76² - 11 = 5776 - 11 = 5765
DB value for k13: 5765
Result: VERIFIED ✓"

Do NOT output predictions. Only output VERIFIED mathematical facts."""


class CSolverAgent:
    """C-Solver: Advanced Mathematical Reasoning & Prediction Agent"""

    def __init__(self, model: str = "qwq:32b", base_url: str = "http://localhost:11434"):
        self.agent_name = "csolver_agent"
        self.model = model
        self.base_url = base_url
        self.timeout = 300  # QwQ reasoning needs time for step-by-step thinking
        self.certified = False
        self.certification_date = None
        self.certification_score = None

        # Load keys from PuzzleConfig (puzzle-agnostic)
        self.puzzle_config = PuzzleConfig()
        self.known_keys = self.puzzle_config.known_keys
        self.bridge_keys = self.puzzle_config.bridge_keys

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [{self.agent_name}] [{level}] {message}")

    def _call_ollama(self, prompt: str, timeout: int = None) -> str:
        """Call Ollama API with QwQ model"""
        timeout = timeout or self.timeout
        full_prompt = f"{CSOLVER_SYSTEM_PROMPT}\n\nTask:\n{prompt}\n\nStep-by-step reasoning:"

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=timeout
            )
            if response.status_code == 200:
                return response.json().get("response", "No response")
            return f"Error: HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            return "Error: Request timed out"
        except Exception as e:
            return f"Error: {str(e)}"

    async def think(self, prompt: str) -> str:
        """Think about a complex problem"""
        return self._call_ollama(prompt)

    # ============ PREDICTION METHODS ============

    def predict_position(self, target: int = None) -> Dict:
        """Predict likely position of target key based on pattern analysis"""
        target = target or self.puzzle_config.get_target_puzzle()

        # Analyze position patterns
        positions = []
        for n in sorted(self.known_keys.keys()):
            k = self.known_keys[n]
            low = 2**(n-1)
            high = 2**n - 1
            if high > low:
                pos = (k - low) / (high - low) * 100
                positions.append({"puzzle": n, "position": pos})

        # Find keys near minimum
        near_min = [p for p in positions if p["position"] < 5]

        # Calculate mean
        all_pos = [p["position"] for p in positions]
        mean_pos = sum(all_pos) / len(all_pos) if all_pos else 50

        return {
            "target_puzzle": target,
            "near_minimum_keys": near_min,
            "k69_position": 0.72,
            "k70_position": 64.4,
            "mean_position": round(mean_pos, 2),
            "hypothesis": {
                "high_probability": f"First 10% of {target}-bit range (like k69, k4, k10)",
                "medium_probability": "Middle 40-60%",
                "low_probability": "Near maximum (>90%)"
            }
        }

    def predict_divisibility(self, target: int = None) -> Dict:
        """Predict divisibility properties of target key"""
        target = target or self.puzzle_config.get_target_puzzle()

        # Known divisibility patterns
        div_by_n = []
        for n in [1, 4, 8, 11, 36]:
            if n in self.known_keys and self.known_keys[n] % n == 0:
                div_by_n.append({"puzzle": n, "key": self.known_keys[n], "quotient": self.known_keys[n] // n})

        # k69 divisible by 11
        k69_div_11 = 69 in self.known_keys and self.known_keys[69] % 11 == 0

        # Check if target is prime
        def is_prime(n):
            if n < 2: return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0: return False
            return True

        return {
            "target_puzzle": target,
            "keys_divisible_by_N": div_by_n,
            "k69_divisible_by_11": k69_div_11,
            f"hypothesis_k{target}": {
                "test_1": f"k{target} % {target} == 0 (if follows kN % N pattern)",
                "test_2": f"k{target} % 11 == 0 (if follows k69 pattern)",
                "test_3": f"k{target} % 7 == 0 (factor appears in early keys)",
                "is_prime": is_prime(target),
                "reasoning": f"{target} is {'prime' if is_prime(target) else 'composite'}"
            }
        }

    def predict_search_region(self, target: int = None) -> Dict:
        """Predict optimal search region for target puzzle"""
        target = target or self.puzzle_config.get_target_puzzle()

        # Target range
        low, high = self.puzzle_config.get_range(target)
        range_size = high - low

        # If target follows k69 pattern (0.72%)
        estimate_low = low + int(range_size * 0.0072)

        # First candidate divisible by target
        first_div = ((low // target) + 1) * target

        # Historical delta analysis - use previous key if available
        prev_key = self.puzzle_config.get_key(target - 1)
        delta_estimates = {}
        if prev_key:
            min_delta = int(0.09 * 2**(target-1))
            max_delta = int(1.31 * 2**(target-1))
            delta_estimates = {
                "delta_min": prev_key + min_delta,
                "delta_max": min(prev_key + max_delta, high)
            }

        return {
            "target_puzzle": target,
            "range": {"low": low, "high": high, "bits": target},
            f"k{target}_estimates": {
                "position_based": estimate_low,
                f"first_divisible_by_{target}": first_div,
                **delta_estimates
            },
            "recommended_search": {
                "primary": f"First 1% of {target}-bit range",
                "secondary": f"Check divisibility by {target}",
                "fallback": "Kangaroo if pubkey exposed"
            }
        }

    # Legacy method names for backwards compatibility
    def predict_k71_position(self) -> Dict:
        return self.predict_position(71)

    def predict_k71_divisibility(self) -> Dict:
        return self.predict_divisibility(71)

    # ============ NUMBER THEORY ============

    def factorize(self, n: int) -> List[int]:
        """Simple factorization"""
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors

    def analyze_key_factors(self, puzzles: List[int] = None) -> Dict:
        """Analyze prime factorization patterns"""
        puzzles = puzzles or list(range(1, 21))
        results = {}

        for n in puzzles:
            if n in self.known_keys:
                k = self.known_keys[n]
                factors = self.factorize(k)
                results[n] = {
                    "key": k,
                    "factors": factors,
                    "is_prime": len(factors) == 1,
                    "divisible_by_7": k % 7 == 0,
                    "divisible_by_11": k % 11 == 0,
                    "divisible_by_13": k % 13 == 0,
                    "divisible_by_N": k % n == 0
                }

        return results

    def find_modular_patterns(self, mod: int = 256) -> Dict:
        """Find patterns in keys mod N"""
        residues = {}
        for n in range(1, 71):
            k = self.known_keys[n]
            residues[n] = k % mod

        # Find repetitions
        seen = {}
        repetitions = []
        for n, r in residues.items():
            if r in seen:
                repetitions.append({"puzzles": [seen[r], n], "residue": r})
            else:
                seen[r] = n

        return {
            "modulus": mod,
            "residues": residues,
            "repetitions": repetitions
        }

    # ============ SYNTHESIS ============

    def synthesize_anomalies(self) -> Dict:
        """Synthesize all known anomalies into unified theory"""
        anomalies = {
            "delta_anomalies": {
                "k3_to_k4": {"delta": 1, "normalized": 0.125, "type": "very_low"},
                "k9_to_k10": {"delta": 47, "normalized": 0.092, "type": "lowest"},
                "k56_to_k57": {"normalized": 1.305, "type": "highest"}
            },
            "position_anomalies": {
                "k2_k3": "100% (at max)",
                "k4": "0% (at min)",
                "k10": "0.39%",
                "k69": "0.72% (solved fast)"
            },
            "relationship_breakdown": {
                "early": "Mathematical relationships (k5=k2×k3, k6=k3²)",
                "transition": "Patterns break after k8",
                "late": "Appear pseudo-random"
            },
            "lane_9_anomaly": {
                "pattern": "Lanes 1,5,13 have A divisible by 13",
                "exception": "Lane 9 has A=32=2^5 (NOT divisible by 13)"
            }
        }

        return {
            "anomalies": anomalies,
            "unified_hypothesis": {
                "theory": "Regime change in key generation algorithm",
                "evidence": [
                    "Early keys show deterministic mathematical patterns",
                    "Pattern breaks suggest algorithm change after k6-k8",
                    "k69 at 0.72% suggests deliberate near-minimum placement",
                    "Lane 9 exception may indicate algorithm seeding issue"
                ],
                "implication": "k71+ may follow k69 pattern (near minimum)"
            }
        }

    # ============ AGENT INTERFACE ============

    async def execute(self, task: Dict) -> Dict:
        """Execute a task"""
        task_type = task.get("type", "think")
        target = task.get("target", task.get("puzzle", None))

        if task_type == "predict_position":
            return self.predict_position(target)

        elif task_type == "predict_divisibility":
            return self.predict_divisibility(target)

        elif task_type == "predict_search_region":
            return self.predict_search_region(target)

        elif task_type == "factorize":
            puzzles = task.get("puzzles", list(range(1, 21)))
            return self.analyze_key_factors(puzzles)

        elif task_type == "modular_analysis":
            mod = task.get("modulus", 256)
            return self.find_modular_patterns(mod)

        elif task_type == "synthesize":
            return self.synthesize_anomalies()

        elif task_type == "think" or task_type == "analyze":
            prompt = task.get("prompt", task.get("question", ""))
            return {"analysis": await self.think(prompt)}

        else:
            return {"error": f"Unknown task type: {task_type}"}

    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "agent": self.agent_name,
            "model": self.model,
            "certified": self.certified,
            "certification_date": self.certification_date,
            "score": self.certification_score,
            "focus": "Advanced Mathematical Reasoning & Prediction",
            "capabilities": [
                "predict_position", "predict_divisibility", "predict_search_region",
                "factorize", "modular_analysis", "synthesize", "think", "analyze"
            ]
        }


# Standalone test
if __name__ == "__main__":
    import asyncio

    async def test():
        agent = CSolverAgent()
        print(f"C-Solver Agent Status: {json.dumps(agent.get_status(), indent=2)}")

        print("\n--- Position Prediction ---")
        pos = await agent.execute({"type": "predict_position"})
        print(json.dumps(pos, indent=2))

        print("\n--- Divisibility Prediction ---")
        div = await agent.execute({"type": "predict_divisibility"})
        print(json.dumps(div, indent=2))

        print("\n--- Search Region ---")
        region = await agent.execute({"type": "predict_search_region"})
        print(json.dumps(region, indent=2, default=str))

        print("\n--- Synthesis ---")
        synth = await agent.execute({"type": "synthesize"})
        print(json.dumps(synth, indent=2))

        print("\n--- Think Test (QwQ) ---")
        result = await agent.execute({
            "type": "think",
            "prompt": "Given k69 at 0.72% and k70 at 64.4%, what is the most likely position for k71? Reason step by step."
        })
        print(result.get("analysis", "")[:2000])

    asyncio.run(test())
