#!/usr/bin/env python3
"""
Math Agent - Handles affine recurrence calculations and drift computation
Runs on Ollama Cloud for heavy mathematical reasoning
"""
import json
import sqlite3
import os
from typing import Dict, List, Optional
from .base_agent import BaseAgent

class MathAgent(BaseAgent):
    """Agent specialized in mathematical computation for the ladder"""

    def __init__(self):
        super().__init__("math_agent")
        self.db_path = self._get_db_path()
        self.calibration = self._load_calibration()

    def _get_db_path(self) -> str:
        """Get path to kh.db"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, self.config['databases']['kh_db'])

    def _load_calibration(self) -> Dict:
        """Load calibration data"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        calib_path = os.path.join(base_dir, "data/calibration/ladder_calib_29_70_full.json")
        try:
            with open(calib_path) as f:
                return json.load(f)
        except FileNotFoundError:
            self.log(f"Calibration file not found: {calib_path}", "WARNING")
            return {}

    def get_puzzle_hex(self, bits: int) -> Optional[str]:
        """Get puzzle hex from database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT actual_hex FROM lcg_residuals WHERE bits = ?", (bits,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    def get_A_matrix(self) -> List[int]:
        """Get A matrix multipliers for all 16 lanes"""
        A = self.calibration.get('A', {})
        return [A.get(str(i), 0) for i in range(16)]

    async def compute_forward_step(self, x_bytes: bytes, block: int = 0) -> bytes:
        """Compute one forward step: y = A*x + C (mod 256)"""
        A = self.get_A_matrix()
        C = self.calibration.get('C', {})

        result = bytearray(16)
        for lane in range(16):
            a = A[lane] & 0xFF
            x = x_bytes[lane]
            # Get drift constant
            c_key = f"{block},{lane},0"
            c = C.get(c_key, 0) if isinstance(C, dict) else 0
            # Affine recurrence
            result[lane] = (a * x + c) & 0xFF

        return bytes(result)

    async def compute_drift_from_bridges(self, bits_a: int, bits_b: int) -> Dict:
        """
        Compute drift constant C[0][l][0] from two bridge puzzles.
        Uses the formula: C = (Y - A^n * X) / (sum of A^i) mod 256
        """
        hex_a = self.get_puzzle_hex(bits_a)
        hex_b = self.get_puzzle_hex(bits_b)

        if not hex_a or not hex_b:
            return {"error": f"Missing puzzle data for bits {bits_a} or {bits_b}"}

        # Extract 16 bytes (32 hex chars after 0x prefix)
        bytes_a = bytes.fromhex(hex_a[2:34]) if hex_a.startswith('0x') else bytes.fromhex(hex_a[:32])
        bytes_b = bytes.fromhex(hex_b[2:34]) if hex_b.startswith('0x') else bytes.fromhex(hex_b[:32])

        if len(bytes_a) != 16 or len(bytes_b) != 16:
            return {"error": f"Invalid byte length: {len(bytes_a)}, {len(bytes_b)}"}

        A = self.get_A_matrix()
        n = bits_b - bits_a  # Number of steps

        drift = []
        for lane in range(16):
            a = A[lane] & 0xFF
            x = bytes_a[lane]
            y = bytes_b[lane]

            # Compute A^n mod 256
            a_n = pow(a, n, 256)

            # Compute sum of A^i for i in 0..n-1
            # This is (A^n - 1) / (A - 1) mod 256, but we compute directly
            coeff_sum = 0
            a_power = 1
            for _ in range(n):
                coeff_sum = (coeff_sum + a_power) & 0xFF
                a_power = (a_power * a) & 0xFF

            # Solve for drift: y = a^n * x + coeff_sum * d (mod 256)
            # d = (y - a^n * x) * inverse(coeff_sum) mod 256
            target = (y - (a_n * x) & 0xFF) & 0xFF

            # Find d such that (coeff_sum * d) mod 256 = target
            found = False
            for d in range(256):
                if ((coeff_sum * d) & 0xFF) == target:
                    drift.append(d)
                    found = True
                    break

            if not found:
                drift.append(-1)  # No solution found
                self.log(f"No drift solution for lane {lane}", "WARNING")

        return {
            "drift": drift,
            "drift_hex": [f"0x{d:02x}" for d in drift],
            "from_bits": bits_a,
            "to_bits": bits_b,
            "steps": n
        }

    async def verify_affine_model(self, start_bits: int, end_bits: int) -> Dict:
        """Verify the affine model over a range of puzzles"""
        results = {
            "total": 0,
            "correct": 0,
            "mismatches": []
        }

        for bits in range(start_bits, end_bits):
            hex_current = self.get_puzzle_hex(bits)
            hex_next = self.get_puzzle_hex(bits + 1)

            if not hex_current or not hex_next:
                continue

            # Get 16 bytes
            current_bytes = bytes.fromhex(hex_current[2:34]) if hex_current.startswith('0x') else bytes.fromhex(hex_current[:32])
            next_bytes = bytes.fromhex(hex_next[2:34]) if hex_next.startswith('0x') else bytes.fromhex(hex_next[:32])

            # Compute expected next
            expected = await self.compute_forward_step(current_bytes, block=0)

            results["total"] += 1
            if expected == next_bytes:
                results["correct"] += 1
            else:
                results["mismatches"].append({
                    "bits": bits,
                    "expected": expected.hex(),
                    "actual": next_bytes.hex()
                })

        results["percentage"] = (results["correct"] / results["total"] * 100) if results["total"] > 0 else 0
        return results

    async def solve_mathematical_problem(self, problem_description: str, context_data: Dict = None) -> Dict:
        """Solve a mathematical problem using intelligent reasoning"""
        context = f"""
