"""Linux Desktop Gremlins - Desktop pet application for Linux."""

__version__ = "0.1.0"

# Public API exports
from .gremlin import GremlinWindow
from .settings import State, Settings, SpriteMap, FrameCounts, EmoteConfig, SfxMap, CurrentFrames
from . import config_manager

__all__ = [
    "GremlinWindow",
    "State",
    "Settings",
    "SpriteMap",
    "FrameCounts",
    "EmoteConfig",
    "SfxMap",
    "CurrentFrames",
    "config_manager",
]
