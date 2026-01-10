import datetime
import os

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QWidget

from . import settings


class AudioEngine:
    def __init__(self, parent: QWidget):
        self.player = QSoundEffect(parent)
        self.player.setVolume(settings.Settings.Volume)

    def play(self, file_name: str, delay_seconds=0):
        """Plays a sound, respecting the LastPlayed delay."""
        path = os.path.join(
            settings.BASE_DIR,
            "sounds",
            settings.Settings.StartingChar.lower(),
            file_name,
        )
        if not os.path.exists(path) or os.path.isdir(path):
            return

        if delay_seconds > 0:
            last_time = settings.Settings.LastPlayed.get(file_name)
            if last_time:
                if (
                    datetime.datetime.now() - last_time
                ).total_seconds() < delay_seconds:
                    return

        try:
            self.player.setSource(QUrl.fromLocalFile(path))
            self.player.play()
            settings.Settings.LastPlayed[file_name] = datetime.datetime.now()
        except Exception as e:
            print(f"Sound error: {e}")
