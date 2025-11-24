#!/usr/bin/env bash
# Launcher for Linux Desktop Gremlins
USE_UV=1
USE_VENV=0

run_detached() {
    # Run the command in background (&), silence output, and disown the PID
    "$@" >/dev/null 2>&1 &
    disown $!
    exit 0
}

# Find python and pip
PYTHON=$(command -v python3 || command -v python) || { echo "Python not found"; exit 1; }
PIP=$(command -v pip3 || command -v pip || command -v uv) || { echo "pip/uv not found"; exit 1; }

# Parse args
while [ $# -gt 0 ]; do
    case $1 in
        --no-uv) USE_UV=0 ;;
        --system) USE_VENV=0 ;;
        --venv) USE_VENV=1 ;;
        --help|-h) cat <<EOF && exit 0
Usage: $0 [OPTIONS] [CHARACTER]
  --no-uv   Use Python directly
  --system  Use system Python
  --venv    Force venv
EOF
        ;;
        *) break ;;
    esac
    shift
done

cd "$(dirname "$0")"

# Wayland -> XCB
[ "${XDG_SESSION_TYPE}" = "wayland" ] && export QT_QPA_PLATFORM=xcb

# Auto: try uv first
if [ $USE_UV -eq 1 ] && command -v uv >/dev/null 2>&1; then
    run_detached uv run python -m src.launcher "$@"
fi

# Explicit --system
if [ $USE_VENV -eq 0 ]; then
    run_detached $PYTHON -m src.launcher "$@"
fi

# Explicit --venv
if [ $USE_VENV -eq 1 ]; then
    [ -d venv ] || $PYTHON -m venv venv
    . venv/bin/activate
    PYTHON=$(command -v python)  # Update PYTHON to venv python
    $PYTHON -m pip install pyside6
    run_detached $PYTHON -m src.launcher "$@"
fi

# Fallback: venv if PySide6 missing
if ! $PYTHON -c "import PySide6" 2>/dev/null; then
    [ -d venv ] || $PYTHON -m venv venv
    . venv/bin/activate
    PYTHON=$(command -v python)  # Update PYTHON to venv python
    $PYTHON -m pip install -q pyside6
fi

run_detached $PYTHON -m src.launcher "$@"
