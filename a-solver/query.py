#!/usr/bin/env python3
"""
A-Solver Query Interface
Bitcoin Puzzle Mathematics AI - qwen3-vl:8b

Usage:
    python query.py "Your question here"
    python query.py --interactive
"""

import requests
import json
import sys
import time
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3-vl:8b"
DEFAULT_TIMEOUT = 300

# System context for puzzle mathematics
SYSTEM_CONTEXT = """You are an expert in Bitcoin puzzle mathematics. You understand:

1. Key ranges: k_N ∈ [2^(N-1), 2^N - 1]
2. Known relationships: k_5 = k_2 × k_3, k_6 = k_3², k_8 = k_4 × k_3 × 4
3. Linear recurrence: k_n = a×k_{n-1} + 19×k_{n-2} (works for early keys)
4. Normalized delta: (k_{n+1} - k_n) / 2^n, range [0.09, 1.31], mean 0.76
5. Affine model: y = A×x + C (mod 256), where A varies by lane
6. A multipliers: Lane 1=91, Lane 5=169, Lane 9=32 (anomaly), Lane 13=182

Key facts:
- Lanes 1, 5, 13 have A divisible by 13; Lane 9 (A=32) breaks this pattern
- The affine model is circular: C requires knowing y (the answer)
- Delta constraints don't reduce search space beyond bit range
- Early keys have exact relationships; larger keys appear cryptographically random

Be precise with calculations. Show your work."""


def ask(prompt: str, timeout: int = DEFAULT_TIMEOUT, verbose: bool = False) -> str:
    """Send a query to the A-Solver model."""
    full_prompt = f"{SYSTEM_CONTEXT}\n\nQuestion: {prompt}\n\nAnswer:"

    try:
        if verbose:
            print(f"Querying {MODEL}...")
            t0 = time.time()

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=timeout
        )

        if verbose:
            print(f"Response time: {time.time() - t0:.1f}s")

        if response.status_code == 200:
            return response.json().get("response", "No response")
        else:
            return f"Error: HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        return "Error: Request timed out"
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Is it running?"
    except Exception as e:
        return f"Error: {str(e)}"


def interactive_mode():
    """Run interactive query session."""
    print("=" * 60)
    print("A-Solver Interactive Mode")
    print("Bitcoin Puzzle Mathematics AI")
    print("=" * 60)
    print("Type 'quit' or 'exit' to end session")
    print("Type 'help' for example queries")
    print()

    examples = [
        "What is the valid range for puzzle 71?",
        "Factorize k_11 = 1155",
        "Is k_7 = k_2 × k_5? Given k_2=3, k_5=21, k_7=76",
        "Calculate normalized delta for k_9=467 to k_10=514",
        "Why is Lane 9's A multiplier anomalous?",
        "Does the delta constraint help reduce search for puzzle 71?",
    ]

    while True:
        try:
            query = input("\n> ").strip()

            if not query:
                continue
            elif query.lower() in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break
            elif query.lower() == 'help':
                print("\nExample queries:")
                for i, ex in enumerate(examples, 1):
                    print(f"  {i}. {ex}")
                continue

            print("\nThinking...")
            response = ask(query, verbose=True)
            print("\n" + "-" * 40)
            print(response)
            print("-" * 40)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            break


def main():
    if len(sys.argv) < 2:
        print("Usage: python query.py \"Your question\"")
        print("       python query.py --interactive")
        sys.exit(1)

    if sys.argv[1] in ('--interactive', '-i'):
        interactive_mode()
    else:
        query = " ".join(sys.argv[1:])
        response = ask(query, verbose=True)
        print("\n" + response)


if __name__ == "__main__":
    main()
