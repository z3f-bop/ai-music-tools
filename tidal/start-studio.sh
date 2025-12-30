#!/bin/bash
# Zeph's Music Studio Startup Script
# Starts SuperCollider with SuperDirt and MIDI routing

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SC_APP="/Applications/SuperCollider.app/Contents/MacOS/sclang"
STARTUP_FILE="$SCRIPT_DIR/superdirt_startup.scd"

echo "=================================="
echo "  Zeph's Music Studio"
echo "=================================="
echo ""
echo "Starting SuperCollider with SuperDirt..."
echo "Model D will be available as: \\modeld"
echo "MIDI Channel: 11 (midichan 10)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run SuperCollider with our startup file
$SC_APP "$STARTUP_FILE"
