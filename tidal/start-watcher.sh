#!/bin/bash
# Start the pattern file watcher
# Edit patterns in ./patterns/ with any editor

cd "$(dirname "$0")/.."

echo "Starting pattern watcher..."
echo "Edit files in ./patterns/ - changes auto-send to SuperDirt"
echo ""

./venv/bin/python3 tidal/pattern_watcher.py --dir ./patterns "$@"
