#!/bin/bash

# Ask user about virtual environment setup
echo "Would you like to set this up with a virtual environment [Y/n]"
read -r choice_vir_env

# Default to "yes" if empty input
choice_vir_env=${choice_vir_env:-Y}

# Convert to lowercase for easier comparison
choice_lower=$(echo "$choice_vir_env" | tr '[:upper:]' '[:lower:]')

if [[ "$choice_lower" == "y" || "$choice_lower" == "" ]]; then
	# Check if uv is installed
	if command -v uv >/dev/null 2>&1; then
		echo "uv is installed"
	else
		echo "uv is not installed, installing..."
		echo "Executing: curl -LsSf https://astral.sh/uv/install.sh | sh"
		curl -LsSf https://astral.sh/uv/install.sh | sh
	fi

	echo "Running 'uv sync' to install required packages..."
	uv sync
else
	echo "Please install pyside6/pyside6-tools and qt6-base using your package manager."
fi

set -e # Exit immediately if a command exits with a non-zero status

echo "=============================="
echo " Linux Desktop Gremlin Installer"
echo "=============================="
echo
echo "1) Install"
echo "2) Uninstall"
echo "3) Update"
echo -n "Select an option [1-3]: "
read choice

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_PATH="$HOME/.config/linux-desktop-gremlin"
BIN_PATH="$HOME/.local/bin"
LINK_PATH="$BIN_PATH/gremlin_picker"
DESKTOP_FILE="$HOME/.local/share/applications/gremlin_picker.desktop"
ICON_PATH="$INSTALL_PATH/icon.png" # optional icon

# Function: uninstall
uninstall() {
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
}

case "$choice" in
1)
	echo "→ Installing Linux Desktop Gremlin..."

	mkdir -p "$INSTALL_PATH" "$BIN_PATH" "$(dirname "$DESKTOP_FILE")"

	cp -r "$SCRIPT_DIR"/* "$INSTALL_PATH/"

	ln -sf "$INSTALL_PATH/gremlin_picker.sh" "$LINK_PATH"
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

	echo "Installed successfully! :)"
	;;

2)
	echo "→ Uninstalling Linux Desktop Gremlin..."
	uninstall
	echo "Uninstalled successfully! X)"
	;;

3)
	echo "→ Updating Linux Desktop Gremlin..."

	if [ -d "$SCRIPT_DIR/.git" ]; then
		echo "Fetching latest changes from git..."
		git -C "$SCRIPT_DIR" fetch --all
		git -C "$SCRIPT_DIR" pull --rebase
	else
		echo "No git repository found in $SCRIPT_DIR. Cannot update automatically."
		exit 1
	fi

	echo "Uninstalling current version..."
	uninstall

	echo "Reinstalling latest version..."
	mkdir -p "$INSTALL_PATH" "$BIN_PATH" "$(dirname "$DESKTOP_FILE")"

	cp -r "$SCRIPT_DIR"/* "$INSTALL_PATH/"

	ln -sf "$INSTALL_PATH/gremlin_picker.sh" "$LINK_PATH"
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

	echo "Update complete! :)"
	;;

*)
	echo "? Invalid option. Please choose 1, 2, or 3."
	exit 1
	;;
esac
