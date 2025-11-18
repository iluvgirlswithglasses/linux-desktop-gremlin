
import os
import json
from . import settings


def load(path, instance) -> bool:
    """ Generic config loader. """
    # load json into instance
    with open(path, 'r') as f:
        data = json.load(f)
        for key, val in data.items():
            if hasattr(instance, key):
                setattr(instance, key, val)
            else:
                print(f"Warning: Unrecognized config key '{key}' in {path}")
    # check for missing keys
    for attr in dir(instance):
        if not attr.startswith("__") and not callable(getattr(instance, attr)):
            if getattr(instance, attr) is None:
                print(f"Warning: Missing config key '{attr}' in {path}'")
                return False
    return True


def load_master_config(argv) -> bool:
    """ Loads the master config from `./config.json` and from command line args. """
    # load from file first
    path = os.path.join(settings.BASE_DIR, "config.json")
    if not os.path.exists(path):
        print(f"Warning: Master config file not found at {path}")
        return False
    if not load(path, settings.Settings):
        return False

    # override with command line args
    if len(argv) > 1:
        charname = argv[1]
        settings.Settings.StartingChar = charname

    return True


def load_sfx_map() -> bool:
    """ Loads the sound effects map config. """
    path = os.path.join(
        settings.BASE_DIR,
        "sounds", settings.Settings.StartingChar.lower(), "sfx-map.json"
    )
    if not os.path.exists(path):
        print(f"Warning: SFX map file not found at {path}")
        return False
    return load(path, settings.SfxMap)


def load_sprite_map() -> bool:
    """ Loads the sprite map config. """
    path = os.path.join(
        settings.BASE_DIR,
        "spritesheet", settings.Settings.StartingChar.lower(), "sprite-map.json"
    )
    if not os.path.exists(path):
        print(f"Warning: Sprite map file not found at {path}")
        return False
    return load(path, settings.SpriteMap)


def load_frame_count() -> bool:
    """ Loads frame count config for a character. """
    path = os.path.join(
        settings.BASE_DIR,
        "spritesheet", settings.Settings.StartingChar.lower(), "frame-count.json"
    )
    if not os.path.exists(path):
        print(f"Warning: Character config file not found at {path}")
        return False
    return load(path, settings.FrameCounts)


def load_emote_config() -> bool:
    """ Loads the emote config. """
    path = os.path.join(
        settings.BASE_DIR,
        "spritesheet", settings.Settings.StartingChar.lower(), "emote-config.json"
    )
    if not os.path.exists(path):
        print(f"Warning: Emote config file not found at {path}")
        return False
    return load(path, settings.EmoteConfig)
