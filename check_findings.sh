#!/bin/bash
# Quick findings checker

echo "🎯 LATEST FINDINGS ACROSS ALL SOURCES"
echo "======================================"
echo ""

echo "📊 FINDINGS DASHBOARD:"
head -50 FINDINGS_DASHBOARD.md 2>/dev/null || echo "  (not created yet)"
echo ""

echo "📁 DAILY SUMMARIES:"
ls -lt findings/*/DAILY_SUMMARY.md 2>/dev/null | head -5 || echo "  (none found)"
echo ""

echo "🔬 LATEST GIT COMMITS:"
git log --all --oneline --graph -10
echo ""

echo "🤖 ACTIVE AI ANALYSES:"
ps aux | grep -E "(ollama|python.*cluster)" | grep -v grep | head -5
echo ""

echo "📝 RECENT EXPLORATIONS:"
ls -lt exploration_exam_*.json 2>/dev/null | head -3
echo ""

echo "✅ TO VIEW FULL DASHBOARD:"
echo "   cat FINDINGS_DASHBOARD.md"
