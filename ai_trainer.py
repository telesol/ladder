#!/usr/bin/env python3
"""
AI Training System for Bitcoin Puzzle Mathematics
Walks local AI through exercises and evaluates responses.
"""

import json
import sqlite3
import os
from datetime import datetime
import puzzle_config  # Central config - all data from DB

# Reference data - loaded from DB via puzzle_config
KEYS = puzzle_config.KEYS  # All 74 known keys

A_MULTIPLIERS = {0: 1, 1: 91, 2: 1, 3: 1, 4: 1, 5: 169, 6: 1, 7: 1, 8: 1, 9: 32, 10: 1, 11: 1, 12: 1, 13: 182, 14: 1, 15: 1}


class AITrainer:
    def __init__(self, db_path="/home/solo/LA/db/kh.db"):
        self.db_path = db_path
        self.session_log = []
        self.scores = {"level_1": [], "level_2": [], "level_3": [], "level_4": []}

    def log(self, message):
        """Log training session message."""
        timestamp = datetime.now().isoformat()
        self.session_log.append({"time": timestamp, "message": message})
        print(f"[{timestamp}] {message}")

    def get_exercise(self, level, exercise_num):
        """Get exercise prompt for AI."""
        exercises = {
            (1, 1): self._exercise_1_1,
            (1, 2): self._exercise_1_2,
            (1, 3): self._exercise_1_3,
            (2, 1): self._exercise_2_1,
            (2, 2): self._exercise_2_2,
            (2, 3): self._exercise_2_3,
            (2, 4): self._exercise_2_4,
            (2, 5): self._exercise_2_5,
            (3, 1): self._exercise_3_1,
            (3, 2): self._exercise_3_2,
        }
        return exercises.get((level, exercise_num), lambda: "Exercise not found")()

    def _exercise_1_1(self):
        """Basic Key Properties - Range calculation."""
        return {
            "level": 1,
            "exercise": 1,
            "title": "Basic Key Properties",
            "instructions": "For each puzzle number N, calculate the valid range [low, high] for key k_N.",
            "formula": "low = 2^(N-1), high = 2^N - 1",
            "test_cases": [
                {"N": 5, "expected_low": 16, "expected_high": 31},
                {"N": 20, "expected_low": 524288, "expected_high": 1048575},
                {"N": 71, "expected_low": 2**70, "expected_high": 2**71 - 1},
            ],
            "prompt_for_ai": """
Exercise 1.1: Basic Key Properties

Given puzzle number N, the private key k_N must be in the range [2^(N-1), 2^N - 1].

Calculate the valid range for:
1. N = 5: Range = [?, ?]
2. N = 20: Range = [?, ?]
3. N = 71: Range = [?, ?]

Show your calculations.
"""
        }

    def _exercise_1_2(self):
        """Key Factorization."""
        return {
            "level": 1,
            "exercise": 2,
            "title": "Key Factorization",
            "test_cases": [
                {"key": "k_5", "value": 21, "expected_factors": [3, 7]},
                {"key": "k_6", "value": 49, "expected_factors": [7, 7]},
                {"key": "k_17", "value": 95823, "expected_factors": [3, 3, 3, 3, 7, 13, 13]},
            ],
            "prompt_for_ai": """
Exercise 1.2: Key Factorization

Factorize these puzzle keys and identify any special properties:

1. k_5 = 21
   Factors: ?
   Special property: ?

2. k_6 = 49
   Factors: ?
   Special property: ?

3. k_17 = 95823
   Factors: ?
   Special property: ?

Hint: Look for relationships to other keys or to the puzzle number.
"""
        }

    def _exercise_1_3(self):
        """Position in Range."""
        return {
            "level": 1,
            "exercise": 3,
            "title": "Position in Range",
            "formula": "position = (k_N - 2^(N-1)) / (2^N - 1 - 2^(N-1)) × 100%",
            "test_cases": [
                {"key": "k_3", "value": 7, "N": 3, "expected_pct": 100.0},
                {"key": "k_69", "value": 297274491920375905804, "N": 69, "expected_pct": 0.72},
                {"key": "k_70", "value": 970436974005023690481, "N": 70, "expected_pct": 64.40},
            ],
            "prompt_for_ai": """
Exercise 1.3: Position in Range

Calculate where each key sits in its valid range.
Formula: position% = (k_N - 2^(N-1)) / (2^N - 1 - 2^(N-1)) × 100

1. k_3 = 7, N = 3
   Position = ?%

2. k_69 = 297274491920375905804, N = 69
   Position = ?%

3. k_70 = 970436974005023690481, N = 70
   Position = ?%

Why is the position of k_69 significant?
"""
        }

    def _exercise_2_1(self):
        """Verify Exact Relationships."""
        return {
            "level": 2,
            "exercise": 1,
            "title": "Verify Exact Relationships",
            "test_cases": [
                {"claim": "k_6 = k_3²", "given": {"k_3": 7, "k_6": 49}},
                {"claim": "k_8 = k_4 × k_3 × 4", "given": {"k_4": 8, "k_3": 7, "k_8": 224}},
                {"claim": "k_7 = k_2 × k_5", "given": {"k_2": 3, "k_5": 21, "k_7": 76}},
            ],
            "prompt_for_ai": """
Exercise 2.1: Verify Exact Relationships

For each claim, verify if it's TRUE or FALSE:

1. Claim: k_6 = k_3²
   Given: k_3 = 7, k_6 = 49
   Verification: ?

2. Claim: k_8 = k_4 × k_3 × 4
   Given: k_4 = 8, k_3 = 7, k_8 = 224
   Verification: ?

3. Claim: k_7 = k_2 × k_5
   Given: k_2 = 3, k_5 = 21, k_7 = 76
   Verification: ?
"""
        }

    def _exercise_2_2(self):
        """Linear Recurrence Test."""
        return {
            "level": 2,
            "exercise": 2,
            "title": "Linear Recurrence Test",
            "prompt_for_ai": """
Exercise 2.2: Linear Recurrence Test

Test the linear recurrence k_n = a × k_{n-1} + b × k_{n-2}:

1. Verify: k_4 = -7 × k_3 + 19 × k_2
   Given: k_2 = 3, k_3 = 7, k_4 = 8
   Calculation: ?

2. Verify: k_5 = -14 × k_4 + 19 × k_3
   Given: k_3 = 7, k_4 = 8, k_5 = 21
   Calculation: ?

3. Test: Does k_7 = a × k_6 + 19 × k_5 for ANY integer a?
   Given: k_5 = 21, k_6 = 49, k_7 = 76
   Analysis: ?

What does this tell us about the recurrence pattern?
"""
        }

    def _exercise_2_3(self):
        """Normalized Delta Calculation."""
        return {
            "level": 2,
            "exercise": 3,
            "title": "Normalized Delta Calculation",
            "prompt_for_ai": """
Exercise 2.3: Normalized Delta Calculation

Formula: Normalized_Delta = (k_{n+1} - k_n) / 2^n

Calculate for these transitions:

1. k_1 = 1, k_2 = 3
   Delta = ?
   Normalized = ? / 2^1 = ?

2. k_9 = 467, k_10 = 514
   Delta = ?
   Normalized = ? / 2^9 = ?

3. k_69 = 297274491920375905804, k_70 = 970436974005023690481
   Delta = ?
   Normalized = ? / 2^69 = ?

Known bounds: Normalized delta is typically in [0.09, 1.31] with mean 0.76.
Which of these is anomalous?
"""
        }

    def _exercise_2_4(self):
        """Affine Model Verification."""
        return {
            "level": 2,
            "exercise": 4,
            "title": "Affine Model Verification",
            "prompt_for_ai": """
Exercise 2.4: Affine Model Verification

The affine model: y = A × x + C (mod 256)
where x is a byte of k_n and y is the same byte of k_{n+1}

A multipliers: Lane 0: A=1, Lane 1: A=91, Lane 5: A=169

Calculate C for these transitions:

1. Lane 0 (A=1): x = 12, y = 241
   C = (y - A×x) mod 256 = ?

2. Lane 1 (A=91): x = 104, y = 53
   C = (y - A×x) mod 256 = ?

3. Lane 5 (A=169): x = 177, y = 215
   C = (y - A×x) mod 256 = ?

CRITICAL QUESTION: Why can't we use this model to PREDICT unknown keys?
"""
        }

    def _exercise_2_5(self):
        """Bridge Ratio Analysis."""
        return {
            "level": 2,
            "exercise": 5,
            "title": "Bridge Ratio Analysis",
            "prompt_for_ai": """
Exercise 2.5: Bridge Ratio Analysis

Bridge puzzles are 5 apart (70, 75, 80, 85, 90...).
Expected ratio for 5-step jump: ~2^5 = 32

Calculate actual ratios:

1. k_75 / k_70 = 22538323240989823823367 / 970436974005023690481 = ?
   Compare to expected 32: deviation = ?%

2. k_80 / k_75 = 1105520030589234487939456 / 22538323240989823823367 = ?
   Compare to expected 32: deviation = ?%

3. k_85 / k_80 = 21090315766411506144426920 / 1105520030589234487939456 = ?
   Compare to expected 32: deviation = ?%

What do these deviations tell us about key growth patterns?
"""
        }

    def _exercise_3_1(self):
        """Anomaly Detection."""
        return {
            "level": 3,
            "exercise": 1,
            "title": "Anomaly Detection",
            "prompt_for_ai": """
Exercise 3.1: Anomaly Detection

Identify and explain what makes each of these anomalous:

1. k_69 = 297274491920375905804
   What is anomalous about this key?
   Why did this allow k_69 to be solved quickly after k_68?

2. The transition 9→10 has normalized delta = 0.092
   What is anomalous about this?
   What does it mean that k_10 barely grew?

3. A[lane 9] = 32 while A[lane 1] = 91, A[lane 5] = 169, A[lane 13] = 182
   What is anomalous about lane 9?
   What pattern do the other lanes follow that lane 9 breaks?
"""
        }

    def _exercise_3_2(self):
        """Constraint Derivation."""
        return {
            "level": 3,
            "exercise": 2,
            "title": "Constraint Derivation",
            "prompt_for_ai": """
Exercise 3.2: Constraint Derivation for Puzzle 71

Given:
- Normalized delta historical range: [0.09, 1.31]
- k_70 = 970436974005023690481
- k_71 must be in [2^70, 2^71 - 1]

Derive the tightest constraint on k_71:

1. From bit range: k_71 ∈ [?, ?]

2. From delta constraint:
   k_71 >= k_70 + 0.09 × 2^70 = ?
   k_71 <= k_70 + 1.31 × 2^70 = ?

3. Combined constraint: k_71 ∈ [?, ?]

4. Does the delta constraint reduce the search space below the bit range?
   Calculate the percentage reduction (if any).
"""
        }

    def evaluate_response(self, level, exercise, ai_response, expected):
        """Evaluate AI's response against expected answer."""
        # This is a simplified evaluator - in practice, would use NLP/regex matching
        score = 0
        feedback = []

        # Check for key elements in response
        if isinstance(expected, dict):
            for key, value in expected.items():
                if str(value).lower() in ai_response.lower():
                    score += 1
                    feedback.append(f"✓ Found expected: {key}")
                else:
                    feedback.append(f"✗ Missing: {key} = {value}")

        max_score = len(expected) if isinstance(expected, dict) else 1
        percentage = (score / max_score * 100) if max_score > 0 else 0

        return {
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "feedback": feedback,
            "passed": percentage >= 70
        }

    def run_training_session(self, level, exercises=None):
        """Run a full training session for a level."""
        self.log(f"Starting Level {level} training session")

        if exercises is None:
            exercises = {1: [1, 2, 3], 2: [1, 2, 3, 4, 5], 3: [1, 2]}[level]

        results = []
        for ex in exercises:
            exercise_data = self.get_exercise(level, ex)
            results.append({
                "level": level,
                "exercise": ex,
                "title": exercise_data.get("title", "Unknown"),
                "prompt": exercise_data.get("prompt_for_ai", "")
            })

        return results

    def generate_training_prompt(self):
        """Generate complete training prompt for local AI."""
        prompt = """# Bitcoin Puzzle Mathematics - Training Session

You are being trained to understand and analyze Bitcoin puzzle private keys.
The goal is to find mathematical patterns that can help solve unsolved puzzles.

## Key Facts to Learn:

1. **Key Range**: Puzzle N has key k_N in range [2^(N-1), 2^N - 1]

2. **Exact Early Relationships**:
   - k_5 = k_2 × k_3 = 3 × 7 = 21
   - k_6 = k_3² = 7² = 49
   - k_8 = k_4 × k_3 × 4 = 8 × 7 × 4 = 224

3. **Linear Recurrence (coefficient 19)**:
   - k_3 = -4×k_2 + 19×k_1
   - k_4 = -7×k_3 + 19×k_2
   - k_5 = -14×k_4 + 19×k_3
   - Pattern breaks after k_6

4. **Normalized Delta**: (k_{n+1} - k_n) / 2^n
   - Range: [0.09, 1.31]
   - Mean: 0.76

5. **Position Anomalies**:
   - k_69 at 0.72% of range (solved quickly)
   - k_4 at 0.00% of range
   - k_2, k_3 at 100% of range

6. **A Multipliers** (affine model):
   - Lane 1: A = 91 = 7 × 13
   - Lane 5: A = 169 = 13²
   - Lane 9: A = 32 = 2^5 (anomaly!)
   - Lane 13: A = 182 = 14 × 13

## Your Task:

Answer the following exercises to demonstrate understanding.
Show all calculations and explain your reasoning.

"""

        # Add all exercises
        for level in [1, 2, 3]:
            prompt += f"\n## LEVEL {level} EXERCISES\n\n"
            exercises = self.run_training_session(level)
            for ex in exercises:
                prompt += f"### {ex['title']}\n"
                prompt += ex['prompt'] + "\n"

        return prompt

    def save_session(self, filename="training_session.json"):
        """Save training session to file."""
        with open(filename, 'w') as f:
            json.dump({
                "log": self.session_log,
                "scores": self.scores
            }, f, indent=2)


def main():
    """Main entry point for training."""
    trainer = AITrainer()

    # Generate the training prompt
    prompt = trainer.generate_training_prompt()

    # Save to file
    with open("/home/solo/LA/AI_TRAINING_PROMPT.md", 'w') as f:
        f.write(prompt)

    print("Training prompt generated: /home/solo/LA/AI_TRAINING_PROMPT.md")
    print("\nTo train local AI:")
    print("1. Send the content of AI_TRAINING_PROMPT.md to your local AI")
    print("2. Have the AI answer all exercises")
    print("3. Compare answers to AI_TRAINING_ANSWER_KEY.json")
    print("4. Iterate until AI passes all levels")


if __name__ == "__main__":
    main()
