#!/usr/bin/env python3
"""
B-Solver Agent - Mathematical Reasoning & Anomaly Detection AI
Uses phi4-reasoning:14b for deep mathematical analysis, drift patterns, and puzzle relations

Focus Areas:
- Mathematical anomalies and outliers
- Drift analysis (how patterns change over puzzle numbers)
- Inter-puzzle relationships
- Statistical analysis and regression
- Number theory patterns
"""
import json
import requests
import sqlite3
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import math

# B-Solver system prompt focused on math reasoning and anomalies
BSOLVER_SYSTEM_PROMPT = """You are B-Solver, a mathematical reasoning AI specialized in Bitcoin puzzle analysis.

SPECIALIZATION: Mathematical Anomalies, Drift Analysis, and Puzzle Relations

YOUR FOCUS AREAS:

1. ANOMALY DETECTION
   - Statistical outliers in key sequences
   - Unexpected patterns or breaks in patterns
   - Keys that don't fit expected distributions
   - Position anomalies (keys at range extremes)

2. DRIFT ANALYSIS
   - How patterns evolve across puzzle numbers
   - Growth rate changes over time
   - Trend analysis in normalized deltas
   - Regime changes in key generation

3. PUZZLE RELATIONS
   - Cross-puzzle dependencies (k_n depends on k_m)
   - Multiplicative relationships (k_a × k_b = k_c)
   - Modular arithmetic patterns
   - Prime factorization connections

4. STATISTICAL ANALYSIS
   - Distribution of keys within ranges
   - Regression analysis on key sequences
   - Correlation between puzzle properties
   - Confidence intervals for predictions

KNOWN DATA:
- Keys k1-k70 are solved
- k69 at position 0.72% (anomaly - near minimum)
- k70 at position 64.4% (mid-range)
- k70/k69 = 3.26 (NOT following doubling pattern)
- Verified: k5=k2×k3, k6=k3², k8=k4×k3×4, k9=2×k8+19

MATHEMATICAL APPROACH:
- Always show calculations step by step
- Quantify uncertainties and confidence levels
- Identify assumptions explicitly
- Consider multiple hypotheses
- Use precise numerical analysis

Be rigorous, skeptical, and mathematically precise."""


