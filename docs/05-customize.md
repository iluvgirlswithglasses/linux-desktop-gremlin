
# 5. Customizations! 🔧

Thanks to the hard work of [@Multex](https://github.com/Multex), all of the following customizations can be done in the Gremlin Picker GUI! But, if you need to know what each variable does, you might still want to read this.

## How to Make Your Gremlin Annoy You (Occasionally!)

Do you want the gremlins to annoy you at random time or not? 😜

To control this, open `./gremlins/<character>/spritesheet/emote-config.json`. You'll see:

```json
{
    "AnnoyEmote": true,
    "MinEmoteTriggerMinutes": 5,
    "MaxEmoteTriggerMinutes": 15,
    "EmoteDuration": 3600
}
```

If you set `AnnoyEmote` to `false`, then nothing happens. If you set it to `true`, however:
- If the gremlin goes without any *"caring interactions"* (no pats, no drags, no clicks,...) they will get bored 😢.
- If you leave them bored for a while (a random time between `MinEmoteTriggerMinutes` and `MaxEmoteTriggerMinutes`), they will suddenly play a special emote (with sound!) all by themselves 😙😙.
- The emote will last for the number of milliseconds set in `EmoteDuration`.
  - *(Note: For now, this duration only affects the animation, not the sound effect, sorry 😢.)*

You can also trigger this animation by hovering over the gremlin and press "P". You can customize this key too, just take a look at `./config.json`.

## Other configurations

For global settings that affect all your gremlins, check out the [config.json](../config.json) file.

| Variable          | Description                                                                   |
| :---------------- | :---------------------------------------------------------------------------- |
| `Systray`         | Show/hide the app icon in your system tray                                    |
| `MoveSpeed`       | How fast should the gremlins walk                                             |
| `Scale`           | Edit this if your gremlin is too big or too small                             |
| `Volume`          | SFX volume (in range 0..1)                                                    |
| `AudioDevice`     | Set a specific audio device if your default isn't working                     |
| `EmoteKeyEnabled` | Toggle the hotkey for triggering emote manually                               |
| `EmoteKey`        | Change the emote trigger key                                                  |
| `IdleMinutes`     | How long should the gremlin be idle before they decide to nap                 |
| `SleepMinutes`    | How long shoudl the gremlin sleep before waking up naturally                  |

---

[--> Next chapter: Create Your Gremlins!](./06-create-your-gremlins.md)

