import datetime
import json
import os
from enum import Enum

from .resources import AnimationData, ResourceRegistry, SoundData, SpriteProperties
from .settings import EmotePreferences, HotspotSettings, Preferences
from .states import Direction, State, to_pascal_case

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CODE_DIR)


def load_resources_and_preferences(char: str | None = None):
    """
    Reads configuration from ./config.json, spritesheet/<char>/*.json, sounds/<char>/*.json
    and writes them into ResourceRegistry, Preferences, EmotePreferences, HotspotSettings.

    This function immediately raises any of these exceptions if anything goes wrong:
    - FileNotFoundError: If any of the required files are missing.
    - ValueError: If any of the JSON files are malformed.
    - KeyError: If any of the required keys are missing in the JSON files.
    """
    # find & load master config
    master_config = _load_json(os.path.join(BASE_DIR, "config.json"))
    _load_master_config(master_config)

    # override starting char if provided
    if char is not None:
        Preferences.StartingChar = char
    else:
        char = Preferences.StartingChar

    # find character configs
    emote_config = _load_char_json(char, ResourceType.SPRITESHEET, "emote-config.json")
    frame_config = _load_char_json(char, ResourceType.SPRITESHEET, "frame-count.json")
    sprite_config = _load_char_json(char, ResourceType.SPRITESHEET, "sprite-map.json")
    sound_config = _load_char_json(char, ResourceType.SOUND, "sfx-map.json")

    # load character configs & resources
    _load_emote_config(emote_config)
    _load_hotspot_config(sprite_config)
    _load_sprite_properties(char, sprite_config)
    _load_sprite_resource(char, sprite_config, frame_config)
    _load_sound_resource(char, sound_config)


"""
@! ---- Path utility -------------------------------------------------------------------------------
"""


class ResourceType(Enum):
    SPRITESHEET = "spritesheet"
    SOUND = "sounds"


def _get_char_file(char_name: str, resource: ResourceType, file_name: str) -> str:
    ans = os.path.join(BASE_DIR, resource.value, char_name.lower(), file_name)
    if not os.path.exists(ans) or not os.path.isfile(ans):
        raise FileNotFoundError(f"Missing required file: {ans}")
    return ans


def _load_json(filepath: str) -> dict:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing config file: {filepath}")
    with open(filepath, "r") as f:
        config = json.load(f)
    return config


def _load_char_json(char_name: str, resource: ResourceType, file_name: str) -> dict:
    filepath = _get_char_file(char_name, resource, file_name)
    return _load_json(filepath)


"""
@! ---- Specifies how configuration is parsed and loaded -------------------------------------------
"""


def _load_to_class(config: dict, cls: type, required: list, optional: list):
    # ensures that all required keys are present
    for key in required:
        if key not in config:
            raise ValueError(f"Missing required key '{key}'")

    # lists all keys
    keys = [*required]
    keys.extend([key for key in optional if key in config])
    for key in keys:
        # ensures the json value type matches the class attribute type
        if type(config[key]) is not type(getattr(cls, key)):
            raise TypeError(f"Invalid type for key '{key}'")
        # writes the value to the class attribute
        setattr(cls, key, config[key])


def _load_master_config(master_config: dict):
    required = [
        "StartingChar",
    ]
    optional = [
        "Systray",
        "MoveSpeed",
        "Volume",
        "AudioDevice",
        "EmoteKey",
        "EmoteKeyEnabled",
        "IdleMinutes",
        "SleepMinutes",
    ]
    _load_to_class(master_config, Preferences, required, optional)


def _load_emote_config(emote_config: dict):
    required = [
        "AnnoyEmote",
        "MinEmoteTriggerMinutes",
        "MaxEmoteTriggerMinutes",
        "EmoteDuration",
    ]
    _load_to_class(emote_config, EmotePreferences, required, [])


def _load_hotspot_config(sprite_config: dict):
    required = [
        "TopHotspotHeight",
        "TopHotspotWidth",
        "SideHotspotHeight",
        "SideHotspotWidth",
    ]
    _load_to_class(sprite_config, HotspotSettings, required, [])


"""
@! ---- Specifies how spritesheets & sounds are parsed and loaded ----------------------------------
"""


def _load_sprite_properties(char: str, sprite_config: dict):
    required = [
        "FrameRate",
        "SpriteColumn",
        "FrameHeight",
        "FrameWidth",
        "HasReloadAnimation",
    ]
    _load_to_class(sprite_config, SpriteProperties, required, [])


def _load_sprite_resource(char: str, sprite_config: dict, frame_config: dict):
    # check if this character has shooting animation
    ResourceRegistry.has_reload = sprite_config.get("HasReloadAnimation", False)

    # spritesheets for these states can be null
    nullable = []
    if not ResourceRegistry.has_reload:
        nullable = [
            State.LEFT_ACTION,
            State.RIGHT_ACTION,
            State.RELOAD,
        ]

    # function for registering animation data
    def register(state: State):
        state_key = to_pascal_case(state)
        sprite_name = sprite_config[state_key]
        
        # Skip if sprite name is empty (e.g. character missing optional animations)
        if not sprite_name:
            return

        sprite_path = _get_char_file(char, ResourceType.SPRITESHEET, sprite_name)
        sprite_frames = frame_config[state_key]
        ResourceRegistry.animations[(state, Direction.NONE)] = AnimationData(
            sprite_path=sprite_path, frame_count=sprite_frames, current_frame=0
        )

    # function for registering animation data if available
    def register_if_exists(state: State):
        try:
            register(state)
        except (KeyError, FileNotFoundError):
            pass

    # function for registering walking animations
    def register_walking_animations():
        for direction in Direction:
            if direction == Direction.NONE:
                continue
            key = to_pascal_case(direction)
            sprite_name = sprite_config[key]
            
            if not sprite_name:
                continue

            sprite_path = _get_char_file(char, ResourceType.SPRITESHEET, sprite_name)
            sprite_frames = frame_config[key]
            ResourceRegistry.animations[(State.WALK, direction)] = AnimationData(
                sprite_path=sprite_path, frame_count=sprite_frames, current_frame=0
            )

    # find spritesheet for every state
    for state in State:
        if state in nullable:
            register_if_exists(state)
        elif state == State.WALK:
            register_walking_animations()
        else:
            register(state)


def _load_sound_resource(char: str, sound_config: dict):
    # every sound resource is optional
    for state in State:
        state_key = to_pascal_case(state)
        try:
            sound_name = sound_config[state_key]
            sound_path = _get_char_file(char, ResourceType.SOUND, sound_name)
            ResourceRegistry.sounds[state] = SoundData(
                sound_path=sound_path, last_played=datetime.datetime.now()
            )
        except (KeyError, FileNotFoundError):
            pass
