#!/usr/bin/env python3
"""
Context Builder - Provides rich context to the AI model for mathematical reasoning

The model needs:
1. The calibration data (A matrix, Cstar drift constants)
2. Puzzle values from the database
3. The mathematical framework (formulas, rules)
4. Current state (what's computed, what's missing)
"""
import json
import sqlite3
import os
from typing import Dict, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KH_ASSIST = os.path.join(BASE_DIR, 'kh-assist')
DB_PATH = os.path.join(KH_ASSIST, 'db', 'kh.db')
CALIB_PATH = os.path.join(KH_ASSIST, 'out', 'ladder_calib_29_70_full.json')


def load_calibration() -> Dict:
    """Load the calibration JSON with A matrix and Cstar"""
    try:
        with open(CALIB_PATH) as f:
            return json.load(f)
    except Exception as e:
        return {'error': str(e)}


def get_puzzle_values(bits_list: List[int]) -> Dict[int, str]:
    """Get puzzle hex values from database for specific bit numbers"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        placeholders = ','.join('?' * len(bits_list))
        cur.execute(f"""
            SELECT bits, actual_hex
            FROM lcg_residuals
            WHERE bits IN ({placeholders})
            ORDER BY bits
        """, bits_list)

        results = {row[0]: row[1] for row in cur.fetchall()}
        conn.close()
        return results
    except Exception as e:
        return {'error': str(e)}


def get_lane_bytes(hex_value: str, lane: int) -> int:
    """Extract a specific lane's byte from a hex value

    The hex format is: 0x<64 hex chars> = 32 bytes
    First 16 bytes (32 hex chars) are the key half-block
    Each lane corresponds to one byte position
    """
    # Remove 0x prefix if present
    hex_clean = hex_value.lower().replace('0x', '')

    # Pad to 64 chars if needed
    hex_clean = hex_clean.zfill(64)

    # First 32 hex chars = first 16 bytes = the key half-block
    first_half = hex_clean[:32]

    # Each lane is 2 hex characters (1 byte)
    start = lane * 2
    byte_hex = first_half[start:start+2]

    return int(byte_hex, 16) if byte_hex else 0


def format_a_matrix(calib: Dict) -> str:
    """Format the A matrix for display to the model"""
    if 'A' not in calib:
        return "A matrix not found in calibration"

    lines = ["A Matrix (Lane Multipliers):"]
    for lane in range(16):
        a_val = calib['A'].get(str(lane), 'missing')
        lines.append(f"  Lane {lane:2d}: A[{lane}] = {a_val}")

    return '\n'.join(lines)


def format_cstar(calib: Dict) -> str:
    """Format the Cstar drift constants for display"""
    if 'Cstar' not in calib:
        return "Cstar not found in calibration"

    lines = ["Cstar (Drift Constants):"]
    cstar = calib['Cstar']

    for block_id, block_data in cstar.items():
        lines.append(f"  Block {block_id}:")
        for lane_id, lane_data in block_data.items():
            if isinstance(lane_data, list):
                lines.append(f"    Lane {lane_id}: {lane_data}")
            else:
                lines.append(f"    Lane {lane_id}: {lane_data}")

    return '\n'.join(lines)


def build_math_context() -> str:
    """Build the mathematical framework context for the model"""
    return """## The Affine Recurrence Model

The Bitcoin puzzle ladder follows a deterministic affine recurrence in GF(2^8):

**Formula for each lane ℓ ∈ {0, 1, ..., 15}:**
```
X_{k+1}(ℓ) = A[ℓ] × X_k(ℓ) + C[block][ℓ][occ]  (mod 256)
```

Where:
- X_k(ℓ) = byte value at position ℓ for puzzle k
- A[ℓ] = lane multiplier (constant for each lane)
- C[block][ℓ][occ] = drift constant (varies by block, lane, occurrence)
- All arithmetic is modulo 256 (byte-level)

**For multi-step computation (e.g., from puzzle 75 to 80):**
```
X_{k+n}(ℓ) = A[ℓ]^n × X_k(ℓ) + Γ_n × C_0(ℓ)  (mod 256)

Where Γ_n = A^{n-1} + A^{n-2} + ... + A + 1  (mod 256)
```

**For 5-step gap (bridges 75→80):**
```
Γ_5 = A^4 + A^3 + A^2 + A + 1  (mod 256)

Solving for drift: C_0(ℓ) = (X_80(ℓ) - A^5 × X_75(ℓ)) × Γ_5^{-1}  (mod 256)
```

