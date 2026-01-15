from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget

from .. import resources
from ..engines import FrameEngine, SoundEngine
from ..fsm.animation_ticker import AnimationTicker
from ..fsm.state_manager import StateManager
from ..fsm.timer_manager import TimerManager
from ..fsm.walk_manager import WalkManager
from ..states import State
from .hotspot_manager import HotspotManager
from .hover_manager import HoverManager
from .keyboard_manager import KeyboardManager
from .mouse_manager import MouseManager
from .systray_icon import SystrayIcon


class GremlinWindow(QWidget):

    def __init__(self):
        super().__init__()

        # --- @! Window Setup ------------------------------------------------------------
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(
            resources.SpriteProperties.FrameWidth,
            resources.SpriteProperties.FrameHeight,
        )
        self.setWindowTitle("ilgwg_desktop_gremlins.py")

        # --- @! Main Sprite Display -----------------------------------------------------
        self.sprite_label = QLabel(self)
        self.sprite_label.setGeometry(
            0,
            0,
            resources.SpriteProperties.FrameWidth,
            resources.SpriteProperties.FrameHeight,
        )
        self.sprite_label.setScaledContents(True)

        # --- @! Logic Components --------------------------------------------------------
        self.frame_engine = FrameEngine(self.sprite_label)
        self.sound_engine = SoundEngine(self)

        self.walk_manager = WalkManager()
        self.state_manager = StateManager(self.sound_engine, self.underMouse)

        self.animation_ticker = AnimationTicker(
            self.state_manager, self.frame_engine, self.update_position_by_walking
        )
        self.timer_manager = TimerManager(
            self, self.state_manager, self.animation_ticker
        )

        # --- @! Extend Window Functionalities -------------------------------------------
        self.mouse_manager = MouseManager(self.state_manager, self.timer_manager, self)
        self.hotspot_manager = HotspotManager(
            self.state_manager, self.timer_manager, self
        )
        self.hover_manager = HoverManager(
            self.walk_manager, self.state_manager, self.timer_manager, self
        )
        self.keyboard_manager = KeyboardManager(
            self.state_manager, self.walk_manager, self.timer_manager, self
        )
        self.systray_icon = SystrayIcon(self, self.close_app)

        # --- @! Start -------------------------------------------------------------------
        self.state_manager.transition_to(State.INTRO)
        self.timer_manager.start_passive_timer()

    def update_position_by_walking(self):
        dx, dy = self.walk_manager.get_velocity()
        if dx != 0 or dy != 0:
            self.move(self.pos().x() + dx, self.pos().y() + dy)

    def close_app(self):
        # play outro
        self.state_manager.transition_to(State.OUTRO)

        # unplug all inputs to prevent further actions
        self.keyPressEvent = lambda _: None
        self.keyReleaseEvent = lambda _: None
        self.mousePressEvent = lambda _: None
        self.mouseReleaseEvent = lambda _: None
        self.enterEvent = lambda _: None
        self.leaveEvent = lambda _: None

    def closeEvent(self, event):
        event.ignore()
        self.close_app()
