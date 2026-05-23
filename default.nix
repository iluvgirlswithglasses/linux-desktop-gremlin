{
  lib,
  python3Packages,
  makeDesktopItem,
  copyDesktopItems,
  qt6,
  libX11,
  libXcursor,
  libXrandr,
  libXi,
  libXrender,
  libXext,
  pipewire,
  wrapGAppsHook3,
  jq,
  python3,
  bash,
  rofi,
  libxcb,
  libxcb-cursor,
  libxcb-keysyms,
  libxcb-render-util,
  libxcb-image,
  makeWrapper,
}:

python3Packages.buildPythonApplication {
  pname = "linux-desktop-gremlin";
  version = "0-unstable-2025-12-11";

  src = ./.;

  pyproject = true;

  desktopItems = [
    (makeDesktopItem {
      name = "linux-desktop-gremlin";
      desktopName = "Linux Desktop Gremlin";
      icon = "linux-desktop-gremlin";
      exec = "linux-desktop-gremlin";
      comment = "Pick your favorite gremlin";
      categories = [ "Utility" ];
    })
    (makeDesktopItem {
      name = "gremlin-picker";
      desktopName = "Gremlin Picker";
      icon = "linux-desktop-gremlin";
      exec = "gremlin-picker";
      comment = "Pick and config your gremlins";
      categories = ["Utility"];
    })
    (makeDesktopItem {
      name = "gremlin-downloader";
      desktopName = "Gremlin Downloader";
      icon = "linux-desktop-gremlin";
      exec = "gremlin-downloader";
      comment = "Download gremlins";
      categories = ["Utility"];
    })
  ];

  nativeBuildInputs = [
    copyDesktopItems
    python3Packages.setuptools
    python3Packages.wheel
    wrapGAppsHook3
    qt6.wrapQtAppsHook
    jq
    makeWrapper
  ];

  propagatedBuildInputs =
    with python3Packages;
    [
      pyside6
      qt6.qtbase
      qt6.qtwayland
      pipewire
      requests
    ]
    ++ [
      libX11
      libXcursor
      libXrandr
      libXi
      libXrender
      libXext
      libxcb
      libxcb-cursor
      libxcb-keysyms
      libxcb-render-util
      libxcb-image
    ];

  postInstall = ''
    mkdir -p $out/share/linux-desktop-gremlin/{src,scripts,gremlins}
    cp -r $src/src/* $out/share/linux-desktop-gremlin/src/

    install -Dm644 $src/config.json $out/share/linux-desktop-gremlin/config.json

    # /nix/store/ read-only yaddayadda
    substituteInPlace $out/share/linux-desktop-gremlin/src/asset_downloader.py \
      --replace-fail \
        'suggested_dir = Path(BASE_DIR) / "gremlins"' \
        'suggested_dir = Path(os.path.expanduser("~/.local/share/linux-desktop-gremlin/gremlins"))' \
      --replace-fail \
        'zip_path = os.path.join(BASE_DIR, "temp_asset.zip")' \
        'zip_path = "/tmp/temp_asset.zip"'

    substituteInPlace $out/share/linux-desktop-gremlin/src/configs_loader.py \
      --replace-fail \
        'master_config = _load_json(os.path.join(BASE_DIR, "config.json"))' \
        'master_config = _load_json(os.path.expanduser("~/.config/linux-desktop-gremlin/config.json") if os.path.exists(os.path.expanduser("~/.config/linux-desktop-gremlin/config.json")) else os.path.join(BASE_DIR, "config.json"))'

    substituteInPlace $out/share/linux-desktop-gremlin/src/picker.py \
      --replace-fail \
        'self.config_path = os.path.join(project_root, "config.json")' \
        'self.config_path = os.path.join(os.path.expanduser("~/.config/linux-desktop-gremlin"), "config.json")' \
      --replace-fail \
        'self.config_path = os.path.join(self.project_root, "config.json")' \
        'self.config_path = os.path.join(os.path.expanduser("~/.config/linux-desktop-gremlin"), "config.json")'

    jq '.Systray = true' $src/config.json > $out/share/linux-desktop-gremlin/config.json # enable tray
    install -Dm644 $src/upstream-assets.json $out/share/linux-desktop-gremlin/upstream-assets.json

    install -Dm755 $src/scripts/gremlin-picker.sh $out/share/linux-desktop-gremlin/scripts/gremlin-picker.sh
    sed -i "s|./run.sh \"\$PICK\"|$out/bin/linux-desktop-gremlin \"\$PICK\"|" \
      $out/share/linux-desktop-gremlin/scripts/gremlin-picker.sh

    install -Dm755 $src/scripts/gremlin-downloader{,-cli}.sh $out/share/linux-desktop-gremlin/scripts/

    # avoids using uv for this
    sed -i '/^PYTHON=""/,/^fi$/c\PYTHON="python3"' \
      $out/share/linux-desktop-gremlin/scripts/gremlin-picker.sh \
      $out/share/linux-desktop-gremlin/scripts/gremlin-downloader{,-cli}.sh

    patchShebangs --build $out/share/linux-desktop-gremlin
    install -Dm644 $src/icon.png $out/share/icons/hicolor/256x256/apps/linux-desktop-gremlin.png
  '';

  postFixup = let
    binPath = lib.makeBinPath [
      (python3.withPackages (ps:
        with ps; [
          pyside6
          requests
        ]))
      bash
      rofi
    ];
  in ''
    wrapProgram $out/bin/linux-desktop-gremlin \
      "''${gappsWrapperArgs[@]}" \
      "''${qtWrapperArgs[@]}" \
      --prefix PYTHONPATH : $out/share/linux-desktop-gremlin \
      --set QT_QPA_PLATFORM xcb \
      --prefix LD_LIBRARY_PATH : ${pipewire}/lib \
      --prefix PATH : ${binPath}

    makeWrapper $out/share/linux-desktop-gremlin/scripts/gremlin-picker.sh $out/bin/gremlin-picker \
      "''${gappsWrapperArgs[@]}" \
      "''${qtWrapperArgs[@]}" \
      --prefix PYTHONPATH : $out/share/linux-desktop-gremlin \
      --set QT_QPA_PLATFORM xcb \
      --prefix LD_LIBRARY_PATH : ${pipewire}/lib \
      --prefix PATH : ${binPath}

    makeWrapper $out/share/linux-desktop-gremlin/scripts/gremlin-downloader.sh $out/bin/gremlin-downloader \
      "''${gappsWrapperArgs[@]}" \
      "''${qtWrapperArgs[@]}" \
      --prefix PYTHONPATH : $out/share/linux-desktop-gremlin \
      --set QT_QPA_PLATFORM xcb \
      --prefix LD_LIBRARY_PATH : ${pipewire}/lib \
      --prefix PATH : ${binPath}
  '';

  meta = {
    description = "Linux Desktop Gremlins brings animated mascots to your Linux desktop.";
    homepage = "https://github.com/iluvgirlswithglasses/linux-desktop-gremlin";
    license = lib.licenses.mit;
    platforms = lib.platforms.linux;
    mainProgram = "linux-desktop-gremlin";
    maintainers = with lib.maintainers; [ lonerOrz ];
  };
}