**Important Rules:**
1. All byte values are 0-255 (mod 256 arithmetic)
2. Database stores values in LITTLE-ENDIAN byte order
3. 16 lanes operate independently in parallel
4. Lanes with A[ℓ] = 1 have simpler recurrence: X_{k+1} = X_k + C (mod 256)
5. Non-unity lanes (A ≠ 1): 1, 5, 9, 13 need full affine computation
"""


def hex_to_big_endian(hex_val: str) -> str:
    """Convert little-endian DB hex to big-endian (human readable)"""
    # Remove 0x prefix
    hex_clean = hex_val.lower().replace('0x', '')
    # Reverse bytes (each byte = 2 hex chars)
    bytes_list = [hex_clean[i:i+2] for i in range(0, len(hex_clean), 2)]
    return ''.join(reversed(bytes_list))


def build_data_context(include_puzzles: List[int] = None) -> str:
    """Build the data context showing current puzzle values"""
    if include_puzzles is None:
        include_puzzles = [70, 75, 80]  # Key puzzles for computation

    puzzle_data = get_puzzle_values(include_puzzles)

    lines = ["## Current Puzzle Data"]
    lines.append("")
    lines.append("**CRITICAL: Byte Order**")
    lines.append("- Database stores LITTLE-ENDIAN (Lane 0 = leftmost byte)")
    lines.append("- Human-readable is BIG-ENDIAN (rightmost byte = Lane 0)")
    lines.append("- The LANES array below is the correct format for computation")
    lines.append("")

    for bits in include_puzzles:
        if bits in puzzle_data:
            hex_val = puzzle_data[bits]
            big_endian = hex_to_big_endian(hex_val.replace('0x', ''))

            lines.append(f"### Puzzle {bits}")
            lines.append(f"  Big-endian (human): 0x{big_endian}")
            lines.append(f"  Little-endian (DB): {hex_val}")

            # Show lane breakdown - THIS IS WHAT MATTERS FOR COMPUTATION
            lane_vals = []
            for lane in range(16):
                byte_val = get_lane_bytes(hex_val, lane)
                lane_vals.append(f"{byte_val:3d}")
            lines.append(f"  **Lanes 0-15: [{', '.join(lane_vals)}]** ← USE THIS FOR MATH")
            lines.append("")
        else:
            lines.append(f"### Puzzle {bits}: NOT IN DATABASE")
            lines.append("")

    return '\n'.join(lines)


def build_calibration_context() -> str:
    """Build the calibration context"""
    calib = load_calibration()

    if 'error' in calib:
        return f"Error loading calibration: {calib['error']}"

    lines = ["## Calibration Data"]
    lines.append("")
    lines.append(format_a_matrix(calib))
    lines.append("")
    lines.append(format_cstar(calib))

    return '\n'.join(lines)


def build_full_context(task: str = None, include_puzzles: List[int] = None) -> str:
    """Build the complete context for the model

    Args:
        task: Optional description of what the model should focus on
        include_puzzles: List of puzzle numbers to include data for
    """
    sections = []

    # Task description
    if task:
        sections.append(f"## Current Task\n{task}\n")

    # Mathematical framework
    sections.append(build_math_context())

    # Calibration data
    sections.append(build_calibration_context())

    # Puzzle data
    sections.append(build_data_context(include_puzzles))

    return '\n\n'.join(sections)


def build_drift_computation_context(lane: int = None) -> str:
    """Build specific context for drift computation

    Uses puzzles 75 and 80 (5-step gap) to compute C_0
    """
    calib = load_calibration()
    puzzle_data = get_puzzle_values([75, 80])

    lines = ["## Drift Computation Context"]
    lines.append("")
    lines.append("**Goal:** Compute C_0[ℓ][0] for each lane using bridges 75 and 80")
    lines.append("")
    lines.append("**Method:** With 5-step gap between puzzles 75 and 80:")
    lines.append("```")
    lines.append("X_80 = A^5 × X_75 + Γ_5 × C_0  (mod 256)")
    lines.append("Where Γ_5 = A^4 + A^3 + A^2 + A + 1  (mod 256)")
    lines.append("")
    lines.append("Rearranging:")
    lines.append("C_0 = (X_80 - A^5 × X_75) × Γ_5^{-1}  (mod 256)")
    lines.append("```")
    lines.append("")

    # Show A matrix
    lines.append("**A Matrix Values:**")
    if 'A' in calib:
        for l in range(16):
            a_val = calib['A'].get(str(l), 1)
            lines.append(f"  A[{l:2d}] = {a_val}")

    lines.append("")

    # Show puzzle values per lane
    if 75 in puzzle_data and 80 in puzzle_data:
        lines.append("**Puzzle Values by Lane:**")
        lines.append("```")
        lines.append("Lane | X_75 | X_80 | A[ℓ]")
        lines.append("-----|------|------|-----")
        for l in range(16):
            x75 = get_lane_bytes(puzzle_data[75], l)
            x80 = get_lane_bytes(puzzle_data[80], l)
            a_val = calib['A'].get(str(l), 1) if 'A' in calib else 1
            lines.append(f"  {l:2d} | {x75:4d} | {x80:4d} | {a_val:3d}")
        lines.append("```")

    if lane is not None:
        lines.append("")
        lines.append(f"**Focus on Lane {lane}:**")
        if 75 in puzzle_data and 80 in puzzle_data and 'A' in calib:
            x75 = get_lane_bytes(puzzle_data[75], lane)
            x80 = get_lane_bytes(puzzle_data[80], lane)
            a_val = calib['A'].get(str(lane), 1)
            lines.append(f"  X_75[{lane}] = {x75} (0x{x75:02x})")
            lines.append(f"  X_80[{lane}] = {x80} (0x{x80:02x})")
            lines.append(f"  A[{lane}] = {a_val}")
            lines.append("")
            lines.append(f"  Compute: C_0[{lane}] = ?")

    return '\n'.join(lines)


if __name__ == '__main__':
    print("=" * 60)
    print("Context Builder Test")
    print("=" * 60)

    print("\n### Full Context ###\n")
    print(build_full_context(
        task="Compute the drift constant C_0 for lane 5",
        include_puzzles=[70, 75, 80, 85]
    ))

    print("\n" + "=" * 60)
    print("\n### Drift Computation Context (Lane 5) ###\n")
    print(build_drift_computation_context(lane=5))
