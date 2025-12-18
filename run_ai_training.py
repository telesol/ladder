#!/usr/bin/env python3
"""
Interactive AI Training Session for Bitcoin Puzzle Mathematics

This script walks your local AI through the training curriculum,
evaluates responses, and guides them to mastery.
"""

import requests
import json
import time
import sys
from datetime import datetime

API_BASE = "http://localhost:5050/api"

# Training exercises organized by level
EXERCISES = {
    "level_1": [
        {
            "id": "1.1",
            "title": "Basic Key Properties",
            "prompt": """Let's start with the basics. For Bitcoin puzzle N, the private key k_N must be in a specific bit range.

The rule is: k_N ∈ [2^(N-1), 2^N - 1]

Calculate the valid range for these puzzles:
1. Puzzle 5: Range = [?, ?]
2. Puzzle 20: Range = [?, ?]
3. Puzzle N: Range = [?, ?]

Show your calculations clearly.""",
            "expected_keywords": ["16", "31", "524288", "1048575", "2^70", "2^71"],
            "correct_answers": {
                "N=5": [16, 31],
                "N=20": [524288, 1048575],
                "N=71": [2**70, 2**71 - 1]
            }
        },
        {
            "id": "1.2",
            "title": "Key Factorization",
            "prompt": """Now factorize these puzzle keys and look for patterns:

1. k_5 = 21 → What are the prime factors?
2. k_6 = 49 → What are the prime factors?
3. k_11 = 1155 → What are the prime factors?

For each, identify if there's any relationship to other keys or to the puzzle number.""",
            "expected_keywords": ["3", "7", "5", "11", "k_2", "k_3", "square"],
            "correct_answers": {
                "k_5": "3 × 7 = k_2 × k_3",
                "k_6": "7² = k_3²",
                "k_11": "3 × 5 × 7 × 11 (includes puzzle number)"
            }
        },
        {
            "id": "1.3",
            "title": "Position in Range",
            "prompt": """Calculate where each key sits in its valid range (as percentage).

Formula: position% = (k_N - 2^(N-1)) / (2^N - 1 - 2^(N-1)) × 100

Calculate for:
1. k_3 = 7, N = 3
2. k_4 = 8, N = 4
3. k_69 = 297274491920375905804, N = 69

Which of these is anomalous and why is it significant?""",
            "expected_keywords": ["100", "0", "0.72", "minimum", "maximum", "solved quickly"],
            "correct_answers": {
                "k_3": "100% (maximum value)",
                "k_4": "0% (minimum value)",
                "k_69": "0.72% (very low - solved quickly)"
            }
        }
    ],
    "level_2": [
        {
            "id": "2.1",
            "title": "Verify Exact Relationships",
            "prompt": """Verify these claimed relationships - TRUE or FALSE:

1. Claim: k_6 = k_3²
   Given: k_3 = 7, k_6 = 49

2. Claim: k_8 = k_4 × k_3 × 4
   Given: k_4 = 8, k_3 = 7, k_8 = 224

3. Claim: k_7 = k_2 × k_5
   Given: k_2 = 3, k_5 = 21, k_7 = 76

Show your verification calculations.""",
            "expected_keywords": ["TRUE", "FALSE", "49", "224", "63", "76"],
            "correct_answers": {
                "claim_1": "TRUE: 7² = 49 = k_6",
                "claim_2": "TRUE: 8 × 7 × 4 = 224 = k_8",
                "claim_3": "FALSE: 3 × 21 = 63 ≠ 76"
            }
        },
        {
            "id": "2.2",
            "title": "Linear Recurrence",
            "prompt": """Test the linear recurrence pattern with coefficient 19:

1. Verify: k_4 = -7×k_3 + 19×k_2
   Given: k_2=3, k_3=7, k_4=8

2. Verify: k_5 = -14×k_4 + 19×k_3
   Given: k_3=7, k_4=8, k_5=21

3. Test: Does k_7 = a×k_6 + 19×k_5 work for ANY integer a?
   Given: k_5=21, k_6=49, k_7=76

What does this tell us about when the recurrence pattern breaks?""",
            "expected_keywords": ["-49", "57", "8", "-112", "133", "21", "not integer", "breaks"],
            "correct_answers": {
                "test_1": "-7×7 + 19×3 = -49 + 57 = 8 ✓",
                "test_2": "-14×8 + 19×7 = -112 + 133 = 21 ✓",
                "test_3": "No - requires a = (76 - 399)/49 = -6.59... not integer"
            }
        },
        {
            "id": "2.3",
            "title": "Normalized Delta",
            "prompt": """Calculate the normalized delta for consecutive keys.

Formula: Normalized_Delta = (k_{n+1} - k_n) / 2^n

Calculate for:
1. k_1=1 → k_2=3
2. k_9=467 → k_10=514
3. k_69=297274491920375905804 → k_70=970436974005023690481

Historical bounds: [0.09, 1.31], mean = 0.76

Which transition is anomalous?""",
            "expected_keywords": ["1.0", "0.09", "1.14", "anomal"],
            "correct_answers": {
                "delta_1_2": "(3-1)/2 = 1.0",
                "delta_9_10": "(514-467)/512 = 0.092 (smallest!)",
                "delta_69_70": "≈ 1.14 (normal)"
            }
        },
        {
            "id": "2.4",
            "title": "Affine Model",
            "prompt": """The affine model: y = A×x + C (mod 256)

A values: Lane 0: A=1, Lane 1: A=91, Lane 5: A=169

Calculate C for:
1. Lane 0: x=12, y=241 (A=1)
2. Lane 1: x=104, y=53 (A=91)
3. Lane 5: x=177, y=215 (A=169)

CRITICAL: Explain why this model CANNOT predict unknown keys.""",
            "expected_keywords": ["229", "61", "254", "circular", "requires", "answer"],
            "correct_answers": {
                "C_lane_0": "(241-12) mod 256 = 229",
                "C_lane_1": "(53-91×104) mod 256 = 61",
                "C_lane_5": "(215-169×177) mod 256 = 254",
                "limitation": "C requires knowing y (the answer)"
            }
        },
        {
            "id": "2.5",
            "title": "Bridge Ratios",
            "prompt": """Calculate ratios between bridge puzzles (5-step jumps):

Given:
- k_70 = 970436974005023690481
- k_75 = 22538323240989823823367
- k_80 = 1105520030589234487939456
- k_85 = 21090315766411506144426920

Expected ratio for 5 bits: 2^5 = 32

Calculate:
1. k_75 / k_70 = ?
2. k_80 / k_75 = ?
3. k_85 / k_80 = ?

How far off are these from expected 32?""",
            "expected_keywords": ["23", "49", "19", "32", "deviat"],
            "correct_answers": {
                "ratio_70_75": "≈ 23.22 (-27% from 32)",
                "ratio_75_80": "≈ 49.05 (+53% from 32)",
                "ratio_80_85": "≈ 19.08 (-40% from 32)"
            }
        }
    ],
    "level_3": [
        {
            "id": "3.1",
            "title": "Anomaly Analysis",
            "prompt": """Explain what makes each of these anomalous:

1. k_69 has position 0.72% in its valid range
   Why is this anomalous? Why did it matter for solving?

2. A[lane 9] = 32, while A[lane 1]=91, A[lane 5]=169, A[lane 13]=182
   What pattern do lanes 1, 5, 13 share that lane 9 breaks?

3. The coefficient 19 appears in early recurrences but the pattern breaks at k_6
   What might 19 represent?""",
            "expected_keywords": ["low", "fast", "13", "divisible", "2^5", "break"],
            "correct_answers": {
                "k_69": "At 0.72%, search from low end found it quickly after k_68",
                "lane_9": "91, 169, 182 are all divisible by 13; 32 = 2^5 is not",
                "coef_19": "19 might relate to initial key generation, breaks suggest different algorithm after k_6"
            }
        },
        {
            "id": "3.2",
            "title": "Constraint Derivation",
            "prompt": """Derive constraints for puzzle 71:

Given:
- k_70 = 970436974005023690481
- Normalized delta range: [0.09, 1.31]
- Bit range: k_71 ∈ [2^70, 2^71 - 1]

Calculate:
1. Lower bound from bit range
2. Upper bound from bit range
3. Lower bound from delta: k_70 + 0.09 × 2^70
4. Upper bound from delta: k_70 + 1.31 × 2^70

Which gives the tighter constraint? By how much does it reduce search space?""",
            "expected_keywords": ["2^70", "reduce", "percent", "not much"],
            "correct_answers": {
                "bit_low": "2^70 = 1180591620717411303424",
                "bit_high": "2^71 - 1 = 2361183241434822606847",
                "delta_low": "≈ 1076690219869790707789",
                "delta_high": "≈ 2517011897944892301427",
                "result": "Bit range is tighter - delta doesn't help reduce search"
            }
        }
    ]
}


