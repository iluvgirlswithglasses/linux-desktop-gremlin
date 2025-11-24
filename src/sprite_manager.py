
import os
from PySide6.QtGui import QPixmap
from . import settings
from .settings import SpriteMap

CACHE = {}


def get(filename: str):
    """ Gets a QPixmap from the cache or loads it from disk. """
    # check cache first
    if filename in CACHE:
        return CACHE[filename]

    # load from disk if not in cache
    sheet = load_sprite(settings.Settings.StartingChar.lower(), filename)
    if sheet:
        CACHE[filename] = sheet
    return sheet


def load_sprite(file_folder, file_name):
    """ Loads a sprite from disk into a QPixmap. """
    path = os.path.join(
        settings.BASE_DIR,
        "spritesheet", file_folder, file_name
    )
    if not os.path.exists(path):
        print(f"Warning: Sprite file not found at {path}")
        return None

    try:
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print(f"Error: Failed to load pixmap from {path}")
            return None
        return pixmap
    except Exception as e:
        print(f"Error loading sprite {path}: {e}")
        return None


def clear_cache():
    CACHE.clear()
