import string

from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget

from ..fsm.state_manager import StateManager
from ..fsm.timer_manager import TimerManager
from ..fsm.walk_manager import WalkManager
from ..settings import Preferences
from ..states import State

AllowedEmoteStates = [
    State.WALK_IDLE,
    State.IDLE,
    State.HOVER,
    State.SLEEP,
]

AllowedWalkStates = [
    *AllowedEmoteStates,
    State.WALK,
]


def resolve_emote_key() -> int | None:
    """
    If the emote key is enabled and valid, returns its ord key code.
    Otherwise, return None.
    """

    if not Preferences.EmoteKeyEnabled:
        return None

    key = Preferences.EmoteKey

    try:
        # limits to qwerty alphanumerical chars and digits 0-9
        char = key.strip().upper()
        if char not in string.ascii_uppercase + string.digits:
            print(f"\n[Warning] EmoteKey {key!r} not allowed (allowed: A-Z, 0-9)")
            return None
        return ord(char)
    except Exception:
        return None


class KeyboardManager:
    def __init__(
        self,
        state_manager: StateManager,
        walk_manager: WalkManager,
        timer_manager: TimerManager,
        window: QWidget,
    ):
        # dependencies
        self.state_manager = state_manager
        self.walk_manager = walk_manager
        self.timer_manager = timer_manager

        # should I have created a separate manager for this?
        self.emote_key = resolve_emote_key()

        # bind window's key events
        window.keyPressEvent = self.on_key_press
        window.keyReleaseEvent = self.on_key_release

    """
    @! ---- Event Listeners ------------------------------------------------------------------------
    """

    def on_key_press(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return

        # check for walk
        self.walk_manager.record_key_press(event)
        if (
            self.walk_manager.is_moving()
            and self.state_manager.current_state in AllowedWalkStates
        ):
            self.state_manager.transition_to(
                State.WALK, self.walk_manager.get_direction()
            )
            self.timer_manager.reset_passive_timer()

        # check for manual emote trigger
        if (
            self.emote_key is not None
            and event.key() == self.emote_key
            and self.state_manager.current_state in AllowedEmoteStates
        ):
            self.state_manager.transition_to(State.EMOTE)
            self.timer_manager.reset_emote_dur_timer()
            self.timer_manager.reset_passive_timer()

    def on_key_release(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return

        self.walk_manager.record_key_release(event)

        # if was walking...
        if self.state_manager.current_state == State.WALK:
            # ...and continued walking, change direction
            if self.walk_manager.is_moving():
                self.state_manager.transition_to(
                    State.WALK, self.walk_manager.get_direction()
                )
            # ...and not walking anymore, switch to walk idle
            else:
                self.state_manager.transition_to(State.WALK_IDLE)
                self.timer_manager.reset_walk_idle_timer()
