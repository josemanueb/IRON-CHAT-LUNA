#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -d "$DIR/venv" ]; then
    "$DIR/venv/bin/python3" "$DIR/main.py"
else
    python3 "$DIR/main.py"
fi