def send_to_ai(message, model="mistral-large-3:675b-cloud"):
    """Send message to local AI via web app API."""
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            json={
                "message": message,
                "model": model,
                "use_rag": False  # Pure reasoning, no RAG
            },
            timeout=300
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


def evaluate_response(response, exercise):
    """Simple evaluation based on keyword matching."""
    score = 0
    found = []
    missing = []

    for keyword in exercise["expected_keywords"]:
        if keyword.lower() in response.lower():
            score += 1
            found.append(keyword)
        else:
            missing.append(keyword)

    max_score = len(exercise["expected_keywords"])
    percentage = (score / max_score * 100) if max_score > 0 else 0

    return {
        "score": score,
        "max_score": max_score,
        "percentage": percentage,
        "found": found,
        "missing": missing,
        "passed": percentage >= 60
    }


def run_training_session(level="all", model="mistral-large-3:675b-cloud"):
    """Run interactive training session."""
    print("=" * 70)
    print("BITCOIN PUZZLE MATHEMATICS - AI TRAINING SESSION")
    print("=" * 70)
    print(f"\nModel: {model}")
    print(f"Levels: {level}\n")

    # Introduction
    intro = """You are being trained on Bitcoin puzzle mathematics.
Your goal is to understand patterns in puzzle private keys to help solve unsolved puzzles.

Key facts:
- Puzzle N has key k_N in range [2^(N-1), 2^N - 1]
- Early keys have exact relationships: k_5 = k_2 × k_3, k_6 = k_3²
- Linear recurrence with coefficient 19 works for k_3, k_4, k_5 but breaks after
- Normalized delta (k_{n+1} - k_n)/2^n is typically in [0.09, 1.31]
- A multipliers 91, 169, 182 are all divisible by 13 (except lane 9 = 32)

Ready to begin training exercises?"""

    print("Sending introduction to AI...")
    print("-" * 50)
    response = send_to_ai(intro, model)
    print(f"AI: {response[:500]}...")
    print("-" * 50)

    # Run exercises
    levels_to_run = ["level_1", "level_2", "level_3"] if level == "all" else [f"level_{level}"]
    results = {}

    for lvl in levels_to_run:
        if lvl not in EXERCISES:
            continue

        print(f"\n{'=' * 70}")
        print(f"LEVEL {lvl.split('_')[1]} EXERCISES")
        print("=" * 70)

        level_results = []

        for ex in EXERCISES[lvl]:
            print(f"\n--- Exercise {ex['id']}: {ex['title']} ---")
            print(f"Sending exercise to AI...")

            response = send_to_ai(ex["prompt"], model)

            print(f"\nAI Response:")
            print("-" * 40)
            print(response[:1500] + "..." if len(response) > 1500 else response)
            print("-" * 40)

            # Evaluate
            evaluation = evaluate_response(response, ex)
            level_results.append({
                "exercise": ex["id"],
                "title": ex["title"],
                "evaluation": evaluation,
                "response": response
            })

            print(f"\nEvaluation: {evaluation['score']}/{evaluation['max_score']} ({evaluation['percentage']:.0f}%)")
            print(f"Found: {evaluation['found']}")
            print(f"Missing: {evaluation['missing']}")
            print(f"Passed: {'✓' if evaluation['passed'] else '✗'}")

            # If failed, provide hint
            if not evaluation['passed']:
                hint = f"\nHint: Look for these concepts: {', '.join(evaluation['missing'][:3])}"
                print(hint)
                # Optionally send hint to AI for retry

            time.sleep(2)  # Rate limiting

        results[lvl] = level_results

        # Level summary
        passed = sum(1 for r in level_results if r["evaluation"]["passed"])
        total = len(level_results)
        print(f"\n{lvl.upper()} SUMMARY: {passed}/{total} exercises passed")

    # Final summary
    print("\n" + "=" * 70)
    print("TRAINING SESSION COMPLETE")
    print("=" * 70)

    for lvl, res in results.items():
        passed = sum(1 for r in res if r["evaluation"]["passed"])
        total = len(res)
        status = "PASSED" if passed >= total * 0.75 else "NEEDS REVIEW"
        print(f"{lvl}: {passed}/{total} ({status})")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"/home/solo/LA/training_results_{timestamp}.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: training_results_{timestamp}.json")

    return results


def quick_test(model="mistral-large-3:675b-cloud"):
    """Quick test with single exercise."""
    print("Quick test - Exercise 1.1")
    ex = EXERCISES["level_1"][0]
    response = send_to_ai(ex["prompt"], model)
    print(f"Response:\n{response}")
    eval_result = evaluate_response(response, ex)
    print(f"\nEvaluation: {eval_result}")
    return eval_result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            quick_test()
        elif sys.argv[1] == "full":
            run_training_session("all")
        elif sys.argv[1].isdigit():
            run_training_session(sys.argv[1])
        else:
            print("Usage: python run_ai_training.py [quick|full|1|2|3]")
    else:
        # Default: run quick test
        print("Run with: python run_ai_training.py [quick|full|1|2|3]")
        print("\nAvailable models:")
        print("  - mistral-large-3:675b-cloud")
        print("  - qwen3-vl:8b")
        print("  - kimi-k2:1t-cloud")
        print("  - gpt-oss:120b-cloud")
