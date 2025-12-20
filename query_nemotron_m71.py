#!/usr/bin/env python3
"""
Query Nemotron for deep analysis of m-sequence generation algorithm.
"""

import json
import requests
import sys

# Load the data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

# Prepare the prompt with all known patterns
prompt = """You are a mathematical cryptanalyst. Your task is to find the EXACT algorithm that generates the m-sequence for the Bitcoin puzzle.

## VERIFIED FORMULA (67/67 matches)
k[n] = 2*k[n-1] + 2^n - m[n] * k[d[n]]

Where:
- m[n] = m_seq[n-2] (index shift)
- d[n] = d_seq[n-2] (index shift)
- d[n] is always chosen to MINIMIZE m[n]

## M-SEQUENCE VALUES (n=2 to n=70)
n=2: m=1, d=2
n=3: m=1, d=3
n=4: m=22, d=1   (22 = π numerator convergent index 1, from 22/7)
n=5: m=9, d=2    (9 = ln2 numerator convergent index 4)
n=6: m=19, d=2   (19 = e numerator convergent index 4)
n=7: m=50, d=2   (50 = 5 × 10 = φ_num[3] × ln2_den[3])
n=8: m=23, d=4   (23 = 1 + 22 = π_den[0] + π_num[1])
n=9: m=493, d=1  (493 = 17 × 29 = √2_num[3] × √2_den[4])
n=10: m=19, d=7  (19 = e_num[4], same as m[6])
n=11: m=1921, d=1 (1921 = 17 × 113 = √2_num[3] × π_den[3])
n=12: m=1241, d=2 (1241 = 1649 - 408 = ln2_den[9] - √2_den[7])

Recent values (n=60-70):
n=60: m=4767950548678049, d=8
n=61: m=1050046055678010578, d=2
n=62: m=1184962853718958602, d=2
n=63: m=8046887172345950164, d=1
n=64: m=6211178871726751508, d=2
n=65: m=1996402169071970173, d=5
n=66: m=395435327538483377, d=8
n=67: m=35869814695994276026, d=2  (NOTE: 35869814695994276026 = 2 × 17 × ...)
n=68: m=340563526170809298635, d=1
n=69: m=34896088136426753598, d=5
n=70: m=268234543517713141517, d=2

## KNOWN CONSTRUCTION TYPES

Type 1 - DIRECT: m[n] = convergent numerator or denominator
Type 2 - PRODUCT: m[n] = conv_A × conv_B (same index)
Type 3 - SUM: m[n] = conv_A + conv_B
Type 4 - DIFFERENCE: m[n] = conv_A - conv_B
Type 5 - PRIME-INDEX (17-network): m[n] = 17 × p[n + m[earlier]]
Type 6 - RECURSIVE: m[n] = m[earlier] × (convergent product)
Type 7 - DIVISIBILITY: m[n] divisible by earlier m values

## SELECTION RULES (PARTIAL)

For n % 3 = 0: √2 constant
For n % 3 = 1: π constant
For n % 3 = 2: √2 or ln2 constant

For d = 1: PRODUCT or PRIME-INDEX operation
For d = 2: Usually involves ln2 or e
For d = 4: SUM operation

## CONVERGENT VALUES (first 15 of each)

π numerators: [3, 22, 333, 355, 103993, 104348, 208341, 312689, 833719, 1146408, 4272943, 5419351, 80143857, 165707065, 245850922]
π denominators: [1, 7, 106, 113, 33102, 33215, 66317, 99532, 265381, 364913, 1360120, 1725033, 25510582, 52746197, 78256779]

e numerators: [2, 3, 8, 11, 19, 87, 106, 193, 1264, 1457, 2721, 23225, 25946, 49171, 517656]
e denominators: [1, 1, 3, 4, 7, 32, 39, 71, 465, 536, 1001, 8544, 9545, 18089, 190435]

√2 numerators: [1, 3, 7, 17, 41, 99, 239, 577, 1393, 3363, 8119, 19601, 47321, 114243, 275807]
√2 denominators: [1, 2, 5, 12, 29, 70, 169, 408, 985, 2378, 5741, 13860, 33461, 80782, 195025]

φ numerators: [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
φ denominators: [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]

ln2 numerators: [0, 1, 2, 9, 11, 75, 236, 311, 547, 1641, 2188, 3829, 5470, 9299, 32966]
ln2 denominators: [1, 1, 3, 13, 16, 109, 341, 450, 791, 2373, 3164, 5537, 8701, 13441, 47684]

## YOUR TASK

Find the EXACT algorithm that determines m[71]:
1. What is the operation type for n=71? (n % 3 = 2)
2. Which constants are used?
3. Which convergent indices?
4. What is m[71]?

Show your reasoning step by step. The answer must be an exact integer that, when used in the formula with the correct d[71], produces k[71] that matches the Bitcoin address 1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU.

Think deeply. This is a mathematical puzzle, not random numbers.
"""

def query_nemotron(prompt, timeout=300):
    """Query Nemotron via Ollama API."""
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "nemotron-3-nano:30b-cloud",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,  # Low temperature for precise reasoning
            "num_predict": 4000,
            "top_p": 0.9
        }
    }

    print("Querying Nemotron for m[71] analysis...")
    print("=" * 70)

    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        return result.get('response', 'No response')
    except requests.exceptions.Timeout:
        return "ERROR: Query timed out"
    except Exception as e:
        return f"ERROR: {str(e)}"

if __name__ == "__main__":
    response = query_nemotron(prompt)
    print(response)
    print("\n" + "=" * 70)

    # Save response
    with open('nemotron_m71_analysis.txt', 'w') as f:
        f.write(response)
    print("Response saved to nemotron_m71_analysis.txt")
