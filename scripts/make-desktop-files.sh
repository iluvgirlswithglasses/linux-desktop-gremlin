#!/bin/bash

# ========================================================================================
# Installation Variables
# ========================================================================================
INSTALL_PATH="$HOME/.config/linux-desktop-gremlin"
ICON_PATH="$INSTALL_PATH/icon.png"
BIN_PATH="$HOME/.local/bin"

PICKER_LINK_PATH="$BIN_PATH/gremlin-picker"
PICKER_DESKTOP_FILE="$HOME/.local/share/applications/gremlin_picker.desktop"

DOWNLOADER_LINK_PATH="$BIN_PATH/gremlin-downloader"
DOWNLOADER_DESKTOP_FILE="$HOME/.local/share/applications/gremlin_downloader.desktop"


# ========================================================================================
# Remove existing files (if any)
# ========================================================================================
rm "$PICKER_LINK_PATH" 2> /dev/null
rm "$PICKER_DESKTOP_FILE" 2> /dev/null
rm "$DOWNLOADER_LINK_PATH" 2> /dev/null
rm "$DOWNLOADER_DESKTOP_FILE" 2> /dev/null


# ========================================================================================
# Install Gremlin Picker
# ========================================================================================
echo "→ Installing Linux Desktop Gremlin..."
mkdir -p "$INSTALL_PATH" "$BIN_PATH" "$(dirname "$PICKER_DESKTOP_FILE")"
ln -sf "$INSTALL_PATH/scripts/gremlin-picker.sh" "$PICKER_LINK_PATH"
chmod +x "$PICKER_LINK_PATH"

cat >"$PICKER_DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=Gremlin Picker
Comment=Pick your favorite gremlin
Exec=$PICKER_LINK_PATH
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Utility;
EOF

chmod 644 "$PICKER_DESKTOP_FILE"


# ========================================================================================
# Install Gremlin Downloader
# ========================================================================================
echo "→ Installing Gremlin Downloader..."
mkdir -p "$(dirname "$DOWNLOADER_DESKTOP_FILE")"
ln -sf "$INSTALL_PATH/scripts/gremlin-downloader.sh" "$DOWNLOADER_LINK_PATH"
chmod +x "$DOWNLOADER_LINK_PATH"

cat >"$DOWNLOADER_DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=Gremlin Downloader
Comment=Download some gremlins
Exec=$DOWNLOADER_LINK_PATH
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Utility;
EOF

chmod 644 "$DOWNLOADER_DESKTOP_FILE"

echo "Installed successfully! :3"
