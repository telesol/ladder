#!/usr/bin/env python3
"""
Bitcoin Puzzle Search Engine - High-Performance Key Discovery
Uses coincurve for fast secp256k1 operations with multiprocessing
"""
import hashlib
import sqlite3
import json
import os
import time
import multiprocessing as mp
from multiprocessing import Process, Queue, Value, Manager
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from coincurve import PrivateKey

# Bitcoin address utilities
def private_key_to_public_key(private_key: int, compressed: bool = True) -> bytes:
    """Convert private key integer to public key bytes"""
    pk_bytes = private_key.to_bytes(32, 'big')
    return PrivateKey(pk_bytes).public_key.format(compressed=compressed)

def public_key_to_address(public_key: bytes) -> str:
    """Convert public key to Bitcoin address (P2PKH)"""
    sha256_hash = hashlib.sha256(public_key).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    hash160 = ripemd160.digest()

    # Add version byte (0x00 for mainnet)
    versioned = b'\x00' + hash160

    # Double SHA256 for checksum
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

    # Base58 encode
    return base58_encode(versioned + checksum)

def base58_encode(data: bytes) -> str:
    """Base58 encoding for Bitcoin addresses"""
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = int.from_bytes(data, 'big')
    result = ''
    while n > 0:
        n, remainder = divmod(n, 58)
        result = alphabet[remainder] + result

    # Add leading '1's for leading zero bytes
    for byte in data:
        if byte == 0:
            result = '1' + result
        else:
            break

    return result

def private_key_to_wif(private_key: int, compressed: bool = True) -> str:
    """Convert private key to WIF format"""
    pk_bytes = private_key.to_bytes(32, 'big')
    if compressed:
        extended = b'\x80' + pk_bytes + b'\x01'
    else:
        extended = b'\x80' + pk_bytes
    checksum = hashlib.sha256(hashlib.sha256(extended).digest()).digest()[:4]
    return base58_encode(extended + checksum)


class SearchStrategy(Enum):
    SEQUENTIAL = "sequential"
    RANDOM = "random"
    GUIDED = "guided"  # AI-guided priority regions
    PATTERN = "pattern"  # Based on pattern analysis


@dataclass
class SearchResult:
    """Result of a search operation"""
    found: bool
    private_key: Optional[int] = None
    public_key: Optional[str] = None
    address: Optional[str] = None
    wif: Optional[str] = None
    keys_checked: int = 0
    time_elapsed: float = 0.0
    keys_per_second: float = 0.0


@dataclass
class SearchTask:
    """A search task for workers"""
    start_key: int
    end_key: int
    target_address: str
    task_id: int


class SearchWorker:
    """Worker process for parallel key search"""

    def __init__(self, worker_id: int, result_queue: Queue, status_dict: dict):
        self.worker_id = worker_id
        self.result_queue = result_queue
        self.status_dict = status_dict
        self.running = True

    def search_range(self, task: SearchTask) -> SearchResult:
        """Search a range of keys for target address"""
        start_time = time.time()
        keys_checked = 0

        for key in range(task.start_key, task.end_key + 1):
            if not self.running:
                break

            try:
                # Generate address from private key
                pub_key = private_key_to_public_key(key, compressed=True)
                address = public_key_to_address(pub_key)
                keys_checked += 1

                # Update status every 10000 keys
                if keys_checked % 10000 == 0:
                    self.status_dict[self.worker_id] = {
                        'current_key': key,
                        'keys_checked': keys_checked,
                        'keys_per_sec': keys_checked / (time.time() - start_time + 0.001)
                    }

                # Check if we found it
                if address == task.target_address:
                    elapsed = time.time() - start_time
                    return SearchResult(
                        found=True,
                        private_key=key,
                        public_key=pub_key.hex(),
                        address=address,
                        wif=private_key_to_wif(key),
                        keys_checked=keys_checked,
                        time_elapsed=elapsed,
                        keys_per_second=keys_checked / elapsed if elapsed > 0 else 0
                    )

                # Also check uncompressed address
                pub_key_uncompressed = private_key_to_public_key(key, compressed=False)
                address_uncompressed = public_key_to_address(pub_key_uncompressed)

                if address_uncompressed == task.target_address:
                    elapsed = time.time() - start_time
                    return SearchResult(
                        found=True,
                        private_key=key,
                        public_key=pub_key_uncompressed.hex(),
                        address=address_uncompressed,
                        wif=private_key_to_wif(key, compressed=False),
                        keys_checked=keys_checked,
                        time_elapsed=elapsed,
                        keys_per_second=keys_checked / elapsed if elapsed > 0 else 0
                    )

            except Exception as e:
                continue

        elapsed = time.time() - start_time
        return SearchResult(
            found=False,
            keys_checked=keys_checked,
            time_elapsed=elapsed,
            keys_per_second=keys_checked / elapsed if elapsed > 0 else 0
        )


