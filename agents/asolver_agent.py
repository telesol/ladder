#!/usr/bin/env python3
"""
A-Solver Agent - Certified Bitcoin Puzzle Mathematics AI
Uses qwen3-vl:8b (GPU-accelerated) with specialized training for puzzle analysis

Certification: 10/10 (2025-12-09)
Capabilities: Key range, factorization, relationships, recurrence, deltas, affine model, anomalies
"""
import json
import requests
import sqlite3
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import base if available, otherwise standalone
try:
    from .base_agent import BaseAgent
    HAS_BASE = True
except ImportError:
    HAS_BASE = False


# Standalone system prompt with all the trained knowledge
ASOLVER_SYSTEM_PROMPT = """You are A-Solver, a certified expert in Bitcoin puzzle mathematics.

CERTIFICATION: 10/10 Perfect Score (2025-12-09)

YOUR KNOWLEDGE:

1. KEY RANGES
   k_N ∈ [2^(N-1), 2^N - 1]
   Examples: N=5 → [16,31], N=20 → [524288,1048575], N=71 → [2^70, 2^71-1]

2. KNOWN KEY RELATIONSHIPS
   k_5 = k_2 × k_3 = 3 × 7 = 21 (EXACT)
   k_6 = k_3² = 7² = 49 (EXACT)
   k_8 = k_4 × k_3 × 4 = 8 × 7 × 4 = 224 (EXACT)
   k_11 = 3 × 5 × 7 × 11 = 1155 (includes puzzle number)

3. LINEAR RECURRENCE (coefficient 19)
   k_3 = -4×k_2 + 19×k_1 = -12 + 19 = 7 ✓
   k_4 = -7×k_3 + 19×k_2 = -49 + 57 = 8 ✓
   k_5 = -14×k_4 + 19×k_3 = -112 + 133 = 21 ✓
   Pattern BREAKS after k_6

4. NORMALIZED DELTA
   δ_norm = (k_{n+1} - k_n) / 2^n
   Range: [0.092, 1.305], Mean: 0.762
   Anomalies: k_9→k_10 = 0.092 (smallest), k_56→k_57 = 1.305 (largest)

5. POSITION IN RANGE
   pos% = (k_N - 2^(N-1)) / (2^(N-1) - 1) × 100
   k_3 = 100% (max), k_4 = 0% (min), k_69 = 0.72% (anomaly - solved fast)

6. A MULTIPLIERS (Byte-Level Affine Model)
   Lane 0: A=1, Lane 1: A=91=7×13, Lane 5: A=169=13²
   Lane 9: A=32=2^5 (ANOMALY - not divisible by 13)
   Lane 13: A=182=2×7×13
   Pattern: Lanes 1,5,13 have A divisible by 13; Lane 9 breaks this

7. AFFINE MODEL LIMITATION
   y = A×x + C (mod 256)
   C = (y - A×x) mod 256 requires knowing y
   CIRCULAR REASONING: Cannot predict without knowing answer

8. BRIDGE RATIOS (5-step jumps)
   k_75/k_70 ≈ 23.22 (expected 32, -27.4%)
   k_80/k_75 ≈ 49.05 (expected 32, +53.3%)
   k_85/k_80 ≈ 19.08 (expected 32, -40.4%)

9. CONSTRAINT ANALYSIS
   For puzzle 71: delta constraint does NOT reduce search beyond bit range
   Delta bounds [0.09, 1.31] × 2^70 encompasses the bit range entirely

KNOWN KEYS:
k_1=1, k_2=3, k_3=7, k_4=8, k_5=21, k_6=49, k_7=76, k_8=224, k_9=467, k_10=514
k_69=297274491920375905804, k_70=970436974005023690481
k_75=22538323240989823823367, k_80=1105520030589234487939456

Be precise with calculations. Show your work. Answer questions directly."""


