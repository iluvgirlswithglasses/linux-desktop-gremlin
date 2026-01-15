from enum import Enum, auto


class State(Enum):
    """
    Defines the possible states of the gremlin.
    At any given time, the gremlin can only be in one state.
    """

    IDLE = auto()
    HOVER = auto()
    SLEEP = auto()
    INTRO = auto()
    OUTRO = auto()
    GRAB = auto()
    WALK = auto()
    WALK_IDLE = auto()
    POKE = auto()
    PAT = auto()
    LEFT_ACTION = auto()
    RIGHT_ACTION = auto()
    RELOAD = auto()
    EMOTE = auto()


class Direction(Enum):
    """
    WALK animation has 8 directions.
    The NONE direction is used for generalization purposes (see ./resources.py).
    """

    NONE = auto()
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP_LEFT = auto()
    UP_RIGHT = auto()
    DOWN_LEFT = auto()
    DOWN_RIGHT = auto()


def to_pascal_case(enum: Enum) -> str:
    """
    Converts enums like 'LEFT_ACTION' to 'LeftAction'.
    Very helpful if you want to parse from a json config file.
    """
    return enum.name.title().replace("_", "")


EndByFrameAnimations = [
    State.INTRO,
    State.LEFT_ACTION,
    State.RIGHT_ACTION,
    State.PAT,
    State.POKE,
    State.RELOAD,
    State.OUTRO,
]

EndByTimeoutAnimations = [
    State.WALK_IDLE,
    State.EMOTE,
]

LoopAnimations = [
    State.IDLE,
    State.HOVER,
    State.WALK,
    State.GRAB,
    State.SLEEP,
]
