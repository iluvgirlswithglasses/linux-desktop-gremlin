
from enum import Enum, auto
import os
import datetime
from typing import Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class State(Enum):
    INTRO = auto()
    IDLE = auto()
    HOVER = auto()
    WALKING = auto()
    WALK_IDLE = auto()
    DRAGGING = auto()
    CLICK = auto()
    PAT = auto()
    SLEEPING = auto()
    OUTRO = auto()
    EMOTE = auto()


class Settings:
    # Why do I use "Matikanetannhauser" instead of "Mambo", you might ask?
    # Well, my name is iluvgirlswithglasses, what do you expect about my length preferences?
    StartingChar = "Matikanetannhauser"
    Systray = False
    FollowRadius = 150.0
    FrameWidth = 200
    FrameHeight = 200
    LastPlayed: Dict[str, datetime.datetime] = {}
    MoveSpeed = 5


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


"""
The following classes should have been shared a trait or something similar.
I'll implement such generalization later.
"""


class SpriteMap:
    FrameRate = 60
    SpriteColumn = 5
    Idle = None
    Hover = None
    Click = None
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
    Pat = None
    Emote = None


class FrameCounts:
    Idle = None
    Hover = None
    Click = None
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
    Pat = None
    Emote = None


class CurrentFrames:
    Idle = 0
    Hover = 0
    Click = 0
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
    Pat = 0
    Emote = 0
