#!/usr/bin/env python3
"""
Agent V3 - Tool-Based Architecture

The AI model understands user intent and explains results.
Python scripts do the REAL math. No hallucinated arithmetic.

Tools available:
- verify_ladder: Run verify_affine.py
- predict_next: Run predict_next_halfblock.py
- compute_drift: Run compute_missing_drift.py
- validate_address: Run validate_address.py
- get_puzzle: Query database for puzzle data
- get_calibration: Read calibration file
"""
import json
import os
import subprocess
import sqlite3
from typing import Dict, Optional, List
from datetime import datetime

from ollama_integration import generate_with_ollama_sync
from memory_system import get_memory_system

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KH_ASSIST = os.path.join(BASE_DIR, 'kh-assist')
DB_PATH = os.path.join(KH_ASSIST, 'db', 'kh.db')
CALIB_PATH = os.path.join(KH_ASSIST, 'out', 'ladder_calib_29_70_full.json')


def get_db_range() -> tuple:
    """Get the actual range of consecutive puzzles in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT MIN(bits), MAX(bits) FROM lcg_residuals")
        min_bits, max_bits = cur.fetchone()

        # Find the consecutive range (puzzles that are sequential)
        cur.execute("SELECT bits FROM lcg_residuals ORDER BY bits")
        all_bits = [row[0] for row in cur.fetchall()]
        conn.close()

        # Find longest consecutive sequence
        consecutive_end = 1
        for i, b in enumerate(all_bits):
            if i > 0 and b != all_bits[i-1] + 1:
                consecutive_end = all_bits[i-1]
                break
            consecutive_end = b

        return (1, consecutive_end, max_bits)  # (min, consecutive_end, max)
    except:
        return (1, 70, 130)  # Fallback


class LadderTools:
    """Real computation tools - provide DATA for reasoning, not just script outputs"""

    @staticmethod
    def verify_ladder(start: int = None, end: int = None) -> Dict:
        """
        Verify the affine recurrence by computing predictions and comparing to actual data.
        Returns RAW DATA for the model to analyze and reason about.

        If start/end not provided, uses the full consecutive range from database.
        """
        try:
            # Get dynamic range if not specified
            db_min, db_consecutive_end, db_max = get_db_range()
            if start is None:
                start = 1
            if end is None:
                end = db_consecutive_end  # Use consecutive end (e.g., 70)

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # Load calibration
            with open(CALIB_PATH) as f:
                calib = json.load(f)

            A = {int(k): int(v) for k, v in calib['A'].items()}
            Cstar = {int(b): {int(l): v for l, v in lanes.items()}
                     for b, lanes in calib['Cstar'].items()}

            # Get puzzle data
            cur.execute("""
                SELECT bits, lower(substr(actual_hex,3)) AS hex
                FROM lcg_residuals
                WHERE bits BETWEEN ? AND ?
                ORDER BY bits
            """, (start, end + 1))
            rows = cur.fetchall()
            conn.close()

            if not rows:
                return {'success': False, 'error': f'No puzzles in range {start}-{end}'}

            # Parse hex to bytes
            def hex_to_bytes(h):
                h = h.rjust(64, '0')
                return [int(h[i:i+2], 16) for i in range(0, 64, 2)]

            data = {bits: hex_to_bytes(hex_str) for bits, hex_str in rows}

            # Block function - use start as base
            def blk(i):
                return (i - start) // 32

            # Verify each transition
            results = []
            total_matches = 0
            total_checks = 0

            for i in range(start, min(end, max(data.keys()))):
                if i not in data or (i+1) not in data:
                    continue

                x = data[i]  # Current puzzle
                y = data[i+1]  # Next puzzle (actual)
                b = blk(i)
                occ = 0 if ((i - start) % 32) < 16 else 1

                lane_results = []
                for lane in range(16):
                    if b not in Cstar or lane not in Cstar[b]:
                        continue
                    if occ >= len(Cstar[b][lane]):
                        continue

                    a = A[lane]
                    c = Cstar[b][lane][occ]
                    x_val = x[lane]
                    y_actual = y[lane]
                    y_predicted = (a * x_val + c) & 0xFF

                    match = y_predicted == y_actual
                    if match:
                        total_matches += 1
                    total_checks += 1

                    lane_results.append({
                        'lane': lane,
                        'A': a,
                        'C': c,
                        'x': x_val,
                        'y_predicted': y_predicted,
                        'y_actual': y_actual,
                        'match': match
                    })

                results.append({
                    'from_puzzle': i,
                    'to_puzzle': i + 1,
                    'block': b,
                    'occurrence': occ,
                    'lanes': lane_results,
                    'all_match': all(lr['match'] for lr in lane_results)
                })

            # Summarize mismatches for analysis
            mismatches = []
            for r in results:
                for lr in r['lanes']:
                    if not lr['match']:
                        mismatches.append({
                            'puzzle': r['from_puzzle'],
                            'lane': lr['lane'],
                            'A': lr['A'],
                            'C': lr['C'],
                            'x': lr['x'],
                            'predicted': lr['y_predicted'],
                            'actual': lr['y_actual'],
                            'diff': (lr['y_actual'] - lr['y_predicted']) & 0xFF
                        })

            return {
                'success': True,
                'range': f'{start}-{end}',
                'total_transitions': len(results),
                'total_checks': total_checks,
                'total_matches': total_matches,
                'accuracy': f'{total_matches}/{total_checks} = {100*total_matches/total_checks:.2f}%' if total_checks > 0 else 'N/A',
                'perfect': total_matches == total_checks,
                'A_matrix': A,
                'mismatches_sample': mismatches[:20],  # First 20 for analysis
                'mismatch_count': len(mismatches),
                'analysis_hint': 'Look at the diff values - they may reveal a pattern in the drift constants'
            }
        except Exception as e:
            import traceback
            return {'success': False, 'error': str(e), 'traceback': traceback.format_exc()}

    @staticmethod
    def calculate_puzzle(target_bits: int = None) -> Dict:
        """
        CALCULATE (not predict) the private key for a puzzle using affine math.
        This is deterministic mathematics: y = A[lane] * x + C[lane] mod 256

        Then VERIFY by converting to Bitcoin address and matching against known address.
        """
        try:
            import hashlib

            # Load calibration
            with open(CALIB_PATH) as f:
                calib = json.load(f)

            A = {int(k): int(v) for k, v in calib['A'].items()}
            Cstar = {int(b): {int(l): v for l, v in lanes.items()}
                     for b, lanes in calib['Cstar'].items()}

            # Get the previous puzzle (source for calculation)
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # Find the nearest lower SOLVED puzzle (exclude '0x?' unsolved entries)
            cur.execute("""
                SELECT bits, lower(substr(actual_hex,3)) AS hex
                FROM lcg_residuals
                WHERE bits < ? AND actual_hex NOT LIKE '%?%'
                ORDER BY bits DESC LIMIT 1
            """, (target_bits,))
            source_row = cur.fetchone()

            if not source_row:
                return {'success': False, 'error': f'No source puzzle found below {target_bits}'}

            source_bits = source_row[0]
            source_hex = source_row[1].rjust(64, '0')
            source_bytes = [int(source_hex[i:i+2], 16) for i in range(0, 64, 2)]

            # Calculate step by step from source to target
            current_bytes = source_bytes[:16]  # First 16 bytes = 16 lanes
            steps_needed = target_bits - source_bits

            calculation_log = []
            calculation_log.append(f"Source puzzle: {source_bits}")
            calculation_log.append(f"Target puzzle: {target_bits}")
            calculation_log.append(f"Steps to calculate: {steps_needed}")
            calculation_log.append("")

            for step in range(steps_needed):
                current_puzzle = source_bits + step
                next_puzzle = current_puzzle + 1
                block = (current_puzzle - 1) // 32
                occ = 0 if ((current_puzzle - 1) % 32) < 16 else 1

                new_bytes = []
                for lane in range(16):
                    a = A.get(lane, 1)
                    c = 0
                    if block in Cstar and lane in Cstar[block]:
                        c_list = Cstar[block][lane]
                        if occ < len(c_list):
                            c = c_list[occ]

                    x = current_bytes[lane]
                    y = (a * x + c) & 0xFF  # Affine recurrence: y = A*x + C mod 256
                    new_bytes.append(y)

                current_bytes = new_bytes

            # Assemble the calculated private key
            calculated_hex = ''.join(f'{b:02x}' for b in current_bytes)
            # Pad to 64 hex chars (256 bits) - the key is in the first N bits
            full_key_hex = calculated_hex.ljust(64, '0')

            calculation_log.append(f"Calculated lanes: {current_bytes}")
            calculation_log.append(f"Calculated key: 0x{full_key_hex}")

            # VERIFICATION: Convert to Bitcoin address and check
            verification_result = LadderTools._verify_key_against_address(
                full_key_hex, target_bits
            )

            conn.close()

            return {
                'success': True,
                'method': 'MATHEMATICAL CALCULATION (not prediction)',
                'formula': 'y = A[lane] * x + C[lane] mod 256',
                'source_puzzle': source_bits,
                'target_puzzle': target_bits,
                'steps_calculated': steps_needed,
                'calculated_key': f'0x{full_key_hex}',
                'lane_values': current_bytes,
                'verification': verification_result,
                'calculation_log': calculation_log
            }
        except Exception as e:
            import traceback
            return {'success': False, 'error': str(e), 'traceback': traceback.format_exc()}

    @staticmethod
    def _verify_key_against_address(privkey_hex: str, puzzle_num: int) -> Dict:
        """
        VERIFY a calculated key by:
        1. Converting private key to public key (secp256k1)
        2. Hashing: SHA256 -> RIPEMD160
        3. Base58Check encoding to get Bitcoin address
        4. Comparing against known address from CSV

        NOTE: The database stores keys in lane-format (big-endian, left-aligned)
        but Bitcoin expects standard format (big-endian, right-aligned).
        We need to convert: 0x0202000... -> 0x0000...0202
        """
        try:
            from ecdsa import SigningKey, SECP256k1
            import base58
            import hashlib

            # Remove 0x prefix
            if privkey_hex.startswith('0x'):
                privkey_hex = privkey_hex[2:]

            # Convert from lane-format (little-endian) to Bitcoin format (big-endian)
            # Lane format: bytes stored as [b0, b1, b2, ...] where b0 is LSB
            # Bitcoin format: standard big-endian 256-bit integer
            # Example: lanes [85, 44, 13, 0, ...] = 85 + 44*256 + 13*65536 = 0xd2c55
            lane_bytes = bytes.fromhex(privkey_hex.zfill(64))
            # Interpret as little-endian: sum of byte[i] * 256^i
            privkey_int = sum(b << (8*i) for i, b in enumerate(lane_bytes[:16]))
            privkey_hex_bitcoin = format(privkey_int, '064x')  # 32 bytes, big-endian

            privkey_bytes = bytes.fromhex(privkey_hex_bitcoin)

            # Derive public key
            try:
                sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
                vk = sk.get_verifying_key()

                # Compressed public key
                try:
                    pubkey_compressed = vk.to_string("compressed")
                except:
                    pubkey_uncompressed = vk.to_string()
                    x = pubkey_uncompressed[:32]
                    y_byte = pubkey_uncompressed[32]
                    prefix = b'\x02' if y_byte % 2 == 0 else b'\x03'
                    pubkey_compressed = prefix + x

                # Hash: SHA256 -> RIPEMD160
                sha256_hash = hashlib.sha256(pubkey_compressed).digest()
                ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

                # Add version byte and encode
                versioned = b'\x00' + ripemd160_hash
                derived_address = base58.b58encode_check(versioned).decode()

            except Exception as e:
                return {
                    'verified': False,
                    'error': f'Key derivation failed: {str(e)}',
                    'reason': 'Private key may be invalid or out of range'
                }

            # Get expected address from CSV
            csv_path = os.path.join(KH_ASSIST, 'data', 'btc_puzzle_1_160_full.csv')
            expected_address = None
            try:
                import csv
                with open(csv_path, 'r') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header
                    for row in reader:
                        if row and int(row[0]) == puzzle_num:
                            expected_address = row[1]
                            break
            except:
                pass

            if expected_address:
                match = derived_address == expected_address
                return {
                    'verified': True,
                    'lane_format_key': privkey_hex,
                    'bitcoin_format_key': f'0x{privkey_hex_bitcoin}',
                    'key_decimal': privkey_int,
                    'derived_address': derived_address,
                    'expected_address': expected_address,
                    'MATCH': match,
                    'conclusion': 'MATH PROVEN CORRECT!' if match else 'Calibration needs adjustment'
                }
            else:
                return {
                    'verified': True,
                    'lane_format_key': privkey_hex,
                    'bitcoin_format_key': f'0x{privkey_hex_bitcoin}',
                    'key_decimal': privkey_int,
                    'derived_address': derived_address,
                    'expected_address': 'NOT IN CSV (unsolved puzzle)',
                    'MATCH': 'UNKNOWN',
                    'conclusion': 'Address derived - compare manually or wait for solution'
                }

        except ImportError:
            return {
                'verified': False,
                'error': 'Missing dependencies: pip install ecdsa base58',
                'derived_address': None
            }
        except Exception as e:
            return {
                'verified': False,
                'error': str(e),
                'derived_address': None
            }

    @staticmethod
    def discover_lanes() -> Dict:
        """
        DISCOVER the mathematical structure of all 16 lanes.
        Shows A (multiplier) and C (drift) values for each lane.
        This is pure mathematics - understanding the affine recurrence.
        """
        try:
            # Load calibration
            with open(CALIB_PATH) as f:
                calib = json.load(f)

            A = {int(k): int(v) for k, v in calib['A'].items()}
            Cstar = calib.get('Cstar', {})

            lane_analysis = {}
            for lane in range(16):
                a = A.get(lane, 'UNKNOWN')

                # Analyze C values across blocks
                c_values = []
                for block, lanes in Cstar.items():
                    if str(lane) in lanes:
                        c_values.extend(lanes[str(lane)])

                # Determine if lane is "weak" (exploitable) or "strong"
                weakness = 'UNKNOWN'
                if isinstance(a, int):
                    if a == 1:
                        weakness = 'TRIVIAL (A=1, pure addition)'
                    elif a % 2 == 0:
                        weakness = 'WEAK (A is even, non-invertible mod 256)'
                    elif a in [3, 5, 7, 11, 13]:
                        weakness = 'MODERATE (small odd multiplier)'
                    else:
                        weakness = 'STRONG (large odd multiplier)'

                lane_analysis[lane] = {
                    'A_multiplier': a,
                    'A_hex': f'0x{a:02x}' if isinstance(a, int) else 'N/A',
                    'weakness': weakness,
                    'C_drift_values': list(set(c_values)) if c_values else [],
                    'formula': f'y = {a} * x + C mod 256'
                }

            return {
                'success': True,
                'total_lanes': 16,
                'lanes': lane_analysis,
                'explanation': 'Each lane follows: y = A[lane] * x + C[block][lane][occ] mod 256',
                'next_step': 'Use "analyze lane N" for detailed transitions of a specific lane'
            }
        except Exception as e:
            import traceback
            return {'success': False, 'error': str(e), 'traceback': traceback.format_exc()}

    @staticmethod
    def generate_calibration(start: int = 1, end: int = 70) -> Dict:
        """
        GENERATE a new calibration file from database puzzles.
        Computes A matrix and C drift constants from known solutions.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # Get all puzzles in range
            cur.execute("""
                SELECT bits, lower(substr(actual_hex,3)) AS hex
                FROM lcg_residuals
                WHERE bits BETWEEN ? AND ?
                ORDER BY bits
            """, (start, end + 1))
            rows = cur.fetchall()
            conn.close()

            if len(rows) < 2:
                return {'success': False, 'error': f'Need at least 2 puzzles, found {len(rows)}'}

            def hex_to_bytes(h):
                h = h.rjust(64, '0')
                return [int(h[i:i+2], 16) for i in range(0, 64, 2)]

            # Filter out unsolved puzzles (those with '?' in hex)
            data = {}
            for bits, hex_str in rows:
                if '?' in hex_str:
                    continue  # Skip unsolved puzzles
                data[bits] = hex_to_bytes(hex_str)

            # Use known A multipliers from established calibration
            # These are the proven values from the ladder model
            # Lane 1, 5, 9, 13 have non-trivial multipliers
            A = {
                0: 1, 1: 91, 2: 1, 3: 1,
                4: 1, 5: 169, 6: 1, 7: 1,
                8: 1, 9: 32, 10: 1, 11: 1,
                12: 1, 13: 182, 14: 1, 15: 1
            }

            # Compute C (drift) for each block/lane/occurrence
            Cstar = {}
            for i in range(start, end):
                if i not in data or (i+1) not in data:
                    continue

                block = (i - start) // 32
                occ = 0 if ((i - start) % 32) < 16 else 1

                if block not in Cstar:
                    Cstar[block] = {lane: [0, 0] for lane in range(16)}

                x = data[i][:16]
                y = data[i+1][:16]

                for lane in range(16):
                    a = A[lane]
                    c = (y[lane] - a * x[lane]) & 0xFF
                    Cstar[block][lane][occ] = c

            # Save calibration file
            calib_data = {
                'range': [start, end],
                'A': {str(k): v for k, v in A.items()},
                'Cstar': {str(b): {str(l): v for l, v in lanes.items()}
                          for b, lanes in Cstar.items()},
                'generated': True
            }

            output_file = os.path.join(KH_ASSIST, 'out', f'ladder_calib_{start}_{end}_full.json')
            with open(output_file, 'w') as f:
                json.dump(calib_data, f, indent=2)

            return {
                'success': True,
                'file_created': output_file,
                'range': f'{start}-{end}',
                'puzzles_used': len(rows),
                'A_matrix': A,
                'blocks_calibrated': len(Cstar),
                'message': f'Calibration file generated: {output_file}'
            }
        except Exception as e:
            import traceback
            return {'success': False, 'error': str(e), 'traceback': traceback.format_exc()}

    @staticmethod
    def get_puzzle(bits: int) -> Dict:
        """Get puzzle data from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "SELECT bits, actual_hex FROM lcg_residuals WHERE bits = ?",
                (bits,)
            )
            row = cur.fetchone()
            conn.close()

            if row:
                hex_val = row[1]
                # Parse into lane bytes
                hex_clean = hex_val.lower().replace('0x', '').zfill(64)
                lanes = [int(hex_clean[i:i+2], 16) for i in range(0, 32, 2)]

                # Automatically verify the puzzle against its known Bitcoin address
                verification = LadderTools._verify_key_against_address(hex_val, bits)

                return {
                    'success': True,
                    'bits': bits,
                    'hex': hex_val,
                    'lanes': lanes,
                    'verification': verification
                }
            else:
                return {'success': False, 'error': f'Puzzle {bits} not in database'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_calibration() -> Dict:
        """Load the calibration data"""
        try:
            with open(CALIB_PATH) as f:
                calib = json.load(f)
            return {
                'success': True,
                'A': calib.get('A', {}),
                'Cstar': calib.get('Cstar', {}),
                'range': calib.get('range', []),
                'lanes': calib.get('lanes', [])
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def list_puzzles() -> Dict:
        """List ALL available puzzles in the database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT bits FROM lcg_residuals ORDER BY bits")
            puzzles = [row[0] for row in cur.fetchall()]
            conn.close()

            # Identify consecutive ranges and gaps
            # Find consecutive range dynamically
            consecutive = []
            bridges = []
            prev = 0
            consecutive_end = 0
            for p in puzzles:
                if prev == 0 or p == prev + 1:
                    consecutive.append(p)
                    consecutive_end = p
                else:
                    bridges.append(p)
                prev = p

            return {
                'success': True,
                'total': len(puzzles),
                'all_puzzles': puzzles,
                'consecutive_range': f"1-{max(consecutive)}" if consecutive else "none",
                'bridge_puzzles': bridges,
                'gaps': [i for i in range(1, max(puzzles)+1) if i not in puzzles]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def analyze_lane(lane: int, start: int = None, end: int = None) -> Dict:
        """
        Get detailed data for a specific lane across puzzles.
        Returns RAW VALUES for the model to analyze patterns.

        If start/end not provided, uses the full consecutive range from database.
        """
        try:
            # Get dynamic range if not specified
            db_min, db_consecutive_end, db_max = get_db_range()
            if start is None:
                start = 1
            if end is None:
                end = db_consecutive_end

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # Load calibration
            with open(CALIB_PATH) as f:
                calib = json.load(f)

            A = int(calib['A'].get(str(lane), 1))
            Cstar = {int(b): {int(l): v for l, v in lanes.items()}
                     for b, lanes in calib['Cstar'].items()}

            # Get puzzle data
            cur.execute("""
                SELECT bits, lower(substr(actual_hex,3)) AS hex
                FROM lcg_residuals
                WHERE bits BETWEEN ? AND ?
                ORDER BY bits
            """, (start, end))
            rows = cur.fetchall()
            conn.close()

            def hex_to_bytes(h):
                h = h.rjust(64, '0')
                return [int(h[i:i+2], 16) for i in range(0, 64, 2)]

            # Extract lane values
            lane_data = []
            for bits, hex_str in rows:
                bytes_arr = hex_to_bytes(hex_str)
                lane_data.append({
                    'puzzle': bits,
                    'value': bytes_arr[lane],
                    'hex': f'0x{bytes_arr[lane]:02x}'
                })

            # Compute differences between consecutive puzzles
            diffs = []
            for i in range(len(lane_data) - 1):
                curr = lane_data[i]
                next_p = lane_data[i + 1]
                if next_p['puzzle'] == curr['puzzle'] + 1:
                    # Compute what C would need to be: y = A*x + C mod 256
                    # C = (y - A*x) mod 256
                    implied_C = (next_p['value'] - A * curr['value']) & 0xFF
                    diffs.append({
                        'from': curr['puzzle'],
                        'to': next_p['puzzle'],
                        'x': curr['value'],
                        'y': next_p['value'],
                        'A': A,
                        'implied_C': implied_C
                    })

            return {
                'success': True,
                'lane': lane,
                'A_value': A,
                'calibrated_C': {b: Cstar.get(b, {}).get(lane, []) for b in Cstar},
                'puzzle_values': lane_data,
                'consecutive_transitions': diffs,
                'analysis_hint': f'Lane {lane} has A={A}. Compare implied_C values with calibrated_C to find patterns.'
            }
        except Exception as e:
            import traceback
            return {'success': False, 'error': str(e), 'traceback': traceback.format_exc()}

    @staticmethod
    def compare_puzzles(puzzle1: int, puzzle2: int) -> Dict:
        """
        Compare two puzzles byte-by-byte with full affine analysis.
        Returns detailed data for the model to reason about.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # Load calibration
            with open(CALIB_PATH) as f:
                calib = json.load(f)

            A = {int(k): int(v) for k, v in calib['A'].items()}

            # Get both puzzles
            cur.execute("""
                SELECT bits, lower(substr(actual_hex,3)) AS hex
                FROM lcg_residuals
                WHERE bits IN (?, ?)
                ORDER BY bits
            """, (puzzle1, puzzle2))
            rows = cur.fetchall()
            conn.close()

            if len(rows) != 2:
                return {'success': False, 'error': f'Need both puzzles {puzzle1} and {puzzle2} in database'}

            def hex_to_bytes(h):
                h = h.rjust(64, '0')
                return [int(h[i:i+2], 16) for i in range(0, 64, 2)]

            p1_data = hex_to_bytes(rows[0][1])
            p2_data = hex_to_bytes(rows[1][1])

            comparison = []
            for lane in range(16):
                x = p1_data[lane]
                y = p2_data[lane]
                a = A[lane]
                # For single step: y = A*x + C mod 256, so C = (y - A*x) mod 256
                implied_C = (y - a * x) & 0xFF

                comparison.append({
                    'lane': lane,
                    'A': a,
                    f'puzzle_{puzzle1}': x,
                    f'puzzle_{puzzle2}': y,
                    'implied_C': implied_C,
                    'formula': f'y = {a}*{x} + C mod 256 → C = {implied_C}'
                })

            return {
                'success': True,
                'puzzle1': puzzle1,
                'puzzle2': puzzle2,
                'step_gap': puzzle2 - puzzle1,
                'comparison': comparison,
                'analysis_hint': 'For multi-step gaps, C accumulates with geometric series. Single step: y = A*x + C'
            }
        except Exception as e:
            import traceback
            return {'success': False, 'error': str(e), 'traceback': traceback.format_exc()}

    @staticmethod
    def compute_drift_stats(start: int = None, end: int = None) -> Dict:
        """
        Compute frequency of implied_C values for ALL lanes.
        This helps the model discover the correct drift constants.

        If start/end not provided, uses the full consecutive range from database.
        """
        try:
            # Get dynamic range if not specified
            db_min, db_consecutive_end, db_max = get_db_range()
            if start is None:
                start = 1
            if end is None:
                end = db_consecutive_end

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # Load calibration for A values
            with open(CALIB_PATH) as f:
                calib = json.load(f)
            A = {int(k): int(v) for k, v in calib['A'].items()}

            # Get puzzle data
            cur.execute("""
                SELECT bits, lower(substr(actual_hex,3)) AS hex
                FROM lcg_residuals
                WHERE bits BETWEEN ? AND ?
                ORDER BY bits
            """, (start, end + 1))
            rows = cur.fetchall()
            conn.close()

            def hex_to_bytes(h):
                h = h.rjust(64, '0')
                return [int(h[i:i+2], 16) for i in range(0, 64, 2)]

            data = [(bits, hex_to_bytes(hex_str)) for bits, hex_str in rows]

            # Compute implied_C for each lane across all consecutive transitions
            lane_stats = {}
            for lane in range(16):
                a = A.get(lane, 1)
                c_counts = {}
                transitions = []

                for i in range(len(data) - 1):
                    p1_bits, p1_bytes = data[i]
                    p2_bits, p2_bytes = data[i + 1]

                    # Only consecutive puzzles
                    if p2_bits == p1_bits + 1:
                        x = p1_bytes[lane]
                        y = p2_bytes[lane]
                        implied_c = (y - a * x) & 0xFF

                        c_counts[implied_c] = c_counts.get(implied_c, 0) + 1
                        transitions.append({
                            'from': p1_bits,
                            'to': p2_bits,
                            'x': x,
                            'y': y,
                            'implied_C': implied_c
                        })

                # Sort by frequency
                sorted_counts = sorted(c_counts.items(), key=lambda x: -x[1])

                lane_stats[lane] = {
                    'A': a,
                    'total_transitions': len(transitions),
                    'unique_C_values': len(c_counts),
                    'frequency': {str(c): count for c, count in sorted_counts},
                    'most_common_C': sorted_counts[0] if sorted_counts else None,
                    'sample_transitions': transitions[:5]  # First 5 for inspection
                }

            # Summary: suggested C values based on frequency
            suggested_C = {}
            for lane, stats in lane_stats.items():
                if stats['most_common_C']:
                    c_val, count = stats['most_common_C']
                    total = stats['total_transitions']
                    suggested_C[lane] = {
                        'value': c_val,
                        'frequency': count,
                        'percentage': f'{100*count/total:.1f}%' if total > 0 else 'N/A'
                    }

            return {
                'success': True,
                'range': f'{start}-{end}',
                'lane_stats': lane_stats,
                'suggested_drift': suggested_C,
                'analysis_hint': 'The most frequent implied_C value for each lane is likely the true drift constant. Compare with current calibration.'
            }
        except Exception as e:
            import traceback
            return {'success': False, 'error': str(e), 'traceback': traceback.format_exc()}

    @staticmethod
    def update_calibration(new_cstar: Dict[int, int]) -> Dict:
        """
        Update the calibration file with new Cstar values.
        new_cstar: dict mapping lane -> C value (single value, will be used for both occurrences)
        """
        try:
            # Load current calibration
            with open(CALIB_PATH) as f:
                calib = json.load(f)

            # Update Cstar for all blocks
            for block in calib['Cstar']:
                for lane_str in calib['Cstar'][block]:
                    lane = int(lane_str)
                    if lane in new_cstar:
                        new_c = new_cstar[lane]
                        calib['Cstar'][block][lane_str] = [new_c, new_c]

            # Save updated calibration
            with open(CALIB_PATH, 'w') as f:
                json.dump(calib, f, indent=2)

            return {
                'success': True,
                'updated_cstar': {str(k): v for k, v in new_cstar.items()},
                'message': f'Updated Cstar for {len(new_cstar)} lanes'
            }
        except Exception as e:
            import traceback
            return {'success': False, 'error': str(e), 'traceback': traceback.format_exc()}

    @staticmethod
    def validate_address(privkey_hex: str, puzzle_num: int = None) -> Dict:
        """Validate a private key against puzzle address"""
        try:
            result = subprocess.run(
                ['python3', 'validate_address.py', privkey_hex, str(puzzle_num)],
                cwd=KH_ASSIST,
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout + result.stderr
            match = 'MATCH' in output.upper()

            return {
                'success': True,
                'match': match,
                'output': output
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class ChattieV3:
    """
    Chattie V3 - Hybrid Agent

    The AI understands intent and explains.
    Python tools do the real math.
    """

    def __init__(self):
        self.memory = get_memory_system()
        self.model_name = "mistral-large-3:675b-cloud"
        self.tools = LadderTools()
        self.conversation_history = []
        self._load_history()

    def _load_history(self):
        """Load recent conversation history"""
        self.conversation_history = self.memory.get_recent_conversations(limit=10)

    def process_message(self, user_message: str, use_rag: bool = True) -> Dict:
        """Process a user message"""

        # Save user message
        self.memory.save_message('user', user_message)

        # 1. Determine what tool(s) to run based on user intent
        intent = self._classify_intent(user_message)

        # 2. Execute the appropriate tool
        tool_result = self._execute_tool(intent, user_message)

        # 3. Ask the model to explain the results to the user
        response = self._generate_explanation(user_message, intent, tool_result, use_rag)

        # Save response
        self.memory.save_message('assistant', response, action=intent)

        return {
            'message': response,
            'action_taken': intent,
            'tool_result': tool_result,
            'data': {'tool_executed': intent != 'chat'}
        }

    def _classify_intent(self, message: str) -> str:
        """Use LLM to classify user intent - much more accurate than keyword matching"""
        import aiohttp
        import asyncio

        # Concise prompt to minimize tokens
        intent_prompt = f"""Classify this message into ONE category:

Categories: verify, calculate, analyze_lane, compare_puzzles, drift_stats, calibration, generate_calibration, discover_lanes, list_puzzles, query_puzzle, validate, chat

Rules:
- verify = check if ladder math works (y=Ax+C) on EXISTING solved puzzles
- calculate = compute private key for a puzzle using affine math (NOT predict!)
- discover_lanes = show all 16 lanes with their A multipliers and weakness
- generate_calibration = CREATE/GENERATE a new calibration JSON file
- calibration = SHOW current A/C values (read only)
- analyze_lane = detailed analysis of ONE specific lane
- chat = questions, planning, discussion, assessment, status

Message: "{message[:500]}"

Reply with ONE word only:"""

        # Direct API call to avoid token management interference
        async def classify():
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": self.model_name,
                        "prompt": intent_prompt,
                        "options": {"temperature": 0.1, "num_predict": 10},
                        "stream": False
                    }
                    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
                    headers = {"Content-Type": "application/json"}
                    api_key = os.getenv("OLLAMA_API_KEY")
                    if api_key:
                        headers["Authorization"] = f"Bearer {api_key}"

                    async with session.post(
                        f"{base_url}/api/generate",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            text = await response.text()
                            try:
                                result = json.loads(text)
                                return result.get('response', '')
                            except:
                                return text
            except Exception as e:
                return ''

        try:
            intent_response = asyncio.run(classify())
        except:
            intent_response = ''

        # Parse the response - extract just the intent word
        if intent_response:
            # Clean up response - get first word, lowercase, strip
            intent = intent_response.strip().lower().split()[0] if intent_response.strip() else 'chat'
            # Remove any punctuation
            intent = ''.join(c for c in intent if c.isalnum() or c == '_')

            # Validate it's a known intent
            valid_intents = ['verify', 'calculate', 'analyze_lane', 'compare_puzzles',
                           'drift_stats', 'calibration', 'generate_calibration',
                           'discover_lanes', 'list_puzzles', 'query_puzzle', 'validate', 'chat']
            if intent in valid_intents:
                return intent

        # Fallback to chat if LLM classification fails
        return 'chat'

    def _execute_tool(self, intent: str, message: str) -> Optional[Dict]:
        """Execute the appropriate tool based on intent"""
        import re

        if intent == 'verify':
            # Check for custom range
            match = re.search(r'(\d+)\s*[-to]+\s*(\d+)', message)
            if match:
                start, end = int(match.group(1)), int(match.group(2))
                return self.tools.verify_ladder(start, end)
            return self.tools.verify_ladder()

        elif intent == 'calculate':
            # CALCULATE (not predict!) a puzzle using affine math
            # Extract target puzzle number
            numbers = re.findall(r'\d+', message)
            target = None  # No default - must specify
            for n in numbers:
                n = int(n)
                if 1 <= n <= 160:
                    target = n
                    break
            return self.tools.calculate_puzzle(target)

        elif intent == 'discover_lanes':
            # Show all 16 lanes with their mathematical properties
            return self.tools.discover_lanes()

        elif intent == 'generate_calibration':
            # Generate a new calibration file
            # Extract range if specified
            numbers = re.findall(r'\d+', message)
            start, end = 1, 70  # Default
            if len(numbers) >= 2:
                start, end = int(numbers[0]), int(numbers[1])
            return self.tools.generate_calibration(start, end)

        elif intent == 'analyze_lane':
            # Extract lane number
            match = re.search(r'lane\s*(\d+)', message.lower())
            if match:
                lane = int(match.group(1))
                if 0 <= lane <= 15:
                    return self.tools.analyze_lane(lane)
            return {'success': False, 'error': 'Please specify a lane number 0-15'}

        elif intent == 'compare_puzzles':
            # Extract two puzzle numbers
            numbers = re.findall(r'\d+', message)
            if len(numbers) >= 2:
                p1, p2 = int(numbers[0]), int(numbers[1])
                return self.tools.compare_puzzles(p1, p2)
            return {'success': False, 'error': 'Please specify two puzzle numbers to compare'}

        elif intent == 'drift_stats':
            return self.tools.compute_drift_stats()

        elif intent == 'calibration':
            return self.tools.get_calibration()

        elif intent == 'list_puzzles':
            return self.tools.list_puzzles()

        elif intent == 'query_puzzle':
            # Extract puzzle number from message
            match = re.search(r'puzzle\s*(\d+)', message.lower())
            if match:
                bits = int(match.group(1))
                return self.tools.get_puzzle(bits)
            # Try just finding a number
            numbers = re.findall(r'\d+', message)
            if numbers:
                return self.tools.get_puzzle(int(numbers[0]))
            return None

        elif intent == 'validate':
            # Extract hex from message
            match = re.search(r'0x[0-9a-fA-F]+', message)
            if match:
                return self.tools.validate_address(match.group(0))
            return None

        return None

    def _generate_explanation(self, user_message: str, intent: str,
                              tool_result: Optional[Dict], use_rag: bool) -> str:
        """Use the LLM to explain results to the user"""

        # For chat-only, just respond naturally
        if intent == 'chat' or tool_result is None:
            return self._chat_response(user_message, use_rag)

        # Build context with tool results
        context = self._build_context(intent, tool_result)

        system_prompt = """You are Chattie, the Bitcoin Puzzle Ladder AI - a MATHEMATICAL CALCULATION system.

CRITICAL: This is MATHEMATICS, not prediction or guessing.
- We CALCULATE using the affine recurrence: y = A[lane] * x + C[lane] mod 256
- Every result is DETERMINISTIC - same input = same output
- We VERIFY results by deriving Bitcoin addresses and matching against known solutions

The system has these mathematical tools:
- calculate: Compute private keys using affine math, then verify via BTC address derivation
- verify: Check if the affine model holds for solved puzzles
- discover_lanes: Show all 16 lanes with A multipliers and C drift values
- generate_calibration: Create calibration file from database puzzles
- analyze_lane: Deep dive into one lane's mathematical behavior

When presenting results:
1. Use MATHEMATICAL language: "calculated", "computed", "derived", "verified"
2. NEVER say "predicted" or "guessed" - this is deterministic math
3. Show the verification: key → pubkey → address → MATCH/MISMATCH
4. If MISMATCH: explain what calibration adjustment is needed
5. If MATCH: confirm "MATH PROVEN CORRECT"

The goal: Discover the mathematical structure of the ladder so we can CALCULATE any puzzle."""

        prompt = f"""User asked: {user_message}

Tool executed: {intent}

Tool result:
{json.dumps(tool_result, indent=2)}

Please explain this result to the user in a helpful way."""

        response = generate_with_ollama_sync(
            model=self.model_name,
            prompt=prompt,
            system=system_prompt,
            max_tokens=16384,  # Ollama cloud max output tokens
            temperature=0.3
        )

        if response is None or response.startswith("Error"):
            # Fallback: just format the tool result nicely
            return self._format_tool_result(intent, tool_result)

        return response

    def _chat_response(self, message: str, use_rag: bool) -> str:
        """Handle general chat without tools"""

        # Get real database info to include in system prompt
        db_info = self.tools.list_puzzles()
        puzzles_summary = ""
        consecutive_range = "unknown"
        bridge_list = []
        if db_info.get('success'):
            consecutive_range = db_info['consecutive_range']
            bridge_list = db_info['bridge_puzzles']
            puzzles_summary = f"""
DATABASE FACTS (from kh.db - DYNAMIC, READ FROM ACTUAL DATABASE):
- Total puzzles: {db_info['total']}
- Consecutive range: {consecutive_range} (these are SOLVED and in database)
- Bridge puzzles: {bridge_list} (these are also SOLVED)
- Gaps (unsolved): {db_info['gaps'][:20]}... (these are UNSOLVED targets)
- IMPORTANT: All puzzles listed above are in the database with known private keys!
"""

        system_prompt = f"""You are Chattie, the Bitcoin Puzzle Ladder AI - a MATHEMATICAL CALCULATION system.

CRITICAL MINDSET: This is PURE MATHEMATICS, not prediction or guessing.
- The affine recurrence y = A*x + C mod 256 is a DETERMINISTIC equation
- We CALCULATE keys, we don't predict them
- We VERIFY calculations by deriving Bitcoin addresses and matching known solutions

{puzzles_summary}

Available MATHEMATICAL tools:
- "calculate puzzle N" - CALCULATE private key using affine math, then VERIFY via BTC address
- "verify the ladder" - Check affine model against solved puzzles
- "discover lanes" - Show all 16 lanes with A multipliers and weakness analysis
- "generate calibration 1 70" - CREATE calibration file from puzzles 1-70
- "analyze lane N" - Deep mathematical analysis of one lane (0-15)
- "compute drift" - Analyze drift constant patterns across blocks
- "show calibration" - Display current A matrix and C values
- "show puzzle N" - Get raw puzzle data from database

LANGUAGE RULES:
- Say "calculate", "compute", "derive" - NEVER "predict" or "guess"
- Say "verification matched" or "math proven correct" - not "prediction was right"
- If calculation doesn't match known address: "calibration needs adjustment"

Database has puzzles {consecutive_range} (consecutive) plus bridges {bridge_list}.

Help users understand the mathematics and guide them to discover the ladder structure."""

        # Add RAG context if enabled
        context = ""
        if use_rag:
            context = self.memory.build_context_summary()

        prompt = f"{context}\n\nUser: {message}" if context else message

        response = generate_with_ollama_sync(
            model=self.model_name,
            prompt=prompt,
            system=system_prompt,
            max_tokens=16384,  # Ollama cloud max output tokens
            temperature=0.5
        )

        return response or "I'm here to help with the Bitcoin Puzzle Ladder. What would you like to do?"

    def _build_context(self, intent: str, tool_result: Dict) -> str:
        """Build context for explanation"""
        return f"Intent: {intent}\nResult: {json.dumps(tool_result)}"

    def _format_tool_result(self, intent: str, result: Dict) -> str:
        """Format tool result as readable message (fallback)"""

        if intent == 'verify':
            if result.get('perfect'):
                return f"**Verification Complete**\n\nForward: {result.get('forward_pct', 'N/A')}%\nReverse: {result.get('reverse_pct', 'N/A')}%\n\nThe ladder is calibrated correctly!"
            else:
                return f"**Verification Result**\n\nForward: {result.get('forward_pct', 'N/A')}%\nReverse: {result.get('reverse_pct', 'N/A')}%\n\n```\n{result.get('output', '')}\n```"

        elif intent == 'calculate':
            if result.get('success'):
                verification = result.get('verification', {})
                match_status = verification.get('MATCH', 'UNKNOWN')
                conclusion = verification.get('conclusion', '')
                return f"""**Mathematical Calculation Result**

Method: {result.get('method', 'Affine recurrence')}
Formula: {result.get('formula', 'y = A*x + C mod 256')}

Source Puzzle: {result.get('source_puzzle')}
Target Puzzle: {result.get('target_puzzle')}
Steps Calculated: {result.get('steps_calculated')}

**Calculated Key:** `{result.get('calculated_key')}`
Lane Values: {result.get('lane_values')}

**Verification:**
- Derived Address: {verification.get('derived_address', 'N/A')}
- Expected Address: {verification.get('expected_address', 'N/A')}
- **MATCH: {match_status}**
- Conclusion: {conclusion}
"""
            else:
                return f"Calculation failed: {result.get('error', 'Unknown error')}"

        elif intent == 'discover_lanes':
            if result.get('success'):
                lanes = result.get('lanes', {})
                output = "**Lane Discovery - Mathematical Structure**\n\n"
                for lane, info in sorted(lanes.items()):
                    output += f"Lane {lane}: A={info['A_multiplier']} ({info['A_hex']}) - {info['weakness']}\n"
                return output
            else:
                return f"Lane discovery failed: {result.get('error')}"

        elif intent == 'generate_calibration':
            if result.get('success'):
                return f"""**Calibration File Generated**

File: {result.get('file_created')}
Range: {result.get('range')}
Puzzles Used: {result.get('puzzles_used')}
Blocks Calibrated: {result.get('blocks_calibrated')}

{result.get('message')}
"""
            else:
                return f"Calibration generation failed: {result.get('error')}"

        elif intent == 'calibration':
            a_matrix = result.get('A', {})
            lines = ["**A Matrix (Lane Multipliers)**\n"]
            for i in range(16):
                lines.append(f"Lane {i}: A[{i}] = {a_matrix.get(str(i), 'N/A')}")
            return '\n'.join(lines)

        elif intent == 'query_puzzle':
            if result.get('success'):
                return f"**Puzzle {result['bits']}**\n\nHex: `{result['hex']}`\n\nLanes: `{result['lanes']}`"
            else:
                return f"Error: {result.get('error', 'Unknown error')}"

        elif intent == 'list_puzzles':
            if result.get('success'):
                lines = ["**Database Contents**\n"]
                lines.append(f"- **Total puzzles:** {result['total']}")
                lines.append(f"- **Consecutive (solved):** {result['consecutive_range']}")
                lines.append(f"- **Bridge puzzles:** {result['bridge_puzzles']}")
                lines.append(f"- **Gaps (unsolved):** {result['gaps'][:15]}...")
                return '\n'.join(lines)
            else:
                return f"Error: {result.get('error', 'Unknown error')}"

        return json.dumps(result, indent=2)


# Global instance
_agent: Optional[ChattieV3] = None

def get_agent() -> ChattieV3:
    """Get or create the agent instance"""
    global _agent
    if _agent is None:
        _agent = ChattieV3()
    return _agent

def process_chat_message_with_rag(message: str, use_rag: bool = True) -> Dict:
    """API endpoint function"""
    agent = get_agent()
    return agent.process_message(message, use_rag)

def get_conversation_history() -> List[Dict]:
    """Get conversation history"""
    agent = get_agent()
    return agent.conversation_history


if __name__ == '__main__':
    print("=" * 60)
    print("Chattie V3 - Tool-Based Agent")
    print("=" * 60)

    agent = ChattieV3()

    # Test intent classification
    test_messages = [
        "verify the ladder",
        "predict puzzle",
        "what is the A matrix?",
        "show puzzle 70",
        "hello, how are you?",
    ]

    print("\nIntent Classification:")
    for msg in test_messages:
        intent = agent._classify_intent(msg)
        print(f"  '{msg}' -> {intent}")

    print("\n" + "=" * 60)
    print("Testing tool execution...")
    print("=" * 60)

    # Test verify
    print("\n[Testing verify_ladder]")
    result = agent.tools.verify_ladder()
    print(f"  Success: {result.get('success')}")
    print(f"  Forward: {result.get('forward_pct')}%")
    print(f"  Reverse: {result.get('reverse_pct')}%")

    # Test predict
    print("\n[Testing predict_next]")
    result = agent.tools.predict_next()
    print(f"  Success: {result.get('success')}")
    print(f"  Predicted: {result.get('predicted_hex', 'N/A')[:20]}...")

    # Test calibration
    print("\n[Testing get_calibration]")
    result = agent.tools.get_calibration()
    print(f"  Success: {result.get('success')}")
    print(f"  A matrix: {result.get('A', {})}")
