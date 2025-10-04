#!/bin/bash

echo "Stopping NetSentry services..."

# Check if .pids file exists
if [ -f .pids ]; then
    while IFS= read -r pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "Stopping process $pid..."
            kill $pid 2>/dev/null
            # Kill child processes too
            pkill -P $pid 2>/dev/null
        fi
    done < .pids
    rm -f .pids
fi

# Also try to kill by port
echo "Cleaning up processes on ports 8000 and 3000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✓ Services stopped"

