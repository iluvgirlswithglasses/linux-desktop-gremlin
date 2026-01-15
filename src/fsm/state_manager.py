import sys
from typing import Callable

from ..engines import SoundEngine
from ..resources import ResourceRegistry, SpriteProperties
from ..states import Direction, State


class StateManager:
    def __init__(self, sound_engine: SoundEngine, is_under_mouse: Callable[[], bool]):
        """
        Manages the current state of the gremlin and handles state transitions.
        It has two dependencies:
        1.   sound_engine:  To play sound effects during state transitions.
        2. is_under_mouse:  A callable that checks if the gremlin is under the mouse cursor.
        """

        self.current_state = State.IDLE
        self.current_direction = Direction.NONE

        # dependencies
        self.sound_engine = sound_engine
        self.is_under_mouse: Callable[[], bool] = is_under_mouse

        # shooting animation for Blue Archive characters
        self.has_reload = SpriteProperties.HasReloadAnimation
        self.ammo = 6 if self.has_reload else 0

    def transition_to(
        self,
        new_state: State,
        new_direction: Direction = Direction.NONE,
        playsound: bool = True,
    ):
        """
        Registers a state transition.
        """
        # direction has process priority over state
        if self.current_direction != new_direction:
            self._reset_current_frame(new_state, new_direction)
        self.current_direction = new_direction

        # prevents entering the same state unless spammable
        if self.current_state == new_state and not self._is_spammable(new_state):
            return

        self._handle_entry_effect(new_state, playsound)
        self._reset_current_frame(new_state, new_direction)
        self.current_state = new_state

    def to_idle_or_hover(self):
        if self.is_under_mouse():
            playsound = self.current_state in [State.IDLE, State.SLEEP]
            self.transition_to(State.HOVER, playsound=playsound)
        else:
            self.transition_to(State.IDLE)

    def on_completion(self):
        """
        Decide how to switch states upon animation completion.
        """
        match self.current_state:
            # EndByFrameAnimations
            case State.INTRO | State.PAT | State.POKE | State.RELOAD:
                self.to_idle_or_hover()
            case State.LEFT_ACTION | State.RIGHT_ACTION:
                self._check_reload()
            case State.OUTRO:
                sys.exit(0)

            # EndByTimeoutAnimations
            case State.WALK_IDLE | State.EMOTE:
                self.to_idle_or_hover()

            # LoopAnimations continue to loop, no action needed
            case _:
                pass

    """
    @! ---- Defines how must a state starts or ends ------------------------------------------------
    """

    def _handle_entry_effect(self, new_state: State, playsound: bool):
        # play the sound effect upon state switch
        if playsound:
            self.sound_engine.play(new_state)

        # some states have special effects on entry
        match new_state:
            case State.LEFT_ACTION | State.RIGHT_ACTION:
                if self.ammo > 0:
                    self.ammo -= 1
            case State.RELOAD:
                self.ammo = 6
            case _:
                pass

    """
    @! ---- Utilities ------------------------------------------------------------------------------
    """

    def _is_spammable(self, state: State) -> bool:
        # if she is shooting, consider allowing her to spam the action
        shootable = state in [State.LEFT_ACTION, State.RIGHT_ACTION] and self.ammo > 0
        if not shootable:
            return False

        # if passed the first quarter of the animation, allow shooting
        frame_data = ResourceRegistry.get_animation(state, Direction.NONE)
        return frame_data.frame_count // 4 < frame_data.current_frame

    def _reset_current_frame(self, state: State, direction: Direction):
        data = ResourceRegistry.get_animation(state, direction)
        data.current_frame = 0

    def _check_reload(self):
        if self.has_reload and self.ammo == 0:
            self.transition_to(State.RELOAD)
        else:
            self.to_idle_or_hover()
