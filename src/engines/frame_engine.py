from PySide6.QtCore import QRect
from PySide6.QtWidgets import QLabel

from ..resources import ResourceRegistry, SpriteProperties
from ..states import Direction, State
from .sprite_engine import get_spritesheet


class FrameEngine:
    def __init__(self, qtlabel: QLabel):
        self.qtlabel = qtlabel

    def advance(self, state: State, direction: Direction = Direction.NONE) -> bool:
        """
        Advance the animation by one frame.
        Returns True if the animation has completed a full loop.
        """

        # fetch data
        frame_data = ResourceRegistry.animations[(state, direction)]
        sheet = get_spritesheet(frame_data.sprite_path)
        cur_frame = frame_data.current_frame
        num_frame = frame_data.frame_count

        # show next frame
        w = SpriteProperties.FrameWidth
        h = SpriteProperties.FrameHeight
        x = (cur_frame % SpriteProperties.SpriteColumn) * w
        y = (cur_frame // SpriteProperties.SpriteColumn) * h
        rect = QRect(x, y, w, h)
        self.qtlabel.setPixmap(sheet.copy(rect))

        # advance frame + loop back if needed
        frame_data.current_frame += 1
        if frame_data.current_frame >= num_frame:
            frame_data.current_frame = 0

        # return true if playing completed a full loop
        return frame_data.current_frame == 0
