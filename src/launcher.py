import sys


def main():
    from PySide6.QtWidgets import QApplication

    from . import configs_loader
    from .window.gremlin_window import GremlinWindow

    app = QApplication(sys.argv)
    try:
        char = sys.argv[1] if len(sys.argv) > 1 else None
        configs_loader.load_resources_and_preferences(char)
    except Exception as e:
        print(f"Fatal Error: Could not load configuration. {e}")
        sys.exit(1)

    window = GremlinWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
