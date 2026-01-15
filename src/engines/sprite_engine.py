from typing import Dict

from PySide6.QtGui import QPixmap

CACHE: Dict[str, QPixmap] = {}


def get_spritesheet(path: str):
    """Gets a QPixmap from cache or loads it from disk."""

    # check cache first
    if path in CACHE:
        return CACHE[path]

    # load from disk & save to cache if not cached
    sheet = _load_sprite(path)
    CACHE[path] = sheet
    return sheet


def _load_sprite(path: str):
    """Loads a sprite sheet from disk."""
    return QPixmap(path)
