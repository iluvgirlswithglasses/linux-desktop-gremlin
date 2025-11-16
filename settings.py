
from enum import Enum, auto
import os
import datetime
from typing import Dict
from PySide6.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


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


class Settings:
    # Why do I use "Matikanetannhauser" instead of "Mambo", you might ask?
    # Well, my name is iluvgirlswithglasses, what do you expect about my length preferences?
    StartingChar = "Matikanetannhauser"
    Systray = False
    FollowRadius = 150.0
    LastPlayed: Dict[str, datetime.datetime] = {}
    MoveSpeed = 5
    EmoteKeyEnabled = True
    EmoteKey = "P"


class MouseSettings:
    # Cursor's information is restricted in wayland, so there's no much we can do here.
    LastMousePosition = None
    FollowSpeed = 5.0
    MouseX = 0.0
    MouseY = 0.0
    Speed = 10.0


class EmoteConfig:
    AnnoyEmote = True
    MinEmoteTriggerMinutes = 5
    MaxEmoteTriggerMinutes = 15
    EmoteDuration = 3600


class SfxMap:
    Hover = None
    Intro = None
    Outro = None
    Grab = None
    Walk = None
    Poke = None
    Pat = None
    LeftAction = None
    RightAction = None
    Reload = None
    Emote = None


"""
The following classes should have been shared a trait or something similar.
I'll implement such generalization later.
"""


class SpriteMap:
    FrameRate = 60
    SpriteColumn = 5
    FrameHeight = None
    FrameWidth = None
    TopHotspotHeight = None
    TopHotspotWidth = None
    SideHotspotHeight = None
    SideHotspotWidth = None
    HasReloadAnimation = False

    Idle = None
    Hover = None
    Sleep = None
    Intro = None
    Outro = None
    Grab = None
    Up = None
    Down = None
    Left = None
    Right = None
    UpLeft = None
    UpRight = None
    DownLeft = None
    DownRight = None
    WalkIdle = None
    Poke = None
    Pat = None
    LeftAction = None
    RightAction = None
    Reload = ""
    Emote = None


class FrameCounts:
    Idle = None
    Hover = None
    Sleep = None
    Intro = None
    Outro = None
    Grab = None
    Up = None
    Down = None
    Left = None
    Right = None
    UpLeft = None
    UpRight = None
    DownLeft = None
    DownRight = None
    WalkIdle = None
    Poke = None
    Pat = None
    LeftAction = None
    RightAction = None
    Reload = None
    Emote = None


class CurrentFrames:
    Idle = 0
    Hover = 0
    Sleep = 0
    Intro = 0
    Outro = 0
    Grab = 0
    Up = 0
    Down = 0
    Left = 0
    Right = 0
    UpLeft = 0
    UpRight = 0
    DownLeft = 0
    DownRight = 0
    WalkIdle = 0
    Poke = 0
    Pat = 0
    LeftAction = 0
    RightAction = 0
    Reload = 0
    Emote = 0
