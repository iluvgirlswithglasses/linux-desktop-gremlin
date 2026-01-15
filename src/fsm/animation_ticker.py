from typing import Callable

from ..engines import FrameEngine
from ..states import EndByFrameAnimations
from .state_manager import State, StateManager


class AnimationTicker:

    def __init__(
        self,
        state_manager: StateManager,
        frame_engine: FrameEngine,
        upd_position: Callable[[], None],
    ):
        self.state_manager = state_manager
        self.frame_engine = frame_engine
        self.upd_position = upd_position

    def tick(self):
        # advance animation by 1 frame
        cur_state = self.state_manager.current_state
        cur_direc = self.state_manager.current_direction
        end_frame = self.frame_engine.advance(cur_state, cur_direc)

        # check for animation completion
        if end_frame and cur_state in EndByFrameAnimations:
            self.state_manager.on_completion()

        # window position update callback
        if cur_state == State.WALK:
            self.upd_position()
