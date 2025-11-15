
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
from hotspot_geometry import *
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
            settings.SpriteMap.FrameWidth,
            settings.SpriteMap.FrameHeight
        )

        # --- @! Main Sprite Display -----------------------------------------------------
        self.sprite_label = QLabel(self)
        self.sprite_label.setGeometry(
            0, 0, settings.SpriteMap.FrameWidth, settings.SpriteMap.FrameHeight)
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
        self.play_sound(settings.SfxMap.Intro)
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
        # except for shooting animations, which can be spammed
        if self.current_state == new_state:
            reshootable = (self.has_reload and
                           new_state in [State.LEFT_ACTION, State.RIGHT_ACTION] and
                           self.ammo > 0)
            if reshootable:
                c = max(settings.CurrentFrames.LeftAction,
                        settings.CurrentFrames.RightAction)
                f = min(settings.FrameCounts.LeftAction,
                        settings.FrameCounts.RightAction)
                # if still in the first quarter of the animation, block shooting again
                if c < f // 4:
                    return
                # otherwise, let her shoot
                pass
            else:
                return

        # --- @! handle timers on state exit ---------------------------------------------
        # except the intro and outro, all states with timers should stop them on exit
        match self.current_state:
            case State.WALK_IDLE:
                self.walk_idle_timer.stop()
            case State.EMOTE:
                self.emote_duration_timer.stop()

        # --- @! handle state entry ------------------------------------------------------
        match new_state:
            case State.GRAB:
                self.play_sound(settings.SfxMap.Grab)
            case State.WALK:
                if self.current_state != State.WALK:
                    self.play_sound(settings.SfxMap.Walk)
            case State.WALK_IDLE:
                self.walk_idle_timer.start(2000)
            case State.POKE:
                self.play_sound(settings.SfxMap.Poke)
            case State.PAT:
                self.play_sound(settings.SfxMap.Pat)
            case State.LEFT_ACTION:
                if self.has_reload and self.ammo > 0:
                    self.play_sound(settings.SfxMap.LeftAction)
                    self.ammo -= 1
            case State.RIGHT_ACTION:
                if self.has_reload and self.ammo > 0:
                    self.play_sound(settings.SfxMap.RightAction)
                    self.ammo -= 1
            case State.RELOAD:
                self.play_sound(settings.SfxMap.Reload)
                self.ammo = 6
            case State.EMOTE:
                self.play_sound(settings.SfxMap.Emote)
                emote_duration = settings.EmoteConfig.EmoteDuration
                self.emote_duration_timer.start(emote_duration)

        # --- @! finalize state change ---------------------------------------------------
        self.current_state = new_state
        self.reset_current_frames(new_state)

    def reset_current_frames(self, state: State):
        """ Resets the frame counter for the new state. """
        c = settings.CurrentFrames
        match state:
            case State.IDLE:
                c.Idle = 0
            case State.HOVER:
                c.Hover = 0
            case State.SLEEP:
                c.Sleep = 0
            case State.INTRO:
                c.Intro = 0
            case State.OUTRO:
                pass
            case State.GRAB:
                c.Grab = 0
            case State.WALK:
                reset_all_walk_frames()
            case State.WALK_IDLE:
                c.WalkIdle = 0
            case State.POKE:
                c.Poke = 0
            case State.PAT:
                c.Pat = 0
            case State.LEFT_ACTION:
                c.LeftAction = 0
            case State.RIGHT_ACTION:
                c.RightAction = 0
            case State.RELOAD:
                c.Reload = 0
            case State.EMOTE:
                c.Emote = 0

    # --- @! Animations ------------------------------------------------------------------

    def play_animation(self, sheet, current_frame, frame_count):
        if sheet is None or frame_count == 0:
            return current_frame

        m = settings.SpriteMap
        cols = m.SpriteColumn
        x = (current_frame % cols) * m.FrameWidth
        y = (current_frame // cols) * m.FrameHeight

        # check bounds
        if x + m.FrameWidth > sheet.width() or y + m.FrameHeight > sheet.height():
            print("Warning: Animation frame out of bounds.")
            return (current_frame + 1) % frame_count

        # create the cropped pixmap
        crop_rect = QRect(x, y, m.FrameWidth, m.FrameHeight)
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

            case State.WALK:
                self.handle_walking_animation_and_movement()

            case State.WALK_IDLE:
                c.WalkIdle = self.play_animation(
                    sprite_manager.get(m.WalkIdle), c.WalkIdle, f.WalkIdle)

            case State.GRAB:
                c.Grab = self.play_animation(
                    sprite_manager.get(m.Grab), c.Grab, f.Grab)

            case State.PAT:
                c.Pat = self.play_animation(
                    sprite_manager.get(m.Pat), c.Pat, f.Pat)
                if c.Pat == 0:
                    # transition to Hover or Idle when "pat" animation finishes
                    self.set_state(
                        State.HOVER if self.underMouse() else State.IDLE)

            case State.POKE:
                c.Poke = self.play_animation(
                    sprite_manager.get(m.Poke), c.Poke, f.Poke)
                if c.Poke == 0:
                    # transition to Hover or Idle when "poke" animation finishes
                    self.set_state(
                        State.HOVER if self.underMouse() else State.IDLE)

            case State.SLEEP:
                c.Sleep = self.play_animation(
                    sprite_manager.get(m.Sleep), c.Sleep, f.Sleep)

            case State.EMOTE:
                c.Emote = self.play_animation(
                    sprite_manager.get(m.Emote), c.Emote, f.Emote)

            case State.LEFT_ACTION:
                if not self.has_reload or self.ammo >= 0:
                    c.LeftAction = self.play_animation(
                        sprite_manager.get(m.LeftAction), c.LeftAction, f.LeftAction)
                if c.LeftAction == 0:
                    self.handle_reload_check()

            case State.RIGHT_ACTION:
                if not self.has_reload or self.ammo >= 0:
                    c.RightAction = self.play_animation(
                        sprite_manager.get(m.RightAction), c.RightAction, f.RightAction)
                if c.RightAction == 0:
                    self.handle_reload_check()

            case State.RELOAD:
                c.Reload = self.play_animation(
                    sprite_manager.get(m.Reload), c.Reload, f.Reload)
                if c.Reload == 0:
                    next_state = State.HOVER if self.underMouse() else State.IDLE
                    self.set_state(next_state)

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

    def handle_reload_check(self):
        """ Checks if we need to reload after a left/right action. """
        if self.has_reload and self.ammo <= 0:
            self.set_state(State.RELOAD)
        else:
            self.set_state(State.HOVER if self.underMouse() else State.IDLE)

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
        if self.current_state == State.SLEEP:
            self.set_state(State.IDLE)

    def idle_timer_tick(self):
        """ After being idle for a long enough time, go to sleep. """
        if self.current_state == State.IDLE:
            self.set_state(State.SLEEP)

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
        if self.current_state in [State.IDLE, State.HOVER, State.SLEEP]:
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
            if self.current_state not in [State.GRAB, State.PAT, State.POKE]:
                self.set_state(State.GRAB)
                self.drag_pos = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            if self.current_state not in [State.GRAB, State.PAT, State.POKE]:
                self.set_state(State.POKE)

    def mouseMoveEvent(self, event):
        if (self.current_state == State.GRAB and
                event.buttons() == Qt.MouseButton.LeftButton):
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_state == State.GRAB:
                # transition to Hover or Idle when dropped
                self.set_state(State.HOVER if self.underMouse()
                               else State.IDLE)

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        # don't allow walking while in these blocking states
        if self.current_state in [State.GRAB, State.PAT, State.POKE, State.SLEEP, State.EMOTE]:
            return

        self.movement_handler.recordKeyPress(event)

        if self.movement_handler.is_moving():
            self.set_state(State.WALK)
            self.reset_idle_timer()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return

        self.movement_handler.recordKeyRelease(event)

        # if we were walking and are no longer moving...
        if self.current_state == State.WALK and not self.movement_handler.is_moving():
            # ...transition to WALK_IDLE
            self.set_state(State.WALK_IDLE)

    def enterEvent(self, event):
        self.setFocus()
        self.reset_idle_timer()
        if self.current_state == State.IDLE:
            self.set_state(State.HOVER)

        if self.current_state not in [State.WALK, State.GRAB, State.SLEEP, State.POKE, State.EMOTE]:
            self.play_sound(settings.SfxMap.Hover, 3)

    def leaveEvent(self, event):
        self.clearFocus()
        self.movement_handler.recordMouseLeave()    # stop all movement

        if self.current_state == State.WALK:
            # if mouse leaves while walking, stop walking and go to WALK_IDLE
            self.set_state(State.WALK_IDLE)
        elif self.current_state == State.HOVER:
            # if mouse leaves while hovering, go to IDLE
            self.set_state(State.IDLE)
        # if in WALK_IDLE, do nothing. The timer will handle the transition.

    # --- @! Hotspot Click Handlers ------------------------------------------------------
    def on_hotspot_click(self, event, state):
        block_states = [
            State.GRAB, State.POKE, State.SLEEP, State.EMOTE, State.RELOAD
        ]
        if event.button() == Qt.MouseButton.RightButton:
            if self.current_state not in block_states:
                self.reset_idle_timer()
                self.reset_emote_timer()
                self.set_state(state)
        elif event.button() == Qt.MouseButton.LeftButton:
            # pass left clicks to main handler
            self.mousePressEvent(event)

    def top_hotspot_click(self, event):
        self.on_hotspot_click(event, State.PAT)

    def left_hotspot_click(self, event):
        self.on_hotspot_click(event, State.LEFT_ACTION)

    def right_hotspot_click(self, event):
        self.on_hotspot_click(event, State.RIGHT_ACTION)
