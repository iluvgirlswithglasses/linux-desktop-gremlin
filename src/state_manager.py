from .movement_handler import reset_all_walk_frames
from .settings import CurrentFrames, EmoteConfig, SfxMap, SpriteMap, State


class AnimationStateManager:
    def __init__(self, window):
        self.window = window
        self.cur_state = State.INTRO

        # shooting animation for Blue Archive characters
        self.has_reload = SpriteMap.HasReloadAnimation
        self.ammo = 6 if self.has_reload else 0

    def transition_to(self, new_state: State):
        # cleans up previous state
        if self.cur_state == State.WALK_IDLE:
            self.window.walk_idle_timer.stop()
        elif self.cur_state == State.EMOTE:
            self.window.emote_duration_timer.stop()

        # prevents entering the same state unless spammable
        if self.cur_state == new_state and not self._is_spammable(new_state):
            return

        # applies state transition effects
        self._handle_entry_effects(new_state)

        # applies state
        self.cur_state = new_state
        self._reset_current_frames(new_state)

    def check_reload(self, is_under_mouse: bool):
        """Checks if we need to reload after a left/right action."""
        if self.has_reload and self.ammo <= 0:
            self.transition_to(State.RELOAD)
        else:
            self.transition_to(State.HOVER if is_under_mouse else State.IDLE)

    def _is_spammable(self, state: State) -> bool:
        # allow shooting (aka. left/right action) when loaded
        return self.ammo > 0 and state in [State.LEFT_ACTION, State.RIGHT_ACTION]

    def _handle_entry_effects(self, new_state: State):
        def play_sound(sfx):
            self.window.sound_engine.play(sfx)

        match new_state:
            case State.GRAB:
                play_sound(SfxMap.Grab)
            case State.WALK:
                if self.cur_state != State.WALK:
                    play_sound(SfxMap.Walk)
            case State.WALK_IDLE:
                self.window.walk_idle_timer.start(2000)
            case State.POKE:
                play_sound(SfxMap.Poke)
            case State.PAT:
                play_sound(SfxMap.Pat)
            case State.LEFT_ACTION:
                if self.has_reload and self.ammo > 0:
                    play_sound(SfxMap.LeftAction)
                    self.ammo -= 1
            case State.RIGHT_ACTION:
                if self.has_reload and self.ammo > 0:
                    play_sound(SfxMap.RightAction)
                    self.ammo -= 1
            case State.RELOAD:
                play_sound(SfxMap.Reload)
                self.ammo = 6
            case State.EMOTE:
                play_sound(SfxMap.Emote)
                emote_duration = EmoteConfig.EmoteDuration
                self.window.emote_duration_timer.start(emote_duration)

    def _reset_current_frames(self, state: State):
        """Resets the frame counter for the new state."""
        c = CurrentFrames
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
