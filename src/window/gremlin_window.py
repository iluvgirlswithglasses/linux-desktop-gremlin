import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from .. import resources
from ..engines import FrameEngine, SoundEngine
from ..fsm.animation_ticker import AnimationTicker
from ..fsm.state_manager import StateManager
from ..fsm.timer_manager import TimerManager
from ..fsm.walk_manager import WalkManager
from ..settings import Preferences
from ..states import State
from .hotspot_manager import HotspotManager
from .hover_manager import HoverManager
from .input_filter import WindowInputFilter
from .keyboard_manager import KeyboardManager
from .mouse_manager import MouseManager
from .systray_icon import SystrayIcon


class GremlinWindow(QWidget):

    def __init__(self) -> None:
        super().__init__()

        # --- Window setup ---------------------------------------------------------------
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        scale = Preferences.Scale
        w = int(resources.SpriteProperties.FrameWidth * scale)
        h = int(resources.SpriteProperties.FrameHeight * scale)
        self.setFixedSize(w, h)
        self.setWindowTitle("ilgwg_desktop_gremlins.py")

        # --- Sprite label ---------------------------------------------------------------
        self.sprite_label = QLabel(self)
        self.sprite_label.setGeometry(0, 0, w, h)
        self.sprite_label.setScaledContents(True)

        # --- Core logic components ------------------------------------------------------
        self.frame_engine = FrameEngine(self.sprite_label)
        self.sound_engine = SoundEngine(self)
        self.walk_manager = WalkManager()
        self.state_manager = StateManager(
            self.sound_engine, self.underMouse, self._on_exit
        )
        self.animation_ticker = AnimationTicker(
            self.state_manager, self.frame_engine, self._update_position
        )
        self.timer_manager = TimerManager(self.state_manager, self.animation_ticker)

        # --- Input managers (no event-slot assignment) ----------------------------------
        self.mouse_manager = MouseManager(self.state_manager, self.timer_manager, self)
        self.keyboard_manager = KeyboardManager(
            self.state_manager, self.walk_manager, self.timer_manager
        )
        self.hover_manager = HoverManager(
            self.walk_manager, self.state_manager, self.timer_manager, self
        )
        self.hotspot_manager = HotspotManager(
            self.state_manager, self.timer_manager, self.mouse_manager, self
        )

        # --- Centralised event filter ---------------------------------------------------
        self.input_filter = WindowInputFilter(self)
        self.input_filter.register_mouse(self.mouse_manager)
        self.input_filter.register_keyboard(self.keyboard_manager)
        self.input_filter.register_hover(self.hover_manager)
        self.installEventFilter(self.input_filter)

        # --- Systray + start ------------------------------------------------------------
        self.systray_icon = SystrayIcon(self, self.close_app)
        self._closing = False

        self.state_manager.transition_to(State.INTRO)
        self.timer_manager.start_passive_timer()

    def _update_position(self) -> None:
        dx, dy = self.walk_manager.get_velocity()
        if dx != 0 or dy != 0:
            self.move(self.pos().x() + dx, self.pos().y() + dy)

    def _on_exit(self) -> None:
        self.timer_manager.stop_all()
        QApplication.quit()
        sys.exit(0)  # without this, the app freezes on some platforms (like mine)

    def close_app(self) -> None:
        if self._closing:
            return
        self._closing = True
        self.state_manager.transition_to(State.OUTRO)
        self.input_filter.unregister_all()

    def closeEvent(self, event) -> None:
        event.ignore()
        self.close_app()
