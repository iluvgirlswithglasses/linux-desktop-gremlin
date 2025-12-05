#!/bin/bash

# Clone the repo into ~/.config
echo "Cloning repo into ~/.config/linux-desktop-gremlin"
git clone https://github.com/iluvgirlswithglasses/linux-desktop-gremlin ~/.config/linux-desktop-gremlin
echo "Clone completed!"
cd ~/.config/linux-desktop-gremlin

# Install uv and sync
if command -v uv >/dev/null 2>&1; then
    echo "uv is installed"
else
    echo "uv is not installed, installing..."
    echo "Executing: curl -LsSf https://astral.sh/uv/install.sh | sh"
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "Running 'uv sync' to install required packages..."
uv sync

# Variables
INSTALL_PATH="$HOME/.config/linux-desktop-gremlin"
BIN_PATH="$HOME/.local/bin"
LINK_PATH="$BIN_PATH/gremlin-picker"
DESKTOP_FILE="$HOME/.local/share/applications/gremlin_picker.desktop"
ICON_PATH="$INSTALL_PATH/icon.png" # optional icon

echo "→ Installing Linux Desktop Gremlin..."
mkdir -p "$INSTALL_PATH" "$BIN_PATH" "$(dirname "$DESKTOP_FILE")"
ln -sf "$INSTALL_PATH/scripts/gremlin-picker.sh" "$LINK_PATH"
chmod +x "$LINK_PATH"

cat >"$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=Gremlin Picker
Comment=Pick your favorite gremlin
Exec=$LINK_PATH
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Utility;
EOF

chmod 644 "$DESKTOP_FILE"
echo "Installed successfully! :3"

