from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from ..fsm.state_manager import StateManager
from ..fsm.timer_manager import TimerManager
from ..states import State
from .hotspot_geometry import (
    compute_left_hotspot_geometry,
    compute_right_hotspot_geometry,
    compute_top_hotspot_geometry,
)


class HotspotManager:
    def __init__(
        self, state_manager: StateManager, timer_manager: TimerManager, window: QWidget
    ):
        self.window = window
        self.state_manager = state_manager
        self.timer_manager = timer_manager

        # hotspots will trigger PAT / LEFT_ACTION / RIGHT_ACTION,
        # which can only be entered from IDLE, HOVER, SLEEP;
        # unless the character has shooting animations,
        # then the LEFT_ACTION and RIGHT_ACTION is spammable
        self.allowed_from = [
            State.WALK_IDLE,
            State.IDLE,
            State.HOVER,
            State.SLEEP,
        ]
        if self.state_manager.has_reload:
            self.allowed_from.extend([State.LEFT_ACTION, State.RIGHT_ACTION])

        # declare 3 hotspots: top, left, right
        self.t = QWidget(self.window)
        self.l = QWidget(self.window)
        self.r = QWidget(self.window)

        # set their geometries
        self.t.setGeometry(*compute_top_hotspot_geometry())
        self.l.setGeometry(*compute_left_hotspot_geometry())
        self.r.setGeometry(*compute_right_hotspot_geometry())

        # connect their click events
        self.t.mousePressEvent = self._top_hotspot_click
        self.l.mousePressEvent = self._left_hotspot_click
        self.r.mousePressEvent = self._right_hotspot_click

    def _on_hotspot_click(self, event, state: State):
        # right click trigger hotspots
        if event.button() == Qt.MouseButton.RightButton:
            if self.state_manager.current_state in self.allowed_from:
                self.state_manager.transition_to(state)
                self.timer_manager.reset_passive_timer()
        # left click is handled by the main window
        elif event.button() == Qt.MouseButton.LeftButton:
            self.window.mousePressEvent(event)

    """
    @! ---- Aliases --------------------------------------------------------------------------------
    """

    def _top_hotspot_click(self, event):
        self._on_hotspot_click(event, State.PAT)

    def _left_hotspot_click(self, event):
        self._on_hotspot_click(event, State.LEFT_ACTION)

    def _right_hotspot_click(self, event):
        self._on_hotspot_click(event, State.RIGHT_ACTION)
