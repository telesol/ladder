#!/usr/bin/env python3
"""
Query Nemotron with the proper context to derive m[71] construction.
"""

import json
import requests

# Read the context file
with open('NEMOTRON_CONTEXT.md', 'r') as f:
    context = f.read()

# Focused query on m-value construction
prompt = f"""You are a mathematical analyst. NO PREDICTIONS - ONLY DERIVATIONS.

{context}

---

## SPECIFIC TASK

Analyze the m-value construction for n ≡ 2 (mod 3) cases.

### Data for n ≡ 2 (mod 3):
- n=50: m=1,332,997,220,739,910, d=1
- n=53: m=10,676,506,562,464,268, d=1
- n=56: m=87,929,632,728,990,281, d=1
- n=59: m=451,343,703,997,841,395, d=1
- n=62: m=1,184,962,853,718,958,602, d=2
- n=65: m=1,996,402,169,071,970,173, d=5
- n=68: m=340,563,526,170,809,298,635, d=1

### Question 1: Factor Analysis
For each m-value above, find its prime factorization or connection to convergents.
Check for factors: 17, 19, 22, 3, 7, 11, 13.

### Question 2: Pattern in d-sequence
For n ≡ 2 (mod 3): d = [1, 1, 1, 1, 2, 5, 1, ...]
What determines when d changes from 1 to 2 or 5?

### Question 3: Predict d[71]
Based on the pattern [1, 1, 1, 1, 2, 5, 1], what is d[71]?
Show your reasoning.

SHOW ALL WORK. NO GUESSING.
"""

def query_nemotron(prompt, timeout=180):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "nemotron-3-nano:30b-cloud",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 2000,
            "top_p": 0.9
        }
    }

    print("Querying Nemotron for m[71] construction analysis...")
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
    with open('nemotron_m71_construction.txt', 'w') as f:
        f.write(response)
    print("Response saved to nemotron_m71_construction.txt")