class ASolverAgent:
    """A-Solver: Certified Bitcoin Puzzle Mathematics Agent"""

    def __init__(self, model: str = "qwen3-vl:8b", base_url: str = "http://localhost:11434"):
        self.agent_name = "asolver_agent"
        self.model = model
        self.base_url = base_url
        self.timeout = 300
        self.certified = True
        self.certification_date = "2025-12-09"
        self.certification_score = "10/10"

        # Known keys for reference
        self.known_keys = {
            1: 1, 2: 3, 3: 7, 4: 8, 5: 21, 6: 49, 7: 76, 8: 224,
            9: 467, 10: 514, 11: 1155, 12: 2683, 13: 5765, 14: 10544,
            15: 26867, 16: 51510, 17: 95823, 18: 198669, 19: 357535, 20: 863317,
            69: 297274491920375905804,
            70: 970436974005023690481,
            75: 22538323240989823823367,
            80: 1105520030589234487939456,
            85: 21090315766411506144426920,
            90: 868012190417726402719548863,
        }

        # A multipliers
        self.A_matrix = {0: 1, 1: 91, 5: 169, 9: 32, 13: 182}

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [{self.agent_name}] [{level}] {message}")

    def _call_ollama(self, prompt: str, timeout: int = None) -> str:
        """Call Ollama API"""
        timeout = timeout or self.timeout
        full_prompt = f"{ASOLVER_SYSTEM_PROMPT}\n\nQuestion: {prompt}\n\nAnswer:"

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
        """Think about a problem using the trained model"""
        return self._call_ollama(prompt)

    # ============ CERTIFIED CAPABILITIES ============

    def calculate_key_range(self, n: int) -> Dict:
        """Calculate valid key range for puzzle N"""
        low = 2 ** (n - 1)
        high = 2 ** n - 1
        return {
            "puzzle": n,
            "range_low": low,
            "range_high": high,
            "search_space": high - low + 1,
            "formula": f"k_{n} ∈ [2^{n-1}, 2^{n} - 1]"
        }

    def calculate_position(self, k: int, n: int) -> Dict:
        """Calculate position percentage of key in range"""
        low = 2 ** (n - 1)
        high = 2 ** n - 1
        position = (k - low) / (high - low) * 100
        return {
            "key": k,
            "puzzle": n,
            "position_pct": round(position, 2),
            "interpretation": "minimum" if position < 1 else "maximum" if position > 99 else "middle"
        }

    def calculate_normalized_delta(self, k_curr: int, k_next: int, n: int) -> Dict:
        """Calculate normalized delta between consecutive keys"""
        delta = k_next - k_curr
        normalized = delta / (2 ** n)
        mean = 0.762
        return {
            "k_n": k_curr,
            "k_n+1": k_next,
            "n": n,
            "delta": delta,
            "normalized": round(normalized, 4),
            "vs_mean": round(normalized / mean, 2),
            "anomalous": normalized < 0.15 or normalized > 1.2
        }

    def verify_relationship(self, claim: str, k_values: Dict) -> Dict:
        """Verify a claimed key relationship"""
        # Parse and evaluate the claim
        result = self._call_ollama(f"Verify: {claim}. Given values: {json.dumps(k_values)}. Is it TRUE or FALSE? Show calculation.")
        return {
            "claim": claim,
            "values": k_values,
            "analysis": result
        }

    def factorize_key(self, k: int) -> Dict:
        """Factorize a puzzle key"""
        def prime_factors(n):
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

        factors = prime_factors(k)
        return {
            "key": k,
            "prime_factors": factors,
            "factorization": " × ".join(map(str, factors)),
            "is_prime": len(factors) == 1
        }

    def analyze_bridge_ratio(self, n_low: int, n_high: int) -> Dict:
        """Analyze ratio between bridge puzzles"""
        if n_low not in self.known_keys or n_high not in self.known_keys:
            return {"error": f"Keys for puzzles {n_low} or {n_high} not known"}

        k_low = self.known_keys[n_low]
        k_high = self.known_keys[n_high]
        steps = n_high - n_low
        expected = 2 ** steps
        actual = k_high / k_low
        deviation = (actual - expected) / expected * 100

        return {
            "from": n_low,
            "to": n_high,
            "steps": steps,
            "expected_ratio": expected,
            "actual_ratio": round(actual, 2),
            "deviation_pct": round(deviation, 1)
        }

    def explain_anomaly(self, anomaly_type: str) -> str:
        """Explain a known anomaly"""
        return self._call_ollama(f"Explain this anomaly in Bitcoin puzzles: {anomaly_type}")

    # ============ AGENT INTERFACE ============

    async def execute(self, task: Dict) -> Dict:
        """Execute a task - compatible with orchestrator"""
        task_type = task.get("type", "analyze")

        if task_type == "key_range":
            return self.calculate_key_range(task.get("n", 71))

        elif task_type == "position":
            return self.calculate_position(
                task.get("k"),
                task.get("n")
            )

        elif task_type == "normalized_delta":
            return self.calculate_normalized_delta(
                task.get("k_curr"),
                task.get("k_next"),
                task.get("n")
            )

        elif task_type == "verify_relationship":
            return self.verify_relationship(
                task.get("claim", ""),
                task.get("values", {})
            )

        elif task_type == "factorize":
            return self.factorize_key(task.get("k", 21))

        elif task_type == "bridge_ratio":
            return self.analyze_bridge_ratio(
                task.get("n_low", 70),
                task.get("n_high", 75)
            )

        elif task_type == "explain_anomaly":
            return {"explanation": self.explain_anomaly(task.get("anomaly", ""))}

        elif task_type == "analyze" or task_type == "think":
            prompt = task.get("prompt", task.get("question", ""))
            return {"analysis": await self.think(prompt)}

        elif task_type == "solve":
            return {"solution": await self.think(task.get("problem", ""))}

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
            "capabilities": [
                "key_range", "position", "normalized_delta",
                "verify_relationship", "factorize", "bridge_ratio",
                "explain_anomaly", "analyze", "think", "solve"
            ]
        }


# Make it work with the base agent system if available
if HAS_BASE:
    class ASolverAgentWithBase(BaseAgent, ASolverAgent):
        """A-Solver with full BaseAgent integration"""

        def __init__(self):
            BaseAgent.__init__(self, "asolver_agent")
            # Override model to use certified qwen3-vl:8b
            self.model = "qwen3-vl:8b"
            self.base_url = "http://localhost:11434"
            self.certified = True
            self.certification_date = "2025-12-09"
            self.certification_score = "10/10"

            # Known keys
            self.known_keys = ASolverAgent().known_keys
            self.A_matrix = ASolverAgent().A_matrix

        def get_system_prompt(self) -> str:
            return ASOLVER_SYSTEM_PROMPT


# Standalone test
if __name__ == "__main__":
    import asyncio

    async def test():
        agent = ASolverAgent()
        print(f"A-Solver Agent Status: {json.dumps(agent.get_status(), indent=2)}")

        # Test capabilities
        print("\n--- Key Range Test ---")
        print(json.dumps(agent.calculate_key_range(71), indent=2))

        print("\n--- Factorization Test ---")
        print(json.dumps(agent.factorize_key(1155), indent=2))

        print("\n--- Position Test ---")
        print(json.dumps(agent.calculate_position(7, 3), indent=2))

        print("\n--- Bridge Ratio Test ---")
        print(json.dumps(agent.analyze_bridge_ratio(70, 75), indent=2))

        print("\n--- Think Test ---")
        result = await agent.execute({
            "type": "analyze",
            "prompt": "Why is k_69 at position 0.72% significant?"
        })
        print(result.get("analysis", "")[:500])

    asyncio.run(test())