class BSolverAgent:
    """B-Solver: Mathematical Reasoning & Anomaly Detection Agent"""

    def __init__(self, model: str = "phi4-reasoning:14b", base_url: str = "http://localhost:11434"):
        self.agent_name = "bsolver_agent"
        self.model = model
        self.base_url = base_url
        self.timeout = 300  # Phi4 may need more time for reasoning
        self.certified = False
        self.certification_date = None
        self.certification_score = None

        # Complete known keys dataset
        self.known_keys = {
            1: 1, 2: 3, 3: 7, 4: 8, 5: 21, 6: 49, 7: 76, 8: 224,
            9: 467, 10: 514, 11: 1155, 12: 2683, 13: 5765, 14: 10544,
            15: 26867, 16: 51510, 17: 95823, 18: 198669, 19: 357535, 20: 863317,
            21: 1811764, 22: 3007503, 23: 5598802, 24: 14428676, 25: 33185509,
            26: 54538862, 27: 111949941, 28: 227634408, 29: 400708894, 30: 1033162084,
            31: 2102388551, 32: 3093472814, 33: 7137437912, 34: 14133072157,
            35: 20112871792, 36: 42387769980, 37: 100251560595, 38: 146971536592,
            39: 323724968937, 40: 1003651412950, 41: 1458252205147, 42: 2895374552463,
            43: 7409811047825, 44: 15404761757071, 45: 19996463086597, 46: 51408670348612,
            47: 119666659114170, 48: 191206974700443, 49: 409118905032525, 50: 611140496167764,
            51: 2058769515153876, 52: 4216495639600700, 53: 6763683971478124,
            54: 9974455244496707, 55: 30045390491869460, 56: 44218742292676575,
            57: 138245758910846492, 58: 199976667976342049, 59: 525070384258266191,
            60: 1135041350219496382, 61: 1425787542618654982, 62: 3908372542507822062,
            63: 8993229949524469768, 64: 17799667357578236628, 65: 30568377312064202855,
            66: 46346217550346335726, 67: 97842531449157303506, 68: 143992573827376775550,
            69: 297274491920375905804, 70: 970436974005023690481
        }

        # Bridge keys
        self.bridge_keys = {
            75: 22538323240989823823367,
            80: 1105520030589234487939456,
            85: 21090315766411506144426920,
            90: 868012190417726402719548863,
        }

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [{self.agent_name}] [{level}] {message}")

    def _call_ollama(self, prompt: str, timeout: int = None) -> str:
        """Call Ollama API with phi4-reasoning"""
        timeout = timeout or self.timeout
        full_prompt = f"{BSOLVER_SYSTEM_PROMPT}\n\nAnalysis Task:\n{prompt}\n\nMathematical Analysis:"

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
        """Think about a mathematical problem"""
        return self._call_ollama(prompt)

    # ============ ANOMALY DETECTION ============

    def detect_delta_anomalies(self, threshold_low: float = 0.15, threshold_high: float = 1.2) -> List[Dict]:
        """Detect anomalous deltas between consecutive keys"""
        anomalies = []
        for n in range(1, 70):
            if n+1 in self.known_keys:
                delta = self.known_keys[n+1] - self.known_keys[n]
                normalized = delta / (2**n)
                if normalized < threshold_low or normalized > threshold_high:
                    anomalies.append({
                        "from": n,
                        "to": n + 1,
                        "delta": delta,
                        "normalized": round(normalized, 4),
                        "type": "low" if normalized < threshold_low else "high"
                    })
        return anomalies

    def detect_position_anomalies(self, threshold_pct: float = 5.0) -> List[Dict]:
        """Detect keys near the edges of their ranges"""
        anomalies = []
        for n in range(1, 71):
            k = self.known_keys[n]
            low = 2**(n-1)
            high = 2**n - 1
            if high > low:
                pos = (k - low) / (high - low) * 100
                if pos < threshold_pct or pos > (100 - threshold_pct):
                    anomalies.append({
                        "puzzle": n,
                        "key": k,
                        "position_pct": round(pos, 4),
                        "type": "near_min" if pos < threshold_pct else "near_max"
                    })
        return anomalies

    def detect_ratio_anomalies(self) -> List[Dict]:
        """Detect anomalous consecutive ratios"""
        anomalies = []
        for n in range(1, 70):
            ratio = self.known_keys[n+1] / self.known_keys[n]
            # Expected ratio is ~2 for doubling pattern
            if ratio < 1.2 or ratio > 3.5:
                anomalies.append({
                    "from": n,
                    "to": n + 1,
                    "ratio": round(ratio, 4),
                    "expected": 2.0,
                    "deviation_pct": round((ratio - 2) / 2 * 100, 1)
                })
        return anomalies

    # ============ DRIFT ANALYSIS ============

    def analyze_drift(self, window_size: int = 10) -> List[Dict]:
        """Analyze how patterns drift over puzzle numbers"""
        drift_data = []

        for start in range(1, 61, window_size):
            end = min(start + window_size - 1, 70)

            # Calculate mean normalized delta for this window
            deltas = []
            for n in range(start, end):
                if n+1 in self.known_keys:
                    delta = self.known_keys[n+1] - self.known_keys[n]
                    normalized = delta / (2**n)
                    deltas.append(normalized)

            if deltas:
                mean_delta = sum(deltas) / len(deltas)
                variance = sum((d - mean_delta)**2 for d in deltas) / len(deltas)

                drift_data.append({
                    "window": f"{start}-{end}",
                    "mean_normalized_delta": round(mean_delta, 4),
                    "variance": round(variance, 4),
                    "std_dev": round(math.sqrt(variance), 4),
                    "sample_size": len(deltas)
                })

        return drift_data

    def analyze_position_drift(self, window_size: int = 10) -> List[Dict]:
        """Analyze how position within range drifts"""
        drift_data = []

        for start in range(1, 61, window_size):
            end = min(start + window_size - 1, 70)

            positions = []
            for n in range(start, end + 1):
                if n in self.known_keys:
                    k = self.known_keys[n]
                    low = 2**(n-1)
                    high = 2**n - 1
                    if high > low:
                        pos = (k - low) / (high - low) * 100
                        positions.append(pos)

            if positions:
                mean_pos = sum(positions) / len(positions)
                drift_data.append({
                    "window": f"{start}-{end}",
                    "mean_position_pct": round(mean_pos, 2),
                    "min_position": round(min(positions), 2),
                    "max_position": round(max(positions), 2),
                    "sample_size": len(positions)
                })

        return drift_data

    # ============ PUZZLE RELATIONS ============

    def find_multiplicative_relations(self, max_n: int = 20) -> List[Dict]:
        """Find k_a × k_b = k_c relationships"""
        relations = []
        for a in range(1, max_n):
            for b in range(a, max_n):
                product = self.known_keys[a] * self.known_keys[b]
                for c in range(max(a, b) + 1, 71):
                    if self.known_keys[c] == product:
                        relations.append({
                            "formula": f"k{a} × k{b} = k{c}",
                            "values": f"{self.known_keys[a]} × {self.known_keys[b]} = {product}",
                            "verified": True
                        })
        return relations

    def find_power_relations(self, max_n: int = 20) -> List[Dict]:
        """Find k_a^p = k_b relationships"""
        relations = []
        for a in range(1, max_n):
            for power in range(2, 5):
                result = self.known_keys[a] ** power
                for b in range(a + 1, 71):
                    if self.known_keys[b] == result:
                        relations.append({
                            "formula": f"k{a}^{power} = k{b}",
                            "values": f"{self.known_keys[a]}^{power} = {result}",
                            "verified": True
                        })
        return relations

    def find_linear_combinations(self, target_n: int) -> List[Dict]:
        """Find linear combinations that produce k_target"""
        target = self.known_keys[target_n]
        combinations = []

        for a in range(1, target_n):
            for b in range(1, target_n):
                for coef_a in range(-10, 11):
                    for coef_b in range(-10, 11):
                        result = coef_a * self.known_keys[a] + coef_b * self.known_keys[b]
                        if result == target and (coef_a != 0 or coef_b != 0):
                            combinations.append({
                                "target": target_n,
                                "formula": f"k{target_n} = {coef_a}×k{a} + {coef_b}×k{b}",
                                "result": target
                            })

        return combinations[:10]  # Limit results

    # ============ STATISTICAL ANALYSIS ============

    def compute_statistics(self) -> Dict:
        """Compute comprehensive statistics on the key sequence"""
        # Normalized deltas
        deltas = []
        for n in range(1, 70):
            if n+1 in self.known_keys:
                delta = self.known_keys[n+1] - self.known_keys[n]
                normalized = delta / (2**n)
                deltas.append(normalized)

        # Positions
        positions = []
        for n in range(1, 71):
            k = self.known_keys[n]
            low = 2**(n-1)
            high = 2**n - 1
            if high > low:
                pos = (k - low) / (high - low) * 100
                positions.append(pos)

        # Consecutive ratios
        ratios = []
        for n in range(1, 70):
            ratio = self.known_keys[n+1] / self.known_keys[n]
            ratios.append(ratio)

        return {
            "normalized_deltas": {
                "mean": round(sum(deltas) / len(deltas), 4),
                "min": round(min(deltas), 4),
                "max": round(max(deltas), 4),
                "std": round(math.sqrt(sum((d - sum(deltas)/len(deltas))**2 for d in deltas) / len(deltas)), 4)
            },
            "positions": {
                "mean": round(sum(positions) / len(positions), 2),
                "min": round(min(positions), 2),
                "max": round(max(positions), 2),
                "near_min_count": sum(1 for p in positions if p < 5),
                "near_max_count": sum(1 for p in positions if p > 95)
            },
            "ratios": {
                "mean": round(sum(ratios) / len(ratios), 4),
                "min": round(min(ratios), 4),
                "max": round(max(ratios), 4)
            }
        }

    # ============ AGENT INTERFACE ============

    async def execute(self, task: Dict) -> Dict:
        """Execute a task"""
        task_type = task.get("type", "analyze")

        if task_type == "detect_anomalies":
            return {
                "delta_anomalies": self.detect_delta_anomalies(),
                "position_anomalies": self.detect_position_anomalies(),
                "ratio_anomalies": self.detect_ratio_anomalies()
            }

        elif task_type == "drift_analysis":
            return {
                "delta_drift": self.analyze_drift(),
                "position_drift": self.analyze_position_drift()
            }

        elif task_type == "find_relations":
            return {
                "multiplicative": self.find_multiplicative_relations(),
                "power": self.find_power_relations(),
                "linear_for_target": self.find_linear_combinations(task.get("target", 7))
            }

        elif task_type == "statistics":
            return self.compute_statistics()

        elif task_type == "analyze" or task_type == "think":
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
            "focus": "Mathematical Reasoning & Anomaly Detection",
            "capabilities": [
                "detect_anomalies", "drift_analysis", "find_relations",
                "statistics", "analyze", "think"
            ]
        }


# Standalone test
if __name__ == "__main__":
    import asyncio

    async def test():
        agent = BSolverAgent()
        print(f"B-Solver Agent Status: {json.dumps(agent.get_status(), indent=2)}")

        print("\n--- Anomaly Detection ---")
        anomalies = await agent.execute({"type": "detect_anomalies"})
        print(f"Delta anomalies: {len(anomalies['delta_anomalies'])}")
        print(f"Position anomalies: {len(anomalies['position_anomalies'])}")

        print("\n--- Drift Analysis ---")
        drift = await agent.execute({"type": "drift_analysis"})
        print(json.dumps(drift["delta_drift"], indent=2))

        print("\n--- Statistics ---")
        stats = await agent.execute({"type": "statistics"})
        print(json.dumps(stats, indent=2))

        print("\n--- Think Test ---")
        result = await agent.execute({
            "type": "analyze",
            "prompt": "Why is k69 at position 0.72% significant? What does this imply for k71?"
        })
        print(result.get("analysis", "")[:1000])

    asyncio.run(test())
