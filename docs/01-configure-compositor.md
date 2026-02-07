
# 1. Configure your Compositor

> If you're using a conventional desktop environment (like Windows, MacOS, KDE,...) please skip this chapter.

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
windowrule {
    name = linux-gremlin
    no_blur = on
    no_shadow = on
    border_size = 0
    match:title = ilgwg_desktop_gremlins.py
}
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

---

[--> Next chapter: Install Linux Desktop Gremlins](./02-install.md)

