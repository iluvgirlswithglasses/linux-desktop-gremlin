#!/usr/bin/env python3
"""
Launcher for Linux Desktop Gremlins.
Handles environment detection and Qt platform configuration.
"""

import sys

def main():
    """Main entry point that sets up environment and launches the application."""
    from PySide6.QtWidgets import QApplication
    from . import config_manager
    from .gremlin import GremlinWindow

    app = QApplication(sys.argv)

    try:
        state = (config_manager.load_master_config(sys.argv) and
                 config_manager.load_sfx_map() and
                 config_manager.load_sprite_map() and
                 config_manager.load_frame_count() and
                 config_manager.load_emote_config())
        if not state:
            print("Fatal Error: Corrupted configuration. Quitting...")
            sys.exit(1)
    except Exception as e:
        print(f"Fatal Error: Could not load configuration. {e}")
        sys.exit(1)

    window = GremlinWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
