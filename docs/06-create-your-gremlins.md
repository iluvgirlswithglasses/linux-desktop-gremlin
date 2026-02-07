
# 6. Create Your Gremlins!

As long as you have the spritesheets, creating a custom gremlin is just a matter of organizing your sprites and sounds into the right folders!

## Overall Structure 🏗️

A gremlin (assume the name `hikari`) should be structured like this:

```
~/.config/linux-desktop-gremlin/gremlins/
└── hikari
    ├── sounds
    │   ├── *.{mkv,mp3,ogg,wav...}
    │   └── sfx-map.json
    └── sprites
        ├── *.png
        ├── emote-config.json
        ├── frame-count.json
        └── sprite-map.json
```

## sfx-map.json

This file tells the app which sound to play when a gremlin enters a specific state. For example:

```json
{
    "Hover": "",
    "Intro": "intro.wav",
    "Outro": "outro.wav",
    "Grab": "grab.wav",
    "Walk": "walk.wav",
    "Poke": "poke.wav",
    "Pat": "pat.wav",
    "LeftAction": "fire.wav",
    "RightAction": "fire.wav",
    "Reload": "reload.wav",
    "Emote": "emote.wav"
}
```

All fields in `sfx-map.json` can be empty.

## sprite-map.json

Defines your spritesheets' properties and which spritesheet corresponds to which action:

```json
{
    "FrameRate": 40,
    "SpriteColumn": 10,
    "FrameHeight": 350,
    "FrameWidth": 350,
    "TopHotspotHeight": 125,
    "TopHotspotWidth": 150,
    "SideHotspotHeight": 150,
    "SideHotspotWidth": 100,
    "HasReloadAnimation": true,
    "Idle": "idle.png",
    "Hover": "hover.png",
    "Sleep": "sleep.png",
    "Intro": "intro.png",
    "Outro": "outro.png",
    "Grab": "grab.png",
    "Up": "backward.png",
    "Down": "forward.png",
    "Left": "left.png",
    "Right": "right.png",
    "UpLeft": "backward.png",
    "UpRight": "backward.png",
    "DownLeft": "forward.png",
    "DownRight": "forward.png",
    "WalkIdle": "wIdle.png",
    "Poke": "poke.png",
    "Pat": "pat.png",
    "LeftAction": "fireL.png",
    "RightAction": "fireR.png",
    "Reload": "reload.png",
    "Emote": "poke.png"
}
```

All fields in `sprite-map.json` are mandatory. Except for when `HasReloadAnimation` is `false`, then `Reload`, `LeftAction`, and `RightAction` can be empty string.

## frame-count.json

For every sheet in `sprite-map.json`, specify the total number of frames here:

```json
{
    "Idle": 121,
    "Hover": 120,
    "Sleep": 60,
    "Intro": 90,
    "Outro": 90,
    "Grab": 328,
    "Up": 21,
    "Down": 21,
    "Left": 21,
    "Right": 21,
    "UpLeft": 21,
    "UpRight": 21,
    "DownLeft": 21,
    "DownRight": 21,
    "WalkIdle": 121,
    "Poke": 160,
    "Pat": 298,
    "LeftAction": 25,
    "RightAction": 25,
    "Reload": 56,
    "Emote": 160
}
```

## emote-config.json

See the previous chapter: [5. Customizations](./05-customize.md).

## Porting Gremlins from KurtVelasco

As you can clearly see, most assets of this project is created by [KurtVelasco](https://github.com/KurtVelasco/Desktop_Gremlin).

To port gremlins from [KurtVelasco's Desktop Gremlin](https://github.com/KurtVelasco/Desktop_Gremlin) to this project, simply:
1. Put the audio files in `gremlins/<character>/sounds` and edit `sfx-map.json`.
2. Put the spritesheets in `gremlins/<character>/sprites` and edit `sprite-map.json`, `frame-count.json`.
3. Create an `emote-config.json` file (see [5. Customizations](./05-customize.md)) to setup emotes.

And you're good to go! 🎉

