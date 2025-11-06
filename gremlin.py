
import sys
import os
import datetime
import random
from PySide6.QtWidgets import (
    QWidget, QLabel, QSystemTrayIcon, QMenu, QApplication
)
from PySide6.QtCore import Qt, QTimer, QRect, QUrl
from PySide6.QtGui import QIcon, QAction
from PySide6.QtMultimedia import QSoundEffect

import settings
import sprite_manager
from hotspot_geometry import compute_top_hotspot_geometry
from movement_handler import MovementHandler, reset_all_walk_frames
from settings import State


class GremlinWindow(QWidget):

    def __init__(self):
        super().__init__()

        # --- @! Window Setup ------------------------------------------------------------
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(
            settings.Settings.FrameWidth,
            settings.Settings.FrameHeight
        )

        # --- @! Main Sprite Display -----------------------------------------------------
        self.sprite_label = QLabel(self)
        self.sprite_label.setGeometry(
            0, 0, settings.Settings.FrameWidth, settings.Settings.FrameHeight)
        self.sprite_label.setScaledContents(True)

        # --- @! Hotspots ----------------------------------------------------------------
        self.left_hotspot = QWidget(self)
        self.left_hotspot.setGeometry(*compute_top_hotspot_geometry())
        self.left_hotspot.mousePressEvent = self.top_hotspot_click

        # --- @! Sound Player ------------------------------------------------------------
        self.sound_player = QSoundEffect(self)
        self.sound_player.setVolume(0.8)

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
        self.current_state = State.INTRO
        self.drag_pos = None

        if settings.EmoteConfig.AnnoyEmote:
            # start the emote timer if the user want to be occasionally annoyed :)
            self.reset_emote_timer()

        # --- @! Start -------------------------------------------------------------------
        self.setup_tray_icon()
        self.play_sound("intro.wav")
        self.master_timer.start(1000 // settings.SpriteMap.FrameRate)
        self.idle_timer.start(120 * 1000)

    # --- @! State Machine Core ----------------------------------------------------------

    def set_state(self, new_state: State):
        """
        Handles animation entries. Normally, it would play some sound effects, reset
        frame counters, and reset timers.

        !TODO: So far there are only two animations that ends on timeout, not on frame
        completion. These are the WALK_IDLE (2 seconds) and EMOTE (configurable). When
        KurtVelasco created the original Desktop Gremlin, he did not design it to have
        such animations; thus, when I added them, their state management seems out of
        place compared to the other states. Soon, I will refactor the state machine to
        have a more uniform way of handling such states.
        """

        # only triggers on state change, does nothing otherwise
        if self.current_state == new_state:
            return

        # --- @! handle timers on state exit ---------------------------------------------
        # if we are leaving the WALK_IDLE state, stop the timer so it doesn't fire.
        if self.current_state == State.WALK_IDLE:
            self.walk_idle_timer.stop()

        # if we are leaving the EMOTE state, stop the duration timer
        if self.current_state == State.EMOTE:
            self.emote_duration_timer.stop()

        # --- @! handle SFX on state entry -----------------------------------------------
        match new_state:
            case State.DRAGGING:
                self.play_sound("grab.wav")
            case State.WALKING:
                if self.current_state != State.WALKING:
                    self.play_sound("run.wav")
            case State.WALK_IDLE:
                self.walk_idle_timer.start(2000)
            case State.CLICK:
                self.play_sound("mambo.wav")
            case State.PAT:
                self.play_sound("pat.wav")
            case State.EMOTE:
                self.play_sound("emote.wav")
                emote_duration = settings.EmoteConfig.EmoteDuration
                self.emote_duration_timer.start(emote_duration)

        # --- @! finalize state change ---------------------------------------------------
        self.current_state = new_state
        self.reset_current_frames(new_state)

    def reset_current_frames(self, state: State):
        """ Resets the frame counter for the new state. """
        c = settings.CurrentFrames
        match state:
            case State.INTRO:
                c.Intro = 0
            case State.IDLE:
                c.Idle = 0
            case State.WALK_IDLE:
                c.WalkIdle = 0
            case State.HOVER:
                c.Hover = 0
            case State.WALKING:
                reset_all_walk_frames()
            case State.DRAGGING:
                c.Grab = 0
            case State.CLICK:
                c.Click = 0
            case State.PAT:
                c.Pat = 0
            case State.EMOTE:
                c.Emote = 0
            case State.SLEEPING:
                c.Sleep = 0

    # --- @! Animations ------------------------------------------------------------------

    def play_animation(self, sheet, current_frame, frame_count):
        if sheet is None or frame_count == 0:
            return current_frame

        s = settings.Settings
        cols = settings.SpriteMap.SpriteColumn
        x = (current_frame % cols) * s.FrameWidth
        y = (current_frame // cols) * s.FrameHeight

        # check bounds
        if x + s.FrameWidth > sheet.width() or y + s.FrameHeight > sheet.height():
            print("Warning: Animation frame out of bounds.")
            return (current_frame + 1) % frame_count

        # create the cropped pixmap
        crop_rect = QRect(x, y, s.FrameWidth, s.FrameHeight)
        cropped_pixmap = sheet.copy(crop_rect)
        self.sprite_label.setPixmap(cropped_pixmap)

        return (current_frame + 1) % frame_count

    def animation_tick(self):
        """ Plays the animation for the current state. """
        c = settings.CurrentFrames
        f = settings.FrameCounts
        m = settings.SpriteMap

        match self.current_state:
            case State.INTRO:
                c.Intro = self.play_animation(
                    sprite_manager.get(m.Intro), c.Intro, f.Intro)
                if c.Intro == 0:
                    self.set_state(State.IDLE)

            case State.IDLE:
                c.Idle = self.play_animation(
                    sprite_manager.get(m.Idle), c.Idle, f.Idle)

            case State.HOVER:
                c.Hover = self.play_animation(
                    sprite_manager.get(m.Hover), c.Hover, f.Hover)

            case State.WALKING:
                self.handle_walking_animation_and_movement()

            case State.WALK_IDLE:
                c.WalkIdle = self.play_animation(
                    sprite_manager.get(m.WalkIdle), c.WalkIdle, f.WalkIdle)

            case State.DRAGGING:
                c.Grab = self.play_animation(
                    sprite_manager.get(m.Grab), c.Grab, f.Grab)

            case State.PAT:
                c.Pat = self.play_animation(
                    sprite_manager.get(m.Pat), c.Pat, f.Pat)
                if c.Pat == 0:
                    # transition to Hover or Idle when "pat" animation finishes
                    self.set_state(
                        State.HOVER if self.underMouse() else State.IDLE)

            case State.CLICK:
                c.Click = self.play_animation(
                    sprite_manager.get(m.Click), c.Click, f.Click)
                if c.Click == 0:
                    # transition to Hover or Idle when "click" animation finishes
                    self.set_state(
                        State.HOVER if self.underMouse() else State.IDLE)

            case State.SLEEPING:
                c.Sleep = self.play_animation(
                    sprite_manager.get(m.Sleep), c.Sleep, f.Sleep)

            case State.EMOTE:
                c.Emote = self.play_animation(
                    sprite_manager.get(m.Emote), c.Emote, f.Emote)

            case State.OUTRO:
                # this state is handled by outro_tick, but we stop master_timer
                # so this case is just a failsafe.
                pass

    def handle_walking_animation_and_movement(self):
        """ Helper function to keep animation_tick clean. """
        f = settings.FrameCounts
        c = settings.CurrentFrames

        direction = self.movement_handler.get_animation_direction()
        direction_sprite = getattr(settings.SpriteMap, direction, None)

        frame_count = getattr(f, direction, 0)
        prev_frame = getattr(c, direction, 0)
        next_frame = self.play_animation(
            sprite_manager.get(direction_sprite), prev_frame, frame_count)
        setattr(c, direction, next_frame)

        # apply the new position to the window
        dx, dy = self.movement_handler.getVelocity()
        if dx != 0 or dy != 0:
            self.move(self.pos().x() + dx, self.pos().y() + dy)

    def play_sound(self, file_name, delay_seconds=0):
        """ Plays a sound, respecting the LastPlayed delay. """
        path = os.path.join(
            settings.BASE_DIR, "sounds", settings.Settings.StartingChar.lower(), file_name)
        if not os.path.exists(path):
            return

        if delay_seconds > 0:
            last_time = settings.Settings.LastPlayed.get(file_name)
            if last_time:
                if (datetime.datetime.now() - last_time).total_seconds() < delay_seconds:
                    return

        try:
            self.sound_player.setSource(QUrl.fromLocalFile(path))
            self.sound_player.play()
            settings.Settings.LastPlayed[file_name] = datetime.datetime.now()
        except Exception as e:
            print(f"Sound error: {e}")

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

        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.outro_tick)
        self.close_timer.start(1000 // settings.SpriteMap.FrameRate)

    def closeEvent(self, event):
        event.ignore()
        self.close_app()

    # --- @! Timers Controls -------------------------------------------------------------

    def reset_idle_timer(self):
        """ Resets the idle timer and wakes the gremlin up if sleeping. """
        self.idle_timer.start(300 * 1000)
        if self.current_state == State.SLEEPING:
            self.set_state(State.IDLE)

    def idle_timer_tick(self):
        """ After being idle for a long enough time, go to sleep. """
        if self.current_state == State.IDLE:
            self.set_state(State.SLEEPING)

    def outro_tick(self):
        s = settings
        s.CurrentFrames.Outro = self.play_animation(
            sprite_manager.get(s.SpriteMap.Outro),
            s.CurrentFrames.Outro,
            s.FrameCounts.Outro
        )

        if s.CurrentFrames.Outro == 0:
            self.close_timer.stop()
            sys.exit(0)

    def on_walk_idle_finished(self):
        """ Called by the walk_idle_timer after 2 seconds. """
        # only transition if we are still in the WALK_IDLE state
        if self.current_state == State.WALK_IDLE:
            # transition to HOVER if mouse is over, otherwise IDLE
            if self.underMouse():
                self.set_state(State.HOVER)
            else:
                self.set_state(State.IDLE)

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
        """ Fires when the emote timer is up. """
        # only trigger if no active interaction is happening
        if self.current_state in [State.IDLE, State.HOVER, State.SLEEPING]:
            self.set_state(State.EMOTE)

        # reset the timer for the next emote
        self.reset_emote_timer()

    def on_emote_finished(self):
        """ Fired by emote_duration_timer. Transitions back to idle/hover. """
        if self.current_state == State.EMOTE:
            if self.underMouse():
                self.set_state(State.HOVER)
            else:
                self.set_state(State.IDLE)
            self.reset_idle_timer()

    # --- @! Event Handlers (Mouse) ------------------------------------------------------

    def mousePressEvent(self, event):
        # Temporarily disable mouse press when emoting...
        if self.current_state == State.EMOTE:
            return

        # ...otherwise, reset the idle timer. Since a click event is an interaction of
        # utmost care and love, we emote timer is also reset.
        self.reset_idle_timer()
        self.reset_emote_timer()

        # switch states based on mouse button
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_state not in [State.DRAGGING, State.PAT, State.CLICK]:
                self.set_state(State.DRAGGING)
                self.drag_pos = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            if self.current_state not in [State.DRAGGING, State.PAT, State.CLICK]:
                self.set_state(State.CLICK)

    def mouseMoveEvent(self, event):
        if (self.current_state == State.DRAGGING and
                event.buttons() == Qt.MouseButton.LeftButton):
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_state == State.DRAGGING:
                # transition to Hover or Idle when dropped
                self.set_state(State.HOVER if self.underMouse()
                               else State.IDLE)

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        # don't allow walking while in these blocking states
        if self.current_state in [State.DRAGGING, State.PAT, State.CLICK, State.SLEEPING, State.EMOTE]:
            return

        self.movement_handler.recordKeyPress(event)

        if self.movement_handler.is_moving():
            self.set_state(State.WALKING)
            self.reset_idle_timer()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return

        self.movement_handler.recordKeyRelease(event)

        # if we were walking and are no longer moving...
        if self.current_state == State.WALKING and not self.movement_handler.is_moving():
            # ...transition to WALK_IDLE
            self.set_state(State.WALK_IDLE)

    def enterEvent(self, event):
        self.setFocus()
        self.reset_idle_timer()
        if self.current_state == State.IDLE:
            self.set_state(State.HOVER)

        if self.current_state not in [State.WALKING, State.SLEEPING, State.CLICK, State.DRAGGING, State.EMOTE]:
            self.play_sound("hover.wav", 3)

    def leaveEvent(self, event):
        self.clearFocus()
        self.movement_handler.recordMouseLeave()    # stop all movement

        if self.current_state == State.WALKING:
            # if mouse leaves while walking, stop walking and go to WALK_IDLE
            self.set_state(State.WALK_IDLE)
        elif self.current_state == State.HOVER:
            # if mouse leaves while hovering, go to IDLE
            self.set_state(State.IDLE)
        # if in WALK_IDLE, do nothing. The timer will handle the transition.

    # --- @! Hotspot Click Handlers ------------------------------------------------------

    def top_hotspot_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_state not in [State.DRAGGING, State.CLICK, State.SLEEPING, State.EMOTE]:
                self.reset_idle_timer()
                self.set_state(State.PAT)

    def left_hotspot_click(self, event):
        pass  # firing removed

    def right_hotspot_click(self, event):
        pass  # firing removed
