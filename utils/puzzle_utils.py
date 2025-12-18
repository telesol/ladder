#!/usr/bin/env python3
"""
Puzzle Utilities - Flexible target puzzle management
Works with ANY puzzle number, not hardcoded to specific puzzles.

Usage:
    from utils.puzzle_utils import PuzzleConfig

    config = PuzzleConfig()
    target = config.get_target_puzzle()  # Returns first unsolved (e.g., 71)

    # Or set specific target
    config.set_target_puzzle(72)
"""
import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "puzzle_config.json"


class PuzzleConfig:
    """Puzzle-agnostic configuration manager"""

    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else CONFIG_PATH
        self.config = self._load_config()

        # Parse known keys (JSON stores keys as strings)
        self.known_keys = {int(k): int(v) for k, v in self.config.get("known_keys", {}).items()}
        self.bridge_keys = {int(k): int(v) for k, v in self.config.get("bridge_keys", {}).items()}
        self.solved_puzzles = sorted(self.config.get("solved_puzzles", list(range(1, 71))))

    def _load_config(self) -> Dict:
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {}

    def _save_config(self):
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_target_puzzle(self) -> int:
        """Get target puzzle number (first unsolved if not specified)"""
        target = self.config.get("target_puzzle")
        if target:
            return int(target)
        # Auto-detect: first unsolved puzzle
        return max(self.solved_puzzles) + 1

    def set_target_puzzle(self, n: int):
        """Set target puzzle number"""
        self.config["target_puzzle"] = n
        self._save_config()

    def mark_solved(self, n: int, key: int):
        """Mark a puzzle as solved and record its key"""
        if n not in self.solved_puzzles:
            self.solved_puzzles.append(n)
            self.solved_puzzles.sort()
            self.config["solved_puzzles"] = self.solved_puzzles

        self.known_keys[n] = key
        self.config["known_keys"][str(n)] = key

        # Auto-update target to next unsolved
        if self.config.get("target_puzzle") == n:
            self.config["target_puzzle"] = None

        self._save_config()

    def get_key(self, n: int) -> Optional[int]:
        """Get known key for puzzle N"""
        return self.known_keys.get(n) or self.bridge_keys.get(n)

    def get_last_solved_key(self) -> Tuple[int, int]:
        """Get last solved puzzle number and its key"""
        n = max(self.solved_puzzles)
        return n, self.known_keys[n]

    def get_range(self, n: int) -> Tuple[int, int]:
        """Get key range for puzzle N: [2^(N-1), 2^N - 1]"""
        low = 2 ** (n - 1)
        high = 2 ** n - 1
        return low, high

    def get_position(self, n: int, key: int = None) -> float:
        """Get position percentage of key in its range"""
        key = key or self.get_key(n)
        if not key:
            return None
        low, high = self.get_range(n)
        if high <= low:
            return 0.0
        return (key - low) / (high - low) * 100

    def predict_search_region(self, n: int = None) -> Dict:
        """Predict optimal search region for puzzle N based on patterns"""
        n = n or self.get_target_puzzle()
        low, high = self.get_range(n)
        range_size = high - low

        # Get previous puzzle's key for delta analysis
        prev_n = n - 1
        prev_key = self.get_key(prev_n)

        # Historical patterns
        patterns = {
            "near_minimum": [4, 10, 69],  # Keys near 0%
            "mid_range": [70],  # Keys around 50%
        }

        result = {
            "target_puzzle": n,
            "range": {"low": low, "high": high, "bits": n},
            "strategies": []
        }

        # Strategy 1: Near minimum (like k69)
        region_1pct = low + int(range_size * 0.01)
        result["strategies"].append({
            "name": "Near Minimum (k69 pattern)",
            "priority": "HIGH",
            "range_start": low,
            "range_end": region_1pct,
            "coverage": "First 1%",
            "rationale": "k69 at 0.72%, k4 at 0%, k10 at 0.39%"
        })

        # Strategy 2: Divisibility check
        if n > 1:
            # First number in range divisible by N
            first_div = ((low // n) + 1) * n
            if first_div < high:
                result["strategies"].append({
                    "name": f"Divisible by {n}",
                    "priority": "MEDIUM",
                    "first_candidate": first_div,
                    "rationale": f"k4%4=0, k8%8=0, k11%11=0 pattern"
                })

        # Strategy 3: Delta bounds
        if prev_key:
            min_delta = int(0.09 * (2 ** (n - 1)))
            max_delta = int(1.31 * (2 ** (n - 1)))
            result["strategies"].append({
                "name": "Delta Bounds",
                "priority": "MEDIUM",
                "range_start": prev_key + min_delta,
                "range_end": min(prev_key + max_delta, high),
                "rationale": "Historical delta range: 0.09 to 1.31 × 2^(N-1)"
            })

        return result


def get_puzzle_summary(n: int = None) -> str:
    """Get human-readable summary for target puzzle"""
    config = PuzzleConfig()
    n = n or config.get_target_puzzle()

    low, high = config.get_range(n)
    prev_n, prev_key = config.get_last_solved_key()

    summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    PUZZLE {n} ANALYSIS                        ║
╠══════════════════════════════════════════════════════════════╣
║ Bit Range: {n}-bit keys
║ Search Space: [{low:,}]
║              to [{high:,}]
║
║ Last Solved: Puzzle {prev_n}
║ k{prev_n} = {prev_key}
║ k{prev_n} position: {config.get_position(prev_n):.2f}%
╚══════════════════════════════════════════════════════════════╝
"""
    return summary


# Convenience functions
def get_target() -> int:
    """Get current target puzzle number"""
    return PuzzleConfig().get_target_puzzle()

def get_range(n: int = None) -> Tuple[int, int]:
    """Get range for puzzle N"""
    config = PuzzleConfig()
    return config.get_range(n or config.get_target_puzzle())

def mark_solved(n: int, key: int):
    """Mark puzzle N as solved with key"""
    PuzzleConfig().mark_solved(n, key)


if __name__ == "__main__":
    # Test
    config = PuzzleConfig()
    print(f"Target puzzle: {config.get_target_puzzle()}")
    print(f"Last solved: {config.get_last_solved_key()}")
    print(get_puzzle_summary())

    prediction = config.predict_search_region()
    print(f"\nSearch strategies for puzzle {prediction['target_puzzle']}:")
    for s in prediction["strategies"]:
        print(f"  - {s['name']} ({s['priority']}): {s['rationale']}")
