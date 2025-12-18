#!/usr/bin/env python3
"""
Verification Agent - Offline Version
Handles verification tasks without Ollama API dependency
"""
import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from .base_agent_offline import BaseAgentOffline

class VerificationAgentOffline(BaseAgentOffline):
    """Agent specialized in verification and validation - offline version"""

    def __init__(self):
        super().__init__("verification_agent")

    def verify_bit_length(self, bits: int) -> Dict:
        """Verify if the bit length is valid"""
        # Bitcoin puzzle ladder typically uses 256-bit addresses
        # Valid bit lengths for the ladder
        valid_lengths = [66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76]
        
        is_valid = bits in valid_lengths
        return {
            "valid": is_valid,
            "bits": bits,
            "valid_range": valid_lengths,
            "message": f"Bit length {bits} is {'valid' if is_valid else 'invalid'}"
        }

    def verify_address_format(self, address: str) -> Dict:
        """Verify Bitcoin address format"""
        # Basic Bitcoin address validation
        if not address or len(address) < 26 or len(address) > 35:
            return {"valid": False, "message": "Invalid address length"}
        
        # Check for valid characters (base58)
        base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        if not all(c in base58_chars for c in address):
            return {"valid": False, "message": "Invalid characters in address"}
        
        return {"valid": True, "message": "Address format appears valid"}

    def verify_hex_format(self, hex_string: str) -> Dict:
        """Verify hexadecimal format"""
        if not hex_string:
            return {"valid": False, "message": "Empty hex string"}
        
        # Remove 0x prefix if present
        hex_clean = hex_string[2:] if hex_string.startswith("0x") else hex_string
        
        # Check for valid hex characters
        if not all(c in "0123456789abcdefABCDEF" for c in hex_clean):
            return {"valid": False, "message": "Invalid hex characters"}
        
        # Check length (should be even for bytes)
        if len(hex_clean) % 2 != 0:
            return {"valid": False, "message": "Hex string length must be even"}
        
        return {"valid": True, "length": len(hex_clean), "message": "Valid hex format"}

    def verify_affine_parameters(self, A_matrix: List[List[int]], C_constants: List[List[List[int]]]) -> Dict:
        """Verify affine recurrence parameters"""
        errors = []
        
        # Check A matrix dimensions
        if len(A_matrix) != 16:
            errors.append("A matrix must have 16 rows (one per lane)")
        
        for i, row in enumerate(A_matrix):
            if len(row) != 16:
                errors.append(f"Row {i} in A matrix must have 16 columns")
        
        # Check C constants dimensions
        if len(C_constants) != 16:  # 16 blocks
            errors.append("C constants must have 16 blocks")
        
        for block_idx, block in enumerate(C_constants):
            if len(block) != 16:  # 16 lanes per block
                errors.append(f"Block {block_idx} must have 16 lanes")
            
            for lane_idx, lane in enumerate(block):
                if not isinstance(lane, list):
                    errors.append(f"Block {block_idx}, lane {lane_idx} must be a list")
        
        # Check value ranges (mod 256)
        for i, row in enumerate(A_matrix):
            for j, val in enumerate(row):
                if val < 0 or val >= 256:
                    errors.append(f"A[{i}][{j}] = {val} must be in range [0, 255]")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "A_matrix_shape": [len(A_matrix), len(A_matrix[0]) if A_matrix else 0],
            "C_constants_shape": [len(C_constants), len(C_constants[0]) if C_constants else 0, len(C_constants[0][0]) if C_constants and C_constants[0] else 0]
        }

    def verify_lcg_parameters(self, seed: int, multiplier: int, increment: int, modulus: int) -> Dict:
        """Verify LCG parameters for validity"""
        errors = []
        
        # Basic parameter checks
        if modulus <= 0:
            errors.append("Modulus must be positive")
        
        if multiplier <= 0 or multiplier >= modulus:
            errors.append(f"Multiplier must be in range (0, {modulus})")
        
        if increment < 0 or increment >= modulus:
            errors.append(f"Increment must be in range [0, {modulus})")
        
        if seed < 0 or seed >= modulus:
            errors.append(f"Seed must be in range [0, {modulus})")
        
        # Check for full period conditions
        full_period = True
        if increment == 0:
            full_period = False
            errors.append("Increment cannot be 0 for full period")
        
        if multiplier - 1 == 0:
            full_period = False
            errors.append("Multiplier - 1 cannot be 0")
        
        # Check if multiplier - 1 is divisible by all prime factors of modulus
        if modulus > 1:
            test_val = multiplier - 1
            temp_mod = modulus
            # Simple factorization check (for small moduli)
            for p in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
                if temp_mod % p == 0:
                    if test_val % p != 0:
                        full_period = False
                        errors.append(f"Multiplier - 1 must be divisible by {p}")
                    while temp_mod % p == 0:
                        temp_mod //= p
        
        return {
            "valid": len(errors) == 0,
            "full_period": full_period,
            "errors": errors,
            "parameters": {
                "seed": seed,
                "multiplier": multiplier,
                "increment": increment,
                "modulus": modulus
            }
        }

    def verify_mathematical_proof(self, proof: Dict) -> Dict:
        """Verify a mathematical proof or derivation"""
        proof_type = proof.get("type", "unknown")
        
        if proof_type == "affine_recurrence":
            return self._verify_affine_proof(proof)
        elif proof_type == "algebraic_exploitation":
            return self._verify_algebraic_proof(proof)
        else:
            return {
                "valid": False,
                "message": f"Unknown proof type: {proof_type}",
                "proof_type": proof_type
            }

    def _verify_affine_proof(self, proof: Dict) -> Dict:
        """Verify affine recurrence proof"""
        required_fields = ["A_matrix", "C_constants", "input_sequence", "output_sequence"]
        
        for field in required_fields:
            if field not in proof:
                return {
                    "valid": False,
                    "message": f"Missing required field: {field}",
                    "missing_field": field
                }
        
        A_matrix = proof["A_matrix"]
        C_constants = proof["C_constants"]
        input_sequence = proof["input_sequence"]
        output_sequence = proof["output_sequence"]
        
        # Verify parameters first
        param_check = self.verify_affine_parameters(A_matrix, C_constants)
        if not param_check["valid"]:
            return {
                "valid": False,
                "message": "Invalid affine parameters",
                "parameter_errors": param_check["errors"]
            }
        
        # Verify the transformation
        errors = []
        for i, (inp, out) in enumerate(zip(input_sequence, output_sequence)):
            # Simple check: output should be transformation of input
            # This is a basic verification - real implementation would be more complex
            if len(inp) != 16 or len(out) != 16:
                errors.append(f"Sequence {i}: input/output must have 16 lanes")
                continue
            
            # Check if transformation is mathematically valid
            # For now, just check that values are in valid range
            for lane in range(16):
                if inp[lane] < 0 or inp[lane] >= 256:
                    errors.append(f"Sequence {i}, lane {lane}: input value {inp[lane]} out of range")
                if out[lane] < 0 or out[lane] >= 256:
                    errors.append(f"Sequence {i}, lane {lane}: output value {out[lane]} out of range")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "sequence_count": len(input_sequence),
            "proof_type": "affine_recurrence"
        }

    def _verify_algebraic_proof(self, proof: Dict) -> Dict:
        """Verify algebraic exploitation proof"""
        required_fields = ["target_lanes", "exploitation_method", "mathematical_steps"]
        
        for field in required_fields:
            if field not in proof:
                return {
                    "valid": False,
                    "message": f"Missing required field: {field}",
                    "missing_field": field
                }
        
        target_lanes = proof["target_lanes"]
        exploitation_method = proof["exploitation_method"]
        mathematical_steps = proof["mathematical_steps"]
        
        # Basic validation
        errors = []
        
        if not isinstance(target_lanes, list) or len(target_lanes) == 0:
            errors.append("target_lanes must be a non-empty list")
        
        for lane in target_lanes:
            if not isinstance(lane, int) or lane < 0 or lane >= 16:
                errors.append(f"Invalid lane number: {lane}")
        
        if exploitation_method not in ["backward_solving", "forward_prediction", "cross_lane_analysis"]:
            errors.append(f"Unknown exploitation method: {exploitation_method}")
        
        if not isinstance(mathematical_steps, list) or len(mathematical_steps) == 0:
            errors.append("mathematical_steps must be a non-empty list")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "target_lanes": target_lanes,
            "exploitation_method": exploitation_method,
            "step_count": len(mathematical_steps),
            "proof_type": "algebraic_exploitation"
        }

    async def verify_approach(self, approach: Dict) -> Dict:
        """Verify if a mathematical approach is sound"""
        approach_type = approach.get("type", "unknown")
        
        if approach_type == "algebraic_exploitation":
            return await self._verify_algebraic_approach(approach)
        elif approach_type == "statistical_analysis":
            return await self._verify_statistical_approach(approach)
        else:
            return {
                "valid": False,
                "confidence": 0.0,
                "message": f"Unknown approach type: {approach_type}",
                "approach_type": approach_type
            }

    async def _verify_algebraic_approach(self, approach: Dict) -> Dict:
        """Verify algebraic exploitation approach"""
        # Check required components
        required_fields = ["target_lanes", "method", "expected_complexity"]
        
        for field in required_fields:
            if field not in approach:
                return {
                    "valid": False,
                    "confidence": 0.0,
                    "message": f"Missing required field: {field}",
                    "missing_field": field
                }
        
        target_lanes = approach["target_lanes"]
        method = approach["method"]
        expected_complexity = approach["expected_complexity"]
        
        # Basic validation
        errors = []
        confidence = 0.5  # Base confidence
        
        # Validate target lanes
        if not isinstance(target_lanes, list):
            errors.append("target_lanes must be a list")
        else:
            for lane in target_lanes:
                if not isinstance(lane, int) or lane < 0 or lane >= 16:
                    errors.append(f"Invalid lane number: {lane}")
        
        # Validate method
        valid_methods = ["backward_solving", "forward_prediction", "cross_lane_analysis", "matrix_inversion"]
        if method not in valid_methods:
            errors.append(f"Unknown method: {method}")
        else:
            # Increase confidence for known good methods
            if method in ["backward_solving", "cross_lane_analysis"]:
                confidence += 0.2
        
        # Validate complexity
        if not isinstance(expected_complexity, (int, float)) or expected_complexity <= 0:
            errors.append("expected_complexity must be a positive number")
        
        # Mathematical soundness check
        if method == "backward_solving" and len(target_lanes) <= 4:
            confidence += 0.2  # Backward solving with few lanes is promising
        elif method == "cross_lane_analysis" and len(target_lanes) >= 8:
            confidence += 0.15  # Cross-lane with many lanes can work
        
        return {
            "valid": len(errors) == 0,
            "confidence": min(confidence, 1.0),
            "errors": errors,
            "approach_type": "algebraic_exploitation",
            "recommendation": "Proceed with implementation and testing" if len(errors) == 0 else "Fix issues before proceeding"
        }

    async def _verify_statistical_approach(self, approach: Dict) -> Dict:
        """Verify statistical analysis approach"""
        required_fields = ["sample_size", "confidence_threshold", "statistical_method"]
        
        for field in required_fields:
            if field not in approach:
                return {
                    "valid": False,
                    "confidence": 0.0,
                    "message": f"Missing required field: {field}",
                    "missing_field": field
                }
        
        sample_size = approach["sample_size"]
        confidence_threshold = approach["confidence_threshold"]
        statistical_method = approach["statistical_method"]
        
        errors = []
        confidence = 0.6  # Base confidence for statistical methods
        
        # Validate parameters
        if not isinstance(sample_size, int) or sample_size <= 0:
            errors.append("sample_size must be a positive integer")
        
        if not isinstance(confidence_threshold, (int, float)) or confidence_threshold <= 0 or confidence_threshold >= 1:
            errors.append("confidence_threshold must be in range (0, 1)")
        
        valid_methods = ["regression", "correlation", "hypothesis_testing", "pattern_recognition"]
        if statistical_method not in valid_methods:
            errors.append(f"Unknown statistical method: {statistical_method}")
        
        # Sample size adequacy
        if sample_size >= 100:
            confidence += 0.2
        elif sample_size >= 50:
            confidence += 0.1
        
        return {
            "valid": len(errors) == 0,
            "confidence": min(confidence, 1.0),
            "errors": errors,
            "approach_type": "statistical_analysis",
            "sample_adequacy": "adequate" if sample_size >= 30 else "may need more samples"
        }

    async def execute(self, task: Dict) -> Dict:
        """Execute a verification task"""
        task_type = task.get("type")

        if task_type == "verify_bit_length":
            bits = task.get("bits", 0)
            return self.verify_bit_length(bits)

        elif task_type == "verify_address":
            address = task.get("address", "")
            return self.verify_address_format(address)

        elif task_type == "verify_hex":
            hex_string = task.get("hex", "")
            return self.verify_hex_format(hex_string)

        elif task_type == "verify_affine_params":
            A_matrix = task.get("A_matrix", [])
            C_constants = task.get("C_constants", [])
            return self.verify_affine_parameters(A_matrix, C_constants)

        elif task_type == "verify_lcg":
            seed = task.get("seed", 0)
            multiplier = task.get("multiplier", 0)
            increment = task.get("increment", 0)
            modulus = task.get("modulus", 256)
            return self.verify_lcg_parameters(seed, multiplier, increment, modulus)

        elif task_type == "verify_proof":
            proof = task.get("proof", {})
            return self.verify_mathematical_proof(proof)

        elif task_type == "verify_approach":
            approach = task.get("approach", {})
            return await self.verify_approach(approach)

        elif task_type == "verify_solution":
            solution = task.get("solution", {})
            return await self.verify_solution(solution)

        elif task_type == "full_verification":
            # Comprehensive verification
            return await self._full_verification(task)

        else:
            return {"error": f"Unknown verification task: {task_type}"}

    async def verify_solution(self, solution: Dict) -> Dict:
        """Verify a complete solution"""
        required_fields = ["approach", "implementation", "test_results"]
        
        for field in required_fields:
            if field not in solution:
                return {
                    "valid": False,
                    "confidence": 0.0,
                    "message": f"Missing required field: {field}",
                    "missing_field": field
                }
        
        approach = solution["approach"]
        implementation = solution["implementation"]
        test_results = solution["test_results"]
        
        # Verify the approach
        approach_verification = await self.verify_approach(approach)
        
        # Verify implementation basics
        implementation_valid = True
        implementation_errors = []
        
        if not isinstance(implementation, dict):
            implementation_valid = False
            implementation_errors.append("Implementation must be a dictionary")
        
        if not isinstance(test_results, dict):
            implementation_valid = False
            implementation_errors.append("Test results must be a dictionary")
        
        # Overall assessment
        valid = approach_verification["valid"] and implementation_valid
        confidence = approach_verification.get("confidence", 0.0) * 0.7  # Weight approach heavily
        
        if implementation_valid:
            confidence += 0.3  # Boost for valid implementation
        
        return {
            "valid": valid,
            "confidence": min(confidence, 1.0),
            "approach_verification": approach_verification,
            "implementation_valid": implementation_valid,
            "implementation_errors": implementation_errors,
            "recommendation": "Solution appears viable" if valid else "Issues need to be addressed"
        }

    async def _full_verification(self, task: Dict) -> Dict:
        """Perform comprehensive verification"""
        # This would verify multiple aspects of the system
        verification_results = {
            "timestamp": datetime.now().isoformat(),
            "comprehensive": True,
            "components": {}
        }
        
        # Verify affine parameters if provided
        if "A_matrix" in task and "C_constants" in task:
            verification_results["components"]["affine_params"] = self.verify_affine_parameters(
                task["A_matrix"], task["C_constants"]
            )
        
        # Verify approach if provided
        if "approach" in task:
            verification_results["components"]["approach"] = await self.verify_approach(task["approach"])
        
        # Verify solution if provided
        if "solution" in task:
            verification_results["components"]["solution"] = await self.verify_solution(task["solution"])
        
        # Overall assessment
        all_valid = all(comp.get("valid", False) for comp in verification_results["components"].values())
        verification_results["overall_valid"] = all_valid
        
        return verification_results


# Standalone execution
if __name__ == "__main__":
    import asyncio

    async def test():
        agent = VerificationAgentOffline()
        print("Verification Agent Offline initialized")

        # Test bit length verification
        result = agent.verify_bit_length(66)
        print(f"Bit length verification: {json.dumps(result, indent=2)}")

        # Test affine parameter verification
        A_matrix = [[1 if i == j else 0 for j in range(16)] for i in range(16)]
        C_constants = [[[0 for occ in range(4)] for lane in range(16)] for block in range(16)]
        result = agent.verify_affine_parameters(A_matrix, C_constants)
        print(f"Affine parameters verification: {json.dumps(result, indent=2)}")

    asyncio.run(test())
