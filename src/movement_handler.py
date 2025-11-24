
from PySide6.QtCore import Qt
import sys
import string
from . import settings


def reset_all_walk_frames():
    c = settings.CurrentFrames
    c.Up = c.Down = c.Left = c.Right = 0
    c.UpLeft = c.UpRight = c.DownLeft = c.DownRight = 0


class MovementHandler:
    def __init__(self):
        self.w = False
        self.a = False
        self.s = False
        self.d = False
        self.emotekey = False
        self.v = settings.Settings.MoveSpeed

        # resolution for Qt key code (resolves to defualt "P" if unset / wrong)
        self.emote_key_code: str | None = None
        self.default_emotekey: int = int(Qt.Key.Key_P)
        self.resolve_emotekey()

    def getVelocity(self) -> tuple[int, int]:
        """
        Returns the velocity vector based on the current key states.
        If both keys in a direction are pressed, they cancel each other out.
        """
        vy = 0
        vx = 0
        if self.w ^ self.s:
            vy = -self.v if self.w else self.v
        if self.a ^ self.d:
            vx = -self.v if self.a else self.v
        return vx, vy

    def is_moving(self) -> bool:
        """
        Returns True if either vertical or horizontal movement is occurring.
        """
        return (self.w ^ self.s) or (self.a ^ self.d)

    def get_animation_direction(self) -> str | None:
        """
        Returns a string representing the current movement direction for animation purposes.
        """
        vertical = ""
        horizontal = ""
        if self.w ^ self.s:
            vertical = "Up" if self.w else "Down"
        if self.a ^ self.d:
            horizontal = "Left" if self.a else "Right"
        return vertical + horizontal

    def resolve_emotekey(self) -> None:
        """
        Returns the value of the emotekey to use
        The reasoning is that, if "Qt.Key.Key_<CHAR>" is always built like this,
        it is possible to extract the alphabetical character from the config file
        and build the type using the character inputted in the config

        Limitations:
        - Assumes emotkey is true, gets checked in the main gremlin.py
        - Assumes that the user will input a valid alphabetic char, the ones
        that are on every qwerty keyboard. Things like pageDwn or other special
        keys are ignored for the sake of simplicity
        """

        key = settings.Settings.EmoteKey
        try:
            # forces single character key
            if not isinstance(key, str) or len(key) != 1:
                print(f"\n[Warning] EmoteKey invalid or not a single char ({key!r}); using default 'P'")
                self.emote_key_code = self.default_emotekey
                return

            # limits to qwerty alphanumerical chars and digits 0-9
            char = key.strip().upper()
            if char not in string.ascii_uppercase + string.digits:
                print(f"\n[Warning] EmoteKey {key!r} not allowed (allowed: A-Z, 0-9); using default 'P'")
                self.emote_key_code = self.default_emotekey
                return

            self.emote_key_code = ord(char)
        except Exception as e:
            print(f"[Error] Failed to resolve EmoteKey from settings: {e!r}.", file=sys.stderr)
            self.emote_key_code = self.default_emotekey
    
    def is_emotekey_pressed(self) -> bool:
        return self.emotekey

    # --- @! event recorders -------------------------------------------------------------

    def recordKeyPress(self, event):
        key = event.key()
        match key:
            case Qt.Key.Key_W:
                self.w = True
            case Qt.Key.Key_A:
                self.a = True
            case Qt.Key.Key_S:
                self.s = True
            case Qt.Key.Key_D:
                self.d = True
            case _:
                pass
        
        # handles the emote keypress
        if self.emote_key_code is not None and key == self.emote_key_code:
            self.emotekey = True

    def recordKeyRelease(self, event):
        key = event.key()
        match key:
            case Qt.Key.Key_W:
                self.w = False
            case Qt.Key.Key_A:
                self.a = False
            case Qt.Key.Key_S:
                self.s = False
            case Qt.Key.Key_D:
                self.d = False
            case _:
                pass
        
        if self.emote_key_code is not None and key == self.emote_key_code:
            self.emotekey = False

    def recordMouseLeave(self):
        self.w = False
        self.a = False
        self.s = False
        self.d = False
        self.emotekey = False
