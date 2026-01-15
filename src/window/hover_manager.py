from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import QWidget

from ..fsm.state_manager import StateManager
from ..fsm.timer_manager import TimerManager
from ..fsm.walk_manager import WalkManager
from ..states import State


class HoverManager:
    def __init__(
        self,
        walk_manager: WalkManager,
        state_manager: StateManager,
        timer_manager: TimerManager,
        window: QWidget,
    ):
        self.walk_manager = walk_manager
        self.state_manager = state_manager
        self.timer_manager = timer_manager

        self.set_focus = window.setFocus
        self.clear_focus = window.clearFocus

        window.enterEvent = self.on_mouse_enter
        window.leaveEvent = self.on_mouse_leave

    def on_mouse_enter(self, _: QEnterEvent):
        self.set_focus()
        self.timer_manager.reset_idle_timer()

        match self.state_manager.current_state:
            case State.IDLE:
                # play hover animation & sound + reset idle timer
                self.state_manager.transition_to(State.HOVER)
            case State.SLEEP:
                # let her sleep
                pass

    def on_mouse_leave(self, _):
        self.clear_focus()
        self.walk_manager.record_mouse_leave()

        match self.state_manager.current_state:
            # if mouse leaves while walking, stop walking and go to WALK_IDLE
            case State.WALK:
                self.state_manager.transition_to(State.WALK_IDLE)
            # if mouse leaves while hovering, go to IDLE
            case State.HOVER:
                self.state_manager.transition_to(State.IDLE)
            # if in WALK_IDLE, do nothing. The timer will handle the transition.
            case _:
                pass
