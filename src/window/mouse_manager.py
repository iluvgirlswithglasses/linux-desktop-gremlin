from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget

from ..fsm.state_manager import StateManager
from ..fsm.timer_manager import TimerManager
from ..states import AllowedClickStates, State


class MouseManager:
    def __init__(
        self,
        state_manager: StateManager,
        timer_manager: TimerManager,
        window: QWidget,
    ) -> None:
        self.state_manager = state_manager
        self.timer_manager = timer_manager

        self._move_window = window.move
        self._window_pos = window.pos
        self._drag_pos = QPoint(0, 0)

    def on_mouse_press(self, event: QMouseEvent) -> None:
        # ignore clicks in disallowed states
        if self.state_manager.current_state not in AllowedClickStates:
            return

        # received interation from user --> reset passive timer
        self.timer_manager.reset_passive_timer()

        # transition to grab
        if event.button() == Qt.MouseButton.LeftButton:
            self.state_manager.transition_to(State.GRAB)
            self._drag_pos = event.globalPosition().toPoint() - self._window_pos()
        # transition to poke
        elif event.button() == Qt.MouseButton.RightButton:
            self.state_manager.transition_to(State.POKE)

    def on_mouse_move(self, event: QMouseEvent) -> None:
        if (
            self.state_manager.current_state == State.GRAB
            and event.buttons() == Qt.MouseButton.LeftButton
        ):
            self._move_window(event.globalPosition().toPoint() - self._drag_pos)

    def on_mouse_release(self, event: QMouseEvent) -> None:
        # release from grab
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.state_manager.current_state == State.GRAB
        ):
            self.state_manager.to_idle_or_hover()
