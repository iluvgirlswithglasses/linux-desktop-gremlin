
# 2. Install Linux Desktop Gremlins

Please choose one method:

## Automatic installation (Linux only)

Just run the following script, and it will take care of the rest:

```sh
# this will install to ~/.config/linux-desktop-gremlin/
curl -s https://raw.githubusercontent.com/iluvgirlswithglasses/linux-desktop-gremlin/refs/heads/main/install.sh | bash
```

It is recommended that you check the content of the script before running.

## Automatic installation, with full git history (Linux only)

If you wish to install this repository with full git history (this will add ~200MB), please run the following script:

```sh
# this will install to ~/.config/linux-desktop-gremlin/
curl -s https://raw.githubusercontent.com/iluvgirlswithglasses/linux-desktop-gremlin/refs/heads/main/install.sh | INCLUDES_GIT=1 bash
```

## Manual installation

<details>
  <summary>Method A: Use Python Virtual Environment (Recommended)</summary>

There's nothing that can go wrong about this, except for the disk space.

```sh
# clone repository
git clone --depth 1 https://github.com/iluvgirlswithglasses/linux-desktop-gremlin ~/.config/linux-desktop-gremlin/
cd ~/.config/linux-desktop-gremlin/

# install uv -- a fast Python package manager -- then sync packages
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# make this app accessible in your app launcher (rofi/wofi/etc.)
# if you didn't install the repo in ~/.config/linux-desktop-gremlin/, please modify
# the `INSTALL_PATH` in this script before executing.
./scripts/make-desktop-files.sh
```
</details>

<details>
  <summary>Method B: Use System Package Manager</summary>

This method uses your distribution's packages to save disk space. You will need PySide6, its Qt6 dependencies, and a Python package called "requests."

```sh
# example package sync for Arch Linux
yay -S pyside6 qt6-base python-requests

# clone and install without further package downloads
git clone --depth 1 https://github.com/iluvgirlswithglasses/linux-desktop-gremlin ~/.config/linux-desktop-gremlin/
cd ~/.config/linux-desktop-gremlin/

# make this app accessible in your app launcher (rofi/wofi/etc.)
# if you didn't install the repo in ~/.config/linux-desktop-gremlin/, please modify
# the `INSTALL_PATH` in this script before executing.
./scripts/make-desktop-files.sh
```
</details>

<details>
    <summary>Method C: For non-Linux users</summary>

Since desktop entries and specific Linux paths don't apply to you, we'll keep it simple! You just need Python and the code:

```sh
# clone the repo
git clone --depth 1 https://github.com/iluvgirlswithglasses/linux-desktop-gremlin
cd linux-desktop-gremlin

# install uv
# (you can either do it this way, or download it from https://docs.astral.sh/uv/getting-started/installation/)
pip install uv

# sync the gremlin dependencies
uv sync
```
</details>

---

[--> Next chapter: Choose your Gremlins!](./03-download-gremlin-assets.md)

