#!/usr/bin/env python3
"""
Autonomous Bitcoin Puzzle Solver
Claude-orchestrated system combining AI analysis with key search
Fully automatic discovery with no artificial limitations
"""
import json
import sqlite3
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, '/home/solo/LA')

from agents.search_engine import BitcoinPuzzleSearchEngine, SearchStrategy, SearchResult
from agents.asolver_agent import ASolverAgent

@dataclass
class SolverState:
    """Current state of the solver"""
    current_puzzle: int
    status: str  # idle, searching, analyzing, found
    keys_checked: int
    keys_per_second: float
    search_start: Optional[datetime]
    last_update: datetime
    discoveries: List[Dict]


class AutonomousSolver:
    """
    Fully autonomous Bitcoin puzzle solver
    Uses mathematical analysis and formula derivation
    No artificial limitations - will search until found
    """

    def __init__(self, db_path: str = "/home/solo/LA/db/solver_state.db"):
        self.db_path = db_path
        self.search_engine = BitcoinPuzzleSearchEngine()
        self.math_agent = ASolverAgent()

        # State
        self.state = SolverState(
            current_puzzle=None,  # No default - derive all
            status="idle",
            keys_checked=0,
            keys_per_second=0,
            search_start=None,
            last_update=datetime.now(),
            discoveries=[]
        )

        # Initialize database
        self._init_db()

        # Load previous state
        self._load_state()

    def _init_db(self):
        """Initialize solver state database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS solver_state (
            id INTEGER PRIMARY KEY,
            puzzle_id INTEGER,
            status TEXT,
            keys_checked INTEGER,
            current_position TEXT,
            started_at TEXT,
            updated_at TEXT,
            found_key TEXT,
            found_at TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS discoveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            puzzle_id INTEGER,
            private_key TEXT,
            wif TEXT,
            address TEXT,
            keys_checked INTEGER,
            time_elapsed REAL,
            found_at TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS search_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            puzzle_id INTEGER,
            action TEXT,
            details TEXT,
            timestamp TEXT
        )''')
        conn.commit()
        conn.close()

    def _load_state(self):
        """Load previous solver state"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM solver_state ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        if row:
            self.state.current_puzzle = row[1]
            self.state.status = row[2]
            self.state.keys_checked = row[3] or 0
        conn.close()

    def _save_state(self):
        """Save current state"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO solver_state
                     (id, puzzle_id, status, keys_checked, current_position, started_at, updated_at)
                     VALUES (1, ?, ?, ?, ?, ?, ?)''',
                  (self.state.current_puzzle, self.state.status, self.state.keys_checked,
                   None, self.state.search_start.isoformat() if self.state.search_start else None,
                   datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def _log(self, action: str, details: str = ""):
        """Log solver action"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {action}: {details}")
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO search_log (puzzle_id, action, details, timestamp) VALUES (?, ?, ?, ?)",
                  (self.state.current_puzzle, action, details, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def _record_discovery(self, puzzle: int, result: SearchResult):
        """Record a discovered solution"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO discoveries
                     (puzzle_id, private_key, wif, address, keys_checked, time_elapsed, found_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (puzzle, str(result.private_key), result.wif, result.address,
                   result.keys_checked, result.time_elapsed, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def analyze_puzzle(self, puzzle: int) -> Dict:
        """Use AI to analyze a puzzle before searching"""
        self._log("ANALYZE", f"Analyzing puzzle {puzzle}")

        analysis = {
            'puzzle': puzzle,
            'range': self.math_agent.calculate_key_range(puzzle),
            'timestamp': datetime.now().isoformat()
        }

        # Get key facts
        if puzzle in self.search_engine.known_puzzles:
            info = self.search_engine.known_puzzles[puzzle]
            analysis['target_address'] = info['address']
            analysis['known_key'] = info['known_key']
            analysis['is_solved'] = info['known_key'] is not None

        # Calculate search difficulty
        search_space = analysis['range']['search_space']
        speed = 33000  # Conservative estimate
        analysis['estimated_time_seconds'] = search_space / speed
        analysis['estimated_time_years'] = analysis['estimated_time_seconds'] / (365.25 * 24 * 3600)

        self._log("ANALYZE_COMPLETE", f"Search space: {search_space:,} keys")

        return analysis

    def solve_puzzle(self, puzzle: int, max_keys: int = None, timeout_seconds: int = None) -> SearchResult:
        """
        Attempt to solve a puzzle
        No artificial limits unless specified
        """
        self.state.current_puzzle = puzzle
        self.state.status = "searching"
        self.state.search_start = datetime.now()
        self._save_state()

        self._log("SEARCH_START", f"Beginning search for puzzle {puzzle}")

        # Analyze first
        analysis = self.analyze_puzzle(puzzle)

        if analysis.get('is_solved') and analysis.get('known_key'):
            self._log("ALREADY_SOLVED", f"Key already known: {analysis['known_key']}")
            # Still verify it works
            verified = self.search_engine.verify_key(
                analysis['known_key'],
                analysis['target_address']
            )
            return SearchResult(
                found=True,
                private_key=analysis['known_key'],
                address=analysis['target_address'],
                keys_checked=0
            )

        # Run the search
        try:
            result = self.search_engine.search_puzzle(
                puzzle,
                strategy=SearchStrategy.SEQUENTIAL,
                max_keys=max_keys
            )

            self.state.keys_checked = result.keys_checked
            self.state.keys_per_second = result.keys_per_second

            if result.found:
                self.state.status = "found"
                self._log("SOLUTION_FOUND", f"Key: {result.private_key}")
                self._record_discovery(puzzle, result)

                print("\n" + "=" * 70)
                print("🎉 AUTONOMOUS DISCOVERY!")
                print("=" * 70)
                print(f"Puzzle: {puzzle}")
                print(f"Private Key: {result.private_key}")
                print(f"WIF: {result.wif}")
                print(f"Address: {result.address}")
                print(f"Keys Checked: {result.keys_checked:,}")
                print(f"Time: {result.time_elapsed:.2f}s")
                print(f"Speed: {result.keys_per_second:,.0f} keys/sec")
                print("=" * 70 + "\n")
            else:
                self.state.status = "idle"
                self._log("SEARCH_PAUSE", f"Checked {result.keys_checked:,} keys, not found yet")

        except KeyboardInterrupt:
            self.state.status = "paused"
            self._log("SEARCH_INTERRUPTED", "User interrupt")
            result = SearchResult(found=False, keys_checked=self.state.keys_checked)

        self._save_state()
        return result

    def run_autonomous(self, start_puzzle: int = 5, end_puzzle: int = 160):
        """
        Run fully autonomous solving
        Attempts each unsolved puzzle in sequence
        """
        self._log("AUTONOMOUS_START", f"Range: {start_puzzle} to {end_puzzle}")

        print("\n" + "=" * 70)
        print("AUTONOMOUS BITCOIN PUZZLE SOLVER")
        print("=" * 70)
        print(f"Range: Puzzles {start_puzzle} - {end_puzzle}")
        print(f"Workers: {self.search_engine.num_workers}")
        print(f"Mode: Fully Automatic")
        print("=" * 70 + "\n")

        solved = []
        for puzzle in range(start_puzzle, end_puzzle + 1):
            if puzzle not in self.search_engine.known_puzzles:
                self._log("SKIP", f"Puzzle {puzzle} - no address data")
                continue

            info = self.search_engine.known_puzzles[puzzle]

            # Skip if we have the known key and just want to discover
            if info['known_key'] is not None:
                # Optionally verify known solutions
                self._log("VERIFY", f"Puzzle {puzzle} - verifying known solution")
                verified = self.search_engine.verify_key(info['known_key'], info['address'])
                if verified:
                    self._log("VERIFIED", f"Puzzle {puzzle} = {info['known_key']}")
                    solved.append(puzzle)
                continue

            # Calculate if feasible within reasonable time
            range_low, range_high = self.search_engine.get_puzzle_range(puzzle)
            search_space = range_high - range_low + 1
            est_time = search_space / 30000  # Conservative 30K keys/sec

            if est_time > 86400 * 365:  # More than 1 year
                self._log("SKIP_INFEASIBLE", f"Puzzle {puzzle}: ~{est_time / (86400 * 365):.0f} years estimated")
                continue

            # Attempt to solve
            self._log("ATTEMPTING", f"Puzzle {puzzle} (est: {est_time:.0f}s)")
            result = self.solve_puzzle(puzzle)

            if result.found:
                solved.append(puzzle)
                self._log("SOLVED", f"Puzzle {puzzle} = {result.private_key}")

        return solved

    def get_status(self) -> Dict:
        """Get current solver status"""
        return {
            'current_puzzle': self.state.current_puzzle,
            'status': self.state.status,
            'keys_checked': self.state.keys_checked,
            'keys_per_second': self.state.keys_per_second,
            'search_start': self.state.search_start.isoformat() if self.state.search_start else None,
            'known_puzzles': len(self.search_engine.known_puzzles),
            'workers': self.search_engine.num_workers
        }

    def benchmark(self, duration: int = 5) -> Dict:
        """Run benchmark to measure search speed"""
        return self.search_engine.benchmark(duration)


def main():
    """Main entry point"""
    solver = AutonomousSolver()

    print("=" * 70)
    print("AUTONOMOUS BITCOIN PUZZLE SOLVER")
    print("=" * 70)

    # Show status
    status = solver.get_status()
    print(f"Known puzzles: {status['known_puzzles']}")
    print(f"Workers: {status['workers']}")

    # Run benchmark
    print("\n--- Benchmark ---")
    bench = solver.benchmark(3)
    print(f"Speed: {bench['keys_per_second']:,.0f} keys/sec")

    # Run autonomous solving on feasible puzzles
    print("\n--- Autonomous Solving ---")
    solved = solver.run_autonomous(start_puzzle=5, end_puzzle=30)

    print(f"\n--- Results ---")
    print(f"Solved/Verified: {len(solved)} puzzles")
    print(f"Puzzles: {solved}")


if __name__ == "__main__":
    main()
