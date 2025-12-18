#!/bin/bash
# Ladder Agents Startup Script

cd "$(dirname "$0")"

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Activate venv
source .venv/bin/activate

# Check API keys
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "WARNING: ANTHROPIC_API_KEY not set in .env"
fi

echo "Starting Ladder Agents..."
echo ""

# Run command or default to status
if [ "$1" == "daemon" ]; then
    python3 main.py daemon
elif [ "$1" == "goal" ]; then
    python3 main.py goal -g "$2"
elif [ "$1" == "rag" ]; then
    python3 main.py rag-index
else
    python3 main.py status
fi
