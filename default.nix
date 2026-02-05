{
  lib,
  python3Packages,
  makeDesktopItem,
  copyDesktopItems,
  qt6,
  xorg,
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
  ];

  nativeBuildInputs = [
    copyDesktopItems
    python3Packages.setuptools
    python3Packages.wheel
    wrapGAppsHook3
    qt6.wrapQtAppsHook
    jq
  ];

  propagatedBuildInputs =
    with python3Packages;
    [
      pyside6
      qt6.qtbase
      qt6.qtwayland
      pipewire
    ]
    ++ (with xorg; [
      libX11
      libXcursor
      libXrandr
      libXi
      libXrender
      libXext
    ])
    ++ [
      libxcb
      libxcb-cursor
      libxcb-keysyms
      libxcb-render-util
      libxcb-image
    ];

  postInstall = ''
    mkdir -p $out/share/linux-desktop-gremlin/{src,scripts}
    cp -r $src/src/* $out/share/linux-desktop-gremlin/src/
    cp -r $src/gremlins $out/share/linux-desktop-gremlin/gremlins

    install -Dm644 $src/config.json $out/share/linux-desktop-gremlin/config.json
    jq '.Systray = true' $src/config.json > $out/share/linux-desktop-gremlin/config.json # enable tray

    install -Dm755 $src/scripts/gremlin-picker.sh $out/share/linux-desktop-gremlin/scripts/gremlin-picker.sh
    sed -i "s|./run.sh \"\$pick\"|$out/bin/linux-desktop-gremlin \"\$pick\"|" \
      $out/share/linux-desktop-gremlin/scripts/gremlin-picker.sh

    install -Dm644 $src/icon.png $out/share/icons/hicolor/256x256/apps/linux-desktop-gremlin.png
  '';

  postFixup =
    let
      binPath = lib.makeBinPath [
        python3
        bash
        rofi
      ];
    in
    ''
      wrapProgram $out/bin/linux-desktop-gremlin \
        "''${gappsWrapperArgs[@]}" \
        --prefix PYTHONPATH : $out/share/linux-desktop-gremlin \
        --set QT_QPA_PLATFORM xcb \
        --prefix LD_LIBRARY_PATH : ${pipewire}/lib \
        --prefix PATH : ${binPath}
      makeWrapper $out/share/linux-desktop-gremlin/scripts/gremlin-picker.sh $out/bin/gremlin-picker \
        --prefix PYTHONPATH : $out/share/linux-desktop-gremlin \
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
