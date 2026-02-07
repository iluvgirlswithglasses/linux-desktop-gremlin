
# 4. Run Desktop Gremlins!

You can find **Gremlin Picker** in your application menu (or app launcher like Rofi/Wofi/Fuzzel). Just search for "Gremlin" and launch it!

<img width="1003" height="500" alt="ss-app_launcher" src="https://github.com/user-attachments/assets/fee960dc-c983-424d-8649-23c4b40d1293" />

Alternatively, you can run the picker from the terminal:

```sh
./scripts/gremlin-picker.sh
```

If you prefer to skip the picker GUI, navigate to `~/.config/linux-desktop-gremlin/` and execute the run script directly:

```sh
./run.sh                    # to spawn the default character (specified in ./config.json)
./run.sh <character-name>   # to spawn any character who is available in ./spritesheet/

# You can now close the terminal which you executed these scripts with.
# The gremlin won't be despawned unless you use your hotkeys for closing window,
# like alt+f4 or mod+q.
```

https://github.com/user-attachments/assets/26e2a3b0-4fde-4a3a-926f-ad9f1e1cfb07

---

[--> Next chapter: Customizations!](./05-customize.md)

