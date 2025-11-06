
# Linux Desktop Gremlins!

Basically [KurtVelasco's Desktop Gremlin](https://github.com/KurtVelasco/Desktop_Gremlin), but re-written in PySide + Qt6.

https://github.com/user-attachments/assets/eeb75510-9725-4f3a-a259-0959ddc22603

💥 Features 💥

- Works on both X11 (with picom) and Hyprland (with XWayland).
- Interactive controls:
    - **Drag & Drop:** 🖱️ Click and drag your gremlins to move 'em.
    - **Walk**: ⌨️ ~Cursor-following does not work in Wayland 🥺🥺🥺~. So hover your mouse over the gremlins, then use W/A/S/D to make 'em skedaddle 💨💨.
    - **Secret Move:** 💃 Right-click to see what happens. (It's Mambo time 😎😎)
    - **Headpats:** 🖐️ You can pat their head by clicking the top hotspot. (Still looking for a Mambo patting animation, send help.)
- The gremlins will make some ✨noises✨ when you interact with them 🥰🥰 Show 'em some love!
- Also, if you leave the gremlins lonely for so long, they will occasionally make more ✨noises✨ to annoy you 😈😈. Think of it as *"1 hour of silence occasionally broken up by Mambo"*.

> Note 1: The *"1 hour of silence occasionally broken up by Mambo"* feature can be turned off (if you are a chicken 🐔🐔). See the "Customize your Gremlins!" section below.
>
> Note 2: It seems that the "Cursor-following does not work in Wayland" statement of mine was, in fact, a skill issue 😩😩. I'll implement it as soon as I can.

# Some differences between this and KurtVelasco's Desktop Gremlins

This is not a strict 1:1 port, because I made some changes to the animation flow to better match my own preferences. I also created a few additional spritesheets; please feel free to use them if they're helpful.

Furthermore, for anyone who wants to add or change the animation logic: Check out the `animation_tick` method in `gremlin.py`. Unlike KurtVelasco's original code, this version uses a more traditional Finite State Machine design, so it should make the logic easier to follow and extend. There's still plenty of room for improvement, though. I'll come back to polishing the code after I finish adding the animations I have in mind.

# How to Install and Run

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
  # Example for Arch / EndeavourOS
  yay -S pyside6 qt6-base
  ```
</details>

## 2. Configure your Compositor

To make the gremlin's background transparent, your compositor must be configured correctly. Here are the guides for X11 desktops and Hyprland:

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

## 3. Run Linux Desktop Gremlins

Execute the script that matches your setup, then a gremlin shall be spawned:

```sh
./run-x11.sh            # for running on X11
./run-wayland.sh        # for running on Hyprland
./run-uv-x11.sh         # for running with virtual environment on X11
./run-uv-wayland.sh     # for running with virtual environment on Hyprland

# You can now close the terminal which you executed these scripts with.
# The gremlin won't be despawned unless you use your hotkeys for closing window,
# like alt+f4 or mod+q.
```

# 🔧 Customize your Gremlins!

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

## How to Enable or Disable the System Tray

This program's systray is disabled by default, and you won't lose any functionality by disabling the systray either. However, if you need it, you might enable it by modifying the `Systray` field in `./config.json` to `true`.

# Stay Tuned! 🚀

I'll be adding more characters as soon as my full-time job and university decide to give me a break.

Also, got a cool spritesheet you're dying to see running on your desktop? Feel free to open an issue on GitHub and share! Thank you!

