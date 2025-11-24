#!/bin/bash

LINK_PATH="$HOME/.local/bin/gremlin-picker"
INSTALL_PATH="$HOME/.config/linux-desktop-gremlin"
DESKTOP_FILE="$HOME/.local/share/applications/gremlin_picker.desktop"

if [ -L "$LINK_PATH" ]; then
    rm "$LINK_PATH"
    echo "Removed symlink: $LINK_PATH"
fi

if [ -d "$INSTALL_PATH" ]; then
    rm -rf "$INSTALL_PATH"
    echo "Removed directory: $INSTALL_PATH"
fi

if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo "Removed desktop entry: $DESKTOP_FILE"
fi

