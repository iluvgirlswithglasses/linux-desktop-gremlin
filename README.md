
# Linux Desktop Gremlins!

Basically [KurtVelasco's Desktop Gremlin](https://github.com/KurtVelasco/Desktop_Gremlin), but re-written in PySide + Qt6.

https://github.com/user-attachments/assets/eeb75510-9725-4f3a-a259-0959ddc22603

💥 Features 💥

- Works on both X11 (with picom) and Hyprland (with XWayland).
- Interactive controls:
    - **Drag & Drop:** 🖱️ Click and drag your gremlins to move 'em.
    - **Walk**: ⌨️ ~Cursor-following does not work in Wayland 🥺🥺🥺~. So hover your mouse over the gremlins, then use W/A/S/D to make 'em skedaddle 💨💨.
    - **Secret Move:** Right-click to see what happens 😎. Pro tip: *where* you right-click matters! A headpat, a poke, (or something even more special) might play!
- Also, if you leave the gremlins lonely for so long, they will occasionally make more ✨noises✨ to annoy you 😈😈. Think of it as *"1 hour of silence occasionally broken up by Mambo"*.

> Note 1: The *"1 hour of silence occasionally broken up by Mambo"* feature can be turned off (if you are a chicken 🐔🐔). See the "Customize your Gremlins!" section below.
>
> Note 2: It seems that the "Cursor-following does not work in Wayland" statement of mine was, in fact, a skill issue 😩😩. I'll implement it as soon as I can.

# Changelog

- 2025-11-18: Massive source code restructure! We now have a unified run script and a package recipe for Guix. (Huge thanks to [@thanosapollo](https://github.com/thanosapollo)! This chad is a much better programmer than I am.)
- 2025-11-16: Added a manual trigger for the annoy emote. Press `P` to make them noisy on command.
- 2025-11-15: Remapped headpats from Left Click to Right Click. No more accidental pats when you want to drag them around!

# Some differences between this and KurtVelasco's Desktop Gremlins

This is not a strict 1:1 port, because I made some changes to the animation flow to better match my own preferences. I also created a few additional spritesheets; please feel free to use them if they're helpful.

Furthermore, for anyone who wants to add or change the animation logic: Check out the `animation_tick` method in `gremlin.py`. Unlike KurtVelasco's original code, this version uses a more traditional Finite State Machine design, so it should make the logic easier to follow and extend. There's still plenty of room for improvement, though. I'll come back to polishing the code after I finish adding the animations I have in mind.

# ⚙ How to Install and Run (Automatically)

## 1. Configure your Compositor

To make the gremlin's background transparent, your compositor must be configured correctly. Unfortunately, this is not something that can really be automated. So, before you install, please follow these guides for X11 desktops and Hyprland:

<details>
  <summary>For X11 (e.g., i3, bspwm, etc.)</summary>

  Install `picom` and have it executed on startup is enough. For example, you may install it via:

  ```sh
  sudo apt install picom  # for Debian/Ubuntu based distros
  yay -S picom            # for AUR users
  ```

  Then, add the following line into your `~/.xinitrc` or equivalent startup script:

  ```sh
  picom &
  ```
</details>

<details>
  <summary>For Hyprland</summary>

  Firstly, you need `xwayland`. Since you're using Hyprland, I suspect you have it already. But if you don't, please install it with this command (or any of its equivalent):

  ```sh
  yay -S xorg-xwayland
  ```

  Then, add the following rules into your `~/.config/hypr/hyprland.conf`:

  ```conf
  windowrulev2 = noblur, title:ilgwg_desktop_gremlins.py
  windowrulev2 = noshadow, title:ilgwg_desktop_gremlins.py
  windowrulev2 = noborder, title:ilgwg_desktop_gremlins.py
  ```
</details>

<details>
  <summary>For Niri</summary>

  Add the following window rules:

  ```conf
  window-rule {
      match title="ilgwg_desktop_gremlins.py"
      draw-border-with-background false
      opacity 0.99
      focus-ring {
          off
      }
      border {
          // Same as focus-ring.
      }
      shadow {
          off
      }
  }
  ```
</details>

## 2. Run the installation script

Just run the following script, and it will take care of the rest:

```sh
curl -s https://raw.githubusercontent.com/iluvgirlswithglasses/linux-desktop-gremlin/refs/heads/main/install.sh | bash
```

It is recommended that you check the content of the script before running.

## 3. Run Desktop Gremins!

If you have [rofi](https://github.com/davatorium/rofi) installed, you can use it to find and run Desktop Gremlin.

<img width="960" height="720" alt="tmp_3" src="https://github.com/user-attachments/assets/45b2cffa-2914-4e25-b8d2-de07432c008e" />

Otherwise, you can navigate to `~/.config/linux-desktop-gremlin/` and execute the run script, then a gremlin shall be spawned:

```sh
./run.sh                    # to spawn the default character (specified in ./config.json)
./run.sh <character-name>   # to spawn any character who is available in ./spritesheet/

# You can now close the terminal which you executed these scripts with.
# The gremlin won't be despawned unless you use your hotkeys for closing window,
# like alt+f4 or mod+q.
```

# ⚙ How to Install and Run (Manually)

## 1. Install Dependencies

You can install dependencies either in a Python virtual environment or using your system's package manager.

<details>
  <summary>Method A: Virtual Environment (Recommended)</summary>

  There's nothing that can go wrong about this, except for the disk space.

  ```sh
  # clone repository
  git clone https://github.com/iluvgirlswithglasses/linux-desktop-gremlin
  cd linux-desktop-gremlin

  # install uv -- a fast Python package manager -- then sync packages
  curl -LsSf https://astral.sh/uv/install.sh | sh
  uv sync
  ```
</details>

<details>
  <summary>Method B: System Package Manager</summary>

  This method uses your distribution's packages to save disk space. You will need PySide6 and its Qt6 dependencies.

  ```sh
  # Example for Arch Linux
  yay -S pyside6 qt6-base
  ```
</details>

## 2. Run Linux Desktop Gremlins

Execute one of these run scripts, then a gremlin shall be spawned:

```sh
./run.sh                    # to spawn the default character (specified in ./config.json)
./run.sh <character-name>   # to spawn any character who is available in ./spritesheet/
./scripts/gremlin-picker.sh # if you want to use a GUI picker (you need rofi installed)

# You can now close the terminal which you executed these scripts with.
# The gremlin won't be despawned unless you use your hotkeys for closing window,
# like alt+f4 or mod+q.
```

You would also need to configure your compositor correctly so that the gremlins have fully transparent background. Refer to section "How to Install and Run (Automatically)" > "1. Configure your Compositor".

# 🔧 Customizations!

https://github.com/user-attachments/assets/26e2a3b0-4fde-4a3a-926f-ad9f1e1cfb07

## How to Make Your Gremlin Annoy You (Occasionally!)

Do you want the gremlins to annoy you at random time or not? 😜

To control this, open `./spritesheet/<character>/emote-config.json`. You'll see:

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

## How to Enable or Disable the System Tray

This program's systray is disabled by default, and you won't lose any functionality by disabling the systray either. However, if you need it, you might enable it by modifying the `Systray` field in `./config.json` to `true`.

## Try other forks!

There are some forks of this repository that you may want to checkout!

- [#22](https://github.com/iluvgirlswithglasses/linux-desktop-gremlin/pull/22): Adds Gold Ship, Oguri Cap and Agnes Tachyon (I will either merge this, or put it in [releases](https://github.com/iluvgirlswithglasses/linux-desktop-gremlin/releases) in the future)
- [#23](https://github.com/iluvgirlswithglasses/linux-desktop-gremlin/pull/23): Significantly reduces memory usage of the app, though some functionalities will be different.

# 🚀 Stay Tuned!

I'll be adding more characters as soon as my full-time job and university decide to give me a break.

Also, got a cool spritesheet you're dying to see running on your desktop? Feel free to open an issue on GitHub and share! Thank you!
