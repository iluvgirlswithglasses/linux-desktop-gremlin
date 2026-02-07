#!/bin/bash
# Download gremlin assets from command line

# ---- move to project root directory --------------------------------
SCRIPT_DIR="$(dirname $(realpath "$0"))"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# ---- check if the script is called with 1 argument -----------------
if [ "$#" -ne 1 ]; then
    SCRIPT_NAME="$(basename "$0")"
    echo "Usage:    $SCRIPT_NAME <gremlin-name>"
    echo "Example:  $SCRIPT_NAME hikari"
    echo ""
    echo "You can check for available gremlin names in:"
    echo "$PROJECT_DIR/upstream-assets.json"
    exit 1
fi

# ---- detect Python environment -------------------------------------
export PATH=$PATH:$HOME/.local/bin
PYTHON=""

if [ -d "venv" ]; then
    PYTHON="./venv/bin/python"
elif command -v uv >/dev/null 2>&1; then
    PYTHON="uv run python"
else
    PYTHON="python3"
fi

# ---- call gremlin downloader ---------------------------------------
$PYTHON -m src.asset_downloader "$@"
