
# Linux Desktop Gremlins!

Basically [KurtVelasco's Desktop Gremlin](https://github.com/KurtVelasco/Desktop_Gremlin), but re-written in PySide + Qt6.

https://github.com/user-attachments/assets/eeb75510-9725-4f3a-a259-0959ddc22603

💥 Features 💥

- Works on both X11 (with picom) and Hyprland (with XWayland).
- Also works on Windows and MacOS (follow the manual installation guide).
- Interactive controls:
    - **Drag & Drop:** 🖱️ Click and drag your gremlins to move 'em.
    - **Walk**: ⌨️ Hover your mouse over the gremlins, then use W/A/S/D to make 'em skedaddle 💨💨.
    - **Secret Moves:** Right-click on different spots to play special animations 😎! It might be a headpat, a poke, or something even more special!
- Also, if you leave the gremlins lonely for so long, they will occasionally make more ✨noises✨ to annoy you 😈😈. Think of it as *"1 hour of silence occasionally broken up by Mambo"*.

> Note: The *"1 hour of silence occasionally broken up by Mambo"* feature can be turned off (if you are a chicken 🐔🐔). See [Customizations](./docs/05-customize.md).

# Install and customize! 🚀

Follow these steps to get your gremlins up and running!

+ [1. Configure your compositor](./docs/01-configure-compositor.md)
+ [2. Install this repository](./docs/02-install.md)
+ [3. Choose your gremlins!](./docs/03-download-gremlin-assets.md)
+ [4. Run desktop gremlins!](./docs/04-run.md)
+ [5. Customizations](./docs/05-customize.md)
+ [6. Create your gremlins!](./docs/06-create-your-gremlins.md)

# Changelog

- **2026-02-08 Breaking Change: Assets have been moved to release tags!** If you have cloned this repo earlier than that, please see [Migration Guide](./docs/migrate-to-v1.0.0.md) to avoid re-downloading the assets after `git pull`. Also, take a look at the [New Downloader](./docs/03-download-gremlin-assets.md)! It helps downloading new gremlin assets with ease!

<details>
    <summary>See 2025 changelog</summary>

- 2026-01-15: Refactored the entire codebase for modularity and strict type-check. Some behaviors have changed, some are intentional, some are bugs.
- 2026-01-14: Added Qt6 character selector GUI! Huge thanks to [@Multex](https://github.com/Multex)!
- 2025-11-18: Massive source code restructure! We now have a unified run script and a package recipe for Guix. (Huge thanks to [@thanosapollo](https://github.com/thanosapollo)! This chad is a much better programmer than I am.)
- 2025-11-16: Added a manual trigger for the annoy emote. Press `P` to make them noisy on command.
- 2025-11-15: Remapped headpats from Left Click to Right Click. No more accidental pats when you want to drag them around!
</details>


# Some differences between this and KurtVelasco's Desktop Gremlins

This is not a strict 1:1 port, because I made some changes to the animation flow to better match my own preferences. I also created a few additional spritesheets; please feel free to use them if they're helpful.

# Try other forks!

There are some forks of this repository that you may want to checkout!

- [#23](https://github.com/iluvgirlswithglasses/linux-desktop-gremlin/pull/23): Significantly reduces memory usage of the app, though some functionalities will be different.

