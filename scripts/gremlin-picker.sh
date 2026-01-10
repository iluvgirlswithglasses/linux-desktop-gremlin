#!/bin/bash
# Universal Gremlin Picker using PySide6

# move to project root directory
SCRIPT_DIR="$(dirname $(realpath "$0"))"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# ensure uv/local bins can be found
export PATH=$PATH:$HOME/.local/bin

# Detect Python environment
PYTHON=""

# 1. Try venv if it exists
if [ -d "venv" ]; then
    PYTHON="./venv/bin/python"
# 2. Try uv if available
elif command -v uv >/dev/null 2>&1; then
    PYTHON="uv run python"
# 3. Fallback to system python
else
    PYTHON="python3"
fi

# Ensure Wayland compatibility for Qt
if [ "${XDG_SESSION_TYPE}" = "wayland" ]; then
    export QT_QPA_PLATFORM=xcb
fi

# Run the picker and capture the selected gremlin name
PICK=$($PYTHON -m src.picker 2>/dev/null)

# If a selection was made, run the gremlin
if [ -n "$PICK" ]; then
    ./run.sh "$PICK"
fi