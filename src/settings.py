class Preferences:
    """
    General application preferences.
    """

    # Why do I use "Matikanetannhauser" instead of "Mambo", you might ask?
    # Well, my name is iluvgirlswithglasses, what do you expect about my length preferences?
    StartingChar: str = "Matikanetannhauser"
    Systray: bool = False
    MoveSpeed: int = 5
    Volume: float = 0.8
    AudioDevice: str = "Default"
    EmoteKeyEnabled: bool = True
    EmoteKey: str = "P"
    IdleMinutes: int = 5  # minutes
    SleepMinutes: int = 5  # minutes


class EmotePreferences:
    """
    Preferences for Annoy Emote.
    If enabled, will casually annoy the user after a random interval.
    """

    AnnoyEmote: bool = True
    MinEmoteTriggerMinutes: int = 5  # in minutes
    MaxEmoteTriggerMinutes: int = 15  # in minutes
    EmoteDuration: int = 3600  # in milliseconds


class HotspotSettings:
    """
    Definition of hotspots where the user can right-click.
    """

    TopHotspotHeight: int = 0
    TopHotspotWidth: int = 0
    SideHotspotHeight: int = 0
    SideHotspotWidth: int = 0
