import os
import random
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QLabel, QMenu, QSystemTrayIcon, QWidget

from . import settings
from .animation_engine import AnimationEngine
from .audio_engine import AudioEngine
from .hotspot_geometry import (
    compute_left_hotspot_geometry,
    compute_right_hotspot_geometry,
    compute_top_hotspot_geometry,
)
from .movement_handler import MovementHandler
from .settings import State
from .state_manager import AnimationStateManager


class GremlinWindow(QWidget):

    def __init__(self):
        super().__init__()

        # --- @! Window Setup ------------------------------------------------------------
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(settings.SpriteMap.FrameWidth, settings.SpriteMap.FrameHeight)

        # Set window title
        self.setWindowTitle("ilgwg_desktop_gremlins.py")

        # --- @! Main Sprite Display -----------------------------------------------------
        self.sprite_label = QLabel(self)
        self.sprite_label.setGeometry(
            0, 0, settings.SpriteMap.FrameWidth, settings.SpriteMap.FrameHeight
        )
        self.sprite_label.setScaledContents(True)

        # --- @! Hotspots ----------------------------------------------------------------
        self.top_hotspot = QWidget(self)
        self.top_hotspot.setGeometry(*compute_top_hotspot_geometry())
        self.top_hotspot.mousePressEvent = self.top_hotspot_click

        self.left_hotspot = QWidget(self)
        self.left_hotspot.setGeometry(*compute_left_hotspot_geometry())
        self.left_hotspot.mousePressEvent = self.left_hotspot_click

        self.right_hotspot = QWidget(self)
        self.right_hotspot.setGeometry(*compute_right_hotspot_geometry())
        self.right_hotspot.mousePressEvent = self.right_hotspot_click

        # --- @! Reload animation for Blue Archive gremlins ------------------------------
        self.has_reload = settings.SpriteMap.HasReloadAnimation
        if self.has_reload:
            self.ammo = 6

        # --- @! SFX and VFX engines -----------------------------------------------------
        self.animation_engine = AnimationEngine(self.sprite_label)
        self.sound_engine = AudioEngine(self)

        # --- @! Timers ------------------------------------------------------------------
        self.master_timer = QTimer(self)
        self.master_timer.timeout.connect(self.animation_tick)

        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.idle_timer_tick)

        self.walk_idle_timer = QTimer(self)
        self.walk_idle_timer.setSingleShot(True)
        self.walk_idle_timer.timeout.connect(self.on_walk_idle_finished)

        self.emote_timer = QTimer(self)
        self.emote_timer.timeout.connect(self.emote_timer_tick)

        self.emote_duration_timer = QTimer(self)
        self.emote_duration_timer.setSingleShot(True)
        self.emote_duration_timer.timeout.connect(self.on_emote_finished)

        self.close_timer = None

        # --- @! State Management --------------------------------------------------------
        self.movement_handler = MovementHandler()
        self.state_manager = AnimationStateManager(self)
        self.drag_pos = None

        if settings.EmoteConfig.AnnoyEmote:
            # start the emote timer if the user want to be occasionally annoyed :)
            self.reset_emote_timer()

        # --- @! Start -------------------------------------------------------------------
        self.setup_tray_icon()
        self.sound_engine.play(settings.SfxMap.Intro)
        self.master_timer.start(1000 // settings.SpriteMap.FrameRate)
        self.idle_timer.start(120 * 1000)

    # --- @! Animations ------------------------------------------------------------------

    def animation_tick(self):
        """Plays the animation for the current state."""
        c = settings.CurrentFrames
        f = settings.FrameCounts
        m = settings.SpriteMap

        match self.state_manager.cur_state:
            case State.INTRO:
                c.Intro = self.animation_engine.play_frame(m.Intro, c.Intro, f.Intro)
                if c.Intro == 0:
                    self.state_manager.transition_to(State.IDLE)

            case State.IDLE:
                c.Idle = self.animation_engine.play_frame(m.Idle, c.Idle, f.Idle)

            case State.HOVER:
                c.Hover = self.animation_engine.play_frame(m.Hover, c.Hover, f.Hover)

            case State.WALK:
                self.handle_walking_animation_and_movement()

            case State.WALK_IDLE:
                c.WalkIdle = self.animation_engine.play_frame(
                    m.WalkIdle, c.WalkIdle, f.WalkIdle
                )

            case State.GRAB:
                c.Grab = self.animation_engine.play_frame(m.Grab, c.Grab, f.Grab)

            case State.PAT:
                c.Pat = self.animation_engine.play_frame(m.Pat, c.Pat, f.Pat)
                if c.Pat == 0:
                    # transition to Hover or Idle when "pat" animation finishes
                    self.state_manager.transition_to(
                        State.HOVER if self.underMouse() else State.IDLE
                    )

            case State.POKE:
                c.Poke = self.animation_engine.play_frame(m.Poke, c.Poke, f.Poke)
                if c.Poke == 0:
                    # transition to Hover or Idle when "poke" animation finishes
                    self.state_manager.transition_to(
                        State.HOVER if self.underMouse() else State.IDLE
                    )

            case State.SLEEP:
                c.Sleep = self.animation_engine.play_frame(m.Sleep, c.Sleep, f.Sleep)

            case State.EMOTE:
                c.Emote = self.animation_engine.play_frame(m.Emote, c.Emote, f.Emote)

            case State.LEFT_ACTION:
                if not self.has_reload or self.ammo >= 0:
                    c.LeftAction = self.animation_engine.play_frame(
                        m.LeftAction, c.LeftAction, f.LeftAction
                    )
                if c.LeftAction == 0:
                    self.state_manager.check_reload(self.underMouse())

            case State.RIGHT_ACTION:
                if not self.has_reload or self.ammo >= 0:
                    c.RightAction = self.animation_engine.play_frame(
                        m.RightAction, c.RightAction, f.RightAction
                    )
                if c.RightAction == 0:
                    self.state_manager.check_reload(self.underMouse())

            case State.RELOAD:
                c.Reload = self.animation_engine.play_frame(
                    m.Reload, c.Reload, f.Reload
                )
                if c.Reload == 0:
                    next_state = State.HOVER if self.underMouse() else State.IDLE
                    self.state_manager.transition_to(next_state)

            case State.OUTRO:
                # this state is handled by outro_tick, but we stop master_timer
                # so this case is just a failsafe.
                pass

    def handle_walking_animation_and_movement(self):
        """Helper function to keep animation_tick clean."""
        f = settings.FrameCounts
        c = settings.CurrentFrames

        direction = self.movement_handler.get_animation_direction()
        direction_sprite = getattr(settings.SpriteMap, direction, None)

        frame_count = getattr(f, direction, 0)
        prev_frame = getattr(c, direction, 0)
        next_frame = self.animation_engine.play_frame(
            direction_sprite, prev_frame, frame_count
        )
        setattr(c, direction, next_frame)

        # apply the new position to the window
        dx, dy = self.movement_handler.getVelocity()
        if dx != 0 or dy != 0:
            self.move(self.pos().x() + dx, self.pos().y() + dy)

    # --- @! System Tray and App Lifecycle ---------------------------------------------------------

    def setup_tray_icon(self):
        if not settings.Settings.Systray:
            return
        self.tray_icon = QSystemTrayIcon(self)

        icon_path = os.path.join(settings.BASE_DIR, "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(settings.BASE_DIR, "icon.png")

        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("applications-games"))

        self.tray_icon.setToolTip("Gremlin")

        menu = QMenu()
        menu.addSeparator()

        reappear_action = QAction("Reappear", self)
        reappear_action.triggered.connect(self.reset_app)
        menu.addAction(reappear_action)

        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close_app)
        menu.addAction(close_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def reset_app(self):
        if settings.Settings.Systray:
            self.tray_icon.hide()
        QApplication.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def close_app(self):
        self.master_timer.stop()
        self.idle_timer.stop()

        if settings.Settings.Systray:
            self.tray_icon.hide()

        # correctly sets the outro state to fix some audio issues
        self.state_manager.transition_to(State.OUTRO)

        # here should be played the outro sound
        self.sound_engine.play(settings.SfxMap.Outro)

        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.outro_tick)
        self.close_timer.start(1000 // settings.SpriteMap.FrameRate)

    def closeEvent(self, event):
        event.ignore()
        self.close_app()

    # --- @! Timers Controls -------------------------------------------------------------

    def reset_idle_timer(self):
        """Resets the idle timer and wakes the gremlin up if sleeping."""
        self.idle_timer.start(300 * 1000)
        if self.state_manager.cur_state == State.SLEEP:
            self.state_manager.transition_to(State.IDLE)

    def idle_timer_tick(self):
        """After being idle for a long enough time, go to sleep."""
        if self.state_manager.cur_state == State.IDLE:
            self.state_manager.transition_to(State.SLEEP)

    def outro_tick(self):
        s = settings
        s.CurrentFrames.Outro = self.animation_engine.play_frame(
            s.SpriteMap.Outro,
            s.CurrentFrames.Outro,
            s.FrameCounts.Outro,
        )

        if s.CurrentFrames.Outro == 0:
            self.close_timer.stop()
            sys.exit(0)

    def on_walk_idle_finished(self):
        """Called by the walk_idle_timer after 2 seconds."""
        # only transition if we are still in the WALK_IDLE state
        if self.state_manager.cur_state == State.WALK_IDLE:
            # transition to HOVER if mouse is over, otherwise IDLE
            if self.underMouse():
                self.state_manager.transition_to(State.HOVER)
            else:
                self.state_manager.transition_to(State.IDLE)

    def reset_emote_timer(self):
        """
        Sets the emote timer to a new random interval.
        You will have your silence occasionally broken up by Mambo :)
        """
        try:
            min_ms = settings.EmoteConfig.MinEmoteTriggerMinutes * 60000
            max_ms = settings.EmoteConfig.MaxEmoteTriggerMinutes * 60000

            if min_ms <= 0 or max_ms <= 0 or max_ms < min_ms:
                print("Warning: Invalid emote timer settings. Disabling emote timer.")
                self.emote_timer.stop()
                return

            interval = random.randint(min_ms, max_ms)
            self.emote_timer.start(interval)
        except Exception as e:
            print(f"Warning: Could not set emote timer. Error: {e}")
            self.emote_timer.stop()

    def emote_timer_tick(self):
        """Fires when the emote timer is up."""
        # only trigger if no active interaction is happening
        if self.state_manager.cur_state in [State.IDLE, State.HOVER, State.SLEEP]:
            self.state_manager.transition_to(State.EMOTE)

        # reset the timer for the next emote
        self.reset_emote_timer()

    def on_emote_finished(self):
        """Fired by emote_duration_timer. Transitions back to idle/hover."""
        if self.state_manager.cur_state == State.EMOTE:
            if self.underMouse():
                self.state_manager.transition_to(State.HOVER)
            else:
                self.state_manager.transition_to(State.IDLE)
            self.reset_idle_timer()

    # --- @! Event Handlers (Mouse) ------------------------------------------------------

    def mousePressEvent(self, event):
        # Temporarily disable mouse press when emoting and while the character is playing the outro
        if self.state_manager.cur_state in [State.EMOTE, State.OUTRO]:
            return

        # ...otherwise, reset the idle timer. Since a click event is an interaction of
        # utmost care and love, we emote timer is also reset.
        self.reset_idle_timer()
        self.reset_emote_timer()

        # switch states based on mouse button
        if event.button() == Qt.MouseButton.LeftButton:
            if self.state_manager.cur_state not in [State.GRAB, State.PAT, State.POKE]:
                self.state_manager.transition_to(State.GRAB)
                self.drag_pos = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            if self.state_manager.cur_state not in [State.GRAB, State.PAT, State.POKE]:
                self.state_manager.transition_to(State.POKE)

    def mouseMoveEvent(self, event):
        if (
            self.state_manager.cur_state == State.GRAB
            and event.buttons() == Qt.MouseButton.LeftButton
        ):
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.state_manager.cur_state == State.GRAB:
                # transition to Hover or Idle when dropped
                self.state_manager.transition_to(
                    State.HOVER if self.underMouse() else State.IDLE
                )

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        # don't allow walking while in these blocking states
        if self.state_manager.cur_state in [
            State.GRAB,
            State.PAT,
            State.POKE,
            State.SLEEP,
            State.EMOTE,
        ]:
            return

        self.movement_handler.recordKeyPress(event)

        if (
            settings.Settings.EmoteKeyEnabled
            and self.movement_handler.is_emotekey_pressed()
        ):
            self.state_manager.transition_to(State.EMOTE)
            self.reset_emote_timer()

        if self.movement_handler.is_moving():
            self.state_manager.transition_to(State.WALK)
            self.reset_idle_timer()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return

        self.movement_handler.recordKeyRelease(event)

        # if we were walking and are no longer moving...
        if (
            self.state_manager.cur_state == State.WALK
            and not self.movement_handler.is_moving()
        ):
            # ...transition to WALK_IDLE
            self.state_manager.transition_to(State.WALK_IDLE)

    def enterEvent(self, event):
        self.setFocus()
        self.reset_idle_timer()
        if self.state_manager.cur_state == State.IDLE:
            self.state_manager.transition_to(State.HOVER)

        if self.state_manager.cur_state not in [
            State.WALK,
            State.GRAB,
            State.SLEEP,
            State.POKE,
            State.EMOTE,
            State.OUTRO,
        ]:
            self.sound_engine.play(settings.SfxMap.Hover, 3)

    def leaveEvent(self, event):
        self.clearFocus()
        self.movement_handler.recordMouseLeave()  # stop all movement

        if self.state_manager.cur_state == State.WALK:
            # if mouse leaves while walking, stop walking and go to WALK_IDLE
            self.state_manager.transition_to(State.WALK_IDLE)
        elif self.state_manager.cur_state == State.HOVER:
            # if mouse leaves while hovering, go to IDLE
            self.state_manager.transition_to(State.IDLE)
        # if in WALK_IDLE, do nothing. The timer will handle the transition.

    # --- @! Hotspot Click Handlers ------------------------------------------------------
    def on_hotspot_click(self, event, state):
        block_states = [State.GRAB, State.POKE, State.SLEEP, State.EMOTE, State.RELOAD]
        if event.button() == Qt.MouseButton.RightButton:
            if self.state_manager.cur_state not in block_states:
                self.reset_idle_timer()
                self.reset_emote_timer()
                self.state_manager.transition_to(state)
        elif event.button() == Qt.MouseButton.LeftButton:
            # pass left clicks to main handler
            self.mousePressEvent(event)

    def top_hotspot_click(self, event):
        self.on_hotspot_click(event, State.PAT)

    def left_hotspot_click(self, event):
        self.on_hotspot_click(event, State.LEFT_ACTION)

    def right_hotspot_click(self, event):
        self.on_hotspot_click(event, State.RIGHT_ACTION)
