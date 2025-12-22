#!/usr/bin/env python3
"""Synthesize results from LLM analysis tasks."""

import os
import re

print("="*80)
print("LLM RESULTS SYNTHESIS")
print("="*80)
print()

# Check if all tasks completed
results_dir = "llm_tasks/results"
if not os.path.exists(results_dir):
    print("ERROR: Results directory not found!")
    print("Run ./run_llm_analysis.sh first")
    exit(1)

tasks = {
    1: "Divisibility Pattern Analysis",
    2: "M-Value Magnitude Pattern",
    3: "D-Selection Meta-Pattern",
    4: "Number Theory Deep Analysis"
}

# Check completion
print("Task Completion Status:")
print("-" * 60)
results = {}
for task_num, task_name in tasks.items():
    result_file = f"{results_dir}/task{task_num}_*.txt"
    import glob
    files = glob.glob(result_file.replace("*", "*"))

    if files:
        with open(files[0], 'r') as f:
            content = f.read()
        results[task_num] = content
        lines = len(content.split('\n'))
        size = len(content)
        print(f"  Task {task_num}: ✓ Complete ({lines} lines, {size} bytes)")
        print(f"           {task_name}")
    else:
        print(f"  Task {task_num}: ❌ Missing")
        print(f"           {task_name}")

print()

if len(results) < 4:
    print("⚠️  Not all tasks complete. Wait for LLM to finish.")
    print()
    print("Current results available:")
    for task_num in results:
        print(f"  - Task {task_num}: {tasks[task_num]}")
    print()
    print("To monitor progress: ./monitor_llm_progress.sh")
    exit(0)

print("="*80)
print("ALL TASKS COMPLETE - ANALYZING FINDINGS")
print("="*80)
print()

# Extract key findings from each task
findings = {}

for task_num, content in results.items():
    print(f"\n{'='*80}")
    print(f"TASK {task_num}: {tasks[task_num]}")
    print("="*80)

    # Show first 2000 characters of response
    preview = content[:2000]
    if len(content) > 2000:
        preview += "\n\n[... truncated, see full file for details ...]"

    print(preview)
    print()

    findings[task_num] = content

print("="*80)
print("SYNTHESIS SUMMARY")
print("="*80)
print()

# Look for key patterns across all findings
print("Searching for actionable predictions...")
print()

# Search for formulas
formulas = []
for task_num, content in findings.items():
    # Look for mathematical formulas (lines with = and mathematical symbols)
    lines = content.split('\n')
    for line in lines:
        if '=' in line and any(sym in line for sym in ['2^', '*', '/', 'mod', '≡', '≈']):
            if len(line) < 200:  # Ignore very long lines
                formulas.append((task_num, line.strip()))

if formulas:
    print("Mathematical Formulas Found:")
    for task_num, formula in formulas[:10]:  # Show first 10
        print(f"  [Task {task_num}] {formula}")
    print()

# Search for predictions
predictions = []
for task_num, content in findings.items():
    lines = content.split('\n')
    for line in lines:
        if any(word in line.lower() for word in ['predict', 'expect', 'will be', 'should be', 'k95', 'k100']):
            if len(line) < 200:
                predictions.append((task_num, line.strip()))

if predictions:
    print("Predictions Found:")
    for task_num, prediction in predictions[:10]:
        print(f"  [Task {task_num}] {prediction}")
    print()

# Save synthesis report
report_file = "llm_tasks/SYNTHESIS_REPORT.md"
with open(report_file, 'w') as f:
    f.write("# LLM Analysis Synthesis Report\n")
    f.write("**Date**: 2025-12-20\n")
    f.write("**Model**: gpt-oss:120b-cloud\n")
    f.write("\n---\n\n")

    for task_num, task_name in tasks.items():
        f.write(f"## Task {task_num}: {task_name}\n\n")
        if task_num in findings:
            f.write("```\n")
            f.write(findings[task_num])
            f.write("\n```\n\n")
        else:
            f.write("*No results*\n\n")

    f.write("\n---\n\n")
    f.write("## Formulas Found\n\n")
    for task_num, formula in formulas:
        f.write(f"- [Task {task_num}] {formula}\n")

    f.write("\n## Predictions Found\n\n")
    for task_num, prediction in predictions:
        f.write(f"- [Task {task_num}] {prediction}\n")

print(f"Full report saved to: {report_file}")
print()

print("="*80)
print("NEXT STEPS")
print("="*80)
print()
print("1. Review synthesis report:")
print(f"   cat {report_file}")
print()
print("2. Test any predictions on bridges:")
print("   python3 test_llm_predictions.py")
print()
print("3. Push findings to GitHub:")
print("   git add llm_tasks/ && git commit -m 'LLM analysis results' && git push")
print()
