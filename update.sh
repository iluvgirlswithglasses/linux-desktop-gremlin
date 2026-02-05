#!/bin/bash
# Run this script to update your existing installation of Linux Desktop Gremlin

# ---- move to project root directory --------------------------------
SCRIPT_DIR="$(dirname $(realpath "$0"))"
cd "$SCRIPT_DIR"

# ---- use `git pull` if git repo exists -----------------------------
if [ -d ".git" ]; then
    git pull
    exit 0
fi

# ---- otherwise, clone upstream & replace sources -------------------
TEMP_DIR="$(mktemp -d)"
git clone --depth 1 https://github.com/iluvgirlswithglasses/linux-desktop-gremlin $TEMP_DIR
mv $TEMP_DIR/{*,.[!.]*} "$SCRIPT_DIR"
rm -rf $TEMP_DIR
echo "Update complete."
