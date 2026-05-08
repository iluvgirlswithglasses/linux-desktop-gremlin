from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QWidget

from ..fsm.state_manager import StateManager
from ..fsm.timer_manager import TimerManager
from ..states import AllowedClickStates, State
from .hotspot_geometry import (
    compute_left_hotspot_geometry,
    compute_right_hotspot_geometry,
    compute_top_hotspot_geometry,
)
from .input_listeners import MouseListener


class HotspotFilter(QObject):
    """
    Per-hotspot eventFilter. Right-click fires the hotspot action; left-click
    forwards to the window's MouseListener so drag still works over hotspots.
    """

    def __init__(
        self,
        action_state: State,
        allowed_from: list[State],
        state_manager: StateManager,
        timer_manager: TimerManager,
        mouse_listener: MouseListener,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.action_state = action_state
        self.allowed_from = allowed_from
        self.state_manager = state_manager
        self.timer_manager = timer_manager
        self.mouse_listener = mouse_listener

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: ARG002
        if event.type() != QEvent.Type.MouseButtonPress:
            return False

        btn = event.button()  # type: ignore[attr-defined]
        if btn == Qt.MouseButton.RightButton:
            if self.state_manager.current_state in self.allowed_from:
                self.state_manager.transition_to(self.action_state)
                self.timer_manager.reset_passive_timer()
            return True  # always consume right-clicks on hotspot children
        elif btn == Qt.MouseButton.LeftButton:
            self.mouse_listener.on_mouse_press(event)  # type: ignore[arg-type]
            return True
        return False


class HotspotManager:
    def __init__(
        self,
        state_manager: StateManager,
        timer_manager: TimerManager,
        mouse_listener: MouseListener,
        window: QWidget,
    ) -> None:
        allowed_from = list(AllowedClickStates)
        if state_manager.has_reload:
            allowed_from.extend([State.LEFT_ACTION, State.RIGHT_ACTION])

        # three child widgets used purely as click-target regions
        self._t = QWidget(window)
        self._l = QWidget(window)
        self._r = QWidget(window)

        self._t.setGeometry(*compute_top_hotspot_geometry())
        self._l.setGeometry(*compute_left_hotspot_geometry())
        self._r.setGeometry(*compute_right_hotspot_geometry())

        # each hotspot gets its own filter with the matching action state
        self._top_filter = HotspotFilter(
            State.PAT, allowed_from, state_manager, timer_manager, mouse_listener
        )
        self._left_filter = HotspotFilter(
            State.LEFT_ACTION,
            allowed_from,
            state_manager,
            timer_manager,
            mouse_listener,
        )
        self._right_filter = HotspotFilter(
            State.RIGHT_ACTION,
            allowed_from,
            state_manager,
            timer_manager,
            mouse_listener,
        )

        self._t.installEventFilter(self._top_filter)
        self._l.installEventFilter(self._left_filter)
        self._r.installEventFilter(self._right_filter)
