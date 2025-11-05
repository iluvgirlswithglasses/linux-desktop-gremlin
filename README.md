
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

> Note: It seems that the "Cursor-following does not work in Wayland" statement of mine was, in fact, a skill issue 😩😩. I'll implement it as soon as I can.

# Some differences between this and KurtVelasco's Desktop Gremlins

Aside from the differences that originate from platform problems, I also made some changes to the animation flow so as to fit my preferences. I don't think it's noticable, I just want to clearly announce that these discrepancies are not bugs, but intended features.

Also, for anyone who wants to dive in and tinker: I took KurtVelasco's original state management code and refactored it from a pile of if-else into a clean, classic Finite State Machine. If you want to add your own animations or change the logic, just check out the `animation_tick` method in `gremlin.py`. It's deadass simple. Go wild.

# How to Install and Run

## 1. Install Dependencies

You can install dependencies either in a Python virtual environment or using your system's package manager.

<details>
  <summary>Method A: Virtual Environment (Recommended)</summary>

  There's nothing that can go wrong about this, except for the disk space.

  ```sh
  # Install uv, a fast Python package manager
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Install dependencies into the virtual environment
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

# Stay Tuned! 🚀

I'll be adding more characters as soon as my full-time job and university decide to give me a break.

Also, got a cool spritesheet you're dying to see running on your desktop? Feel free to open an issue on GitHub and share! Thank you!

