from PySide6.QtCore import QEvent, QObject

from .input_listeners import HoverListener, KeyboardListener, MouseListener


class WindowInputFilter(QObject):
    """
    Single QObject eventFilter installed on GremlinWindow.
    Dispatches Qt events to registered typed listeners.
    Replaces all direct Qt event-slot assignments (monkey-patching).
    """

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._mouse: list[MouseListener] = []
        self._keyboard: list[KeyboardListener] = []
        self._hover: list[HoverListener] = []

    def register_mouse(self, listener: MouseListener) -> None:
        self._mouse.append(listener)

    def register_keyboard(self, listener: KeyboardListener) -> None:
        self._keyboard.append(listener)

    def register_hover(self, listener: HoverListener) -> None:
        self._hover.append(listener)

    def unregister_all(self) -> None:
        """Clear all listeners (called on shutdown to silence further input)."""
        self._mouse.clear()
        self._keyboard.clear()
        self._hover.clear()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        match event.type():
            case QEvent.Type.MouseButtonPress:
                for listener in self._mouse:
                    listener.on_mouse_press(event)  # type: ignore[arg-type]
            case QEvent.Type.MouseMove:
                for listener in self._mouse:
                    listener.on_mouse_move(event)  # type: ignore[arg-type]
            case QEvent.Type.MouseButtonRelease:
                for listener in self._mouse:
                    listener.on_mouse_release(event)  # type: ignore[arg-type]
            case QEvent.Type.KeyPress:
                for listener in self._keyboard:
                    listener.on_key_press(event)  # type: ignore[arg-type]
            case QEvent.Type.KeyRelease:
                for listener in self._keyboard:
                    listener.on_key_release(event)  # type: ignore[arg-type]
            case QEvent.Type.Enter:
                for listener in self._hover:
                    listener.on_mouse_enter(event)  # type: ignore[arg-type]
            case QEvent.Type.Leave:
                for listener in self._hover:
                    listener.on_mouse_leave(event)
        return False  # don't consume
