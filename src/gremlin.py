import datetime
import gc
import os
import random
import sys

from PySide6.QtCore import QRect, Qt, QTimer, QUrl
from PySide6.QtGui import (QAction, QIcon, QPainter,  # <-- ADDED QPixmapCache
                           QPixmap, QPixmapCache)
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget

from . import settings, sprite_manager
from .hotspot_geometry import (compute_left_hotspot_geometry,
                               compute_right_hotspot_geometry,
                               compute_top_hotspot_geometry)
from .movement_handler import MovementHandler, reset_all_walk_frames
from .settings import State


class GremlinWindow(QWidget):
    def __init__(self):
        super().__init__()

        # --- @! Window Setup ------------------------------------------------------------
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(settings.SpriteMap.FrameWidth, settings.SpriteMap.FrameHeight)
        self.setWindowTitle("ilgwg_desktop_gremlins.py")

        # --- @! Rendering State (Optimized) ---------------------------------------------
        # We hold ONLY the currently needed sprite sheet.
        self._current_sheet: QPixmap | None = None
        self._current_src_rect: QRect = QRect()
        self._last_loaded_sprite_key = None  # To prevent reloading the same sheet

        # --- @! Reload animation for Blue Archive gremlins ------------------------------
        self.has_reload = settings.SpriteMap.HasReloadAnimation
        if self.has_reload:
            self.ammo = 6

        # --- @! Sound Player ------------------------------------------------------------
        self.sound_player = QSoundEffect(self)
        self.sound_player.setVolume(settings.Settings.Volume)

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
            self.reset_emote_timer()

        # --- @! Start -------------------------------------------------------------------
        self.setup_tray_icon()
        self.play_sound(settings.SfxMap.Intro)

        # Initialize the first state's resources manually
        self.load_sprite_sheet(settings.SpriteMap.Intro)

        self.master_timer.start(1000 // settings.SpriteMap.FrameRate)
        self.idle_timer.start(120 * 1000)

    # --- @! Resource Management (Crucial for Memory) ------------------------------------

    def load_sprite_sheet(self, sprite_key):
        """
        Loads the sprite sheet ONLY if it's different from the current one.
        Explicitly clears all known caches (sprite_manager and Qt) to free memory.
        """
        if self._last_loaded_sprite_key == sprite_key:
            return

        # 1. Explicitly release the old reference from the window
        self._current_sheet = None

        # 2. Force sprite_manager to clear its global cache (The FIX)
        sprite_manager.clear_cache()

        # 3. Clear Qt's internal QPixmap cache (extra precaution)
        QPixmapCache.clear()

        # 4. Force Python Garbage Collection to reclaim the memory immediately
        gc.collect()

        # 5. Load the new sheet (this will trigger a disk load in sprite_manager now)
        self._current_sheet = sprite_manager.get(sprite_key)
        self._last_loaded_sprite_key = sprite_key

        self.update()  # Force repaint with the new sheet

    # --- @! Rendering -------------------------------------------------------------------

    def paintEvent(self, event):
        if self._current_sheet and not self._current_sheet.isNull():
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self._current_sheet, self._current_src_rect)
            painter.end()

    def update_frame_rect(self, current_frame):
        """Calculates the slice of the sprite sheet to draw."""
        m = settings.SpriteMap
        cols = m.SpriteColumn

        x = (current_frame % cols) * m.FrameWidth
        y = (current_frame // cols) * m.FrameHeight

        new_rect = QRect(x, y, m.FrameWidth, m.FrameHeight)

        # Only trigger a repaint if the frame actually changed
        if self._current_src_rect != new_rect:
            self._current_src_rect = new_rect
            self.update()

    # --- @! State Machine Core ----------------------------------------------------------

    def set_state(self, new_state: State):
        if self.current_state == new_state:
            # Re-trigger logic for shooting
            reshootable = (
                self.has_reload
                and new_state in [State.LEFT_ACTION, State.RIGHT_ACTION]
                and self.ammo > 0
            )
            if not reshootable:
                return
            # Continue re-shoot logic...
            if self.has_reload and self.ammo > 0:
                self.ammo -= 1
                sfx_key = (
                    settings.SfxMap.LeftAction
                    if new_state == State.LEFT_ACTION
                    else settings.SfxMap.RightAction
                )
                self.play_sound(sfx_key)
                # Reset frame to 0 to restart animation
                self.reset_current_frames(new_state)
                return

        # Stop timers on exit
        match self.current_state:
            case State.WALK_IDLE:
                self.walk_idle_timer.stop()
            case State.EMOTE:
                self.emote_duration_timer.stop()

        # Handle Entry
        match new_state:
            case State.GRAB:
                self.play_sound(settings.SfxMap.Grab)
                self.load_sprite_sheet(settings.SpriteMap.Grab)
            case State.WALK:
                if self.current_state != State.WALK:
                    self.play_sound(settings.SfxMap.Walk)
                # Note: Walk sprites are dynamic, handled in animation_tick
            case State.WALK_IDLE:
                self.walk_idle_timer.start(2000)
                self.load_sprite_sheet(settings.SpriteMap.WalkIdle)
            case State.IDLE:
                self.load_sprite_sheet(settings.SpriteMap.Idle)
            case State.HOVER:
                self.load_sprite_sheet(settings.SpriteMap.Hover)
            case State.POKE:
                self.play_sound(settings.SfxMap.Poke)
                self.load_sprite_sheet(settings.SpriteMap.Poke)
            case State.PAT:
                self.play_sound(settings.SfxMap.Pat)
                self.load_sprite_sheet(settings.SpriteMap.Pat)
            case State.SLEEP:
                self.load_sprite_sheet(settings.SpriteMap.Sleep)
            case State.LEFT_ACTION:
                if self.has_reload and self.ammo > 0:
                    self.play_sound(settings.SfxMap.LeftAction)
                    self.ammo -= 1
                self.load_sprite_sheet(settings.SpriteMap.LeftAction)
            case State.RIGHT_ACTION:
                if self.has_reload and self.ammo > 0:
                    self.play_sound(settings.SfxMap.RightAction)
                    self.ammo -= 1
                self.load_sprite_sheet(settings.SpriteMap.RightAction)
            case State.RELOAD:
                self.play_sound(settings.SfxMap.Reload)
                self.ammo = 6
                self.load_sprite_sheet(settings.SpriteMap.Reload)
            case State.EMOTE:
                self.play_sound(settings.SfxMap.Emote)
                emote_duration = settings.EmoteConfig.EmoteDuration
                self.emote_duration_timer.start(emote_duration)
                self.load_sprite_sheet(settings.SpriteMap.Emote)

        self.current_state = new_state
        self.reset_current_frames(new_state)

    def reset_current_frames(self, state: State):
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

    def advance_frame(self, current_frame, frame_count):
        """Just calculates the next number and updates the rect."""
        if frame_count == 0:
            return current_frame

        self.update_frame_rect(current_frame)
        return (current_frame + 1) % frame_count

    def animation_tick(self):
        """
        Optimized Tick:
        Uses the pre-loaded self._current_sheet.
        """
        c = settings.CurrentFrames
        f = settings.FrameCounts

        match self.current_state:
            case State.INTRO:
                c.Intro = self.advance_frame(c.Intro, f.Intro)
                if c.Intro == 0:
                    self.set_state(State.IDLE)
            case State.IDLE:
                c.Idle = self.advance_frame(c.Idle, f.Idle)
            case State.HOVER:
                c.Hover = self.advance_frame(c.Hover, f.Hover)
            case State.WALK:
                self.handle_walking_animation_and_movement()
            case State.WALK_IDLE:
                c.WalkIdle = self.advance_frame(c.WalkIdle, f.WalkIdle)
            case State.GRAB:
                c.Grab = self.advance_frame(c.Grab, f.Grab)
            case State.PAT:
                c.Pat = self.advance_frame(c.Pat, f.Pat)
                if c.Pat == 0:
                    self.set_state(State.HOVER if self.underMouse() else State.IDLE)
            case State.POKE:
                c.Poke = self.advance_frame(c.Poke, f.Poke)
                if c.Poke == 0:
                    self.set_state(State.HOVER if self.underMouse() else State.IDLE)
            case State.SLEEP:
                c.Sleep = self.advance_frame(c.Sleep, f.Sleep)
            case State.EMOTE:
                c.Emote = self.advance_frame(c.Emote, f.Emote)
            case State.LEFT_ACTION:
                if not self.has_reload or self.ammo >= 0:
                    c.LeftAction = self.advance_frame(c.LeftAction, f.LeftAction)
                if c.LeftAction == 0:
                    self.handle_reload_check()
            case State.RIGHT_ACTION:
                if not self.has_reload or self.ammo >= 0:
                    c.RightAction = self.advance_frame(c.RightAction, f.RightAction)
                if c.RightAction == 0:
                    self.handle_reload_check()
            case State.RELOAD:
                c.Reload = self.advance_frame(c.Reload, f.Reload)
                if c.Reload == 0:
                    self.set_state(State.HOVER if self.underMouse() else State.IDLE)

    def handle_walking_animation_and_movement(self):
        f = settings.FrameCounts
        c = settings.CurrentFrames

        # Determine direction
        direction = self.movement_handler.get_animation_direction()
        direction_sprite_key = getattr(settings.SpriteMap, direction, None)

        # Lazy load the walk sprite only if direction changed
        # This will call the aggressive load_sprite_sheet()
        self.load_sprite_sheet(direction_sprite_key)

        frame_count = getattr(f, direction, 0)
        prev_frame = getattr(c, direction, 0)

        # Advance frame
        next_frame = self.advance_frame(prev_frame, frame_count)
        setattr(c, direction, next_frame)

        # Move window
        dx, dy = self.movement_handler.getVelocity()
        if dx != 0 or dy != 0:
            self.move(self.pos().x() + dx, self.pos().y() + dy)

    # Standard boilerplate needed for the class to function
    def handle_reload_check(self):
        if self.has_reload and self.ammo <= 0:
            self.set_state(State.RELOAD)
        else:
            self.set_state(State.HOVER if self.underMouse() else State.IDLE)

    def play_sound(self, file_name, delay_seconds=0):
        # (Keep your original sound logic here)
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
            if (
                last_time
                and (datetime.datetime.now() - last_time).total_seconds()
                < delay_seconds
            ):
                return
        try:
            self.sound_player.setSource(QUrl.fromLocalFile(path))
            self.sound_player.play()
            settings.Settings.LastPlayed[file_name] = datetime.datetime.now()
        except:
            pass

    def setup_tray_icon(self):
        # ... (same as previous)
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
        menu = QMenu()
        reappear = QAction("Reappear", self)
        reappear.triggered.connect(self.reset_app)
        menu.addAction(reappear)
        close = QAction("Close", self)
        close.triggered.connect(self.close_app)
        menu.addAction(close)
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

    def reset_idle_timer(self):
        self.idle_timer.start(300 * 1000)
        if self.current_state == State.SLEEP:
            self.set_state(State.IDLE)

    def idle_timer_tick(self):
        if self.current_state == State.IDLE:
            self.set_state(State.SLEEP)

    def outro_tick(self):
        s = settings
        # Manual load/advance for outro
        self.load_sprite_sheet(s.SpriteMap.Outro)
        s.CurrentFrames.Outro = self.advance_frame(
            s.CurrentFrames.Outro, s.FrameCounts.Outro
        )
        if s.CurrentFrames.Outro == 0:
            self.close_timer.stop()
            sys.exit(0)

    def on_walk_idle_finished(self):
        if self.current_state == State.WALK_IDLE:
            self.set_state(State.HOVER if self.underMouse() else State.IDLE)

    def reset_emote_timer(self):
        try:
            val = random.randint(
                settings.EmoteConfig.MinEmoteTriggerMinutes * 60000,
                settings.EmoteConfig.MaxEmoteTriggerMinutes * 60000,
            )
            self.emote_timer.start(val)
        except:
            self.emote_timer.stop()

    def emote_timer_tick(self):
        if self.current_state in [State.IDLE, State.HOVER, State.SLEEP]:
            self.set_state(State.EMOTE)
        self.reset_emote_timer()

    def on_emote_finished(self):
        if self.current_state == State.EMOTE:
            self.set_state(State.HOVER if self.underMouse() else State.IDLE)
            self.reset_idle_timer()

    # Helper for Hotspots (Optimized)
    def mousePressEvent(self, event):
        if self.current_state == State.EMOTE:
            return

        click_pos = event.pos()

        def check(geom_func):
            return QRect(*geom_func()).contains(click_pos)

        if event.button() == Qt.MouseButton.RightButton:
            if check(compute_top_hotspot_geometry):
                self.on_hotspot_click(event, State.PAT)
                return
            if check(compute_left_hotspot_geometry):
                self.on_hotspot_click(event, State.LEFT_ACTION)
                return
            if check(compute_right_hotspot_geometry):
                self.on_hotspot_click(event, State.RIGHT_ACTION)
                return

            if self.current_state not in [State.GRAB, State.PAT, State.POKE]:
                self.reset_idle_timer()
                self.reset_emote_timer()
                self.set_state(State.POKE)

        elif event.button() == Qt.MouseButton.LeftButton:
            self.reset_idle_timer()
            self.reset_emote_timer()
            if self.current_state not in [State.GRAB, State.PAT, State.POKE]:
                self.set_state(State.GRAB)
                self.drag_pos = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if (
            self.current_state == State.GRAB
            and event.buttons() == Qt.MouseButton.LeftButton
        ):
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.current_state == State.GRAB
        ):
            self.set_state(State.HOVER if self.underMouse() else State.IDLE)

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        if self.current_state in [
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
            self.set_state(State.EMOTE)
            self.reset_emote_timer()
        if self.movement_handler.is_moving():
            self.set_state(State.WALK)
            self.reset_idle_timer()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        self.movement_handler.recordKeyRelease(event)
        if self.current_state == State.WALK and not self.movement_handler.is_moving():
            self.set_state(State.WALK_IDLE)

    def enterEvent(self, event):
        self.setFocus()
        self.reset_idle_timer()
        if self.current_state == State.IDLE:
            self.set_state(State.HOVER)
        if self.current_state not in [
            State.WALK,
            State.GRAB,
            State.SLEEP,
            State.POKE,
            State.EMOTE,
        ]:
            self.play_sound(settings.SfxMap.Hover, 3)

    def leaveEvent(self, event):
        self.clearFocus()
        self.movement_handler.recordMouseLeave()
        if self.current_state == State.WALK:
            self.set_state(State.WALK_IDLE)
        elif self.current_state == State.HOVER:
            self.set_state(State.IDLE)

    def on_hotspot_click(self, event, state):
        if self.current_state not in [
            State.GRAB,
            State.POKE,
            State.SLEEP,
            State.EMOTE,
            State.RELOAD,
        ]:
            self.reset_idle_timer()
            self.reset_emote_timer()
            self.set_state(state)

    def top_hotspot_click(self, event):
        self.on_hotspot_click(event, State.PAT)

    def left_hotspot_click(self, event):
        self.on_hotspot_click(event, State.LEFT_ACTION)

    def right_hotspot_click(self, event):
        self.on_hotspot_click(event, State.RIGHT_ACTION)
