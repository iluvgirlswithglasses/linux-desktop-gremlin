import json
import os
import sys
from pathlib import Path
from typing import Dict, TypedDict

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from .asset_downloader import download_asset
from .configs_loader import BASE_DIR, GREMLIN_DIRS


def load_asset_list() -> Dict[str, str]:
    path = Path(BASE_DIR) / "upstream-assets.json"
    with open(path, "r") as f:
        return json.load(f)


def resolve_asset_dir() -> Path:
    for dir in GREMLIN_DIRS:
        if dir.exists():
            return dir

    suggested_path = Path(BASE_DIR) / "gremlins"
    os.makedirs(suggested_path, exist_ok=True)
    return suggested_path


class AssetItem(TypedDict):
    name: str
    url: str
    installed: bool


class DownloadWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, asset_name, url):
        super().__init__()
        self.asset_name = asset_name
        self.url = url

    def run(self):
        try:
            download_asset(self.url)
            self.finished.emit(True, self.asset_name)
        except Exception as e:
            self.finished.emit(False, str(e))


class AssetDownloaderGui(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gremlins Downloader")
        self.setMinimumSize(450, 500)

        self.assets_data = load_asset_list()
        self.data_bucket = 69420  # unique role for storing data in QListWidgetItem

        self.init_ui()

    def init_ui(self):
        # ---- populate the layout -------------------------------------------------------
        self.info_label = QLabel()
        self.list_widget = QListWidget()
        self._to_standby_state()

        layout = QVBoxLayout(self)
        layout.addWidget(self.info_label)
        layout.addWidget(self.list_widget)

        # ---- make a simple button, in case people don't want to Mod+Q ------------------
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        self.close_btn.setStyleSheet(
            # matches the save button of ./picker.py
            "background-color: #528bff; color: white; border: none; padding: 8px 16px; border-radius: 4px;"
        )

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

        # ---- set global stylesheet (matches picker.py) ---------------------------------
        self.setStyleSheet(
            """
            QDialog { background-color: #2b2b2b; color: white; }
            QLabel { color: #dddddd; font-size: 14px; }
            QListWidget { background-color: #363636; border: 1px solid #454545; border-radius: 8px; color: white; outline: none; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #404040; }
            QListWidget::item:hover { background-color: #404040; }
            QListWidget::item:selected { background-color: #528bff; }
            QPushButton { border-radius: 4px; font-weight: bold; }
        """
        )

        self.refresh_list()
        self.list_widget.itemDoubleClicked.connect(self.start_download)

    def is_installed(self, asset_name: str) -> bool:
        """Checks if the asset exists in the gremlins folder."""
        target_path = resolve_asset_dir() / asset_name
        return target_path.exists() and target_path.is_dir()

    def refresh_list(self):
        self.list_widget.clear()

        # ---- fetch items ---------------------------------------------------------------
        items = []
        for name, url in self.assets_data.items():
            items.append(
                AssetItem(name=name, url=url, installed=self.is_installed(name))
            )
        items.sort(key=lambda x: (x["installed"], x["name"]))

        # ---- populate list -------------------------------------------------------------
        for item in items:
            installed = item["installed"]
            if installed:
                list_item = QListWidgetItem(f"(installed) {item['name']}")
                list_item.setForeground(QColor("#888888"))
            else:
                list_item = QListWidgetItem(item["name"])
            list_item.setData(self.data_bucket, item)

            # disable clicking on installed assets
            if installed:
                list_item.setFlags(list_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)

            self.list_widget.addItem(list_item)

    def start_download(self, list_item: QListWidgetItem):
        item: AssetItem = list_item.data(self.data_bucket)
        name = item["name"]
        url = item["url"]

        self._to_download_state(name)
        self.worker = DownloadWorker(name, url)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, success: bool, message: str):
        self._to_standby_state()
        if success:
            self.refresh_list()
        else:
            QMessageBox.critical(self, "Error", f"Failed to download: {message}")

    def _to_download_state(self, asset_name: str):
        self.info_label.setText(f"Downloading {asset_name}...")
        self.list_widget.setEnabled(False)

    def _to_standby_state(self):
        self.info_label.setText("Double click to download:")
        self.list_widget.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssetDownloaderGui()
    window.show()
    sys.exit(app.exec())
