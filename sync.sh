#!/bin/bash
# Auto-sync script for multi-Claude coordination
# Run this every hour to stay synced with other boxes

echo "======================================================================="
echo "  MULTI-CLAUDE SYNC CHECK - $(date)"
echo "======================================================================="

# Navigate to repo
cd "$(dirname "$0")"

# Fetch updates from GitHub
echo ""
echo "📡 Fetching updates from GitHub..."
git fetch origin 2>&1 | grep -v "^From"

# Check if we're behind
LOCAL=$(git rev-parse @ 2>/dev/null)
REMOTE=$(git rev-parse @{u} 2>/dev/null)
BASE=$(git merge-base @ @{u} 2>/dev/null)

if [ -z "$LOCAL" ] || [ -z "$REMOTE" ]; then
    echo "⚠️  Git repository not properly configured!"
    echo "   Run: git checkout -b local-work origin/local-work"
    exit 1
fi

echo ""
if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ You're up to date with origin/local-work"
elif [ "$LOCAL" = "$BASE" ]; then
    echo "⚠️  NEW UPDATES FROM OTHER BOXES!"
    echo ""
    echo "Recent commits you don't have:"
    echo "----------------------------------------"
    git log --oneline --decorate HEAD..@{u} | head -10
    echo "----------------------------------------"
    echo ""
    echo "🔄 Run this to update:"
    echo "   git pull origin local-work"
    echo ""
elif [ "$REMOTE" = "$BASE" ]; then
    echo "⬆️  You have unpushed commits"
    echo ""
    echo "Your commits not on GitHub:"
    echo "----------------------------------------"
    git log --oneline --decorate @{u}..HEAD
    echo "----------------------------------------"
    echo ""
    echo "📤 Run this to share:"
    echo "   git push origin local-work"
    echo ""
else
    echo "🔀 Your branch has diverged from origin!"
    echo "   You AND others have new commits"
    echo ""
    echo "Run this to merge:"
    echo "   git pull origin local-work"
fi

# Check for uncommitted changes
echo ""
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "💾 You have uncommitted changes:"
    echo "----------------------------------------"
    git status --short
    echo "----------------------------------------"
    echo ""
    echo "Save your work:"
    echo "   git add ."
    echo "   git commit -m 'BOX-NAME: Brief description'"
    echo "   git push origin local-work"
else
    echo "✅ No uncommitted changes"
fi

# Check for urgent updates
echo ""
URGENT_FILES=$(ls -t URGENT_UPDATE_*.md 2>/dev/null | head -3)
if [ -n "$URGENT_FILES" ]; then
    echo "🚨 URGENT UPDATES FOUND!"
    echo "----------------------------------------"
    for file in $URGENT_FILES; do
        echo "📄 $file"
        head -5 "$file" | grep -E "^(#|\\*\\*)" || head -5 "$file"
        echo ""
    done
    echo "Read full updates:"
    for file in $URGENT_FILES; do
        echo "   cat $file"
    done
else
    echo "ℹ️  No urgent updates"
fi

# Show recent activity summary
echo ""
echo "📊 Recent Activity (last 24 hours):"
echo "----------------------------------------"
git log --oneline --all --since="24 hours ago" | head -10
if [ $(git log --oneline --all --since="24 hours ago" | wc -l) -eq 0 ]; then
    echo "   (No activity in last 24 hours)"
fi
echo "----------------------------------------"

# Show current branch info
echo ""
echo "📍 Current Status:"
echo "   Branch: $(git branch --show-current)"
echo "   Tracking: $(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo 'Not set')"
echo "   Last commit: $(git log -1 --pretty=format:'%h - %s (%cr)' 2>/dev/null)"

echo ""
echo "======================================================================="
echo "  Sync check complete. Run './sync.sh' again anytime to check status."
echo "======================================================================="
