
# 3. Download Gremlins Assets!

We have a dozen of Gremlins for you to choose! Use one of the tools below to download them.

## Method A: GUI Downloader

You can run the GUI Downloader from your app launcher:

<img width="747" height="370" alt="downloader" src="https://github.com/user-attachments/assets/7e03877d-c26a-4bb2-9bc3-af3eb041204f" />

You can also execute [scripts/gremlin-downloader.sh](../scripts/gremlin-downloader.sh) to launch the GUI, if you can't use app launchers.

## Method B: CLI Downloader

Prefer the terminal? Use [scripts/gremlin-downloader-cli.sh](../scripts/gremlin-downloader-cli.sh) to download assets without a GUI!

You may check for available gremlins in [upstream-assets.json](../upstream-assets.json). Whoever you want to download, just give the names to the script as arguments:

```sh
# this will install Tachibana Hikari, Matikanetannhauser, and Manhattan Cafe
./gremlin-downloader-cli.sh hikari mambo cafe
```

---

[--> Next chapter: Run Desktop Gremlins!](./04-run.md)