class BitcoinPuzzleSearchEngine:
    """
    High-performance Bitcoin puzzle search engine with multiprocessing
    and Claude orchestration integration
    """

    def __init__(self, db_path: str = "/home/solo/LA/db/search_engine.db", num_workers: int = None):
        self.db_path = db_path
        self.num_workers = num_workers or max(1, mp.cpu_count() - 1)
        self.manager = Manager()
        self.status_dict = self.manager.dict()
        self.result_queue = Queue()
        self.workers: List[Process] = []
        self.running = Value('b', False)

        # Known puzzle data
        self.known_puzzles = self._load_known_puzzles()

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize search progress database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS search_progress (
            puzzle_id INTEGER PRIMARY KEY,
            target_address TEXT,
            range_low TEXT,
            range_high TEXT,
            current_position TEXT,
            keys_searched INTEGER DEFAULT 0,
            strategy TEXT,
            status TEXT DEFAULT 'pending',
            started_at TEXT,
            updated_at TEXT,
            found_key TEXT,
            found_at TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS search_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            puzzle_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            keys_searched INTEGER,
            keys_per_second REAL,
            strategy TEXT,
            result TEXT
        )''')
        conn.commit()
        conn.close()

    def _load_known_puzzles(self) -> Dict:
        """Load known puzzle data from CSV and database"""
        puzzles = {}

        # Load from CSV file (primary source)
        csv_path = "/home/solo/LA/data/btc_puzzle_1_160_full.csv"
        try:
            import csv
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    puzzle_num = int(row['puzzle'])
                    key_hex = row.get('key_hex', '')
                    key_decimal = int(key_hex, 16) if key_hex and key_hex != '' else None
                    puzzles[puzzle_num] = {
                        'address': row['address'].split('#')[0].strip(),  # Remove comments
                        'known_key': key_decimal
                    }
        except Exception as e:
            print(f"Warning: Could not load CSV: {e}")

        # Fallback to database
        if not puzzles:
            try:
                conn = sqlite3.connect("/home/solo/LA/db/kh.db")
                c = conn.cursor()
                c.execute("SELECT id, address FROM puzzles WHERE address IS NOT NULL")
                for row in c.fetchall():
                    addr = row[1].split('#')[0].strip() if row[1] else None
                    if addr:
                        puzzles[row[0]] = {
                            'address': addr,
                            'known_key': None
                        }
                conn.close()
            except:
                pass

        # Ensure puzzle 71 is present (next unsolved)
        if 71 not in puzzles:
            puzzles[71] = {
                'address': '1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU',
                'known_key': None
            }

        return puzzles

    def get_puzzle_range(self, puzzle_num: int) -> Tuple[int, int]:
        """Get the valid key range for a puzzle"""
        low = 2 ** (puzzle_num - 1)
        high = 2 ** puzzle_num - 1
        return (low, high)

    def search_puzzle(self, puzzle_num: int, strategy: SearchStrategy = SearchStrategy.SEQUENTIAL,
                      max_keys: int = None, checkpoint_interval: int = 1000000) -> SearchResult:
        """
        Search for a puzzle solution

        Args:
            puzzle_num: The puzzle number to search
            strategy: Search strategy to use
            max_keys: Maximum number of keys to check (None = unlimited)
            checkpoint_interval: How often to save progress
        """
        if puzzle_num not in self.known_puzzles:
            return SearchResult(found=False, keys_checked=0)

        target_address = self.known_puzzles[puzzle_num]['address']
        range_low, range_high = self.get_puzzle_range(puzzle_num)

        # Get starting position from database or start fresh
        start_pos = self._get_search_position(puzzle_num) or range_low

        print(f"\n{'='*60}")
        print(f"SEARCH ENGINE: Puzzle {puzzle_num}")
        print(f"{'='*60}")
        print(f"Target: {target_address}")
        print(f"Range: [{range_low:,}, {range_high:,}]")
        print(f"Search space: {range_high - range_low + 1:,} keys")
        print(f"Starting at: {start_pos:,}")
        print(f"Workers: {self.num_workers}")
        print(f"Strategy: {strategy.value}")
        print(f"{'='*60}\n")

        # Record session start
        session_start = datetime.now()
        self._record_session_start(puzzle_num, strategy)

        # Divide work among workers
        total_keys = min(max_keys, range_high - start_pos + 1) if max_keys else (range_high - start_pos + 1)
        chunk_size = total_keys // self.num_workers

        tasks = []
        for i in range(self.num_workers):
            chunk_start = start_pos + (i * chunk_size)
            chunk_end = chunk_start + chunk_size - 1 if i < self.num_workers - 1 else min(start_pos + total_keys - 1, range_high)
            tasks.append(SearchTask(
                start_key=chunk_start,
                end_key=chunk_end,
                target_address=target_address,
                task_id=i
            ))

        # Run search with workers
        self.running.value = True
        total_result = SearchResult(found=False, keys_checked=0, time_elapsed=0)

        try:
            # For now, run sequentially (can add multiprocessing later)
            for task in tasks:
                if not self.running.value:
                    break

                worker = SearchWorker(task.task_id, self.result_queue, self.status_dict)
                result = worker.search_range(task)

                total_result.keys_checked += result.keys_checked
                total_result.time_elapsed += result.time_elapsed

                if result.found:
                    total_result = result
                    self._record_solution(puzzle_num, result)
                    break

                # Checkpoint
                self._save_progress(puzzle_num, task.end_key, total_result.keys_checked)

        except KeyboardInterrupt:
            print("\nSearch interrupted by user")
            self.running.value = False

        # Calculate final stats
        if total_result.time_elapsed > 0:
            total_result.keys_per_second = total_result.keys_checked / total_result.time_elapsed

        # Record session end
        self._record_session_end(puzzle_num, total_result)

        return total_result

    def _get_search_position(self, puzzle_num: int) -> Optional[int]:
        """Get last search position from database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT current_position FROM search_progress WHERE puzzle_id = ?", (puzzle_num,))
        row = c.fetchone()
        conn.close()
        return int(row[0]) if row and row[0] else None

    def _save_progress(self, puzzle_num: int, position: int, keys_searched: int):
        """Save search progress to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO search_progress
                     (puzzle_id, current_position, keys_searched, updated_at, status)
                     VALUES (?, ?, ?, ?, ?)''',
                  (puzzle_num, str(position), keys_searched, datetime.now().isoformat(), 'in_progress'))
        conn.commit()
        conn.close()

    def _record_session_start(self, puzzle_num: int, strategy: SearchStrategy):
        """Record search session start"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO search_sessions (puzzle_id, start_time, strategy)
                     VALUES (?, ?, ?)''',
                  (puzzle_num, datetime.now().isoformat(), strategy.value))
        conn.commit()
        conn.close()

    def _record_session_end(self, puzzle_num: int, result: SearchResult):
        """Record search session end"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''UPDATE search_sessions SET end_time = ?, keys_searched = ?,
                     keys_per_second = ?, result = ?
                     WHERE puzzle_id = ? AND end_time IS NULL''',
                  (datetime.now().isoformat(), result.keys_checked,
                   result.keys_per_second, 'found' if result.found else 'not_found', puzzle_num))
        conn.commit()
        conn.close()

    def _record_solution(self, puzzle_num: int, result: SearchResult):
        """Record found solution"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''UPDATE search_progress SET found_key = ?, found_at = ?, status = ?
                     WHERE puzzle_id = ?''',
                  (str(result.private_key), datetime.now().isoformat(), 'solved', puzzle_num))
        conn.commit()
        conn.close()

        print(f"\n{'='*60}")
        print(f"!!! SOLUTION FOUND !!!")
        print(f"{'='*60}")
        print(f"Puzzle: {puzzle_num}")
        print(f"Private Key: {result.private_key}")
        print(f"WIF: {result.wif}")
        print(f"Address: {result.address}")
        print(f"Keys checked: {result.keys_checked:,}")
        print(f"Time: {result.time_elapsed:.2f}s")
        print(f"{'='*60}\n")

    def get_status(self) -> Dict:
        """Get current search status"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM search_progress ORDER BY updated_at DESC LIMIT 5")
        rows = c.fetchall()
        conn.close()

        return {
            'active_searches': len([r for r in rows if r[7] == 'in_progress']),
            'total_workers': self.num_workers,
            'worker_status': dict(self.status_dict),
            'recent_progress': rows
        }

    def verify_key(self, private_key: int, expected_address: str) -> bool:
        """Verify a private key produces the expected address"""
        try:
            pub_key = private_key_to_public_key(private_key, compressed=True)
            address = public_key_to_address(pub_key)
            if address == expected_address:
                return True

            # Try uncompressed
            pub_key = private_key_to_public_key(private_key, compressed=False)
            address = public_key_to_address(pub_key)
            return address == expected_address
        except:
            return False

    def benchmark(self, duration_seconds: int = 10) -> Dict:
        """Benchmark search speed"""
        print(f"Benchmarking for {duration_seconds} seconds...")

        # Use puzzle 20 range for benchmarking (small enough to be fast)
        range_low, range_high = self.get_puzzle_range(20)

        start_time = time.time()
        keys_checked = 0

        while time.time() - start_time < duration_seconds:
            for key in range(range_low, min(range_low + 10000, range_high)):
                pub_key = private_key_to_public_key(key, compressed=True)
                address = public_key_to_address(pub_key)
                keys_checked += 1

        elapsed = time.time() - start_time
        keys_per_second = keys_checked / elapsed

        result = {
            'duration_seconds': elapsed,
            'keys_checked': keys_checked,
            'keys_per_second': keys_per_second,
            'estimated_puzzle_71_time_years': (2**70) / keys_per_second / 86400 / 365
        }

        print(f"Benchmark complete: {keys_per_second:,.0f} keys/second")
        print(f"Estimated puzzle 71 time: {result['estimated_puzzle_71_time_years']:,.0f} years (brute force)")

        return result


# Test
if __name__ == "__main__":
    engine = BitcoinPuzzleSearchEngine()

    print("=== Bitcoin Puzzle Search Engine ===\n")

    # Benchmark
    print("--- Benchmark ---")
    bench = engine.benchmark(5)
    print(f"Speed: {bench['keys_per_second']:,.0f} keys/sec\n")

    # Verify a known puzzle (puzzle 20)
    print("--- Verification Test ---")
    known_key_20 = 863317
    known_addr_20 = "1HBtApAFA9B2YZw3G2YKSMCtb3dVnjuNe2"
    verified = engine.verify_key(known_key_20, known_addr_20)
    print(f"Puzzle 20 key verification: {'PASS' if verified else 'FAIL'}")

    # Small search test (puzzle 5, already solved)
    print("\n--- Small Search Test (Puzzle 5) ---")
    result = engine.search_puzzle(5, max_keys=50)
    print(f"Found: {result.found}")
    if result.found:
        print(f"Key: {result.private_key}")
        print(f"Address: {result.address}")
