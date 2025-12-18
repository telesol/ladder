#!/usr/bin/env python3
"""
B-Solver ORACLE MODE
====================
Like C-Solver's Oracle Mode, but for phi4-reasoning:14b.
Deep reasoning with streaming output, no timeout.

Usage:
    python oracle_query.py "Your deep question here"
    python oracle_query.py  # Uses default puzzle analysis question
"""
import sys
import json
import requests
from datetime import datetime

MODEL = "phi4-reasoning:14b"

# All 70 known keys for context
KNOWN_KEYS = """
k1=1, k2=3, k3=7, k4=8, k5=21, k6=49, k7=76, k8=224, k9=467, k10=514
k11=1155, k12=2683, k13=5765, k14=10544, k15=26867, k16=51510
k17=95823, k18=198669, k19=357535, k20=863317, k21=1811764, k22=3007503
k23=5598802, k24=14428676, k25=33185509, k26=54538862, k27=111949941
k28=227634408, k29=400708894, k30=1033162084, k31=2102388551, k32=3093472814
k33=7137437912, k34=14133072157, k35=20112871792, k36=42387769980
k37=100251560595, k38=146971536592, k39=323724968937, k40=1003651412950
k41=1458252205147, k42=2895374552463, k43=7409811047825, k44=15404761757071
k45=19996463086597, k46=51408670348612, k47=119666659114170, k48=191206974700443
k49=409118905032525, k50=611140496167764, k51=2058769515153876, k52=4216495639600700
k53=6763683971478124, k54=9974455244496707, k55=30045390491869460
k56=44218742292676575, k57=138245758910846492, k58=199976667976342049
k59=525070384258266191, k60=1135041350219496382, k61=1425787542618654982
k62=3908372542507822062, k63=8993229949524469768, k64=17799667357578236628
k65=30568377312064202855, k66=46346217550346335726, k67=97842531449157303506
k68=143992573827376775550, k69=297274491920375905804, k70=970436974005023690481

Bridge keys (future puzzles, already known):
k75=22538323240989823823367
k80=1105520030589234487939456
k85=21090315766411506144426920
k90=868012190417726402719548863
"""

VERIFIED_PATTERNS = """
Verified mathematical relationships:
- k5 = k2 x k3 = 3 x 7 = 21
- k6 = k3^2 = 7^2 = 49
- k8 = k4 x k3 x 4 = 8 x 7 x 4 = 224
- k9 = 2 x k8 + 19 = 2 x 224 + 19 = 467
- k11 = 3 x 5 x 7 x 11 = 1155 (contains the puzzle number 11!)
- k13 = k7^2 - 11 = 76^2 - 11 = 5765

Position anomalies (position% = where key is in its bit range):
- k2, k3: 100% (at maximum)
- k4: 0% (at minimum!)
- k10: 0.39% (near minimum)
- k69: 0.72% (near minimum - this is why it was "solved fast")
- k70: 64.4% (mid-range)

Divisibility patterns:
- k4 % 4 = 0, k8 % 8 = 0, k11 % 11 = 0
- k69 % 11 = 0 (divisible by 11, not 69)
"""

DEFAULT_QUESTION = """You are B-Solver, an advanced mathematical reasoning AI using phi4-reasoning.

CONTEXT:
""" + KNOWN_KEYS + """

KNOWN PATTERNS:
""" + VERIFIED_PATTERNS + """

YOUR SPECIALIZATION: Deep reasoning, anomaly detection, and pattern analysis.

YOUR TASK:
Think deeply and step-by-step. Take as much time as you need.
Use your <think> blocks to explore all possibilities.

The puzzle creator generated these keys in 2015. We have 70 solved keys.
k69 was found quickly because it was near the minimum of its range (0.72%).

Question: Analyze the ANOMALIES in this data:

1. Delta anomalies:
   - k3->k4: delta=1, normalized=0.125 (VERY LOW)
   - k9->k10: delta=47, normalized=0.092 (LOWEST)
   - k56->k57: normalized=1.305 (HIGHEST)

2. Position anomalies: Why are some keys at extremes (0% or 100%)?

3. The number 13: Why does 13 appear in A-multipliers for lanes 1,5,13 but NOT lane 9?

4. Regime change: Mathematical relationships exist for k1-k8, then disappear. Why?

Think like a cryptanalyst. Find the hidden pattern. Show all reasoning.
What does this tell us about WHERE to search for the next key?
"""


def oracle_stream(question: str):
    """Stream phi4-reasoning's response - no timeout, see thinking in real-time"""
    print("=" * 70)
    print("B-SOLVER ORACLE MODE - phi4-reasoning:14b Deep Reasoning")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {MODEL}")
    print("No timeout. Streaming output. Let it think...")
    print("=" * 70)
    print()

    full_response = ""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": question,
                "stream": True
            },
            stream=True,
            timeout=None  # No timeout - let it think
        )

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    token = data.get("response", "")
                    full_response += token
                    print(token, end="", flush=True)

                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue

    except KeyboardInterrupt:
        print("\n\n[Interrupted by user]")
    except Exception as e:
        print(f"\n\nError: {e}")

    print("\n")
    print("=" * 70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Save the full response
    output = {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "question": question[:500] + "..." if len(question) > 500 else question,
        "response": full_response,
        "response_length": len(full_response)
    }

    with open("/home/solo/LA/b-solver/oracle_response.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Response saved to: b-solver/oracle_response.json")
    print(f"Response length: {len(full_response)} characters")

    return full_response


if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = DEFAULT_QUESTION

    oracle_stream(question)
