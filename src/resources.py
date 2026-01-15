import datetime
from dataclasses import dataclass
from typing import Dict, Tuple

from .states import Direction, State


class SpriteProperties:
    """
    Description of sprite properties.
    You must tell this program what the sprites look like here.
    """

    FrameRate: int = 60
    SpriteColumn: int = 5
    FrameHeight: int = 0
    FrameWidth: int = 0
    HasReloadAnimation: bool = False


@dataclass
class AnimationData:
    """
    Each animation has three properties:
    1. sprite_path: The path to the sprite file.
    2. frame_count: The total number of frames in the animation.
    3. current_frame: The current frame being displayed.

    (1) and (2) must be given by `sprite-map.json` and `frame-count.json`.
    """

    sprite_path: str
    frame_count: int
    current_frame: int


@dataclass
class SoundData:
    """
    Each sound has two properties:
    1. sound_file: The name of the sound file.
    2. last_played: The last time the sound was played, which helps prevent sound overlap.

    (1) must be given by `sound-map.json`.
    """

    sound_path: str
    last_played: datetime.datetime


class ResourceRegistry:
    """
    Maps State to AnimationData and SoundData.
    """

    # Most animations can be accessed via `animations[(state, Direction.NONE)]`,
    # except for WALK which you must pass a direction.
    animations: Dict[Tuple[State, Direction], AnimationData] = {}
    sounds: Dict[State, SoundData] = {}

    has_reload: bool = False

    @classmethod
    def get_animation(
        cls, state: State, direction: Direction = Direction.NONE
    ) -> AnimationData:
        ans = cls.animations.get((state, direction))
        if ans is None:
            raise ValueError(f"State {state} and direction {direction} is invalid")
        return ans

    @classmethod
    def get_sound(cls, state: State) -> SoundData:
        ans = cls.sounds.get(state)
        if ans is None:
            raise ValueError(f"State {state} has no sound")
        return ans