Problem: {problem_description}
Context: {json.dumps(context_data) if context_data else 'No additional context'}
A matrix: {self.get_A_matrix()}
Available puzzles: Check database for bits 1-70 and bridges 75,80,85,90,95,100,105,110,115,120,125,130
"""
        analysis = await self.think(context)
        return {
            "success": True,
            "solution": {"mathematical_analysis": analysis, "problem": problem_description},
            "approach": "intelligent_mathematical_reasoning"
        }

    async def test_approach(self, approach: Dict) -> Dict:
        """Test a mathematical approach for viability"""
        context = f"""
Testing approach: {json.dumps(approach)}
A matrix: {self.get_A_matrix()}
Available puzzles: Check database for bits 1-70 and bridges 75,80,85,90,95,100,105,110,115,120,125,130
"""
        analysis = await self.think(context)
        return {
            "promising": "promising" in analysis.lower() or "viable" in analysis.lower(),
            "analysis": analysis,
            "approach": approach
        }

    async def develop_solution(self, approach: Dict) -> Dict:
        """Develop a full solution from a promising approach"""
        context = f"""
Developing solution from approach: {json.dumps(approach)}
A matrix: {self.get_A_matrix()}
Available puzzles: Check database for bits 1-70 and bridges 75,80,85,90,95,100,105,110,115,120,125,130
"""
        analysis = await self.think(context)
        return {
            "success": True,
            "solution": {"developed_solution": analysis, "approach_used": approach},
            "approach": "solution_development"
        }

    async def optimize_solution(self, solution: Dict) -> Dict:
        """Optimize an existing solution"""
        context = f"""
Optimizing solution: {json.dumps(solution)}
A matrix: {self.get_A_matrix()}
Available puzzles: Check database for bits 1-70 and bridges 75,80,85,90,95,100,105,110,115,120,125,130
"""
        analysis = await self.think(context)
        return {
            "improved": "optimized" in analysis.lower() or "improved" in analysis.lower(),
            "optimized_solution": {"original": solution, "optimization": analysis},
            "analysis": analysis
        }

    async def execute(self, task: Dict) -> Dict:
        """Execute a math task"""
        task_type = task.get("type")

        if task_type == "compute_drift":
            bits_a = task.get("bits_a", 75)
            bits_b = task.get("bits_b", 80)
            return await self.compute_drift_from_bridges(bits_a, bits_b)

        elif task_type == "verify":
            start = task.get("start", 1)
            end = task.get("end", 70)
            return await self.verify_affine_model(start, end)

        elif task_type == "forward_step":
            hex_input = task.get("hex_input")
            block = task.get("block", 0)
            if hex_input:
                input_bytes = bytes.fromhex(hex_input.replace("0x", "")[:32])
                result = await self.compute_forward_step(input_bytes, block)
                return {"result_hex": "0x" + result.hex()}

        elif task_type == "analyze":
            # Use LLM for complex analysis
            prompt = task.get("prompt", "")
            context = f"""
Calibration A matrix: {self.get_A_matrix()}
Available puzzles: Check database for bits 1-70 and bridges 75,80,85,90,95,100,105,110,115,120,125,130

Task: {prompt}
"""
            analysis = await self.think(context)
            return {"analysis": analysis}

        elif task_type == "solve":
            return await self.solve_mathematical_problem(task.get("description", ""), task.get("context_data"))
        
        elif task_type == "test_approach":
            return await self.test_approach(task.get("approach", {}))
        
        elif task_type == "develop_solution":
            return await self.develop_solution(task.get("approach", {}))
        
        elif task_type == "optimize_solution":
            return await self.optimize_solution(task.get("solution", {}))

        else:
            return {"error": f"Unknown task type: {task_type}"}


# Standalone execution
if __name__ == "__main__":
    import asyncio

    async def test():
        agent = MathAgent()
        print(f"Math Agent initialized")
        print(f"A matrix: {agent.get_A_matrix()}")

        # Test drift computation
        result = await agent.compute_drift_from_bridges(75, 80)
        print(f"Drift from 75->80: {json.dumps(result, indent=2)}")

    asyncio.run(test())
