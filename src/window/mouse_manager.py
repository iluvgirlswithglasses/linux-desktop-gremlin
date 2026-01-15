from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget

from ..fsm.state_manager import StateManager
from ..fsm.timer_manager import TimerManager
from ..states import State

AllowedClickStates = [
    State.WALK_IDLE,
    State.IDLE,
    State.HOVER,
    State.SLEEP,
]


class MouseManager:
    def __init__(
        self,
        state_manager: StateManager,
        timer_manager: TimerManager,
        window: QWidget,
    ):
        # dependencies
        self.state_manager = state_manager
        self.timer_manager = timer_manager

        # allow this class to move the window
        self.move_window = window.move
        self.window_pos = window.pos
        self.drag_pos = QPoint(0, 0)

        # binds window's mouse events
        window.mousePressEvent = self.on_mouse_press
        window.mouseMoveEvent = self.on_mouse_move
        window.mouseReleaseEvent = self.on_mouse_release

    def on_mouse_press(self, event: QMouseEvent):
        # ignore clicks in disallowed states
        if self.state_manager.current_state not in AllowedClickStates:
            return

        # received interation from user --> reset passive timer
        self.timer_manager.reset_passive_timer()

        # transition to grab
        if event.button() == Qt.MouseButton.LeftButton:
            self.state_manager.transition_to(State.GRAB)
            self.drag_pos = event.globalPosition().toPoint() - self.window_pos()
        # transition to poke
        elif event.button() == Qt.MouseButton.RightButton:
            self.state_manager.transition_to(State.POKE)

    def on_mouse_move(self, event: QMouseEvent):
        if (
            self.state_manager.current_state == State.GRAB
            and event.buttons() == Qt.MouseButton.LeftButton
        ):
            self.move_window(event.globalPosition().toPoint() - self.drag_pos)

    def on_mouse_release(self, event: QMouseEvent):
        # release from grab
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.state_manager.current_state == State.GRAB
        ):
            self.state_manager.to_idle_or_hover()
