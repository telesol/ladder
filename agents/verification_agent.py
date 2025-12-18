#!/usr/bin/env python3
"""
Verification Agent - Handles Bitcoin address verification and cryptographic validation
Ensures all predictions are cryptographically correct before acceptance
"""
import json
from log_integration import get_system_logger, get_ai_logger, get_memory_logger
import hashlib
import sqlite3
import os
from typing import Dict, Optional, Tuple
from .base_agent import BaseAgent

# Bitcoin address generation imports
try:
    import ecdsa
    import base58
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

class VerificationAgent(BaseAgent):
    """Agent specialized in cryptographic verification"""

    def __init__(self):
        super().__init__("verification_agent")
        self.db_path = self._get_db_path()

    def _get_db_path(self) -> str:
        """Get path to kh.db"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, self.config['databases']['kh_db'])

    def privkey_to_pubkey(self, privkey_hex: str) -> Tuple[str, str]:
        """
        Convert private key to public key (uncompressed and compressed)
        Pure Python implementation - no external dependencies
        """
        # secp256k1 parameters
        P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
        N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
        Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

        def modinv(a, m):
            """Modular inverse using extended Euclidean algorithm"""
            if a < 0:
                a = a % m
            g, x, _ = extended_gcd(a, m)
            if g != 1:
                raise Exception('Modular inverse does not exist')
            return x % m

        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y

        def point_add(p1, p2):
            if p1 is None:
                return p2
            if p2 is None:
                return p1
            x1, y1 = p1
            x2, y2 = p2
            if x1 == x2 and y1 != y2:
                return None
            if x1 == x2:
                m = (3 * x1 * x1) * modinv(2 * y1, P) % P
            else:
                m = (y2 - y1) * modinv(x2 - x1, P) % P
            x3 = (m * m - x1 - x2) % P
            y3 = (m * (x1 - x3) - y1) % P
            return (x3, y3)

        def scalar_mult(k, point):
            result = None
            addend = point
            while k:
                if k & 1:
                    result = point_add(result, addend)
                addend = point_add(addend, addend)
                k >>= 1
            return result

        # Parse private key
        privkey = int(privkey_hex.replace("0x", ""), 16)

        # Compute public key point
        pub_point = scalar_mult(privkey, (Gx, Gy))
        if pub_point is None:
            raise ValueError("Invalid private key")

        x, y = pub_point

        # Uncompressed public key (04 + x + y)
        pubkey_uncompressed = "04" + format(x, '064x') + format(y, '064x')

        # Compressed public key (02/03 + x)
        prefix = "02" if y % 2 == 0 else "03"
        pubkey_compressed = prefix + format(x, '064x')

        return pubkey_uncompressed, pubkey_compressed

    def pubkey_to_address(self, pubkey_hex: str) -> str:
        """Convert public key to Bitcoin address (P2PKH)"""
        # SHA256
        sha256_hash = hashlib.sha256(bytes.fromhex(pubkey_hex)).digest()

        # RIPEMD160
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        pubkey_hash = ripemd160.digest()

        # Add version byte (0x00 for mainnet)
        versioned = b'\x00' + pubkey_hash

        # Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

        # Base58Check encode
        address_bytes = versioned + checksum
        return self._base58_encode(address_bytes)

    def _base58_encode(self, data: bytes) -> str:
        """Base58 encode bytes"""
        ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

        # Count leading zeros
        leading_zeros = 0
        for byte in data:
            if byte == 0:
                leading_zeros += 1
            else:
                break

        # Convert to integer
        num = int.from_bytes(data, 'big')

        # Convert to base58
        result = ''
        while num > 0:
            num, remainder = divmod(num, 58)
            result = ALPHABET[remainder] + result

        # Add leading '1's for each leading zero byte
        return '1' * leading_zeros + result

    def validate_private_key(self, privkey_hex: str, expected_bits: int) -> Dict:
        """
        Validate a private key:
        1. Check bit length matches expected
        2. Generate public key
        3. Generate address
        4. Return validation result
        """
        try:
            # Clean hex
            privkey_hex = privkey_hex.replace("0x", "").lower()

            # Check bit length
            privkey_int = int(privkey_hex, 16)
            actual_bits = privkey_int.bit_length()

            if actual_bits != expected_bits:
                return {
                    "valid": False,
                    "error": f"Bit length mismatch: expected {expected_bits}, got {actual_bits}",
                    "privkey": privkey_hex
                }

            # Generate public keys
            pubkey_uncompressed, pubkey_compressed = self.privkey_to_pubkey(privkey_hex)

            # Generate addresses
            address_uncompressed = self.pubkey_to_address(pubkey_uncompressed)
            address_compressed = self.pubkey_to_address(pubkey_compressed)

            return {
                "valid": True,
                "privkey_hex": "0x" + privkey_hex,
                "bits": actual_bits,
                "pubkey_uncompressed": pubkey_uncompressed,
                "pubkey_compressed": pubkey_compressed,
                "address_uncompressed": address_uncompressed,
                "address_compressed": address_compressed
            }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "privkey": privkey_hex
            }

    def verify_against_known(self, privkey_hex: str, expected_address: str) -> Dict:
        """Verify a private key generates the expected address"""
        validation = self.validate_private_key(privkey_hex, 0)  # Skip bit check

        if not validation["valid"]:
            return validation

        # Check if either address matches
        if (validation["address_compressed"] == expected_address or
            validation["address_uncompressed"] == expected_address):
            return {
                "verified": True,
                "match_type": "compressed" if validation["address_compressed"] == expected_address else "uncompressed",
                **validation
            }
        else:
            return {
                "verified": False,
                "error": "Address mismatch",
                "expected": expected_address,
                "got_compressed": validation["address_compressed"],
                "got_uncompressed": validation["address_uncompressed"],
                **validation
            }

    def get_known_address(self, bits: int) -> Optional[str]:
        """Get known address for a puzzle from database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT address FROM puzzles WHERE bits = ?", (bits,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    async def verify_solution(self, solution: Dict) -> Dict:
        """Verify a mathematical solution for validity"""
        context = f"""
Verifying solution: {json.dumps(solution)}
Available verification methods: validate_private_key, verify_against_known, full_verify
"""
        analysis = await self.think(context)
        
        # Extract key information for verification
        if 'privkey' in solution:
            privkey = solution['privkey']
            bits = solution.get('bits', 0)
            validation = self.validate_private_key(privkey, bits)
            return {
                "valid": validation.get("valid", False),
                "verification_type": "private_key_validation",
                "details": validation,
                "analysis": analysis
            }
        elif 'solution_data' in solution:
            # Generic solution verification
            return {
                "valid": "valid" in analysis.lower() or "correct" in analysis.lower(),
                "verification_type": "solution_analysis",
                "analysis": analysis
            }
        else:
            return {
                "valid": False,
                "verification_type": "unknown_solution_format",
                "error": "Solution format not recognized",
                "analysis": analysis
            }

    async def execute(self, task: Dict) -> Dict:
        """Execute a verification task"""
        task_type = task.get("type")

        if task_type == "validate":
            privkey = task.get("privkey")
            bits = task.get("bits", 0)
            return self.validate_private_key(privkey, bits)

        elif task_type == "verify_against_known":
            privkey = task.get("privkey")
            expected = task.get("expected_address")
            return self.verify_against_known(privkey, expected)

        elif task_type == "full_verify":
            # Full verification: validate + check against known
            privkey = task.get("privkey")
            bits = task.get("bits")

            validation = self.validate_private_key(privkey, bits)
            if not validation["valid"]:
                return validation

            known_address = self.get_known_address(bits)
            if known_address:
                return self.verify_against_known(privkey, known_address)
            else:
                return {
                    **validation,
                    "known_address": None,
                    "note": f"No known address for puzzle {bits} to verify against"
                }

        elif task_type == "verify_solution":
            solution = task.get("solution", {})
            return await self.verify_solution(solution)

        elif task_type == "analyze":
            # Use LLM for complex cryptographic analysis
            prompt = task.get("prompt", "")
            analysis = await self.think(f"Cryptographic analysis task: {prompt}")
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
        agent = VerificationAgent()
        print("Verification Agent initialized")

        # Test with known puzzle 1 (1 bit = 1)
        result = agent.validate_private_key("0x1", 1)
        print(f"Puzzle 1 validation: {json.dumps(result, indent=2)}")

        # Test with puzzle 10 (10 bits)
        result = agent.validate_private_key("0x357", 10)
        print(f"Puzzle 10 validation: {json.dumps(result, indent=2)}")

    asyncio.run(test())
