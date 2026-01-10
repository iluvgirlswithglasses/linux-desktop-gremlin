"""Linux Desktop Gremlins - Desktop pet application for Linux."""

__version__ = "0.1.0"

# Public API exports
from . import config_manager
from .gremlin import GremlinWindow
from .settings import (
    CurrentFrames,
    EmoteConfig,
    FrameCounts,
    Settings,
    SfxMap,
    SpriteMap,
    State,
)

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
