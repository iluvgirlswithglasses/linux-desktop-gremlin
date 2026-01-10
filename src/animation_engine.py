from PySide6.QtCore import QRect
from PySide6.QtWidgets import QLabel

from . import settings, sprite_manager


class AnimationEngine:
    def __init__(self, sprite_label: QLabel):
        self.sprite_label = sprite_label

    def play_frame(self, sheet_name: str, current_frame: int, frame_count: int):
        sheet = sprite_manager.get(sheet_name)
        if sheet is None or frame_count == 0:
            return current_frame

        m = settings.SpriteMap
        x = (current_frame % m.SpriteColumn) * m.FrameWidth
        y = (current_frame // m.SpriteColumn) * m.FrameHeight

        rect = QRect(x, y, m.FrameWidth, m.FrameHeight)
        self.sprite_label.setPixmap(sheet.copy(rect))
        return (current_frame + 1) % frame_count
