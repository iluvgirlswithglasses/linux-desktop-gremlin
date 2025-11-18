#!/bin/bash
# an extremely simple gremlin picker using rofi

# move to project root directory
SCRIPT_DIR="$(dirname $(realpath "$0"))"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# ensure uv can be found
export PATH=$PATH:$HOME/.local/bin

# list all gremlins in spritesheet
available_gremlins=$(command ls -1 ./spritesheet 2>/dev/null)

# use rofi to pick the selected gremlin
main_menu() {
	pick=$(echo -e "$available_gremlins\nExit" | rofi -dmenu)

	if [[ -z $pick || $pick == "Exit" ]]; then
		exit 0
	fi

	# run with the unified launcher script
	./run.sh "$pick"
}

main_menu
