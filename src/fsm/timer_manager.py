import random

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget

from ..resources import SpriteProperties
from ..settings import EmotePreferences, Preferences
from ..states import State
from .animation_ticker import AnimationTicker
from .state_manager import StateManager


def _mins2ms(mins: int) -> int:
    return mins * 60 * 1000


AllowedEmoteStates = [
    State.WALK_IDLE,
    State.IDLE,
    State.HOVER,
    State.SLEEP,
]


class TimerManager:
    def __init__(
        self,
        parent: QWidget,
        state_manager: StateManager,
        animation_ticker: AnimationTicker,
    ):
        """
        List of timers
        - master_timer:     Each tick updates one animation frame.
        - idle_timer:       Time spent idle; Tick fires sleep animation.
        - sleep_timer:      Time spent sleeping; Tick fires idle animation.
        - walk_idle_timer:  Time since last walking; Tick fires idle animation.
        - emote_timer:      Tick triggers emote animation.
        - emote_dur_timer:  Time spent emoting; Tick triggers idle animation.
        """

        self.state_manager = state_manager

        self.master_timer = QTimer(parent)
        self.idle_timer = QTimer(parent)
        self.sleep_timer = QTimer(parent)
        self.walk_idle_timer = QTimer(parent)
        self.emote_timer = QTimer(parent)
        self.emote_dur_timer = QTimer(parent)

        self.walk_idle_timer.setSingleShot(True)
        self.emote_dur_timer.setSingleShot(True)

        self.master_timer.timeout.connect(animation_ticker.tick)
        self.idle_timer.timeout.connect(self.tick_idle_timer)
        self.sleep_timer.timeout.connect(self.tick_sleep_timer)
        self.walk_idle_timer.timeout.connect(self.tick_walk_idle_timer)
        self.emote_timer.timeout.connect(self.tick_emote_timer)
        self.emote_dur_timer.timeout.connect(self.tick_emote_dur_timer)

    """
    @! ---- Package Timer Kickoffs -----------------------------------------------------------------
    """

    def start_passive_timer(self):
        self.master_timer.start(1000 // SpriteProperties.FrameRate)
        self.reset_passive_timer()

    def reset_passive_timer(self):
        self.reset_idle_timer()
        self.reset_emote_timer()

    """
    @! ---- Timer Kickoffs -------------------------------------------------------------------------
    """

    def reset_idle_timer(self):
        timeout = _mins2ms(Preferences.IdleMinutes)
        self.idle_timer.start(timeout)

    def reset_sleep_timer(self):
        timeout = _mins2ms(Preferences.SleepMinutes)
        self.sleep_timer.start(timeout)

    def reset_walk_idle_timer(self):
        timeout = 2000
        self.walk_idle_timer.start(timeout)

    def reset_emote_timer(self):
        min_ms = _mins2ms(EmotePreferences.MinEmoteTriggerMinutes)
        max_ms = _mins2ms(EmotePreferences.MaxEmoteTriggerMinutes)

        # extra safety
        min_ms = max(10000, min_ms)
        max_ms = max(min_ms, max_ms)

        timeout = random.randint(min_ms, max_ms)
        self.emote_timer.start(timeout)

    def reset_emote_dur_timer(self):
        timeout = EmotePreferences.EmoteDuration
        self.emote_dur_timer.start(timeout)

    """
    @! ---- Timer Tick -----------------------------------------------------------------------------
    """

    def tick_idle_timer(self):
        if self.state_manager.current_state == State.IDLE:
            self.state_manager.transition_to(State.SLEEP)
            self.reset_sleep_timer()

    def tick_sleep_timer(self):
        if self.state_manager.current_state == State.SLEEP:
            self.state_manager.transition_to(State.IDLE)
            self.reset_idle_timer()

    def tick_walk_idle_timer(self):
        if self.state_manager.current_state == State.WALK_IDLE:
            self.state_manager.to_idle_or_hover()

    def tick_emote_timer(self):
        if self.state_manager.current_state in AllowedEmoteStates:
            self.state_manager.transition_to(State.EMOTE)
            self.reset_emote_dur_timer()
        else:
            self.reset_emote_timer()

    def tick_emote_dur_timer(self):
        if self.state_manager.current_state == State.EMOTE:
            self.state_manager.to_idle_or_hover()
            self.reset_passive_timer()
