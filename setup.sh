#!/bin/bash

# clone the repo into ~/.config
echo "Cloning repo into ~/.config/linux-desktop-gremlin"
git clone https://github.com/iluvgirlswithglasses/linux-desktop-gremlin ~/.config/linux-desktop-gremlin
echo "Clone completed!"

cd ~/.config/linux-desktop-gremlin
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
