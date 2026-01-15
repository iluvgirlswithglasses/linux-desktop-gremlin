import os
from typing import Callable

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QWidget

from ..configs_loader import BASE_DIR
from ..settings import Preferences


class SystrayIcon:
    def __init__(self, parent: QWidget, close_app: Callable[[], None]):
        # ignore if systray is disabled
        if not Preferences.Systray:
            return

        # create system tray icon
        self.tray_icon = QSystemTrayIcon(parent)
        self.tray_icon.setToolTip("Gremlin")
        self.set_icon()

        # create menu
        menu = QMenu()
        menu.addSeparator()

        # create close action
        close_action = QAction("Close", parent)
        close_action.triggered.connect(close_app)
        menu.addAction(close_action)

        # set context menu
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def set_icon(self):
        # find icon.ico or icon.png in BASE_DIR
        icon_path = os.path.join(BASE_DIR, "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(BASE_DIR, "icon.png")

        # set tray icon
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("applications-games"))
