#!/bin/bash
# an extremely simple gremlin picker using rofi

# move to script directory
DIR=$( dirname $(realpath "$0") )
cd $DIR

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

	# check which session to launch (use uv)
	if [[ $XDG_SESSION_TYPE == "wayland" ]]; then
		if command -v uv >/dev/null 2>&1; then
			./run-uv-xwayland.sh "$pick"
		else
			./run-xwayland.sh "$pick"
		fi
	elif [[ $XDG_SESSION_TYPE == "x11" ]]; then
		if command -v uv >/dev/null 2>&1; then
			./run-uv-x11.sh "$pick"
		else
			./run-x11.sh "$pick"
		fi
	fi
}

main_menu
